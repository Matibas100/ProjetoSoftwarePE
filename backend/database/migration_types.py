"""Tipos compartilhados pelo runner e seus módulos de infraestrutura."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class MigrationError(RuntimeError):
    """Erro operacional seguro, adequado para exibição no terminal."""


@dataclass(frozen=True)
class Migration:
    version: str
    description: str
    script_name: str
    checksum: str
    sql: str
    path: Path
