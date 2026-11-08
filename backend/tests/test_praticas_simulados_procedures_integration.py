"""Contratos, identidade ORM e transações de Práticas/Simulados no MySQL real."""
from datetime import datetime, timedelta
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event, get_ident
from uuid import uuid4

from sqlalchemy import Boolean, JSON, column, event, inspect, select, text

from app.extensions import db
from app.modules.praticas.repositories.pratica_repository import PraticaRepository as Praticas
from app.modules.simulados.repositories.simulado_repository import SimuladoRepository as Simulados
from app.modules.simulados.models.simulado import Simulado, SimuladoResposta, SimuladoVersaoItem, SimuladoTentativa
from app.modules.praticas.models.pratica_tentativa import PraticaTentativa
from app.modules.praticas.services.responder_pratica_service import ResponderPraticaService
from app.modules.simulados.services.iniciar_simulado_service import IniciarSimuladoService
from app.transaction_manager import TransactionManager
from tests.integration_support import MySQLIntegrationTestCase
from tests import test_simulados_integration as fixture


class PraticasSimuladosProceduresIntegrationTest(MySQLIntegrationTestCase):
    setUp = fixture.SimuladosIntegrationTest.setUp
    conta = fixture.SimuladosIntegrationTest.conta
    publicar = fixture.SimuladosIntegrationTest.publicar
    criar = fixture.SimuladosIntegrationTest.criar
    confirmar = fixture.SimuladosIntegrationTest.confirmar
    iniciar = fixture.SimuladosIntegrationTest.iniciar
    resposta = fixture.SimuladosIntegrationTest.resposta
    finalizar = fixture.SimuladosIntegrationTest.finalizar

    def test_ordem_em_empate_historicos_vazios_composicao_e_chave_por_dono(self):
        from tests.test_praticas_integration import PraticasIntegrationTest
        chave = str(uuid4())
        pratica = PraticasIntegrationTest.iniciar(self, chave).json
        alheia = self.outro.post('/api/aluno/praticas', json={
            'questao_versao_id': self.versao, 'chave_envio': chave}).json
        ids = [pratica['id'], PraticasIntegrationTest.iniciar(self).json['id']]
        for id_ in ids:
            self.assertEqual(PraticasIntegrationTest.responder(self, id_).status_code, 200)
        PraticasIntegrationTest.iniciar(self)  # Aberta não aparece no histórico.
        tentativas = []
        for _ in range(2):
            t = self.iniciar().json
            self.assertEqual(self.finalizar(t).status_code, 200)
            tentativas.append(t['id'])
        self.iniciar()  # Aberta também fica fora do histórico do Simulado.
        rascunho = self.criar(questao_versao_ids=self.versoes[::-1]).json
        with self.app.app_context():
            from app.core.relogio import agora_utc
            instante = agora_utc()
            db.session.execute(text('UPDATE pratica_tentativas SET respondida_em=:agora '
                'WHERE usuario_id=:dono AND estado=\'respondida\''), {'agora': instante, 'dono': self.usuario})
            db.session.execute(text('UPDATE simulado_tentativas SET finalizada_em=:agora '
                'WHERE usuario_id=:dono AND estado=\'finalizada\''), {'agora': instante, 'dono': self.usuario})
            db.session.commit()
            linhas, total = Praticas.historico(self.usuario, None, 1, 100)
            self.assertEqual(([r.id for r in linhas], total), (ids[::-1], 2))
            self.assertEqual(Praticas.historico(self.usuario, 2**31+1, 1, 20), ([], 0))
            self.assertEqual(Praticas.historico(self.outro_id, None, 1, 20), ([], 0))
            self.assertEqual(Praticas.por_chave(self.outro_id, chave).id, alheia['id'])
            self.assertEqual(Praticas.por_chave(self.usuario, chave).id, pratica['id'])
            linhas, total = Simulados.historico(self.usuario, 1, 100)
            self.assertEqual(([r.id for r in linhas], total), (tentativas[::-1], 2))
            self.assertEqual(Simulados.historico(self.outro_id, 1, 20), ([], 0))
            self.assertEqual(Simulados.historico(self.usuario, 2, 1)[0][0].id, tentativas[0])
            self.assertEqual([i.questao_versao_id for i in Simulados.itens(simulado_id=rascunho['id'])], self.versoes[::-1])
            self.assertEqual([i.questao_versao_id for i in Simulados.itens(simulado_id=rascunho['id'], versao_id=self.v)], self.versoes)
            lote = Simulados.itens_em_lote(simulado_ids=[rascunho['id'], rascunho['id']])
            self.assertEqual([i.questao_versao_id for i in lote[rascunho['id']]], self.versoes[::-1])
            self.assertEqual(Simulados.itens(), [])
            self.assertEqual(Simulados.itens(versao_id=2**31+1), [])
            self.assertEqual(Simulados.respostas(2**31+1), [])
            linhas, total = Simulados.listar(1, 100, 'rascunho')
            self.assertEqual(([s.id for s in linhas], total), ([rascunho['id']], 1))
            self.assertEqual(Simulados.listar(1, 20, "' OR 1=1 --"), ([], 0))

    def test_locks_recarregam_entidades_gerenciadas_e_rollback(self):
        from tests.test_praticas_integration import PraticasIntegrationTest
        p = PraticasIntegrationTest.iniciar(self).json
        tentativa = self.iniciar().json
        with self.app.app_context():
            pratica = db.session.get(PraticaTentativa, p['id'])
            simulado = db.session.get(Simulado, self.s['id'])
            t = db.session.get(SimuladoTentativa, tentativa['id'])
            r, i = Simulados.respostas(t.id)[0]
            with db.engine.begin() as outra:
                outra.execute(text("UPDATE pratica_tentativas SET materia_nome='Nome corrente' WHERE id=:id"), {'id': pratica.id})
                outra.execute(text('UPDATE simulados SET revisao=7 WHERE id=:id'), {'id': simulado.id})
                outra.execute(text('UPDATE simulado_tentativas SET revisao=7 WHERE id=:id'), {'id': t.id})
                outra.execute(text("UPDATE simulado_respostas SET alternativa='B' WHERE id=:id"), {'id': r.id})
            self.assertIs(Praticas.propria(self.usuario, pratica.id, True), pratica)
            self.assertIs(Praticas.por_chave(self.usuario, pratica.chave_envio, True), pratica)
            self.assertEqual(pratica.materia_nome, 'Nome corrente')
            self.assertIs(Simulados.bloquear(simulado.id), simulado)
            self.assertEqual(simulado.revisao, 7)
            self.assertIs(Simulados.propria(self.usuario, t.id, True), t)
            self.assertIs(Simulados.por_chave(self.usuario, t.chave_envio), t)
            self.assertIs(Simulados.andamento(self.usuario, self.v), t)
            self.assertIs(Simulados.andamentos_em_lote(self.usuario, [self.v, self.v])[self.v], t)
            self.assertEqual(Simulados.andamentos_em_lote(self.outro_id, [self.v]), {})
            self.assertEqual(t.revisao, 7)
            atual, item = Simulados.respostas(t.id, True)[0]
            self.assertIs(atual, r)
            self.assertIs(item, i)
            self.assertEqual(atual.alternativa, 'B')
            self.assertTrue(all(inspect(e).persistent for e in (pratica, simulado, t, r, i)))
            atual.alternativa = 'C'
            atual.salvar(confirmar=False)
            db.session.rollback()
            self.assertEqual(r.alternativa, 'B')
            self.assertIsNone(Praticas.por_chave(self.outro_id, pratica.chave_envio, True))
            self.assertIsNone(Simulados.por_chave(self.outro_id, t.chave_envio))
            self.assertIsNone(Simulados.andamento(self.outro_id, self.v))

    def test_responder_espera_lock_replay_e_rollback(self):
        from tests.test_praticas_integration import PraticasIntegrationTest
        p = PraticasIntegrationTest.iniciar(self).json
        with self.app.app_context():
            pratica = Praticas.propria(self.usuario, p['id'], True)
            chegou = Event()
            principal = get_ident()
            def observar(conexao, cursor, comando, parametros, contexto, executemany):
                if get_ident()!=principal and comando.startswith('CALL sp_pratica_propria'):
                    chegou.set()
            def responder():
                with self.app.app_context():
                    return ResponderPraticaService.executar(self.usuario, p['id'], {'alternativa': 'A'})
            pool = ThreadPoolExecutor(max_workers=1)
            event.listen(db.engine, 'before_cursor_execute', observar)
            try:
                futuro = pool.submit(responder)
                self.assertTrue(chegou.wait(10))
                self.assertFalse(futuro.done())
                self.assertIs(Praticas.por_chave(self.usuario, pratica.chave_envio, True), pratica)
                pratica.materia_nome = 'Alteração revertida'
                pratica.salvar(confirmar=False)
                db.session.rollback()
                self.assertTrue(futuro.result(timeout=10)['correta'])
                db.session.expire_all()
                self.assertEqual(Praticas.propria(self.usuario, p['id'], True).materia_nome, self.materia['nome'])
            finally:
                db.session.rollback()
                pool.shutdown(wait=True)
                event.remove(db.engine, 'before_cursor_execute', observar)

    def test_inicio_concorrente_chaves_distintas_tem_um_andamento(self):
        barreira = Barrier(2)
        def iniciar(_):
            with self.app.app_context():
                barreira.wait(timeout=10)
                return IniciarSimuladoService.executar(self.usuario,
                    {'simulado_versao_id': self.v, 'chave_envio': str(uuid4())})
        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(iniciar, range(2)))
        self.assertEqual(sorted(r[1] for r in resultados), [200, 201])
        self.assertEqual(resultados[0][0]['id'], resultados[1][0]['id'])

    def test_falha_mysql_apos_correcao_parcial_reverte_tudo(self):
        tentativa = self.iniciar().json
        self.assertEqual(self.resposta(tentativa).status_code, 200)
        self.assertEqual(self.resposta(tentativa, n=1, revisao=2).status_code, 200)
        with self.app.app_context():
            segundo = Simulados.respostas(tentativa['id'])[1][0].id
            db.session.remove()
            with db.engine.begin() as instalacao:
                instalacao.exec_driver_sql('CREATE TRIGGER tr_falha_correcao_014 BEFORE UPDATE ON simulado_respostas '
                    f"FOR EACH ROW BEGIN IF NEW.id={int(segundo)} AND NEW.correta IS NOT NULL THEN "
                    "SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Falha sintética após primeira correção'; END IF; END")
            try:
                self.assertEqual(self.finalizar(tentativa, revisao=3).status_code, 500)
                db.session.remove()
                self.assertTrue(all(r.correta is None for r, _ in Simulados.respostas(tentativa['id'])))
                t = Simulados.propria(self.usuario, tentativa['id'])
                self.assertEqual((t.estado, t.revisao, t.total), ('em_andamento', 3, None))
            finally:
                db.session.remove()
                with db.engine.begin() as limpeza:
                    limpeza.exec_driver_sql('DROP TRIGGER tr_falha_correcao_014')
        self.assertEqual(self.finalizar(tentativa, revisao=3).status_code, 200)

    def test_rotinas_ausentes_falham_sem_fallback_ou_detalhe_sql(self):
        from tests.test_praticas_integration import PraticasIntegrationTest
        pratica = PraticasIntegrationTest.iniciar(self).json
        tentativa = self.iniciar().json
        casos = [
            ('sp_pratica_propria', self.aluno, f"/api/aluno/praticas/{pratica['id']}"),
            ('sp_praticas_historico', self.aluno, '/api/aluno/praticas'),
            ('sp_simulados_listar', self.client, '/api/admin/simulados'),
            ('sp_simulado_respostas', self.aluno, f"/api/aluno/tentativas-simulado/{tentativa['id']}"),
        ]
        for nome, cliente, url in casos:
            with self.subTest(nome=nome), self.app.app_context():
                with db.engine.connect() as con:
                    ddl = con.exec_driver_sql('SHOW CREATE PROCEDURE '+nome).mappings().one()['Create Procedure']
                    with con.connection.driver_connection.cursor() as c:
                        c.execute('DROP PROCEDURE '+nome)
                try:
                    resposta = cliente.get(url)
                    self.assertEqual(resposta.status_code, 500)
                    self.assertEqual(set(resposta.json), {'erro'})
                    self.assertNotIn(nome, resposta.json['erro'])
                finally:
                    db.session.remove()
                    with db.engine.connect() as con:
                        with con.connection.driver_connection.cursor() as c:
                            c.execute(ddl)
                self.assertEqual(cliente.get(url).status_code, 200)

    def test_caracterizacao_paginas_lotes_dono_e_limites_utc(self):
        from tests.test_praticas_integration import PraticasIntegrationTest
        pratica = PraticasIntegrationTest.iniciar(self).json
        self.assertEqual(PraticasIntegrationTest.responder(self, pratica['id']).status_code, 200)
        tentativa = self.iniciar().json
        self.assertEqual(self.resposta(tentativa).status_code, 200)
        self.assertEqual(self.finalizar(tentativa, revisao=2).status_code, 200)
        with self.app.app_context():
            p = Praticas.propria(self.usuario, pratica['id'])
            self.assertIsInstance(p.correta, bool)
            self.assertIsInstance(p.respondida_em, datetime)
            self.assertEqual(Praticas.historico(self.usuario, self.assunto['id'], 2**31+1, 20), ([], 1))
            self.assertEqual([r.id for r in Praticas.fatos(self.usuario, p.respondida_em,
                p.respondida_em+timedelta(microseconds=1))], [p.id])
            self.assertEqual(Praticas.fatos(self.usuario, p.respondida_em-timedelta(seconds=1), p.respondida_em), [])
            self.assertIsNone(Praticas.propria(self.outro_id, p.id))
            self.assertEqual(Simulados.historico(self.usuario, 2**31+1, 20), ([], 1))
            self.assertEqual(Simulados.listar(2**31+1, 20, 'publicado')[0], [])
            itens = Simulados.itens_em_lote(versao_ids=[self.v, self.v, 2**31+1])[self.v]
            self.assertEqual([i.questao_versao_id for i in itens], self.versoes)
            self.assertEqual(Simulados.itens_em_lote(versao_ids=[]), {})
            self.assertEqual(Simulados.andamentos_em_lote(self.usuario, []), {})
            self.assertEqual(Simulados.titulos_em_lote([]), {})
            self.assertEqual(Simulados.titulos_em_lote([self.v, self.v]), {self.v: self.s['titulo']})
            t = Simulados.propria(self.usuario, tentativa['id'])
            self.assertIsInstance(t.percentual_acerto, Decimal)
            fatos = Simulados.fatos(self.usuario, t.finalizada_em, t.finalizada_em+timedelta(microseconds=1))
            self.assertEqual(len(fatos), 1)
            self.assertIs(fatos[0][2], t)
            self.assertEqual(Simulados.fatos(self.usuario, t.iniciada_em, t.finalizada_em), [])
            self.assertIsNone(Simulados.propria(self.outro_id, t.id))
            self.assertEqual(Simulados.fatos(self.outro_id, t.iniciada_em, t.finalizada_em+timedelta(seconds=1)), [])

    def test_call_tripla_tipos_identidade_leitura_corrente_rollback_e_drenagem(self):
        tentativa = self.iniciar().json
        with self.app.app_context():
            entidades = (SimuladoResposta, SimuladoVersaoItem, SimuladoTentativa)
            campos = ','.join(f'{alias}.{c.name} AS {alias}_{c.name}'
                for alias, entidade in zip(('r', 'i', 't'), entidades) for c in entidade.__table__.columns)
            with db.engine.begin() as instalacao:
                instalacao.exec_driver_sql('CREATE PROCEDURE sp_teste_tripla_014(IN p_id BIGINT UNSIGNED) '
                    'READS SQL DATA SQL SECURITY INVOKER BEGIN SELECT '+campos+
                    ",JSON_OBJECT('numero',7) AS dados,TRUE AS flag FROM simulado_respostas r "
                    'JOIN simulado_versao_itens i ON i.id=r.item_id '
                    'JOIN simulado_tentativas t ON t.id=r.tentativa_id WHERE t.id=p_id ORDER BY i.posicao FOR UPDATE; '
                    'SELECT 99 AS terminal_util; END')
            try:
                antiga = db.session.get(SimuladoTentativa, tentativa['id'])
                resposta = Simulados.respostas(antiga.id)[0][0]
                with db.engine.begin() as outra:
                    outra.execute(text('UPDATE simulado_tentativas SET revisao=7 WHERE id=:id'), {'id': antiga.id})
                    outra.execute(text("UPDATE simulado_respostas SET alternativa='B' WHERE id=:id"), {'id': resposta.id})
                comando = text('CALL sp_teste_tripla_014(:id)').columns(
                    *(c for e in entidades for c in e.__table__.columns), column('dados', JSON), column('flag', Boolean))
                def ler(id_):
                    resultado = db.session.execute(select(*entidades, column('dados', JSON), column('flag', Boolean))
                        .from_statement(comando).execution_options(populate_existing=True), {'id': id_})
                    try:
                        return resultado.all()
                    finally:
                        resultado.close()
                def operacao():
                    linhas = ler(antiga.id)
                    r, i, t, dados, flag = linhas[0]
                    self.assertIs(t, antiga)
                    self.assertIs(r, resposta)
                    self.assertEqual(t.revisao, 7)
                    self.assertEqual(r.alternativa, 'B')
                    self.assertTrue(all(inspect(e).persistent for e in (r, i, t)))
                    self.assertEqual(dados, {'numero': 7})
                    self.assertIs(flag, True)
                    self.assertIsInstance(t.iniciada_em, datetime)
                    r.alternativa = 'C'
                    r.salvar(confirmar=False)
                    self.assertEqual(ler(2**31+1), [])
                    self.assertEqual(db.session.execute(text('SELECT 7')).scalar_one(), 7)
                    raise RuntimeError('Reverter mutação participante')
                with self.assertRaisesRegex(RuntimeError, 'Reverter mutação'):
                    TransactionManager.executar(operacao)
                self.assertEqual(db.session.get(SimuladoResposta, resposta.id).alternativa, 'B')
            finally:
                db.session.remove()
                with db.engine.begin() as limpeza:
                    limpeza.exec_driver_sql('DROP PROCEDURE sp_teste_tripla_014')
