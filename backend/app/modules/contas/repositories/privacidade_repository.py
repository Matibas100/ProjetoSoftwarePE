"""Leituras correntes de privacidade e lock de identidade na transação externa."""
from sqlalchemy import select, text

from app.extensions import db
from app.modules.contas.models.usuario import Usuario
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade


class PrivacidadeRepository:
    @staticmethod
    def bloquear_usuario(usuario_id):
        db.session.flush()
        resultado = db.session.execute(text('CALL sp_bloquear_identidade_privacidade(:id)')
            .columns(Usuario.__table__.c.id), {'id': usuario_id})
        try:
            resultado.scalar_one()
        finally:
            resultado.close()

    @staticmethod
    def ultimas(usuario_id):
        db.session.flush()
        resultado = db.session.execute(select(RegistroPrivacidade).from_statement(
            text('CALL sp_ultimas_decisoes_privacidade(:id)').columns(*RegistroPrivacidade.__table__.columns))
            .execution_options(populate_existing=True), {'id': usuario_id})
        try:
            registros = {'uso': None, 'plano': None}
            for registro in resultado.scalars():
                registros[registro.tipo] = registro
            return registros
        finally:
            resultado.close()

    @staticmethod
    def por_chave(usuario_id, chave):
        db.session.flush()
        resultado = db.session.execute(select(RegistroPrivacidade).from_statement(
            text('CALL sp_decisao_privacidade_por_chave(:id,:chave)').columns(*RegistroPrivacidade.__table__.columns))
            .execution_options(populate_existing=True), {'id': usuario_id, 'chave': chave})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()
