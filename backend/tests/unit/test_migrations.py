import hashlib
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

from database import migrate
from database import legacy_schema


class StructuralFingerprintTest(unittest.TestCase):
    def test_procedure_metadados_indisponiveis_falham_fechado(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        for procedure in (None, {}, {"routine_definition": None}):
            cursor.fetchone.return_value = procedure
            cursor.fetchall.return_value = [{
                "parameter_mode": "IN",
                "parameter_name": "p_assunto_id",
                "dtd_identifier": "int"
            }]
            with self.assertRaises(migrate.MigrationError):
                legacy_schema._validate_procedure(connection)
        cursor.execute.side_effect = migrate.pymysql.MySQLError(1142, "segredo-sentinela")
        with self.assertRaises(migrate.MigrationError) as error:
            legacy_schema._validate_procedure(connection)
        self.assertNotIn("segredo-sentinela", str(error.exception))

    def metadata(self):
        return {
            "table": [{
                "TABLE_NAME": "probe",
                "ENGINE": "InnoDB",
                "TABLE_COLLATION": "utf8mb4_unicode_ci",
                "ROW_FORMAT": "Dynamic",
                "CREATE_OPTIONS": "",
                "TABLE_COMMENT": "Teste Á"
            }],
            "columns": [
                dict(
                    ORDINAL_POSITION=position,
                    COLUMN_NAME=name,
                    COLUMN_TYPE="varchar(20)",
                    IS_NULLABLE="YES",
                    COLUMN_DEFAULT=default,
                    EXTRA="",
                    CHARACTER_SET_NAME="utf8mb4",
                    COLLATION_NAME="utf8mb4_unicode_ci",
                    GENERATION_EXPRESSION="",
                    COLUMN_COMMENT=""
                )
                for position,
                name,
                default in [
                    (
                        1,
                        "valor",
                        None
                    ),
                    (
                        2,
                        "literal",
                        "NULL"
                    )
                ]
            ],
            "indexes": [dict(
                INDEX_NAME="PRIMARY",
                NON_UNIQUE=0,
                SEQ_IN_INDEX=1,
                COLUMN_NAME="valor",
                EXPRESSION=None,
                SUB_PART=None,
                COLLATION="A",
                INDEX_TYPE="BTREE",
                IS_VISIBLE="YES",
                INDEX_COMMENT=""
            )],
            "foreign_keys": [dict(
                CONSTRAINT_NAME="fk_probe",
                ORDINAL_POSITION=1,
                COLUMN_NAME="valor",
                REFERENCED_TABLE_SCHEMA="origem",
                REFERENCED_TABLE_NAME="parent",
                REFERENCED_COLUMN_NAME="id",
                POSITION_IN_UNIQUE_CONSTRAINT=1,
                UNIQUE_CONSTRAINT_NAME="PRIMARY",
                UPDATE_RULE="RESTRICT",
                DELETE_RULE="RESTRICT",
                MATCH_OPTION="NONE"
            )],
            "checks": [dict(
                CONSTRAINT_NAME="ck_probe",
                CHECK_CLAUSE="(`literal` <> _utf8mb4'Null')",
                ENFORCED="YES"
            )],
        }

    def canonical(self, metadata, schema="origem"):
        return legacy_schema._canonical_structure(metadata, schema)

    def test_ordem_estatisticas_e_schema_fisico_nao_mudam_assinatura(self):
        metadata = self.metadata()
        other = copy.deepcopy(metadata)
        for section, rows in other.items():
            rows.reverse()
            for row in rows:
                row["CARDINALITY"] = 999
                row["AUTO_INCREMENT"] = 777
                row["TABLE_SCHEMA"] = "copia"
        other["foreign_keys"][0]["REFERENCED_TABLE_SCHEMA"] = "copia"
        self.assertEqual(self.canonical(metadata), self.canonical(other, "copia"))
        decoded = json.loads(self.canonical(metadata))
        self.assertEqual(decoded["foreign_keys"][0][3], ["internal"])
        self.assertEqual([row[4] for row in decoded["columns"]], [None, "NULL"])
        self.assertEqual(decoded["checks"][0][1], "(`literal` <> _utf8mb4'Null')")

    def test_cada_campo_estrutural_e_sensivel_inclusive_fk_externa(self):
        original = self.metadata()
        expected = self.canonical(original)
        for section, rows in original.items():
            for field, value in rows[0].items():
                with self.subTest(section=section, field=field):
                    other = copy.deepcopy(original)
                    other[section][0][field] = value + 1 if isinstance(
                        value,
                        int
                    ) else str(value) + "X"
                    self.assertNotEqual(expected, self.canonical(other))
        other = copy.deepcopy(original)
        other["foreign_keys"][0]["REFERENCED_TABLE_SCHEMA"] = "internal"
        self.assertEqual(
            json.loads(self.canonical(other))["foreign_keys"][0][3],
            [
                "external",
                "internal"
            ]
        )

    def test_defaults_preservam_tipo_caixa_e_literal(self):
        variants = []
        for value in (None, "NULL", "null", 1, "1", True, "CURRENT_TIMESTAMP", "current_timestamp"):
            metadata = self.metadata()
            metadata["columns"][0]["COLUMN_DEFAULT"] = value
            variants.append(self.canonical(metadata))
        self.assertEqual(len(set(variants)), len(variants))

    def test_coleta_parametrizada_e_hash_utf8(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = {"schema_name": "origem"}
        metadata = self.metadata()
        cursor.fetchall.side_effect = list(metadata.values())
        expected = hashlib.sha256(self.canonical(metadata).encode("utf-8")).hexdigest()
        self.assertEqual(legacy_schema._table_fingerprint(connection, "probe"), expected)
        for call in cursor.execute.call_args_list[1:]:
            self.assertEqual(call.args[1], ("probe",))
            self.assertIn("DATABASE()", call.args[0])

    def test_metadados_insuficientes_ou_erro_mysql_falham_sem_segredo(self):
        variants = []
        for section, rows in self.metadata().items():
            for field in rows[0]:
                other = self.metadata()
                del other[section][0][field]
                variants.append(other)
        for section in ("table", "columns", "indexes"):
            other = self.metadata()
            other[section] = []
            variants.append(other)
        other = self.metadata()
        other["checks"][0]["ENFORCED"] = None
        variants.append(other)
        other = self.metadata()
        other["columns"][0]["COLUMN_DEFAULT"] = b"unsupported"
        variants.append(other)
        for metadata in variants:
            connection = MagicMock()
            cursor = connection.cursor.return_value.__enter__.return_value
            cursor.fetchone.return_value = {"schema_name": "origem"}
            cursor.fetchall.side_effect = list(metadata.values())
            with self.assertRaisesRegex(migrate.MigrationError, "Metadados.*probe"):
                legacy_schema._table_fingerprint(connection, "probe")
        for result in (None, {}, {"schema_name": None}):
            connection = MagicMock()
            cursor = connection.cursor.return_value.__enter__.return_value
            cursor.fetchone.return_value = result
            cursor.fetchall.side_effect = list(self.metadata().values())
            with self.assertRaises(migrate.MigrationError):
                legacy_schema._table_fingerprint(connection, "probe")
        cursor.execute.side_effect = migrate.pymysql.MySQLError(1142, "segredo-sentinela")
        with self.assertRaises(migrate.MigrationError) as error:
            legacy_schema._table_fingerprint(connection, "probe")
        self.assertNotIn("segredo-sentinela", str(error.exception))


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self._one = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, statement, params=None):
        self.connection.calls.append((statement, params))
        normalized = " ".join(statement.split()).upper()
        if statement.strip() == "BROKEN":
            raise migrate.pymysql.MySQLError(1064, "segredo-sentinela")
        if normalized.startswith("SELECT GET_LOCK"):
            self._one = {"acquired": self.connection.lock_result}
        elif normalized.startswith("SELECT VERSION"):
            self._one = {"version": self.connection.version}

    def fetchone(self):
        return self._one

    def fetchall(self):
        return []

    def nextset(self):
        return False


class FakeConnection:
    def __init__(self, lock_result=1, version="8.0.36"):
        self.calls = []
        self.lock_result = lock_result
        self.version = version

    def cursor(self):
        return FakeCursor(self)


class FakeMigrationPath:
    def __init__(self, name, content=b"SELECT 1;"):
        self.name = name
        self.suffix = Path(name).suffix
        self.content = content

    def is_dir(self):
        return False

    def read_bytes(self):
        return self.content


class FakeMigrationDirectory:
    def __init__(self, *paths):
        self.paths = paths

    def is_dir(self):
        return True

    def iterdir(self):
        return iter(self.paths)


def migration(version="000", sql="SELECT 1;"):
    name = f"{version}_teste.sql"
    return migrate.Migration(
        version=version,
        description="teste",
        script_name=name,
        checksum=hashlib.sha256(sql.encode()).hexdigest(),
        sql=sql,
        path=Path(name),
    )


class DatabaseSettingsTest(unittest.TestCase):
    def test_le_variaveis_e_url_mysql(self):
        settings = migrate.load_database_settings(
            {
                "DB_HOST": "localhost",
                "DB_PORT": "3307",
                "DB_NAME": "enem_teste",
                "DB_USER": "usuario",
                "DB_PASSWORD": "senha",
            }
        )
        self.assertEqual(
            (
                settings.port,
                settings.name,
                settings.charset
            ),
            (
                3307,
                "enem_teste",
                "utf8mb4"
            )
        )

        settings = migrate.load_database_settings(
            {
                "DATABASE_URL": (
                    "mysql+pymysql://usuario%40email:senha%20forte@db:3308/"
                    "enem_url?charset=utf8mb4"
                )
            }
        )
        self.assertEqual(settings.user, "usuario@email")
        self.assertEqual(settings.password, "senha forte")
        self.assertEqual((settings.host, settings.port, settings.name), ("db", 3308, "enem_url"))

    def test_rejeita_configuracao_incompleta_sem_expor_valores(self):
        with self.assertRaisesRegex(migrate.MigrationError, "DB_PORT, DB_NAME") as error:
            migrate.load_database_settings({"DB_HOST": "segredo-sentinela"})
        self.assertNotIn("segredo-sentinela", str(error.exception))

        invalid = [
            ({"DATABASE_URL": "postgresql://u:p@db/enem"}, "MySQL"),
            ({"DATABASE_URL": "mysql+pymysql://u@db/enem"}, "host, usuario e senha"),
            (
                {
                    "DB_HOST": "db",
                    "DB_PORT": "invalida",
                    "DB_NAME": "enem",
                    "DB_USER": "u",
                    "DB_PASSWORD": "p",
                },
                "DB_PORT",
            ),
            (
                {
                    "DB_HOST": "db",
                    "DB_PORT": "3306",
                    "DB_NAME": "x" * 65,
                    "DB_USER": "u",
                    "DB_PASSWORD": "p",
                },
                "64 caracteres",
            ),
        ]
        for environment, message in invalid:
            with self.subTest(environment=environment), self.assertRaisesRegex(
                migrate.MigrationError,
                message
            ):
                migrate.load_database_settings(environment)


class MigrationFilesTest(unittest.TestCase):
    def test_descobre_ordena_e_canonicaliza_checksum(self):
        directory = FakeMigrationDirectory(
            FakeMigrationPath("001_segunda.sql", b"SELECT 2;\r\n"),
            FakeMigrationPath("000_primeira.sql", b"SELECT 1;\r\n"),
        )
        found = migrate.discover_migrations(directory)
        self.assertEqual([item.version for item in found], ["000", "001"])
        expected = hashlib.sha256(b"SELECT 1;\n").hexdigest()
        self.assertEqual(found[0].checksum, expected)
        self.assertEqual(
            migrate.canonical_sql(b"SELECT 1;\r\n", Path("x.sql")),
            migrate.canonical_sql(b"SELECT 1;\n", Path("x.sql")),
        )

    def test_rejeita_nome_lacuna_duplicidade_bom_e_diretorio_vazio(self):
        cases = [
            ([FakeMigrationPath("migration.sql")], "Nome"),
            ([FakeMigrationPath("001_sem_zero.sql")], "esperado 000"),
            (
                [FakeMigrationPath("000_a.sql"), FakeMigrationPath("000_b.sql")],
                "duplicada",
            ),
            ([FakeMigrationPath("000_bom.sql", b"\xef\xbb\xbfSELECT 1;")], "BOM"),
        ]
        for paths, message in cases:
            with self.subTest(paths=paths), self.assertRaisesRegex(
                migrate.MigrationError,
                message
            ):
                migrate.discover_migrations(FakeMigrationDirectory(*paths))
        with self.assertRaisesRegex(migrate.MigrationError, "Nenhuma"):
            migrate.discover_migrations(FakeMigrationDirectory())


class SqlParserTest(unittest.TestCase):
    def test_procedure_delimiter_literals_e_comentarios(self):
        sql = """
        -- cabecalho com ;
        SELECT 'a;--b', "c;d", `e;f`;
        DELIMITER $$
        CREATE PROCEDURE p()
        BEGIN
            SELECT 'x;$$'; # comentario $$
            SELECT 2 /* ; $$ */;
        END$$
        DELIMITER ;
        SELECT 3;
        """
        statements = migrate.validate_statements(migrate.split_sql(sql))
        self.assertEqual(len(statements), 3)
        self.assertIn("CREATE PROCEDURE", statements[1])
        self.assertIn("SELECT 2", statements[1])

    def test_rejeita_delimiter_em_instrucao_e_comandos_de_cliente(self):
        with self.assertRaisesRegex(migrate.MigrationError, "DELIMITER"):
            migrate.split_sql("SELECT 1\nDELIMITER $$\n")
        for command in ("USE outro;", "SOURCE arquivo.sql;", "\\. arquivo.sql;"):
            with self.subTest(command=command), self.assertRaisesRegex(
                migrate.MigrationError,
                "nao permitido"
            ):
                migrate.validate_statements(migrate.split_sql(command))

    def test_rejeita_literal_nao_terminado(self):
        with self.assertRaisesRegex(migrate.MigrationError, "nao terminado"):
            migrate.split_sql("SELECT 'aberto")


class HistoryAndExecutionTest(unittest.TestCase):
    def test_executa_em_ordem_drena_resultados_e_para_no_erro(self):
        connection = FakeConnection()
        migrate.execute_statements(connection, ["SELECT 1", "SELECT 2"])
        self.assertEqual([call[0] for call in connection.calls], ["SELECT 1", "SELECT 2"])

        connection = FakeConnection()
        with self.assertRaises(migrate.pymysql.MySQLError):
            migrate.execute_statements(connection, ["SELECT 1", "BROKEN", "SELECT 3"])
        self.assertNotIn("SELECT 3", [call[0] for call in connection.calls])

    def test_valida_prefixo_checksum_nome_e_estado(self):
        migrations = [migration("000"), migration("001")]
        applied = {
            "version": "000",
            "script_name": migrations[0].script_name,
            "checksum": migrations[0].checksum,
            "status": "APPLIED",
            "reconciled_at": None,
        }
        state = migrate.inspect_history(migrations, [applied])
        self.assertEqual(state.applied_count, 1)

        for field, value, message in (
            ("version", "001", "fora de ordem"),
            ("script_name", "000_outro.sql", "Arquivo divergente"),
            ("checksum", "0" * 64, "Checksum divergente"),
        ):
            row = dict(applied)
            row[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(
                migrate.MigrationError,
                message
            ):
                migrate.inspect_history(migrations, [row])

        failed = dict(applied, status="FAILED")
        state = migrate.inspect_history(migrations, [failed])
        self.assertEqual(state.blocking_row["status"], "FAILED")

    def test_lock_sucesso_falha_e_liberacao(self):
        connection = FakeConnection()
        with migrate.migration_lock(connection, "enem", timeout=0):
            pass
        statements = [call[0] for call in connection.calls]
        self.assertTrue(any("GET_LOCK" in item for item in statements))
        self.assertTrue(any("RELEASE_LOCK" in item for item in statements))

        with self.assertRaisesRegex(migrate.MigrationError, "Outra execucao"):
            with migrate.migration_lock(FakeConnection(lock_result=0), "enem", timeout=0):
                pass

    def test_aplicacao_registra_sucesso_e_falha_sanitizada(self):
        connection = FakeConnection()
        migrate.apply_migration(connection, migration(sql="SELECT 1;"))
        calls = [(" ".join(sql.split()), params) for sql, params in connection.calls]
        self.assertTrue(any("VALUES (%s, %s, %s, %s, 'RUNNING')" in sql for sql, _ in calls))
        self.assertTrue(any("status = 'APPLIED'" in sql for sql, _ in calls))

        connection = FakeConnection()
        with self.assertRaisesRegex(migrate.MigrationError, "historico foi bloqueado") as error:
            migrate.apply_migration(connection, migration(sql="BROKEN;"))
        self.assertNotIn("segredo-sentinela", str(error.exception))
        failed_updates = [params for sql, params in connection.calls if "status = 'FAILED'" in sql]
        self.assertEqual(failed_updates[0][0], "MYSQL_1064")

    def test_mysql_8_e_confirmacoes_obrigatorias(self):
        migrate.ensure_mysql_8(FakeConnection(version="8.0.36"))
        with self.assertRaisesRegex(migrate.MigrationError, "MySQL 8"):
            migrate.ensure_mysql_8(FakeConnection(version="5.7.44"))
        settings = migrate.DatabaseSettings("db", 3306, "enem", "u", "p")
        with self.assertRaisesRegex(migrate.MigrationError, "--confirm"):
            migrate.run_baseline(FakeConnection(), settings, [migration()], False)
        with self.assertRaisesRegex(migrate.MigrationError, "--confirm"):
            migrate.reconcile_failure(
                FakeConnection(),
                settings,
                [migration()],
                "000",
                False
            )


class ImportAndEntrypointTest(unittest.TestCase):
    def run_isolated(self, *arguments):
        environment = os.environ.copy()
        environment.update(
            PYTHONPATH=str(migrate.PROJECT_ROOT / "backend"),
            PYTHON_DOTENV_DISABLED="1",
            DATABASE_URL="configuracao-invalida-para-importacao",
            DB_PORT="invalida",
        )
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, *arguments],
                cwd=directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=15,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_importacao_sem_configuracao_conexao_ou_cli(self):
        self.run_isolated(
            "-c",
            textwrap.dedent('''
            from unittest.mock import patch

            with patch("dotenv.load_dotenv", side_effect=AssertionError("configuracao")), \
                 patch("pymysql.connect", side_effect=AssertionError("conexao")), \
                 patch("argparse.ArgumentParser.parse_args", side_effect=AssertionError("cli")):
                from database import migration_types, sql_scripts, legacy_schema, migrate

                for operation in (
                    lambda: sql_scripts.split_sql("SELECT 'aberto"),
                    lambda: migrate.load_database_settings({}),
                ):
                    try:
                        operation()
                    except migration_types.MigrationError:
                        pass
                    else:
                        raise AssertionError("Entrada invalida aceita")
        ''')
        )

    def test_help_por_caminho_fora_do_projeto(self):
        output = self.run_isolated(
            str(migrate.PROJECT_ROOT / "backend" / "database" / "migrate.py"),
            "--help"
        )
        for command in ("status", "up", "baseline", "reconcile"):
            self.assertIn(command, output)

    def test_help_em_pacote_fora_do_projeto(self):
        output = self.run_isolated("-m", "database.migrate", "--help")
        for command in ("status", "up", "baseline", "reconcile"):
            self.assertIn(command, output)


class CliTest(unittest.TestCase):
    @patch("database.migrate.connect")
    @patch("database.migrate.discover_migrations", return_value=[migration()])
    @patch("database.migrate.load_database_settings")
    @patch("database.migrate.status_lines", return_value=["Schema: enem", "000 PENDING"])
    def test_status_e_up(self, status_lines, settings, _discover, connection):
        settings.return_value = migrate.DatabaseSettings("db", 3306, "enem", "u", "p")
        connection.return_value = MagicMock()
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(migrate.main(["status"]), 0)
        self.assertIn("000 PENDING", output.getvalue())
        status_lines.assert_called_once()

        with patch("database.migrate.run_up", return_value=2), redirect_stdout(output):
            self.assertEqual(migrate.main(["up"]), 0)
        self.assertIn("2 migration(s)", output.getvalue())

    @patch("database.migrate.connect")
    @patch("database.migrate.discover_migrations", return_value=[migration()])
    @patch("database.migrate.load_database_settings")
    def test_baseline_reconcile_e_atalhos_make(self, settings, _discover, connection):
        settings.return_value = migrate.DatabaseSettings("db", 3306, "enem", "u", "p")
        connection.return_value = MagicMock()
        output = io.StringIO()
        with patch("database.migrate.run_baseline", return_value="002"), redirect_stdout(output):
            self.assertEqual(migrate.main(["baseline", "--confirm"]), 0)
        self.assertIn("ate 002", output.getvalue())

        with patch("database.migrate.reconcile_failure") as reconcile, redirect_stdout(output):
            self.assertEqual(migrate.main(["reconcile", "001", "--confirm"]), 0)
        reconcile.assert_called_once()
        self.assertIn("001 reconciliada", output.getvalue())

        makefile = (migrate.PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
        for target in ("db-status:", "db-up:", "db-baseline:", "db-reconcile:"):
            self.assertIn(target, makefile)

    @patch("database.migrate.load_database_settings", side_effect=RuntimeError("senha-sentinela"))
    def test_falha_inesperada_nao_expoe_segredo(self, _settings):
        error = io.StringIO()
        with redirect_stderr(error):
            self.assertEqual(migrate.main(["status"]), 1)
        self.assertNotIn("senha-sentinela", error.getvalue())
        self.assertIn("schema selecionado", error.getvalue())


if __name__ == "__main__":
    unittest.main()
