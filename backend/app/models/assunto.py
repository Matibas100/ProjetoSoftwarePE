from app.extensions import db
from app.models.crud_mixin import CrudMixin


class Assunto(CrudMixin):
    __tablename__ = "assuntos"
    __table_args__ = (
        db.UniqueConstraint(
            "materia_id", "nome_normalizado", name="uq_assuntos_materia_nome_normalizado"
        ),
        db.CheckConstraint(
            "status IN ('ativa', 'inativa', 'arquivada')", name="ck_assuntos_status"
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    nome_normalizado = db.Column(
        db.String(150, collation="utf8mb4_0900_ai_ci"), nullable=False
    )
    descricao = db.Column(db.Text, nullable=True)
    materia_id = db.Column(
        db.Integer,
        db.ForeignKey("materias.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    status = db.Column(db.String(20), nullable=False, default="ativa", index=True)
    criado_em = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp(6)
    )
    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(6),
        server_onupdate=db.func.current_timestamp(6),
    )

    materia = db.relationship("Materia", back_populates="assuntos")
    questoes = db.relationship(
        "Questao",
        back_populates="assunto",
        passive_deletes="all",
    )
    transferencias = db.relationship(
        "AssuntoTransferencia", back_populates="assunto", passive_deletes="all"
    )

    campos_atualizaveis = {
        "nome",
        "nome_normalizado",
        "descricao",
        "materia_id",
        "status",
    }

    @classmethod
    def listar_ativos(cls, materia_id=None):
        from app.repositories.catalogo_repository import CatalogoRepository

        return CatalogoRepository.listar_assuntos_ativos(materia_id)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "nome_normalizado": self.nome_normalizado,
            "descricao": self.descricao,
            "materia_id": self.materia_id,
            "status": self.status,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
