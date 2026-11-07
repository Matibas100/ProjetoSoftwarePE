from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, DadosInvalidosError, RecursoNaoEncontradoError
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.domain.catalogo import normalizar_nome_assunto
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository
from app.modules.conteudo.services.catalogo_validacao import validar_descricao, validar_id, validar_nome


class CriarAssuntoService:
    @staticmethod
    def executar(dados):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados do assunto em formato JSON.")

        nome = validar_nome(dados.get("nome"), "do assunto", 150)
        nome_normalizado = normalizar_nome_assunto(nome)
        materia_id = validar_id(dados.get("materia_id"), "materia_id")
        materia = Materia.buscar_por_id(materia_id)
        if materia is None:
            raise RecursoNaoEncontradoError("Materia nao encontrada.")
        if materia.status != "ativa":
            raise DadosInvalidosError("A materia precisa estar ativa para receber assuntos.")
        if CatalogoRepository.existe_assunto_equivalente(materia_id, nome_normalizado):
            raise ConflitoError("Ja existe um assunto equivalente nesta materia.")
        descricao = validar_descricao(dados.get("descricao"))

        assunto = Assunto(
            nome=nome,
            nome_normalizado=nome_normalizado,
            descricao=descricao,
            materia_id=materia_id,
            status="ativa",
        )

        try:
            assunto.salvar()
        except IntegrityError as erro:
            raise ConflitoError(
                "Ja existe um assunto equivalente nesta materia."
            ) from erro

        return assunto.to_dict()
