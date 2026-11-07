import unittest
from unittest.mock import patch
from werkzeug.datastructures import MultiDict
from app import create_app
from app.exceptions import DadosInvalidosError
from app.modules.simulados.services.simulado_validacao import composicao, paginacao, revisao
from app.modules.simulados.controllers.simulado_controller import SimuladoController
from tests.unit.test_config_and_app import TestConfig


class SimuladosUnitTest(unittest.TestCase):
    def test_limites_e_filtros_sem_ambiguidade(self):
        self.assertEqual(composicao({'titulo':'  Prova  ','questao_versao_ids':[1]}),('Prova',[1]))
        for dados in [None,[],{}, {'titulo':'Valido','questao_versao_ids':[1],'extra':1}]:
            with self.assertRaises(DadosInvalidosError):composicao(dados)
        for valor in [None,False,0,-1,2147483648,'1']:
            with self.assertRaises(DadosInvalidosError):revisao({'revisao':valor})
        self.assertEqual(paginacao({},True),({'pagina':1,'por_pagina':20},None))
        for filtros in [MultiDict([('pagina','1'),('pagina','2')]),{'status':''},{'por_pagina':'101'}]:
            with self.assertRaises(DadosInvalidosError):paginacao(filtros,True)

    def test_erro_generico_sem_detalhes(self):
        app=create_app(TestConfig);app.logger.disabled=True
        with app.test_request_context():
            def falhar():raise RuntimeError('segredo de infraestrutura')
            response,status=SimuladoController._responder(falhar)
            self.assertEqual(status,500);self.assertNotIn('segredo',response.get_data(as_text=True))

    def test_erro_integridade_alheio_ao_replay_propaga(self):
        from app.modules.simulados.services.iniciar_simulado_service import IniciarSimuladoService
        from sqlalchemy.exc import IntegrityError
        erro=IntegrityError('INSERT',{},Exception('FK'))
        with patch('app.modules.simulados.services.iniciar_simulado_service.TransactionManager.executar',side_effect=[erro,erro]):
            with self.assertRaises(IntegrityError):IniciarSimuladoService.executar(1,{
                'simulado_versao_id':1,'chave_envio':'00000000-0000-0000-0000-000000000001'})
