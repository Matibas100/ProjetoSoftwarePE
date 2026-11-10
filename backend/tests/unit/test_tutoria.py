"""Transporte e relógio controlados somente em unidade; nenhuma chamada paga."""
from concurrent.futures import ThreadPoolExecutor
import json
from threading import Barrier
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import requests
from urllib3.exceptions import ReadTimeoutError

from app import create_app
from app.extensions import db
from app.modules.contas.api import ValidarPermissaoTutoriaService
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.repositories.privacidade_repository import PrivacidadeRepository
from app.modules.tutor_ia.domain.tutoria import (
    TITULOS,
    TutoriaError,
    validar_entrada,
    validar_resposta,
)
from app.modules.tutor_ia.services.gemini_service import GeminiService, ENDPOINT, MAX_BYTES
from app.modules.tutor_ia.services.gerar_tutoria_service import GerarTutoriaService
from app.modules.tutor_ia.services.limite_tutoria import LimiteTutoria
from app.modules.tutor_ia.controllers.tutoria_controller import TutoriaController
from tests.unit.test_config_and_app import TestConfig


ENTRADA = {
    'disciplina': 'Física',
    'nivel': 'ensino_medio',
    'assunto': 'Eletricidade',
    'duvida': 'Qual a diferença entre corrente e tensão?'
}
TEXTO = '\n'.join(t + '\nConteúdo pedagógico.' for t in TITULOS)


class TutoriaValidacaoTest(unittest.TestCase):
    def test_contrato_normalizacao_limites_e_controles(self):
        self.assertEqual(validar_entrada({k: ' ' + v + ' ' for k, v in ENTRADA.items()}), ENTRADA)
        for campo, minimo, maximo in [
            (
                'disciplina',
                1,
                100
            ),
            (
                'assunto',
                1,
                150
            ),
            (
                'duvida',
                10,
                2000
            )
        ]:
            for n in (minimo, maximo):
                self.assertEqual(len(validar_entrada({**ENTRADA, campo: 'a'*n})[campo]), n)
            for valor in (
                '',
                'a'*(minimo - 1),
                'a'*(maximo + 1),
                None,
                1,
                True,
                [],
                'x\x00',
                '\x7fx'
            ):
                with self.subTest(
                    campo=campo,
                    valor=str(valor)[: 15]
                ), self.assertRaises(TutoriaError):
                    validar_entrada({**ENTRADA, campo: valor})
        for entrada in (
            None,
            [],
            {},
            {**ENTRADA, 'extra': 'x'},
            {**ENTRADA, 'nivel': 'outro'},
            {
                **ENTRADA,
                'disciplina': 'Fí\nsica'
            },
            {
                **ENTRADA,
                'duvida': '\x00'+ENTRADA['duvida']
            }
        ):
            with self.assertRaises(TutoriaError):
                validar_entrada(entrada)
        self.assertIn(
            '\t\n',
            validar_entrada({
                **ENTRADA,
                'duvida': 'Texto com\t\nquebra válida'
            })['duvida']
        )

    def test_quatro_secoes_unicas_ordenadas_com_conteudo(self):
        self.assertEqual(validar_resposta(TEXTO.replace('\n', '\r\n')), TEXTO)
        for texto in (
            None,
            '',
            'x'*12001,
            TEXTO + '\n'+TITULOS[0],
            TEXTO.replace(
                TITULOS[2],
                'Outro'
            ),
            TEXTO.replace(
                '1. Explicação simples\nConteúdo pedagógico.',
                TITULOS[0]
            ),
            'Prefácio\n' + TEXTO,
            '\n'.join(reversed(TEXTO.split('\n')))
        ):
            with self.assertRaises(TutoriaError) as cm:
                validar_resposta(texto)
            self.assertEqual(cm.exception.codigo, 'tutor_resposta_invalida')

    def test_ordem_sem_rede_em_erro_limite_e_liberacao_finally(self):
        eventos = []
        gerador = Mock(disponivel=True)
        gerador.gerar.side_effect = lambda dados, prompt: eventos.append('rede') or TEXTO
        limite = LimiteTutoria()
        service = GerarTutoriaService(gerador, lambda id_: eventos.append('permissao'), limite)
        self.assertEqual(service.executar(9, ENTRADA)['resposta'], TEXTO)
        self.assertEqual(eventos, ['permissao', 'rede'])
        self.assertIn('SEM gabarito', gerador.gerar.call_args.args[1])
        with self.assertRaises(TutoriaError):
            service.executar(9, {})
        gerador.gerar.assert_called_once()
        gerador.disponivel = False
        with self.assertRaises(TutoriaError) as cm:
            service.executar(9, ENTRADA)
        self.assertEqual(cm.exception.status_code, 503)
        self.assertEqual(limite._contas[9].tentativas, 1)
        gerador.disponivel = True
        gerador.gerar.side_effect = RuntimeError('conteúdo privado')
        for _ in range(3):
            with self.assertRaises(RuntimeError):
                service.executar(9, ENTRADA)
        self.assertEqual(limite._ativas, 0)
        with self.assertRaises(TutoriaError) as cm:
            service.executar(9, ENTRADA)
        self.assertEqual(cm.exception.status_code, 429)
        negado = GerarTutoriaService(
            gerador,
            Mock(side_effect=AutenticacaoError(
                'Pendente',
                409
            )),
            limite
        )
        with self.assertRaises(AutenticacaoError):
            negado.executar(9, ENTRADA)


