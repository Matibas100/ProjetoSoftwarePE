from decimal import Decimal, ROUND_HALF_UP
from app.domain.autenticacao import agora_utc
from app.exceptions import DadosInvalidosError
from app.services.pratica_validacao import corpo
from app.services.simulado_validacao import revisao, conferir_revisao
from app.services.consultar_simulado_service import propria
from app.services.gestao_questao_service import ConsultarVersaoHistoricaService
from app.repositories.simulado_repository import SimuladoRepository as Repo
from app.transaction_manager import TransactionManager


class FinalizarSimuladoService:
    @staticmethod
    def executar(usuario_id, tentativa_id, dados):
        corpo(dados, {"revisao", "confirmar"}); valor = revisao(dados)
        if dados["confirmar"] is not True:
            raise DadosInvalidosError("Confirme explicitamente a finalização.")
        def operacao():
            t = propria(usuario_id, tentativa_id, bloquear=True)
            if t.estado == "finalizada":
                return t.resultado()
            conferir_revisao(t, valor)
            respostas = Repo.respostas(t.id, bloquear=True)
            acertos = erros = brancos = 0
            for r, i in respostas:
                if r.alternativa is None:
                    brancos += 1
                else:
                    q = ConsultarVersaoHistoricaService.executar(i.questao_versao_id, correcao=True)
                    r.correta = r.alternativa == q["resposta_correta"]
                    acertos += int(r.correta); erros += int(not r.correta)
                    r.salvar(confirmar=False)
            t.total = len(respostas); t.respondidas = acertos + erros
            t.acertos = acertos; t.erros = erros; t.em_branco = brancos
            t.percentual_acerto = (Decimal(100) * acertos / t.total).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
            t.finalizada_em = agora_utc(); t.estado = "finalizada"; t.revisao += 1
            t.salvar(confirmar=False)
            return t.resultado()
        return TransactionManager.executar(operacao)
