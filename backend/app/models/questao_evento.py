from sqlalchemy import event
from app.extensions import db
from app.models.crud_mixin import ModeloBase
from app.exceptions import ConflitoError


class QuestaoEvento(ModeloBase):
    __tablename__ = "questao_eventos"
    __table_args__ = (db.CheckConstraint("acao IN ('cadastro','edicao','revisao','aprovacao','publicacao','arquivamento')", name="ck_questao_eventos_acao"),)
    id = db.Column(db.BigInteger, primary_key=True)
    questao_id = db.Column(db.Integer, db.ForeignKey("questoes.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False, index=True)
    versao_id = db.Column(db.Integer, db.ForeignKey("questao_versoes.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    ator_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    acao = db.Column(db.String(20), nullable=False)
    motivo = db.Column(db.String(500), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False)



@event.listens_for(QuestaoEvento, "before_update")
@event.listens_for(QuestaoEvento, "before_delete")
def impedir_mutacao_evento(mapper, connection, target):
    raise ConflitoError("Eventos editoriais são append-only.")
