from sqlalchemy.exc import IntegrityError

from app.exceptions import (
    ConflitoError,
    DadosInvalidosError,
    RecursoNaoEncontradoError,
)
from app.models.materia import Materia


class AtualizarMateriaService:
    @staticmethod
    def executar(materia_id, dados):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados da materia em formato JSON.")

        materia = Materia.buscar_por_id(materia_id)
        if materia is None:
            raise RecursoNaoEncontradoError("Materia nao encontrada.")

        campos_permitidos = {"nome", "descricao"}
        if not campos_permitidos.intersection(dados):
            raise DadosInvalidosError("Informe nome ou descricao para atualizar.")

        dados_atualizacao = {}

        if "nome" in dados:
            nome = dados["nome"]
            if not isinstance(nome, str) or not nome.strip():
                raise DadosInvalidosError("O nome da materia nao pode ser vazio.")
            nome = nome.strip()
            if len(nome) > 100:
                raise DadosInvalidosError(
                    "O nome deve possuir no maximo 100 caracteres."
                )
            dados_atualizacao["nome"] = nome

        if "descricao" in dados:
            descricao = dados["descricao"]
            if descricao is not None and not isinstance(descricao, str):
                raise DadosInvalidosError("A descricao deve ser um texto ou nula.")
            dados_atualizacao["descricao"] = (
                descricao.strip() if isinstance(descricao, str) else None
            )

        try:
            materia.atualizar(**dados_atualizacao)
        except IntegrityError as erro:
            raise ConflitoError("Ja existe uma materia com esse nome.") from erro

        return materia.to_dict()
