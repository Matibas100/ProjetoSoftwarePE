import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflitoError, DadosInvalidosError, RecursoNaoEncontradoError
from app.services.atualizar_assunto_service import AtualizarAssuntoService
from app.services.atualizar_materia_service import AtualizarMateriaService
from app.services.buscar_questoes_por_assunto_service import BuscarQuestoesPorAssuntoService
from app.services.criar_assunto_service import CriarAssuntoService
from app.services.criar_materia_service import CriarMateriaService
from app.services.criar_questao_service import CriarQuestaoService
from app.services.deletar_assunto_service import DeletarAssuntoService
from app.services.deletar_materia_service import DeletarMateriaService
from app.services.health_check_service import HealthCheckService
from app.services.listar_assuntos_service import ListarAssuntosService
from app.services.listar_materias_service import ListarMateriasService


def integrity_error():
    return IntegrityError("statement", {}, Exception("constraint"))


class MateriaServicesTest(unittest.TestCase):
    def test_criar_rejeita_formato_nome_tamanho_e_descricao(self):
        invalid = [None, {}, {"nome": " "}, {"nome": "x" * 101}, {"nome": "ok", "descricao": 1}]
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(DadosInvalidosError):
                CriarMateriaService.executar(data)

    @patch("app.services.criar_materia_service.AreaEnem")
    @patch("app.services.criar_materia_service.Materia")
    def test_criar_normaliza_e_persiste(self, materia_class, area_class):
        area_class.buscar_por_id.return_value = object()
        materia = materia_class.return_value
        materia.to_dict.return_value = {"id": 1, "nome": "Fisica", "descricao": "Mecanica"}
        result = CriarMateriaService.executar(
            {"nome": " Fisica ", "descricao": " Mecanica ", "area_enem_id": 3}
        )
        materia_class.assert_called_once_with(
            nome="Fisica", descricao="Mecanica", area_enem_id=3, status="ativa"
        )
        materia.salvar.assert_called_once_with()
        self.assertEqual(result["id"], 1)

    @patch("app.services.criar_materia_service.AreaEnem")
    @patch("app.services.criar_materia_service.Materia")
    def test_criar_traduz_duplicidade(self, materia_class, area_class):
        area_class.buscar_por_id.return_value = object()
        materia_class.return_value.salvar.side_effect = integrity_error()
        with self.assertRaises(ConflitoError):
            CriarMateriaService.executar({"nome": "Fisica", "area_enem_id": 3})

    @patch("app.services.atualizar_materia_service.Materia")
    def test_atualizar_valida_existencia_e_payload(self, materia_class):
        materia_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            AtualizarMateriaService.executar(1, {"nome": "x"})
        materia_class.buscar_por_id.return_value = MagicMock()
        invalid = [None, {}, {"nome": ""}, {"nome": "x" * 101}, {"descricao": 2}]
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(DadosInvalidosError):
                AtualizarMateriaService.executar(1, data)

    @patch("app.services.atualizar_materia_service.Materia")
    def test_atualizar_filtra_campos_e_traduz_conflito(self, materia_class):
        materia = materia_class.buscar_por_id.return_value
        materia.to_dict.return_value = {"id": 1}
        self.assertEqual(
            AtualizarMateriaService.executar(
                1, {"nome": " Nova ", "descricao": None, "ignorado": True}
            ),
            {"id": 1},
        )
        materia.atualizar.assert_called_once_with(nome="Nova", descricao=None)
        materia.atualizar.side_effect = integrity_error()
        with self.assertRaises(ConflitoError):
            AtualizarMateriaService.executar(1, {"nome": "Duplicada"})

    @patch("app.services.deletar_materia_service.CatalogoRepository")
    @patch("app.services.deletar_materia_service.Materia")
    def test_deletar_existente_inexistente_e_vinculado(self, materia_class, repository):
        materia_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            DeletarMateriaService.executar(1)
        materia = MagicMock()
        materia_class.buscar_por_id.return_value = materia
        repository.impacto_materia.return_value = {
            "assuntos": 0, "questoes": 0, "transferencias": 0
        }
        self.assertIsNone(DeletarMateriaService.executar(1))
        materia.deletar.side_effect = integrity_error()
        with self.assertRaises(ConflitoError):
            DeletarMateriaService.executar(1)

    @patch("app.services.listar_materias_service.Materia")
    def test_listar(self, materia_class):
        materia_class.listar_ativos.return_value = [MagicMock(to_dict=lambda: {"id": 1})]
        self.assertEqual(ListarMateriasService.executar(), [{"id": 1}])


