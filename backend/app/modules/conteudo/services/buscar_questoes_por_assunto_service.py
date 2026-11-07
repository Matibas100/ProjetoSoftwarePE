from app.exceptions import DadosInvalidosError, RecursoNaoEncontradoError
from typing import Callable
from app.contracts.questoes import ConsultaQuestoesPorAssunto


class BuscarQuestoesPorAssuntoService:
    def __init__(self, consulta: ConsultaQuestoesPorAssunto, assunto_existe: Callable[[int], bool]):
        self._consulta = consulta
        self._assunto_existe = assunto_existe

    def executar(self, assunto_id):
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

        if not self._assunto_existe(assunto_id):
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")

        return self._consulta.buscar_por_assunto(assunto_id)
