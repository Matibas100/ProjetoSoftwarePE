import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock
from datetime import datetime

from app.modules.contas.domain.privacidade import DOCUMENTOS, VIGENTES, documento_vigente, estado_privacidade
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.services.privacidade_validacao import validar_corpo, validar_revisao, validar_versao, resposta_reenvio
from app.modules.contas.services.validar_permissao_plano_service import ValidarPermissaoPlanoService
from app.modules.contas.repositories.privacidade_repository import PrivacidadeRepository


class DocumentosPrivacidadeTest(unittest.TestCase):
    def test_hash_das_fontes_publicadas_e_links_locais(self):
        frontend = Path(__file__).resolve().parents[3] / "frontend"
        for tipo, versoes in DOCUMENTOS.items():
            for versao, doc in versoes.items():
                conteudo = (frontend / doc["url"].lstrip("/")).read_bytes()
                self.assertEqual(hashlib.sha256(conteudo).hexdigest(), doc["sha256"])
                texto = conteudo.decode("utf-8")
                self.assertIn('lang="pt-BR"', texto)
                self.assertIn('datetime="2026-11-', texto)
                self.assertIn("Matheus Gabriel Oliveira Martins", texto)
                self.assertIn("contato@plataformaenem.example", texto)
                self.assertNotIn("<script", texto)
                self.assertEqual(doc["versao"], versao)
            self.assertIn(VIGENTES[tipo], versoes)
        copia = documento_vigente("uso"); copia["versao"] = "outra"
        self.assertEqual(documento_vigente("uso")["versao"], "2.0")

    def test_ausencia_versao_hash_e_negativas(self):
        self.assertFalse(estado_privacidade({})["plano_liberado"])
        def registro(tipo, acao="aceitar", **extra):
            doc = documento_vigente(tipo)
            return SimpleNamespace(id=1, acao=acao, versao=doc["versao"],
                documento_sha256=doc["sha256"], registrado_em=datetime(2026, 11, 6), **extra)
        registros = {tipo: registro(tipo) for tipo in ("uso", "plano")}
        estado = estado_privacidade(registros)
        self.assertTrue(estado["plano_liberado"])
        self.assertTrue(estado["termos_uso"]["registro"]["registrado_em"].endswith("Z"))
        registros["uso"].documento_sha256 = "0" * 64
        self.assertFalse(estado_privacidade(registros)["plano_liberado"])
        for acao, esperado in (("aceitar", "desatualizado"), ("recusar", "recusado"), ("revogar", "revogado")):
            registros["plano"].acao = acao; registros["plano"].versao = "antiga"
            self.assertEqual(estado_privacidade(registros)["consentimento_plano"]["estado"], esperado)


class DecisoesPrivacidadeUnitTest(unittest.TestCase):
    def test_corpo_estrito_e_revisao_uuid_canonico(self):
        dados = {'versao':'1.0','chave_envio':'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','revisao':0}
        self.assertEqual(validar_corpo(dados),dados)
        self.assertEqual(validar_corpo({**dados,'confirmar':True},True)['confirmar'],True)
        for invalido in (None,[],{}, {**dados,'revisao':True},{**dados,'revisao':-1},
                {**dados,'revisao':9223372036854775808},{**dados,'chave_envio':None},
                {**dados,'chave_envio':dados['chave_envio'].upper()}, {**dados,'chave_envio':'abc'},
                {**dados,'versao':None},{**dados,'versao':'x'*21},{**dados,'hash':'a'*64}):
            with self.assertRaises(AutenticacaoError):validar_corpo(invalido)
        for value in (False,1,'true',None):
            with self.assertRaises(AutenticacaoError):validar_corpo({**dados,'confirmar':value},True)
        validar_revisao(None,0);validar_revisao(SimpleNamespace(id=8),8)
        with self.assertRaises(AutenticacaoError):validar_revisao(None,1)
        with self.assertRaises(AutenticacaoError):validar_versao('uso','antiga')

    def test_reenvio_confere_acao_tipo_versao_e_revisao(self):
        registro=SimpleNamespace(tipo='uso',acao='aceitar',versao='1.0',revisao_base=0)
        for alteracao in ({'versao':'2.0'},{'revisao':1}):
            with self.assertRaises(AutenticacaoError):resposta_reenvio(registro,{'versao':'1.0','revisao':0,**alteracao},'uso','aceitar',{})
        with self.assertRaises(AutenticacaoError):resposta_reenvio(registro,{'versao':'1.0','revisao':0},'plano','aceitar',{})

    @patch.object(PrivacidadeRepository,'ultimas',side_effect=RuntimeError('consulta indisponível'))
    def test_falha_da_consulta_nao_autoriza(self,_):
        with self.assertRaises(RuntimeError):ValidarPermissaoPlanoService.executar(7)

    def test_guard_apos_lock_antes_de_replay_snapshot_ou_item(self):
        from app.modules.plano_estudos.services import gerar_plano_service as gerar
        from app.modules.plano_estudos.services import consultar_plano_service as consultar
        from app.modules.plano_estudos.services import concluir_plano_item_service as concluir
        calls=[]
        def bloquear(_):calls.append('lock')
        def negar(_):calls.append('guard');raise AutenticacaoError('Pendente',403,'consentimento_plano_necessario')
        with patch.object(gerar.TransactionManager,'executar',side_effect=lambda fn:fn()), \
                patch.object(gerar.Repo,'bloquear_usuario',side_effect=bloquear), \
                patch.object(ValidarPermissaoPlanoService,'executar',side_effect=negar), \
                patch.object(gerar.Repo,'por_chave') as replay,patch.object(gerar.Repo,'atual') as atual, \
                patch.object(gerar.Repo,'item_proprio') as item:
            seletor=Mock()
            for operacao in (lambda:gerar.gerar(7,{'chave_envio':'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'},seletor),
                    lambda:gerar.gerar(7,{'chave_envio':'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','plano_atual_id':1,'confirmar':True},seletor,True),
                    lambda:consultar.ConsultarPlanoService.executar(7),lambda:concluir.ConcluirPlanoItemService.executar(7,1,{'confirmar':True})):
                calls.clear()
                with self.assertRaises(AutenticacaoError):operacao()
                self.assertEqual(calls,['lock','guard'])
            replay.assert_not_called();atual.assert_not_called();item.assert_not_called();seletor.executar.assert_not_called()
