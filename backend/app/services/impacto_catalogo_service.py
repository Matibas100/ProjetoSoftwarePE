from app.exceptions import RecursoNaoEncontradoError
from app.models.assunto import Assunto
from app.models.materia import Materia
from app.repositories.catalogo_repository import CatalogoRepository


class ImpactoMateriaService:
    @staticmethod
    def executar(materia_id):
        if Materia.buscar_por_id(materia_id) is None:
            raise RecursoNaoEncontradoError("Materia nao encontrada.")
        return {"materia_id": materia_id, "impacto": CatalogoRepository.impacto_materia(materia_id)}


class ImpactoAssuntoService:
    @staticmethod
    def executar(assunto_id):
        if Assunto.buscar_por_id(assunto_id) is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")
        return {"assunto_id": assunto_id, "impacto": CatalogoRepository.impacto_assunto(assunto_id)}
