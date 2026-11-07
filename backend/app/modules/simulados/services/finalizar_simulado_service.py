from decimal import Decimal, ROUND_HALF_UP
from app.core.relogio import agora_utc
from app.exceptions import DadosInvalidosError
from app.core.validacao import corpo
from app.modules.simulados.services.simulado_validacao import revisao, conferir_revisao
from app.modules.simulados.services.consultar_simulado_service import propria
from app.modules.conteudo.api import ConsultarVersaoHistoricaService
from app.modules.simulados.repositories.simulado_repository import SimuladoRepository as Repo
from app.transaction_manager import TransactionManager


class FinalizarSimuladoService:
    @staticmethod
    def executar(usuario_id, tentativa_id, dados):
        corpo(dados, {"revisao", "confirmar"})
        revisao_recebida = revisao(dados)
        if dados["confirmar"] is not True:
            raise DadosInvalidosError("Confirme explicitamente a finalização.")

        def operacao():
            tentativa = propria(usuario_id, tentativa_id, bloquear=True)
            if tentativa.estado == "finalizada":
                return tentativa.resultado()
            conferir_revisao(tentativa, revisao_recebida)
            respostas = Repo.respostas(tentativa.id, bloquear=True)
            acertos = erros = brancos = 0
            for resposta, item in respostas:
                if resposta.alternativa is None:
                    brancos += 1
                else:
                    versao_historica = ConsultarVersaoHistoricaService.executar(
                        item.questao_versao_id, correcao=True
                    )
                    resposta.correta = (
                        resposta.alternativa == versao_historica["resposta_correta"]
                    )
                    acertos += int(resposta.correta)
                    erros += int(not resposta.correta)
                    resposta.salvar(confirmar=False)
            tentativa.total = len(respostas)
            tentativa.respondidas = acertos + erros
            tentativa.acertos = acertos
            tentativa.erros = erros
            tentativa.em_branco = brancos
            tentativa.percentual_acerto = (
                Decimal(100) * acertos / tentativa.total
            ).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
            tentativa.finalizada_em = agora_utc()
            tentativa.estado = "finalizada"
            tentativa.revisao += 1
            tentativa.salvar(confirmar=False)
            return tentativa.resultado()

        return TransactionManager.executar(operacao)
