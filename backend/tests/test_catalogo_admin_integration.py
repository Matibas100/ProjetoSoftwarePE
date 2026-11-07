from uuid import uuid4

from sqlalchemy import text

from app.extensions import db
from tests.integration_support import MySQLIntegrationTestCase


class CatalogoAdminIntegrationTest(MySQLIntegrationTestCase):
    def _matter(self, area=4, status="ativa"):
        response = self.client.post(
            "/api/materias",
            json={
                "nome": f"Materia catalogo {uuid4().hex[:10]}",
                "descricao": "Descricao pesquisavel",
                "area_enem_id": area,
                "status": status,
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()

    def _subject(self, matter_id, name=None):
        response = self.client.post(
            "/api/assuntos",
            json={
                "nome": name or f"Assunto catalogo {uuid4().hex[:10]}",
                "descricao": "Descricao do assunto",
                "materia_id": matter_id,
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()

    def _question(self, subject_id):
        response = self.client.post(
            "/api/questoes",
            json={
                "enunciado": "Enunciado de impacto",
                "alternativa_a": "A",
                "alternativa_b": "B",
                "alternativa_c": "C",
                "alternativa_d": "D",
                "alternativa_e": "E",
                "resposta_correta": "A",
                "dificuldade": "facil",
                "assunto_id": subject_id,
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()

    def test_areas_fixas_somente_leitura(self):
        response = self.client.get("/api/areas-enem")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [(item["codigo"], item["ordem"]) for item in response.get_json()],
            [
                ("linguagens", 1),
                ("ciencias-humanas", 2),
                ("ciencias-natureza", 3),
                ("matematica", 4),
            ],
        )
        self.assertEqual(self.client.post("/api/areas-enem", json={}).status_code, 405)

    def test_materia_exige_area_e_listagem_admin_combina_filtros(self):
        self.assertEqual(
            self.client.post("/api/materias", json={"nome": "Sem area"}).status_code, 400
        )
        self.assertEqual(
            self.client.post(
                "/api/materias", json={"nome": "Area ausente", "area_enem_id": 999}
            ).status_code,
            404,
        )
        matter = self._matter(area=3)
        subject = self._subject(matter["id"])
        self._question(subject["id"])
        response = self.client.get(
            "/api/admin/materias",
            query_string={"busca": "PESQUISAVEL", "area_enem_id": 3, "status": "ativa"},
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        item = next(item for item in response.get_json()["itens"] if item["id"] == matter["id"])
        self.assertEqual((item["assuntos"], item["questoes"]), (1, 1))
        self.assertEqual(item["area_enem"]["codigo"], "ciencias-natureza")
        self.assertEqual(self.client.get("/api/admin/materias?por_pagina=101").status_code, 400)

    def test_unicidade_normalizada_inclui_arquivados_e_permite_outra_materia(self):
        first = self._matter()
        second = self._matter()
        subject = self._subject(first["id"], "  Genética   Molecular  ")
        self.assertEqual(subject["nome_normalizado"], "genética molecular")
        duplicate = self.client.post(
            "/api/assuntos", json={"nome": "GENETICA MOLECULAR", "materia_id": first["id"]}
        )
        self.assertEqual(duplicate.status_code, 409, duplicate.get_json())
        self.assertEqual(
            self.client.post(
                f"/api/assuntos/{subject['id']}/arquivar"
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                "/api/assuntos", json={"nome": "genética molecular", "materia_id": first["id"]}
            ).status_code,
            409,
        )
        self.assertEqual(
            self.client.post(
                "/api/assuntos", json={"nome": "genetica molecular", "materia_id": second["id"]}
            ).status_code,
            201,
        )

    def test_ciclo_de_vida_preserva_questoes_e_bloqueia_dependencias(self):
        matter = self._matter()
        subject = self._subject(matter["id"])
        question = self._question(subject["id"])
        blocked = self.client.post(f"/api/materias/{matter['id']}/arquivar")
        self.assertEqual(blocked.status_code, 409, blocked.get_json())
        self.assertEqual(self.client.post(f"/api/assuntos/{subject['id']}/arquivar").status_code, 200)
        self.assertEqual(
            self.client.get(
                "/api/questoes/por-assunto", query_string={"assunto_id": subject["id"]}
            ).get_json()[0]["id"],
            question["id"],
        )
        self.assertEqual(self.client.post(f"/api/materias/{matter['id']}/arquivar").status_code, 200)
        self.assertEqual(self.client.post(f"/api/assuntos/{subject['id']}/reativar").status_code, 409)
        self.assertEqual(self.client.post(f"/api/materias/{matter['id']}/reativar").status_code, 200)
        self.assertEqual(self.client.post(f"/api/assuntos/{subject['id']}/reativar").status_code, 200)
        impact = self.client.get(f"/api/assuntos/{subject['id']}/impacto-exclusao").get_json()
        self.assertEqual(impact["impacto"]["questoes"], 1)
        self.assertEqual(self.client.delete(f"/api/assuntos/{subject['id']}").status_code, 409)

    def test_transferencia_atomica_confere_impacto_e_registra_historico(self):
        origin = self._matter(area=3)
        destination = self._matter(area=3)
        subject = self._subject(origin["id"], "Mecânica")
        self._question(subject["id"])
        preview = self.client.get(
            f"/api/assuntos/{subject['id']}/impacto-transferencia",
            query_string={"materia_destino_id": destination["id"]},
        ).get_json()
        changed = self.client.post(
            f"/api/assuntos/{subject['id']}/transferir",
            json={"materia_destino_id": destination["id"], "impacto_esperado": {"questoes": 0}},
        )
        self.assertEqual(changed.status_code, 409, changed.get_json())
        self.assertEqual(changed.get_json()["detalhes"]["previa"]["impacto"]["questoes"], 1)
        response = self.client.post(
            f"/api/assuntos/{subject['id']}/transferir",
            json={
                "materia_destino_id": destination["id"],
                "impacto_esperado": preview["impacto"],
                "nome": "Mecânica clássica",
            },
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(response.get_json()["id"], subject["id"])
        self.assertEqual(response.get_json()["materia_id"], destination["id"])
        with self.app.app_context():
            row = db.session.execute(
                text(
                    "SELECT materia_origem_id, materia_destino_id, questoes_impactadas "
                    "FROM assunto_transferencias WHERE assunto_id = :id"
                ),
                {"id": subject["id"]},
            ).mappings().one()
            self.assertEqual(
                tuple(row.values()), (origin["id"], destination["id"], 1)
            )

    def test_listagem_assuntos_retorna_resumos_indisponiveis(self):
        matter = self._matter(area=2)
        subject = self._subject(matter["id"], "Brasil Colônia")
        response = self.client.get(
            "/api/admin/assuntos",
            query_string={"area_enem_id": 2, "materia_id": matter["id"], "status": "ativa"},
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        item = next(item for item in response.get_json()["itens"] if item["id"] == subject["id"])
        self.assertIsNone(item["resumos"])
        self.assertEqual(item["area_enem"]["codigo"], "ciencias-humanas")

    def test_listagem_ativa_filtra_status_materia_e_ordena_nome_id(self):
        matter = self._matter()
        other = self._matter()
        suffix = uuid4().hex[:8]
        last = self._subject(matter["id"], f"Zulu {suffix}")
        first = self._subject(matter["id"], f"Alfa {suffix}")
        inactive = self._subject(matter["id"])
        archived = self._subject(matter["id"])
        hidden = self._subject(other["id"])
        self.assertEqual(self.client.post(f"/api/materias/{other['id']}/inativar").status_code, 200)
        self.assertEqual(self.client.post(f"/api/assuntos/{inactive['id']}/inativar").status_code, 200)
        self.assertEqual(self.client.post(f"/api/assuntos/{archived['id']}/arquivar").status_code, 200)

        response = self.client.get("/api/assuntos", query_string={"materia_id": matter["id"]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.get_json()], [first["id"], last["id"]])
        all_active = self.client.get("/api/assuntos").get_json()
        self.assertFalse({inactive["id"], archived["id"], hidden["id"]} & {row["id"] for row in all_active})
        self.assertEqual(self.client.get("/api/assuntos", query_string={"materia_id": other["id"]}).get_json(), [])

        from app.modules.conteudo.models.assunto import Assunto
        from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository
        with self.app.app_context():
            self.assertEqual([row.id for row in Assunto.listar_ativos(matter["id"])],
                [row.id for row in CatalogoRepository.listar_assuntos_ativos(matter["id"])])
