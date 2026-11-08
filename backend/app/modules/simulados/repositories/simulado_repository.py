"""Consultas especializadas, composição e locks; sem commit próprio."""
import json
from app.core.procedures_mysql import executar_resultados
from app.modules.simulados.repositories.registros_simulados import (SIMULADO, TENTATIVA, SimuladoRegistro, TentativaHistoricoRegistro)
from app.core.procedures_mysql import conferir_resultados
from sqlalchemy import select, func, literal, text
from app.extensions import db
from app.modules.simulados.models.simulado import (Simulado, SimuladoVersao, SimuladoRascunhoItem,
    SimuladoVersaoItem, SimuladoTentativa, SimuladoResposta)


class SimuladoRepository:
    @staticmethod
    def projecao_desempenho(usuario_id, inicio, fim):
        from app.modules.conteudo.api import projecao_classificacao_historica
        if usuario_id is None or inicio is None or fim is None:
            raise ValueError("Usuário e intervalo são obrigatórios.")
        t, r, i = SimuladoTentativa, SimuladoResposta, SimuladoVersaoItem
        classificacao = projecao_classificacao_historica().subquery()
        q = classificacao.c
        return (select(literal("simulado").label("tipo"), r.id.label("id"), t.id.label("atividade_id"),
            t.usuario_id, t.finalizada_em.label("ocorrido_em"), r.correta,
            q.materia_id, q.materia_nome, q.assunto_id, q.assunto_nome)
            .select_from(r).join(t, t.id == r.tentativa_id).join(i, i.id == r.item_id)
            .join(classificacao, q.questao_versao_id == i.questao_versao_id).where(t.usuario_id == usuario_id,
                t.estado == "finalizada", r.alternativa.is_not(None), t.finalizada_em >= inicio, t.finalizada_em < fim))

    @staticmethod
    def projecao_atividades(usuario_id, inicio, fim):
        if usuario_id is None or inicio is None or fim is None:
            raise ValueError("Usuário e intervalo são obrigatórios.")
        t, v = SimuladoTentativa, SimuladoVersao
        return (select(literal("simulado").label("tipo"), t.id, t.finalizada_em.label("ocorrido_em"), v.titulo)
            .join(v, v.id == t.simulado_versao_id).where(t.usuario_id == usuario_id,
                t.estado == "finalizada", t.finalizada_em >= inicio, t.finalizada_em < fim))

    @staticmethod
    def contagens_dashboard(contexto):
        resultados = contexto.executar_resultados("CALL sp_simulados_contagens_dashboard()")
        linhas, = conferir_resultados(resultados, [('rascunhos', 'publicados', 'arquivados', 'finalizadas')])
        linha, = linhas
        return {estado: int(linha[estado]) for estado in ('rascunhos', 'publicados', 'arquivados')}, int(linha['finalizadas'])

    @staticmethod
    def bloquear(simulado_id):
        db.session.flush()
        resultado = db.session.execute(select(Simulado).from_statement(
            text("CALL sp_bloquear_simulado(:id)").columns(*Simulado.__table__.columns))
            .execution_options(populate_existing=True),
            {'id': simulado_id})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def itens(simulado_id=None, versao_id=None):
        entidade = SimuladoRascunhoItem if versao_id is None else SimuladoVersaoItem
        db.session.flush()
        resultado = db.session.execute(select(entidade).from_statement(
            text("CALL sp_simulado_itens(:simulado_id,:versao_id)").columns(*entidade.__table__.columns)),
            {'simulado_id': simulado_id, 'versao_id': versao_id})
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()

    @staticmethod
    def itens_em_lote(simulado_ids=None, versao_ids=None):
        entidade = SimuladoRascunhoItem if versao_ids is None else SimuladoVersaoItem
        ids = simulado_ids if versao_ids is None else versao_ids
        if not ids:
            return {}
        db.session.flush()
        resultado = db.session.execute(select(entidade).from_statement(
            text("CALL sp_simulados_itens_lote(:simulados,:versoes)").columns(*entidade.__table__.columns)),
            {'simulados': json.dumps(sorted(set(ids))) if versao_ids is None else None,
             'versoes': json.dumps(sorted(set(ids))) if versao_ids is not None else None})
        try:
            grupos = {}
            for item in resultado.scalars():
                id_ = item.simulado_id if versao_ids is None else item.simulado_versao_id
                grupos.setdefault(id_, []).append(item)
            return grupos
        finally:
            resultado.close()

    @staticmethod
    def andamentos_em_lote(usuario_id, versao_ids):
        if not versao_ids:
            return {}
        db.session.flush()
        resultado = db.session.execute(select(SimuladoTentativa).from_statement(
            text("CALL sp_simulados_andamentos_lote(:usuario_id,:ids)").columns(*SimuladoTentativa.__table__.columns)),
            {'usuario_id': usuario_id, 'ids': json.dumps(sorted(set(versao_ids)))})
        try:
            return {t.simulado_versao_id: t for t in resultado.scalars()}
        finally:
            resultado.close()

    @staticmethod
    def titulos_em_lote(versao_ids):
        if not versao_ids:
            return {}
        db.session.flush()
        resultados = executar_resultados(db.session.connection(), "CALL sp_simulados_titulos_lote(%s)",
            (json.dumps(sorted(set(versao_ids))),))
        linhas, = conferir_resultados(resultados, [('id', 'titulo')])
        return {r['id']: r['titulo'] for r in linhas}

    @staticmethod
    def listar(pagina, limite, estado=None):
        db.session.flush()
        resultados = executar_resultados(db.session.connection(), "CALL sp_simulados_listar(%s,%s,%s)",
            (pagina, limite, estado or None))
        linhas, totais = conferir_resultados(resultados, [SIMULADO, ('total',)])
        total, = totais
        return [SimuladoRegistro(**r) for r in linhas], int(total['total'])

    @staticmethod
    def propria(usuario_id, tentativa_id, bloquear=False):
        db.session.flush()
        consulta = select(SimuladoTentativa).from_statement(
            text("CALL sp_simulado_tentativa_propria(:usuario_id,:id,:bloquear)").columns(*SimuladoTentativa.__table__.columns))
        if bloquear:
            consulta = consulta.execution_options(populate_existing=True)
        resultado = db.session.execute(consulta,
            {'usuario_id': usuario_id, 'id': tentativa_id, 'bloquear': int(bloquear)})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def por_chave(usuario_id, chave):
        db.session.flush()
        resultado = db.session.execute(select(SimuladoTentativa).from_statement(
            text("CALL sp_simulado_tentativa_por_chave(:usuario_id,:chave)").columns(*SimuladoTentativa.__table__.columns))
            .execution_options(populate_existing=True),
            {'usuario_id': usuario_id, 'chave': chave})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def andamento(usuario_id, versao_id):
        db.session.flush()
        resultado = db.session.execute(select(SimuladoTentativa).from_statement(
            text("CALL sp_simulado_em_andamento(:usuario_id,:versao_id)").columns(*SimuladoTentativa.__table__.columns))
            .execution_options(populate_existing=True),
            {'usuario_id': usuario_id, 'versao_id': versao_id})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def respostas(tentativa_id, bloquear=False):
        db.session.flush()
        resultado = db.session.execute(select(SimuladoResposta, SimuladoVersaoItem).from_statement(
            text("CALL sp_simulado_respostas(:tentativa_id,:bloquear)").columns(*SimuladoResposta.__table__.columns, *SimuladoVersaoItem.__table__.columns))
            .execution_options(populate_existing=True),
            {'tentativa_id': tentativa_id, 'bloquear': int(bloquear)})
        try:
            return resultado.all()
        finally:
            resultado.close()

    @staticmethod
    def historico(usuario_id, pagina, limite):
        db.session.flush()
        resultados = executar_resultados(db.session.connection(), "CALL sp_simulados_historico(%s,%s,%s)",
            (usuario_id, pagina, limite))
        linhas, totais = conferir_resultados(resultados, [TENTATIVA, ('total',)])
        total, = totais
        return [TentativaHistoricoRegistro(**r) for r in linhas], int(total['total'])

    @staticmethod
    def fatos(usuario_id, inicio, fim):
        db.session.flush()
        resultado = db.session.execute(select(SimuladoResposta, SimuladoVersaoItem, SimuladoTentativa).from_statement(
            text("CALL sp_simulados_fatos(:usuario_id,:inicio,:fim)").columns(*SimuladoResposta.__table__.columns, *SimuladoVersaoItem.__table__.columns, *SimuladoTentativa.__table__.columns)),
            {'usuario_id': usuario_id, 'inicio': inicio, 'fim': fim})
        try:
            return resultado.all()
        finally:
            resultado.close()
