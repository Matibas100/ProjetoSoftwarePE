"""Leitura, validação, separação e execução de scripts SQL oficiais."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Iterable

from database.migration_types import Migration, MigrationError


DEFAULT_MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
MIGRATION_NAME = re.compile(r"^(?P<version>\d{3})_(?P<description>[a-z0-9]+(?:_[a-z0-9]+)*)\.sql$")
FORBIDDEN_CLIENT_COMMAND = re.compile(r"^(?:SOURCE|CONNECT|USE)\b|^\\\.", re.IGNORECASE)


def canonical_sql(raw: bytes, path: Path) -> str:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise MigrationError(f"Migration {path.name} nao esta em UTF-8.") from error
    if text.startswith("\ufeff"):
        raise MigrationError(f"Migration {path.name} nao pode conter BOM.")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def discover_migrations(directory: Path = DEFAULT_MIGRATIONS_DIR) -> list[Migration]:
    if not directory.is_dir():
        raise MigrationError(f"Diretorio de migrations inexistente: {directory}.")

    migrations: list[Migration] = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if path.is_dir() or path.suffix.lower() != ".sql":
            continue
        match = MIGRATION_NAME.fullmatch(path.name)
        if not match:
            raise MigrationError(f"Nome de migration invalido: {path.name}.")
        sql = canonical_sql(path.read_bytes(), path)
        migrations.append(
            Migration(
                version=match.group("version"),
                description=match.group("description"),
                script_name=path.name,
                checksum=hashlib.sha256(sql.encode("utf-8")).hexdigest(),
                sql=sql,
                path=path,
            )
        )

    if not migrations:
        raise MigrationError("Nenhuma migration SQL foi encontrada.")

    seen: set[str] = set()
    for expected, migration in enumerate(sorted(migrations, key=lambda item: item.version)):
        if migration.version in seen:
            raise MigrationError(f"Versao duplicada: {migration.version}.")
        seen.add(migration.version)
        expected_version = f"{expected:03d}"
        if migration.version != expected_version:
            raise MigrationError(
                f"Sequencia invalida: esperado {expected_version}, encontrado {migration.version}."
            )
    return sorted(migrations, key=lambda item: item.version)


def split_sql(sql: str) -> list[str]:
    """Divide SQL respeitando delimitadores, literais, identificadores e comentários."""
    statements: list[str] = []
    buffer: list[str] = []
    delimiter = ";"
    state = "normal"
    index = 0
    line_start = True

    while index < len(sql):
        if state == "normal" and line_start:
            line_end = sql.find("\n", index)
            if line_end == -1:
                line_end = len(sql)
            line = sql[index:line_end]
            directive = re.fullmatch(r"\s*DELIMITER\s+(\S+)\s*", line, re.IGNORECASE)
            if directive:
                if "".join(buffer).strip():
                    raise MigrationError("DELIMITER deve aparecer entre instrucoes SQL.")
                delimiter = directive.group(1)
                if not delimiter or len(delimiter) > 16:
                    raise MigrationError("DELIMITER possui formato invalido.")
                index = line_end + (line_end < len(sql))
                line_start = True
                continue

        char = sql[index]
        next_char = sql[index + 1] if index + 1 < len(sql) else ""

        if state == "normal":
            if sql.startswith(delimiter, index):
                statement = "".join(buffer).strip()
                if statement:
                    statements.append(statement)
                buffer.clear()
                index += len(delimiter)
                line_start = False
                continue
            if char == "'":
                state = "single"
            elif char == '"':
                state = "double"
            elif char == "`":
                state = "backtick"
            elif char == "#":
                state = "line_comment"
            elif char == "-" and next_char == "-":
                state = "line_comment"
            elif char == "/" and next_char == "*":
                state = "block_comment"
        elif state in {"single", "double", "backtick"}:
            quote = {"single": "'", "double": '"', "backtick": "`"}[state]
            if char == "\\" and next_char:
                buffer.extend((char, next_char))
                index += 2
                line_start = next_char == "\n"
                continue
            if char == quote:
                if next_char == quote:
                    buffer.extend((char, next_char))
                    index += 2
                    line_start = False
                    continue
                state = "normal"
        elif state == "line_comment" and char == "\n":
            state = "normal"
        elif state == "block_comment" and char == "*" and next_char == "/":
            buffer.extend((char, next_char))
            index += 2
            state = "normal"
            line_start = False
            continue

        buffer.append(char)
        line_start = char == "\n"
        index += 1

    if state in {"single", "double", "backtick", "block_comment"}:
        raise MigrationError("Migration contem literal, identificador ou comentario nao terminado.")
    trailing = "".join(buffer).strip()
    if trailing:
        statements.append(trailing)
    return statements


def _without_leading_comments(statement: str) -> str:
    remaining = statement.lstrip()
    while remaining:
        if remaining.startswith("--") or remaining.startswith("#"):
            _, separator, remaining = remaining.partition("\n")
            if not separator:
                return ""
            remaining = remaining.lstrip()
            continue
        if remaining.startswith("/*"):
            end = remaining.find("*/", 2)
            if end == -1:
                return remaining
            remaining = remaining[end + 2 :].lstrip()
            continue
        break
    return remaining


def validate_statements(statements: Iterable[str]) -> list[str]:
    validated: list[str] = []
    for statement in statements:
        significant = _without_leading_comments(statement)
        if not significant:
            continue
        if FORBIDDEN_CLIENT_COMMAND.match(significant):
            command = significant.split(None, 1)[0]
            raise MigrationError(f"Comando de cliente nao permitido: {command}.")
        validated.append(statement)
    return validated


def execute_statements(connection, statements: Iterable[str]) -> None:
    with connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)
            while cursor.nextset():
                pass
