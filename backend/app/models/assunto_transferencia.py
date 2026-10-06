from app.extensions import db
from app.models.crud_mixin import CrudMixin


class AssuntoTransferencia(CrudMixin):
    __tablename__ = "assunto_transferencias"
    __table_args__ = (
        db.CheckConstraint("questoes_impactadas >= 0", name="ck_transferencias_questoes"),
        db.CheckConstraint(
            "materia_origem_id <> materia_destino_id", name="ck_transferencias_materias"
        ),
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    assunto_id = db.Column(
        db.Integer,
        db.ForeignKey("assuntos.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    materia_origem_id = db.Column(
        db.Integer,
        db.ForeignKey("materias.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    materia_destino_id = db.Column(
        db.Integer,
        db.ForeignKey("materias.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    questoes_impactadas = db.Column(db.Integer, nullable=False)
    criado_em = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp(6)
    )
    assunto = db.relationship("Assunto", back_populates="transferencias")
    materia_origem = db.relationship("Materia", foreign_keys=[materia_origem_id])
    materia_destino = db.relationship("Materia", foreign_keys=[materia_destino_id])
    campos_atualizaveis = frozenset()

    def to_dict(self):
        return {
            "id": self.id,
            "assunto_id": self.assunto_id,
            "materia_origem_id": self.materia_origem_id,
            "materia_destino_id": self.materia_destino_id,
            "questoes_impactadas": self.questoes_impactadas,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
