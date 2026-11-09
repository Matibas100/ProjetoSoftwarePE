"""Contrato textual de tutoria; sem identidade, ORM ou histórico."""
from typing import Protocol, TypedDict


class EntradaTutoria(TypedDict):
    disciplina: str
    nivel: str
    assunto: str
    duvida: str


class RespostaTutoria(TypedDict):
    disciplina: str
    assunto: str
    resposta: str


class GeradorTutoria(Protocol):
    @property
    def disponivel(self) -> bool: ...

    def gerar(self, entrada: EntradaTutoria, instrucao: str) -> str: ...
