from app.core.relogio import agora_utc
from app.modules.contas.domain.autenticacao import validar_dados, validar_nome, validar_email
from app.modules.contas.domain.gestao_alunos import validar_id, exigir_aluno, apresentar_usuario
from app.modules.contas.repositories.usuario_repository import UsuarioRepository
from app.modules.contas.repositories.autenticacao_repository import AutenticacaoRepository
from app.modules.contas.services.gestao_alunos_validacao import executar_mutacao


class AtualizarAlunoAdminService:
    @staticmethod
    def executar(usuario_id, dados):
        validar_id(usuario_id)

        def atualizar():
            usuario = exigir_aluno(UsuarioRepository.bloquear(usuario_id))
            validar_dados(dados, {'nome', 'email'})
            nome, email = validar_nome(dados['nome']), validar_email(dados['email'])
            mudou_email = email != usuario.email
            if nome != usuario.nome or mudou_email:
                usuario.atualizar(confirmar=False, nome=nome, email=email)
            if mudou_email:
                AutenticacaoRepository.revogar_usuario(usuario_id, agora_utc())
            return apresentar_usuario(usuario)
        return executar_mutacao(atualizar)
