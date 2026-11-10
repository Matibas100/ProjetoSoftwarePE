"""Instalação, baseline e contratos oficiais de 013 no MySQL descartável."""
import re
import pymysql

from database import migrate, sql_resources
from tests.migration_integration_support import MySQLMigrationTestCase
from tests import test_schema_portavel_integration as fixture


class CatalogoMigrationsIntegrationTest(MySQLMigrationTestCase):
    second_schema = fixture.SchemaPortavelIntegrationTest.second_schema
    restore = fixture.SchemaPortavelIntegrationTest.restore
    seed = fixture.SchemaPortavelIntegrationTest.seed
    rows = fixture.SchemaPortavelIntegrationTest.rows

    def setUp(self):
        super().setUp()
        self.migrations = self.migrations[: 14]

    def test_upgrade_012_013_dados_baseline_restauracao_e_idempotencia(self):
        self.apply_without_history('012')
        self.seed()
        antes = self.rows(self.connection)
        self.assertEqual(
            migrate.run_baseline(
                self.connection,
                self.settings,
                self.migrations,
                True
            ),
            '012'
        )
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 1)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), '013')
        self.assertEqual(self.rows(self.connection), antes)
        with self.second_schema() as (restaurada, settings):
            self.restore(restaurada)
            self.assertEqual(migrate.detect_legacy_prefix(restaurada), '013')
            self.assertEqual(
                migrate.run_baseline(
                    restaurada,
                    settings,
                    self.migrations,
                    True
                ),
                '013'
            )
            self.assertEqual(migrate.run_up(restaurada, settings, self.migrations), 0)
            self.assertEqual(self.rows(restaurada), antes)
            self.assertEqual(
                [r['version'] for r in migrate.fetch_history(restaurada)],
                [m.version for m in self.migrations]
            )

    def test_recurso_013_parcial_corpo_assinatura_seguranca_e_dependencia_012(self):
        for tipo in ['ausente', 'corpo', 'assinatura', 'seguranca', 'dependencia']:
            with self.subTest(tipo=tipo):
                self.recreate_schema()
                self.apply_without_history('013')
                nome = 'sp_bloquear_assunto' if tipo != 'dependencia' else 'sp_desempenho_resumo'
                with self.connection.cursor() as c:
                    c.execute('SHOW CREATE PROCEDURE '+nome)
                    ddl = c.fetchone()['Create Procedure']
                    c.execute('DROP PROCEDURE '+nome)
                    if tipo != 'ausente':
                        if tipo == 'assinatura':
                            ddl = re.sub('BIGINT UNSIGNED', 'INT', ddl, count=1, flags=re.I)
                        elif tipo == 'seguranca':
                            ddl = ddl.replace('SQL SECURITY INVOKER', 'SQL SECURITY DEFINER')
                        elif tipo == 'corpo':
                            ddl = ddl.replace('FOR UPDATE', 'FOR SHARE')
                        else:
                            ddl = ddl.replace('COUNT(*)', 'COUNT(DISTINCT id)', 1)
                        c.execute(ddl)
                with self.assertRaises(migrate.MigrationError):
                    migrate.run_baseline(self.connection, self.settings, self.migrations, True)
                self.assertEqual(migrate.fetch_history(self.connection), [])

    def test_json_vazio_repetido_invalidos_assinaturas_e_conexao(self):
        migrate.run_up(self.connection, self.settings, self.migrations)
        with self.connection.cursor() as c:
            c.execute("INSERT INTO materias(nome,area_enem_id) VALUES('Lote sintético',4)")
            id_ = c.lastrowid
            for nome in [
                'sp_bloquear_materias',
                'sp_questoes_versoes_elegiveis',
                'sp_questoes_versoes_historicas'
            ]:
                c.execute(f'CALL {nome}(%s)', ('[]',))
                self.assertFalse(c.fetchall())
                while c.nextset():
                    pass
                for valor in [None, '{}', '[null]', '[0]', '["texto"]']:
                    with self.assertRaises(pymysql.MySQLError):
                        c.execute(f'CALL {nome}(%s)', (valor,))
                    while c.nextset():
                        pass
            c.execute('CALL sp_bloquear_materias(%s)', (f'[{id_},{id_},2147483649]',))
            self.assertEqual([r['id'] for r in c.fetchall()], [id_])
            while c.nextset():
                pass
            c.execute('SELECT 7 AS ok')
            self.assertEqual(c.fetchone()['ok'], 7)
            c.execute("SELECT ROUTINE_NAME,SQL_DATA_ACCESS,SECURITY_TYPE FROM information_schema.ROUTINES "
                'WHERE ROUTINE_SCHEMA=DATABASE()')
            novas = [r for r in c.fetchall() if r['ROUTINE_NAME'] in sql_resources.PROCEDURES_013]
            self.assertEqual(len(novas), 15)
            self.assertTrue(all(r['SECURITY_TYPE']=='INVOKER' and r['SQL_DATA_ACCESS']=='READS SQL DATA' for r in novas))
