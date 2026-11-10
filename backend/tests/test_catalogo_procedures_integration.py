"""Caracterização e participação ORM de CALL no MySQL real."""
from datetime import datetime
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from threading import Event, get_ident

from sqlalchemy import Boolean, JSON, column, event, inspect, select, text
from sqlalchemy.exc import DBAPIError

from app.extensions import db
from app.modules.conteudo.models.area_enem import AreaEnem
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.models.questao import Questao
from app.modules.conteudo.models.questao_versao import QuestaoVersao
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository
from app.modules.conteudo.repositories.questao_repository import QuestaoRepository
from app.modules.conteudo.repositories.consultas_questoes import ConsultaQuestoesElegiveisMySQL
from app.modules.conteudo.services.gestao_questao_service import PublicarQuestaoService
from app.modules.conteudo.services.transferir_assunto_service import TransferirAssuntoService
from app.transaction_manager import TransactionManager
from tests.integration_support import MySQLIntegrationTestCase
from tests import test_catalogo_admin_integration as fixture


class CatalogoProceduresIntegrationTest(MySQLIntegrationTestCase):
    _matter = fixture.CatalogoAdminIntegrationTest._matter
    _subject = fixture.CatalogoAdminIntegrationTest._subject
    _question = fixture.CatalogoAdminIntegrationTest._question

    def test_lotes_versoes_antigas_pagina_vazia_e_lista_segura(self):
        materia = self._matter()
        assunto = self._subject(materia['id'])
        questao = self._question(assunto['id'])
        url = f"/api/questoes/{questao['id']}"
        confirmacao = {'revisao': 1, 'confirmar': True, 'motivo': 'Versão para histórico'}
        antiga = self.client.post(url+'/publicar', json=confirmacao).json['versao_publicada_id']
        self.assertEqual(
            self.client.put(
                url,
                json={
                    'revisao': 1,
                    'enunciado': 'Outra versão'
                }
            ).status_code,
            200
        )
        atual = self.client.post(
            url+'/publicar',
            json={
                **confirmacao,
                'revisao': 2
            }
        ).json['versao_publicada_id']
        with self.app.app_context():
            versoes = QuestaoRepository.versoes(questao['id'])
            self.assertEqual([v.numero for v in versoes], sorted(v.numero for v in versoes))
            self.assertTrue(all(inspect(v).persistent for v in versoes))
            self.assertEqual(
                [v.id for v in QuestaoRepository.versoes_elegiveis([
                    atual,
                    atual,
                    2**31+1
                ])],
                [atual]
            )
            self.assertEqual(
                {v.id for v in QuestaoRepository.versoes_historicas([
                    antiga,
                    antiga,
                    atual
                ])},
                {
                    antiga,
                    atual
                }
            )
            for consulta in [
                QuestaoRepository.versoes_elegiveis,
                QuestaoRepository.versoes_historicas
            ]:
                self.assertEqual(consulta([]), [])
            linhas, total = QuestaoRepository.listar_elegiveis(
                {'assunto_id': assunto['id']},
                2**31+1,
                20
            )
            self.assertEqual((linhas, total), ([], 1))
            seguros, total = ConsultaQuestoesElegiveisMySQL().listar(
                {'assunto_id': assunto['id']},
                1,
                20
            )
            self.assertEqual(total, 1)
            self.assertEqual(seguros[0]['questao_versao_id'], atual)
            self.assertNotIn('resposta_correta', seguros[0])
            self.assertNotIn('explicacao', seguros[0])
            self.assertIs(
                QuestaoRepository.versao_elegivel(
                    atual,
                    bloquear=True
                ),
                db.session.get(
                    QuestaoVersao,
                    atual
                )
            )
            db.session.rollback()
        self.assertEqual(
            self.client.post(
                url+'/arquivar',
                json={
                    **confirmacao,
                    'revisao': 2
                }
            ).status_code,
            200
        )
        with self.app.app_context():
            self.assertIsNone(QuestaoRepository.versao_elegivel(atual))
            self.assertEqual(QuestaoRepository.versoes_elegiveis([antiga, atual]), [])
            self.assertEqual(
                {v.id for v in QuestaoRepository.versoes_historicas([
                    antiga,
                    atual
                ])},
                {
                    antiga,
                    atual
                }
            )

    def test_rotinas_013_ausentes_geram_erro_seguro_sem_fallback(self):
        materia = self._matter()
        assunto = self._subject(materia['id'])
        questao = self._question(assunto['id'])
        for rotina, url in [
            ('sp_areas_enem_ordenadas', '/api/areas-enem'),
            ('sp_versoes_questao', f"/api/questoes/{questao['id']}")
        ]:
            with self.subTest(rotina=rotina), self.app.app_context():
                with db.engine.connect() as con:
                    ddl = con.exec_driver_sql('SHOW CREATE PROCEDURE '+rotina).mappings().one()['Create Procedure']
                    with con.connection.driver_connection.cursor() as c:
                        c.execute('DROP PROCEDURE '+rotina)
                try:
                    resposta = self.client.get(url)
                    self.assertEqual(resposta.status_code, 500)
                    self.assertEqual(set(resposta.json), {'erro'})
                    self.assertNotIn(rotina, resposta.json['erro'])
                finally:
                    db.session.remove()
                    with db.engine.connect() as con:
                        with con.connection.driver_connection.cursor() as c:
                            c.execute(ddl)
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_locks_recarregam_identidade_e_conservam_ordem(self):
        origem, destino = self._matter(), self._matter()
        assunto = self._subject(origem['id'])
        questao = self._question(assunto['id'])
        with self.app.app_context():
            s = db.session.get(Assunto, assunto['id'])
            m = db.session.get(Materia, origem['id'])
            q = db.session.get(Questao, questao['id'])
            with db.engine.begin() as outra:
                outra.execute(
                    text('UPDATE assuntos SET materia_id=:id WHERE id=:s'),
                    {'id': destino['id'], 's': s.id}
                )
                outra.execute(
                    text("UPDATE materias SET descricao='Estado corrente' WHERE id=:id"),
                    {'id': m.id}
                )
                outra.execute(text('UPDATE questoes SET revisao=7 WHERE id=:id'), {'id': q.id})
            self.assertIs(CatalogoRepository.buscar_assunto_para_atualizacao(s.id), s)
            self.assertEqual(s.materia_id, destino['id'])
            materias = CatalogoRepository.buscar_materias_para_atualizacao([
                destino['id'],
                origem['id'],
                destino['id']
            ])
            self.assertEqual([r.id for r in materias], sorted([origem['id'], destino['id']]))
            self.assertIs(next(r for r in materias if r.id == m.id), m)
            self.assertEqual(m.descricao, 'Estado corrente')
            self.assertIs(QuestaoRepository.bloquear(q.id), q)
            self.assertEqual(q.revisao, 7)
            chamadas = []

            def observar(conexao, cursor, comando, parametros, contexto, executemany):
                if comando.startswith('CALL sp_bloquear'):
                    chamadas.append(comando.split('(')[0])
            event.listen(db.engine, 'before_cursor_execute', observar)
            try:
                classificacao = QuestaoRepository.bloquear_classificacao(s.id)
            finally:
                event.remove(db.engine, 'before_cursor_execute', observar)
            self.assertEqual(chamadas, ['CALL sp_bloquear_assunto', 'CALL sp_bloquear_materias'])
            self.assertEqual(classificacao[1].id, destino['id'])
            s.atualizar(confirmar=False, descricao='Reverter após lock')
            db.session.rollback()
            self.assertEqual(db.session.get(Assunto, s.id).descricao, assunto['descricao'])
            self.assertIsNone(QuestaoRepository.bloquear_classificacao(2**31+1))

    def test_transferencia_serializa_publicacao_em_outra_conexao(self):
        origem, destino = self._matter(), self._matter()
        assunto = self._subject(origem['id'])
        questao = self._question(assunto['id'])
        ator = self.client.get('/api/auth/sessao').json['usuario']['id']
        with self.app.app_context():
            CatalogoRepository.buscar_assunto_para_atualizacao(assunto['id'])
            chegou = Event()
            principal = get_ident()
            engine = db.engine

            def observar(conexao, cursor, comando, parametros, contexto, executemany):
                if get_ident() != principal and comando.startswith('CALL sp_bloquear_assunto'):
                    chegou.set()

            def publicar():
                with self.app.app_context():
                    return PublicarQuestaoService.executar(
                        questao['id'],
                        {'revisao': 1, 'confirmar': True, 'motivo': 'Publicação concorrente'},
                        ator
                    )
            pool = ThreadPoolExecutor(max_workers=1)
            event.listen(engine, 'before_cursor_execute', observar)
            try:
                futuro = pool.submit(publicar)
                self.assertTrue(chegou.wait(timeout=10))
                self.assertFalse(futuro.done())
                movido = TransferirAssuntoService.executar(
                    assunto['id'],
                    {'materia_destino_id': destino['id'], 'impacto_esperado': {'questoes': 1}}
                )
                self.assertEqual(movido['materia_id'], destino['id'])
                publicado = futuro.result(timeout=10)
                versao = db.session.get(QuestaoVersao, publicado['versao_publicada_id'])
                self.assertEqual(versao.materia_id, destino['id'])
            finally:
                db.session.rollback()
                pool.shutdown(wait=True)
                event.remove(engine, 'before_cursor_execute', observar)

    def test_falha_mysql_no_historico_reverte_transferencia_integral(self):
        origem, destino = self._matter(), self._matter()
        assunto = self._subject(origem['id'])
        with self.app.app_context():
            with db.engine.begin() as instalacao:
                instalacao.exec_driver_sql('CREATE TRIGGER tr_falha_transferencia_013 BEFORE INSERT '
                    "ON assunto_transferencias FOR EACH ROW SIGNAL SQLSTATE '45000' "
                    "SET MESSAGE_TEXT='Falha sintética no histórico'")
            try:
                with self.assertRaises(DBAPIError):
                    TransferirAssuntoService.executar(
                        assunto['id'],
                        {'materia_destino_id': destino['id'], 'impacto_esperado': {'questoes': 0}}
                    )
                s = db.session.get(Assunto, assunto['id'])
                self.assertEqual(s.materia_id, origem['id'])
                self.assertEqual(CatalogoRepository.impacto_assunto(s.id)['transferencias'], 0)
            finally:
                db.session.remove()
                with db.engine.begin() as limpeza:
                    limpeza.exec_driver_sql('DROP TRIGGER tr_falha_transferencia_013')

    def test_mapeamento_textual_join_tipos_identidade_corrente_e_rollback(self):
        materia = self._matter()
        assunto = self._subject(materia['id'])
        with self.app.app_context():
            campos = ','.join(f's.{c.name} AS s_{c.name}' for c in Assunto.__table__.columns)
            campos += ',' + ','.join(f'm.{c.name} AS m_{c.name}' for c in Materia.__table__.columns)
            with db.engine.begin() as instalacao:
                instalacao.exec_driver_sql('CREATE PROCEDURE sp_teste_orm(IN p_id BIGINT UNSIGNED) '
                    'READS SQL DATA SQL SECURITY INVOKER BEGIN SELECT '+campos+
                    ",JSON_OBJECT('numero',7) AS dados,TRUE AS flag FROM assuntos s "
                    'JOIN materias m ON m.id=s.materia_id WHERE s.id=p_id FOR UPDATE; '
                    'SELECT 99 AS terminal_util; END')
            try:
                atual = db.session.get(Assunto, assunto['id'])
                antiga = db.session.get(Materia, materia['id'])
                with db.engine.begin() as outra:
                    outra.execute(
                        text('UPDATE materias SET descricao=:valor WHERE id=:id'),
                        {'valor': 'Leitura corrente', 'id': materia['id']}
                    )
                dados = column('dados', JSON)
                flag = column('flag', Boolean)
                comando = text('CALL sp_teste_orm(:id)').columns(
                    *Assunto.__table__.columns,
                    *Materia.__table__.columns,
                    dados,
                    flag
                )

                def operacao():
                    resultado = db.session.execute(
                        select(Assunto, Materia, dados, flag)
                        .from_statement(comando).execution_options(populate_existing=True),
                        {'id': assunto['id']}
                    )
                    try:
                        s, m, json_, booleano = resultado.one()
                    finally:
                        resultado.close()
                    self.assertIs(s, atual)
                    self.assertIs(m, antiga)
                    self.assertTrue(inspect(s).persistent)
                    self.assertIs(inspect(s).session, db.session())
                    self.assertEqual(m.descricao, 'Leitura corrente')
                    self.assertEqual(json_, {'numero': 7})
                    self.assertIs(booleano, True)
                    self.assertIsInstance(s.criado_em, datetime)
                    s.atualizar(confirmar=False, descricao='Será revertida')
                    self.assertEqual(db.session.execute(text('SELECT 8')).scalar_one(), 8)
                    raise RuntimeError('Falha posterior à mutação')

                with self.assertRaisesRegex(RuntimeError, 'posterior'):
                    TransactionManager.executar(operacao)
                self.assertEqual(
                    db.session.get(
                        Assunto,
                        assunto['id']
                    ).descricao,
                    assunto['descricao']
                )
                self.assertEqual(
                    db.session.get(
                        Materia,
                        materia['id']
                    ).descricao,
                    'Leitura corrente'
                )
                vazio = db.session.execute(
                    select(
                        Assunto,
                        Materia,
                        dados,
                        flag
                    ).from_statement(comando),
                    {'id': 2**31+1}
                )
                try:
                    self.assertEqual(vazio.all(), [])
                finally:
                    vazio.close()
                self.assertEqual(db.session.execute(text('SELECT 9')).scalar_one(), 9)
            finally:
                db.session.remove()
                with db.engine.begin() as limpeza:
                    limpeza.exec_driver_sql('DROP PROCEDURE sp_teste_orm')

    def test_caracterizacao_seletores_impactos_equivalencia_e_entidades(self):
        materia = self._matter()
        outra = self._matter()
        assunto = self._subject(materia['id'], '  Genética '+uuid4().hex[: 8])
        self._question(assunto['id'])
        self._question(assunto['id'])
        with self.app.app_context():
            self.assertEqual([a.id for a in AreaEnem.listar_ordenadas()], [1, 2, 3, 4])
            materias = Materia.listar_ativos()
            self.assertEqual(
                [(
                    m.nome,
                    m.id
                ) for m in materias],
                sorted((
                    m.nome,
                    m.id
                ) for m in materias)
            )
            self.assertEqual(
                CatalogoRepository.impacto_materia(materia['id']),
                {'assuntos': 1, 'questoes': 2, 'transferencias': 0}
            )
            self.assertEqual(
                CatalogoRepository.impacto_assunto(assunto['id']),
                {'questoes': 2, 'transferencias': 0}
            )
            s = db.session.get(Assunto, assunto['id'])
            self.assertTrue(CatalogoRepository.existe_assunto_equivalente(
                materia['id'],
                s.nome_normalizado.upper()
            ))
            self.assertFalse(CatalogoRepository.existe_assunto_equivalente(
                materia['id'],
                s.nome_normalizado,
                s.id
            ))
            self.assertFalse(CatalogoRepository.existe_assunto_equivalente(
                outra['id'],
                s.nome_normalizado
            ))
            self.assertEqual(CatalogoRepository.contar_assuntos_nao_arquivados(materia['id']), 1)
            self.assertEqual(
                CatalogoRepository.impacto_assunto(2**31+1),
                {
                    'questoes': 0,
                    'transferencias': 0
                }
            )
            self.assertTrue(all(inspect(m).persistent for m in materias))
        self.assertEqual(
            self.client.post(f"/api/assuntos/{assunto['id']}/arquivar").status_code,
            200
        )
        with self.app.app_context():
            self.assertEqual(CatalogoRepository.listar_assuntos_ativos(materia['id']), [])
            self.assertEqual(CatalogoRepository.contar_assuntos_nao_arquivados(materia['id']), 0)
            self.assertTrue(CatalogoRepository.existe_assunto_equivalente(
                materia['id'],
                assunto['nome_normalizado']
            ))
