import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from app.controllers.assunto_controller import AssuntoController
from app.controllers.materia_controller import MateriaController
from app.controllers.questao_controller import QuestaoController
from app.exceptions import DadosInvalidosError
from app.models.assunto import Assunto
from app.models.materia import Materia
from app.models.questao import Questao
from app.repositories.questao_repository import QuestaoRepository


class ModelSerializationTest(unittest.TestCase):
    def test_materia_to_dict(self):
        materia = Materia(id=1, nome="Matematica", descricao=None, area_enem_id=4, status="ativa")
        result = materia.to_dict()
        self.assertEqual(result["area_enem_id"], 4)
        self.assertEqual(result["status"], "ativa")
        self.assertTrue({"id", "nome", "descricao"}.issubset(result))

    def test_assunto_to_dict(self):
        assunto = Assunto(
            id=2, nome="Algebra", nome_normalizado="algebra", descricao="Basica",
            materia_id=1, status="ativa"
        )
        result = assunto.to_dict()
        self.assertEqual(result["nome_normalizado"], "algebra")
        self.assertEqual(result["status"], "ativa")
        self.assertTrue({"id", "nome", "descricao", "materia_id"}.issubset(result))

    def test_questao_to_dict(self):
        data = {
            "id": 3,
            "enunciado": "Quanto?",
            "alternativa_a": "1",
            "alternativa_b": "2",
            "alternativa_c": "3",
            "alternativa_d": "4",
            "alternativa_e": "5",
            "resposta_correta": "D",
            "explicacao": None,
            "dificuldade": "facil",
            "assunto_id": 2,
        }
        self.assertEqual(Questao(**data).to_dict(), data)


class CrudMixinTest(unittest.TestCase):
    @patch("app.models.crud_mixin.db.session")
    def test_salvar_commit_e_rollback(self, session):
        materia = Materia(nome="Fisica")
        self.assertIs(materia.salvar(), materia)
        session.add.assert_called_once_with(materia)
        session.commit.assert_called_once_with()

        session.commit.side_effect = RuntimeError("falha")
        with self.assertRaises(RuntimeError):
            materia.salvar()
        session.rollback.assert_called_once_with()

    @patch("app.models.crud_mixin.db.session")
    def test_operacoes_sem_commit_usam_flush(self, session):
        materia = Materia(nome="Fisica")
        self.assertIs(materia.salvar(confirmar=False), materia)
        materia.atualizar(confirmar=False, nome="Quimica")
        materia.deletar(confirmar=False)
        self.assertEqual(session.flush.call_count, 3)
        session.commit.assert_not_called()

    @patch("app.models.crud_mixin.db.session")
    def test_atualizar_filtra_campos_commit_e_rollback(self, session):
        materia = Materia(nome="Antiga", descricao=None)
        self.assertIs(
            materia.atualizar(nome="Nova", descricao="Texto", inexistente=True), materia
        )
        self.assertEqual(materia.nome, "Nova")
        self.assertFalse(hasattr(materia, "inexistente"))
        session.commit.assert_called_once_with()

        session.commit.side_effect = RuntimeError("falha")
        with self.assertRaises(RuntimeError):
            materia.atualizar(nome="Outra")
        session.rollback.assert_called_once_with()

    @patch("app.models.crud_mixin.db.session")
    def test_deletar_commit_e_rollback(self, session):
        materia = Materia(nome="Fisica")
        self.assertIsNone(materia.deletar())
        session.delete.assert_called_once_with(materia)
        session.commit.assert_called_once_with()

        session.commit.side_effect = RuntimeError("falha")
        with self.assertRaises(RuntimeError):
            materia.deletar()
        session.rollback.assert_called_once_with()

    @patch("app.models.crud_mixin.db.session")
    @patch("app.models.crud_mixin.db.select")
    def test_listar_e_buscar(self, select, session):
        statement = select.return_value
        session.execute.return_value.scalars.return_value.all.return_value = ["item"]
        self.assertEqual(Materia.listar_todos(), ["item"])
        select.assert_called_once_with(Materia)
        session.execute.assert_called_once_with(statement)
        session.get.return_value = "registro"
        self.assertEqual(Materia.buscar_por_id(7), "registro")
        session.get.assert_called_once_with(Materia, 7)


class QuestaoRepositoryTest(unittest.TestCase):
    @patch("app.repositories.questao_repository.db.session.execute")
    def test_fecha_resultado_no_sucesso(self, execute):
        result = execute.return_value
        result.mappings.return_value.all.return_value = [{"id": 1}]
        self.assertEqual(QuestaoRepository.buscar_por_assunto(2), [{"id": 1}])
        result.close.assert_called_once_with()

    @patch("app.repositories.questao_repository.db.session.execute")
    def test_fecha_resultado_quando_mapeamento_falha(self, execute):
        result = execute.return_value
        result.mappings.return_value.all.side_effect = ValueError("linha invalida")
        with self.assertRaises(ValueError):
            QuestaoRepository.buscar_por_assunto(2)
        result.close.assert_called_once_with()


class ControllerResponseTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.logger.disabled = True

    def assert_responder(self, controller):
        with self.app.app_context():
            response, status = controller._responder(lambda: {"id": 1}, 201)
            self.assertEqual(status, 201)
            self.assertEqual(response.get_json(), {"id": 1})

            response, status = controller._responder(
                lambda: (_ for _ in ()).throw(DadosInvalidosError("invalido"))
            )
            self.assertEqual(status, 400)
            self.assertEqual(response.get_json(), {"erro": "invalido"})

            response, status = controller._responder(
                lambda: (_ for _ in ()).throw(RuntimeError("inesperado"))
            )
            self.assertEqual(status, 500)
            self.assertEqual(
                response.get_json(), {"erro": "Ocorreu um erro interno no servidor."}
            )

    def test_materia_respostas_inclusive_204(self):
        self.assert_responder(MateriaController)
        with self.app.app_context():
            self.assertEqual(MateriaController._responder(lambda: None, 204), ("", 204))

    def test_assunto_respostas_inclusive_204(self):
        self.assert_responder(AssuntoController)
        with self.app.app_context():
            self.assertEqual(AssuntoController._responder(lambda: None, 204), ("", 204))

    def test_questao_respostas(self):
        self.assert_responder(QuestaoController)


if __name__ == "__main__":
    unittest.main()
