from sqlalchemy.exc import IntegrityError

from app.exceptions import (
    ConflitoError,
    DadosInvalidosError,
    RecursoNaoEncontradoError,
)
from app.models.materia import Materia
from app.models.area_enem import AreaEnem
from app.repositories.catalogo_repository import CatalogoRepository
from app.services.catalogo_validacao import (
    validar_descricao,
    validar_id,
    validar_nome,
    validar_status_catalogo,
)


class AtualizarMateriaService:
    @staticmethod
    def executar(materia_id, dados):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados da materia em formato JSON.")

        materia = Materia.buscar_por_id(materia_id)
        if materia is None:
            raise RecursoNaoEncontradoError("Materia nao encontrada.")

        campos_permitidos = {"nome", "descricao", "area_enem_id", "status"}
        if not campos_permitidos.intersection(dados):
            raise DadosInvalidosError("Informe ao menos um campo para atualizar.")

        dados_atualizacao = {}

        if "nome" in dados:
            dados_atualizacao["nome"] = validar_nome(dados["nome"], "da materia", 100)

        if "descricao" in dados:
            dados_atualizacao["descricao"] = validar_descricao(dados["descricao"])

        if "area_enem_id" in dados:
            area_id = validar_id(dados["area_enem_id"], "area_enem_id")
            if AreaEnem.buscar_por_id(area_id) is None:
                raise RecursoNaoEncontradoError("Area do ENEM nao encontrada.")
            dados_atualizacao["area_enem_id"] = area_id

        if "status" in dados:
            status = validar_status_catalogo(dados["status"])
            if status == "arquivada" and CatalogoRepository.contar_assuntos_nao_arquivados(materia_id):
                raise ConflitoError(
                    "Arquive ou transfira os assuntos ativos e inativos antes de arquivar a materia."
                )
            dados_atualizacao["status"] = status

        try:
            materia.atualizar(**dados_atualizacao)
        except IntegrityError as erro:
            raise ConflitoError("Ja existe uma materia com esse nome.") from erro

        return materia.to_dict()
