from app.exceptions import DadosInvalidosError, RecursoNaoEncontradoError
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.services.catalogo_validacao import validar_id


class BuscarAssuntoPorIdService:
    @staticmethod
    def executar(assunto_id):
        validar_id(assunto_id, "assunto_id")
        if assunto_id > 2147483647:
            raise DadosInvalidosError("assunto_id deve ser no maximo 2147483647.")
        assunto = Assunto.buscar_por_id(assunto_id)
        if assunto is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")
        return assunto.to_dict()