class GeminiUnitTest(unittest.TestCase):
    def setUp(self):
        self.cliente = GeminiService(
            habilitado=True,
            chave='chave-sintetica',
            modelo='gemini-3.6-flash'
        )

    def resposta(self, dados=None, raw=None, status=200):
        resposta = Mock(status_code=status)
        resposta.__enter__ = Mock(return_value=resposta)
        resposta.__exit__ = Mock(return_value=False)
        if dados is None:
            dados = {
                'status': 'completed',
                'steps': [
                    {'type': 'model_output', 'content': [{'type': 'text', 'text': 'anterior'}]},
                    {'type': 'thought', 'content': [{'type': 'text', 'text': 'pensamento privado'}]},
                    {
                        'type': 'model_output',
                        'content': [
                            {'type': 'thought', 'text': 'interno'},
                            {'type': 'text', 'text': TEXTO[: 20]},
                            {'type': 'text', 'text': TEXTO[20:]}
                        ]
                    }
                ]
            }
        resposta.iter_content.return_value = [raw if raw is not None else json.dumps(dados).encode()]
        return resposta

    @patch('app.modules.tutor_ia.services.gemini_service.requests.post')
    def test_payload_minimo_extracao_final_sem_output_text_e_fechamento(self, post):
        resposta = self.resposta()
        post.return_value = resposta
        self.assertEqual(self.cliente.gerar(ENTRADA, 'instrução'), TEXTO)
        post.assert_called_once()
        args, kwargs = post.call_args
        self.assertEqual(args, (ENDPOINT,))
        self.assertEqual(kwargs['headers'], {'x-goog-api-key': 'chave-sintetica'})
        self.assertEqual(kwargs['timeout'], (5, 30))
        self.assertFalse(kwargs['allow_redirects'])
        self.assertTrue(kwargs['stream'])
        payload = kwargs['json']
        self.assertEqual(
            set(payload),
            {
                'model',
                'system_instruction',
                'input',
                'store',
                'generation_config'
            }
        )
        self.assertIs(payload['store'], False)
        self.assertEqual(json.loads(payload['input']), ENTRADA)
        self.assertEqual(payload['generation_config']['max_output_tokens'], 4096)
        resposta.__exit__.assert_called_once()

    @patch('app.modules.tutor_ia.services.gemini_service.requests.post')
    def test_erros_sanitizados_sem_retries_e_fechamento(self, post):
        for erro, codigo in (
            (requests.Timeout('segredo'), 'tutor_timeout'),
            (
                requests.ConnectionError(ReadTimeoutError(
                    None,
                    ENDPOINT,
                    'segredo'
                )),
                'tutor_timeout'
            ),
            (requests.ConnectionError('segredo'), 'tutor_provedor_indisponivel'),
            (requests.RequestException('segredo'), 'tutor_provedor_indisponivel')
        ):
            post.reset_mock()
            post.side_effect = erro
            with self.assertRaises(TutoriaError) as cm:
                self.cliente.gerar(ENTRADA, 'instrução')
            self.assertEqual(cm.exception.codigo, codigo)
            self.assertNotIn('segredo', str(cm.exception))
            post.assert_called_once()
        post.side_effect = None
        for status in (301, 400, 429, 500):
            resposta = self.resposta(status=status)
            post.return_value = resposta
            with self.assertRaises(TutoriaError) as cm:
                self.cliente.gerar(ENTRADA, 'instrução')
            self.assertEqual(cm.exception.codigo, 'tutor_provedor_indisponivel')
            resposta.__exit__.assert_called_once()
            resposta.iter_content.assert_not_called()
        for raw in (b'invalid', b'\xff', b'x'*(MAX_BYTES+1)):
            resposta = self.resposta(raw=raw)
            post.return_value = resposta
            with self.assertRaises(TutoriaError) as cm:
                self.cliente.gerar(ENTRADA, 'instrução')
            self.assertEqual(cm.exception.codigo, 'tutor_resposta_invalida')
            resposta.__exit__.assert_called_once()
        resposta = self.resposta()
        resposta.iter_content.side_effect = requests.Timeout()
        post.return_value = resposta
        with self.assertRaises(TutoriaError):
            self.cliente.gerar(ENTRADA, 'instrução')
        resposta.__exit__.assert_called_once()

    def test_configuracao_opcional_e_esquemas_invalidos(self):
        for config in (
            {},
            {'habilitado': True},
            {'habilitado': True, 'chave': 'x', 'modelo': ''},
            {'habilitado': True, 'chave': None},
            {'habilitado': True, 'chave': ' '}
        ):
            service = GeminiService(**config)
            self.assertFalse(service.disponivel)
            with self.assertRaises(TutoriaError) as cm:
                service.gerar(ENTRADA, 'instrução')
            self.assertEqual(cm.exception.status_code, 503)
        for dados in (
            None,
            [],
            {},
            {'status': 'blocked'},
            {'status': 'in_progress'},
            {'status': 'completed', 'steps': None},
            {'status': 'completed', 'steps': [None]},
            {'status': 'completed', 'steps': []},
            *({'status': 'completed', 'steps': [{'type': 'model_output', 'content': conteudo}]}
                for conteudo in (
                    None,
                    [],
                    [None],
                    [{'type': 'text', 'text': None}],
                    [{
                        'type': 'text',
                        'text': ''
                    }],
                    [{
                        'type': 'thought',
                        'text': 'privado'
                    }]
                ))
        ):
            with self.assertRaises(TutoriaError):
                GeminiService._extrair(dados)


