from app.models.assunto import Assunto
from app.repositories.catalogo_repository import CatalogoRepository


class ListarAssuntosService:
    @staticmethod
    def executar(incluir_inativos=False, materia_id=None):
        assuntos = (
            Assunto.listar_todos()
            if incluir_inativos
            else CatalogoRepository.listar_assuntos_ativos(materia_id)
        )
        return [assunto.to_dict() for assunto in assuntos]
