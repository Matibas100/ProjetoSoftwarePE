"""Histórico e locks de propriedade, sem confirmação autônoma."""
from sqlalchemy import select, func, literal
from app.extensions import db
from app.models.pratica_tentativa import PraticaTentativa as Tentativa


class PraticaRepository:
    @staticmethod
    def projecao_desempenho(usuario_id, inicio, fim):
        if usuario_id is None or inicio is None or fim is None:
            raise ValueError("Usuário e intervalo são obrigatórios.")
        return select(literal("pratica").label("tipo"), Tentativa.id.label("id"),
            Tentativa.id.label("atividade_id"), Tentativa.usuario_id, Tentativa.respondida_em.label("ocorrido_em"),
            Tentativa.correta, Tentativa.materia_id, Tentativa.materia_nome, Tentativa.assunto_id, Tentativa.assunto_nome
        ).where(Tentativa.usuario_id == usuario_id, Tentativa.estado == "respondida",
            Tentativa.respondida_em >= inicio, Tentativa.respondida_em < fim)

    @staticmethod
    def projecao_atividades(usuario_id, inicio, fim):
        fatos = PraticaRepository.projecao_desempenho(usuario_id, inicio, fim).subquery()
        return select(fatos.c.tipo, fatos.c.atividade_id.label("id"), fatos.c.ocorrido_em,
            func.concat(fatos.c.materia_nome, " · ", fatos.c.assunto_nome).label("titulo"))

    @staticmethod
    def por_chave(usuario_id, chave, bloquear=False):
        consulta = select(Tentativa).where(Tentativa.usuario_id == usuario_id, Tentativa.chave_envio == chave)
        if bloquear:
            consulta = consulta.with_for_update().execution_options(populate_existing=True)
        return db.session.execute(consulta).scalar_one_or_none()

    @staticmethod
    def propria(usuario_id, tentativa_id, bloquear=False):
        consulta = select(Tentativa).where(Tentativa.usuario_id == usuario_id, Tentativa.id == tentativa_id)
        if bloquear:
            consulta = consulta.with_for_update().execution_options(populate_existing=True)
        return db.session.execute(consulta).scalar_one_or_none()

    @staticmethod
    def historico(usuario_id, assunto_id, pagina, limite):
        base = select(Tentativa).where(Tentativa.usuario_id == usuario_id, Tentativa.estado == "respondida")
        if assunto_id:
            base = base.where(Tentativa.assunto_id == assunto_id)
        total = db.session.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        linhas = db.session.execute(base.order_by(Tentativa.respondida_em.desc(), Tentativa.id.desc())
            .offset((pagina - 1) * limite).limit(limite)).scalars().all()
        return linhas, total

    @staticmethod
    def fatos(usuario_id, inicio, fim):
        return db.session.execute(select(Tentativa).where(Tentativa.usuario_id == usuario_id,
            Tentativa.estado == "respondida", Tentativa.respondida_em >= inicio,
            Tentativa.respondida_em < fim).order_by(Tentativa.respondida_em, Tentativa.id)).scalars().all()
