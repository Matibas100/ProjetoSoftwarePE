"""Contratos HTTP e sentinelas de dados sensíveis em falhas inesperadas."""
import unittest
from unittest.mock import patch

from flask import jsonify
from sqlalchemy.exc import StatementError

from app import create_app
from app.controllers.assunto_controller import AssuntoController
from app.controllers.materia_controller import MateriaController
from app.controllers.questao_controller import QuestaoController
from app.controllers.pratica_controller import PraticaController
from app.controllers.simulado_controller import SimuladoController
from app.controllers.plano_estudo_controller import PlanoEstudoController
from app.controllers.desempenho_controller import DesempenhoController
from app.controllers.area_enem_controller import AreaEnemController
from app.controllers.autenticacao_controller import AutenticacaoController
from app.domain.autenticacao import AutenticacaoError
from app.exceptions import ConflitoError
from tests.unit.test_config_and_app import TestConfig


class HttpResponseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)

    def test_envelopes_detalhes_e_status_especificos(self):
        with self.app.test_request_context():
            for controller in (MateriaController, AssuntoController, QuestaoController,
                               PraticaController, SimuladoController, PlanoEstudoController, DesempenhoController):
                with self.subTest(controller=controller):
                    response, status = controller._responder(lambda: {'itens': []})
                    self.assertEqual((status, response.json), (200, {'itens': []}))
                    def falhar():
                        raise ConflitoError('Conflito esperado', {'revisao': 2})
                    response, status = controller._responder(falhar)
                    esperado = {'erro': 'Conflito esperado'}
                    if controller is not QuestaoController:
                        esperado['detalhes'] = {'revisao': 2}
                    self.assertEqual((status, response.json), (409, esperado))
            for controller in (MateriaController, AssuntoController, QuestaoController):
                response, status = controller._responder(lambda: {'id': 1}, 201)
                self.assertEqual((status, response.json), (201, {'id': 1}))
            for controller in (MateriaController, AssuntoController):
                self.assertEqual(controller._responder(lambda: None, 204), ('', 204))
            for controller in (PraticaController, SimuladoController, PlanoEstudoController):
                response, status = controller._responder(lambda: ({'id': 1}, 201))
                self.assertEqual((status, response.json), (201, {'id': 1}))

    def test_falhas_sanitizadas_em_todos_adaptadores(self):
        erro = StatementError('senha-SENTINELA', 'SELECT token-SENTINELA',
            {'password': 'parametro-SENTINELA'}, RuntimeError('corpo-SENTINELA'))
        def falhar():
            raise erro
        with self.app.test_request_context('/api/materias?token=url-SENTINELA',
                headers={'Cookie': 'cookie-SENTINELA'}):
            for controller in (MateriaController, AssuntoController, QuestaoController,
                               PraticaController, SimuladoController, PlanoEstudoController,
                               DesempenhoController, AutenticacaoController):
                with self.subTest(controller=controller), self.assertLogs(self.app.logger, 'ERROR') as logs:
                    result = controller._responder(falhar)
                    response = self.app.make_response(result)
                    self.assertEqual(response.status_code, 500)
                self.assertIn('StatementError', str(logs.output))
                self.assertNotIn('SENTINELA', str(logs.output) + response.get_data(as_text=True))
                self.assertTrue(all(record.exc_info is None for record in logs.records))
            for target, call in (
                ('app.controllers.area_enem_controller.ListarAreasEnemService.executar', AreaEnemController.listar),
                ('app.auth_http.AutorizarService.executar', lambda: self.app.test_client().get('/api/materias')),
            ):
                with patch(target, side_effect=erro), self.assertLogs(self.app.logger, 'ERROR') as logs:
                    response = self.app.make_response(call())
                    self.assertEqual(response.status_code, 500)
                self.assertIn('StatementError', str(logs.output))
                self.assertNotIn('SENTINELA', str(logs.output) + response.get_data(as_text=True))

    def test_auth_preserva_resposta_cookie_codigo_e_retry_after(self):
        with self.app.test_request_context():
            response = jsonify({'csrf_token': 'teste'})
            response.set_cookie('enem_session', 'teste', httponly=True)
            self.assertIs(AutenticacaoController._responder(lambda: response), response)
            def falhar():
                raise AutenticacaoError('Espere', 429, 'limite', retry_after=30)
            result = AutenticacaoController._responder(falhar)
            self.assertEqual((result.status_code, result.json), (429, {'erro': 'Espere', 'codigo': 'limite'}))
            self.assertEqual(result.headers['Retry-After'], '30')
            def expirar():
                raise AutenticacaoError('Sessão expirada', 401, 'sessao_invalida')
            self.assertIn('Max-Age=0', AutenticacaoController._responder(expirar).headers['Set-Cookie'])
