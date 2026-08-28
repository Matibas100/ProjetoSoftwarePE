from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, RecursoNaoEncontradoError
from app.models.materia import Materia


class DeletarMateriaService:
    @staticmethod
    def executar(materia_id):
        materia = Materia.buscar_por_id(materia_id)
        if materia is None:
            raise RecursoNaoEncontradoError("Materia nao encontrada.")

        try:
            materia.deletar()
        except IntegrityError as erro:
            raise ConflitoError(
                "A materia nao pode ser excluida porque possui assuntos vinculados."
            ) from erro
