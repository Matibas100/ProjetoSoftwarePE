from app.extensions import db
from app.core.persistencia import CrudMixin


class Sessao(CrudMixin):
    __tablename__ = "sessoes"
    id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id",
            ondelete="RESTRICT",
            onupdate="RESTRICT"
        )
    )
    identificador_hash = db.Column(db.CHAR(64, collation="ascii_bin"), nullable=False, unique=True)
    criada_em = db.Column(db.DateTime, nullable=False)
    ultimo_acesso_em = db.Column(db.DateTime, nullable=False)
    expira_em = db.Column(db.DateTime, nullable=False)
    reautenticada_em = db.Column(db.DateTime)
    revogada_em = db.Column(db.DateTime)
    usuario = db.relationship("Usuario")
    campos_atualizaveis = {"ultimo_acesso_em", "reautenticada_em", "revogada_em"}
