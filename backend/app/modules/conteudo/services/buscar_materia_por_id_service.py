from app.exceptions import DadosInvalidosError, RecursoNaoEncontradoError
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.services.catalogo_validacao import validar_id


class BuscarMateriaPorIdService:
    @staticmethod
    def executar(materia_id):
        validar_id(materia_id, "materia_id")
        if materia_id > 2147483647:
            raise DadosInvalidosError("materia_id deve ser no maximo 2147483647.")
        materia = Materia.buscar_por_id(materia_id)
        if materia is None:
            raise RecursoNaoEncontradoError("Materia nao encontrada.")
        return materia.to_dict()
