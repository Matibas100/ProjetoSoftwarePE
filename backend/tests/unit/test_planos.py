import unittest
from datetime import datetime
from unittest.mock import patch, Mock
from app.exceptions import DadosInvalidosError
from app.modules.plano_estudos.services.plano_validacao import operacao, confirmacao
from app.modules.plano_estudos.services.selecionar_plano_service import SelecionarPlanoService
from app.modules.plano_estudos.controllers.plano_estudo_controller import PlanoEstudoController
from app import create_app
from tests.unit.test_config_and_app import TestConfig


class PlanosUnitTest(unittest.TestCase):
    def test_corpos_estritos_uuid_e_confirmacao(self):
        chave='00000000-0000-0000-0000-000000000001'
        self.assertEqual(operacao({'chave_envio':chave}),(chave,None))
        self.assertEqual(operacao({'chave_envio':chave,'plano_atual_id':1,'confirmar':True},True),(chave,1))
        for dados in [None,[],{}, {'chave_envio':chave,'usuario_id':1}, {'chave_envio':None}, {'chave_envio':'x'*36}, {'chave_envio':'x'}]:
            with self.assertRaises(DadosInvalidosError):operacao(dados)
        for valor in [None,True,0,-1,'1',9223372036854775808]:
            with self.assertRaises(DadosInvalidosError):operacao({'chave_envio':chave,'plano_atual_id':valor,'confirmar':True},True)
        for valor in [False,1,'true',None]:
            with self.assertRaises(DadosInvalidosError):confirmacao({'confirmar':valor})

    def selecionar(self, linhas, pares=None):
        d={'limiar_amostra':5,'periodo':{'inicio':'2026-09-25','fim':'2026-10-24','timezone':'UTC'},'assuntos':linhas}
        diagnostico = Mock()
        diagnostico.executar.return_value = d
        with patch('app.modules.plano_estudos.services.selecionar_plano_service.pares_elegiveis_plano',return_value=pares if pares is not None else {(a['assunto_id'],1) for a in linhas}):
            resultado=SelecionarPlanoService(diagnostico).executar(7,'contexto',datetime(2026,10,24))
            diagnostico.executar.assert_called_once_with(7,contexto='contexto',instante=datetime(2026,10,24))
            return resultado[1]

    @staticmethod
    def linha(id_,acertos,total,percentual=20):
        return dict(assunto_id=id_,materia_id=1,assunto_nome='Assunto',materia_nome='Matéria',acertos=acertos,total_respostas=total,percentual_acerto=percentual)

    def test_fracoes_exatas_limite_desempates_e_100(self):
        itens=self.selecionar([self.linha(4,4,10),self.linha(3,1,5),self.linha(2,2,10),self.linha(1,2,10),self.linha(5,0,4)])
        self.assertEqual([i['assunto_id'] for i in itens],[1,2,3])
        self.assertIn('1 acerto em 5 respostas',itens[2]['justificativa'])
        itens=self.selecionar([self.linha(1,10000,30000,33.33),self.linha(2,9999,30000,33.33)])
        self.assertEqual([i['assunto_id'] for i in itens],[2,1])
        i=self.selecionar([self.linha(1,5,5,100)])[0]
        self.assertEqual(i['percentual_acerto'],100);self.assertIn('Prioridade relativa',i['justificativa']);self.assertNotIn('dificuldade',i['justificativa'])
        self.assertEqual(self.selecionar([self.linha(1,0,4)]),[])
        self.assertEqual(self.selecionar([self.linha(1,0,5)],set()),[])

    def test_diagnostico_indisponivel_propaga_e_http_nao_expoe_interno(self):
        diagnostico = Mock()
        diagnostico.executar.side_effect = RuntimeError('interno')
        with self.assertRaises(RuntimeError):SelecionarPlanoService(diagnostico).executar(1,None,datetime(2026,10,24))
        app=create_app(type('PlanoTestConfig',(TestConfig,),{'AUTH_SECRET_KEY':'ab'*32}));app.logger.disabled=True
        with app.test_request_context():
            def falhar():raise RuntimeError('interno secreto')
            r,s=PlanoEstudoController._responder(falhar)
            self.assertEqual(s,500);self.assertNotIn('secreto',r.get_data(as_text=True))
