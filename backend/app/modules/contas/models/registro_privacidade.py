"""Evidência append-only de decisões atribuídas à própria conta."""
from sqlalchemy import event
from sqlalchemy.dialects.mysql import DATETIME

from app.core.relogio import agora_utc
from app.exceptions import ConflitoError
from app.extensions import db
from app.core.persistencia import ModeloBase


class RegistroPrivacidade(ModeloBase):
    __tablename__ = "registros_privacidade"
    __table_args__ = (
        db.UniqueConstraint("usuario_id", "chave_envio", name="uq_privacidade_chave"),
        db.Index("ix_privacidade_ultima", "usuario_id", "tipo", "id"),
        db.CheckConstraint("tipo IN ('uso','plano')", name="ck_privacidade_tipo"),
        db.CheckConstraint("acao IN ('aceitar','recusar','revogar')", name="ck_privacidade_acao"),
        db.CheckConstraint("tipo = 'plano' OR acao = 'aceitar'", name="ck_privacidade_combinacao"),
        db.CheckConstraint("revisao_base >= 0", name="ck_privacidade_revisao"),
    )
    id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id",
            ondelete="RESTRICT",
            onupdate="RESTRICT"
        ),
        nullable=False
    )
    tipo = db.Column(db.String(8), nullable=False)
    acao = db.Column(db.String(8), nullable=False)
    versao = db.Column(db.String(20), nullable=False)
    documento_sha256 = db.Column(db.CHAR(64, collation="ascii_bin"), nullable=False)
    registrado_em = db.Column(DATETIME(fsp=6), nullable=False, default=agora_utc)
    chave_envio = db.Column(db.CHAR(36, collation="ascii_bin"), nullable=False)
    revisao_base = db.Column(db.BigInteger, nullable=False)


@event.listens_for(RegistroPrivacidade, "before_update")
@event.listens_for(RegistroPrivacidade, "before_delete")
def preservar_registro(mapper, connection, target):
    raise ConflitoError("O registro de privacidade é imutável.")
