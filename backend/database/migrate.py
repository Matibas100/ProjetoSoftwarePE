"""Runner oficial de migrations SQL da Plataforma ENEM."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import parse_qs, unquote, urlsplit

import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
MIGRATION_NAME = re.compile(r"^(?P<version>\d{3})_(?P<description>[a-z0-9]+(?:_[a-z0-9]+)*)\.sql$")
SAFE_SCHEMA_NAME = re.compile(r"^[A-Za-z0-9_]+$")
FORBIDDEN_CLIENT_COMMAND = re.compile(r"^(?:SOURCE|CONNECT|USE)\b|^\\\.", re.IGNORECASE)
HISTORY_TABLE = "schema_migrations"
LOCK_TIMEOUT_SECONDS = 10


class MigrationError(RuntimeError):
    """Erro operacional seguro, adequado para exibição no terminal."""


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    name: str
    user: str
    password: str
    charset: str = "utf8mb4"


@dataclass(frozen=True)
class Migration:
    version: str
    description: str
    script_name: str
    checksum: str
    sql: str
    path: Path


@dataclass(frozen=True)
class HistoryState:
    applied_count: int
    blocking_row: dict | None


def load_database_settings(environment: dict[str, str] | None = None) -> DatabaseSettings:
    """Lê configuração sem incluir valores sensíveis nas mensagens de erro."""
    if environment is None:
        load_dotenv(PROJECT_ROOT / ".env")
        environment = dict(os.environ)

    database_url = environment.get("DATABASE_URL")
    if database_url:
        return _settings_from_url(database_url)

    required = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    missing = [name for name in required if not environment.get(name)]
    if missing:
        raise MigrationError(
            "Configuracao do MySQL incompleta. Defina: " + ", ".join(missing) + "."
        )

    try:
        port = int(environment["DB_PORT"])
    except (TypeError, ValueError) as error:
        raise MigrationError("DB_PORT deve ser um numero inteiro valido.") from error
    if not 1 <= port <= 65535:
        raise MigrationError("DB_PORT deve estar entre 1 e 65535.")

    return _validated_settings(
        host=environment["DB_HOST"],
        port=port,
        name=environment["DB_NAME"],
        user=environment["DB_USER"],
        password=environment["DB_PASSWORD"],
        charset=environment.get("DB_CHARSET", "utf8mb4"),
    )


def _settings_from_url(database_url: str) -> DatabaseSettings:
    try:
        parsed = urlsplit(database_url)
        port = parsed.port or 3306
    except ValueError as error:
        raise MigrationError("DATABASE_URL possui formato invalido.") from error

    if parsed.scheme not in {"mysql", "mysql+pymysql"}:
        raise MigrationError("DATABASE_URL deve usar MySQL com PyMySQL.")
    if not parsed.hostname or parsed.username is None or parsed.password is None:
        raise MigrationError("DATABASE_URL deve informar host, usuario e senha.")

    name = unquote(parsed.path.lstrip("/"))
    charset = parse_qs(parsed.query).get("charset", ["utf8mb4"])[0]
    return _validated_settings(
        host=parsed.hostname,
        port=port,
        name=name,
        user=unquote(parsed.username),
        password=unquote(parsed.password),
        charset=charset,
    )


def _validated_settings(**values) -> DatabaseSettings:
    if not values["host"] or not values["user"] or values["password"] == "":
        raise MigrationError("Configuracao do MySQL possui campo obrigatorio vazio.")
    if not SAFE_SCHEMA_NAME.fullmatch(values["name"] or "") or len(values["name"]) > 64:
        raise MigrationError(
            "DB_NAME deve ter ate 64 caracteres com somente letras, numeros e sublinhado."
        )
    if not re.fullmatch(r"[A-Za-z0-9_-]+", values["charset"] or ""):
        raise MigrationError("DB_CHARSET possui formato invalido.")
    return DatabaseSettings(**values)


def connect(settings: DatabaseSettings):
    return pymysql.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password,
        database=settings.name,
        charset=settings.charset,
        autocommit=True,
        cursorclass=DictCursor,
    )


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


def ensure_mysql_8(connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION() AS version")
        version = str(cursor.fetchone()["version"])
    try:
        major = int(version.split(".", 1)[0])
    except ValueError as error:
        raise MigrationError("Nao foi possivel validar a versao do MySQL.") from error
    if major < 8:
        raise MigrationError("O runner exige MySQL 8 ou superior.")


def ensure_history_table(connection) -> None:
    statement = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version CHAR(3) NOT NULL,
            script_name VARCHAR(255) NOT NULL,
            description VARCHAR(255) NOT NULL,
            checksum CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
            status ENUM('RUNNING', 'APPLIED', 'FAILED') NOT NULL,
            attempt_count INT UNSIGNED NOT NULL DEFAULT 1,
            started_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            finished_at DATETIME(6) NULL,
            reconciled_at DATETIME(6) NULL,
            error_code VARCHAR(64) NULL,
            PRIMARY KEY (version),
            CONSTRAINT uq_schema_migrations_script_name UNIQUE (script_name),
            CONSTRAINT ck_schema_migrations_attempt_count CHECK (attempt_count >= 1)
        ) ENGINE = InnoDB
          DEFAULT CHARACTER SET utf8mb4
          COLLATE utf8mb4_unicode_ci
    """
    execute_statements(connection, [statement])


