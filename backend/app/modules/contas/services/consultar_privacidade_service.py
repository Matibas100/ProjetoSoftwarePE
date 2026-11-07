from app.modules.contas.domain.privacidade import estado_privacidade
from app.modules.contas.repositories.privacidade_repository import PrivacidadeRepository as Repo
from app.transaction_manager import TransactionManager


class ConsultarPrivacidadeService:
    @staticmethod
    def executar(usuario_id):
        def consultar():
            Repo.bloquear_usuario(usuario_id)
            return estado_privacidade(Repo.ultimas(usuario_id))
        return TransactionManager.executar(consultar)
