from app.modules.contas.services.autenticacao_service import preparar_usuario
from app.modules.contas.services.gestao_alunos_validacao import executar_mutacao
from app.modules.contas.domain.gestao_alunos import apresentar_usuario


class CriarAlunoAdminService:
    @staticmethod
    def executar(dados):
        usuario = preparar_usuario(dados, 'aluno')
        return executar_mutacao(lambda: apresentar_usuario(usuario.salvar(confirmar=False)))
