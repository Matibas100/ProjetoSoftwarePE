from app.extensions import db
from app.models.crud_mixin import CrudMixin


class Materia(CrudMixin):
    __tablename__ = "materias"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text, nullable=True)

    assuntos = db.relationship(
        "Assunto",
        back_populates="materia",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    campos_atualizaveis = {"nome", "descricao"}

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
        }
