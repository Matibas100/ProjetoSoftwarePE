"""Leituras correntes de privacidade e lock de identidade na transação externa."""
from sqlalchemy import select

from app.extensions import db
from app.modules.contas.models.usuario import Usuario
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade


class PrivacidadeRepository:
    @staticmethod
    def bloquear_usuario(usuario_id):
        db.session.execute(select(Usuario.id).where(Usuario.id == usuario_id).with_for_update()).scalar_one()

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
