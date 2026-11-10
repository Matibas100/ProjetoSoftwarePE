"""Consultas simples, limites antes da persistência e adaptação HTTP segura."""
import unittest
from unittest.mock import patch

from flask import Flask

from app.exceptions import DadosInvalidosError, RecursoNaoEncontradoError
from app.modules.conteudo.controllers.materia_controller import MateriaController
from app.modules.conteudo.controllers.assunto_controller import AssuntoController
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.services.buscar_materia_por_id_service import BuscarMateriaPorIdService
from app.modules.conteudo.services.buscar_assunto_por_id_service import BuscarAssuntoPorIdService


CASOS = (
    (
        BuscarMateriaPorIdService,
        Materia,
        MateriaController,
        "app.modules.conteudo.controllers.materia_controller.BuscarMateriaPorIdService",
        {"area_enem_id": 4}
    ),
    (
        BuscarAssuntoPorIdService,
        Assunto,
        AssuntoController,
        "app.modules.conteudo.controllers.assunto_controller.BuscarAssuntoPorIdService",
        {"materia_id": 9, "nome_normalizado": "álgebra"}
    ),
)


class BuscarCatalogoPorIdTest(unittest.TestCase):
    def test_rejeita_tipos_e_intervalo_sem_consultar_model(self):
        for service, model, *_ in CASOS:
            with patch.object(model, "buscar_por_id") as buscar:
                for valor in (None, True, False, "1", 1.0, -1, 0, 2147483648, 10**100):
                    with self.subTest(
                        service=service,
                        valor=valor
                    ), self.assertRaises(DadosInvalidosError):
                        service.executar(valor)
                buscar.assert_not_called()

    def test_serializa_campos_basicos_tres_estados_e_id_maximo(self):
        for service, model, _, _, vinculo in CASOS:
            for status in ("ativa", "inativa", "arquivada"):
                registro = model(
                    id=2147483647,
                    nome="Álgebra",
                    descricao=None,
                    status=status,
                    **vinculo
                )
                with self.subTest(model=model, status=status), patch.object(
                    model,
                    "buscar_por_id",
                    return_value=registro
                ) as buscar:
                    self.assertEqual(service.executar(2147483647), registro.to_dict())
                    buscar.assert_called_once_with(2147483647)
                    self.assertIsNone(service.executar(1)["descricao"])

    def test_ausencia_e_delegacao_controller_incluindo_erros(self):
        app = Flask(__name__)
        app.logger.disabled = True
        for service, model, controller, alvo, _ in CASOS:
            with patch.object(model, "buscar_por_id", return_value=None):
                with self.assertRaises(RecursoNaoEncontradoError):
                    service.executar(1)
            with app.app_context(), patch(alvo) as caso:
                caso.executar.return_value = {"id": 7}
                response, status = controller.buscar_por_id(7)
                self.assertEqual((status, response.json), (200, {"id": 7}))
                caso.executar.assert_called_once_with(7)
                for erro, esperado in (
                    (DadosInvalidosError("invalido"), 400),
                    (RecursoNaoEncontradoError("ausente"), 404),
                    (RuntimeError("SELECT senha segredo"), 500)
                ):
                    caso.executar.side_effect = erro
                    response, status = controller.buscar_por_id(7)
                    self.assertEqual(status, esperado)
                    if esperado == 500:
                        self.assertEqual(
                            response.json,
                            {"erro": "Ocorreu um erro interno no servidor."}
                        )
