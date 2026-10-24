"""Consultas especializadas, composição e locks; sem commit próprio."""
from sqlalchemy import select, func, literal
from app.extensions import db
from app.models.simulado import (Simulado, SimuladoVersao, SimuladoRascunhoItem,
    SimuladoVersaoItem, SimuladoTentativa, SimuladoResposta)


class SimuladoRepository:
    @staticmethod
    def projecao_desempenho(usuario_id, inicio, fim):
        from app.repositories.questao_repository import QuestaoRepository
        if usuario_id is None or inicio is None or fim is None:
            raise ValueError("Usuário e intervalo são obrigatórios.")
        t, r, i = SimuladoTentativa, SimuladoResposta, SimuladoVersaoItem
        classificacao = QuestaoRepository.projecao_classificacao_historica().subquery()
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
        estados = dict(contexto.executar(select(Simulado.estado, func.count()).group_by(Simulado.estado)).all())
        finalizadas = contexto.executar(select(func.count()).select_from(SimuladoTentativa)
            .where(SimuladoTentativa.estado == "finalizada")).scalar_one()
        return {"rascunhos": estados.get("rascunho", 0), "publicados": estados.get("publicado", 0),
            "arquivados": estados.get("arquivado", 0)}, finalizadas

    @staticmethod
    def bloquear(simulado_id):
        return db.session.execute(select(Simulado).where(Simulado.id == simulado_id)
            .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()

    @staticmethod
    def itens(simulado_id=None, versao_id=None):
        entidade = SimuladoRascunhoItem if versao_id is None else SimuladoVersaoItem
        condicao = entidade.simulado_id == simulado_id if versao_id is None else entidade.simulado_versao_id == versao_id
        return db.session.execute(select(entidade).where(condicao).order_by(entidade.posicao)).scalars().all()

    @staticmethod
    def listar(pagina, limite, estado=None):
        consulta = select(Simulado)
        if estado:
            consulta = consulta.where(Simulado.estado == estado)
        total = db.session.execute(select(func.count()).select_from(consulta.subquery())).scalar_one()
        linhas = db.session.execute(consulta.order_by(Simulado.id.desc()).offset((pagina - 1) * limite).limit(limite)).scalars().all()
        return linhas, total

    @staticmethod
    def propria(usuario_id, tentativa_id, bloquear=False):
        consulta = select(SimuladoTentativa).where(SimuladoTentativa.usuario_id == usuario_id,
            SimuladoTentativa.id == tentativa_id)
        if bloquear:
            consulta = consulta.with_for_update().execution_options(populate_existing=True)
        return db.session.execute(consulta).scalar_one_or_none()

    @staticmethod
    def por_chave(usuario_id, chave):
        return db.session.execute(select(SimuladoTentativa).where(SimuladoTentativa.usuario_id == usuario_id,
            SimuladoTentativa.chave_envio == chave).with_for_update()
            .execution_options(populate_existing=True)).scalar_one_or_none()

    @staticmethod
    def andamento(usuario_id, versao_id):
        return db.session.execute(select(SimuladoTentativa).where(SimuladoTentativa.usuario_id == usuario_id,
            SimuladoTentativa.simulado_versao_id == versao_id, SimuladoTentativa.estado == "em_andamento")
            .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()

    @staticmethod
    def respostas(tentativa_id, bloquear=False):
        consulta = (select(SimuladoResposta, SimuladoVersaoItem)
            .join(SimuladoVersaoItem, SimuladoVersaoItem.id == SimuladoResposta.item_id)
            .where(SimuladoResposta.tentativa_id == tentativa_id).order_by(SimuladoVersaoItem.posicao)
            .execution_options(populate_existing=True))
        if bloquear:
            consulta = consulta.with_for_update()
        return db.session.execute(consulta).all()

    @staticmethod
    def historico(usuario_id, pagina, limite):
        consulta = select(SimuladoTentativa).where(SimuladoTentativa.usuario_id == usuario_id,
            SimuladoTentativa.estado == "finalizada")
        total = db.session.execute(select(func.count()).select_from(consulta.subquery())).scalar_one()
        linhas = db.session.execute(consulta.order_by(SimuladoTentativa.finalizada_em.desc(),
            SimuladoTentativa.id.desc()).offset((pagina - 1) * limite).limit(limite)).scalars().all()
        return linhas, total

    @staticmethod
    def fatos(usuario_id, inicio, fim):
        return db.session.execute(select(SimuladoResposta, SimuladoVersaoItem, SimuladoTentativa)
            .join(SimuladoVersaoItem, SimuladoResposta.item_id == SimuladoVersaoItem.id)
            .join(SimuladoTentativa, SimuladoResposta.tentativa_id == SimuladoTentativa.id)
            .where(SimuladoTentativa.usuario_id == usuario_id, SimuladoTentativa.estado == "finalizada",
                SimuladoResposta.alternativa.is_not(None), SimuladoTentativa.finalizada_em >= inicio,
                SimuladoTentativa.finalizada_em < fim)
            .order_by(SimuladoTentativa.finalizada_em, SimuladoResposta.id)).all()
