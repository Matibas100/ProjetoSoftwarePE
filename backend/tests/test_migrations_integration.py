from dataclasses import replace
from pathlib import Path

from database import migrate
from tests.migration_integration_support import MySQLMigrationTestCase


FAILURE_MIGRATIONS = (
    Path(__file__).resolve().parent / "fixtures" / "migrations_failure"
)
UPGRADE_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "catalogo_upgrade"


class MigrationRunnerIntegrationTest(MySQLMigrationTestCase):
    def _execute_file(self, path):
        sql = path.read_text(encoding="utf-8")
        migrate.execute_statements(
            self.connection, migrate.validate_statements(migrate.split_sql(sql))
        )

    def test_upgrade_preserva_dados_e_aplica_backfill_fechado(self):
        self.apply_without_history("002")
        self._execute_file(UPGRADE_FIXTURES / "validos.sql")
        self._execute_file(self.migrations[3].path)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), "003")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, nome, descricao, area_enem_id FROM materias "
                "WHERE id IN (910001, 910002) ORDER BY id"
            )
            self.assertEqual(
                cursor.fetchall(),
                [
                    {"id": 910001, "nome": "Matemática", "descricao": "Descrição preservada", "area_enem_id": 4},
                    {"id": 910002, "nome": "História", "descricao": None, "area_enem_id": 2},
                ],
            )
            cursor.execute("SELECT nome_normalizado FROM assuntos WHERE id = 920001")
            self.assertEqual(cursor.fetchone()["nome_normalizado"], "geometria plana")
            cursor.execute("SELECT assunto_id FROM questoes WHERE id = 930001")
            self.assertEqual(cursor.fetchone()["assunto_id"], 920001)
        self._execute_file(self.migrations[4].path)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), "004")

    def test_precheck_preserva_materia_nao_classificada(self):
        self.apply_without_history("002")
        self._execute_file(UPGRADE_FIXTURES / "materia_nao_classificavel.sql")
        self._execute_file(self.migrations[3].path)
        with self.assertRaisesRegex(Exception, "CATALOGO_004_MATERIAS_NAO_CLASSIFICADAS"):
            self._execute_file(self.migrations[4].path)
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT nome, area_enem_id FROM materias WHERE id = 910003")
            self.assertEqual(
                cursor.fetchone(), {"nome": "Astronomia Avançada", "area_enem_id": None}
            )

    def test_precheck_preserva_assuntos_conflitantes(self):
        self.apply_without_history("002")
        self._execute_file(UPGRADE_FIXTURES / "assuntos_conflitantes.sql")
        self._execute_file(self.migrations[3].path)
        with self.assertRaisesRegex(
            Exception, "CATALOGO_004_ASSUNTOS_NORMALIZADOS_CONFLITANTES"
        ):
            self._execute_file(self.migrations[4].path)
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, nome FROM assuntos WHERE id IN (920003, 920004) ORDER BY id"
            )
            self.assertEqual([row["id"] for row in cursor.fetchall()], [920003, 920004])

    def test_instalacao_idempotencia_historico_e_procedure(self):
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 5)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)

        history = migrate.fetch_history(self.connection)
        self.assertEqual(
            [row["version"] for row in history], ["000", "001", "002", "003", "004"]
        )
        self.assertTrue(all(row["status"] == "APPLIED" for row in history))
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), "004")

        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO materias (nome, area_enem_id) VALUES ('Materia migration', 4)"
            )
            materia_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO assuntos (nome, nome_normalizado, materia_id) "
                "VALUES ('Assunto migration', 'assunto migration', %s)", (materia_id,),
            )
            assunto_id = cursor.lastrowid
            values = (
                "Enunciado",
                "A",
                "B",
                "C",
                "D",
                "E",
                "A",
                "facil",
                assunto_id,
            )
            cursor.execute(
                "INSERT INTO questoes (enunciado, alternativa_a, alternativa_b, "
                "alternativa_c, alternativa_d, alternativa_e, resposta_correta, "
                "dificuldade, assunto_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                values,
            )
            first_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO questoes (enunciado, alternativa_a, alternativa_b, "
                "alternativa_c, alternativa_d, alternativa_e, resposta_correta, "
                "dificuldade, assunto_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                values,
            )
            second_id = cursor.lastrowid
            cursor.execute("CALL sp_questoes_por_assunto(%s)", (assunto_id,))
            ids = [row["id"] for row in cursor.fetchall()]
            while cursor.nextset():
                pass
        self.assertEqual(ids, [first_id, second_id])

    def test_baseline_reconhece_todos_os_prefixos_sem_alterar_dados(self):
        for prefix in ("000", "001", "002", "003", "004"):
            with self.subTest(prefix=prefix):
                self.recreate_schema()
                self.apply_without_history(prefix)
                with self.connection.cursor() as cursor:
                    if int(prefix) >= 3:
                        cursor.execute(
                            "INSERT INTO materias (nome, area_enem_id) "
                            "VALUES ('Matemática', 4)"
                        )
                    else:
                        cursor.execute("INSERT INTO materias (nome) VALUES ('Matemática')")
                    persisted_id = cursor.lastrowid

                self.assertEqual(
                    migrate.run_baseline(
                        self.connection, self.settings, self.migrations, confirmed=True
                    ),
                    prefix,
                )
                history = migrate.fetch_history(self.connection)
                self.assertEqual(history[-1]["version"], prefix)
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT nome FROM materias WHERE id = %s", (persisted_id,))
                    self.assertEqual(cursor.fetchone()["nome"], "Matemática")

                expected_pending = 4 - int(prefix)
                self.assertEqual(
                    migrate.run_up(self.connection, self.settings, self.migrations),
                    expected_pending,
                )
                self.assertEqual(migrate.detect_legacy_prefix(self.connection), "004")

    def test_baseline_recusa_schema_divergente(self):
        self.apply_without_history("000")
        with self.connection.cursor() as cursor:
            cursor.execute("ALTER TABLE materias ADD COLUMN divergente INT NULL")
            cursor.execute("INSERT INTO materias (nome) VALUES ('Nao remover')")
        with self.assertRaisesRegex(migrate.MigrationError, "Colunas"):
            migrate.run_baseline(
                self.connection, self.settings, self.migrations, confirmed=True
            )
        self.assertEqual(migrate.fetch_history(self.connection), [])
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM materias")
            self.assertEqual(cursor.fetchone()["total"], 1)

        self.recreate_schema()
        self.apply_without_history("000")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE questoes DROP CHECK ck_questoes_dificuldade"
            )
            cursor.execute(
                "ALTER TABLE questoes ADD CONSTRAINT ck_questoes_dificuldade "
                "CHECK (dificuldade IN ('facil', 'media'))"
            )
        with self.assertRaisesRegex(migrate.MigrationError, "Checks"):
            migrate.run_baseline(
                self.connection, self.settings, self.migrations, confirmed=True
            )

        self.recreate_schema()
        self.apply_without_history("002")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE tabela_extra (id INT NOT NULL PRIMARY KEY) ENGINE = InnoDB"
            )
        with self.assertRaisesRegex(migrate.MigrationError, "tabelas MVP"):
            migrate.run_baseline(
                self.connection, self.settings, self.migrations, confirmed=True
            )
        self.assertEqual(migrate.fetch_history(self.connection), [])

    def test_lock_concorrente_bloqueia_segundo_runner(self):
        second_connection = migrate.connect(self.settings)
        self.addCleanup(second_connection.close)
        with migrate.migration_lock(self.connection, self.settings.name, timeout=0):
            with self.assertRaisesRegex(migrate.MigrationError, "Outra execucao"):
                migrate.run_up(
                    second_connection,
                    self.settings,
                    self.migrations,
                    lock_timeout=0,
                )

    def test_falha_bloqueia_reexecucao_e_exige_reconciliacao(self):
        migrations = migrate.discover_migrations(FAILURE_MIGRATIONS)
        with self.assertRaisesRegex(migrate.MigrationError, "001 falhou"):
            migrate.run_up(self.connection, self.settings, migrations)
        history = migrate.fetch_history(self.connection)
        self.assertEqual([row["status"] for row in history], ["APPLIED", "FAILED"])
        self.assertEqual(history[1]["error_code"], "MYSQL_1064")

        with self.assertRaisesRegex(migrate.MigrationError, "exige reconciliacao"):
            migrate.run_up(self.connection, self.settings, migrations)
        with self.assertRaisesRegex(migrate.MigrationError, "nao e a execucao"):
            migrate.reconcile_failure(
                self.connection, self.settings, migrations, "000", confirmed=True
            )
        migrate.reconcile_failure(
            self.connection, self.settings, migrations, "001", confirmed=True
        )
        lines = migrate.status_lines(self.connection, self.settings, migrations)
        self.assertTrue(any("RETRY_READY" in line for line in lines))

    def test_running_e_checksum_divergente_bloqueiam_avanco(self):
        migrate.ensure_history_table(self.connection)
        first = self.migrations[0]
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO schema_migrations "
                "(version, script_name, description, checksum, status) "
                "VALUES (%s, %s, %s, %s, 'RUNNING')",
                (first.version, first.script_name, first.description, first.checksum),
            )
        with self.assertRaisesRegex(migrate.MigrationError, "RUNNING"):
            migrate.run_up(self.connection, self.settings, self.migrations)

        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM schema_migrations")
        migrate.run_up(self.connection, self.settings, self.migrations)
        drifted = [replace(self.migrations[0], checksum="0" * 64), *self.migrations[1:]]
        with self.assertRaisesRegex(migrate.MigrationError, "Checksum"):
            migrate.run_up(self.connection, self.settings, drifted)

    def test_bootstrap_consolidado_equivale_as_migrations(self):
        migrate.run_up(self.connection, self.settings, self.migrations)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), "004")

        other_name = self.schema_name[:-12] + "f" * 12
        if other_name == self.schema_name:
            other_name = self.schema_name[:-12] + "e" * 12
        from tests.migration_integration_support import validate_migration_test_schema

        validate_migration_test_schema(other_name)
        with self.admin_connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE `{other_name}` CHARACTER SET utf8mb4 "
                "COLLATE utf8mb4_unicode_ci"
            )
        other_settings = replace(self.settings, name=other_name)
        other_connection = migrate.connect(other_settings)
        try:
            snapshot = (
                migrate.PROJECT_ROOT / "backend" / "database" / "create_database.sql"
            ).read_text(encoding="utf-8")
            statements = migrate.split_sql(snapshot)
            selected = []
            for statement in statements:
                significant = migrate._without_leading_comments(statement).upper()
                if significant.startswith("CREATE DATABASE") or significant.startswith("USE "):
                    continue
                selected.append(statement)
            migrate.execute_statements(other_connection, selected)
            self.assertEqual(migrate.detect_legacy_prefix(other_connection), "004")
        finally:
            other_connection.close()
            with self.admin_connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS `{other_name}`")
