"""Fronteiras executáveis do ADR-010, sem banco ou leitura de .env."""
import ast
import importlib
from pathlib import Path
import unittest
from unittest.mock import patch

from app import create_app
from app.extensions import db
from tests.unit.test_config_and_app import TestConfig


APP = Path(__file__).resolve().parents[2] / 'app'
MODULOS = {
    'contas': 4,
    'conteudo': 7,
    'praticas': 1,
    'simulados': 7,
    'desempenho': 0,
    'plano_estudos': 2,
    'tutor_ia': 0
}
# Sete proprietários; Tutor acrescenta zero mappers.
MIGRADOS = tuple(MODULOS)


def importacoes(tree):
    """Inclui imports locais, aliases e carregamento dinâmico."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ''
            if node.level:
                yield '<relativo>'
            else:
                yield base
                yield from (base + '.' + alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            fn = node.func
            if (isinstance(fn, ast.Name) and fn.id == '__import__') or (
                isinstance(fn, ast.Attribute) and fn.attr == 'import_module'):
                yield '<dinamico>'
        elif isinstance(node, ast.Name) and node.id == '__import__':
            yield '<dinamico>'
        elif isinstance(node, ast.Attribute) and node.attr == '__import__':
            yield '<dinamico>'


def violacoes_fronteira(owner, tree):
    for name in importacoes(tree):
        if name in {'<relativo>', '<dinamico>'}:
            yield name
        if name.startswith('importlib'):
            yield name
        if name.startswith((
            'app.models',
            'app.services',
            'app.repositories',
            'app.controllers',
            'app.domain'
        )):
            yield name
        if name.startswith('app.modules.'):
            parts = name.split('.')
            if len(parts) >= 3 and parts[2] != owner and (
                len(parts) < 4 or parts[3] != 'api'):
                yield name


class ArquiteturaModularTest(unittest.TestCase):
    def test_detecta_imports_privados_inclusive_locais_e_dinamicos(self):
        for source in (
            'from app.modules.contas.models.usuario import Usuario',
            'def executar():\n from app.modules.contas import repositories',
            'import app.modules.contas.services as apelido',
            'import importlib\nimportlib.import_module("app.modules.contas.models")',
            'from importlib import import_module as carregar\ncarregar("app.modules.contas.models")',
            '__import__("app.modules.contas.models")'
        ):
            self.assertTrue(list(violacoes_fronteira('praticas', ast.parse(source))), source)
        self.assertFalse(list(violacoes_fronteira(
            'praticas',
            ast.parse(
                'from app.modules.conteudo.api import ConsultarVersaoElegivelService')
        )))

    def test_fronteiras_dos_modulos_concluidos(self):
        for owner in MIGRADOS:
            root = APP / 'modules' / owner
            for path in root.rglob('*.py'):
                with self.subTest(path=path.relative_to(APP)):
                    tree = ast.parse(path.read_text(encoding='utf-8'))
                    self.assertEqual(list(violacoes_fronteira(owner, tree)), [])
                    names = list(importacoes(tree))
                    for node in ast.walk(tree):
                        if isinstance(
                            node,
                            ast.ImportFrom
                        ) and node.module and node.module.startswith('app.modules.'):
                            parts = node.module.split('.')
                            if len(parts) == 4 and parts[2] != owner and parts[3] == 'api':
                                public = importlib.import_module(node.module).__all__
                                self.assertTrue(all(a.name in public for a in node.names))
                    if 'services' in path.parts or 'controllers' in path.parts:
                        self.assertFalse(any(n.startswith(('pymysql', 'app.extensions')) or (
                            n.startswith('sqlalchemy') and not n.startswith('sqlalchemy.exc')) for n in names))
                        self.assertFalse(any(isinstance(
                            n,
                            ast.Attribute
                        ) and n.attr == 'session' for n in ast.walk(tree)))
                    if 'controllers' in path.parts:
                        self.assertFalse(any('.models.' in n or '.repositories.' in n for n in names))
                        self.assertFalse(any(n.startswith('sqlalchemy') for n in names))
                    if 'services' in path.parts:
                        self.assertFalse(any(n.startswith((
                            'flask',
                            'app.composition',
                            'app.http_composition'
                        )) for n in names))
                        self.assertFalse(any(isinstance(
                            n,
                            ast.Name
                        ) and n.id == 'db' for n in ast.walk(tree)))
                        self.assertFalse(any(isinstance(n, ast.Attribute) and n.attr in {
                            'execute',
                            'exec_driver_sql',
                            'query',
                            'commit',
                            'rollback',
                            'flush'
                        } for n in ast.walk(tree)))
                    if 'domain' in path.parts:
                        self.assertFalse(any(n.startswith((
                            'flask',
                            'app.composition',
                            'app.extensions',
                            'sqlalchemy'
                        )) for n in names))
                    if path.name == 'routes.py':
                        self.assertFalse(any('.repositories' in n or '.models' in n or '.services' in n for n in names))
                        self.assertFalse(any(isinstance(
                            n,
                            (
                                ast.FunctionDef,
                                ast.Lambda,
                                ast.If
                            )
                        ) for n in ast.walk(tree)))
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ImportFrom):
                                self.assertTrue(node.module == 'flask' or node.module.startswith(
                                    f'app.modules.{owner}.controllers.'))
                                if node.module == 'flask':
                                    self.assertEqual([a.name for a in node.names], ['Blueprint'])
                            if isinstance(node, ast.Call):
                                fn = node.func
                                self.assertTrue((isinstance(
                                    fn,
                                    ast.Name
                                ) and fn.id in {
                                    'Blueprint',
                                    'getattr'
                                }) or (
                                    isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name)
                                    and fn.value.id == 'blueprint' and fn.attr == 'add_url_rule'))
                    if path.name == '__init__.py':
                        self.assertFalse(any(isinstance(
                            n,
                            (
                                ast.Import,
                                ast.ImportFrom,
                                ast.Call
                            )
                        ) for n in ast.walk(tree)))

    def test_apis_explicitas_sem_exportar_persistencia(self):
        for owner in MIGRADOS:
            api = importlib.import_module(f'app.modules.{owner}.api')
            self.assertIsInstance(api.__all__, (list, tuple))
            self.assertEqual(len(api.__all__), len(set(api.__all__)))
            for name in api.__all__:
                self.assertFalse(name.startswith('_'))
                obj = getattr(api, name)
                self.assertNotIn('Repository', getattr(obj, '__name__', ''))
                self.assertNotIn('.repositories.', getattr(obj, '__module__', ''))
                self.assertFalse(isinstance(obj, db.Model))
                self.assertFalse(isinstance(obj, type) and issubclass(obj, db.Model))
            tree = ast.parse(Path(api.__file__).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    self.assertNotIn('.models.', node.module or '')
                    for alias in node.names:
                        self.assertNotEqual(alias.name, '*')
                        if '.repositories.' in (node.module or '') or '.services.' in (node.module or ''):
                            self.assertTrue((alias.asname or alias.name).startswith('_'))

    @patch('sqlalchemy.engine.Engine.connect', side_effect=AssertionError('Factory não conecta'))
    def test_duas_factories_com_metadata_unica_e_composicao_independente(self, connect):
        a, b = create_app(TestConfig), create_app(TestConfig)
        self.assertIsNot(a.extensions['servicos'], b.extensions['servicos'])
        self.assertIs(a.extensions['sqlalchemy'], db)
        self.assertIs(b.extensions['sqlalchemy'], db)
        mappers = list(db.Model.registry.mappers)
        self.assertEqual(len(mappers), 21)
        self.assertEqual(len({m.local_table.name for m in mappers}), 21)
        self.assertEqual(len(db.metadata.tables), 21)
        for owner in MIGRADOS:
            classes = [m.class_ for m in mappers if m.class_.__module__.startswith(f'app.modules.{owner}.models.')]
            self.assertEqual(len(classes), MODULOS[owner])
            self.assertIn(f'api.{owner}', a.blueprints)
        self.assertEqual(
            sorted((r.rule, sorted(r.methods)) for r in a.url_map.iter_rules()),
            sorted((r.rule, sorted(r.methods)) for r in b.url_map.iter_rules())
        )
        self.assertEqual(len(a.before_request_funcs[None]), 1)
        self.assertEqual(len(a.after_request_funcs[None]), 2)  # CORS e cache.
        self.assertEqual(set(a.cli.commands), {'criar-administrador', 'limpar-autenticacao'})
        connect.assert_not_called()

    def test_nucleo_e_contratos_independentes_de_negocio(self):
        for root in (APP / 'core', APP / 'contracts'):
            for path in root.glob('*.py'):
                names = list(importacoes(ast.parse(path.read_text(encoding='utf-8'))))
                self.assertFalse(
                    any(n.startswith((
                        'app.modules',
                        'app.domain',
                        'app.composition',
                        'flask'
                    )) for n in names),
                    path
                )

    def test_pastas_globais_sem_implementacoes_apos_transicao(self):
        if set(MIGRADOS) == set(MODULOS):
            for name in ('controllers', 'services', 'repositories', 'domain'):
                self.assertFalse(list((APP / name).rglob('*.py')))
            self.assertEqual(
                {p.name for p in (APP / 'models').glob('*.py')},
                {
                    '__init__.py',
                    'crud_mixin.py'
                }
            )
