import unittest
from uuid import uuid4

from app import create_app


class MateriasApiIntegrationTest(unittest.TestCase):
    """Exercita a API contra o MySQL configurado, sem mocks ou SQLite."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)
        cls.app.logger.disabled = True
        cls.client = cls.app.test_client()

    def _nome_unico(self):
        return f"Materia teste {uuid4().hex[:12]}"

    def _cadastrar_materia(self):
        resposta = self.client.post(
            "/api/materias",
            json={"nome": self._nome_unico(), "descricao": "Teste de integracao"},
        )
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        materia = resposta.get_json()
        self.addCleanup(self.client.delete, f"/api/materias/{materia['id']}")
        return materia

    def test_post_valido(self):
        materia = self._cadastrar_materia()
        self.assertIsInstance(materia["id"], int)
        resposta_lista = self.client.get("/api/materias")
        self.assertEqual(resposta_lista.status_code, 200, resposta_lista.get_json())
        ids = [item["id"] for item in resposta_lista.get_json()]
        self.assertIn(materia["id"], ids)

    def test_post_sem_nome(self):
        resposta = self.client.post("/api/materias", json={"descricao": "Sem nome"})
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.get_json())

    def test_get_lista(self):
        materia = self._cadastrar_materia()
        resposta = self.client.get("/api/materias")
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        ids = [item["id"] for item in resposta.get_json()]
        self.assertIn(materia["id"], ids)

    def test_put_existente(self):
        materia = self._cadastrar_materia()
        novo_nome = self._nome_unico()
        resposta = self.client.put(
            f"/api/materias/{materia['id']}",
            json={"nome": novo_nome, "descricao": "Atualizada"},
        )
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        self.assertEqual(resposta.get_json()["nome"], novo_nome)

        resposta_lista = self.client.get("/api/materias")
        self.assertEqual(resposta_lista.status_code, 200, resposta_lista.get_json())
        materia_persistida = next(
            item
            for item in resposta_lista.get_json()
            if item["id"] == materia["id"]
        )
        self.assertEqual(materia_persistida["nome"], novo_nome)
        self.assertEqual(materia_persistida["descricao"], "Atualizada")

    def test_put_inexistente(self):
        resposta = self.client.put(
            "/api/materias/2147483647",
            json={"nome": self._nome_unico()},
        )
        self.assertEqual(resposta.status_code, 404, resposta.get_json())

    def test_delete_existente(self):
        materia = self._cadastrar_materia()
        resposta = self.client.delete(f"/api/materias/{materia['id']}")
        self.assertEqual(resposta.status_code, 204)
        self.assertEqual(resposta.data, b"")

        resposta_lista = self.client.get("/api/materias")
        self.assertEqual(resposta_lista.status_code, 200, resposta_lista.get_json())
        ids = [item["id"] for item in resposta_lista.get_json()]
        self.assertNotIn(materia["id"], ids)

    def test_delete_inexistente(self):
        resposta = self.client.delete("/api/materias/2147483647")
        self.assertEqual(resposta.status_code, 404, resposta.get_json())


if __name__ == "__main__":
    unittest.main()
