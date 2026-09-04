import os
import unittest
from unittest.mock import patch

from tests.integration_support import MySQLIntegrationTestCase
from tests.migration_integration_support import validate_migration_test_schema


class IntegrationGuardTest(unittest.TestCase):
    def test_bloqueia_antes_de_criar_app_sem_opt_in(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("tests.integration_support.create_app") as create_app,
            self.assertRaisesRegex(RuntimeError, "RUN_MYSQL_INTEGRATION=1"),
        ):
            MySQLIntegrationTestCase.setUpClass()
        create_app.assert_not_called()

    def test_schema_descartavel_exige_nome_seguro(self):
        valid = "plataforma_enem_migration_test_abcdef123456"
        self.assertEqual(validate_migration_test_schema(valid), valid)
        for invalid in (
            "plataforma_enem",
            "plataforma_enem_migration_test_",
            "plataforma_enem_migration_test_abcdef123456;DROP",
        ):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                RuntimeError, "recusado"
            ):
                validate_migration_test_schema(invalid)


if __name__ == "__main__":
    unittest.main()
