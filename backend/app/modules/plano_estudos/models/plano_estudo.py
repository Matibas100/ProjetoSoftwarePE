"""Gerações preservadas; somente atual e conclusão podem mudar."""
from sqlalchemy import event, inspect
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import column_property
from app.extensions import db
from app.exceptions import ConflitoError
from app.core.persistencia import ModeloAtualizavel


class PlanoEstudo(ModeloAtualizavel):
    __tablename__ = "planos_estudo"
    __table_args__ = (
        db.UniqueConstraint("usuario_id", "geracao", name="uq_plano_geracao"),
        db.UniqueConstraint("usuario_id", "chave_envio", name="uq_plano_chave"),
        db.UniqueConstraint("usuario_atual", name="uq_plano_atual"),
        db.CheckConstraint("geracao >= 1 AND atual IN (0,1)", name="ck_plano_geracao"),
        db.CheckConstraint("(operacao = 'gerar' AND plano_anterior_id IS NULL) OR (operacao = 'recalcular' AND plano_anterior_id IS NOT NULL)", name="ck_plano_operacao"),
    )
    id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    geracao = db.Column(db.Integer, nullable=False)
    atual = db.Column(db.Boolean, nullable=False)
    usuario_atual = db.Column(db.Integer, db.Computed("CASE WHEN atual = 1 THEN usuario_id ELSE NULL END", persisted=True))
    periodo = db.Column(db.JSON, nullable=False)
    gerado_em = db.Column(DATETIME(fsp=6), nullable=False)
    chave_envio = db.Column(db.CHAR(36, collation="ascii_bin"), nullable=False)
    operacao = db.Column(db.String(12), nullable=False)
    plano_anterior_id = db.Column(db.BigInteger, db.ForeignKey("planos_estudo.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    campos_atualizaveis = {"atual"}


class PlanoEstudoItem(ModeloAtualizavel):
    __tablename__ = "plano_estudo_itens"
    __table_args__ = (
        db.UniqueConstraint("plano_id", "posicao", name="uq_plano_item_posicao"),
        db.UniqueConstraint("plano_id", "assunto_id", name="uq_plano_item_assunto"),
        db.CheckConstraint("posicao BETWEEN 1 AND 3", name="ck_plano_item_posicao"),
        db.CheckConstraint("(estado = 'pendente' AND concluido_em IS NULL) OR (estado = 'concluido' AND concluido_em IS NOT NULL)", name="ck_plano_item_estado"),
    )
    id = db.Column(db.BigInteger, primary_key=True)
    plano_id = db.Column(db.BigInteger, db.ForeignKey("planos_estudo.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    assunto_id = db.Column(db.Integer, db.ForeignKey("assuntos.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    posicao = db.Column(db.Integer, nullable=False)
    snapshot = db.Column(db.JSON, nullable=False)
    estado = column_property(db.Column(db.String(12), nullable=False), active_history=True)
    concluido_em = column_property(db.Column(DATETIME(fsp=6)), active_history=True)
    campos_atualizaveis = {"estado", "concluido_em"}


def preservar(target, permitidos):
    if any(a.history.has_changes() for a in inspect(target).attrs if a.key not in permitidos):
        raise ConflitoError("O snapshot do plano é imutável.")


@event.listens_for(PlanoEstudo, "before_update")
def preservar_plano(mapper, connection, target):
    preservar(target, {"atual"})
    if inspect(target).attrs.atual.history.has_changes() and target.atual:
        raise ConflitoError("Um plano histórico não pode voltar a ser atual.")


@event.listens_for(PlanoEstudoItem, "before_update")
def preservar_item(mapper, connection, target):
    preservar(target, {"estado", "concluido_em"})
    anterior = inspect(target).attrs.estado.history.deleted
    data = inspect(target).attrs.concluido_em.history
    if (anterior and anterior[0] == "concluido") or (data.has_changes() and data.deleted and data.deleted[0] is not None):
        raise ConflitoError("Uma conclusão salva não pode ser alterada.")


@event.listens_for(PlanoEstudo, "before_delete")
@event.listens_for(PlanoEstudoItem, "before_delete")
def impedir_exclusao(mapper, connection, target):
    raise ConflitoError("O histórico do plano deve ser preservado.")
