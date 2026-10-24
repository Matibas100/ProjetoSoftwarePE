import unittest
from unittest.mock import patch
from werkzeug.datastructures import MultiDict
from app.exceptions import DadosInvalidosError
from app.services.pratica_validacao import parametros, inicio
from app.services.iniciar_pratica_service import IniciarPraticaService
from app.controllers.pratica_controller import PraticaController
from app import create_app
from tests.unit.test_config_and_app import TestConfig


class PraticasUnitTest(unittest.TestCase):
    def test_validacao_rejeita_entradas_ambiguas_e_limites(self):
        for filtros in [{'pagina':None},{'pagina':True},{'pagina':'1'*5000},{'assunto_id':'１２'},
                        {'por_pagina':'0'},MultiDict([('pagina','1'),('pagina','2')])]:
            with self.assertRaises(DadosInvalidosError): parametros(filtros,{'assunto_id'})
        self.assertEqual(parametros({},set()),{'pagina':1,'por_pagina':20})
        chave='A'*8+'-'+'B'*4+'-'+'C'*4+'-'+'D'*4+'-'+'E'*12
        self.assertEqual(inicio({'questao_versao_id':1,'chave_envio':chave}),(1,chave.lower()))
        for chave_invalida in ['x'*36,'a'*32,'{00000000-0000-0000-0000-000000000000}',1]:
            with self.assertRaises(DadosInvalidosError): inicio({'questao_versao_id':1,'chave_envio':chave_invalida})

    def test_erro_http_nao_expoe_detalhes_internos(self):
        app=create_app(TestConfig); app.logger.disabled=True
        with app.test_request_context():
            def falhar(): raise RuntimeError('detalhe privado de infraestrutura')
            response,status=PraticaController._responder(falhar)
            self.assertEqual(status,500); self.assertNotIn('privado',response.get_data(as_text=True))

    def test_erro_integridade_nao_relacionado_a_replay_propaga(self):
        from sqlalchemy.exc import IntegrityError
        erro=IntegrityError('INSERT',{},Exception('FK'))
        with patch('app.services.iniciar_pratica_service.PraticaRepository.por_chave',return_value=None), \
             patch('app.services.iniciar_pratica_service.TransactionManager.executar',side_effect=[erro,erro]):
            with self.assertRaises(IntegrityError):
                IniciarPraticaService.executar(1,{'questao_versao_id':1,'chave_envio':'00000000-0000-0000-0000-000000000000'})
