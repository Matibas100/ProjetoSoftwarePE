"""Registros já representados, sem entidades ORM ou envelope HTTP."""
from typing import Mapping, Protocol, TypedDict

FiltrosCatalogo = Mapping[str, str | int | None]


class Referencia(TypedDict):
    id: int
    nome: str


class AreaRegistro(Referencia):
    codigo: str
    ordem: int


class MateriaRegistro(Referencia):
    descricao: str | None
    area_enem_id: int
    status: str
    criado_em: str | None
    atualizado_em: str | None


class AssuntoRegistro(Referencia):
    nome_normalizado: str
    descricao: str | None
    materia_id: int
    status: str
    criado_em: str | None
    atualizado_em: str | None


class MateriaAdminRegistro(MateriaRegistro):
    area_enem: AreaRegistro
    assuntos: int
    questoes: int


class AssuntoAdminRegistro(AssuntoRegistro):
    materia: MateriaRegistro
    area_enem: AreaRegistro
    questoes: int


class ConsultaMateriasAdmin(Protocol):
    def listar(self, filtros: FiltrosCatalogo, pagina: int, limite: int) -> tuple[list[MateriaAdminRegistro], int]: ...


class ConsultaAssuntosAdmin(Protocol):
    def listar(self, filtros: FiltrosCatalogo, pagina: int, limite: int) -> tuple[list[AssuntoAdminRegistro], int]: ...
