"""Restauração de DDL literal com percentuais no MySQL descartável."""

from sqlalchemy.exc import DBAPIError

from app.extensions import db
from tests.integration_support import MySQLIntegrationTestCase


class RestauracaoProceduresIntegrationTest(MySQLIntegrationTestCase):
    autenticar_administrador = False

    def test_restauracao_preserva_percentual_e_marcador_literal(self):
        nome = 'sp_teste_restauracao_literal'
        with self.app.app_context(), db.engine.begin() as ddl:
            try:
                ddl.exec_driver_sql(
                    f"CREATE PROCEDURE {nome}() "
                    "SELECT '100% ENEM' AS percentual, '%s' AS marcador",
                    execution_options={"no_parameters": True},
                )
                original = ddl.exec_driver_sql(
                    'SHOW CREATE PROCEDURE ' + nome
                ).mappings().one()['Create Procedure']
                self.assertIn('100% ENEM', original)
                self.assertIn('%s', original)
                ddl.exec_driver_sql('DROP PROCEDURE ' + nome)
                ddl.exec_driver_sql(original, execution_options={"no_parameters": True})
                restaurado = ddl.exec_driver_sql(
                    'SHOW CREATE PROCEDURE ' + nome
                ).mappings().one()['Create Procedure']
                self.assertEqual(restaurado, original)
                self.assertEqual(
                    tuple(ddl.exec_driver_sql('CALL ' + nome + '()').one()),
                    ('100% ENEM', '%s'),
                )
                with self.assertRaises(DBAPIError):
                    ddl.exec_driver_sql('CALL ' + nome + '(1)')
                self.assertEqual(
                    tuple(ddl.exec_driver_sql('CALL ' + nome + '()').one()),
                    ('100% ENEM', '%s'),
                )
                self.assertEqual(ddl.exec_driver_sql('SELECT 1').scalar_one(), 1)
            finally:
                ddl.exec_driver_sql('DROP PROCEDURE IF EXISTS ' + nome)
            self.assertEqual(ddl.exec_driver_sql(
                'SELECT COUNT(*) FROM information_schema.ROUTINES '
                'WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_NAME = %s',
                (nome,),
            ).scalar_one(), 0)
