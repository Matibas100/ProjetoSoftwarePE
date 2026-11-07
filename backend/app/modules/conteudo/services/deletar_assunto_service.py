from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, RecursoNaoEncontradoError
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository


class DeletarAssuntoService:
    @staticmethod
    def executar(assunto_id):
        assunto = Assunto.buscar_por_id(assunto_id)
        if assunto is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")

        impacto = CatalogoRepository.impacto_assunto(assunto_id)
        if impacto["questoes"] or impacto["transferencias"]:
            raise ConflitoError(
                "O assunto nao pode ser excluido porque possui vinculos.",
                detalhes={"impacto": impacto},
            )

        try:
            assunto.deletar()
        except IntegrityError as erro:
            raise ConflitoError(
                "O assunto nao pode ser excluido porque possui questoes vinculadas."
            ) from erro
