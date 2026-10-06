from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, RecursoNaoEncontradoError
from app.models.materia import Materia
from app.repositories.catalogo_repository import CatalogoRepository


class DeletarMateriaService:
    @staticmethod
    def executar(materia_id):
        materia = Materia.buscar_por_id(materia_id)
        if materia is None:
            raise RecursoNaoEncontradoError("Materia nao encontrada.")

        impacto = CatalogoRepository.impacto_materia(materia_id)
        if impacto["assuntos"] or impacto["transferencias"]:
            raise ConflitoError(
                "A materia nao pode ser excluida porque possui vinculos.",
                detalhes={"impacto": impacto},
            )

        try:
            materia.deletar()
        except IntegrityError as erro:
            raise ConflitoError(
                "A materia nao pode ser excluida porque possui assuntos vinculados."
            ) from erro
