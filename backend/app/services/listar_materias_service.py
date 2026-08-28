from app.models.materia import Materia


class ListarMateriasService:
    @staticmethod
    def executar():
        materias = Materia.listar_todos()
        return [materia.to_dict() for materia in materias]
