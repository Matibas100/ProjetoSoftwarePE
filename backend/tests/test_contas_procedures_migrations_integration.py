"""Instalação, restauração e reconhecimento conservador da 016 no MySQL."""
import re
from pathlib import Path

import pymysql

from database import migrate, sql_resources
from tests.migration_integration_support import MySQLMigrationTestCase
from tests import test_schema_portavel_integration as fixture
from tests import test_plano_procedures_migrations_integration as planos


class ContasProceduresMigrationsIntegrationTest(MySQLMigrationTestCase):
    second_schema = fixture.SchemaPortavelIntegrationTest.second_schema
    restore = fixture.SchemaPortavelIntegrationTest.restore
    seed = fixture.SchemaPortavelIntegrationTest.seed
    rows = fixture.SchemaPortavelIntegrationTest.rows
    seed_planos = planos.PlanoProceduresMigrationsIntegrationTest.seed_planos
    alterar = planos.PlanoProceduresMigrationsIntegrationTest.alterar

    def setUp(self):
        super().setUp()
        self.migrations = self.migrations[: 17]

    def seed_contas(self):
        self.seed_planos()
        with self.connection.cursor() as c:
            c.execute(
                'INSERT INTO sessoes(id,usuario_id,identificador_hash,criada_em,ultimo_acesso_em,expira_em) '
                "VALUES(107,101,%s,'2026-11-08 12:00:00','2026-11-08 12:00:00','2026-11-08 20:00:00')",
                (
                    'b'*64,
                )
            )
            c.execute(
                'INSERT INTO auth_limites(chave_hash,falhas,janela_inicio) '
                "VALUES(%s,4,'2026-11-08 12:00:00')",
                ('c'*64,)
            )
            c.execute(
                'INSERT INTO registros_privacidade '
                '(id,usuario_id,tipo,acao,versao,documento_sha256,registrado_em,chave_envio,revisao_base) '
                "VALUES(108,101,'uso','aceitar','1.0',%s,'2026-11-08 12:00:00.123456',%s,0)",
                ('a'*64, '00000000-0000-0000-0000-000000000002')
            )

    def test_upgrade_015_016_dados_baseline_restauracao_idempotencia(self):
        self.apply_without_history('015')
        self.seed_contas()
        antes = self.rows(self.connection)
        self.assertEqual(
            migrate.run_baseline(
                self.connection,
                self.settings,
                self.migrations,
                True
            ),
            '015'
        )
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 1)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), '016')
        self.assertEqual(self.rows(self.connection), antes)
        with self.second_schema() as (restaurada, settings):
            self.restore(restaurada)
            self.assertEqual(
                migrate.run_baseline(
                    restaurada,
                    settings,
                    self.migrations,
                    True
                ),
                '016'
            )
            self.assertEqual(migrate.run_up(restaurada, settings, self.migrations), 0)
            self.assertEqual(self.rows(restaurada), antes)

    def test_bootstrap_equivale_instalacao_vazia_sem_dml_funcional(self):
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 17)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)
        oficiais = {n: sql_resources.assinatura(
            self.connection,
            n
        ) for n in sql_resources.NOMES - sql_resources.PROCEDURES_017}
        with self.second_schema() as (bootstrap, settings):
            sql = Path(migrate.__file__).with_name('create_database.sql').read_text(encoding='utf-8')
            comandos = [s for s in migrate.split_sql(sql) if not
                migrate._without_leading_comments(s).upper().startswith((
                    'CREATE DATABASE',
                    'USE '
                ))]
            migrate.execute_statements(bootstrap, comandos)
            self.assertEqual(migrate.detect_legacy_prefix(bootstrap), '017')
            self.assertEqual(
                {n: sql_resources.assinatura(
                    bootstrap,
                    n
                ) for n in sql_resources.NOMES - sql_resources.PROCEDURES_017},
                oficiais
            )
            self.assertEqual(self.rows(bootstrap), self.rows(self.connection))

    def test_cada_recurso_ausente_e_contrato_alterado_bloqueiam_baseline(self):
        self.apply_without_history('016')
        self.seed_contas()
        antes = self.rows(self.connection)
        for nome in sorted(sql_resources.PROCEDURES_016):
            with self.subTest(ausente=nome), self.connection.cursor() as c:
                c.execute('SHOW CREATE PROCEDURE '+nome)
                original = c.fetchone()['Create Procedure']
                c.execute('DROP PROCEDURE '+nome)
                try:
                    with self.assertRaises(migrate.MigrationError):
                        migrate.run_baseline(self.connection, self.settings, self.migrations, True)
                    self.assertEqual(migrate.fetch_history(self.connection), [])
                    self.assertEqual(self.rows(self.connection), antes)
                finally:
                    c.execute(original)
        for tipo in ('corpo', 'assinatura', 'seguranca', 'dependencia'):
            nome = 'sp_decisao_privacidade_por_chave' if tipo != 'dependencia' else 'sp_plano_itens'
            with self.subTest(tipo=tipo), self.connection.cursor() as c:
                c.execute('SHOW CREATE PROCEDURE '+nome)
                original = c.fetchone()['Create Procedure']
                self.alterar(tipo, nome)
                try:
                    with self.assertRaises(migrate.MigrationError):
                        migrate.run_baseline(self.connection, self.settings, self.migrations, True)
                    self.assertEqual(migrate.fetch_history(self.connection), [])
                    self.assertEqual(self.rows(self.connection), antes)
                finally:
                    c.execute('DROP PROCEDURE '+nome)
                    c.execute(original)

    def test_upgrade_recusa_drift_015_antes_running_ddl_e_permite_reparacao(self):
        for tipo in (
            'ausente',
            'corpo',
            'assinatura',
            'seguranca',
            'legada',
            'tabela',
            'parcial016',
            'completo016'
        ):
            with self.subTest(tipo=tipo):
                self.recreate_schema()
                migrate.run_up(self.connection, self.settings, self.migrations[: 16])
                self.seed_contas()
                with self.connection.cursor() as c:
                    c.execute('SHOW CREATE PROCEDURE sp_plano_itens')
                    original = c.fetchone()['Create Procedure']
                    if tipo == 'tabela':
                        c.execute('ALTER TABLE sessoes ADD divergente INT NULL')
                    elif tipo in {'parcial016', 'completo016'}:
                        comandos = migrate.validate_statements(migrate.split_sql(self.migrations[16].sql))
                        migrate.execute_statements(
                            self.connection,
                            comandos[: 1] if tipo == 'parcial016' else comandos
                        )
                    else:
                        self.alterar(
                            tipo,
                            'sp_questoes_por_assunto' if tipo == 'legada' else 'sp_plano_itens'
                        )
                antes, historico = self.rows(self.connection), migrate.fetch_history(self.connection)
                recursos = sql_resources.inventariar(self.connection)
                with self.assertRaises(migrate.MigrationError):
                    migrate.run_up(self.connection, self.settings, self.migrations)
                self.assertEqual(self.rows(self.connection), antes)
                self.assertEqual(migrate.fetch_history(self.connection), historico)
                self.assertEqual(sql_resources.inventariar(self.connection), recursos)
                with self.connection.cursor() as c:
                    c.execute(
                        'SELECT IS_USED_LOCK(%s) AS dono',
                        (
                            migrate._lock_name(self.settings.name),
                        )
                    )
                    self.assertIsNone(c.fetchone()['dono'])
                    if tipo == 'ausente':
                        c.execute(original)
                if tipo == 'ausente':
                    self.assertEqual(
                        migrate.run_up(
                            self.connection,
                            self.settings,
                            self.migrations
                        ),
                        1
                    )
                    self.assertEqual(
                        migrate.run_up(
                            self.connection,
                            self.settings,
                            self.migrations
                        ),
                        0
                    )

    def test_parametros_contratos_segurança_e_conexao_apos_erros(self):
        migrate.run_up(self.connection, self.settings, self.migrations)
        with self.connection.cursor() as c:
            invalidos = [
                'CALL sp_usuario_por_email(NULL)',
                "CALL sp_usuario_por_email('')",
                "CALL sp_consultar_sessao('curto')",
                'CALL sp_consultar_sessao(NULL)',
                'CALL sp_usuario_ativo_bloqueado(0)',
                'CALL sp_bloquear_identidade_privacidade(NULL)',
                'CALL sp_ultimas_decisoes_privacidade(0)',
                "CALL sp_decisao_privacidade_por_chave(1,'invalida')",
                'CALL sp_decisao_privacidade_por_chave(NULL,NULL)',
                "CALL sp_preparar_limite_autenticacao('curto','2026-11-08')",
                "CALL sp_preparar_limite_autenticacao(REPEAT('a',64),NULL)",
                'CALL sp_limpar_autenticacao(NULL)',
            ]
            for nome in (
                'sp_renovar_acesso_sessao',
                'sp_revogar_sessao',
                'sp_revogar_sessoes_usuario'
            ):
                invalidos.extend([f"CALL {nome}(0,'2026-11-08')", f'CALL {nome}(1,NULL)'])
            for comando in invalidos:
                with self.subTest(comando=comando), self.assertRaises(pymysql.MySQLError):
                    c.execute(comando)
                while c.nextset():
                    pass
            c.execute('CALL sp_renovar_acesso_sessao(2147483649,%s)', ('2026-11-08',))
            self.assertEqual(c.fetchone(), {'correspondencias': 0})
            while c.nextset():
                pass
            c.execute('CALL sp_revogar_sessoes_usuario(2147483649,%s)', ('2026-11-08',))
            self.assertEqual(c.fetchone(), {'afetadas': 0})
            while c.nextset():
                pass
            c.execute('CALL sp_ultimas_decisoes_privacidade(2147483649)')
            self.assertEqual(c.fetchall(), ())
            self.assertEqual(len(c.description), 9)
            self.assertTrue(c.nextset())  # Somente o conjunto terminal, sem colunas.
            self.assertIsNone(c.description)
            self.assertIsNone(c.nextset())
            c.execute('SELECT 7 AS ok')
            self.assertEqual(c.fetchone()['ok'], 7)
            c.execute('SELECT ROUTINE_NAME,SQL_DATA_ACCESS,SECURITY_TYPE FROM information_schema.ROUTINES '
                'WHERE ROUTINE_SCHEMA=DATABASE()')
            novas = [r for r in c.fetchall() if r['ROUTINE_NAME'] in sql_resources.PROCEDURES_016]
            self.assertEqual(len(novas), 11)
            escritas = {
                'sp_renovar_acesso_sessao',
                'sp_revogar_sessao',
                'sp_revogar_sessoes_usuario',
                'sp_preparar_limite_autenticacao',
                'sp_limpar_autenticacao'
            }
            for routine in novas:
                self.assertEqual(routine['SECURITY_TYPE'], 'INVOKER')
                self.assertEqual(
                    routine['SQL_DATA_ACCESS'],
                    'MODIFIES SQL DATA' if
                    routine['ROUTINE_NAME'] in escritas else 'READS SQL DATA'
                )
