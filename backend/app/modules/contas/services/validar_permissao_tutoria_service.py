"""Exige somente uso vigente e encerra a leitura antes da rede externa."""
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.domain.privacidade import aceite_vigente
from app.modules.contas.repositories.privacidade_repository import PrivacidadeRepository
from app.transaction_manager import TransactionManager


class ValidarPermissaoTutoriaService:
    @staticmethod
    def executar(usuario_id):
        def conferir():
            PrivacidadeRepository.bloquear_usuario(usuario_id)
            if not aceite_vigente(PrivacidadeRepository.ultimas(usuario_id)['uso'], 'uso'):
                raise AutenticacaoError('Aceite o Termo de Uso vigente na página de privacidade.',
                                       409, 'termos_uso_pendentes')
        TransactionManager.executar(conferir)
