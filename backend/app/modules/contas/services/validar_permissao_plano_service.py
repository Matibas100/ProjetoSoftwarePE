from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.domain.privacidade import estado_privacidade
from app.modules.contas.repositories.privacidade_repository import PrivacidadeRepository


class ValidarPermissaoPlanoService:
    @staticmethod
    def executar(usuario_id):
        # O caso do plano já mantém o mesmo lock de usuário nesta transação.
        if not estado_privacidade(PrivacidadeRepository.ultimas(usuario_id))["plano_liberado"]:
            raise AutenticacaoError(
                "Autorize o plano na página de privacidade para continuar.",
                403,
                "consentimento_plano_necessario"
            )
