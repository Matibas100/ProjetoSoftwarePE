"""Histórico e locks de propriedade, sem confirmação autônoma."""
from app.core.procedures_mysql import executar_resultados, conferir_resultados
from app.modules.praticas.repositories.registros_praticas import PRATICA, PraticaHistoricoRegistro
from sqlalchemy import select, func, literal, text
from app.extensions import db
from app.modules.praticas.models.pratica_tentativa import PraticaTentativa as Tentativa


class PraticaRepository:
    @staticmethod
    def projecao_desempenho(usuario_id, inicio, fim):
        if usuario_id is None or inicio is None or fim is None:
            raise ValueError("Usuário e intervalo são obrigatórios.")
        return select(
            literal("pratica").label("tipo"),
            Tentativa.id.label("id"),
            Tentativa.id.label("atividade_id"),
            Tentativa.usuario_id,
            Tentativa.respondida_em.label("ocorrido_em"),
            Tentativa.correta,
            Tentativa.materia_id,
            Tentativa.materia_nome,
            Tentativa.assunto_id,
            Tentativa.assunto_nome
        ).where(
            Tentativa.usuario_id == usuario_id,
            Tentativa.estado == "respondida",
            Tentativa.respondida_em >= inicio,
            Tentativa.respondida_em < fim
        )

    @staticmethod
    def projecao_atividades(usuario_id, inicio, fim):
        fatos = PraticaRepository.projecao_desempenho(usuario_id, inicio, fim).subquery()
        return select(
            fatos.c.tipo,
            fatos.c.atividade_id.label("id"),
            fatos.c.ocorrido_em,
            func.concat(fatos.c.materia_nome, " · ", fatos.c.assunto_nome).label("titulo")
        )

    @staticmethod
    def por_chave(usuario_id, chave, bloquear=False):
        db.session.flush()
        consulta = select(Tentativa).from_statement(
            text("CALL sp_pratica_por_chave(:usuario_id,:valor,:bloquear)").columns(*Tentativa.__table__.columns))
        if bloquear:
            consulta = consulta.execution_options(populate_existing=True)
        resultado = db.session.execute(
            consulta,
            {'usuario_id': usuario_id, 'valor': chave, 'bloquear': int(bloquear)}
        )
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def propria(usuario_id, tentativa_id, bloquear=False):
        db.session.flush()
        consulta = select(Tentativa).from_statement(
            text("CALL sp_pratica_propria(:usuario_id,:valor,:bloquear)").columns(*Tentativa.__table__.columns))
        if bloquear:
            consulta = consulta.execution_options(populate_existing=True)
        resultado = db.session.execute(
            consulta,
            {'usuario_id': usuario_id, 'valor': tentativa_id, 'bloquear': int(bloquear)}
        )
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def historico(usuario_id, assunto_id, pagina, limite):
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            "CALL sp_praticas_historico(%s,%s,%s,%s)",
            (usuario_id, assunto_id or None, pagina, limite)
        )
        linhas, totais = conferir_resultados(resultados, [PRATICA, ('total',)])
        total, = totais
        return [PraticaHistoricoRegistro(**{
            **r,
            'correta': bool(r['correta'])
        }) for r in linhas], int(total['total'])

    @staticmethod
    def fatos(usuario_id, inicio, fim):
        db.session.flush()
        resultado = db.session.execute(
            select(Tentativa).from_statement(
                text("CALL sp_praticas_fatos(:usuario_id,:inicio,:fim)").columns(*Tentativa.__table__.columns)),
            {'usuario_id': usuario_id, 'inicio': inicio, 'fim': fim}
        )
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()
