"""Composição editorial e tentativas do domínio de simulados."""
from sqlalchemy import event
from sqlalchemy.dialects.mysql import DATETIME
from app.extensions import db
from app.exceptions import ConflitoError
from app.core.persistencia import CrudMixin, ModeloBase


def referencia(tabela, tipo=db.Integer, **opcoes):
    return db.Column(tipo, db.ForeignKey(tabela + ".id", ondelete="RESTRICT", onupdate="RESTRICT"), **opcoes)


class Simulado(CrudMixin):
    __tablename__ = "simulados"
    __table_args__ = (
        db.CheckConstraint("estado IN ('rascunho','publicado','arquivado')", name="ck_simulados_estado"),
        db.CheckConstraint("revisao >= 1", name="ck_simulados_revisao"),
    )
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    revisao = db.Column(db.Integer, nullable=False)
    autor_id = referencia("usuarios", nullable=False)
    criado_em = db.Column(DATETIME(fsp=6), nullable=False)
    atualizado_em = db.Column(DATETIME(fsp=6), nullable=False)
    simulado_versao_id = referencia("simulado_versoes")


class SimuladoRascunhoItem(CrudMixin):
    __tablename__ = "simulado_rascunho_itens"
    __table_args__ = (
        db.UniqueConstraint("simulado_id", "posicao", name="uq_sim_rascunho_posicao"),
        db.UniqueConstraint("simulado_id", "questao_id", name="uq_sim_rascunho_questao"),
        db.CheckConstraint("posicao BETWEEN 1 AND 180", name="ck_sim_rascunho_posicao"),
    )
    id = db.Column(db.Integer, primary_key=True)
    simulado_id = referencia("simulados", nullable=False)
    posicao = db.Column(db.Integer, nullable=False)
    questao_id = referencia("questoes", nullable=False)
    questao_versao_id = referencia("questao_versoes", nullable=False)


class SimuladoVersao(ModeloBase):
    __tablename__ = "simulado_versoes"
    __table_args__ = (
        db.UniqueConstraint("simulado_id", "numero", name="uq_sim_versao_numero"),
        db.UniqueConstraint("simulado_id", "revisao_origem", name="uq_sim_versao_revisao"),
        db.CheckConstraint("numero >= 1 AND revisao_origem >= 1", name="ck_sim_versao_numero"),
    )
    id = db.Column(db.Integer, primary_key=True)
    simulado_id = referencia("simulados", nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    revisao_origem = db.Column(db.Integer, nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    autor_id = referencia("usuarios", nullable=False)
    criado_em = db.Column(DATETIME(fsp=6), nullable=False)


class SimuladoVersaoItem(ModeloBase):
    __tablename__ = "simulado_versao_itens"
    __table_args__ = (
        db.UniqueConstraint("simulado_versao_id", "posicao", name="uq_sim_item_posicao"),
        db.UniqueConstraint("simulado_versao_id", "questao_id", name="uq_sim_item_questao"),
        db.CheckConstraint("posicao BETWEEN 1 AND 180", name="ck_sim_item_posicao"),
    )
    id = db.Column(db.Integer, primary_key=True)
    simulado_versao_id = referencia("simulado_versoes", nullable=False)
    posicao = db.Column(db.Integer, nullable=False)
    questao_id = referencia("questoes", nullable=False)
    questao_versao_id = referencia("questao_versoes", nullable=False)


class SimuladoEvento(ModeloBase):
    __tablename__ = "simulado_eventos"
    id = db.Column(db.BigInteger, primary_key=True)
    simulado_id = referencia("simulados", nullable=False)
    versao_id = referencia("simulado_versoes")
    ator_id = referencia("usuarios", nullable=False)
    acao = db.Column(db.String(30), nullable=False)
    motivo = db.Column(db.String(500), nullable=False)
    criado_em = db.Column(DATETIME(fsp=6), nullable=False)


class SimuladoTentativa(CrudMixin):
    __tablename__ = "simulado_tentativas"
    __table_args__ = (
        db.UniqueConstraint("usuario_id", "chave_envio", name="uq_sim_tentativa_chave"),
        db.UniqueConstraint("usuario_id", "simulado_versao_id", "em_andamento_marcador", name="uq_sim_tentativa_andamento"),
        db.Index("ix_sim_tentativa_historico", "usuario_id", "finalizada_em", "id"),
        db.CheckConstraint("revisao >= 1", name="ck_sim_tentativa_revisao"),
        db.CheckConstraint("(estado = 'em_andamento' AND finalizada_em IS NULL AND total IS NULL AND respondidas IS NULL AND acertos IS NULL AND erros IS NULL AND em_branco IS NULL AND percentual_acerto IS NULL) OR (estado = 'finalizada' AND finalizada_em IS NOT NULL AND finalizada_em >= iniciada_em AND total IS NOT NULL AND total BETWEEN 1 AND 180 AND respondidas IS NOT NULL AND acertos IS NOT NULL AND erros IS NOT NULL AND em_branco IS NOT NULL AND percentual_acerto IS NOT NULL AND acertos >= 0 AND erros >= 0 AND em_branco >= 0 AND total = acertos + erros + em_branco AND respondidas = acertos + erros AND percentual_acerto = ROUND(100 * acertos / total, 2))", name="ck_sim_tentativa_estado"),
    )
    id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = referencia("usuarios", nullable=False)
    simulado_versao_id = referencia("simulado_versoes", nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    revisao = db.Column(db.Integer, nullable=False)
    chave_envio = db.Column(db.CHAR(36, collation="ascii_bin"), nullable=False)
    iniciada_em = db.Column(DATETIME(fsp=6), nullable=False)
    finalizada_em = db.Column(DATETIME(fsp=6))
    total = db.Column(db.Integer)
    respondidas = db.Column(db.Integer)
    acertos = db.Column(db.Integer)
    erros = db.Column(db.Integer)
    em_branco = db.Column(db.Integer)
    percentual_acerto = db.Column(db.Numeric(5, 2))
    em_andamento_marcador = db.Column(db.Integer, db.Computed("CASE WHEN estado = 'em_andamento' THEN 1 ELSE NULL END", persisted=True))

    def resultado(self):
        return {**{c: getattr(self, c) for c in ("total", "respondidas", "acertos", "erros", "em_branco")},
                "percentual_acerto": float(self.percentual_acerto), "finalizada_em": self.finalizada_em.isoformat() + "Z"}


class SimuladoResposta(CrudMixin):
    __tablename__ = "simulado_respostas"
    __table_args__ = (
        db.UniqueConstraint("tentativa_id", "item_id", name="uq_sim_resposta_item"),
        db.CheckConstraint("alternativa IS NULL OR alternativa IN ('A','B','C','D','E')", name="ck_sim_resposta_alternativa"),
        db.CheckConstraint("correta IS NULL OR correta IN (0,1)", name="ck_sim_resposta_correta"),
    )
    id = db.Column(db.BigInteger, primary_key=True)
    tentativa_id = referencia("simulado_tentativas", db.BigInteger, nullable=False)
    item_id = referencia("simulado_versao_itens", nullable=False)
    alternativa = db.Column(db.CHAR(1, collation="ascii_bin"))
    correta = db.Column(db.Boolean)


def impedir_mutacao(mapper, connection, target):
    raise ConflitoError("Composição e eventos publicados são imutáveis.")


for entidade in (SimuladoVersao, SimuladoVersaoItem, SimuladoEvento):
    event.listen(entidade, "before_update", impedir_mutacao)
    event.listen(entidade, "before_delete", impedir_mutacao)
