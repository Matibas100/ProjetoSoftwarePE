"""Consultas especializadas e locks; commits pertencem ao TransactionManager."""
from datetime import timedelta

from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.modules.contas.models.auth_limite import AuthLimite
from app.modules.contas.models.sessao import Sessao
from app.modules.contas.models.usuario import Usuario


class AutenticacaoRepository:
    @staticmethod
    def consultar_sessao(identificador_hash):
        return db.session.execute(
            db.select(Sessao).options(joinedload(Sessao.usuario))
            .filter_by(identificador_hash=identificador_hash)
            .execution_options(populate_existing=True)
        ).scalar_one_or_none()

    @staticmethod
    def renovar_acesso(sessao_id, agora):
        resultado = db.session.execute(db.update(Sessao).where(
            Sessao.id == sessao_id, Sessao.revogada_em.is_(None), Sessao.expira_em > agora,
            Sessao.ultimo_acesso_em > agora - timedelta(minutes=30),
        ).values(ultimo_acesso_em=agora))
        return resultado.rowcount == 1

    @staticmethod
    def revogar(sessao_id, agora):
        db.session.execute(db.update(Sessao).where(
            Sessao.id == sessao_id, Sessao.revogada_em.is_(None)
        ).values(revogada_em=agora))

    @staticmethod
    def revogar_usuario(usuario_id, agora):
        return db.session.execute(db.update(Sessao).where(
            Sessao.usuario_id == usuario_id, Sessao.revogada_em.is_(None)
        ).values(revogada_em=agora)).rowcount

    @staticmethod
    def usuario_ativo_bloqueado(usuario_id):
        return db.session.execute(db.select(Usuario).where(
            Usuario.id == usuario_id, Usuario.ativo.is_(True)
        ).with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()

    @staticmethod
    def limite_bloqueado(chave_hash, agora):
        # Upsert atomico prepara a chave inclusive sob primeira tentativa concorrente.
        statement = insert(AuthLimite).values(
            chave_hash=chave_hash, falhas=0, janela_inicio=agora
        )
        db.session.execute(statement.on_duplicate_key_update(chave_hash=statement.inserted.chave_hash))
        return db.session.execute(db.select(AuthLimite).filter_by(chave_hash=chave_hash)
            .with_for_update().execution_options(populate_existing=True)).scalar_one()

    @staticmethod
    def limpar(agora):
        corte = agora - timedelta(hours=24)
        inativa = db.and_(Sessao.usuario_id.is_not(None), Sessao.ultimo_acesso_em < corte - timedelta(minutes=30))
        sessoes = db.session.execute(db.delete(Sessao).where(db.or_(
            Sessao.expira_em < corte, Sessao.revogada_em < corte, inativa
        ))).rowcount
        limites = db.session.execute(db.delete(AuthLimite).where(
            AuthLimite.janela_inicio < corte - timedelta(minutes=15),
            db.or_(AuthLimite.bloqueado_ate.is_(None), AuthLimite.bloqueado_ate < corte),
        )).rowcount
        return {"sessoes": sessoes, "limites": limites}