def fetch_history(connection) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version, script_name, description, checksum, status, "
            "attempt_count, started_at, finished_at, reconciled_at, error_code "
            "FROM schema_migrations ORDER BY version"
        )
        return list(cursor.fetchall())


def inspect_history(migrations: Sequence[Migration], rows: Sequence[dict]) -> HistoryState:
    if len(rows) > len(migrations):
        raise MigrationError("Historico possui mais versoes que os arquivos locais.")

    blocking_row = None
    applied_count = 0
    for index, row in enumerate(rows):
        migration = migrations[index]
        version = str(row["version"])
        if version != migration.version:
            raise MigrationError(
                f"Historico fora de ordem: esperado {migration.version}, encontrado {version}."
            )
        if row["script_name"] != migration.script_name:
            raise MigrationError(f"Arquivo divergente na migration {version}.")
        if row["checksum"] != migration.checksum:
            raise MigrationError(f"Checksum divergente na migration {version}.")

        if row["status"] == "APPLIED":
            if blocking_row is not None:
                raise MigrationError("Historico possui versao aplicada apos falha.")
            applied_count += 1
        else:
            if blocking_row is not None or index != len(rows) - 1:
                raise MigrationError("Historico possui mais de uma execucao inconclusiva.")
            blocking_row = row

    return HistoryState(applied_count=applied_count, blocking_row=blocking_row)


def _lock_name(schema: str) -> str:
    digest = hashlib.sha256(schema.encode("utf-8")).hexdigest()[:40]
    return f"enem:migrations:{digest}"


@contextmanager
def migration_lock(connection, schema: str, timeout: int = LOCK_TIMEOUT_SECONDS):
    name = _lock_name(schema)
    acquired = False
    with connection.cursor() as cursor:
        cursor.execute("SELECT GET_LOCK(%s, %s) AS acquired", (name, timeout))
        acquired = cursor.fetchone()["acquired"] == 1
    if not acquired:
        raise MigrationError("Outra execucao de migrations mantem o lock deste schema.")
    try:
        yield
    finally:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT RELEASE_LOCK(%s)", (name,))
        except Exception:
            pass


def _safe_error_code(error: Exception) -> str:
    if error.args and isinstance(error.args[0], int):
        return f"MYSQL_{error.args[0]}"
    return error.__class__.__name__[:64]


def _mark_running(connection, migration: Migration, existing: dict | None) -> None:
    with connection.cursor() as cursor:
        if existing is None:
            cursor.execute(
                "INSERT INTO schema_migrations "
                "(version, script_name, description, checksum, status) "
                "VALUES (%s, %s, %s, %s, 'RUNNING')",
                (
                    migration.version,
                    migration.script_name,
                    migration.description,
                    migration.checksum,
                ),
            )
        else:
            cursor.execute(
                "UPDATE schema_migrations SET status = 'RUNNING', "
                "attempt_count = attempt_count + 1, started_at = CURRENT_TIMESTAMP(6), "
                "finished_at = NULL, reconciled_at = NULL, error_code = NULL "
                "WHERE version = %s",
                (migration.version,),
            )


