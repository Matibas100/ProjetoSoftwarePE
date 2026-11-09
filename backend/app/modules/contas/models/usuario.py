from app.extensions import db
from app.core.persistencia import CrudMixin


class Usuario(CrudMixin):
    __tablename__ = "usuarios"
    __table_args__ = (
        db.UniqueConstraint("email", name="uq_usuarios_email"),
        db.CheckConstraint("perfil IN ('aluno', 'administrador')", name="ck_usuarios_perfil"),
        db.CheckConstraint("ativo IN (0, 1)", name="ck_usuarios_ativo"),
    )
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254, collation="utf8mb4_bin"), nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False)
    campos_atualizaveis = {"nome", "email", "ativo", "senha_hash"}

    @classmethod
    def buscar_por_email(cls, email):
        from app.modules.contas.repositories.autenticacao_repository import AutenticacaoRepository
        return AutenticacaoRepository.buscar_por_email(email)

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "email": self.email, "perfil": self.perfil}
