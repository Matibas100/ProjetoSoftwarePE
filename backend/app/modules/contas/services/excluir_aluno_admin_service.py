from app.modules.contas.domain.gestao_alunos import validar_id, exigir_aluno
from app.modules.contas.repositories.usuario_repository import UsuarioRepository
from app.modules.contas.services.gestao_alunos_validacao import confirmar_acao, executar_mutacao


class ExcluirAlunoAdminService:
    @staticmethod
    def executar(usuario_id, dados):
        validar_id(usuario_id)

        def excluir():
            usuario = exigir_aluno(UsuarioRepository.bloquear(usuario_id))
            confirmar_acao(dados)
            usuario.deletar(confirmar=False)
        return executar_mutacao(excluir)
