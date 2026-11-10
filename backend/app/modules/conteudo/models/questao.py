from app.extensions import db
from app.core.persistencia import CrudMixin


class Questao(CrudMixin):
    __tablename__ = "questoes"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('rascunho','publicada','arquivada')",
            name="ck_questoes_status"
        ),
        db.CheckConstraint("revisao >= 1", name="ck_questoes_revisao"),
        db.CheckConstraint(
            "resposta_correta IN ('A', 'B', 'C', 'D', 'E')",
            name="ck_questoes_resposta_correta",
        ),
        db.CheckConstraint(
            "dificuldade IN ('facil', 'media', 'dificil')",
            name="ck_questoes_dificuldade",
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(20), nullable=False, default="rascunho", index=True)
    revisao = db.Column(db.Integer, nullable=False, default=1)
    criado_em = db.Column(db.DateTime)
    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(6)
    )
    versao_publicada_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "questao_versoes.id",
            ondelete="RESTRICT",
            onupdate="RESTRICT"
        )
    )
    enunciado = db.Column(db.Text, nullable=False)
    alternativa_a = db.Column(db.Text, nullable=False)
    alternativa_b = db.Column(db.Text, nullable=False)
    alternativa_c = db.Column(db.Text, nullable=False)
    alternativa_d = db.Column(db.Text, nullable=False)
    alternativa_e = db.Column(db.Text, nullable=False)
    resposta_correta = db.Column(db.CHAR(1), nullable=False)
    explicacao = db.Column(db.Text, nullable=True)
    dificuldade = db.Column(db.String(10), nullable=False)
    assunto_id = db.Column(
        db.Integer,
        db.ForeignKey("assuntos.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )

    assunto = db.relationship("Assunto", back_populates="questoes")

    campos_atualizaveis = {
        "enunciado",
        "alternativa_a",
        "alternativa_b",
        "alternativa_c",
        "alternativa_d",
        "alternativa_e",
        "resposta_correta",
        "explicacao",
        "dificuldade",
        "assunto_id",
    }

    def to_dict(self):
        return {
            "id": self.id,
            "enunciado": self.enunciado,
            "alternativa_a": self.alternativa_a,
            "alternativa_b": self.alternativa_b,
            "alternativa_c": self.alternativa_c,
            "alternativa_d": self.alternativa_d,
            "alternativa_e": self.alternativa_e,
            "resposta_correta": self.resposta_correta,
            "explicacao": self.explicacao,
            "dificuldade": self.dificuldade,
            "assunto_id": self.assunto_id,
        }