class AssuntoServicesTest(unittest.TestCase):
    @patch("app.services.criar_assunto_service.CatalogoRepository")
    @patch("app.services.criar_assunto_service.Materia")
    def test_criar_valida_campos(self, materia_class, repository):
        repository.existe_assunto_equivalente.return_value = False
        invalid = [
            None,
            {},
            {"nome": " ", "materia_id": 1},
            {"nome": "x" * 151, "materia_id": 1},
            {"nome": "x", "materia_id": True},
            {"nome": "x", "materia_id": 0},
        ]
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(DadosInvalidosError):
                CriarAssuntoService.executar(data)
        materia_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            CriarAssuntoService.executar({"nome": "x", "materia_id": 1})
        materia_class.buscar_por_id.return_value = MagicMock(status="ativa")
        with self.assertRaises(DadosInvalidosError):
            CriarAssuntoService.executar({"nome": "x", "materia_id": 1, "descricao": 2})

    @patch("app.services.criar_assunto_service.CatalogoRepository")
    @patch("app.services.criar_assunto_service.Assunto")
    @patch("app.services.criar_assunto_service.Materia")
    def test_criar_persiste_e_traduz_conflito(self, materia_class, assunto_class, repository):
        materia_class.buscar_por_id.return_value = MagicMock(status="ativa")
        repository.existe_assunto_equivalente.return_value = False
        assunto = assunto_class.return_value
        assunto.to_dict.return_value = {"id": 2}
        self.assertEqual(
            CriarAssuntoService.executar({"nome": " Algebra ", "materia_id": 1, "descricao": " A "}),
            {"id": 2},
        )
        assunto_class.assert_called_once_with(
            nome="Algebra", nome_normalizado="algebra", descricao="A",
            materia_id=1, status="ativa"
        )
        assunto.salvar.side_effect = integrity_error()
        with self.assertRaises(ConflitoError):
            CriarAssuntoService.executar({"nome": "Algebra", "materia_id": 1})

    @patch("app.services.atualizar_assunto_service.Materia")
    @patch("app.services.atualizar_assunto_service.Assunto")
    def test_atualizar_valida_campos(self, assunto_class, materia_class):
        assunto_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            AtualizarAssuntoService.executar(1, {"nome": "x"})
        assunto_class.buscar_por_id.return_value = MagicMock()
        invalid = [None, {}, {"nome": ""}, {"nome": "x" * 151}, {"descricao": 1}, {"materia_id": True}]
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(DadosInvalidosError):
                AtualizarAssuntoService.executar(1, data)
        materia_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            AtualizarAssuntoService.executar(1, {"materia_id": 2})

    @patch("app.services.atualizar_assunto_service.CatalogoRepository")
    @patch("app.services.atualizar_assunto_service.Materia")
    @patch("app.services.atualizar_assunto_service.Assunto")
    def test_atualizar_persiste_e_traduz_conflito(self, assunto_class, materia_class, repository):
        assunto = assunto_class.buscar_por_id.return_value
        assunto.materia_id = 2
        assunto.nome_normalizado = "antigo"
        materia_class.buscar_por_id.return_value = MagicMock(status="ativa")
        repository.existe_assunto_equivalente.return_value = False
        assunto.to_dict.return_value = {"id": 1}
        self.assertEqual(
            AtualizarAssuntoService.executar(1, {"nome": " Novo ", "descricao": " D ", "materia_id": 2}),
            {"id": 1},
        )
        assunto.atualizar.assert_called_once_with(
            nome="Novo", nome_normalizado="novo", descricao="D"
        )
        assunto.atualizar.side_effect = integrity_error()
        with self.assertRaises(ConflitoError):
            AtualizarAssuntoService.executar(1, {"nome": "Duplicado"})

    @patch("app.services.deletar_assunto_service.CatalogoRepository")
    @patch("app.services.deletar_assunto_service.Assunto")
    def test_deletar_existente_inexistente_e_vinculado(self, assunto_class, repository):
        assunto_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            DeletarAssuntoService.executar(1)
        assunto = MagicMock()
        assunto_class.buscar_por_id.return_value = assunto
        repository.impacto_assunto.return_value = {"questoes": 0, "transferencias": 0}
        self.assertIsNone(DeletarAssuntoService.executar(1))
        assunto.deletar.side_effect = integrity_error()
        with self.assertRaises(ConflitoError):
            DeletarAssuntoService.executar(1)

    @patch("app.services.listar_assuntos_service.Assunto")
    def test_listar(self, assunto_class):
        assunto_class.listar_ativos.return_value = [MagicMock(to_dict=lambda: {"id": 1})]
        self.assertEqual(ListarAssuntosService.executar(), [{"id": 1}])


