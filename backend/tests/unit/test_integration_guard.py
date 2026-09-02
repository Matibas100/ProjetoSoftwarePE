import os
import unittest
from unittest.mock import patch

from tests.integration_support import MySQLIntegrationTestCase


class IntegrationGuardTest(unittest.TestCase):
    def test_bloqueia_antes_de_criar_app_sem_opt_in(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("tests.integration_support.create_app") as create_app,
            self.assertRaisesRegex(RuntimeError, "RUN_MYSQL_INTEGRATION=1"),
        ):
            MySQLIntegrationTestCase.setUpClass()
        create_app.assert_not_called()


if __name__ == "__main__":
    unittest.main()
