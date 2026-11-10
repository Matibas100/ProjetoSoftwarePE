"""Contratos, upgrade e reconhecimento conservador da migration 017."""
from pathlib import Path
import pymysql
from database import migrate, sql_resources
from tests.migration_integration_support import MySQLMigrationTestCase
from tests import test_contas_procedures_migrations_integration as contas


class GestaoAlunosMigrationsIntegrationTest(MySQLMigrationTestCase):
    second_schema = contas.ContasProceduresMigrationsIntegrationTest.second_schema
    restore = contas.ContasProceduresMigrationsIntegrationTest.restore
    rows = contas.ContasProceduresMigrationsIntegrationTest.rows
    seed = contas.ContasProceduresMigrationsIntegrationTest.seed
    seed_planos = contas.ContasProceduresMigrationsIntegrationTest.seed_planos
    seed_contas = contas.ContasProceduresMigrationsIntegrationTest.seed_contas
    alterar = contas.ContasProceduresMigrationsIntegrationTest.alterar

    def test_upgrade_snapshot_baseline_dados_e_reexecucao(self):
        migrate.run_up(self.connection, self.settings, self.migrations[: 17])
        self.seed_contas()
        antes = self.rows(self.connection)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 1)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), '017')
        self.assertEqual(self.rows(self.connection), antes)
        with self.second_schema() as (c, s):
            self.restore(c)
            self.assertEqual(migrate.run_baseline(c, s, self.migrations, True), '017')
            self.assertEqual(migrate.run_up(c, s, self.migrations), 0)
            self.assertEqual(self.rows(c), antes)

    def test_bootstrap_equivale_instalacao_limpa(self):
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 18)
        with self.second_schema() as (c, s):
            sql=Path(migrate.__file__).with_name('create_database.sql').read_text(encoding='utf-8')
            migrate.execute_statements(
                c,
                [q for q in migrate.split_sql(sql) if not
                    migrate._without_leading_comments(q).upper().startswith((
                        'CREATE DATABASE',
                        'USE '
                    ))]
            )
            self.assertEqual(migrate.detect_legacy_prefix(c), '017')
            self.assertEqual(
                {n: sql_resources.assinatura(c, n) for n in sql_resources.NOMES},
                {n: sql_resources.assinatura(self.connection, n) for n in sql_resources.NOMES}
            )

    def test_parcial_drift_e_dependencia_invalida(self):
        self.apply_without_history('017')
        for nome in sorted(sql_resources.PROCEDURES_017):
            with self.subTest(nome=nome), self.connection.cursor() as c:
                c.execute('SHOW CREATE PROCEDURE '+nome)
                original=c.fetchone()['Create Procedure']
                c.execute('DROP PROCEDURE '+nome)
                try:
                    with self.assertRaises(migrate.MigrationError):
                        migrate.run_baseline(self.connection, self.settings, self.migrations, True)
                finally:
                    c.execute(original)
                for modificado in [
                    original.replace('INVOKER', 'DEFINER'),
                    original.replace(
                        'p_usuario_id INT',
                        'p_usuario_id BIGINT'
                    ) if 'p_usuario_id INT' in original
                    else original.replace('p_limite INT', 'p_limite BIGINT'),
                    original.replace("MESSAGE_TEXT='", "MESSAGE_TEXT='Divergente ")
                ]:
                    c.execute('DROP PROCEDURE '+nome)
                    c.execute(modificado)
                    try:
                        with self.assertRaises(migrate.MigrationError):
                            migrate.run_baseline(
                                self.connection,
                                self.settings,
                                self.migrations,
                                True
                            )
                    finally:
                        c.execute('DROP PROCEDURE '+nome)
                        c.execute(original)
        self.recreate_schema()
        migrate.run_up(self.connection, self.settings, self.migrations[: 17])
        with self.connection.cursor() as c:
            c.execute('DROP PROCEDURE sp_usuario_por_email')
        with self.assertRaises(migrate.MigrationError):
            migrate.run_up(self.connection, self.settings, self.migrations)
        self.assertEqual(len(migrate.fetch_history(self.connection)), 17)

    def test_contrato_listagem_literal_total_e_lock_inativo(self):
        self.apply_without_history('017')
        with self.connection.cursor() as c:
            for id, nome, perfil, ativo in [
                (
                    1,
                    'Aluno %_\\ literal',
                    'aluno',
                    0
                ),
                (
                    2,
                    'Aluno normal',
                    'aluno',
                    1
                ),
                (
                    3,
                    'Administrador',
                    'administrador',
                    1
                )
            ]:
                c.execute(
                    'INSERT INTO usuarios(id,nome,email,senha_hash,perfil,ativo,criado_em) '
                    'VALUES(%s,%s,%s,%s,%s,%s,%s)',
                    (
                        id,
                        nome,
                        f'conta{id}@teste.local',
                        'hash-privado',
                        perfil,
                        ativo,
                        '2026-11-09'
                    )
                )
            for busca, ativo, offset, ids, total in [
                (
                    None,
                    None,
                    0,
                    [
                        2,
                        1
                    ],
                    2
                ),
                (
                    '%_\\',
                    None,
                    0,
                    [1],
                    1
                ),
                (None, 0, 0, [1], 1),
                (None, None, 40, [], 2),
                ('CONTA2@', None, 0, [2], 1)
            ]:
                c.execute('CALL sp_alunos_admin(%s,%s,%s,%s)', (busca, ativo, offset, 20))
                self.assertEqual([r['id'] for r in c.fetchall()], ids)
                self.assertEqual(
                    [d[0] for d in c.description],
                    [
                        'id',
                        'nome',
                        'email',
                        'perfil',
                        'ativo',
                        'criado_em'
                    ]
                )
                self.assertTrue(c.nextset())
                self.assertEqual(c.fetchone()['total_itens'], total)
                while c.nextset():
                    pass
            c.execute('CALL sp_usuario_gestao_bloqueado(1)')
            self.assertEqual(c.fetchone()['ativo'], 0)
            while c.nextset():
                pass
            for params in [
                (
                    None,
                    2,
                    0,
                    20
                ),
                (
                    None,
                    None,
                    -1,
                    20
                ),
                (
                    None,
                    None,
                    0,
                    101
                ),
                (
                    None,
                    None,
                    0,
                    None
                )
            ]:
                with self.assertRaises(pymysql.MySQLError):
                    c.execute('CALL sp_alunos_admin(%s,%s,%s,%s)', params)
