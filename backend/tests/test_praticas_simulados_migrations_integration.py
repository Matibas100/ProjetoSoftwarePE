"""Instalação e reconhecimento conservador de 014 no MySQL descartável."""
import re
import pymysql

from database import migrate, sql_resources
from tests.migration_integration_support import MySQLMigrationTestCase
from tests import test_schema_portavel_integration as fixture


class PraticasSimuladosMigrationsIntegrationTest(MySQLMigrationTestCase):
    second_schema = fixture.SchemaPortavelIntegrationTest.second_schema
    restore = fixture.SchemaPortavelIntegrationTest.restore
    seed = fixture.SchemaPortavelIntegrationTest.seed
    rows = fixture.SchemaPortavelIntegrationTest.rows

    def setUp(self):
        super().setUp()
        self.migrations = self.migrations[:15]

    def test_upgrade_bloqueia_drift_fisico_013_antes_de_qualquer_ddl_014(self):
        for tipo in ['ausente', 'corpo', 'assinatura', 'seguranca', 'legada', 'tabela', 'parcial014', 'completo014']:
            with self.subTest(tipo=tipo):
                self.recreate_schema()
                migrate.run_up(self.connection, self.settings, self.migrations[:14])
                self.seed()
                with self.connection.cursor() as c:
                    if tipo == 'tabela':
                        c.execute('ALTER TABLE simulados ADD COLUMN divergente INT NULL')
                    elif tipo in {'parcial014', 'completo014'}:
                        comandos = migrate.validate_statements(migrate.split_sql(self.migrations[14].sql))
                        migrate.execute_statements(self.connection, comandos[:1] if tipo == 'parcial014' else comandos)
                    else:
                        nome = 'sp_questoes_por_assunto' if tipo == 'legada' else 'sp_bloquear_assunto'
                        c.execute('SHOW CREATE PROCEDURE '+nome)
                        ddl = c.fetchone()['Create Procedure']
                        c.execute('DROP PROCEDURE '+nome)
                        if tipo != 'ausente':
                            if tipo == 'assinatura':
                                ddl = re.sub('BIGINT UNSIGNED', 'INT', ddl, count=1, flags=re.I)
                            elif tipo == 'seguranca':
                                ddl = ddl.replace('SQL SECURITY INVOKER', 'SQL SECURITY DEFINER')
                            elif tipo == 'legada':
                                ddl = 'CREATE PROCEDURE sp_questoes_por_assunto(IN p_assunto_id INT) SELECT 1'
                            else:
                                ddl = ddl.replace('FOR UPDATE', 'FOR SHARE')
                            c.execute(ddl)
                dados = self.rows(self.connection)
                historico = migrate.fetch_history(self.connection)
                recursos = sql_resources.inventariar(self.connection)
                with self.assertRaises(migrate.MigrationError):
                    migrate.run_up(self.connection, self.settings, self.migrations)
                self.assertEqual(migrate.fetch_history(self.connection), historico)
                self.assertEqual(self.rows(self.connection), dados)
                self.assertEqual(sql_resources.inventariar(self.connection), recursos)
                with self.connection.cursor() as c:
                    c.execute('SELECT IS_USED_LOCK(%s) AS dono', (migrate._lock_name(self.settings.name),))
                    self.assertIsNone(c.fetchone()['dono'])

    def test_reparar_dependencia_permite_upgrade_sem_reconciliacao_ficticia(self):
        migrate.run_up(self.connection, self.settings, self.migrations[:14])
        with self.connection.cursor() as c:
            c.execute('SHOW CREATE PROCEDURE sp_bloquear_assunto')
            ddl = c.fetchone()['Create Procedure']
            c.execute('DROP PROCEDURE sp_bloquear_assunto')
        historico = migrate.fetch_history(self.connection)
        with self.assertRaises(migrate.MigrationError):
            migrate.run_up(self.connection, self.settings, self.migrations)
        self.assertEqual(migrate.fetch_history(self.connection), historico)
        with self.connection.cursor() as c:
            c.execute(ddl)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 1)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), '014')

    def test_upgrade_013_014_dados_baseline_restauracao_idempotencia(self):
        self.apply_without_history('013')
        self.seed()
        antes = self.rows(self.connection)
        self.assertEqual(migrate.run_baseline(self.connection, self.settings, self.migrations, True), '013')
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 1)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), '014')
        self.assertEqual(self.rows(self.connection), antes)
        with self.second_schema() as (restaurada, settings):
            self.restore(restaurada)
            self.assertEqual(migrate.run_baseline(restaurada, settings, self.migrations, True), '014')
            self.assertEqual(migrate.run_up(restaurada, settings, self.migrations), 0)
            self.assertEqual(self.rows(restaurada), antes)

    def test_parcial_corpo_assinatura_seguranca_e_dependencia_013(self):
        for tipo in ['ausente', 'corpo', 'assinatura', 'seguranca', 'dependencia']:
            with self.subTest(tipo=tipo):
                self.recreate_schema()
                self.apply_without_history('014')
                nome = 'sp_simulado_respostas' if tipo != 'dependencia' else 'sp_bloquear_assunto'
                with self.connection.cursor() as c:
                    c.execute('SHOW CREATE PROCEDURE '+nome)
                    ddl = c.fetchone()['Create Procedure']
                    c.execute('DROP PROCEDURE '+nome)
                    if tipo != 'ausente':
                        if tipo == 'assinatura':
                            ddl = re.sub('BIGINT UNSIGNED', 'INT', ddl, count=1, flags=re.I)
                        elif tipo == 'seguranca':
                            ddl = ddl.replace('SQL SECURITY INVOKER', 'SQL SECURITY DEFINER')
                        else:
                            ddl = ddl.replace('FOR UPDATE', 'FOR SHARE')
                        c.execute(ddl)
                with self.assertRaises(migrate.MigrationError):
                    migrate.run_baseline(self.connection, self.settings, self.migrations, True)
                self.assertEqual(migrate.fetch_history(self.connection), [])

    def test_lotes_formatos_vazios_flags_e_seguranca(self):
        migrate.run_up(self.connection, self.settings, self.migrations)
        with self.connection.cursor() as c:
            for sql, validos in [
                ('CALL sp_simulados_itens_lote(%s,NULL)', ('[]',)),
                ('CALL sp_simulados_itens_lote(NULL,%s)', ('[]',)),
                ('CALL sp_simulados_andamentos_lote(1,%s)', ('[]',)),
                ('CALL sp_simulados_titulos_lote(%s)', ('[]',)),
            ]:
                c.execute(sql, validos)
                self.assertEqual(c.fetchall(), ())
                while c.nextset():
                    pass
                for invalido in ['{}', '[null]', '[0]', '["texto"]']:
                    with self.assertRaises(pymysql.MySQLError):
                        c.execute(sql, (invalido,))
                    while c.nextset():
                        pass
            for sql in ['CALL sp_pratica_propria(1,1,%s)',
                        "CALL sp_pratica_por_chave(1,'00000000-0000-0000-0000-000000000000',%s)",
                        'CALL sp_simulado_tentativa_propria(1,1,%s)', 'CALL sp_simulado_respostas(1,%s)']:
                for flag in [None, -1, 2]:
                    with self.assertRaises(pymysql.MySQLError):
                        c.execute(sql, (flag,))
                    while c.nextset():
                        pass
            c.execute('SELECT 7 AS ok')
            self.assertEqual(c.fetchone()['ok'], 7)
            c.execute('SELECT ROUTINE_NAME,SQL_DATA_ACCESS,SECURITY_TYPE FROM information_schema.ROUTINES '
                'WHERE ROUTINE_SCHEMA=DATABASE()')
            novas = [r for r in c.fetchall() if r['ROUTINE_NAME'] in sql_resources.PROCEDURES_014]
            self.assertEqual(len(novas), 16)
            self.assertTrue(all(r['SQL_DATA_ACCESS']=='READS SQL DATA' and r['SECURITY_TYPE']=='INVOKER' for r in novas))
