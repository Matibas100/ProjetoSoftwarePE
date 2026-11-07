"""Casos de uso dependem dos colaboradores recebidos, sem banco."""
from datetime import datetime
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from contextlib import contextmanager
from copy import deepcopy

from app.modules.praticas.services.listar_questoes_aluno_service import ListarQuestoesAlunoService
from app.modules.simulados.services.listar_simulados_aluno_service import ListarSimuladosAlunoService
from app.modules.simulados.services.listar_historico_simulados_service import ListarHistoricoSimuladosService
from app.modules.desempenho.services.consultar_desempenho_service import ConsultarDesempenhoService
from app.modules.desempenho.services.dashboard_service import ConsultarDashboardAlunoService, ConsultarDashboardAdminService
from app.exceptions import DadosInvalidosError


class EscoposMemoria:
    def __init__(self):
        self.contexto = SimpleNamespace(instante=datetime(2026, 11, 6, 10))
        self.abertos = self.fechados = 0

    @contextmanager
    def usar(self, contexto=None, instante=None):
        if contexto is not None:
            yield contexto
        else:
            self.abertos += 1
            try:
                yield self.contexto
            finally:
                self.fechados += 1


class MetricasPrecalculadas:
    def agregar(self, contexto, usuario_id, inicio, fim):
        return ({'total_respostas': 3, 'acertos': 1, 'pratica': 2, 'simulado': 1}, [], [])


class MetricasPorFatos:
    def agregar(self, contexto, usuario_id, inicio, fim):
        fatos = [('pratica', True), ('pratica', False), ('simulado', False)]
        return ({'total_respostas': len(fatos), 'acertos': sum(c for _, c in fatos),
                 'pratica': sum(t == 'pratica' for t, _ in fatos),
                 'simulado': sum(t == 'simulado' for t, _ in fatos)}, [], [])


class ConsultasCompostasTest(unittest.TestCase):
    def test_questoes_seguras_paginadas_sem_transformacao_orm(self):
        consulta = Mock()
        dados = [{'questao_versao_id': 8, 'enunciado': 'Texto'}]
        consulta.listar.return_value = dados, 3
        r = ListarQuestoesAlunoService(consulta).executar({'pagina': '2', 'por_pagina': '2', 'assunto_id': '7'})
        self.assertEqual(r['itens'], dados)
        self.assertEqual(r['total_paginas'], 2)
        consulta.listar.assert_called_once_with({'assunto_id': 7, 'materia_id': None}, 2, 2)
        self.assertFalse({'resposta_correta', 'explicacao'} & r['itens'][0].keys())

    def test_catalogo_simulados_decide_disponibilidade_e_usa_lotes(self):
        consulta, elegibilidade = Mock(), Mock()
        consulta.listar.return_value = ([{'id': i, 'simulado_versao_id': i + 10, 'titulo': str(i)} for i in range(3)], 3)
        consulta.composicoes.return_value = {10: [1, 2], 11: [1, 3]}
        consulta.andamentos.return_value = {10: 99}
        elegibilidade.executar.return_value = {1: {}, 2: {}}
        r = ListarSimuladosAlunoService(consulta, elegibilidade).executar(7, {})
        self.assertEqual([i['disponivel'] for i in r['itens']], [True, False, False])
        self.assertEqual([i['tentativa_em_andamento_id'] for i in r['itens']], [99, None, None])
        consulta.composicoes.assert_called_once_with([10, 11, 12])
        consulta.andamentos.assert_called_once_with(7, [10, 11, 12])
        elegibilidade.executar.assert_called_once_with([1, 2, 1, 3])

    def test_historico_proprio_recebe_resultado_persistido(self):
        consulta = Mock()
        dados = [{'id': 8, 'simulado_versao_id': 10, 'titulo': 'Título histórico',
                  'resultado': {'finalizada_em': '2026-11-06T10:00:00Z', 'acertos': 1}}]
        consulta.listar.return_value = dados, 1
        r = ListarHistoricoSimuladosService(consulta).executar(7, {})
        self.assertEqual(r['itens'], dados)
        consulta.listar.assert_called_once_with(7, 1, 20)

    def test_metricas_intercambiaveis_e_contexto_opaco_externo(self):
        resultados = []
        for consulta in (MetricasPrecalculadas(), MetricasPorFatos()):
            escopos = EscoposMemoria()
            service = ConsultarDesempenhoService(consulta, escopos)
            r = service.executar(7, contexto=escopos.contexto, instante=escopos.contexto.instante)
            self.assertEqual(r['geral']['percentual_acerto'], 33.33)
            self.assertEqual(r['geral']['estado_amostra'], 'amostra_pequena')
            self.assertEqual(r['base'], {'pratica': 2, 'simulado': 1})
            self.assertEqual((escopos.abertos, escopos.fechados), (0, 0))
            resultados.append(r)
        self.assertEqual(*resultados)

    def test_dashboard_compartilha_contexto_relogio_e_falha_completa(self):
        escopos, atividades = EscoposMemoria(), Mock()
        diagnostico = ConsultarDesempenhoService(MetricasPorFatos(), escopos)
        atividades.atividades.return_value = [dict(id=1, tipo='pratica', titulo='Assunto', ocorrido_em=escopos.contexto.instante),
                                             dict(id=2, tipo='simulado', titulo='Título', ocorrido_em=escopos.contexto.instante)]
        dashboard = ConsultarDashboardAlunoService(diagnostico, atividades, escopos)
        r = dashboard.executar(7, {})
        self.assertEqual((escopos.abertos, escopos.fechados), (1, 1))
        self.assertEqual(r['desempenho']['calculado_em'], '2026-11-06T10:00:00Z')
        self.assertEqual(r['ultimas_atividades'][1]['url'], '/aluno/simulado.html?tentativa_id=2')
        self.assertIs(atividades.atividades.call_args.args[0], escopos.contexto)
        atividades.atividades.side_effect = RuntimeError('Indisponível')
        with self.assertRaises(RuntimeError): dashboard.executar(7, {})
        self.assertEqual((escopos.abertos, escopos.fechados), (2, 2))

    def test_dashboard_admin_so_consulta_contagens_sem_identidade(self):
        escopos, contagens = EscoposMemoria(), Mock()
        contagens.administrativo.return_value = {'catalogo': {}, 'questoes': {}, 'simulados': {}, 'tentativas_simulado_finalizadas': 0}
        service = ConsultarDashboardAdminService(contagens, escopos)
        with self.assertRaises(DadosInvalidosError): service.executar({'usuario_id': 7})
        self.assertEqual(escopos.abertos, 0)
        r = service.executar({})
        self.assertEqual(r['tentativas_simulado_finalizadas'], 0)
        contagens.administrativo.assert_called_once_with(escopos.contexto)
