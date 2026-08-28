from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, DadosInvalidosError, RecursoNaoEncontradoError
from app.models.assunto import Assunto
from app.models.materia import Materia


class CriarAssuntoService:
    @staticmethod
    def executar(dados):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados do assunto em formato JSON.")

        nome = dados.get("nome")
        if not isinstance(nome, str) or not nome.strip():
            raise DadosInvalidosError("O nome do assunto e obrigatorio.")

        nome = nome.strip()
        if len(nome) > 150:
            raise DadosInvalidosError("O nome deve possuir no maximo 150 caracteres.")

        materia_id = dados.get("materia_id")
        if (
            not isinstance(materia_id, int)
            or isinstance(materia_id, bool)
            or materia_id <= 0
        ):
            raise DadosInvalidosError("materia_id deve ser um numero inteiro valido.")

        if Materia.buscar_por_id(materia_id) is None:
            raise RecursoNaoEncontradoError("Materia nao encontrada.")

        descricao = dados.get("descricao")
        if descricao is not None and not isinstance(descricao, str):
            raise DadosInvalidosError("A descricao deve ser um texto ou nula.")

        assunto = Assunto(
            nome=nome,
            descricao=descricao.strip() if isinstance(descricao, str) else None,
            materia_id=materia_id,
        )

        try:
            assunto.salvar()
        except IntegrityError as erro:
            raise ConflitoError(
                "Nao foi possivel cadastrar o assunto por conflito de integridade."
            ) from erro

        return assunto.to_dict()
