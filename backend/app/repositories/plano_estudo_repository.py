"""Locks de geração/propriedade e consulta ordenada, sem CRUD duplicado."""
from sqlalchemy import select
from app.contexto_leitura import ContextoLeitura
from app.extensions import db
from app.models.usuario import Usuario
from app.models.plano_estudo import PlanoEstudo as Plano, PlanoEstudoItem as Item


class PlanoEstudoRepository:
    @staticmethod
    def bloquear_usuario(usuario_id):
        db.session.execute(select(Usuario.id).where(Usuario.id == usuario_id).with_for_update()).scalar_one()

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
        return db.session.execute(select(Item).where(Item.plano_id == plano_id).order_by(Item.posicao)).scalars().all()

    @staticmethod
    def item_proprio(usuario_id, item_id):
        return db.session.execute(select(Item, Plano).join(Plano, Item.plano_id == Plano.id)
            .where(Plano.usuario_id == usuario_id, Item.id == item_id)
            .with_for_update().execution_options(populate_existing=True)).one_or_none()
