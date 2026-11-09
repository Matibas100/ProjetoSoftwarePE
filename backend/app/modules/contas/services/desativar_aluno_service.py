from app.core.relogio import agora_utc
from app.modules.contas.domain.gestao_alunos import validar_id, exigir_aluno, apresentar_usuario
from app.modules.contas.repositories.usuario_repository import UsuarioRepository
from app.modules.contas.repositories.autenticacao_repository import AutenticacaoRepository
from app.modules.contas.services.gestao_alunos_validacao import confirmar_acao, executar_mutacao


class DesativarAlunoService:
    @staticmethod
    def executar(usuario_id,dados):
        validar_id(usuario_id)
        def desativar():
            usuario = exigir_aluno(UsuarioRepository.bloquear(usuario_id))
            confirmar_acao(dados)
            usuario.atualizar(confirmar=False,ativo=False)
            AutenticacaoRepository.revogar_usuario(usuario_id,agora_utc())
            return apresentar_usuario(usuario)
        return executar_mutacao(desativar)
