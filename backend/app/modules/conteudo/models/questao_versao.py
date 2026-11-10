from sqlalchemy import event
from app.extensions import db
from app.core.persistencia import ModeloBase
from app.exceptions import ConflitoError


class QuestaoVersao(ModeloBase):
    """Snapshot editorial append-only; alterações criam outra versão."""

    __tablename__ = "questao_versoes"
    __table_args__ = (
        db.UniqueConstraint("questao_id", "numero", name="uq_questao_versoes_numero"),
        db.CheckConstraint("numero >= 1 AND revisao_origem >= 1", name="ck_questao_versoes_numero"),
        db.CheckConstraint("estado IN ('rascunho','publicada')", name="ck_questao_versoes_estado"),
        db.CheckConstraint("origem IN ('legado','manual')", name="ck_questao_versoes_origem"),
        db.CheckConstraint(
            "resposta_correta IN ('A','B','C','D','E')",
            name="ck_questao_versoes_resposta"
        ),
        db.CheckConstraint(
            "dificuldade IN ('facil','media','dificil')",
            name="ck_questao_versoes_dificuldade"
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    questao_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "questoes.id",
            ondelete="RESTRICT",
            onupdate="RESTRICT"
        ),
        nullable=False
    )
    numero = db.Column(db.Integer, nullable=False)
    revisao_origem = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    enunciado = db.Column(db.Text, nullable=False)
    alternativa_a = db.Column(db.Text, nullable=False)
    alternativa_b = db.Column(db.Text, nullable=False)
    alternativa_c = db.Column(db.Text, nullable=False)
    alternativa_d = db.Column(db.Text, nullable=False)
    alternativa_e = db.Column(db.Text, nullable=False)
    resposta_correta = db.Column(db.CHAR(1), nullable=False)
    explicacao = db.Column(db.Text)
    dificuldade = db.Column(db.String(10), nullable=False)
    assunto_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "assuntos.id",
            ondelete="RESTRICT",
            onupdate="RESTRICT"
        ),
        nullable=False
    )
    assunto_nome = db.Column(db.String(150), nullable=False)
    materia_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "materias.id",
            ondelete="RESTRICT",
            onupdate="RESTRICT"
        ),
        nullable=False
    )
    materia_nome = db.Column(db.String(100), nullable=False)
    area_enem_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "areas_enem.id",
            ondelete="RESTRICT",
            onupdate="RESTRICT"
        ),
        nullable=False
    )
    area_enem_nome = db.Column(db.String(100), nullable=False)
    ator_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id",
            ondelete="RESTRICT",
            onupdate="RESTRICT"
        )
    )
    origem = db.Column(db.String(20), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False)

    def conteudo(self, correcao=False):
        from app.modules.conteudo.models.questao import Questao
        dados = {campo: getattr(self, campo) for campo in Questao.campos_atualizaveis}
        if not correcao:
            dados.pop("resposta_correta")
            dados.pop("explicacao")
        dados.update(
            questao_id=self.questao_id,
            questao_versao_id=self.id,
            assunto={"id": self.assunto_id, "nome": self.assunto_nome},
            materia={"id": self.materia_id, "nome": self.materia_nome},
            area_enem={"id": self.area_enem_id, "nome": self.area_enem_nome}
        )
        return dados


@event.listens_for(QuestaoVersao, "before_update")
@event.listens_for(QuestaoVersao, "before_delete")
def impedir_mutacao_snapshot(mapper, connection, target):
    raise ConflitoError("Snapshots editoriais são append-only.")
