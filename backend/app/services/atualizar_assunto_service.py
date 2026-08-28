from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, DadosInvalidosError, RecursoNaoEncontradoError
from app.models.assunto import Assunto
from app.models.materia import Materia


class AtualizarAssuntoService:
    @staticmethod
    def executar(assunto_id, dados):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados do assunto em formato JSON.")

        assunto = Assunto.buscar_por_id(assunto_id)
        if assunto is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")

        campos_permitidos = {"nome", "descricao", "materia_id"}
        if not campos_permitidos.intersection(dados):
            raise DadosInvalidosError(
                "Informe nome, descricao ou materia_id para atualizar."
            )

        dados_atualizacao = {}

        if "nome" in dados:
            nome = dados["nome"]
            if not isinstance(nome, str) or not nome.strip():
                raise DadosInvalidosError("O nome do assunto nao pode ser vazio.")
            nome = nome.strip()
            if len(nome) > 150:
                raise DadosInvalidosError(
                    "O nome deve possuir no maximo 150 caracteres."
                )
            dados_atualizacao["nome"] = nome

        if "descricao" in dados:
            descricao = dados["descricao"]
            if descricao is not None and not isinstance(descricao, str):
                raise DadosInvalidosError("A descricao deve ser um texto ou nula.")
            dados_atualizacao["descricao"] = (
                descricao.strip() if isinstance(descricao, str) else None
            )

        if "materia_id" in dados:
            materia_id = dados["materia_id"]
            if (
                not isinstance(materia_id, int)
                or isinstance(materia_id, bool)
                or materia_id <= 0
            ):
                raise DadosInvalidosError(
                    "materia_id deve ser um numero inteiro valido."
                )
            if Materia.buscar_por_id(materia_id) is None:
                raise RecursoNaoEncontradoError("Materia nao encontrada.")
            dados_atualizacao["materia_id"] = materia_id

        try:
            assunto.atualizar(**dados_atualizacao)
        except IntegrityError as erro:
            raise ConflitoError(
                "Nao foi possivel atualizar o assunto por conflito de integridade."
            ) from erro

        return assunto.to_dict()
