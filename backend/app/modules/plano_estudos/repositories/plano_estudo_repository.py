"""Locks de geração/propriedade e consulta ordenada, sem CRUD duplicado."""
from sqlalchemy import delete, select
from app.contexto_leitura import ContextoLeitura
from app.extensions import db
from app.modules.contas.api import bloquear_usuario
from app.modules.plano_estudos.models.plano_estudo import PlanoEstudo as Plano, PlanoEstudoItem as Item


class PlanoEstudoRepository:
    bloquear_usuario = staticmethod(bloquear_usuario)

    @staticmethod
    def contexto(instante):
        return ContextoLeitura(db.session.connection(), instante)

    @staticmethod
    def atual(usuario_id, bloquear=False):
        consulta = select(Plano).where(Plano.usuario_id == usuario_id, Plano.atual.is_(True))
        if bloquear:
            consulta = consulta.with_for_update().execution_options(populate_existing=True)
        return db.session.execute(consulta).scalar_one_or_none()

    @staticmethod
    def por_chave(usuario_id, chave):
        return db.session.execute(select(Plano).where(Plano.usuario_id == usuario_id, Plano.chave_envio == chave)
            .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()

    @staticmethod
    def itens(plano_id):
        return db.session.execute(select(Item).where(Item.plano_id == plano_id).order_by(Item.posicao)
            .with_for_update().execution_options(populate_existing=True)).scalars().all()

    @staticmethod
    def item_proprio(usuario_id, item_id):
        return db.session.execute(select(Item, Plano).join(Plano, Item.plano_id == Plano.id)
            .where(Plano.usuario_id == usuario_id, Item.id == item_id)
            .with_for_update().execution_options(populate_existing=True)).one_or_none()

    @staticmethod
    def eliminar_planos_proprios(usuario_id):
        # O chamador mantém o lock do usuário até o único commit da negativa.
        ids = db.session.execute(select(Plano.id).where(Plano.usuario_id == usuario_id)
            .order_by(Plano.id.desc()).with_for_update()).scalars().all()
        for plano_id in ids:
            propria = select(Plano.id).where(Plano.usuario_id == usuario_id,
                Plano.id == plano_id)
            db.session.execute(delete(Item).where(Item.plano_id == plano_id,
                Item.plano_id.in_(propria)), execution_options={"synchronize_session": False})
            db.session.execute(delete(Plano).where(Plano.id == plano_id,
                Plano.usuario_id == usuario_id), execution_options={"synchronize_session": False})
