import os
import runpy
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app import create_app
from app import config


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://unit:unit@127.0.0.1:9/unit"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ["http://frontend.test"]


class ConfigTest(unittest.TestCase):
    def test_as_bool(self):
        for value in ("1", "TRUE", " yes ", "on"):
            with self.subTest(value=value):
                self.assertTrue(config._as_bool(value))
        self.assertFalse(config._as_bool("false"))

    def test_database_uri_prefere_url_completa(self):
        with patch.dict(os.environ, {"DATABASE_URL": "mysql+pymysql://full"}, clear=True):
            self.assertEqual(config._database_uri(), "mysql+pymysql://full")

    def test_database_uri_monta_componentes_e_charset_padrao(self):
        environment = {
            "DB_HOST": "localhost",
            "DB_PORT": "3306",
            "DB_NAME": "enem",
            "DB_USER": "usuario@email",
            "DB_PASSWORD": "senha com espaco",
        }
        with patch.dict(os.environ, environment, clear=True):
            uri = config._database_uri()
        self.assertEqual(
            uri,
            "mysql+pymysql://usuario%40email:senha+com+espaco@localhost:3306/enem?charset=utf8mb4",
        )

    def test_database_uri_respeita_charset(self):
        environment = {
            "DB_HOST": "db",
            "DB_PORT": "3307",
            "DB_NAME": "enem",
            "DB_USER": "user",
            "DB_PASSWORD": "pass",
            "DB_CHARSET": "latin1",
        }
        with patch.dict(os.environ, environment, clear=True):
            self.assertTrue(config._database_uri().endswith("?charset=latin1"))

    def test_database_uri_informa_variaveis_ausentes_sem_valores(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "DB_HOST, DB_PORT") as error:
                config._database_uri()
        self.assertNotIn("unit:unit", str(error.exception))

    def test_cors_origins_padrao_e_customizado(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                config._cors_origins(),
                ["http://127.0.0.1:5500", "http://localhost:5500"],
            )
        with patch.dict(os.environ, {"CORS_ORIGINS": " a, ,b "}, clear=True):
            self.assertEqual(config._cors_origins(), ["a", "b"])


class ApplicationFactoryTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)

    def test_registra_as_rotas_api(self):
        rules = [rule for rule in self.app.url_map.iter_rules() if rule.rule.startswith("/api/")]
        self.assertEqual(len(rules), 24)
        self.assertTrue(
            {
                "/api/health",
                "/api/areas-enem",
                "/api/materias",
                "/api/materias/<int:materia_id>",
                "/api/admin/materias",
                "/api/materias/<int:materia_id>/impacto-exclusao",
                "/api/assuntos",
                "/api/assuntos/<int:assunto_id>",
                "/api/admin/assuntos",
                "/api/assuntos/<int:assunto_id>/impacto-transferencia",
                "/api/assuntos/<int:assunto_id>/transferir",
                "/api/questoes",
                "/api/questoes/por-assunto",
            }.issubset({rule.rule for rule in rules})
        )

    def test_health_e_cors(self):
        response = self.app.test_client().get(
            "/api/health", headers={"Origin": "http://frontend.test"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"aplicacao": "Plataforma ENEM", "status": "online"},
        )
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"], "http://frontend.test"
        )

    def test_run_py_configura_host_port_e_debug(self):
        fake_app = MagicMock()
        fake_app.config = {"DEBUG": True}
        run_file = Path(__file__).resolve().parents[2] / "run.py"
        with (
            patch("app.create_app", return_value=fake_app),
            patch.dict(os.environ, {"APP_HOST": "0.0.0.0", "APP_PORT": "5050"}),
        ):
            namespace = runpy.run_path(str(run_file), run_name="__main__")
        self.assertIs(namespace["app"], fake_app)
        fake_app.run.assert_called_once_with(host="0.0.0.0", port=5050, debug=True)


if __name__ == "__main__":
    unittest.main()