def apply_migration(connection, migration: Migration, existing: dict | None = None) -> None:
    statements = validate_statements(split_sql(migration.sql))
    if not statements:
        raise MigrationError(f"Migration {migration.version} nao contem SQL executavel.")
    _mark_running(connection, migration, existing)
    try:
        execute_statements(connection, statements)
    except Exception as error:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE schema_migrations SET status = 'FAILED', "
                    "finished_at = CURRENT_TIMESTAMP(6), reconciled_at = NULL, "
                    "error_code = %s WHERE version = %s",
                    (_safe_error_code(error), migration.version),
                )
        except Exception:
            pass
        raise MigrationError(
            f"Migration {migration.version} falhou; o historico foi bloqueado."
        ) from error

    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE schema_migrations SET status = 'APPLIED', "
            "finished_at = CURRENT_TIMESTAMP(6), reconciled_at = NULL, "
            "error_code = NULL WHERE version = %s",
            (migration.version,),
        )


def _user_tables(connection) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT TABLE_NAME AS table_name FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'"
        )
        return {
            row["table_name"]
            for row in cursor.fetchall()
            if row["table_name"] != HISTORY_TABLE
        }


def run_up(
    connection,
    settings: DatabaseSettings,
    migrations: Sequence[Migration],
    lock_timeout: int = LOCK_TIMEOUT_SECONDS,
) -> int:
    with migration_lock(connection, settings.name, lock_timeout):
        ensure_mysql_8(connection)
        ensure_history_table(connection)
        rows = fetch_history(connection)
        state = inspect_history(migrations, rows)
        existing = None
        next_index = state.applied_count

        if state.blocking_row:
            if state.blocking_row.get("reconciled_at") is None:
                raise MigrationError(
                    f"Migration {state.blocking_row['version']} esta em estado "
                    f"{state.blocking_row['status']} e exige reconciliacao."
                )
            existing = state.blocking_row
        elif not rows and _user_tables(connection):
            raise MigrationError(
                "Schema nao vazio e sem historico; execute baseline apos validar um backup."
            )

        applied = 0
        for index in range(next_index, len(migrations)):
            migration = migrations[index]
            apply_migration(connection, migration, existing if index == next_index else None)
            existing = None
            applied += 1
        return applied


def reconcile_failure(
    connection,
    settings: DatabaseSettings,
    migrations: Sequence[Migration],
    version: str,
    confirmed: bool,
    lock_timeout: int = LOCK_TIMEOUT_SECONDS,
) -> None:
    if not confirmed:
        raise MigrationError(
            "Reconciliacao exige --confirm apos inspecao do schema e restauracao ou correcao."
        )
    with migration_lock(connection, settings.name, lock_timeout):
        ensure_mysql_8(connection)
        ensure_history_table(connection)
        rows = fetch_history(connection)
        state = inspect_history(migrations, rows)
        row = state.blocking_row
        if row is None or row["version"] != version:
            raise MigrationError("A versao informada nao e a execucao bloqueante atual.")
        if row["status"] not in {"FAILED", "RUNNING"}:
            raise MigrationError("Somente execucao FAILED ou RUNNING pode ser reconciliada.")
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE schema_migrations SET reconciled_at = CURRENT_TIMESTAMP(6) "
                "WHERE version = %s",
                (version,),
            )


EXPECTED_COLUMNS = {
    "materias": [
        ("id", "int", "NO", None, "auto_increment"),
        ("nome", "varchar(100)", "NO", None, ""),
        ("descricao", "text", "YES", None, ""),
    ],
    "assuntos": [
        ("id", "int", "NO", None, "auto_increment"),
        ("nome", "varchar(150)", "NO", None, ""),
        ("descricao", "text", "YES", None, ""),
        ("materia_id", "int", "NO", None, ""),
    ],
    "questoes": [
        ("id", "int", "NO", None, "auto_increment"),
        ("enunciado", "text", "NO", None, ""),
        ("alternativa_a", "text", "NO", None, ""),
        ("alternativa_b", "text", "NO", None, ""),
        ("alternativa_c", "text", "NO", None, ""),
        ("alternativa_d", "text", "NO", None, ""),
        ("alternativa_e", "text", "NO", None, ""),
        ("resposta_correta", "char(1)", "NO", None, ""),
        ("explicacao", "text", "YES", None, ""),
        ("dificuldade", "varchar(10)", "NO", None, ""),
        ("assunto_id", "int", "NO", None, ""),
    ],
}

