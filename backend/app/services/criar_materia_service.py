from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, DadosInvalidosError
from app.models.area_enem import AreaEnem
from app.models.materia import Materia
from app.services.catalogo_validacao import (
    validar_descricao,
    validar_id,
    validar_nome,
    validar_status_catalogo,
)
from app.exceptions import RecursoNaoEncontradoError


class CriarMateriaService:
    @staticmethod
    def executar(dados):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados da materia em formato JSON.")

        nome = validar_nome(dados.get("nome"), "da materia", 100)
        area_enem_id = validar_id(dados.get("area_enem_id"), "area_enem_id")
        if AreaEnem.buscar_por_id(area_enem_id) is None:
            raise RecursoNaoEncontradoError("Area do ENEM nao encontrada.")
        descricao = validar_descricao(dados.get("descricao"))
        status = validar_status_catalogo(dados.get("status", "ativa"))

        materia = Materia(
            nome=nome,
            descricao=descricao,
            area_enem_id=area_enem_id,
            status=status,
        )

        try:
            materia.salvar()
        except IntegrityError as erro:
            raise ConflitoError("Ja existe uma materia com esse nome.") from erro

        return materia.to_dict()
