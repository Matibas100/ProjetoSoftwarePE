"""Caracterização dos contratos HTTP antes/depois da troca por procedures."""
from uuid import uuid4
from sqlalchemy import text
from app.extensions import db
from app.core.procedures_mysql import executar_resultados, conferir_resultados

from tests.integration_support import MySQLIntegrationTestCase
from tests import test_catalogo_admin_integration as fixture


class ConsultasCatalogoCaracterizacaoTest(MySQLIntegrationTestCase):
    _subject = fixture.CatalogoAdminIntegrationTest._subject
    _question = fixture.CatalogoAdminIntegrationTest._question

    def test_rotina_ausente_ou_formato_incompativel_nao_tem_fallback(self):
        for rotina, url, substituir in [
            ('sp_materias_admin', '/api/admin/materias', True),
            ('sp_assuntos_admin', '/api/admin/assuntos', False),
            ('sp_questoes_admin', '/api/admin/questoes', False),
            ('sp_conteudo_contagens_dashboard', '/api/admin/dashboard', True),
            ('sp_simulados_contagens_dashboard', '/api/admin/dashboard', False),
        ]:
            with self.subTest(rotina=rotina), self.app.app_context():
                with db.engine.connect() as con:
                    ddl = con.exec_driver_sql('SHOW CREATE PROCEDURE ' + rotina).mappings().one()['Create Procedure']
                    with con.connection.driver_connection.cursor() as c:
                        c.execute('DROP PROCEDURE ' + rotina)
                        if substituir:
                            c.execute('CREATE PROCEDURE ' + rotina + '() READS SQL DATA '
                                'SQL SECURITY INVOKER SELECT 1 AS coluna_incompativel')
                try:
                    resposta = self.client.get(url)
                    self.assertEqual(resposta.status_code, 500)
                    self.assertEqual(set(resposta.json), {'erro'})
                    self.assertNotIn(rotina, resposta.json['erro'])
                finally:
                    # O app_context externo da fixture mantém a sessão da
                    # requisição viva; libera seu metadata lock antes do DDL.
                    db.session.remove()
                    with db.engine.connect() as con:
                        with con.connection.driver_connection.cursor() as c:
                            c.execute('DROP PROCEDURE IF EXISTS ' + rotina)
                            c.execute(ddl)
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_falha_mysql_apos_primeiro_resultado_libera_pool(self):
        with self.app.app_context():
            with db.engine.begin() as instalacao:
                instalacao.exec_driver_sql('CREATE PROCEDURE sp_teste_erro() READS SQL DATA '
                    "SQL SECURITY INVOKER BEGIN SELECT 1 AS primeiro; SIGNAL SQLSTATE '45000' "
                    "SET MESSAGE_TEXT='Falha sintética'; END")
            try:
                with db.engine.connect() as conexao:
                    with self.assertRaises(Exception):
                        executar_resultados(conexao, 'CALL sp_teste_erro()')
                with db.engine.connect() as conexao:
                    self.assertEqual(conexao.exec_driver_sql('SELECT 9').scalar_one(), 9)
            finally:
                with db.engine.begin() as limpeza:
                    limpeza.exec_driver_sql('DROP PROCEDURE sp_teste_erro')

    def test_helper_participante_vazio_multiplos_resultados_e_rollback(self):
        with self.app.app_context():
            with db.engine.begin() as instalacao:
                instalacao.exec_driver_sql('CREATE PROCEDURE sp_teste_resultados() '
                    'READS SQL DATA SQL SECURITY INVOKER BEGIN '
                    'SELECT id FROM materias WHERE 1=0; SELECT 7 AS total; END')
            try:
                with db.engine.connect() as conexao:
                    transacao = conexao.begin()
                    nome = 'Rollback ' + uuid4().hex
                    conexao.execute(text('INSERT INTO materias(nome,area_enem_id) VALUES(:nome,4)'),
                        {'nome': nome})
                    resultados = executar_resultados(conexao, 'CALL sp_teste_resultados()')
                    conferir_resultados(resultados, [('id',), ('total',)])
                    self.assertEqual(resultados, [[], [{'total': 7}]])
                    self.assertEqual(conexao.exec_driver_sql('SELECT 9').scalar_one(), 9)
                    self.assertTrue(transacao.is_active)
                    transacao.rollback()
                self.assertEqual(db.session.execute(text('SELECT COUNT(*) FROM materias WHERE nome=:nome'),
                    {'nome': nome}).scalar_one(), 0)
            finally:
                with db.engine.begin() as limpeza:
                    limpeza.exec_driver_sql('DROP PROCEDURE sp_teste_resultados')

    def test_listagens_campos_nulos_busca_filtros_totais_e_pagina_grande(self):
        nome = 'Álgebra_% ' + uuid4().hex[:12]
        materia = self.client.post('/api/materias', json={
            'nome': nome, 'area_enem_id': 4}).json
        assunto = self._subject(materia['id'], nome)
        questao = self._question(assunto['id'])
        # Uma segunda Questão prova que JOIN não multiplica assuntos/contagens.
        self._question(assunto['id'])
        casos = [
            ('materias', {'busca': nome, 'area_enem_id': 4, 'status': 'ativa'},
             materia, {'assuntos': 1, 'questoes': 2}),
            ('assuntos', {'busca': nome, 'materia_id': materia['id'],
                          'area_enem_id': 4, 'status': 'ativa'},
             assunto, {'questoes': 2, 'resumos': None}),
            ('questoes', {'assunto_id': assunto['id'], 'materia_id': materia['id'],
                         'area_enem_id': 4, 'status': 'rascunho', 'dificuldade': 'facil'},
             questao, {}),
        ]
        for recurso, filtros, esperado, extras in casos:
            url = '/api/admin/' + recurso
            resposta = self.client.get(url, query_string=filtros)
            self.assertEqual(resposta.status_code, 200, resposta.json)
            dados = resposta.json
            item = next(i for i in dados['itens'] if i['id'] == esperado['id'])
            for campo, valor in {**esperado, **extras}.items():
                self.assertEqual(item[campo], valor, (recurso, campo))
            self.assertEqual(item['area_enem']['id'], 4)
            if recurso != 'materias':
                self.assertEqual(item['materia'], materia)
            for pagina in [2, 2**31 + 1]:
                vazia = self.client.get(url, query_string={**filtros,
                    'pagina': pagina, 'por_pagina': 100}).json
                self.assertEqual(vazia['itens'], [])
                self.assertEqual(vazia['total_itens'], dados['total_itens'])
            ausente = self.client.get(url, query_string={**filtros,
                'area_enem_id': 2**31 + 1}).json
            self.assertEqual((ausente['itens'], ausente['total_itens']), ([], 0))
            self.assertEqual(self.app.test_client().get(url).status_code, 401)

    def test_questoes_busca_literal_e_catalogo_like(self):
        nome = 'Caracterização ' + uuid4().hex[:12]
        materia = self.client.post('/api/materias', json={
            'nome': nome, 'area_enem_id': 4, 'descricao': None}).json
        assunto = self._subject(materia['id'], nome)
        q = self._question(assunto['id'])
        texto = "Acento á 50%_ / ' \\"
        self.assertEqual(self.client.put('/api/questoes/' + str(q['id']),
            json={'revisao': 1, 'enunciado': texto}).status_code, 200)
        for busca in ['%', '_', "'", '/', '\\', 'á']:
            r = self.client.get('/api/admin/questoes', query_string={
                'busca': busca, 'assunto_id': assunto['id']})
            self.assertEqual(r.status_code, 200)
            self.assertEqual([i['id'] for i in r.json['itens']], [q['id']])
        for recurso in ['materias', 'assuntos']:
            r = self.client.get('/api/admin/' + recurso, query_string={
                'busca': nome[:5] + '%', 'area_enem_id': 4})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json['itens'])
        r = self.client.get('/api/admin/questoes', query_string={
            'busca': "' OR 1=1 --", 'assunto_id': assunto['id']})
        self.assertEqual((r.json['itens'], r.json['total_itens']), ([], 0))