EXPECTED_INDEXES = {
    ("materias", "PRIMARY", 0, 1, "id"),
    ("materias", "uq_materias_nome", 0, 1, "nome"),
    ("assuntos", "PRIMARY", 0, 1, "id"),
    ("assuntos", "ix_assuntos_materia_id", 1, 1, "materia_id"),
    ("questoes", "PRIMARY", 0, 1, "id"),
    ("questoes", "ix_questoes_assunto_id", 1, 1, "assunto_id"),
}

EXPECTED_PROCEDURE_BODY = """
BEGIN
    SELECT id, enunciado, alternativa_a, alternativa_b, alternativa_c,
           alternativa_d, alternativa_e, resposta_correta, explicacao,
           dificuldade, assunto_id
    FROM questoes
    WHERE assunto_id = p_assunto_id
    ORDER BY id;
END
"""


def _sql_tokens(value: str) -> list[str]:
    return re.findall(r"[a-z_][a-z0-9_]*|\d+|'[^']*'|[,();=]", value.lower().replace("`", ""))


def _check_tokens(value: str) -> list[str]:
    unescaped = value.lower().replace("\\'", "'")
    without_charset = re.sub(r"_[a-z0-9]+(?=')", "", unescaped)
    return [token for token in _sql_tokens(without_charset) if token not in {"(", ")"}]


def _detect_catalogo_prefix(connection, tables: set[str]) -> str:
    expected = {"areas_enem", "materias", "assuntos", "questoes", "assunto_transferencias"}
    if tables != expected:
        raise MigrationError("Schema nao corresponde as tabelas conhecidas do catalogo.")
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, codigo, nome, ordem FROM areas_enem ORDER BY ordem")
        areas = [tuple(row.values()) for row in cursor.fetchall()]
        if areas != [
            (1, "linguagens", "Linguagens", 1),
            (2, "ciencias-humanas", "Ciências Humanas", 2),
            (3, "ciencias-natureza", "Ciências da Natureza", 3),
            (4, "matematica", "Matemática", 4),
        ]:
            raise MigrationError("Catalogo fixo de Areas do ENEM diverge do esperado.")
        cursor.execute(
            "SELECT TABLE_NAME AS table_name, COLUMN_NAME AS column_name, "
            "IS_NULLABLE AS is_nullable, COLLATION_NAME AS collation_name "
            "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() "
            "AND (TABLE_NAME, COLUMN_NAME) IN "
            "(('materias', 'area_enem_id'), ('materias', 'status'), "
            "('assuntos', 'nome_normalizado'), ('assuntos', 'status'))"
        )
        columns = {
            (row["table_name"], row["column_name"]): (
                row["is_nullable"], row["collation_name"]
            )
            for row in cursor.fetchall()
        }
        if set(columns) != {
            ("materias", "area_enem_id"),
            ("materias", "status"),
            ("assuntos", "nome_normalizado"),
            ("assuntos", "status"),
        } or columns[("assuntos", "nome_normalizado")][1] != "utf8mb4_0900_ai_ci":
            raise MigrationError("Colunas principais do catalogo divergem do esperado.")
        cursor.execute(
            "SELECT rc.TABLE_NAME AS table_name, rc.DELETE_RULE AS delete_rule, "
            "kcu.COLUMN_NAME AS column_name FROM information_schema.REFERENTIAL_CONSTRAINTS rc "
            "JOIN information_schema.KEY_COLUMN_USAGE kcu "
            "ON kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA "
            "AND kcu.TABLE_NAME = rc.TABLE_NAME "
            "AND kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME "
            "WHERE rc.CONSTRAINT_SCHEMA = DATABASE()"
        )
        delete_rules = {
            (row["table_name"], row["column_name"]): row["delete_rule"]
            for row in cursor.fetchall()
        }
        cursor.execute(
            "SELECT COUNT(*) AS total FROM information_schema.ROUTINES "
            "WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE' "
            "AND ROUTINE_NAME = 'sp_questoes_por_assunto'"
        )
        if cursor.fetchone()["total"] != 1:
            raise MigrationError("Stored Procedure obrigatoria diverge do esperado.")
        cursor.execute(
            "SELECT COUNT(*) AS total FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'assuntos' "
            "AND INDEX_NAME = 'uq_assuntos_materia_nome_normalizado' AND NON_UNIQUE = 0"
        )
        unique_final = cursor.fetchone()["total"] == 2

    preparatorio = (
        columns[("materias", "area_enem_id")][0] == "YES"
        and columns[("assuntos", "nome_normalizado")][0] == "YES"
        and delete_rules.get(("assuntos", "materia_id")) == "CASCADE"
        and not unique_final
    )
    final = (
        columns[("materias", "area_enem_id")][0] == "NO"
        and columns[("assuntos", "nome_normalizado")][0] == "NO"
        and delete_rules.get(("materias", "area_enem_id")) == "RESTRICT"
        and delete_rules.get(("assuntos", "materia_id")) == "RESTRICT"
        and delete_rules.get(("questoes", "assunto_id")) == "RESTRICT"
        and unique_final
    )
    if preparatorio:
        return "003"
    if final:
        return "004"
    raise MigrationError("Schema combina estados historicos incompatíveis.")


