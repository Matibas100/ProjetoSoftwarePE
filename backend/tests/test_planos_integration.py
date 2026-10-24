"""Plano sobre diagnóstico real, sem substitutos para MySQL ou APIs de prática."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4
from sqlalchemy import event, select, text
from app.extensions import db
from app.exceptions import ConflitoError
from app.models.plano_estudo import PlanoEstudo as Plano, PlanoEstudoItem as Item
from app.services.gerar_plano_service import GerarPlanoService
from app.services.recalcular_plano_service import RecalcularPlanoService
from app.services.concluir_plano_item_service import ConcluirPlanoItemService
from tests.integration_support import MySQLIntegrationTestCase
from tests import test_praticas_integration as fixture


class PlanosIntegrationTest(MySQLIntegrationTestCase):
    conta = fixture.PraticasIntegrationTest.conta
    publicar = fixture.PraticasIntegrationTest.publicar
    setUp = fixture.PraticasIntegrationTest.setUp
    url = '/api/aluno/plano'

    def base(self, acertos=2, total=5, versao=None):
        for n in range(total):
            t=self.aluno.post('/api/aluno/praticas',json={'questao_versao_id':versao or self.versao,'chave_envio':str(uuid4())})
            self.assertEqual(t.status_code,201)
            r=self.aluno.post(f"/api/aluno/praticas/{t.json['id']}/resposta",json={'alternativa':'A' if n < acertos else 'B'})
            self.assertEqual(r.status_code,200)

    def gerar(self, chave=None):
        return self.aluno.post(self.url+'/gerar',json={'chave_envio':chave or str(uuid4())})

    def recalcular(self, plano, chave=None):
        return self.aluno.post(self.url+'/recalcular',json={'chave_envio':chave or str(uuid4()),'plano_atual_id':plano['id'],'confirmar':True})

    def concluir(self, item, cliente=None):
        return (cliente or self.aluno).post(self.url+f"/itens/{item}/concluir",json={'confirmar':True})

    def test_get_sem_gravacao_amostra_insuficiente_e_geracao_replay(self):
        self.assertEqual(self.aluno.get(self.url).json,{'estado':'sem_plano','plano':None})
        self.base(total=4)
        self.assertEqual(self.gerar().json,{'estado':'sem_base_suficiente','plano':None})
        self.base(acertos=0,total=1)
        chave=str(uuid4());r=self.gerar(chave);self.assertEqual(r.status_code,201)
        p=r.json['plano'];self.assertEqual(p['geracao'],1);self.assertTrue(p['atual'])
        self.assertEqual(p['itens'][0]['snapshot']['total_respostas'],5)
        self.assertEqual(p['itens'][0]['snapshot']['acertos'],2)
        self.assertEqual(p['itens'][0]['snapshot']['percentual_acerto'],40)
        self.assertEqual(self.gerar(chave).status_code,200);self.assertEqual(self.gerar(chave).json,r.json)
        self.assertEqual(self.aluno.get(self.url).json,r.json);self.assertEqual(self.gerar().status_code,409)
        self.assertEqual(self.recalcular(p,chave).status_code,409)
        self.assertEqual(self.outro.get(self.url).json,{'estado':'sem_plano','plano':None})
        with self.app.app_context():
            self.assertEqual(db.session.execute(select(Plano).where(Plano.usuario_id==self.usuario)).scalars().all().__len__(),1)

    def test_ordenacao_real_limite_e_disponibilidade_classificacao(self):
        versoes=[self.versao];ids=[self.assunto['id']]
        for n in range(4):
            a=self.client.post('/api/assuntos',json={'nome':'Prioridade '+uuid4().hex,'materia_id':self.materia['id']}).json;ids.append(a['id'])
            dados={k:'Conteúdo' for k in ('enunciado','alternativa_a','alternativa_b','alternativa_c','alternativa_d','alternativa_e')}
            dados.update(assunto_id=a['id'],resposta_correta='A',dificuldade='media')
            q=self.client.post('/api/questoes',json=dados).json
            v=self.client.post(f"/api/questoes/{q['id']}/publicar",json={'revisao':1,'confirmar':True,'motivo':'Publicação de teste'}).json
            versoes.append(v['versao_publicada_id'])
        for v,(acertos,total) in zip(versoes,[(2,10),(1,5),(4,10),(0,4),(5,5)]):self.base(acertos,total,v)
        p=self.gerar().json['plano'];self.assertEqual([i['assunto_id'] for i in p['itens']],ids[:3])
        # Sem alteração automática ao chegar outra resposta.
        self.base(0,1,versoes[1]);self.assertEqual(self.aluno.get(self.url).json['plano'],p)
        novo=self.recalcular(p).json['plano'];self.assertEqual(novo['itens'][0]['assunto_id'],ids[1])

    def test_conclusao_manual_replay_indisponibilidade_e_historico(self):
        self.base();p=self.gerar().json['plano'];i=p['itens'][0]['id']
        antes=self.aluno.get('/api/aluno/desempenho').json
        c=self.concluir(i);self.assertEqual(c.status_code,200);self.assertEqual(c.json['estado'],'concluido')
        self.assertEqual(self.concluir(i).json,c.json)
        depois=self.aluno.get('/api/aluno/desempenho').json
        for k in ['geral','base','assuntos','materias']:self.assertEqual(antes[k],depois[k])
        self.client.post(self.qpath+'/arquivar',json={'revisao':1,'confirmar':True,'motivo':'Retirada de teste'})
        retirado=self.aluno.get(self.url).json['plano'];self.assertEqual(retirado['itens'][0]['snapshot'],p['itens'][0]['snapshot'])
        self.assertFalse(retirado['itens'][0]['disponivel_para_pratica'])
        r=self.recalcular(p);self.assertEqual(r.status_code,200);self.assertEqual(r.json['estado'],'sem_base_suficiente')
        self.assertEqual(r.json['plano'],retirado)
        self.assertEqual(self.aluno.get(self.url).json['plano'],retirado)

    def test_recalculo_preserva_conclusoes_replay_historico_e_chave_divergente(self):
        self.base();chave=str(uuid4());p=self.gerar(chave).json['plano'];i=p['itens'][0]['id']
        c=self.concluir(i).json;self.base(0,1)
        nova_chave=str(uuid4());r=self.recalcular(p,nova_chave);self.assertEqual(r.status_code,201)
        novo=r.json['plano'];self.assertEqual(novo['geracao'],2);self.assertEqual(novo['itens'][0]['estado'],'pendente')
        self.assertEqual(novo['itens'][0]['snapshot']['total_respostas'],6)
        self.assertEqual(self.recalcular(p,nova_chave).json,r.json);self.assertEqual(self.recalcular(p,nova_chave).status_code,200)
        self.assertEqual(self.recalcular(novo,nova_chave).status_code,409)
        self.assertEqual(self.recalcular(p).status_code,409)
        self.assertEqual(self.gerar(nova_chave).status_code,409)
        historico=self.gerar(chave).json['plano'];self.assertFalse(historico['atual'])
        self.assertEqual(historico['itens'][0],c)
        self.assertEqual(self.concluir(i).status_code,409)

    def test_transferencia_e_catalogo_arquivado_nao_reclassificam_fatos(self):
        self.base()
        m=self.client.post('/api/materias',json={'nome':'Destino '+uuid4().hex,'area_enem_id':4}).json
        url=f"/api/assuntos/{self.assunto['id']}"
        previa=self.client.get(url+'/impacto-transferencia',query_string={'materia_destino_id':m['id']}).json
        self.assertEqual(self.client.post(url+'/transferir',json={'materia_destino_id':m['id'],'impacto_esperado':previa['impacto']}).status_code,200)
        self.assertEqual(self.gerar().json['estado'],'sem_base_suficiente')
        self.assertEqual(self.aluno.get('/api/aluno/desempenho').json['assuntos'][0]['materia_id'],self.materia['id'])
        self.client.put(self.qpath,json={'revisao':1,'enunciado':'Conteúdo novo'})
        self.versao=self.publicar(2);self.base(5,5)
        p=self.gerar().json['plano'];self.assertEqual(p['itens'][0]['materia_id'],m['id'])
        self.assertEqual(p['itens'][0]['snapshot']['percentual_acerto'],100)
        self.assertEqual(self.client.post(url+'/arquivar').status_code,200)
        self.assertFalse(self.aluno.get(self.url).json['plano']['itens'][0]['disponivel_para_pratica'])
        self.assertEqual(self.recalcular(p).json['estado'],'sem_base_suficiente')

    def test_http_estrito_perfis_csrf_propriedade_e_no_store(self):
        self.base();p=self.gerar().json['plano'];i=p['itens'][0]['id'];item=self.url+f'/itens/{i}/concluir'
        for url,metodo,dados in [(self.url,'get',None),(self.url+'/gerar','post',{}),(self.url+'/recalcular','post',{}),(item,'post',{'confirmar':True})]:
            for cliente,codigo in [(self.client,403),(self.app.test_client(),401)]:
                r=getattr(cliente,metodo)(url,json=dados);self.assertEqual(r.status_code,codigo);self.assertEqual(r.headers['Cache-Control'],'no-store')
        a=self.concluir(i,self.outro);b=self.concluir(9223372036854775807,self.outro)
        self.assertEqual((a.status_code,a.json),(b.status_code,b.json));self.assertEqual(a.status_code,404)
        for headers in [{'Origin':'http://evil.test'},{'X-CSRF-Token':'invalido'}]:self.assertEqual(self.aluno.post(item,json={'confirmar':True},headers=headers).status_code,403)
        for dados in [{},None,{'confirmar':False},{'confirmar':True,'usuario_id':self.usuario}]:
            self.assertEqual(self.aluno.post(item,json=dados).status_code,400)
        for dados in [{}, {'chave_envio':str(uuid4()),'taxa':1}, {'chave_envio':True}]:self.assertEqual(self.aluno.post(self.url+'/gerar',json=dados).status_code,400)
        self.assertEqual(self.aluno.get(self.url+'?usuario_id=1').status_code,400)
        self.assertEqual(self.aluno.get(self.url).headers['Cache-Control'],'no-store')
        dados={'chave_envio':str(uuid4()),'plano_atual_id':p['id'],'confirmar':True}
        for extra in [{'confirmar':False},{'plano_atual_id':False},{'prioridade':1}]:
            self.assertEqual(self.aluno.post(self.url+'/recalcular',json={**dados,**extra}).status_code,400)

    def test_falha_ultima_etapa_rollback_geracao_recalculo_e_diagnostico(self):
        self.base()
        with self.app.app_context():
            engine=db.engine
            def falhar(conexao,cursor,statement,parameters,context,executemany):
                if statement.startswith('INSERT INTO plano_estudo_itens'):raise RuntimeError('Falha controlada')
            event.listen(engine,'before_cursor_execute',falhar)
            try:self.assertEqual(self.gerar().status_code,500)
            finally:event.remove(engine,'before_cursor_execute',falhar)
        self.assertEqual(self.aluno.get(self.url).json['estado'],'sem_plano')
        p=self.gerar().json['plano'];self.concluir(p['itens'][0]['id']);antes=self.aluno.get(self.url).json
        for gatilho in ['INSERT INTO plano_estudo_itens','fatos AS']:
            with self.app.app_context():
                def falhar(conexao,cursor,statement,parameters,context,executemany):
                    if gatilho in statement:raise RuntimeError('Falha controlada')
                event.listen(engine,'before_cursor_execute',falhar)
                try:r=self.recalcular(p);self.assertEqual(r.status_code,500);self.assertNotIn('controlada',str(r.json))
                finally:event.remove(engine,'before_cursor_execute',falhar)
            self.assertEqual(self.aluno.get(self.url).json,antes)
        with self.app.app_context():self.assertEqual(db.session.execute(select(Plano).where(Plano.usuario_id==self.usuario)).scalars().all().__len__(),1)

    def disputa(self, operacao):
        barreira=Barrier(2)
        def executar(_):
            with self.app.app_context():
                barreira.wait(timeout=10)
                try:return operacao()
                except ConflitoError:return None,409
                finally:db.session.remove()
        with ThreadPoolExecutor(max_workers=2) as pool:return list(pool.map(executar,range(2)))

    def test_concorrencia_geracao_mesma_chave_e_distinta_e_recalculo(self):
        self.base();chave=str(uuid4())
        resultados=self.disputa(lambda:GerarPlanoService.executar(self.usuario,{'chave_envio':chave}))
        self.assertEqual(sorted(r[1] for r in resultados),[200,201])
        p=resultados[0][0]['plano']
        resultados=self.disputa(lambda:RecalcularPlanoService.executar(self.usuario,{'chave_envio':str(uuid4()),'plano_atual_id':p['id'],'confirmar':True}))
        self.assertEqual(sorted(r[1] for r in resultados),[201,409])
        self.base(total=5)
        # Outra identidade possui base própria e duas chaves de geração disputam.
        with self.app.app_context():
            db.session.execute(text('UPDATE pratica_tentativas SET usuario_id=:outro WHERE usuario_id=:u'),{'outro':self.outro_id,'u':self.usuario});db.session.commit()
        resultados=self.disputa(lambda:GerarPlanoService.executar(self.outro_id,{'chave_envio':str(uuid4())}))
        self.assertEqual(sorted(r[1] for r in resultados),[201,409])

    def test_snapshot_transacional_exclui_resposta_concorrente_e_preserva_imutabilidade(self):
        self.base()
        t=self.aluno.post('/api/aluno/praticas',json={'questao_versao_id':self.versao,'chave_envio':str(uuid4())}).json
        with self.app.app_context():
            engine=db.engine;inseriu=[]
            def responder(conexao,cursor,statement,parameters,context,executemany):
                if 'fatos AS' in statement and not inseriu:
                    inseriu.append(True)
                    with engine.begin() as outra:
                        outra.execute(text("UPDATE pratica_tentativas SET estado='respondida',resposta_escolhida='B',correta=0,respondida_em=UTC_TIMESTAMP(6) WHERE id=:i"),{'i':t['id']})
            event.listen(engine,'after_cursor_execute',responder)
            try:r=self.gerar();self.assertEqual(r.status_code,201)
            finally:event.remove(engine,'after_cursor_execute',responder)
        self.assertEqual(r.json['plano']['itens'][0]['snapshot']['total_respostas'],5)
        self.assertEqual(self.aluno.get('/api/aluno/desempenho').json['geral']['total_respostas'],6)
        with self.app.app_context():
            p=db.session.get(Plano,r.json['plano']['id']);i=db.session.get(Item,r.json['plano']['itens'][0]['id'])
            for entidade,campo,valor in [(p,'geracao',99),(i,'snapshot',{'justificativa':'adulterado'})]:
                setattr(entidade,campo,valor)
                with self.assertRaises(ConflitoError):db.session.flush()
                db.session.rollback()
            for entidade in [p,i]:
                db.session.delete(entidade)
                with self.assertRaises(ConflitoError):db.session.flush()
                db.session.rollback()
            ConcluirPlanoItemService.executar(self.usuario,i.id,{'confirmar':True})
            i.concluido_em=None
            with self.assertRaises(ConflitoError):db.session.flush()
            db.session.rollback()
