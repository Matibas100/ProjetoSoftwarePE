import unittest
from unittest.mock import patch

from app import create_app


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://unit:unit@127.0.0.1:9/unit"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = []


class ControllerDelegationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = create_app(TestConfig).test_client()
        cls.guard = patch("app.auth_http.AutorizarService.executar", return_value=None)
        cls.guard.start()
        cls.addClassCleanup(cls.guard.stop)

    @patch("app.controllers.materia_controller.CriarMateriaService.executar", return_value={"id": 1})
    def test_cadastrar_materia(self, execute):
        response = self.client.post("/api/materias", json={"nome": "x"})
        self.assertEqual(response.status_code, 201)
        execute.assert_called_once_with({"nome": "x"})

    @patch("app.controllers.materia_controller.ListarMateriasService.executar", return_value=[])
    def test_listar_materias(self, execute):
        self.assertEqual(self.client.get("/api/materias").get_json(), [])
        execute.assert_called_once_with(False)

    @patch("app.controllers.materia_controller.AtualizarMateriaService.executar", return_value={"id": 2})
    def test_atualizar_materia(self, execute):
        self.client.put("/api/materias/2", json={"nome": "y"})
        execute.assert_called_once_with(2, {"nome": "y"})

    @patch("app.controllers.materia_controller.DeletarMateriaService.executar")
    def test_deletar_materia(self, execute):
        self.assertEqual(self.client.delete("/api/materias/2").status_code, 204)
        execute.assert_called_once_with(2)

    @patch("app.controllers.assunto_controller.CriarAssuntoService.executar", return_value={"id": 1})
    def test_cadastrar_assunto(self, execute):
        self.client.post("/api/assuntos", json={"nome": "x"})
        execute.assert_called_once_with({"nome": "x"})

    @patch("app.controllers.assunto_controller.ListarAssuntosService.executar", return_value=[])
    def test_listar_assuntos(self, execute):
        self.client.get("/api/assuntos")
        execute.assert_called_once_with(False, None)

    @patch("app.controllers.assunto_controller.AtualizarAssuntoService.executar", return_value={"id": 2})
    def test_atualizar_assunto(self, execute):
        self.client.put("/api/assuntos/2", json={"nome": "y"})
        execute.assert_called_once_with(2, {"nome": "y"})

    @patch("app.controllers.assunto_controller.DeletarAssuntoService.executar")
    def test_deletar_assunto(self, execute):
        self.client.delete("/api/assuntos/2")
        execute.assert_called_once_with(2)

    @patch("app.controllers.questao_controller.CriarQuestaoService.executar", return_value={"id": 1})
    def test_cadastrar_questao(self, execute):
        self.client.post("/api/questoes", json={"enunciado": "x"})
        execute.assert_called_once_with({"enunciado": "x"})

    @patch("app.controllers.questao_controller.BuscarQuestoesPorAssuntoService.executar", return_value=[])
    def test_buscar_questoes(self, execute):
        self.client.get("/api/questoes/por-assunto?assunto_id=3")
        execute.assert_called_once_with("3")


if __name__ == "__main__":
    unittest.main()
