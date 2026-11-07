from app.extensions import db
from app.core.persistencia import CrudMixin


class AreaEnem(CrudMixin):
    __tablename__ = "areas_enem"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    ordem = db.Column(db.SmallInteger, nullable=False, unique=True)
    materias = db.relationship(
        "Materia", back_populates="area_enem", passive_deletes="all"
    )
    campos_atualizaveis = frozenset()

    @classmethod
    def listar_ordenadas(cls):
        return db.session.execute(db.select(cls).order_by(cls.ordem, cls.id)).scalars().all()

    def to_dict(self):
        return {"id": self.id, "codigo": self.codigo, "nome": self.nome, "ordem": self.ordem}
