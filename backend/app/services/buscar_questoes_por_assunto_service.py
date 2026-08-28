from app.exceptions import DadosInvalidosError, RecursoNaoEncontradoError
from app.models.assunto import Assunto
from app.repositories.questao_repository import QuestaoRepository


class BuscarQuestoesPorAssuntoService:
    @staticmethod
    def executar(assunto_id):
        if assunto_id is None:
            raise DadosInvalidosError("O parametro assunto_id e obrigatorio.")

        try:
            assunto_id = int(assunto_id)
        except (TypeError, ValueError) as erro:
            raise DadosInvalidosError(
                "assunto_id deve ser um numero inteiro valido."
            ) from erro

        if assunto_id <= 0:
            raise DadosInvalidosError("assunto_id deve ser um numero inteiro valido.")

        if Assunto.buscar_por_id(assunto_id) is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")

        return QuestaoRepository.buscar_por_assunto(assunto_id)
