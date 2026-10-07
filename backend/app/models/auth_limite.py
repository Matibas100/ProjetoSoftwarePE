from app.extensions import db
from app.models.crud_mixin import CrudMixin


class AuthLimite(CrudMixin):
    __tablename__ = "auth_limites"
    chave_hash = db.Column(db.CHAR(64, collation="ascii_bin"), primary_key=True)
    falhas = db.Column(db.SmallInteger, nullable=False)
    janela_inicio = db.Column(db.DateTime, nullable=False)
    bloqueado_ate = db.Column(db.DateTime)
    campos_atualizaveis = {"falhas", "janela_inicio", "bloqueado_ate"}
