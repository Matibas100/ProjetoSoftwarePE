"""Listagem em snapshot próprio e lock participante, sem CRUD/commit."""
from sqlalchemy import select, text
from app.contexto_leitura import ContextoLeitura
from app.core.procedures_mysql import conferir_resultados
from app.extensions import db
from app.modules.contas.models.usuario import Usuario


class UsuarioRepository:
    @staticmethod
    def listar(busca, ativo, pagina, limite):
        with ContextoLeitura() as contexto:
            resultados = contexto.executar_resultados('CALL sp_alunos_admin(%s,%s,%s,%s)',
                (busca, ativo, (pagina-1)*limite, limite))
            linhas, totais = conferir_resultados(resultados,
                [('id','nome','email','perfil','ativo','criado_em'), ('total_itens',)])
            total, = totais
            return [dict(linha) for linha in linhas], int(total['total_itens'])

    @staticmethod
    def bloquear(usuario_id):
        db.session.flush()
        resultado = db.session.execute(select(Usuario).from_statement(
            text('CALL sp_usuario_gestao_bloqueado(:id)').columns(*Usuario.__table__.columns))
            .execution_options(populate_existing=True), {'id': usuario_id})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()
