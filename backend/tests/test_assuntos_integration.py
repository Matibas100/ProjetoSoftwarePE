import unittest
from uuid import uuid4

from app.models.questao import Questao
from tests.integration_support import MySQLIntegrationTestCase


class AssuntosApiIntegrationTest(MySQLIntegrationTestCase):
    """Exercita Assunto contra o MySQL real, sem mocks ou SQLite."""

    def _nome_unico(self, recurso):
        return f"{recurso} teste {uuid4().hex[:12]}"

    def _cadastrar_materia(self):
        resposta = self.client.post(
            "/api/materias",
            json={
                "nome": self._nome_unico("Materia"),
                "descricao": "Dado temporario do teste de Assunto",
                "area_enem_id": 4,
            },
        )
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        materia = resposta.get_json()
        self.addCleanup(self.client.delete, f"/api/materias/{materia['id']}")
        return materia

    def _cadastrar_assunto(self, materia_id=None):
        if materia_id is None:
            materia_id = self._cadastrar_materia()["id"]

        resposta = self.client.post(
            "/api/assuntos",
            json={
                "nome": self._nome_unico("Assunto"),
                "descricao": "Teste de integracao",
                "materia_id": materia_id,
            },
        )
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        assunto = resposta.get_json()
        self.addCleanup(self.client.delete, f"/api/assuntos/{assunto['id']}")
        return assunto

    def _cadastrar_questao_diretamente(self, assunto_id):
        with self.app.app_context():
            questao = Questao(
                enunciado="Questao temporaria para validar integridade",
                alternativa_a="A",
                alternativa_b="B",
                alternativa_c="C",
                alternativa_d="D",
                alternativa_e="E",
                resposta_correta="A",
                explicacao="Registro removido ao final do teste",
                dificuldade="facil",
                assunto_id=assunto_id,
            )
            questao.salvar()
            questao_id = questao.id

        self.addCleanup(self._deletar_questao_diretamente, questao_id)

    def _deletar_questao_diretamente(self, questao_id):
        with self.app.app_context():
            questao = Questao.buscar_por_id(questao_id)
            if questao is not None:
                questao.deletar()

    def test_post_valido(self):
        assunto = self._cadastrar_assunto()
        resposta_lista = self.client.get("/api/assuntos")
        self.assertEqual(resposta_lista.status_code, 200, resposta_lista.get_json())
        ids = [item["id"] for item in resposta_lista.get_json()]
        self.assertIn(assunto["id"], ids)

    def test_post_sem_nome(self):
        materia = self._cadastrar_materia()
        resposta = self.client.post(
            "/api/assuntos",
            json={"descricao": "Sem nome", "materia_id": materia["id"]},
        )
        self.assertEqual(resposta.status_code, 400, resposta.get_json())

    def test_post_com_materia_inexistente(self):
        resposta = self.client.post(
            "/api/assuntos",
            json={"nome": self._nome_unico("Assunto"), "materia_id": 2147483647},
        )
        self.assertEqual(resposta.status_code, 404, resposta.get_json())

    def test_get_lista(self):
        assunto = self._cadastrar_assunto()
        resposta = self.client.get("/api/assuntos")
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        ids = [item["id"] for item in resposta.get_json()]
        self.assertIn(assunto["id"], ids)

    def test_put_existente(self):
        materia_original = self._cadastrar_materia()
        nova_materia = self._cadastrar_materia()
        assunto = self._cadastrar_assunto(materia_original["id"])
        novo_nome = self._nome_unico("Assunto atualizado")

        resposta = self.client.put(
            f"/api/assuntos/{assunto['id']}",
            json={
                "nome": novo_nome,
                "descricao": "Descricao atualizada",
                "materia_id": nova_materia["id"],
            },
        )
        self.assertEqual(resposta.status_code, 200, resposta.get_json())

        resposta_lista = self.client.get("/api/assuntos")
        assunto_persistido = next(
            item
            for item in resposta_lista.get_json()
            if item["id"] == assunto["id"]
        )
        self.assertEqual(assunto_persistido["nome"], novo_nome)
        self.assertEqual(assunto_persistido["descricao"], "Descricao atualizada")
        self.assertEqual(assunto_persistido["materia_id"], nova_materia["id"])

    def test_put_com_materia_inexistente(self):
        assunto = self._cadastrar_assunto()
        resposta = self.client.put(
            f"/api/assuntos/{assunto['id']}",
            json={"materia_id": 2147483647},
        )
        self.assertEqual(resposta.status_code, 404, resposta.get_json())

    def test_put_assunto_inexistente(self):
        materia = self._cadastrar_materia()
        resposta = self.client.put(
            "/api/assuntos/2147483647",
            json={"nome": self._nome_unico("Assunto"), "materia_id": materia["id"]},
        )
        self.assertEqual(resposta.status_code, 404, resposta.get_json())

    def test_delete_existente(self):
        assunto = self._cadastrar_assunto()
        resposta = self.client.delete(f"/api/assuntos/{assunto['id']}")
        self.assertEqual(resposta.status_code, 204)
        self.assertEqual(resposta.data, b"")

        resposta_lista = self.client.get("/api/assuntos")
        ids = [item["id"] for item in resposta_lista.get_json()]
        self.assertNotIn(assunto["id"], ids)

    def test_delete_inexistente(self):
        resposta = self.client.delete("/api/assuntos/2147483647")
        self.assertEqual(resposta.status_code, 404, resposta.get_json())

    def test_delete_com_questao_vinculada(self):
        assunto = self._cadastrar_assunto()
        self._cadastrar_questao_diretamente(assunto["id"])

        resposta = self.client.delete(f"/api/assuntos/{assunto['id']}")
        self.assertEqual(resposta.status_code, 409, resposta.get_json())
        self.assertIn("possui vinculos", resposta.get_json()["erro"])


if __name__ == "__main__":
    unittest.main()
