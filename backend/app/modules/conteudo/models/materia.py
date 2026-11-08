from app.extensions import db
from app.core.persistencia import CrudMixin


class Materia(CrudMixin):
    __tablename__ = "materias"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('ativa', 'inativa', 'arquivada')", name="ck_materias_status"
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text, nullable=True)
    area_enem_id = db.Column(
        db.Integer,
        db.ForeignKey("areas_enem.id", ondelete="RESTRICT", onupdate="RESTRICT"),
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

    area_enem = db.relationship("AreaEnem", back_populates="materias")
    assuntos = db.relationship(
        "Assunto",
        back_populates="materia",
        passive_deletes="all",
    )

    campos_atualizaveis = {"nome", "descricao", "area_enem_id", "status"}

    @classmethod
    def listar_ativos(cls):
        from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository

        return CatalogoRepository.listar_materias_ativas()

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "area_enem_id": self.area_enem_id,
            "status": self.status,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