class QuestaoServicesTest(unittest.TestCase):
    def valid_data(self):
        return {
            "enunciado": "Enunciado",
            "alternativa_a": "A",
            "alternativa_b": "B",
            "alternativa_c": "C",
            "alternativa_d": "D",
            "alternativa_e": "E",
            "resposta_correta": "C",
            "dificuldade": "media",
            "assunto_id": 1,
            "explicacao": " Explicacao ",
        }

    def test_criar_rejeita_formato_e_todos_os_textos_obrigatorios(self):
        with self.assertRaises(DadosInvalidosError):
            CriarQuestaoService.executar(None)
        for field in CriarQuestaoService.CAMPOS_TEXTO_OBRIGATORIOS:
            data = self.valid_data()
            data[field] = " "
            with self.subTest(field=field), self.assertRaises(DadosInvalidosError):
                CriarQuestaoService.executar(data)

    def test_criar_valida_resposta_dificuldade_e_identificador(self):
        for field, value in (
            ("resposta_correta", None),
            ("resposta_correta", "F"),
            ("dificuldade", None),
            ("dificuldade", "extrema"),
            ("assunto_id", True),
            ("assunto_id", 0),
        ):
            data = self.valid_data()
            data[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(DadosInvalidosError):
                CriarQuestaoService.executar(data)

    @patch("app.services.criar_questao_service.Assunto")
    def test_criar_valida_assunto_e_explicacao(self, assunto_class):
        assunto_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            CriarQuestaoService.executar(self.valid_data())
        assunto_class.buscar_por_id.return_value = MagicMock(
            status="ativa", materia=MagicMock(status="ativa")
        )
        data = self.valid_data()
        data["explicacao"] = 10
        with self.assertRaises(DadosInvalidosError):
            CriarQuestaoService.executar(data)

    @patch("app.services.criar_questao_service.Questao")
    @patch("app.services.criar_questao_service.Assunto")
    def test_criar_persiste_e_traduz_conflito(self, assunto_class, questao_class):
        assunto_class.buscar_por_id.return_value = MagicMock(
            status="ativa", materia=MagicMock(status="ativa")
        )
        questao = questao_class.return_value
        questao.to_dict.return_value = {"id": 3}
        with patch("app.services.criar_questao_service.TransactionManager.executar", side_effect=lambda op: op()), \
             patch("app.services.criar_questao_service.QuestaoEvento"):
            self.assertEqual(CriarQuestaoService.executar(self.valid_data(), 1), {"id": 3})
        self.assertEqual(questao_class.call_args.kwargs["explicacao"], "Explicacao")
        questao.salvar.side_effect = integrity_error()
        with patch("app.services.criar_questao_service.TransactionManager.executar", side_effect=lambda op: op()), \
             self.assertRaises(ConflitoError):
            CriarQuestaoService.executar(self.valid_data(), 1)

    @patch("app.services.buscar_questoes_por_assunto_service.QuestaoRepository")
    @patch("app.services.buscar_questoes_por_assunto_service.Assunto")
    def test_buscar_valida_e_retorna_repository(self, assunto_class, repository):
        for value in (None, "abc", 0, -1):
            with self.subTest(value=value), self.assertRaises(DadosInvalidosError):
                BuscarQuestoesPorAssuntoService.executar(value)
        assunto_class.buscar_por_id.return_value = None
        with self.assertRaises(RecursoNaoEncontradoError):
            BuscarQuestoesPorAssuntoService.executar("2")
        assunto_class.buscar_por_id.return_value = object()
        repository.buscar_por_assunto.return_value = [{"id": 4}]
        self.assertEqual(BuscarQuestoesPorAssuntoService.executar("2"), [{"id": 4}])
        repository.buscar_por_assunto.assert_called_once_with(2)

    def test_health(self):
        self.assertEqual(HealthCheckService.executar()["status"], "online")


if __name__ == "__main__":
    unittest.main()
