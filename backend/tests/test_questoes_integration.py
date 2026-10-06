import unittest
from uuid import uuid4

from app.models.questao import Questao
from tests.integration_support import MySQLIntegrationTestCase


class QuestoesApiIntegrationTest(MySQLIntegrationTestCase):
    """Exercita as duas funcionalidades de Questao no MySQL real."""

    def _nome_unico(self, recurso):
        return f"{recurso} teste {uuid4().hex[:12]}"

    def _cadastrar_materia(self):
        resposta = self.client.post(
            "/api/materias",
            json={"nome": self._nome_unico("Materia"), "area_enem_id": 4},
        )
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        materia = resposta.get_json()
        self.addCleanup(self.client.delete, f"/api/materias/{materia['id']}")
        return materia

    def _cadastrar_assunto(self):
        materia = self._cadastrar_materia()
        resposta = self.client.post(
            "/api/assuntos",
            json={
                "nome": self._nome_unico("Assunto"),
                "materia_id": materia["id"],
            },
        )
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        assunto = resposta.get_json()
        self.addCleanup(self.client.delete, f"/api/assuntos/{assunto['id']}")
        return assunto

    def _dados_questao(self, assunto_id):
        identificador = uuid4().hex[:12]
        return {
            "enunciado": f"Enunciado temporario {identificador}",
            "alternativa_a": "Alternativa A",
            "alternativa_b": "Alternativa B",
            "alternativa_c": "Alternativa C",
            "alternativa_d": "Alternativa D",
            "alternativa_e": "Alternativa E",
            "resposta_correta": "C",
            "explicacao": "Explicacao temporaria",
            "dificuldade": "media",
            "assunto_id": assunto_id,
        }

    def _cadastrar_questao(self, assunto_id):
        resposta = self.client.post(
            "/api/questoes",
            json=self._dados_questao(assunto_id),
        )
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        questao = resposta.get_json()
        self.addCleanup(self._deletar_questao_diretamente, questao["id"])
        return questao

    def _deletar_questao_diretamente(self, questao_id):
        with self.app.app_context():
            questao = Questao.buscar_por_id(questao_id)
            if questao is not None:
                questao.deletar()

    def test_post_questao_valida(self):
        assunto = self._cadastrar_assunto()
        questao = self._cadastrar_questao(assunto["id"])
        self.assertIsInstance(questao["id"], int)
        self.assertEqual(questao["assunto_id"], assunto["id"])

    def test_post_sem_enunciado(self):
        assunto = self._cadastrar_assunto()
        dados = self._dados_questao(assunto["id"])
        dados.pop("enunciado")
        resposta = self.client.post("/api/questoes", json=dados)
        self.assertEqual(resposta.status_code, 400, resposta.get_json())

    def test_post_sem_alternativa_obrigatoria(self):
        assunto = self._cadastrar_assunto()
        dados = self._dados_questao(assunto["id"])
        dados.pop("alternativa_e")
        resposta = self.client.post("/api/questoes", json=dados)
        self.assertEqual(resposta.status_code, 400, resposta.get_json())

    def test_post_resposta_correta_invalida(self):
        assunto = self._cadastrar_assunto()
        dados = self._dados_questao(assunto["id"])
        dados["resposta_correta"] = "F"
        resposta = self.client.post("/api/questoes", json=dados)
        self.assertEqual(resposta.status_code, 400, resposta.get_json())

    def test_post_assunto_inexistente(self):
        resposta = self.client.post(
            "/api/questoes",
            json=self._dados_questao(2147483647),
        )
        self.assertEqual(resposta.status_code, 404, resposta.get_json())

    def test_persistencia_real_da_questao(self):
        assunto = self._cadastrar_assunto()
        questao = self._cadastrar_questao(assunto["id"])

        with self.app.app_context():
            questao_persistida = Questao.buscar_por_id(questao["id"])
            self.assertIsNotNone(questao_persistida)
            self.assertEqual(questao_persistida.enunciado, questao["enunciado"])

    def test_busca_sem_assunto_id(self):
        resposta = self.client.get("/api/questoes/por-assunto")
        self.assertEqual(resposta.status_code, 400, resposta.get_json())

    def test_busca_com_assunto_id_invalido(self):
        resposta = self.client.get("/api/questoes/por-assunto?assunto_id=invalido")
        self.assertEqual(resposta.status_code, 400, resposta.get_json())

    def test_busca_assunto_inexistente(self):
        resposta = self.client.get(
            "/api/questoes/por-assunto?assunto_id=2147483647"
        )
        self.assertEqual(resposta.status_code, 404, resposta.get_json())

    def test_busca_assunto_sem_questoes(self):
        assunto = self._cadastrar_assunto()
        resposta = self.client.get(
            f"/api/questoes/por-assunto?assunto_id={assunto['id']}"
        )
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        self.assertEqual(resposta.get_json(), [])

    def test_busca_assunto_com_questao(self):
        assunto = self._cadastrar_assunto()
        questao = self._cadastrar_questao(assunto["id"])
        resposta = self.client.get(
            f"/api/questoes/por-assunto?assunto_id={assunto['id']}"
        )
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        ids = [item["id"] for item in resposta.get_json()]
        self.assertIn(questao["id"], ids)

    def test_busca_ordena_questoes_por_id(self):
        assunto = self._cadastrar_assunto()
        primeira = self._cadastrar_questao(assunto["id"])
        segunda = self._cadastrar_questao(assunto["id"])

        resposta = self.client.get(
            f"/api/questoes/por-assunto?assunto_id={assunto['id']}"
        )
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        self.assertEqual(
            [item["id"] for item in resposta.get_json()],
            [primeira["id"], segunda["id"]],
        )

    def test_busca_nao_retorna_questao_de_outro_assunto(self):
        assunto_consultado = self._cadastrar_assunto()
        outro_assunto = self._cadastrar_assunto()
        questao_consultada = self._cadastrar_questao(assunto_consultado["id"])
        outra_questao = self._cadastrar_questao(outro_assunto["id"])

        resposta = self.client.get(
            f"/api/questoes/por-assunto?assunto_id={assunto_consultado['id']}"
        )
        self.assertEqual(resposta.status_code, 200, resposta.get_json())
        ids = [item["id"] for item in resposta.get_json()]
        self.assertIn(questao_consultada["id"], ids)
        self.assertNotIn(outra_questao["id"], ids)


if __name__ == "__main__":
    unittest.main()
