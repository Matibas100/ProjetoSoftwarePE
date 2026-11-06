import ast
import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

from app import create_app
from app.http_composition import servicos
from app.composition import compor
from tests.unit.test_config_and_app import TestConfig


class CompositionTest(unittest.TestCase):
    @patch('sqlalchemy.engine.Engine.connect', side_effect=AssertionError('Não conectar na factory'))
    def test_composicao_por_aplicacao_sem_conexao(self, connect):
        a, b = create_app(TestConfig), create_app(TestConfig)
        self.assertIsNot(a.extensions['servicos'], b.extensions['servicos'])
        self.assertIsNot(a.extensions['servicos'].materias_admin, b.extensions['servicos'].materias_admin)
        with a.app_context():
            self.assertIs(servicos(), a.extensions['servicos'])
        connect.assert_not_called()

    def test_contratos_independentes_de_infraestrutura(self):
        root = Path(__file__).resolve().parents[2] / 'app' / 'contracts'
        for path in root.glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf8'))):
                if isinstance(node, ast.ImportFrom):
                    self.assertTrue(node.module.startswith(('typing', 'datetime', 'contextlib', 'app.contracts')), path)
                if isinstance(node, ast.Import):
                    self.fail(f'Import não previsto no contrato: {path.name}')

    def test_nove_consultas_recebem_dependencias_obrigatorias(self):
        c = compor()
        nomes = ('materias_admin', 'assuntos_admin', 'questoes_por_assunto', 'questoes_aluno',
                 'simulados_aluno', 'historico_simulados', 'desempenho', 'dashboard_aluno', 'dashboard_admin')
        proibidos = ('flask', 'sqlalchemy', 'pymysql', 'app.models', 'app.repositories',
                     'app.extensions', 'app.composition', 'app.http_composition', 'app.contexto_leitura')
        for nome in nomes:
            service = getattr(c, nome)
            parametros = list(inspect.signature(type(service)).parameters.values())
            self.assertTrue(parametros)
            self.assertTrue(all(p.default is inspect.Parameter.empty for p in parametros))
            tree = ast.parse(Path(inspect.getfile(type(service))).read_text(encoding='utf8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse(node.module.startswith(proibidos), nome)
                if isinstance(node, ast.Name):
                    self.assertNotIn(node.id, ('current_app', 'db'), nome)
        self.assertIs(c.dashboard_aluno._diagnostico, c.desempenho)
        self.assertIs(c.gerar_plano._seletor._diagnostico, c.desempenho)
        self.assertIs(c.gerar_plano._seletor, c.recalcular_plano._seletor)
        self.assertIs(c.dashboard_aluno._escopos, c.desempenho._escopos)
        self.assertIs(c.dashboard_admin._escopos, c.desempenho._escopos)
