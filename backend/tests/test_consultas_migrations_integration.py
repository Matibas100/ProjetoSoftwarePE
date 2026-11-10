"""Instalação e contratos SQL em schemas MySQL descartáveis."""
from database import migrate
from tests.migration_integration_support import MySQLMigrationTestCase
from tests import test_schema_portavel_integration as fixture
from database import sql_resources
import pymysql
import re


class ConsultasMigrationsIntegrationTest(MySQLMigrationTestCase):
    second_schema = fixture.SchemaPortavelIntegrationTest.second_schema
    restore = fixture.SchemaPortavelIntegrationTest.restore
    seed = fixture.SchemaPortavelIntegrationTest.seed
    rows = fixture.SchemaPortavelIntegrationTest.rows

    def test_upgrade_010_011_012_dados_baseline_e_referencias_oficiais(self):
        for prefixo in ['011', '012']:
            with self.subTest(prefixo=prefixo):
                self.recreate_schema()
                self.apply_without_history('010')
                self.seed()
                antes = self.rows(self.connection)
                for item in self.migrations[11: int(prefixo)+1]:
                    migrate.execute_statements(
                        self.connection,
                        migrate.validate_statements(migrate.split_sql(item.sql))
                    )
                self.assertEqual(migrate.detect_legacy_prefix(self.connection), prefixo)
                self.assertEqual(self.rows(self.connection), antes)
                with self.second_schema() as (restaurada, settings):
                    self.restore(restaurada)
                    self.assertEqual(
                        migrate.run_baseline(
                            restaurada,
                            settings,
                            self.migrations,
                            confirmed=True
                        ),
                        prefixo
                    )
                    self.assertEqual(self.rows(restaurada), antes)
                    self.assertEqual(
                        migrate.run_up(
                            restaurada,
                            settings,
                            self.migrations[: 13]
                        ),
                        12-int(prefixo)
                    )
                    self.assertEqual(migrate.run_up(restaurada, settings, self.migrations[: 13]), 0)
                    self.assertEqual(migrate.detect_legacy_prefix(restaurada), '012')
                    self.assertEqual(self.rows(restaurada), antes)

    def test_recursos_ausentes_corpos_assinaturas_seguranca_e_schema_externo(self):
        for alteracao in [
            'ausente',
            'corpo',
            'assinatura',
            'seguranca',
            'view',
            'coluna',
            'externo'
        ]:
            with self.subTest(alteracao=alteracao):
                self.recreate_schema()
                self.apply_without_history('012')
                with self.connection.cursor() as c:
                    if alteracao in ['ausente', 'corpo', 'assinatura', 'seguranca']:
                        c.execute('SHOW CREATE PROCEDURE sp_materias_admin')
                        ddl = c.fetchone()['Create Procedure']
                        c.execute('DROP PROCEDURE sp_materias_admin')
                        if alteracao != 'ausente':
                            if alteracao == 'corpo':
                                ddl = ddl.replace('COUNT(DISTINCT s.id)', 'COUNT(s.id)')
                            elif alteracao == 'assinatura':
                                ddl = re.sub(
                                    r'varchar\(100\)',
                                    'varchar(99)',
                                    ddl,
                                    count=1,
                                    flags=re.IGNORECASE
                                )
                            else:
                                ddl = ddl.replace('SQL SECURITY INVOKER', 'SQL SECURITY DEFINER')
                            c.execute(ddl)
                    elif alteracao == 'view':
                        c.execute('DROP VIEW vw_simulados_atividades')
                    elif alteracao == 'coluna':
                        c.execute('ALTER SQL SECURITY INVOKER VIEW vw_simulados_atividades AS '
                            "SELECT 'simulado' AS tipo,id,usuario_id,finalizada_em AS ocorrido_em,"
                            "CAST('Outro título' AS CHAR(10)) AS titulo FROM simulado_tentativas WHERE estado='finalizada'")
                    else:
                        with self.second_schema() as (externa, settings):
                            migrate.run_up(externa, settings, self.migrations)
                            c.execute('ALTER SQL SECURITY INVOKER VIEW vw_conteudo_classificacao_historica AS '
                                'SELECT questao_versao_id,materia_id,materia_nome,assunto_id,assunto_nome '
                                f'FROM `{settings.name}`.vw_conteudo_classificacao_historica')
                            with self.assertRaises(migrate.MigrationError):
                                migrate.detect_legacy_prefix(self.connection)
                            continue
                with self.assertRaises(migrate.MigrationError):
                    migrate.run_baseline(
                        self.connection,
                        self.settings,
                        self.migrations,
                        confirmed=True
                    )
                self.assertEqual(migrate.fetch_history(self.connection), [])

    def test_metricas_sql_recusam_usuario_intervalo_e_preservam_vazios(self):
        migrate.run_up(self.connection, self.settings, self.migrations)
        with self.connection.cursor() as c:
            for nome in ['sp_desempenho_resumo', 'sp_atividades_recentes']:
                for parametros in [
                    (
                        None,
                        '2026-01-01',
                        '2026-01-02'
                    ),
                    (
                        0,
                        '2026-01-01',
                        '2026-01-02'
                    ),
                    (1, None, '2026-01-02'),
                    (1, '2026-01-02', '2026-01-01')
                ]:
                    with self.assertRaises(pymysql.MySQLError):
                        c.execute(f'CALL {nome}(%s,%s,%s)', parametros)
                    while c.nextset():
                        pass
            c.execute("CALL sp_desempenho_resumo(1,'2026-01-01','2026-01-02')")
            self.assertEqual(
                dict(c.fetchone()),
                {
                    'total_respostas': 0,
                    'acertos': 0,
                    'pratica': 0,
                    'simulado': 0
                }
            )
            self.assertTrue(c.nextset())
            self.assertFalse(c.fetchall())
            self.assertTrue(c.nextset())
            self.assertFalse(c.fetchall())
            while c.nextset():
                pass

    def test_011_instala_quatro_procedures_e_recusa_parametros_invalidos(self):
        migrate.run_up(self.connection, self.settings, self.migrations[: 12])
        with self.connection.cursor() as c:
            c.execute('SELECT COUNT(*) AS total FROM information_schema.ROUTINES '
                "WHERE ROUTINE_SCHEMA=DATABASE() AND ROUTINE_NAME <> 'sp_questoes_por_assunto' "
                "AND SECURITY_TYPE='INVOKER' AND SQL_DATA_ACCESS='READS SQL DATA'")
            self.assertEqual(c.fetchone()['total'], 4)
            for chamada in [
                'CALL sp_materias_admin(NULL,NULL,NULL,0,20)',
                'CALL sp_materias_admin(NULL,NULL,0,1,20)',
                "CALL sp_materias_admin(NULL,'erro',NULL,1,20)",
                'CALL sp_assuntos_admin(NULL,NULL,NULL,NULL,1,101)',
                "CALL sp_questoes_admin(NULL,NULL,'erro',NULL,NULL,NULL,1,20)",
            ]:
                with self.assertRaises(pymysql.MySQLError):
                    c.execute(chamada)
                while c.nextset():
                    pass
            c.execute('CALL sp_materias_admin(NULL,NULL,NULL,2147483649,20)')
            self.assertEqual(c.fetchall(), ())
            self.assertTrue(c.nextset())
            self.assertEqual(c.fetchone()['total'], 0)
            while c.nextset():
                pass
            c.execute('SELECT 1 AS ok')
            self.assertEqual(c.fetchone()['ok'], 1)
