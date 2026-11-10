from app.exceptions import RecursoNaoEncontradoError
from app.modules.praticas.repositories.pratica_repository import PraticaRepository
from app.modules.conteudo.api import ConsultarVersaoHistoricaService


def exigir_propria(usuario_id, tentativa_id, bloquear=False):
    tentativa = PraticaRepository.propria(usuario_id, tentativa_id, bloquear)
    if tentativa is None:
        raise RecursoNaoEncontradoError("Tentativa não encontrada.")
    return tentativa


def detalhe(tentativa):
    respondida = tentativa.estado == "respondida"
    questao = ConsultarVersaoHistoricaService.executar(
        tentativa.questao_versao_id,
        correcao=respondida
    )
    questao.update(tentativa.classificacao())
    dados = {"id": tentativa.id, "estado": tentativa.estado, "questao": questao}
    if respondida:
        dados.update(
            tentativa.resumo(),
            gabarito=questao["resposta_correta"],
            explicacao=questao["explicacao"]
        )
    return dados


class ConsultarPraticaService:
    @staticmethod
    def executar(usuario_id, tentativa_id):
        return detalhe(exigir_propria(usuario_id, tentativa_id))
