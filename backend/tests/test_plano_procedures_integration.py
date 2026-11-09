"""Caracterização do Plano e das entidades gerenciadas no MySQL real."""
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event, get_ident
from uuid import uuid4

from sqlalchemy import inspect, select, text

from app.extensions import db
from app.modules.plano_estudos.models.plano_estudo import PlanoEstudo as Plano, PlanoEstudoItem as Item
from app.modules.plano_estudos.repositories.plano_estudo_repository import PlanoEstudoRepository as Planos
from app.modules.conteudo.repositories.questao_repository import QuestaoRepository as Questoes
from tests.integration_support import MySQLIntegrationTestCase
from tests import test_planos_integration as fixture
from tests import sql_observer


class PlanoProceduresIntegrationTest(MySQLIntegrationTestCase):
    setUp = fixture.PlanosIntegrationTest.setUp
    conta = fixture.PlanosIntegrationTest.conta
    publicar = fixture.PlanosIntegrationTest.publicar
    base = fixture.PlanosIntegrationTest.base
    gerar = fixture.PlanosIntegrationTest.gerar
    recalcular = fixture.PlanosIntegrationTest.recalcular
    concluir = fixture.PlanosIntegrationTest.concluir
    url = fixture.PlanosIntegrationTest.url

    def test_caracterizacao_propriedade_tipos_vazios_e_rollback(self):
        self.base()
        chave = str(uuid4())
        resposta = self.gerar(chave)
        self.assertEqual(resposta.status_code, 201)
        p = resposta.json['plano']
        with self.app.app_context():
            plano = Planos.atual(self.usuario, True)
            self.assertIs(Planos.por_chave(self.usuario, chave), plano)
            itens = Planos.itens(plano.id)
            item, mesmo = Planos.item_proprio(self.usuario, itens[0].id)
            self.assertIs(mesmo, plano)
            self.assertIs(item, itens[0])
            self.assertIsInstance(plano.atual, bool)
            self.assertIsInstance(plano.periodo, dict)
            self.assertIsInstance(item.snapshot, dict)
            self.assertIsInstance(plano.gerado_em, datetime)
            self.assertIsNone(item.concluido_em)
            self.assertIsNone(Planos.item_proprio(self.outro_id, item.id))
            self.assertIsNone(Planos.por_chave(self.outro_id, chave))
            self.assertIsNone(Planos.atual(self.outro_id))
            self.assertEqual(Planos.itens(2**31+1), [])
            self.assertIsNone(Planos.item_proprio(self.usuario, 2**31+1))
            self.assertTrue(all(inspect(e).persistent for e in (plano, item)))
            item.estado, item.concluido_em = 'concluido', datetime(2026, 11, 8, 12, 0, 0, 123456)
            item.salvar(confirmar=False)
            db.session.rollback()
            self.assertEqual(Planos.itens(p['id'])[0].estado, 'pendente')
            self.assertEqual(Questoes.pares_elegiveis_plano([]), set())
            self.assertEqual(Questoes.pares_elegiveis_plano([self.assunto['id']]*2, True),
                {(self.assunto['id'], self.materia['id'])})
        self.assertEqual(self.gerar(chave).json, resposta.json)
        self.assertEqual(self.concluir(p['itens'][0]['id'], self.outro).status_code, 404)

    def test_prova_call_textual_join_corrente_identidade_mutacao_e_drenagem(self):
        self.base()
        p = self.gerar().json['plano']
        with self.app.app_context():
            engine = db.engine
            with engine.begin() as ddl:
                ddl.exec_driver_sql('CREATE PROCEDURE sp_teste_plano_join_015(IN p_id BIGINT UNSIGNED) '
                    'READS SQL DATA SQL SECURITY INVOKER '
                    'SELECT i.id AS i_id, i.plano_id AS i_plano_id, i.assunto_id AS i_assunto_id, '
                    'i.materia_id AS i_materia_id, i.posicao AS i_posicao, i.snapshot AS i_snapshot, '
                    'i.estado AS i_estado, i.concluido_em AS i_concluido_em, '
                    'p.id AS p_id, p.usuario_id AS p_usuario_id, p.geracao AS p_geracao, p.atual AS p_atual, '
                    'p.usuario_atual AS p_usuario_atual, p.periodo AS p_periodo, p.gerado_em AS p_gerado_em, '
                    'p.chave_envio AS p_chave_envio, p.operacao AS p_operacao, p.plano_anterior_id AS p_plano_anterior_id '
                    'FROM plano_estudo_itens i JOIN planos_estudo p ON p.id=i.plano_id WHERE i.id=p_id FOR UPDATE')
            try:
                item = db.session.get(Item, p['itens'][0]['id'])
                plano = db.session.get(Plano, p['id'])
                with engine.begin() as outra:
                    outra.execute(text("UPDATE plano_estudo_itens SET snapshot=JSON_OBJECT('corrente', true) WHERE id=:id"),
                        {'id': item.id})
                comando = text('CALL sp_teste_plano_join_015(:id)').columns(
                    *Item.__table__.columns, *Plano.__table__.columns)
                for id_, vazio in [(item.id, False), (2**31+1, True), (item.id, False)]:
                    resultado = db.session.execute(select(Item, Plano).from_statement(comando)
                        .execution_options(populate_existing=True), {'id': id_})
                    try:
                        linha = resultado.one_or_none()
                    finally:
                        resultado.close()
                    if vazio:
                        self.assertIsNone(linha)
                    else:
                        self.assertIs(linha[0], item)
                        self.assertIs(linha[1], plano)
                        self.assertEqual(item.snapshot, {'corrente': True})
                        self.assertIs(plano.atual, True)
                        self.assertIsInstance(plano.gerado_em, datetime)
                item.estado, item.concluido_em = 'concluido', datetime(2026, 11, 8, 12)
                item.salvar(confirmar=False)
                db.session.rollback()
                self.assertEqual(db.session.get(Item, item.id).estado, 'pendente')
                self.assertEqual(db.session.execute(text('SELECT 7')).scalar_one(), 7)
            finally:
                db.session.rollback()
                with engine.begin() as ddl:
                    ddl.exec_driver_sql('DROP PROCEDURE sp_teste_plano_join_015')

    def test_procedures_correntes_atualizam_mesma_entidade_e_revertem(self):
        self.base()
        p = self.gerar().json['plano']
        with self.app.app_context():
            plano = db.session.get(Plano, p['id'])
            item = db.session.get(Item, p['itens'][0]['id'])
            with db.engine.begin() as outra:
                outra.execute(text("UPDATE plano_estudo_itens SET snapshot=JSON_OBJECT('corrente',true) WHERE id=:id"),
                    {'id': item.id})
            corrente, mesmo = Planos.item_proprio(self.usuario, item.id)
            self.assertIs(corrente, item)
            self.assertIs(mesmo, plano)
            self.assertEqual(item.snapshot, {'corrente': True})
            self.assertIs(Planos.itens(plano.id)[0], item)
            plano.atual = False
            plano.salvar(confirmar=False)
            db.session.rollback()
            self.assertIs(Planos.atual(self.usuario, True), plano)
            self.assertIs(plano.atual, True)

    def test_eliminacao_contagens_varias_geracoes_expiracao_seletiva_e_rollback(self):
        from app.core.procedures_mysql import executar_resultados
        from app.core.relogio import agora_utc
        self.base()
        p = self.gerar().json['plano']
        self.concluir(p['itens'][0]['id'])
        novo = self.recalcular(p).json['plano']
        with self.app.app_context():
            outro = Plano(usuario_id=self.outro_id, geracao=1, atual=True, periodo={}, gerado_em=agora_utc(),
                chave_envio=str(uuid4()), operacao='gerar').salvar()
            plano = db.session.get(Plano, novo['id'])
            item = db.session.get(Item, p['itens'][0]['id'])
            Planos.bloquear_usuario(self.usuario)
            contagens, = executar_resultados(db.session.connection(),
                'CALL sp_eliminar_planos_proprios(%s)', (self.usuario,))
            self.assertEqual(contagens, [{'planos_eliminados': 2, 'itens_eliminados': 2}])
            db.session.rollback()
            self.assertEqual(Planos.itens(p['id'])[0].estado, 'concluido')
            Planos.bloquear_usuario(self.usuario)
            Planos.eliminar_planos_proprios(self.usuario)
            self.assertTrue(inspect(plano).expired)
            self.assertTrue(inspect(item).expired)
            self.assertFalse(inspect(outro).expired)
            self.assertIsNone(db.session.get(Plano, novo['id']))
            self.assertIsNone(db.session.get(Item, p['itens'][0]['id']))
            self.assertIs(db.session.get(Plano, outro.id), outro)
            db.session.rollback()
            self.assertIsNotNone(db.session.get(Plano, novo['id']))
            self.assertEqual(db.session.get(Item, p['itens'][0]['id']).estado, 'concluido')
            # Um item pode estar carregado sem sua geração no identity map.
            db.session.expunge_all()
            sozinho = db.session.get(Item, p['itens'][0]['id'])
            Planos.bloquear_usuario(self.usuario)
            Planos.eliminar_planos_proprios(self.usuario)
            self.assertTrue(inspect(sozinho).expired)
            db.session.rollback()

    def test_falta_de_routine_erro_http_seguro_sem_fallback_e_guard_precede_derivados(self):
        from tests.test_privacidade_integration import PrivacidadeIntegrationTest as Privacidade
        self.base()
        p = self.gerar().json['plano']
        for nome, path, body in [
            ('sp_plano_atual', self.url, None),
            ('sp_plano_itens', self.url, None),
            ('sp_pares_elegiveis_plano', self.url, None),
            ('sp_plano_por_chave', self.url+'/gerar', {'chave_envio': str(uuid4())}),
            ('sp_plano_item_proprio', self.url+f"/itens/{p['itens'][0]['id']}/concluir", {'confirmar': True}),
        ]:
            with self.subTest(nome=nome), self.app.app_context():
                engine = db.engine
                with engine.begin() as ddl:
                    original = ddl.exec_driver_sql('SHOW CREATE PROCEDURE '+nome).mappings().one()['Create Procedure']
                    ddl.exec_driver_sql('DROP PROCEDURE '+nome)
                try:
                    r = self.aluno.get(path) if body is None else self.aluno.post(path, json=body)
                    self.assertEqual(r.status_code, 500)
                    self.assertEqual(set(r.json), {'erro'})
                    self.assertNotIn(nome, str(r.json))
                finally:
                    db.session.remove()
                    with engine.begin() as ddl:
                        ddl.exec_driver_sql(original, execution_options={"no_parameters": True})
        self.privacy = Privacidade.privacy
        r, _ = Privacidade.decidir(self, 'revogar')
        self.assertEqual(r.status_code, 201)
        with self.app.app_context():
            comandos = []
            def observar(con, cursor, comando, parametros, contexto, executemany):
                comandos.append(comando)
            sql_observer.listen(db.engine, 'before_cursor_execute', observar)
            try:
                for path, body in [
                    (self.url, None), (self.url+'/gerar', {'chave_envio': str(uuid4())}),
                    (self.url+'/recalcular', {'chave_envio': str(uuid4()), 'plano_atual_id': p['id'], 'confirmar': True}),
                    (self.url+f"/itens/{p['itens'][0]['id']}/concluir", {'confirmar': True}),
                ]:
                    r = self.aluno.get(path) if body is None else self.aluno.post(path, json=body)
                    self.assertEqual(r.status_code, 403)
            finally:
                sql_observer.remove(db.engine, 'before_cursor_execute', observar)
            self.assertFalse(any('CALL sp_plano_' in s or 'CALL sp_desempenho_' in s or
                'CALL sp_pares_elegiveis_plano' in s for s in comandos))

    def test_elegibilidade_for_share_serializa_publicacao_e_transferencia(self):
        from app.modules.conteudo.services.gestao_questao_service import PublicarQuestaoService
        from app.modules.conteudo.services.transferir_assunto_service import TransferirAssuntoService
        self.assertEqual(self.client.put(self.qpath, json={'revisao': 1, 'enunciado': 'Nova publicação'}).status_code, 200)
        destino = self.client.post('/api/materias', json={'nome': 'Destino '+uuid4().hex, 'area_enem_id': 4}).json
        ator = self.client.get('/api/auth/sessao').json['usuario']['id']
        for tipo in ('publicar', 'transferir'):
            with self.subTest(tipo=tipo), self.app.app_context():
                self.assertEqual(Questoes.pares_elegiveis_plano([self.assunto['id']], True),
                    {(self.assunto['id'], self.materia['id'])})
                chegou, principal, engine = Event(), get_ident(), db.engine
                def observar(con, cursor, comando, parametros, contexto, executemany):
                    alvo = 'CALL sp_bloquear_questao' if tipo=='publicar' else 'CALL sp_bloquear_assunto'
                    if get_ident()!=principal and comando.startswith(alvo):
                        chegou.set()
                def executar():
                    with self.app.app_context():
                        if tipo=='publicar':
                            return PublicarQuestaoService.executar(self.questao['id'],
                                {'revisao': 2, 'confirmar': True, 'motivo': 'Publicação concorrente'}, ator)
                        return TransferirAssuntoService.executar(self.assunto['id'],
                            {'materia_destino_id': destino['id'], 'impacto_esperado': {'questoes': 1}})
                pool = ThreadPoolExecutor(1)
                sql_observer.listen(engine, 'before_cursor_execute', observar)
                try:
                    futuro = pool.submit(executar)
                    self.assertTrue(chegou.wait(timeout=10))
                    self.assertFalse(futuro.done())
                    db.session.rollback()
                    futuro.result(timeout=15)
                finally:
                    db.session.rollback()
                    pool.shutdown(wait=True)
                    sql_observer.remove(engine, 'before_cursor_execute', observar)
        with self.app.app_context():
            self.assertEqual(Questoes.pares_elegiveis_plano([self.assunto['id']], True), set())

    def test_revogacao_concorrente_com_conclusao_e_recalculo(self):
        from app.http_composition import servicos
        from app.modules.contas.domain.autenticacao import AutenticacaoError
        from app.modules.contas.models.usuario import Usuario
        from app.modules.plano_estudos.services.concluir_plano_item_service import ConcluirPlanoItemService
        from tests.test_privacidade_integration import PrivacidadeIntegrationTest as Privacidade
        self.privacy = Privacidade.privacy
        self.base()
        for tipo in ('recalcular', 'concluir'):
            if tipo == 'concluir':
                self.assertEqual(Privacidade.decidir(self, 'aceitar')[0].status_code, 201)
            p = self.gerar().json['plano']
            revisao = self.aluno.get(self.privacy).json['consentimento_plano']['registro']['id']
            barreira = Barrier(2)
            def agir():
                with self.app.app_context():
                    db.session.get(Usuario, self.usuario)
                    barreira.wait(timeout=10)
                    try:
                        if tipo=='concluir':
                            ConcluirPlanoItemService.executar(self.usuario, p['itens'][0]['id'], {'confirmar': True})
                            return 200
                        return servicos().recalcular_plano.executar(self.usuario,
                            {'chave_envio': str(uuid4()), 'plano_atual_id': p['id'], 'confirmar': True})[1]
                    except AutenticacaoError as erro:
                        return erro.status_code
            def revogar():
                with self.app.app_context():
                    db.session.get(Usuario, self.usuario)
                    barreira.wait(timeout=10)
                    return servicos().revogar_consentimento_plano.executar(self.usuario,
                        {'versao': '1.0', 'revisao': revisao, 'chave_envio': str(uuid4()), 'confirmar': True})[1]
            with ThreadPoolExecutor(2) as pool:
                acao, negativa = pool.submit(agir), pool.submit(revogar)
                self.assertIn(acao.result(timeout=20), (200 if tipo=='concluir' else 201, 403))
                self.assertEqual(negativa.result(timeout=20), 201)
            with self.app.app_context():
                self.assertIsNone(Planos.atual(self.usuario))
                self.assertEqual(db.session.execute(select(Plano).where(Plano.usuario_id==self.usuario)).scalars().all(), [])

    def test_falha_mysql_apos_troca_de_geracao_reverte_toda_escrita(self):
        self.base()
        p = self.gerar().json['plano']
        with self.app.app_context():
            engine = db.engine
            with engine.begin() as ddl:
                ddl.exec_driver_sql('CREATE TRIGGER falhar_item_plano_015 BEFORE INSERT ON plano_estudo_itens '
                    "FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Falha sintética após troca de geração'")
            try:
                resposta = self.recalcular(p)
                self.assertEqual(resposta.status_code, 500)
                self.assertEqual(set(resposta.json), {'erro'})
                self.assertNotIn('sintética', str(resposta.json))
                self.assertEqual(self.aluno.get(self.url).json['plano'], p)
                self.assertEqual(len(db.session.execute(select(Plano).where(Plano.usuario_id==self.usuario))
                    .scalars().all()), 1)
            finally:
                db.session.remove()
                with engine.begin() as ddl:
                    ddl.exec_driver_sql('DROP TRIGGER falhar_item_plano_015')
