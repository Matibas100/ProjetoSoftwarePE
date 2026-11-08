"""Interfaces especializadas de Contas na sessão/transação do caso de uso."""
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm.attributes import set_committed_value

from app.core.procedures_mysql import conferir_resultados, executar_resultados
from app.extensions import db
from app.modules.contas.models.auth_limite import AuthLimite
from app.modules.contas.models.sessao import Sessao
from app.modules.contas.models.usuario import Usuario


class AutenticacaoRepository:
    @staticmethod
    def buscar_por_email(email):
        db.session.flush()
        resultado = db.session.execute(select(Usuario).from_statement(
            text('CALL sp_usuario_por_email(:email)').columns(*Usuario.__table__.columns)), {'email': email})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def consultar_sessao(identificador_hash):
        db.session.flush()
        resultado = db.session.execute(select(Sessao).options(contains_eager(Sessao.usuario)).from_statement(
            text('CALL sp_consultar_sessao(:hash)').columns(*Sessao.__table__.columns, *Usuario.__table__.columns))
            .execution_options(populate_existing=True), {'hash': identificador_hash})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def renovar_acesso(sessao_id, agora):
        db.session.flush()
        resultados = executar_resultados(db.session.connection(),
            'CALL sp_renovar_acesso_sessao(%s,%s)', (sessao_id, agora))
        linhas, = conferir_resultados(resultados, [('correspondencias',)])
        linha, = linhas
        renovada = linha['correspondencias'] == 1
        if renovada:
            for entidade in list(db.session.identity_map.values()):
                if isinstance(entidade, Sessao) and inspect(entidade).identity == (sessao_id,):
                    set_committed_value(entidade, 'ultimo_acesso_em', agora)
        return renovada

    @staticmethod
    def revogar(sessao_id, agora):
        db.session.flush()
        resultados = executar_resultados(db.session.connection(), 'CALL sp_revogar_sessao(%s,%s)', (sessao_id, agora))
        linhas, = conferir_resultados(resultados, [('afetadas',)])
        _, = linhas
        for entidade in list(db.session.identity_map.values()):
            if isinstance(entidade, Sessao) and inspect(entidade).identity == (sessao_id,):
                # Releitura seletiva conserva o instante original de revogação repetida.
                db.session.expire(entidade, ['revogada_em'])

    @staticmethod
    def revogar_usuario(usuario_id, agora):
        db.session.flush()
        resultados = executar_resultados(db.session.connection(),
            'CALL sp_revogar_sessoes_usuario(%s,%s)', (usuario_id, agora))
        linhas, = conferir_resultados(resultados, [('afetadas',)])
        linha, = linhas
        for entidade in list(db.session.identity_map.values()):
            if isinstance(entidade, Sessao) and entidade.usuario_id == usuario_id:
                db.session.expire(entidade, ['revogada_em'])
        return int(linha['afetadas'])

    @staticmethod
    def usuario_ativo_bloqueado(usuario_id):
        db.session.flush()
        resultado = db.session.execute(select(Usuario).from_statement(
            text('CALL sp_usuario_ativo_bloqueado(:id)').columns(*Usuario.__table__.columns))
            .execution_options(populate_existing=True), {'id': usuario_id})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def limite_bloqueado(chave_hash, agora):
        db.session.flush()
        resultado = db.session.execute(select(AuthLimite).from_statement(
            text('CALL sp_preparar_limite_autenticacao(:chave,:agora)').columns(*AuthLimite.__table__.columns))
            .execution_options(populate_existing=True), {'chave': chave_hash, 'agora': agora})
        try:
            return resultado.scalar_one()
        finally:
            resultado.close()

    @staticmethod
    def limpar(agora):
        db.session.flush()
        resultados = executar_resultados(db.session.connection(), 'CALL sp_limpar_autenticacao(%s)', (agora,))
        linhas, = conferir_resultados(resultados, [('sessoes', 'limites')])
        linha, = linhas
        for entidade in list(db.session.identity_map.values()):
            if isinstance(entidade, (Sessao, AuthLimite)):
                db.session.expire(entidade)
        return {nome: int(linha[nome]) for nome in ('sessoes', 'limites')}
