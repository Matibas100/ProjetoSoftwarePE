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
from typing import Sequence
from urllib.parse import parse_qs, unquote, urlsplit

import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor

# A execução por caminho também funciona fora da raiz do projeto.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.legacy_schema import (
    EXPECTED_COLUMNS,
    EXPECTED_INDEXES,
    EXPECTED_PROCEDURE_BODY,
    HISTORY_TABLE,
    PLANOS_FINGERPRINTS,
    SIMULADOS_FINGERPRINTS,
    _check_tokens,
    _detect_auth_prefix,
    _detect_catalogo_prefix,
    _detect_planos_prefix,
    _detect_praticas_prefix,
    _detect_questoes_prefix,
    _detect_simulados_prefix,
    _sql_tokens,
    _user_tables,
    detect_legacy_prefix,
)
from database.migration_types import Migration, MigrationError
from database.sql_scripts import (
    DEFAULT_MIGRATIONS_DIR,
    FORBIDDEN_CLIENT_COMMAND,
    MIGRATION_NAME,
    _without_leading_comments,
    canonical_sql,
    discover_migrations,
    execute_statements,
    split_sql,
    validate_statements,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAFE_SCHEMA_NAME = re.compile(r"^[A-Za-z0-9_]+$")
LOCK_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    name: str
    user: str
    password: str
    charset: str = "utf8mb4"


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