def detect_legacy_prefix(connection) -> str:
    expected_tables = set(EXPECTED_COLUMNS)
    user_tables = _user_tables(connection)
    if user_tables != expected_tables:
        if user_tables == {
            "areas_enem",
            "materias",
            "assuntos",
            "questoes",
            "assunto_transferencias",
        }:
            return _detect_catalogo_prefix(connection, user_tables)
        raise MigrationError("Schema nao corresponde as tabelas MVP esperadas.")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT TABLE_NAME AS table_name, ENGINE AS engine, "
            "TABLE_COLLATION AS table_collation FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN (%s, %s, %s)",
            tuple(sorted(expected_tables)),
        )
        table_rows = cursor.fetchall()
        actual_tables = {
            row["table_name"]: (row["engine"], row["table_collation"])
            for row in table_rows
        }
        if set(actual_tables) != expected_tables or any(
            engine.lower() != "innodb" or collation != "utf8mb4_unicode_ci"
            for engine, collation in actual_tables.values()
        ):
            raise MigrationError("Schema nao corresponde as tabelas MVP esperadas.")

        cursor.execute(
            "SELECT TABLE_NAME AS table_name, COLUMN_NAME AS column_name, "
            "COLUMN_TYPE AS column_type, IS_NULLABLE AS is_nullable, "
            "COLUMN_DEFAULT AS column_default, EXTRA AS extra "
            "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() "
            "AND TABLE_NAME IN (%s, %s, %s) ORDER BY TABLE_NAME, ORDINAL_POSITION",
            tuple(sorted(expected_tables)),
        )
        actual_columns: dict[str, list[tuple]] = {name: [] for name in expected_tables}
        for row in cursor.fetchall():
            actual_columns[row["table_name"]].append(
                (
                    row["column_name"],
                    row["column_type"].lower(),
                    row["is_nullable"],
                    row["column_default"],
                    row["extra"].lower(),
                )
            )
        if actual_columns != EXPECTED_COLUMNS:
            raise MigrationError("Colunas do schema nao correspondem ao MVP conhecido.")

        cursor.execute(
            "SELECT TABLE_NAME AS table_name, INDEX_NAME AS index_name, "
            "NON_UNIQUE AS non_unique, SEQ_IN_INDEX AS seq_in_index, "
            "COLUMN_NAME AS column_name FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN (%s, %s, %s)",
            tuple(sorted(expected_tables)),
        )
        indexes = {
            (
                row["table_name"],
                row["index_name"],
                int(row["non_unique"]),
                int(row["seq_in_index"]),
                row["column_name"],
            )
            for row in cursor.fetchall()
        }
        if indexes != EXPECTED_INDEXES:
            raise MigrationError("Indices do schema nao correspondem ao MVP conhecido.")

        cursor.execute(
            "SELECT rc.TABLE_NAME AS table_name, "
            "rc.CONSTRAINT_NAME AS constraint_name, rc.UPDATE_RULE AS update_rule, "
            "rc.DELETE_RULE AS delete_rule, kcu.COLUMN_NAME AS column_name, "
            "kcu.REFERENCED_TABLE_NAME AS referenced_table_name, "
            "kcu.REFERENCED_COLUMN_NAME AS referenced_column_name "
            "FROM information_schema.REFERENTIAL_CONSTRAINTS rc "
            "JOIN information_schema.KEY_COLUMN_USAGE kcu "
            "ON kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA "
            "AND kcu.TABLE_NAME = rc.TABLE_NAME "
            "AND kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME "
            "WHERE rc.CONSTRAINT_SCHEMA = DATABASE()"
        )
        foreign_keys = {
            (
                row["table_name"],
                row["constraint_name"],
                row["update_rule"],
                row["delete_rule"],
                row["column_name"],
                row["referenced_table_name"],
                row["referenced_column_name"],
            )
            for row in cursor.fetchall()
            if row["table_name"] in expected_tables
        }
        assunto_fk = (
            "assuntos",
            "fk_assuntos_materias",
            "CASCADE",
            "CASCADE",
            "materia_id",
            "materias",
            "id",
        )
        if assunto_fk not in foreign_keys or len(foreign_keys) != 2:
            raise MigrationError("Foreign keys do schema nao correspondem ao MVP conhecido.")
        questao_fk = next(
            (item for item in foreign_keys if item[0] == "questoes"), None
        )
        if not questao_fk or (
            questao_fk[1],
            questao_fk[2],
            questao_fk[4],
            questao_fk[5],
            questao_fk[6],
        ) != ("fk_questoes_assuntos", "CASCADE", "assunto_id", "assuntos", "id"):
            raise MigrationError("Foreign key de questoes nao corresponde ao MVP conhecido.")

        cursor.execute(
            "SELECT tc.CONSTRAINT_NAME AS constraint_name, cc.CHECK_CLAUSE AS check_clause "
            "FROM information_schema.TABLE_CONSTRAINTS tc "
            "JOIN information_schema.CHECK_CONSTRAINTS cc "
            "ON cc.CONSTRAINT_SCHEMA = tc.CONSTRAINT_SCHEMA "
            "AND cc.CONSTRAINT_NAME = tc.CONSTRAINT_NAME "
            "WHERE tc.TABLE_SCHEMA = DATABASE() AND tc.TABLE_NAME = 'questoes' "
            "AND tc.CONSTRAINT_TYPE = 'CHECK'"
        )
        checks = {
            row["constraint_name"]: _check_tokens(row["check_clause"])
            for row in cursor.fetchall()
        }
        expected_checks = {
            "ck_questoes_resposta_correta": _check_tokens(
                "resposta_correta IN ('A', 'B', 'C', 'D', 'E')"
            ),
            "ck_questoes_dificuldade": _check_tokens(
                "dificuldade IN ('facil', 'media', 'dificil')"
            ),
        }
        if checks != expected_checks:
            raise MigrationError("Checks do schema nao correspondem ao MVP conhecido.")

        cursor.execute(
            "SELECT ROUTINE_DEFINITION AS routine_definition FROM information_schema.ROUTINES "
            "WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE' "
            "AND ROUTINE_NAME = 'sp_questoes_por_assunto'"
        )
        procedure = cursor.fetchone()
        procedure_exists = procedure is not None
        if procedure_exists:
            cursor.execute(
                "SELECT PARAMETER_MODE AS parameter_mode, PARAMETER_NAME AS parameter_name, "
                "DTD_IDENTIFIER AS dtd_identifier FROM information_schema.PARAMETERS "
                "WHERE SPECIFIC_SCHEMA = DATABASE() "
                "AND SPECIFIC_NAME = 'sp_questoes_por_assunto' "
                "ORDER BY ORDINAL_POSITION"
            )
            parameters = cursor.fetchall()
            if len(parameters) != 1 or (
                parameters[0]["parameter_mode"],
                parameters[0]["parameter_name"],
                parameters[0]["dtd_identifier"].lower(),
            ) != ("IN", "p_assunto_id", "int"):
                raise MigrationError("Assinatura da Stored Procedure diverge do MVP conhecido.")
            if _sql_tokens(procedure["routine_definition"]) != _sql_tokens(
                EXPECTED_PROCEDURE_BODY
            ):
                raise MigrationError("Corpo da Stored Procedure diverge do MVP conhecido.")

    delete_rule = questao_fk[3]
    if delete_rule == "CASCADE" and not procedure_exists:
        return "000"
    if delete_rule == "RESTRICT" and not procedure_exists:
        return "001"
    if delete_rule == "RESTRICT" and procedure_exists:
        return "002"
    raise MigrationError("Schema combina estados historicos incompatíveis.")


