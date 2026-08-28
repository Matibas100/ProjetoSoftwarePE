from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, RecursoNaoEncontradoError
from app.models.assunto import Assunto


class DeletarAssuntoService:
    @staticmethod
    def executar(assunto_id):
        assunto = Assunto.buscar_por_id(assunto_id)
        if assunto is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")

        try:
            assunto.deletar()
        except IntegrityError as erro:
            raise ConflitoError(
                "O assunto nao pode ser excluido porque possui questoes vinculadas."
            ) from erro
