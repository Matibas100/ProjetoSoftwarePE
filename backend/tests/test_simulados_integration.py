"""Composição, privacidade, replay e transações com MySQL real."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from uuid import uuid4
from sqlalchemy import event, text
from app.extensions import db
from app.core.relogio import agora_utc
from app.exceptions import ConflitoError
from app.modules.simulados.models.simulado import SimuladoEvento, SimuladoTentativa, SimuladoVersao, SimuladoVersaoItem
from app.modules.simulados.services.iniciar_simulado_service import IniciarSimuladoService
from app.modules.simulados.services.responder_simulado_service import ResponderSimuladoService
from app.modules.simulados.services.finalizar_simulado_service import FinalizarSimuladoService
from app.modules.simulados.services.consultar_simulado_service import ConsultarFatosSimuladosService
from tests.integration_support import MySQLIntegrationTestCase
from tests import test_praticas_integration as pratica_fixture


class SimuladosIntegrationTest(MySQLIntegrationTestCase):
    conta = pratica_fixture.PraticasIntegrationTest.conta
    publicar = pratica_fixture.PraticasIntegrationTest.publicar

    def setUp(self):
        pratica_fixture.PraticasIntegrationTest.setUp(self)
        self.versoes = [self.versao]
        for n in range(2):
            dados = {c: 'Texto ' + c for c in ('enunciado', 'alternativa_a', 'alternativa_b', 'alternativa_c', 'alternativa_d', 'alternativa_e')}
            dados.update(assunto_id=self.assunto['id'], resposta_correta='A', dificuldade='media', explicacao=None)
            q = self.client.post('/api/questoes', json=dados).get_json()
            self.versoes.append(self.client.post(f"/api/questoes/{q['id']}/publicar", json={
                'revisao':1,'confirmar':True,'motivo':'Revisão de teste'}).get_json()['versao_publicada_id'])
        self.s = self.criar().get_json()
        self.path = f"/api/admin/simulados/{self.s['id']}"
        r = self.client.post(self.path+'/publicar', json=self.confirmar())
        self.assertEqual(r.status_code,200)
        self.v = r.get_json()['simulado_versao_id']

    def criar(self, **dados):
        return self.client.post('/api/admin/simulados', json={'titulo':'Simulado de teste', 'questao_versao_ids':self.versoes, **dados})

    def confirmar(self, revisao=1):
        return {'revisao':revisao,'confirmar':True,'motivo':'Revisão explícita de teste'}

    def test_selects_constantes_por_composicao_pagina_e_propriedade(self):
        from app.modules.simulados.services.gestao_simulado_service import ListarSimuladosAdminService
        from app.modules.simulados.services.consultar_simulado_service import (
            ListarSimuladosAlunoService, ConsultarTentativaSimuladoService,
            ListarHistoricoSimuladosService,
        )
        from app.http_composition import servicos

        pequeno = self.criar(questao_versao_ids=self.versoes[:1]).json
        publicado = self.client.post(f"/api/admin/simulados/{pequeno['id']}/publicar", json=self.confirmar()).json
        pequeno_v = publicado['simulado_versao_id']
        maior = self.iniciar().json
        menor = self.iniciar(versao=pequeno_v).json
        alheia = self.iniciar(cliente=self.outro).json
        aluno_id = self.aluno.get('/api/auth/sessao').json['usuario']['id']

        def medir(operacao):
            from tests import sql_observer
            consultas = []
            def contar(connection, cursor, statement, parameters, context, executemany):
                if statement.lstrip().upper().startswith(('SELECT', 'CALL')):
                    consultas.append(statement)
            db.session.remove()
            sql_observer.listen(db.engine, 'before_cursor_execute', contar)
            try:
                resultado = operacao()
            finally:
                sql_observer.remove(db.engine, 'before_cursor_execute', contar)
            self.assertFalse(any('FOR UPDATE' in sql.upper() for sql in consultas))
            return resultado, len(consultas)

        with self.app.app_context():
            for listar in (lambda filtros: ListarSimuladosAdminService.executar({**filtros, 'status':'publicado'}),
                           lambda filtros: servicos().simulados_aluno.executar(aluno_id, filtros),
                           servicos().questoes_aluno.executar):
                _, poucas = medir(lambda: listar({'por_pagina':'1'}))
                pagina, muitas = medir(lambda: listar({'por_pagina':'100'}))
                self.assertGreater(len(pagina['itens']), 1)
                self.assertEqual(muitas, poucas)
            _, poucas = medir(lambda: ConsultarTentativaSimuladoService.executar(aluno_id, menor['id']))
            detalhe, muitas = medir(lambda: ConsultarTentativaSimuladoService.executar(aluno_id, maior['id']))
            self.assertEqual(muitas, poucas)
            self.assertEqual([i['questao']['questao_versao_id'] for i in detalhe['itens']], self.versoes)
            self.assertNotIn('resposta_correta', str(detalhe))

        self.assertEqual(self.finalizar(maior).status_code, 200)
        self.assertEqual(self.finalizar(menor).status_code, 200)
        with self.app.app_context():
            _, poucas = medir(lambda: ConsultarTentativaSimuladoService.executar(aluno_id, menor['id'], 'correcao'))
            _, muitas = medir(lambda: ConsultarTentativaSimuladoService.executar(aluno_id, maior['id'], 'correcao'))
            self.assertEqual(muitas, poucas)
            _, poucas = medir(lambda: servicos().historico_simulados.executar(aluno_id, {'por_pagina':'1'}))
            _, muitas = medir(lambda: servicos().historico_simulados.executar(aluno_id, {'por_pagina':'100'}))
            self.assertEqual(muitas, poucas)

        disponivel = self.criar(questao_versao_ids=self.versoes[1:]).json
        self.assertEqual(self.client.post(f"/api/admin/simulados/{disponivel['id']}/publicar", json=self.confirmar()).status_code, 200)
        self.assertEqual(self.client.post(self.qpath+'/arquivar', json=self.confirmar()).status_code, 200)
        catalogo = self.aluno.get('/api/aluno/simulados').json['itens']
        retirado = next(s for s in catalogo if s['id'] == self.s['id'])
        self.assertFalse(retirado['disponivel'])
        self.assertTrue(next(s for s in catalogo if s['id'] == disponivel['id'])['disponivel'])
        self.assertIsNone(retirado['tentativa_em_andamento_id'])
        self.assertNotEqual(alheia['id'], maior['id'])
        self.assertEqual(self.outro.get(f"/api/aluno/tentativas-simulado/{maior['id']}").status_code, 404)

    def iniciar(self, chave=None, versao=None, cliente=None):
        return (cliente or self.aluno).post('/api/aluno/tentativas-simulado', json={
            'simulado_versao_id':versao or self.v, 'chave_envio':chave or str(uuid4())})

    def resposta(self, t, n=0, alternativa='A', revisao=None):
        return self.aluno.put(f"/api/aluno/tentativas-simulado/{t['id']}/respostas/{t['itens'][n]['item_id']}",
            json={'alternativa':alternativa,'revisao':revisao or t['revisao']})

    def finalizar(self,t,revisao=None):
        return self.aluno.post(f"/api/aluno/tentativas-simulado/{t['id']}/finalizar",
            json={'revisao':revisao or t['revisao'],'confirmar':True})

    def test_criar_editar_publicar_replay_arquivar_e_eventos(self):
        s=self.criar().get_json(); path=f"/api/admin/simulados/{s['id']}"
        dados={'titulo':'Composição alterada','questao_versao_ids':self.versoes[::-1],'revisao':1}
        r=self.client.put(path,json=dados); self.assertEqual(r.status_code,200)
        self.assertEqual([i['questao_versao_id'] for i in r.json['itens']],self.versoes[::-1])
        self.assertEqual(self.client.put(path,json=dados).status_code,409)
        self.assertEqual(self.client.post(path+'/publicar',json=self.confirmar(1)).status_code,409)
        r=self.client.post(path+'/publicar',json=self.confirmar(2)); self.assertEqual(r.status_code,200)
        self.assertEqual(self.client.post(path+'/publicar',json=self.confirmar(2)).json,r.json)
        self.assertEqual(self.client.put(path,json={**dados,'revisao':2}).status_code,409)
        self.assertEqual(self.client.post(path+'/arquivar',json=self.confirmar(1)).status_code,409)
        a=self.client.post(path+'/arquivar',json=self.confirmar(2)); self.assertEqual(a.status_code,200)
        self.assertEqual(self.client.post(path+'/arquivar',json=self.confirmar(2)).json,a.json)
        self.assertEqual(self.client.post(path+'/publicar',json=self.confirmar(2)).status_code,409)
        with self.app.app_context():
            eventos=db.session.execute(db.select(SimuladoEvento).where(SimuladoEvento.simulado_id==s['id']).order_by(SimuladoEvento.id)).scalars().all()
            self.assertEqual([e.acao for e in eventos],['cadastro','edicao','revisao','aprovacao','publicacao','arquivamento'])
            for entidade in (SimuladoVersao,SimuladoVersaoItem,SimuladoEvento):
                linha=db.session.execute(db.select(entidade)).scalars().first()
                db.session.delete(linha)
                with self.assertRaises(ConflitoError): db.session.flush()
                db.session.rollback()

    def test_validacao_composicao_filtros_e_nao_encontrado(self):
        for dados in [{'titulo':'x'}, {'titulo':'x'*151}, {'titulo':None}, {'questao_versao_ids':[]},
            {'questao_versao_ids':self.versoes*61},{'questao_versao_ids':[True]}, {'questao_versao_ids':[self.v, self.v]}]:
            self.assertEqual(self.criar(**dados).status_code,400,dados)
        self.assertEqual(self.criar(questao_versao_ids=[2147483647]).status_code,404)
        self.assertEqual(self.client.get('/api/admin/simulados/2147483647').status_code,404)
        self.assertEqual(self.client.put(self.path,json={'titulo':'Outro','questao_versao_ids':self.versoes,'revisao':1}).status_code,409)
        for dados in [{}, {'revisao':True}, {**self.confirmar(),'confirmar':False}, {**self.confirmar(),'motivo':'x'}]:
            self.assertEqual(self.client.post(self.path+'/publicar',json=dados).status_code,400)
        for query in ['status=invalido','busca=teste','por_pagina=101','pagina=0','status=publicado&status=publicado']:
            self.assertEqual(self.client.get('/api/admin/simulados?'+query).status_code,400)
        r=self.client.get('/api/admin/simulados?status=publicado&por_pagina=1')
        self.assertEqual(r.status_code,200); self.assertEqual(len(r.json['itens']),1)
        self.assertEqual(self.client.get('/api/admin/simulados?pagina=99999').json['itens'],[])
        self.assertEqual(self.aluno.get('/api/aluno/simulados?usuario_id=1').status_code,400)
        self.assertEqual(self.aluno.get('/api/aluno/tentativas-simulado?pagina=0').status_code,400)

    def test_perfis_csrf_no_store_e_propriedade(self):
        t=self.iniciar().json; base=f"/api/aluno/tentativas-simulado/{t['id']}"
        rotas=[('/api/admin/simulados','get',None),('/api/admin/simulados','post',{}),
            (self.path,'get',None),(self.path,'put',{}),(self.path+'/publicar','post',{}),(self.path+'/arquivar','post',{})]
        for url,metodo,dados in rotas:
            self.assertEqual(getattr(self.aluno,metodo)(url,json=dados).status_code,403)
            self.assertEqual(getattr(self.app.test_client(),metodo)(url,json=dados).status_code,401)
            self.assertEqual(getattr(self.app.test_client(),metodo)(url,json=dados).headers['Cache-Control'],'no-store')
        rotas=[('/api/aluno/simulados','get',None),('/api/aluno/tentativas-simulado','get',None),
            ('/api/aluno/tentativas-simulado','post',{}),(base,'get',None),(base+'/resultado','get',None),
            (base+'/correcao','get',None),(base+'/finalizar','post',{}),
            (base+f"/respostas/{t['itens'][0]['item_id']}",'put',{})]
        for url,metodo,dados in rotas:
            self.assertEqual(getattr(self.client,metodo)(url,json=dados).status_code,403)
            self.assertEqual(getattr(self.app.test_client(),metodo)(url,json=dados).status_code,401)
        for sufixo in ['', '/resultado','/correcao']:
            r=self.outro.get(base+sufixo); self.assertEqual(r.status_code,404)
            self.assertEqual(r.headers['Cache-Control'],'no-store')
        self.assertEqual(self.outro.post(base+'/finalizar',json={'revisao':1,'confirmar':True}).status_code,404)
        self.assertEqual(self.outro.put(base+'/respostas/1',json={'revisao':1,'alternativa':'A'}).status_code,404)
        self.assertEqual(self.aluno.get(base+'/resultado').status_code,409)
        self.assertEqual(self.aluno.get(base+'/correcao').status_code,409)
        self.assertEqual(self.aluno.head(base).status_code,200)
        self.assertEqual(self.aluno.put(base+'/respostas/2147483647',json={'revisao':1,'alternativa':'A'}).status_code,404)
        for headers in [{'Origin':'https://outra.test'}, {'X-CSRF-Token':'errado'}]:
            self.assertEqual(self.aluno.post(base+'/finalizar',json={'revisao':1,'confirmar':True},headers=headers).status_code,403)
        with self.app.app_context():
            db.session.execute(text('UPDATE sessoes SET reautenticada_em=NULL'));db.session.commit()
        self.assertEqual(self.client.post(self.path+'/arquivar',json=self.confirmar()).json['codigo'],'reautenticacao_necessaria')

    def test_inicio_retomada_replay_conteudo_retirado_e_chave_divergente(self):
        chave=str(uuid4()); r=self.iniciar(chave); t=r.json; self.assertEqual(r.status_code,201)
        self.assertEqual(self.iniciar(chave.upper()).json,t)
        self.assertEqual(self.iniciar().json,t)
        texto=str(t); self.assertNotIn('resposta_correta',texto); self.assertNotIn('explicacao',texto); self.assertNotIn('correta',texto)
        s=self.criar().json; path=f"/api/admin/simulados/{s['id']}"
        v=self.client.post(path+'/publicar',json=self.confirmar()).json['simulado_versao_id']
        self.assertEqual(self.iniciar(chave,v).status_code,409)
        self.assertEqual(self.client.post(self.path+'/arquivar',json=self.confirmar()).status_code,200)
        self.assertEqual(self.iniciar().json,t)
        self.assertEqual(self.finalizar(t).status_code,200)
        self.assertEqual(self.iniciar().status_code,409)
        self.assertEqual(self.iniciar(chave).json['id'],t['id'])
        self.assertEqual(self.iniciar(versao=2147483647).status_code,404)

    def test_inelegibilidade_superada_catalogo_e_duplicidade_logica(self):
        self.assertEqual(self.client.put(self.qpath,json={'revisao':1,'enunciado':'Nova versão'}).status_code,200)
        nova=self.publicar(2)
        self.assertEqual(self.criar(questao_versao_ids=[self.versao,nova]).status_code,400)
        self.assertEqual(self.iniciar().status_code,409)
        r=self.aluno.get('/api/aluno/simulados').json
        self.assertFalse(next(s for s in r['itens'] if s['id']==self.s['id'])['disponivel'])
        self.assertEqual(self.criar(questao_versao_ids=[self.versao]).status_code,409)
        self.assertEqual(self.client.post(f"/api/assuntos/{self.assunto['id']}/inativar",json={'confirmar':True,'motivo':'Teste de catálogo'}).status_code,200)
        self.assertEqual(self.criar(questao_versao_ids=[nova]).status_code,409)

    def test_responder_alterar_limpar_finalizar_e_recarregar(self):
        t=self.iniciar().json; base=f"/api/aluno/tentativas-simulado/{t['id']}"
        r=self.resposta(t);self.assertEqual(r.status_code,200);self.assertEqual(r.json['revisao'],2)
        self.assertEqual(self.resposta(t,alternativa='B').status_code,409)
        self.assertEqual(self.resposta(t,alternativa=None,revisao=2).status_code,200)
        self.assertIsNone(self.aluno.get(base).json['itens'][0]['alternativa'])
        self.assertEqual(self.resposta(t,revisao=3).status_code,200)
        self.assertEqual(self.resposta(t,n=1,alternativa='B',revisao=4).status_code,200)
        self.assertNotIn('correta',str(self.aluno.get(base).json))
        self.assertEqual(self.finalizar(t,revisao=4).status_code,409)
        r=self.finalizar(t,revisao=5);self.assertEqual(r.status_code,200)
        self.assertEqual({k:r.json[k] for k in ('total','respondidas','acertos','erros','em_branco','percentual_acerto')},
            {'total':3,'respondidas':2,'acertos':1,'erros':1,'em_branco':1,'percentual_acerto':33.33})
        self.assertEqual(self.finalizar(t).json,r.json)
        self.assertEqual(self.aluno.get(base+'/resultado').json,r.json)
        c=self.aluno.get(base+'/correcao').json
        self.assertEqual([i['correta'] for i in c['itens']],[True,False,None])
        self.assertEqual([i['gabarito'] for i in c['itens']],['A']*3)
        self.assertEqual(self.resposta(t,revisao=6).status_code,409)
        h=self.aluno.get('/api/aluno/tentativas-simulado').json
        self.assertEqual(h['total_itens'],1);self.assertEqual(h['itens'][0]['resultado'],r.json)
        self.assertEqual(self.outro.get('/api/aluno/tentativas-simulado').json['itens'],[])
        self.assertEqual(self.iniciar().status_code,201)

    def test_entradas_invalidas_sem_mutacao(self):
        t=self.iniciar().json; url=f"/api/aluno/tentativas-simulado/{t['id']}/respostas/{t['itens'][0]['item_id']}"
        for dados in [None,[],{}, {'alternativa':'a','revisao':1},{'alternativa':True,'revisao':1},
            {'alternativa':'A','revisao':True},{'alternativa':[],'revisao':1},{'alternativa':'A','revisao':1,'extra':1}]:
            self.assertEqual(self.aluno.put(url,json=dados).status_code,400)
        for dados in [{},{'revisao':1,'confirmar':False},{'revisao':True,'confirmar':True}]:
            self.assertEqual(self.aluno.post(f"/api/aluno/tentativas-simulado/{t['id']}/finalizar",json=dados).status_code,400)
        for dados in [{},{'simulado_versao_id':True,'chave_envio':str(uuid4())},{'simulado_versao_id':self.v,'chave_envio':'x'}]:
            self.assertEqual(self.aluno.post('/api/aluno/tentativas-simulado',json=dados).status_code,400)

    def test_rollback_publicacao_e_finalizacao_na_ultima_gravacao(self):
        s=self.criar().json; path=f"/api/admin/simulados/{s['id']}"
        def falhar_publicacao(mapper,connection,target):
            if target.acao=='publicacao':raise RuntimeError('Falha controlada')
        event.listen(SimuladoEvento,'before_insert',falhar_publicacao)
        try:self.assertEqual(self.client.post(path+'/publicar',json=self.confirmar()).status_code,500)
        finally:event.remove(SimuladoEvento,'before_insert',falhar_publicacao)
        self.assertEqual(self.client.get(path).json['estado'],'rascunho')
        with self.app.app_context():
            self.assertEqual(db.session.execute(db.select(SimuladoVersao).where(SimuladoVersao.simulado_id==s['id'])).scalars().all(),[])
        t=self.iniciar().json;self.resposta(t)
        def falhar_finalizacao(mapper,connection,target):
            if target.estado=='finalizada':raise RuntimeError('Falha controlada')
        event.listen(SimuladoTentativa,'before_update',falhar_finalizacao)
        try:self.assertEqual(self.finalizar(t,revisao=2).status_code,500)
        finally:event.remove(SimuladoTentativa,'before_update',falhar_finalizacao)
        d=self.aluno.get(f"/api/aluno/tentativas-simulado/{t['id']}").json
        self.assertEqual(d['estado'],'em_andamento');self.assertEqual(d['revisao'],2)
        with self.app.app_context():
            self.assertTrue(all(r.correta is None for r,i in __import__('app.modules.simulados.repositories.simulado_repository',fromlist=['SimuladoRepository']).SimuladoRepository.respostas(t['id'])))
        self.assertEqual(self.finalizar(t,revisao=2).status_code,200)

    def test_snapshots_e_eventos_sem_mutacoes_ou_exclusao(self):
        with self.app.app_context():
            versao = db.session.get(SimuladoVersao, self.v)
            item = db.session.execute(db.select(SimuladoVersaoItem).where(
                SimuladoVersaoItem.simulado_versao_id == self.v)).scalars().first()
            evento = db.session.execute(db.select(SimuladoEvento).where(
                SimuladoEvento.simulado_id == self.s['id'])).scalars().first()
            for registro, campo in [(versao, 'titulo'), (item, 'posicao'), (evento, 'motivo')]:
                self.assertFalse(hasattr(registro, 'atualizar'))
                self.assertFalse(hasattr(registro, 'deletar'))
                antes = getattr(registro, campo)
                setattr(registro, campo, 99 if campo == 'posicao' else 'Mutação proibida')
                with self.assertRaises(ConflitoError): registro.salvar()
                self.assertEqual(getattr(registro, campo), antes)
                db.session.delete(registro)
                with self.assertRaises(ConflitoError): db.session.flush()
                db.session.rollback()
                self.assertEqual(getattr(registro, campo), antes)

    def test_fatos_preservados_apos_arquivamento_transferencia_e_novo_login(self):
        t=self.iniciar().json;self.resposta(t);self.resposta(t,n=1,alternativa='B',revisao=2)
        self.finalizar(t,revisao=3)
        base=f"/api/aluno/tentativas-simulado/{t['id']}";antes=self.aluno.get(base+'/correcao').json
        pendente=self.iniciar().json
        self.assertEqual(self.resposta(pendente).status_code,200)
        self.client.post(self.path+'/arquivar',json=self.confirmar())
        m=self.client.post('/api/materias',json={'nome':'Destino '+uuid4().hex,'area_enem_id':4}).json
        a=self.assunto['id']
        previa=self.client.get(f'/api/assuntos/{a}/impacto-transferencia',query_string={'materia_destino_id':m['id']})
        self.assertEqual(previa.status_code,200)
        self.assertEqual(self.client.post(f'/api/assuntos/{a}/transferir',json={
            'materia_destino_id':m['id'],'impacto_esperado':previa.json['impacto']}).status_code,200)
        self.aluno.post('/api/auth/logout');self.aluno.csrf=self.aluno.get('/api/auth/csrf').json['csrf_token']
        r=self.aluno.post('/api/auth/login',json={'email':self.email,'senha':self.senha});self.aluno.csrf=r.json['csrf_token']
        self.assertEqual(self.aluno.get(base+'/correcao').json,antes)
        with self.app.app_context():
            inicio=agora_utc()-timedelta(days=1);fim=agora_utc()+timedelta(days=1)
            fatos=ConsultarFatosSimuladosService.executar(self.usuario,inicio,fim)
            self.assertEqual(len(fatos),2);self.assertEqual([f['correta'] for f in fatos],[True,False])
            self.assertTrue(all(f['classificacao']['materia']['id']==self.materia['id'] for f in fatos))
            self.assertTrue(all(f['atividade_id']==t['id'] for f in fatos))
            self.assertEqual(ConsultarFatosSimuladosService.executar(self.outro_id,inicio,fim),[])
            self.assertEqual(ConsultarFatosSimuladosService.executar(self.usuario,fim,fim+timedelta(days=1)),[])

    def test_constraints_composicao_e_item_unico_no_mysql(self):
        from sqlalchemy.exc import DBAPIError
        from app.modules.simulados.models.simulado import SimuladoRascunhoItem, SimuladoResposta
        t=self.iniciar().json
        with self.app.app_context():
            item=db.session.execute(db.select(SimuladoRascunhoItem).where(SimuladoRascunhoItem.simulado_id==self.s['id'])).scalars().first()
            valores={c:getattr(item,c) for c in ('simulado_id','posicao','questao_id','questao_versao_id')}
            for mudanca in ({},{'posicao':0},{'posicao':181},{'posicao':4}):
                with self.assertRaises(DBAPIError):
                    SimuladoRascunhoItem(**{**valores,**mudanca}).salvar(confirmar=False)
                db.session.rollback()
            with self.assertRaises(DBAPIError):
                SimuladoResposta(tentativa_id=t['id'],item_id=t['itens'][0]['item_id']).salvar(confirmar=False)
            db.session.rollback()

    def test_concorrencia_inicio_e_salvar_versus_finalizar(self):
        chave=str(uuid4());barreira=Barrier(2)
        def iniciar(_):
            with self.app.app_context():
                barreira.wait(timeout=10)
                return IniciarSimuladoService.executar(self.usuario,{'simulado_versao_id':self.v,'chave_envio':chave})
        with ThreadPoolExecutor(max_workers=2) as pool:resultados=list(pool.map(iniciar,range(2)))
        self.assertEqual(sorted(r[1] for r in resultados),[200,201]);self.assertEqual(resultados[0][0],resultados[1][0])
        t=resultados[0][0];barreira=Barrier(2)
        def competir(salvar):
            with self.app.app_context():
                barreira.wait(timeout=10)
                try:
                    if salvar:return ResponderSimuladoService.executar(self.usuario,t['id'],t['itens'][0]['item_id'],{'revisao':1,'alternativa':'A'})
                    return FinalizarSimuladoService.executar(self.usuario,t['id'],{'revisao':1,'confirmar':True})
                except ConflitoError:return 409
        with ThreadPoolExecutor(max_workers=2) as pool:r=list(pool.map(competir,[True,False]))
        self.assertEqual(r.count(409),1)