def run_baseline(
    connection,
    settings: DatabaseSettings,
    migrations: Sequence[Migration],
    confirmed: bool,
    lock_timeout: int = LOCK_TIMEOUT_SECONDS,
) -> str:
    if not confirmed:
        raise MigrationError("Baseline exige --confirm apos backup e validacao do schema.")
    with migration_lock(connection, settings.name, lock_timeout):
        ensure_mysql_8(connection)
        ensure_history_table(connection)
        if fetch_history(connection):
            raise MigrationError("Baseline exige historico vazio.")
        if not _user_tables(connection):
            raise MigrationError("Schema vazio deve ser instalado com up, nao com baseline.")
        prefix = detect_legacy_prefix(connection)
        connection.begin()
        try:
            with connection.cursor() as cursor:
                for migration in migrations[: int(prefix) + 1]:
                    cursor.execute(
                        "INSERT INTO schema_migrations "
                        "(version, script_name, description, checksum, status, "
                        "started_at, finished_at) "
                        "VALUES (%s, %s, %s, %s, 'APPLIED', "
                        "CURRENT_TIMESTAMP(6), CURRENT_TIMESTAMP(6))",
                        (
                            migration.version,
                            migration.script_name,
                            migration.description,
                            migration.checksum,
                        ),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        return prefix


def status_lines(
    connection,
    settings: DatabaseSettings,
    migrations: Sequence[Migration],
    lock_timeout: int = LOCK_TIMEOUT_SECONDS,
) -> list[str]:
    with migration_lock(connection, settings.name, lock_timeout):
        ensure_mysql_8(connection)
        ensure_history_table(connection)
        rows = fetch_history(connection)
        state = inspect_history(migrations, rows)
        lines = [f"Schema: {settings.name}"]
        by_version = {row["version"]: row for row in rows}
        for migration in migrations:
            row = by_version.get(migration.version)
            status = row["status"] if row else "PENDING"
            lines.append(f"{migration.version} {status} {migration.script_name}")
        if not rows and _user_tables(connection):
            lines.append("BASELINE_REQUIRED schema nao vazio sem historico")
        elif state.blocking_row:
            if state.blocking_row.get("reconciled_at") is None:
                lines.append(
                    f"BLOCKED migration {state.blocking_row['version']} exige reconciliacao"
                )
            else:
                lines.append(
                    f"RETRY_READY migration {state.blocking_row['version']} reconciliada"
                )
        return lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrations SQL da Plataforma ENEM")
    parser.add_argument(
        "--migrations-dir", type=Path, default=DEFAULT_MIGRATIONS_DIR, help=argparse.SUPPRESS
    )
    parser.add_argument("--lock-timeout", type=int, default=LOCK_TIMEOUT_SECONDS)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Exibe o estado das migrations")
    subparsers.add_parser("up", help="Aplica migrations pendentes")
    baseline = subparsers.add_parser("baseline", help="Adota um schema MVP existente")
    baseline.add_argument("--confirm", action="store_true")
    repair = subparsers.add_parser("reconcile", help="Reconcilia uma falha ja inspecionada")
    repair.add_argument("version")
    repair.add_argument("--confirm", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    connection = None
    try:
        if args.lock_timeout < 0:
            raise MigrationError("O timeout do lock nao pode ser negativo.")
        settings = load_database_settings()
        migrations = discover_migrations(args.migrations_dir)
        connection = connect(settings)
        if args.command == "status":
            for line in status_lines(
                connection, settings, migrations, args.lock_timeout
            ):
                print(line)
        elif args.command == "up":
            applied = run_up(connection, settings, migrations, args.lock_timeout)
            print(f"Schema {settings.name}: {applied} migration(s) aplicada(s).")
        elif args.command == "baseline":
            prefix = run_baseline(
                connection, settings, migrations, args.confirm, args.lock_timeout
            )
            print(f"Schema {settings.name}: baseline reconhecido ate {prefix}.")
        else:
            reconcile_failure(
                connection,
                settings,
                migrations,
                args.version,
                args.confirm,
                args.lock_timeout,
            )
            print(f"Schema {settings.name}: migration {args.version} reconciliada.")
        return 0
    except MigrationError as error:
        print(f"ERRO: {error}", file=sys.stderr)
        return 2
    except Exception:
        print(
            "ERRO: falha ao conectar ou executar migrations no schema selecionado.",
            file=sys.stderr,
        )
        return 1
    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
