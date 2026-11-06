"""Duas leituras válidas exercitam os mesmos Services sem MySQL."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from app import create_app
from app.services.listar_catalogo_admin_service import ListarMateriasAdminService, ListarAssuntosAdminService
from tests.unit.test_config_and_app import TestConfig


class CatalogoEmLista:
    def __init__(self, linhas):
        self.linhas = linhas

    def listar(self, filtros, pagina, limite):
        linhas = [r for r in self.linhas if
                  (not filtros['busca'] or filtros['busca'].lower() in r['nome'].lower()) and
                  all(not filtros.get(k) or r[k] == filtros[k] for k in ('status', 'area_enem_id', 'materia_id'))]
        linhas.sort(key=lambda r: (r['nome'], r['id']))
        return deepcopy(linhas[(pagina-1)*limite:pagina*limite]), len(linhas)


class CatalogoIndexado:
    def __init__(self, linhas):
        self.por_id = {r['id']: r for r in linhas}

    def listar(self, filtros, pagina, limite):
        ids = set(self.por_id)
        for chave in ('status', 'area_enem_id', 'materia_id'):
            if filtros.get(chave):
                ids &= {i for i, r in self.por_id.items() if r[chave] == filtros[chave]}
        if filtros['busca']:
            ids &= {i for i, r in self.por_id.items() if filtros['busca'].lower() in r['nome'].lower()}
        linhas = sorted((self.por_id[i] for i in ids), key=lambda r: (r['nome'], r['id']))
        return deepcopy(linhas[(pagina-1)*limite:pagina*limite]), len(linhas)


def registros():
    area = dict(id=4, nome='Matemática', codigo='matematica', ordem=4)
    materia = dict(id=7, nome='Álgebra', descricao=None, area_enem_id=4, status='ativa',
                   criado_em='2026-11-06T10:00:00', atualizado_em=None)
    return [dict(materia, id=i, nome=f'Álgebra {i}', nome_normalizado=f'álgebra {i}', materia_id=7,
                 area_enem=area, materia=materia, assuntos=2, questoes=i)
            for i in (3, 1, 2)] + [dict(materia, id=9, nome='Física', nome_normalizado='física',
                materia_id=8, area_enem=area, materia=materia, assuntos=0, questoes=0, status='inativa')]


class SubstituicaoCatalogoTest(unittest.TestCase):
    def test_dois_adaptadores_mesma_paginacao_filtros_e_representacao(self):
        for service in (ListarMateriasAdminService, ListarAssuntosAdminService):
            resultados = []
            for adapter in (CatalogoEmLista, CatalogoIndexado):
                consulta = service(adapter(registros()))
                filtros = {'busca': ' Álgebra ', 'status': 'ativa', 'area_enem_id': '4',
                           'pagina': '2', 'por_pagina': '2'}
                if service is ListarAssuntosAdminService:
                    filtros['materia_id'] = '7'
                r = consulta.executar(filtros)
                self.assertEqual([i['id'] for i in r['itens']], [3])
                self.assertEqual((r['total_itens'], r['total_paginas']), (3, 2))
                self.assertEqual(r['itens'][0]['criado_em'], '2026-11-06T10:00:00')
                self.assertIsNone(r['itens'][0]['descricao'])
                self.assertEqual(consulta.executar({'busca': 'Inexistente'})['total_paginas'], 0)
                resultados.append(r)
            self.assertEqual(*resultados)

    def test_substituicao_explicita_somente_na_composicao_da_aplicacao(self):
        a, b = create_app(TestConfig), create_app(TestConfig)
        anterior = b.extensions['servicos'].materias_admin
        a.extensions['servicos'].materias_admin = ListarMateriasAdminService(CatalogoIndexado(registros()))
        with patch('app.auth_http.AutorizarService.executar'):
            r = a.test_client().get('/api/admin/materias?busca=Inexistente')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json['itens'], [])
        self.assertIs(b.extensions['servicos'].materias_admin, anterior)
