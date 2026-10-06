from app.models.materia import Materia


class ListarMateriasService:
    @staticmethod
    def executar(incluir_inativos=False):
        materias = (
            Materia.listar_todos()
            if incluir_inativos
            else Materia.listar_ativos()
        )
        return [materia.to_dict() for materia in materias]
