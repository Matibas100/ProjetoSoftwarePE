"""Diagnóstico e dashboards sobre MySQL real, sem mocks de origem."""
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import select, text
from tests import sql_observer as event
from app.contexto_leitura import ContextoLeitura
from app.core.relogio import agora_utc
from app.extensions import db
from app.modules.praticas.models.pratica_tentativa import PraticaTentativa
from app.modules.simulados.models.simulado import SimuladoTentativa
from app.modules.praticas.repositories.pratica_repository import PraticaRepository
from app.modules.simulados.repositories.simulado_repository import SimuladoRepository
from app.modules.desempenho.repositories.desempenho_repository import DesempenhoRepository
from app.http_composition import servicos
from app.modules.praticas.services.listar_praticas_service import ConsultarFatosPraticasService
from app.modules.simulados.services.consultar_simulado_service import ConsultarFatosSimuladosService
from app.modules.praticas.services.iniciar_pratica_service import IniciarPraticaService
from app.modules.praticas.services.responder_pratica_service import ResponderPraticaService
from tests.integration_support import MySQLIntegrationTestCase
from tests import test_simulados_integration as sim_fixture


class DesempenhoIntegrationTest(MySQLIntegrationTestCase):
    setUp = sim_fixture.SimuladosIntegrationTest.setUp
    conta = sim_fixture.SimuladosIntegrationTest.conta
    publicar = sim_fixture.SimuladosIntegrationTest.publicar
    criar = sim_fixture.SimuladosIntegrationTest.criar
    confirmar = sim_fixture.SimuladosIntegrationTest.confirmar
    iniciar = sim_fixture.SimuladosIntegrationTest.iniciar
    resposta = sim_fixture.SimuladosIntegrationTest.resposta
    finalizar = sim_fixture.SimuladosIntegrationTest.finalizar

    def pratica(self, alternativa='A'):
        dados={'questao_versao_id':self.versao,'chave_envio':str(uuid4())}
        t=self.aluno.post('/api/aluno/praticas',json=dados).json
        if alternativa is not None:
            self.assertEqual(self.aluno.post(f"/api/aluno/praticas/{t['id']}/resposta",json={'alternativa':alternativa}).status_code,200)
        return t['id']

    def diagnostico(self):
        r=self.aluno.get('/api/aluno/desempenho');self.assertEqual(r.status_code,200);return r.json

    def transferir(self,materia_id):
        url=f"/api/assuntos/{self.assunto['id']}"
        previa=self.client.get(url+'/impacto-transferencia',query_string={'materia_destino_id':materia_id})
        self.assertEqual(previa.status_code,200)
        r=self.client.post(url+'/transferir',json={'materia_destino_id':materia_id,'impacto_esperado':previa.json['impacto']})
        self.assertEqual(r.status_code,200)

    def test_vazio_perfil_filtros_e_no_store(self):
        d=self.diagnostico();self.assertEqual(d['geral']['total_respostas'],0)
        self.assertIsNone(d['geral']['percentual_acerto']);self.assertEqual(d['geral']['estado_amostra'],'sem_dados')
        self.assertEqual(d['base'],{'pratica':0,'simulado':0});self.assertEqual(d['materias'],[]);self.assertEqual(d['assuntos'],[])
        self.assertEqual(self.aluno.get('/api/aluno/dashboard').json['ultimas_atividades'],[])
        for url in ['/api/aluno/desempenho','/api/aluno/dashboard']:
            self.assertEqual(self.client.get(url).status_code,403)
            a=self.app.test_client().get(url);self.assertEqual(a.status_code,401);self.assertEqual(a.headers['Cache-Control'],'no-store')
            for q in ['usuario_id=1','inicio=2026-01-01','inicio=2026-01-02&fim=2026-01-01',
                'inicio=2026-01-01&fim=2099-01-01','inicio=2020-01-01&fim=2026-01-01',
                'inicio=2026-02-30&fim=2026-03-01','inicio=2026-1-01&fim=2026-01-02',
                'inicio=2026-01-01&fim=2026-01-01&fim=2026-01-01']:
                self.assertEqual(self.aluno.get(url+'?'+q).status_code,400,q)
        self.assertEqual(self.aluno.get('/api/admin/dashboard').status_code,403)
        self.assertEqual(self.client.get('/api/admin/dashboard?usuario_id=1').status_code,400)

    def test_projecoes_equivalentes_replay_repeticoes_e_origens(self):
        p=self.pratica();self.pratica('B');self.pratica(None)
        self.aluno.post(f'/api/aluno/praticas/{p}/resposta',json={'alternativa':'A'})
        t=self.iniciar().json;self.resposta(t);self.resposta(t,n=1,alternativa='B',revisao=2);self.finalizar(t,revisao=3);self.finalizar(t)
        pendente=self.iniciar().json;self.resposta(pendente)
        d=self.diagnostico();self.assertEqual(d['geral']['total_respostas'],4);self.assertEqual(d['geral']['acertos'],2)
        self.assertEqual(d['geral']['percentual_acerto'],50);self.assertEqual(d['base'],{'pratica':2,'simulado':2})
        self.assertEqual(d['geral']['estado_amostra'],'amostra_pequena')
        self.pratica();d=self.diagnostico();self.assertEqual(d['geral']['estado_amostra'],'dados_disponiveis')
        self.assertEqual(d['geral']['total_respostas'],5)
        self.assertEqual(self.outro.get('/api/aluno/desempenho').json['geral']['total_respostas'],0)
        with self.app.app_context():
            inicio=agora_utc()-timedelta(days=1);fim=agora_utc()+timedelta(days=1)
            for repo,service,campo,tipo in [(PraticaRepository,ConsultarFatosPraticasService,'respondida_em','pratica'),
                (SimuladoRepository,ConsultarFatosSimuladosService,'finalizada_em','simulado')]:
                fatos=service.executar(self.usuario,inicio,fim)
                with ContextoLeitura() as leitura:linhas=leitura.executar(repo.projecao_desempenho(self.usuario,inicio,fim)).mappings().all()
                self.assertEqual([f['id'] for f in fatos], sorted(r['id'] for r in linhas))
                for f in fatos:
                    r=next(r for r in linhas if r['id']==f['id'])
                    self.assertEqual((r['tipo'],r['usuario_id'],r['ocorrido_em'],bool(r['correta'])),(tipo,f['usuario_id'],f[campo],f['correta']))
                    self.assertEqual(r['atividade_id'],f.get('atividade_id',f['id']))
                    self.assertEqual(r['materia_id'],f['classificacao']['materia']['id'])
                    self.assertEqual(r['assunto_nome'],f['classificacao']['assunto']['nome'])

    def test_atividades_ordem_periodo_limite_e_simulado_em_branco(self):
        ids=[self.pratica('A') for _ in range(6)]
        t=self.iniciar().json;self.finalizar(t)
        instante=agora_utc().replace(microsecond=0)
        with self.app.app_context():
            db.session.execute(text('UPDATE pratica_tentativas SET iniciada_em=:data,respondida_em=:data WHERE usuario_id=:id AND estado=\'respondida\''),{'data':instante,'id':self.usuario})
            db.session.execute(text('UPDATE simulado_tentativas SET iniciada_em=:data,finalizada_em=:data WHERE id=:id'),{'data':instante,'id':t['id']});db.session.commit()
        d=self.aluno.get('/api/aluno/dashboard').json
        self.assertEqual(d['desempenho']['base'],{'pratica':6,'simulado':0})
        a=d['ultimas_atividades'];self.assertEqual(len(a),5)
        self.assertEqual((a[0]['tipo'],a[0]['id']),('simulado',t['id']))
        self.assertEqual([r['id'] for r in a[1:]],sorted(ids,reverse=True)[:4])
        self.assertEqual(set(a[0]),{'tipo','id','ocorrido_em','titulo','url'})
        self.assertEqual(a[0]['url'],f"/aluno/simulado.html?tentativa_id={t['id']}")
        self.assertTrue(a[1]['url'].startswith('/aluno/questao.html?tentativa_id='))
        anterior=(instante-timedelta(days=1)).date().isoformat()
        self.assertEqual(self.aluno.get('/api/aluno/dashboard',query_string={'inicio':anterior,'fim':anterior}).json['ultimas_atividades'],[])

    def test_limites_utc_relogio_fixo_e_intervalo_366(self):
        ids=[self.pratica() for _ in range(3)]
        inicio=datetime(2026,10,10);instantes=[inicio-timedelta(microseconds=1),inicio,inicio+timedelta(days=1)]
        with self.app.app_context():
            for id_,instante in zip(ids,instantes):
                db.session.execute(text('UPDATE pratica_tentativas SET iniciada_em=:data,respondida_em=:data WHERE id=:id'),{'data':instante,'id':id_})
            db.session.commit()
            relogio=datetime(2026,10,24,0,0,1)
            d=servicos().desempenho.executar(self.usuario,{'inicio':'2026-10-10','fim':'2026-10-10'},instante=relogio)
            self.assertEqual(d['geral']['total_respostas'],1);self.assertEqual(d['calculado_em'],'2026-10-24T00:00:01Z')
            d=servicos().desempenho.executar(self.usuario,instante=relogio)
            self.assertEqual(d['periodo'],{'inicio':'2026-09-25','fim':'2026-10-24','timezone':'UTC'})
            fim=relogio.date();ini=(fim-timedelta(days=365)).isoformat()
            d=servicos().desempenho.executar(self.usuario,{'inicio':ini,'fim':fim.isoformat()},instante=relogio)
            self.assertEqual(d['geral']['total_respostas'],3)

    def test_rotulos_recentes_transferencia_e_media_ponderada(self):
        self.pratica('B');self.pratica('B')
        with self.app.app_context():
            m_id=self.materia['id']
            db.session.execute(text("UPDATE pratica_tentativas SET materia_nome='Nome mais novo',respondida_em=respondida_em+INTERVAL 1 SECOND WHERE usuario_id=:id AND id=(SELECT id FROM (SELECT MAX(id) id FROM pratica_tentativas WHERE usuario_id=:id) x)"),{'id':self.usuario});db.session.commit()
        t=self.iniciar().json;self.resposta(t);self.finalizar(t,revisao=2)
        # Simulado 1/1 e práticas 0/2: total ponderado 1/3, não média de 100 e 0.
        d=self.diagnostico();self.assertEqual(d['geral']['percentual_acerto'],33.33)
        self.assertEqual(d['materias'][0]['materia_nome'],'Nome mais novo')
        m=self.client.post('/api/materias',json={'nome':'Destino '+uuid4().hex,'area_enem_id':4}).json
        self.transferir(m['id'])
        depois=self.diagnostico();self.assertEqual(depois['materias'],d['materias']);self.assertEqual(depois['materias'][0]['materia_id'],m_id)

    def test_views_preservam_fatos_e_atividades_apos_arquivamento(self):
        self.pratica('B')
        tentativa = self.iniciar().json
        self.resposta(tentativa)
        self.finalizar(tentativa, revisao=2)
        antes = self.diagnostico()
        atividades = self.aluno.get('/api/aluno/dashboard').json['ultimas_atividades']
        for url, dados in [
            (self.path+'/arquivar', self.confirmar()),
            (self.qpath+'/arquivar', self.confirmar()),
            (f"/api/assuntos/{self.assunto['id']}/arquivar", {}),
            (f"/api/materias/{self.materia['id']}/arquivar", {}),
        ]:
            resposta = self.client.post(url, json=dados)
            self.assertEqual(resposta.status_code, 200, resposta.json)
        depois = self.diagnostico()
        for campo in ['geral', 'base', 'materias', 'assuntos']:
            self.assertEqual(depois[campo], antes[campo])
        self.assertEqual(self.aluno.get('/api/aluno/dashboard').json['ultimas_atividades'], atividades)

    def test_procedures_aluno_ausentes_falham_sem_blocos_parciais_e_pool_recupera(self):
        for rotina in ['sp_desempenho_resumo', 'sp_atividades_recentes']:
            with self.subTest(rotina=rotina), self.app.app_context():
                with db.engine.connect() as con:
                    ddl = con.exec_driver_sql('SHOW CREATE PROCEDURE '+rotina).mappings().one()['Create Procedure']
                    with con.connection.driver_connection.cursor() as c:
                        c.execute('DROP PROCEDURE '+rotina)
                try:
                    resposta = self.aluno.get('/api/aluno/dashboard')
                    self.assertEqual(resposta.status_code, 500)
                    self.assertEqual(set(resposta.json), {'erro'})
                    self.assertNotIn(rotina, resposta.json['erro'])
                finally:
                    db.session.remove()
                    with db.engine.connect() as con:
                        with con.connection.driver_connection.cursor() as c:
                            c.execute(ddl)
                self.assertEqual(self.aluno.get('/api/aluno/dashboard').status_code, 200)

    def test_grupos_distintos_apos_transferencia_nao_reatribuem_historico(self):
        self.pratica('B');self.pratica('B')
        destino=self.client.post('/api/materias',json={'nome':'Outra matéria '+uuid4().hex,'area_enem_id':4}).json
        self.transferir(destino['id'])
        self.assertEqual(self.client.put(self.qpath,json={'revisao':1,'enunciado':'Versão na nova classificação'}).status_code,200)
        self.versao=self.publicar(2);self.pratica('A')
        self.client.post('/api/materias',json={'nome':'Sem respostas '+uuid4().hex,'area_enem_id':4})
        d=self.diagnostico();self.assertEqual(d['geral']['percentual_acerto'],33.33)
        self.assertEqual([r['materia_id'] for r in d['materias']],[self.materia['id'],destino['id']])
        self.assertEqual([r['total_respostas'] for r in d['materias']],[2,1])
        self.assertEqual([r['percentual_acerto'] for r in d['materias']],[0,100])
        self.assertEqual([(r['materia_id'],r['assunto_id']) for r in d['assuntos']],
            [(self.materia['id'],self.assunto['id']),(destino['id'],self.assunto['id'])])

    def test_snapshot_nao_inclui_resposta_concorrente_e_contexto_externo_preservado(self):
        self.pratica()
        with self.app.app_context():
            instante=agora_utc()
            with ContextoLeitura(instante=instante) as leitura:
                antes=servicos().desempenho.executar(self.usuario,contexto=leitura,instante=instante)
                # Outra sessão/conexão confirma uma resposta após a abertura do snapshot.
                with self.app.app_context():
                    t,_=IniciarPraticaService.executar(self.usuario,{'questao_versao_id':self.versao,'chave_envio':str(uuid4())})
                    ResponderPraticaService.executar(self.usuario,t['id'],{'alternativa':'B'})
                depois=servicos().desempenho.executar(self.usuario,contexto=leitura,instante=instante)
                self.assertEqual(antes,depois)
                _,inicio,fim=__import__('app.modules.desempenho.services.desempenho_validacao',fromlist=['periodo']).periodo({},instante)
                self.assertEqual(len(DesempenhoRepository.atividades(leitura,self.usuario,inicio,fim)),1)
            self.assertEqual(servicos().desempenho.executar(self.usuario)['geral']['total_respostas'],2)
            with db.engine.connect().execution_options(isolation_level='REPEATABLE READ') as conexao:
                transacao=conexao.begin()
                conexao.execute(text("INSERT INTO materias(nome,area_enem_id) VALUES('Transação externa',4)"))
                with ContextoLeitura(conexao,instante) as leitura:
                    servicos().desempenho.executar(self.usuario,contexto=leitura,instante=instante)
                    with self.assertRaises(ValueError):servicos().desempenho.executar(self.usuario,contexto=leitura,instante=instante+timedelta(seconds=1))
                    self.assertTrue(transacao.is_active)
                self.assertTrue(transacao.is_active);transacao.rollback()
            self.assertEqual(db.session.execute(text("SELECT COUNT(*) FROM materias WHERE nome='Transação externa'")).scalar_one(),0)

    def test_contextos_invalidos_falha_limpa_conexao_sem_payload_parcial(self):
        from sqlalchemy.exc import DBAPIError
        with self.app.app_context():
            c=ContextoLeitura()
            with self.assertRaises(ValueError):c.validar()
            with ContextoLeitura() as somente_leitura:
                with self.assertRaises(DBAPIError):
                    somente_leitura.executar(text("INSERT INTO materias(nome,area_enem_id) VALUES('Escrita proibida',4)"))
                with self.assertRaises(ValueError):somente_leitura.__enter__()
            with db.engine.connect().execution_options(isolation_level='READ COMMITTED') as conexao:
                transacao=conexao.begin()
                with self.assertRaises(ValueError):
                    with ContextoLeitura(conexao):pass
                self.assertTrue(transacao.is_active);transacao.rollback()
            def falhar(conexao,cursor,statement,parameters,context,executemany):
                if 'CALL sp_atividades_recentes' in statement:raise RuntimeError('Falha interna controlada')
            engine=db.engine;event.listen(engine,'before_cursor_execute',falhar)
            try:
                r=self.aluno.get('/api/aluno/dashboard');self.assertEqual(r.status_code,500)
                self.assertEqual(set(r.json),{'erro'});self.assertNotIn('controlada',r.json['erro'])
            finally:event.remove(engine,'before_cursor_execute',falhar)
            self.assertEqual(self.aluno.get('/api/aluno/dashboard').status_code,200)
            with self.assertRaises(RuntimeError):
                with c:raise RuntimeError('falha')
            self.assertTrue(c._conexao.closed)
            def falhar_diagnostico(conexao,cursor,statement,parameters,context,executemany):
                if 'CALL sp_desempenho_resumo' in statement:raise RuntimeError('Falha na leitura externa')
            with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conexao:
                transacao=conexao.begin()
                conexao.execute(text("INSERT INTO materias(nome,area_enem_id) VALUES('Falha externa',4)"))
                with ContextoLeitura(conexao) as leitura:
                    event.listen(conexao,'before_cursor_execute',falhar_diagnostico)
                    try:
                        with self.assertRaises(RuntimeError):servicos().desempenho.executar(self.usuario,contexto=leitura)
                    finally:event.remove(conexao,'before_cursor_execute',falhar_diagnostico)
                    self.assertTrue(transacao.is_active)
                self.assertTrue(transacao.is_active);transacao.rollback()
            self.assertEqual(db.session.execute(text("SELECT COUNT(*) FROM materias WHERE nome IN ('Falha externa','Escrita proibida')")).scalar_one(),0)

    def test_administrativo_contagens_reais_sem_individuos(self):
        antes=self.client.get('/api/admin/dashboard');self.assertEqual(antes.status_code,200)
        d=antes.json;self.assertEqual(set(d),{'calculado_em','catalogo','questoes','simulados','tentativas_simulado_finalizadas'})
        self.assertNotIn('email',str(d));self.assertNotIn('usuario',str(d))
        self.criar();t=self.iniciar().json;self.finalizar(t)
        depois=self.client.get('/api/admin/dashboard').json
        self.assertEqual(depois['simulados']['rascunhos'],d['simulados']['rascunhos']+1)
        self.assertEqual(depois['tentativas_simulado_finalizadas'],d['tentativas_simulado_finalizadas']+1)
        self.assertEqual(depois['catalogo'],d['catalogo'])

    def test_contagens_admin_compartilham_snapshot(self):
        antes=self.client.get('/api/admin/dashboard').json
        with self.app.app_context():
            engine=db.engine;executou=[]
            def inserir(conexao,cursor,statement,parameters,context,executemany):
                if not executou and 'CALL sp_conteudo_contagens_dashboard' in statement:
                    executou.append(True)
                    with engine.begin() as outra:
                        materia=outra.execute(text("INSERT INTO materias(nome,area_enem_id) VALUES('Nova concorrente',4)")).lastrowid
                        outra.execute(text("INSERT INTO assuntos(nome,nome_normalizado,materia_id) VALUES('Novo concorrente','novo concorrente',:m)"),{'m':materia})
            event.listen(engine,'after_cursor_execute',inserir)
            try:r=self.client.get('/api/admin/dashboard')
            finally:event.remove(engine,'after_cursor_execute',inserir)
        self.assertEqual(r.status_code,200);self.assertEqual(r.json['catalogo'],antes['catalogo'])
        depois=self.client.get('/api/admin/dashboard').json
        self.assertEqual(depois['catalogo']['materias_ativas'],antes['catalogo']['materias_ativas']+1)
        self.assertEqual(depois['catalogo']['assuntos_ativos'],antes['catalogo']['assuntos_ativos']+1)


class DashboardVazioIntegrationTest(MySQLIntegrationTestCase):
    def test_todas_contagens_iniciais_zero(self):
        r=self.client.get('/api/admin/dashboard');self.assertEqual(r.status_code,200)
        for bloco in ['catalogo','questoes','simulados']:
            self.assertTrue(all(v==0 for v in r.json[bloco].values()))
        self.assertEqual(r.json['tentativas_simulado_finalizadas'],0)
