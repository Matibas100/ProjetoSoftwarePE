"""Instalação, upgrade e reconhecimento fechado do prefixo 015."""
import re
from pathlib import Path

import pymysql

from database import migrate, sql_resources
from tests.migration_integration_support import MySQLMigrationTestCase
from tests import test_schema_portavel_integration as fixture


class PlanoProceduresMigrationsIntegrationTest(MySQLMigrationTestCase):
    second_schema = fixture.SchemaPortavelIntegrationTest.second_schema
    restore = fixture.SchemaPortavelIntegrationTest.restore
    seed = fixture.SchemaPortavelIntegrationTest.seed
    rows = fixture.SchemaPortavelIntegrationTest.rows

    def setUp(self):
        super().setUp()
        self.migrations = self.migrations[: 16]

    def seed_planos(self):
        self.seed()
        with self.connection.cursor() as c:
            c.execute("INSERT INTO assuntos(id,nome,nome_normalizado,materia_id) VALUES(104,'Sintético','sintetico',102)")
            c.execute("INSERT INTO planos_estudo(id,usuario_id,geracao,atual,periodo,gerado_em,chave_envio,operacao) "
                "VALUES(105,101,1,1,JSON_OBJECT(),'2026-11-08 12:00:00','00000000-0000-0000-0000-000000000001','gerar')")
            c.execute("INSERT INTO plano_estudo_itens(id,plano_id,assunto_id,materia_id,posicao,snapshot,estado) "
                "VALUES(106,105,104,102,1,JSON_OBJECT(),'pendente')")

    def test_upgrade_014_015_baseline_restauracao_dados_idempotencia(self):
        self.apply_without_history('014')
        self.seed_planos()
        antes = self.rows(self.connection)
        self.assertEqual(
            migrate.run_baseline(
                self.connection,
                self.settings,
                self.migrations,
                True
            ),
            '014'
        )
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 1)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), '015')
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
                '015'
            )
            self.assertEqual(migrate.run_up(restaurada, settings, self.migrations), 0)
            self.assertEqual(self.rows(restaurada), antes)

    def test_bootstrap_equivale_instalacao_vazia_sem_dml_funcional(self):
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 16)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)
        recursos = sql_resources.NOMES - sql_resources.PROCEDURES_016 - sql_resources.PROCEDURES_017
        oficiais = {n: sql_resources.assinatura(self.connection, n) for n in recursos}
        with self.second_schema() as (bootstrap, settings):
            sql = Path(migrate.__file__).with_name('create_database.sql').read_text(encoding='utf-8')
            comandos = [s for s in migrate.split_sql(sql) if not
                migrate._without_leading_comments(s).upper().startswith(('CREATE DATABASE', 'USE '))
                and not any(re.match(
                    r'CREATE PROCEDURE '+nome+r'\b',
                    migrate._without_leading_comments(s),
                    re.I
                )
                    for nome in sql_resources.PROCEDURES_016 | sql_resources.PROCEDURES_017)]
            migrate.execute_statements(bootstrap, comandos)
            self.assertEqual(migrate.detect_legacy_prefix(bootstrap), '015')
            self.assertEqual(
                {n: sql_resources.assinatura(
                    bootstrap,
                    n
                ) for n in recursos},
                oficiais
            )
            self.assertEqual(self.rows(bootstrap), self.rows(self.connection))

    def alterar(self, tipo, nome):
        with self.connection.cursor() as c:
            c.execute('SHOW CREATE PROCEDURE '+nome)
            ddl = c.fetchone()['Create Procedure']
            c.execute('DROP PROCEDURE '+nome)
            if tipo == 'ausente':
                return
            if tipo == 'assinatura':
                ddl = re.sub('BIGINT UNSIGNED', 'INT', ddl, count=1, flags=re.I)
            elif tipo == 'seguranca':
                ddl = ddl.replace('SQL SECURITY INVOKER', 'SQL SECURITY DEFINER')
            elif tipo == 'legada':
                ddl = 'CREATE PROCEDURE sp_questoes_por_assunto(IN p_assunto_id INT) SELECT 1'
            else:
                ddl = ddl.replace('FOR UPDATE', 'FOR SHARE')
            c.execute(ddl)

    def test_reconhecimento_rejeita_parcial_corpo_assinatura_seguranca_e_dependencia(self):
        for tipo in ('ausente', 'corpo', 'assinatura', 'seguranca', 'dependencia'):
            with self.subTest(tipo=tipo):
                self.recreate_schema()
                self.apply_without_history('015')
                self.seed_planos()
                antes = self.rows(self.connection)
                self.alterar(
                    tipo,
                    'sp_plano_itens' if tipo != 'dependencia' else 'sp_simulado_respostas'
                )
                with self.assertRaises(migrate.MigrationError):
                    migrate.run_baseline(self.connection, self.settings, self.migrations, True)
                self.assertEqual(migrate.fetch_history(self.connection), [])
                self.assertEqual(self.rows(self.connection), antes)

    def test_upgrade_bloqueia_drift_014_antes_ddl_e_permite_reparacao(self):
        for tipo in (
            'ausente',
            'corpo',
            'assinatura',
            'seguranca',
            'legada',
            'tabela',
            'parcial015',
            'completo015'
        ):
            with self.subTest(tipo=tipo):
                self.recreate_schema()
                migrate.run_up(self.connection, self.settings, self.migrations[: 15])
                self.seed_planos()
                with self.connection.cursor() as c:
                    c.execute('SHOW CREATE PROCEDURE sp_simulado_respostas')
                    original = c.fetchone()['Create Procedure']
                if tipo == 'tabela':
                    with self.connection.cursor() as c:
                        c.execute('ALTER TABLE planos_estudo ADD divergente INT NULL')
                elif tipo in {'parcial015', 'completo015'}:
                    comandos = migrate.validate_statements(migrate.split_sql(self.migrations[15].sql))
                    migrate.execute_statements(
                        self.connection,
                        comandos[: 1] if tipo == 'parcial015' else comandos
                    )
                else:
                    self.alterar(
                        tipo,
                        'sp_questoes_por_assunto' if tipo == 'legada' else 'sp_simulado_respostas'
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

    def test_formatos_vazios_flags_contratos_e_conexao_reutilizavel(self):
        migrate.run_up(self.connection, self.settings, self.migrations)
        with self.connection.cursor() as c:
            c.execute('CALL sp_pares_elegiveis_plano(%s,1)', ('[]',))
            self.assertEqual(c.fetchall(), ())
            while c.nextset():
                pass
            for lista in (None, '{}', '[null]', '[0]', '["texto"]', '[-1]', '[true]'):
                with self.assertRaises(pymysql.MySQLError):
                    c.execute('CALL sp_pares_elegiveis_plano(%s,0)', (lista,))
                while c.nextset():
                    pass
            for flag in (None, -1, 2):
                for comando in (
                    'CALL sp_plano_atual(1,%s)',
                    'CALL sp_pares_elegiveis_plano(JSON_ARRAY(),%s)'
                ):
                    with self.assertRaises(pymysql.MySQLError):
                        c.execute(comando, (flag,))
                    while c.nextset():
                        pass
            for comando in (
                'CALL sp_plano_atual(NULL,0)',
                'CALL sp_plano_itens(0)',
                'CALL sp_plano_item_proprio(1,0)',
                'CALL sp_eliminar_planos_proprios(0)',
                "CALL sp_plano_por_chave(1,'invalida')"
            ):
                with self.assertRaises(pymysql.MySQLError):
                    c.execute(comando)
                while c.nextset():
                    pass
            c.execute('CALL sp_eliminar_planos_proprios(2147483649)')
            self.assertEqual(c.fetchone(), {'planos_eliminados': 0, 'itens_eliminados': 0})
            while c.nextset():
                pass
            c.execute('SELECT 7 AS ok')
            self.assertEqual(c.fetchone()['ok'], 7)
            c.execute('SELECT ROUTINE_NAME,SQL_DATA_ACCESS,SECURITY_TYPE FROM information_schema.ROUTINES '
                'WHERE ROUTINE_SCHEMA=DATABASE()')
            novas = [r for r in c.fetchall() if r['ROUTINE_NAME'] in sql_resources.PROCEDURES_015]
            self.assertEqual(len(novas), 6)
            for r in novas:
                self.assertEqual(r['SECURITY_TYPE'], 'INVOKER')
                self.assertEqual(
                    r['SQL_DATA_ACCESS'],
                    'MODIFIES SQL DATA' if
                    r['ROUTINE_NAME']=='sp_eliminar_planos_proprios' else 'READS SQL DATA'
                )
