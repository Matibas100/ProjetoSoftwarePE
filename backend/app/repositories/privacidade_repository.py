"""Leituras correntes e eliminação transacional delimitada do plano próprio."""
from sqlalchemy import delete, select

from app.extensions import db
from app.models.plano_estudo import PlanoEstudo, PlanoEstudoItem
from app.models.registro_privacidade import RegistroPrivacidade
from app.repositories.plano_estudo_repository import PlanoEstudoRepository


class PrivacidadeRepository:
    bloquear_usuario = staticmethod(PlanoEstudoRepository.bloquear_usuario)

    @staticmethod
    def ultimas(usuario_id):
        registros = {}
        for tipo in ("uso", "plano"):
            registros[tipo] = db.session.execute(select(RegistroPrivacidade).where(
                RegistroPrivacidade.usuario_id == usuario_id, RegistroPrivacidade.tipo == tipo)
                .order_by(RegistroPrivacidade.id.desc()).limit(1).with_for_update()
                .execution_options(populate_existing=True)).scalar_one_or_none()
        return registros

    @staticmethod
    def por_chave(usuario_id, chave):
        return db.session.execute(select(RegistroPrivacidade).where(
            RegistroPrivacidade.usuario_id == usuario_id, RegistroPrivacidade.chave_envio == chave)
            .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()

    @staticmethod
    def eliminar_planos_proprios(usuario_id):
        # O chamador mantém o lock do usuário até o único commit da negativa.
        ids = db.session.execute(select(PlanoEstudo.id).where(PlanoEstudo.usuario_id == usuario_id)
            .order_by(PlanoEstudo.id.desc()).with_for_update()).scalars().all()
        for plano_id in ids:
            propria = select(PlanoEstudo.id).where(PlanoEstudo.usuario_id == usuario_id,
                PlanoEstudo.id == plano_id)
            db.session.execute(delete(PlanoEstudoItem).where(PlanoEstudoItem.plano_id == plano_id,
                PlanoEstudoItem.plano_id.in_(propria)), execution_options={"synchronize_session": False})
            db.session.execute(delete(PlanoEstudo).where(PlanoEstudo.id == plano_id,
                PlanoEstudo.usuario_id == usuario_id), execution_options={"synchronize_session": False})
