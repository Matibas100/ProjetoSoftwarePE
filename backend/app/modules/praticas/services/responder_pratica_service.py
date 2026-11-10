from app.core.relogio import agora_utc
from app.exceptions import ConflitoError, DadosInvalidosError
from app.modules.praticas.services.consultar_pratica_service import exigir_propria, detalhe
from app.modules.conteudo.api import ConsultarVersaoHistoricaService
from app.core.validacao import corpo
from app.transaction_manager import TransactionManager


class ResponderPraticaService:
    @staticmethod
    def executar(usuario_id, tentativa_id, dados):
        corpo(dados, {"alternativa"})
        alternativa = dados["alternativa"]
        if not isinstance(alternativa, str) or alternativa not in {"A", "B", "C", "D", "E"}:
            raise DadosInvalidosError("Alternativa deve ser A, B, C, D ou E.")

        def responder():
            tentativa = exigir_propria(usuario_id, tentativa_id, bloquear=True)
            if tentativa.estado == "respondida":
                if tentativa.resposta_escolhida != alternativa:
                    raise ConflitoError("Esta tentativa já possui uma resposta definitiva.")
                return detalhe(tentativa)
            versao = ConsultarVersaoHistoricaService.executar(
                tentativa.questao_versao_id,
                correcao=True
            )
            tentativa.resposta_escolhida = alternativa
            tentativa.correta = alternativa == versao["resposta_correta"]
            tentativa.respondida_em = agora_utc()
            tentativa.estado = "respondida"
            tentativa.salvar(confirmar=False)
            return detalhe(tentativa)
        return TransactionManager.executar(responder)
