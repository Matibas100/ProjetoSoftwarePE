"""Consulta administrativa de Alunos, sem entidades ORM."""
from datetime import datetime
from typing import Protocol, TypedDict


class AlunoAdminRegistro(TypedDict):
    id: int
    nome: str
    email: str
    perfil: str
    ativo: bool
    criado_em: datetime


class ConsultaAlunosAdmin(Protocol):
    def listar(
        self,
        busca: str,
        ativo: bool | None,
        pagina: int,
        limite: int
    ) -> tuple[list[AlunoAdminRegistro], int]:
        ...
