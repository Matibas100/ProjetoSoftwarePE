from app.extensions import db
from app.models.crud_mixin import CrudMixin


class Assunto(CrudMixin, db.Model):
    __tablename__ = "assuntos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    materia_id = db.Column(
        db.Integer,
        db.ForeignKey("materias.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    materia = db.relationship("Materia", back_populates="assuntos")
    questoes = db.relationship(
        "Questao",
        back_populates="assunto",
        passive_deletes="all",
    )

    campos_atualizaveis = {"nome", "descricao", "materia_id"}

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "materia_id": self.materia_id,
        }
