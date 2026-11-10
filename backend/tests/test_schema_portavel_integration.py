"""Restauração estrutural e recusa de drift em schemas MySQL descartáveis."""

from contextlib import contextmanager
from dataclasses import replace
import re
from uuid import uuid4

from database import legacy_schema, migrate, sql_resources
from tests.migration_integration_support import (
    MIGRATION_TEST_PREFIX,
    MySQLMigrationTestCase,
    validate_migration_test_schema,
)


class SchemaPortavelIntegrationTest(MySQLMigrationTestCase):
    @contextmanager
    def second_schema(self):
        name = validate_migration_test_schema(MIGRATION_TEST_PREFIX + uuid4().hex[: 12])
        connection = None
        try:
            with self.admin_connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            settings = replace(self.settings, name=name)
            connection = migrate.connect(settings)
            yield connection, settings
        finally:
            try:
                if connection is not None:
                    connection.close()
            finally:
                with self.admin_connection.cursor() as cursor:
                    cursor.execute(f"DROP DATABASE IF EXISTS `{name}`")

    def seed(self):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO usuarios(id,nome,email,senha_hash,perfil,ativo,criado_em) "
                "VALUES(101,'Sintético','schema@teste.local','hash','aluno',1,'2026-11-07 12:00:00')")
            cursor.execute("INSERT INTO materias(id,nome,area_enem_id) VALUES(102,'Matéria sintética',4)")
            cursor.execute("INSERT INTO simulados(id,titulo,estado,revisao,autor_id,criado_em,atualizado_em) "
                "VALUES(103,'Simulado sintético','rascunho',1,101,'2026-11-07 12:00:00','2026-11-07 12:00:00')")

    def rows(self, connection, include_history=False):
        tables = migrate._user_tables(connection)
        if include_history:
            tables.add(migrate.HISTORY_TABLE)
        result = {}
        with connection.cursor() as cursor:
            for table in sorted(tables):
                cursor.execute(f"SELECT * FROM `{table}` ORDER BY 1")
                result[table] = cursor.fetchall()
        return result

    def restore(self, target, include_history=False):
        tables = sorted(migrate._user_tables(self.connection))
        if include_history:
            tables.append(migrate.HISTORY_TABLE)
        altered = 0
        with self.connection.cursor() as source, target.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            try:
                for table in tables:
                    source.execute(f"SHOW CREATE TABLE `{table}`")
                    ddl = source.fetchone()["Create Table"]
                    # Reproduz o charset redundante sem normalizar o validador.
                    variant = re.sub(
                        r"(varchar\(\d+\)) COLLATE utf8mb4_",
                        r"\1 CHARACTER SET utf8mb4 COLLATE utf8mb4_",
                        ddl
                    )
                    altered += variant != ddl
                    cursor.execute(variant)
                    source.execute(
                        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s "
                        "AND GENERATION_EXPRESSION='' ORDER BY ORDINAL_POSITION",
                        (
                            table,
                        )
                    )
                    columns = [row["COLUMN_NAME"] for row in source.fetchall()]
                    names = ",".join(f"`{name}`" for name in columns)
                    source.execute(f"SELECT {names} FROM `{table}` ORDER BY 1")
                    rows = source.fetchall()
                    if rows:
                        cursor.executemany(
                            f"INSERT INTO `{table}` ({names}) VALUES ({','.join(['%s'] * len(columns))})",
                            [tuple(row[name] for name in columns) for row in rows]
                        )
                routines, views = sql_resources.inventariar(self.connection)
                for routine in sorted(routines):
                    source.execute(f"SHOW CREATE PROCEDURE `{routine}`")
                    ddl = source.fetchone()["Create Procedure"]
                    cursor.execute(re.sub(r'DEFINER=`[^`]*`@`[^`]*`', '', ddl))
                source.execute('SELECT DATABASE() AS nome')
                origem = source.fetchone()['nome']
                cursor.execute('SELECT DATABASE() AS nome')
                destino = cursor.fetchone()['nome']
                ordem = [
                    'vw_conteudo_classificacao_historica',
                    'vw_praticas_fatos_desempenho',
                    'vw_simulados_fatos_desempenho',
                    'vw_simulados_atividades'
                ]
                for view in ordem:
                    if view in views:
                        source.execute(f"SHOW CREATE VIEW `{view}`")
                        ddl = source.fetchone()['Create View']
                        ddl = re.sub(r'DEFINER=`[^`]*`@`[^`]*`', '', ddl)
                        ddl = sql_resources.normalizar_schema(
                            ddl,
                            origem
                        ).replace(
                            '`<local>`.',
                            '`'+destino+'`.'
                        )
                        cursor.execute(ddl)
            finally:
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        self.assertGreater(altered, 0, "A fixture precisa conter DDL com charset redundante.")

    def test_round_trip_prefixos_baseline_upgrade_dados_e_contadores(self):
        for prefix in ("008", "009", "010", "011", "012", "013", "014", "015", "016", "017"):
            with self.subTest(prefix=prefix):
                self.recreate_schema()
                self.apply_without_history(prefix)
                self.seed()
                before = self.rows(self.connection)
                with self.second_schema() as (target, settings):
                    self.restore(target)
                    with target.cursor() as cursor:
                        cursor.execute("ALTER TABLE simulados AUTO_INCREMENT=9999")
                        cursor.execute("ANALYZE TABLE simulados")
                    self.assertEqual(self.rows(target), before)
                    # Expectativa independente do helper: prefixo oficial e invariantes.
                    self.assertEqual(migrate.detect_legacy_prefix(target), prefix)
                    for table in set(migrate.SIMULADOS_FINGERPRINTS) | (set(migrate.PLANOS_FINGERPRINTS) if prefix >= '009' else set()) | ({'registros_privacidade'} if prefix >= '010' else set()):
                        self.assertEqual(
                            legacy_schema._table_fingerprint(self.connection, table),
                            legacy_schema._table_fingerprint(target, table)
                        )
                    self.assertEqual(
                        migrate.run_baseline(
                            target,
                            settings,
                            self.migrations,
                            confirmed=True
                        ),
                        prefix
                    )
                    self.assertEqual(self.rows(target), before)
                    history = migrate.fetch_history(target)
                    self.assertEqual(
                        [(
                            row['version'],
                            row['checksum'],
                            row['status']
                        ) for row in history],
                        [(
                            item.version,
                            item.checksum,
                            'APPLIED'
                        ) for item in self.migrations[: int(prefix) + 1]]
                    )
                    self.assertEqual(
                        migrate.run_up(
                            target,
                            settings,
                            self.migrations
                        ),
                        17 - int(prefix)
                    )
                    self.assertEqual(migrate.run_up(target, settings, self.migrations), 0)
                    after = self.rows(target)
                    for table, rows in before.items():
                        self.assertEqual(after[table], rows)
                    self.assertEqual(migrate.detect_legacy_prefix(target), '017')

    def test_round_trip_com_historico_preserva_checksums_e_nao_reexecuta(self):
        migrate.run_up(self.connection, self.settings, self.migrations)
        self.seed()
        before = self.rows(self.connection, include_history=True)
        with self.second_schema() as (target, settings):
            self.restore(target, include_history=True)
            self.assertEqual(migrate.run_up(target, settings, self.migrations), 0)
            self.assertEqual(self.rows(target, include_history=True), before)
            self.assertEqual(migrate.detect_legacy_prefix(target), '017')
            with target.cursor() as cursor:
                cursor.execute(
                    "UPDATE schema_migrations SET checksum=%s WHERE version='008'",
                    (
                        '0' * 64,
                    )
                )
            with self.assertRaisesRegex(migrate.MigrationError, 'Checksum'):
                migrate.run_up(target, settings, self.migrations)

    def test_drift_recusado_sem_baseline_nem_dml_funcional(self):
        mutations = {
            'tipo': ["ALTER TABLE registros_privacidade MODIFY versao VARCHAR(21) NOT NULL"],
            'nulabilidade': ["ALTER TABLE registros_privacidade MODIFY versao VARCHAR(20) NULL"],
            'default_literal': ["ALTER TABLE registros_privacidade ALTER versao SET DEFAULT 'NULL'"],
            'collation': ["ALTER TABLE registros_privacidade MODIFY versao VARCHAR(20) COLLATE utf8mb4_bin NOT NULL"],
            'charset': ["ALTER TABLE registros_privacidade MODIFY versao VARCHAR(20) CHARACTER SET ascii NOT NULL"],
            'ordem_coluna': ["ALTER TABLE registros_privacidade MODIFY versao VARCHAR(20) NOT NULL AFTER id"],
            'coluna_extra': ["ALTER TABLE registros_privacidade ADD extra INT NULL"],
            'sem_auto_increment': ["ALTER TABLE registros_privacidade MODIFY id BIGINT NOT NULL"],
            'indice_ausente': ["ALTER TABLE registros_privacidade DROP INDEX ix_privacidade_ultima"],
            'ordem_indice': ["ALTER TABLE registros_privacidade DROP INDEX ix_privacidade_ultima, ADD INDEX ix_privacidade_ultima(usuario_id,id,tipo)"],
            'unicidade': ["ALTER TABLE registros_privacidade DROP INDEX uq_privacidade_chave, ADD INDEX uq_privacidade_chave(usuario_id,chave_envio)"],
            'visibilidade': ["ALTER TABLE registros_privacidade ALTER INDEX ix_privacidade_ultima INVISIBLE"],
            'prefixo_indice': ["ALTER TABLE registros_privacidade ADD INDEX ix_versao(versao(3))"],
            'expressao_indice': ["ALTER TABLE registros_privacidade ADD INDEX ix_expressao((revisao_base + 1))"],
            'fk_regra': [
                "ALTER TABLE registros_privacidade DROP FOREIGN KEY fk_privacidade_usuario",
                "ALTER TABLE registros_privacidade ADD CONSTRAINT fk_privacidade_usuario FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE RESTRICT"
            ],
            'fk_destino': [
                "ALTER TABLE registros_privacidade DROP FOREIGN KEY fk_privacidade_usuario",
                "ALTER TABLE registros_privacidade ADD CONSTRAINT fk_privacidade_usuario FOREIGN KEY(usuario_id) REFERENCES materias(id) ON DELETE RESTRICT ON UPDATE RESTRICT"
            ],
            'check_expressao': [
                "ALTER TABLE registros_privacidade DROP CHECK ck_privacidade_revisao",
                "ALTER TABLE registros_privacidade ADD CONSTRAINT ck_privacidade_revisao CHECK(revisao_base >= 1)"
            ],
            'check_enforced': ["ALTER TABLE registros_privacidade ALTER CHECK ck_privacidade_revisao NOT ENFORCED"],
            'generated': ["ALTER TABLE planos_estudo MODIFY usuario_atual INT GENERATED ALWAYS AS (CASE WHEN atual=1 THEN usuario_id + 1 ELSE NULL END) STORED"],
            'row_format': ["ALTER TABLE registros_privacidade ROW_FORMAT=COMPACT"],
            'opcoes': ["ALTER TABLE registros_privacidade STATS_PERSISTENT=0"],
            'comentario_tabela': ["ALTER TABLE registros_privacidade COMMENT='Divergente'"],
            'comentario_coluna': ["ALTER TABLE registros_privacidade MODIFY versao VARCHAR(20) NOT NULL COMMENT 'Divergente'"],
            'engine': [
                "ALTER TABLE registros_privacidade DROP FOREIGN KEY fk_privacidade_usuario",
                "ALTER TABLE registros_privacidade ENGINE=MyISAM"
            ],
            'tabela_ausente': ["DROP TABLE registros_privacidade", "DROP TABLE plano_estudo_itens"],
            'tabela_extra': ["CREATE TABLE extra(id INT PRIMARY KEY)"],
            'procedure_ausente': ["DROP PROCEDURE sp_questoes_por_assunto"],
        }
        for dimension, commands in mutations.items():
            with self.subTest(dimension=dimension):
                self.recreate_schema()
                self.apply_without_history('010')
                self.seed()
                with self.connection.cursor() as cursor:
                    for command in commands:
                        cursor.execute(command)
                before = self.rows(self.connection)
                with self.assertRaises(migrate.MigrationError):
                    migrate.run_baseline(
                        self.connection,
                        self.settings,
                        self.migrations,
                        confirmed=True
                    )
                self.assertEqual(migrate.fetch_history(self.connection), [])
                self.assertEqual(self.rows(self.connection), before)

    def test_fk_externa_nao_equivale_a_interna(self):
        self.apply_without_history('010')
        self.seed()
        with self.second_schema() as (external, settings):
            with external.cursor() as cursor:
                cursor.execute('CREATE TABLE usuarios(id INT PRIMARY KEY) ENGINE=InnoDB')
            with self.connection.cursor() as cursor:
                cursor.execute('ALTER TABLE registros_privacidade DROP FOREIGN KEY fk_privacidade_usuario')
                cursor.execute(f'ALTER TABLE registros_privacidade ADD CONSTRAINT fk_privacidade_usuario '
                    f'FOREIGN KEY(usuario_id) REFERENCES `{settings.name}`.usuarios(id) '
                    'ON UPDATE RESTRICT ON DELETE RESTRICT')
            before = self.rows(self.connection)
            try:
                with self.assertRaisesRegex(migrate.MigrationError, 'privacidade'):
                    migrate.run_baseline(
                        self.connection,
                        self.settings,
                        self.migrations,
                        confirmed=True
                    )
                self.assertEqual(migrate.fetch_history(self.connection), [])
                self.assertEqual(self.rows(self.connection), before)
            finally:
                with self.connection.cursor() as cursor:
                    cursor.execute('ALTER TABLE registros_privacidade DROP FOREIGN KEY fk_privacidade_usuario')

    def test_procedure_incompativel_continua_recusada_no_prefixo_legado(self):
        self.apply_without_history('002')
        with self.connection.cursor() as cursor:
            cursor.execute('DROP PROCEDURE sp_questoes_por_assunto')
            cursor.execute('CREATE PROCEDURE sp_questoes_por_assunto(IN p_assunto_id INT) SELECT 1')
        with self.assertRaisesRegex(migrate.MigrationError, 'Corpo da Stored Procedure'):
            migrate.run_baseline(self.connection, self.settings, self.migrations, confirmed=True)
        self.assertEqual(migrate.fetch_history(self.connection), [])

    def test_procedure_corpo_e_parametros_recusados_em_008_009_010(self):
        variants = [
            ('IN p_assunto_id INT', 'SELECT 1', 'Corpo'),
            (
                'IN outro_nome INT',
                migrate.EXPECTED_PROCEDURE_BODY.replace(
                    'p_assunto_id',
                    'outro_nome'
                ),
                'Assinatura'
            ),
            ('OUT p_assunto_id INT', migrate.EXPECTED_PROCEDURE_BODY, 'Assinatura'),
            ('IN p_assunto_id BIGINT', migrate.EXPECTED_PROCEDURE_BODY, 'Assinatura'),
            ('IN p_assunto_id INT, IN extra INT', migrate.EXPECTED_PROCEDURE_BODY, 'Assinatura'),
        ]
        for prefix in ('008', '009', '010'):
            self.recreate_schema()
            self.apply_without_history(prefix)
            self.seed()
            before = self.rows(self.connection)
            for parameters, body, message in variants:
                with self.subTest(prefix=prefix, parameters=parameters, message=message):
                    with self.connection.cursor() as cursor:
                        cursor.execute('DROP PROCEDURE sp_questoes_por_assunto')
                        cursor.execute(f'CREATE PROCEDURE sp_questoes_por_assunto({parameters}) {body}')
                    with self.assertRaisesRegex(migrate.MigrationError, message):
                        migrate.run_baseline(
                            self.connection,
                            self.settings,
                            self.migrations,
                            confirmed=True
                        )
                    self.assertEqual(migrate.fetch_history(self.connection), [])
                    self.assertEqual(self.rows(self.connection), before)

    def test_limpeza_do_segundo_schema_mesmo_apos_falha(self):
        name = None
        with self.assertRaisesRegex(RuntimeError, 'falha sintética'):
            with self.second_schema() as (_, settings):
                name = settings.name
                raise RuntimeError('falha sintética')
        with self.admin_connection.cursor() as cursor:
            cursor.execute(
                'SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s',
                (
                    name,
                )
            )
            self.assertIsNone(cursor.fetchone())
