"""Versão estudada e única resposta definitiva de uma prática."""
from sqlalchemy.dialects.mysql import DATETIME
from app.extensions import db
from app.core.persistencia import CrudMixin


class PraticaTentativa(CrudMixin):
    __tablename__ = "pratica_tentativas"
    __table_args__ = (
        db.UniqueConstraint("usuario_id", "chave_envio", name="uq_pratica_tentativas_chave"),
        db.Index("ix_pratica_tentativas_historico", "usuario_id", "respondida_em", "id"),
        db.CheckConstraint("(estado = 'em_andamento' AND resposta_escolhida IS NULL AND correta IS NULL AND respondida_em IS NULL) OR (estado = 'respondida' AND resposta_escolhida IS NOT NULL AND resposta_escolhida IN ('A','B','C','D','E') AND correta IS NOT NULL AND correta IN (0,1) AND respondida_em IS NOT NULL AND respondida_em >= iniciada_em)", name="ck_pratica_tentativas_estado"),
    )
    id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    questao_versao_id = db.Column(db.Integer, db.ForeignKey("questao_versoes.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    chave_envio = db.Column(db.CHAR(36, collation="ascii_bin"), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    resposta_escolhida = db.Column(db.CHAR(1, collation="ascii_bin"))
    correta = db.Column(db.Boolean)
    iniciada_em = db.Column(DATETIME(fsp=6), nullable=False)
    respondida_em = db.Column(DATETIME(fsp=6))
    assunto_id = db.Column(db.Integer, db.ForeignKey("assuntos.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    assunto_nome = db.Column(db.String(150), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    materia_nome = db.Column(db.String(100), nullable=False)

    def classificacao(self):
        return {"assunto": {"id": self.assunto_id, "nome": self.assunto_nome},
                "materia": {"id": self.materia_id, "nome": self.materia_nome}}

    def resumo(self):
        return {"id": self.id, "questao_versao_id": self.questao_versao_id,
                "resposta_escolhida": self.resposta_escolhida, "correta": self.correta,
                "respondida_em": self.respondida_em.isoformat() + "Z", **self.classificacao()}
