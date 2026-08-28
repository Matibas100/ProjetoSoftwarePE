from app.models.assunto import Assunto


class ListarAssuntosService:
    @staticmethod
    def executar():
        assuntos = Assunto.listar_todos()
        return [assunto.to_dict() for assunto in assuntos]