class LimiteTutoriaTest(unittest.TestCase):
    def test_janela_expiracao_capacidade_e_retry_after(self):
        instante = [0]
        limite = LimiteTutoria(lambda: instante[0], capacidade=2)
        for _ in range(4):
            limite.reservar(1)
            limite.liberar(1)
        instante[0] = 10.2
        with self.assertRaises(TutoriaError) as cm:
            limite.reservar(1)
        self.assertEqual(cm.exception.retry_after, 50)
        limite.reservar(2)
        limite.liberar(2)
        with self.assertRaises(TutoriaError):
            limite.reservar(3)
        instante[0] = 60
        limite.reservar(1)
        limite.liberar(1)
        self.assertEqual(limite._contas[1].tentativas, 1)
        instante[0] = 121
        limite.reservar(3)
        self.assertEqual(set(limite._contas), {3})

    def test_reservas_concorrentes_mesma_conta_e_duas_globais(self):
        for contas, admitidas in (([1]*8, 1), (list(range(8)), 2)):
            limite = LimiteTutoria()
            barreira = Barrier(8)

            def tentar(id_):
                barreira.wait(timeout=5)
                try:
                    limite.reservar(id_)
                    return 1
                except TutoriaError as erro:
                    self.assertEqual((erro.status_code, erro.retry_after), (429, 1))
                    return 0
            with ThreadPoolExecutor(8) as pool:
                self.assertEqual(sum(pool.map(tentar, contas)), admitidas)
            for id_ in contas:
                limite.liberar(id_)
            self.assertEqual(limite._ativas, 0)
            limite.liberar('ausente')


class TutoriaComposicaoTest(unittest.TestCase):
    @patch('requests.post', side_effect=AssertionError('Factory não faz HTTP'))
    @patch('sqlalchemy.engine.Engine.connect', side_effect=AssertionError('Factory não conecta'))
    def test_clientes_limites_independentes_e_sem_configuracao(self, connect, post):
        a, b = create_app(TestConfig), create_app(TestConfig)
        sa, sb = a.extensions['servicos'].gerar_tutoria, b.extensions['servicos'].gerar_tutoria
        self.assertIsNot(sa, sb)
        self.assertIsNot(sa._gerador, sb._gerador)
        self.assertIsNot(sa._limite, sb._limite)
        self.assertFalse(sa._gerador.disponivel)
        connect.assert_not_called()
        post.assert_not_called()

    def test_permissao_uso_encerra_leitura_inclusive_negativa(self):
        with patch(
            'app.transaction_manager.TransactionManager.executar',
            side_effect=lambda fn: fn()
        ) as tx, \
                patch.object(PrivacidadeRepository, 'bloquear_usuario'), \
                patch.object(PrivacidadeRepository, 'ultimas', return_value={'uso': None}):
            with self.assertRaises(AutenticacaoError) as cm:
                ValidarPermissaoTutoriaService.executar(1)
            self.assertEqual(cm.exception.codigo, 'termos_uso_pendentes')
            tx.assert_called_once()


class TutoriaControllerUnitTest(unittest.TestCase):
    def test_headers_de_limite_erro_interno_e_logs_sanitizados(self):
        from flask import g
        app = create_app(TestConfig)
        for erro, status, codigo in (
            (TutoriaError('Aguarde.', 429, 'limite_tutoria', 12), 429, 'limite_tutoria'),
            (RuntimeError('segredo-sentinela-duvida'), 500, 'erro_interno')
        ):
            with app.test_request_context('/api/tutoria', method='POST', json=ENTRADA), \
                    patch.object(
                        app.extensions['servicos'].gerar_tutoria,
                        'executar',
                        side_effect=erro
                    ), \
                    patch.object(app.logger, 'error') as logger:
                g.auth_sessao = SimpleNamespace(usuario_id=9)
                resposta, codigo_http = TutoriaController.gerar()
                self.assertEqual((codigo_http, resposta.json['codigo']), (status, codigo))
                self.assertNotIn('segredo-sentinela', resposta.get_data(as_text=True))
                self.assertNotIn('segredo-sentinela', str(logger.call_args))
                if status == 429:
                    self.assertEqual(resposta.headers['Retry-After'], '12')
