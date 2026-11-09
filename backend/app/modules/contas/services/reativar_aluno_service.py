from app.modules.contas.domain.gestao_alunos import validar_id, exigir_aluno, apresentar_usuario
from app.modules.contas.repositories.usuario_repository import UsuarioRepository
from app.modules.contas.services.gestao_alunos_validacao import confirmar_acao, executar_mutacao


class ReativarAlunoService:
    @staticmethod
    def executar(usuario_id,dados):
        validar_id(usuario_id)
        def reativar():
            usuario = exigir_aluno(UsuarioRepository.bloquear(usuario_id))
            confirmar_acao(dados)
            usuario.atualizar(confirmar=False,ativo=True)
            return apresentar_usuario(usuario)
        return executar_mutacao(reativar)
