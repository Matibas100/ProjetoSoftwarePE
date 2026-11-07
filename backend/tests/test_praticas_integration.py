"""Prática, propriedade, persistência e concorrência no MySQL real."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from uuid import uuid4

from sqlalchemy import event, text
from app.extensions import db
from app.modules.praticas.models.pratica_tentativa import PraticaTentativa
from app.core.relogio import agora_utc
from app.exceptions import ConflitoError
from app.modules.praticas.services.iniciar_pratica_service import IniciarPraticaService
from app.modules.praticas.services.responder_pratica_service import ResponderPraticaService
from app.modules.praticas.services.listar_praticas_service import ConsultarFatosPraticasService
from tests.integration_support import MySQLIntegrationTestCase


class PraticasIntegrationTest(MySQLIntegrationTestCase):
    def setUp(self):
        self.senha = 'Senha segura de teste 123'
        self.aluno, self.usuario, self.email = self.conta()
        self.outro, self.outro_id, _ = self.conta()
        m = self.client.post('/api/materias', json={'nome':'Prática '+uuid4().hex,'area_enem_id':4}).get_json()
        a = self.client.post('/api/assuntos', json={'nome':'Assunto '+uuid4().hex,'materia_id':m['id']}).get_json()
        self.materia, self.assunto = m, a
        dados = {c:'Conteúdo '+c for c in ['enunciado','alternativa_a','alternativa_b','alternativa_c','alternativa_d','alternativa_e']}
        dados.update(assunto_id=a['id'], resposta_correta='A', explicacao=None, dificuldade='media')
        self.questao = self.client.post('/api/questoes', json=dados).get_json()
        self.qpath = '/api/questoes/'+str(self.questao['id'])
        ator = self.client.get('/api/auth/sessao').get_json()['usuario']['id']
        with self.app.app_context():
            db.session.execute(text('UPDATE sessoes SET reautenticada_em=:agora WHERE usuario_id=:id'),{'agora':agora_utc(),'id':ator})
            db.session.commit()
        self.versao = self.publicar(1)

    def conta(self):
        cliente = self.app.test_client()
        cliente.csrf = cliente.get('/api/auth/csrf').get_json()['csrf_token']
        email = uuid4().hex+'@teste.local'
        from app.modules.contas.domain.privacidade import VIGENTES
        r = cliente.post('/api/auth/cadastro', json={'nome':'Estudante','email':email,'senha':self.senha,'senha_confirmacao':self.senha,
            'termos_uso':{'versao':VIGENTES['uso'],'aceito':True}})
        self.assertEqual(r.status_code,201)
        r = cliente.post('/api/auth/login', json={'email':email,'senha':self.senha})
        self.assertEqual(r.status_code,200)
        cliente.csrf = r.get_json()['csrf_token']
        return cliente, r.get_json()['usuario']['id'], email

    def publicar(self, revisao):
        r = self.client.post(self.qpath+'/publicar',json={'revisao':revisao,'confirmar':True,'motivo':'Revisão de teste'})
        self.assertEqual(r.status_code,200)
        return r.get_json()['versao_publicada_id']

    def iniciar(self, chave=None, versao=None):
        return self.aluno.post('/api/aluno/praticas',json={'questao_versao_id':versao or self.versao,'chave_envio':chave or str(uuid4())})

    def responder(self, tentativa, alternativa='A'):
        return self.aluno.post(f'/api/aluno/praticas/{tentativa}/resposta',json={'alternativa':alternativa})

    def test_selecao_segura_paginacao_e_catalogo_indisponivel(self):
        url='/api/aluno/questoes'
        filtros={'materia_id':self.materia['id'],'assunto_id':self.assunto['id'],'por_pagina':1}
        r=self.aluno.get(url,query_string=filtros)
        self.assertEqual(r.status_code,200)
        dados=r.get_json(); self.assertEqual(dados['total_itens'],1)
        item=dados['itens'][0]; self.assertEqual(item['questao_versao_id'],self.versao)
        self.assertNotIn('resposta_correta',item); self.assertNotIn('explicacao',item)
        self.assertEqual(r.headers['Cache-Control'],'no-store')
        filtros['pagina']=2
        self.assertEqual(self.aluno.get(url,query_string=filtros).get_json()['itens'],[])
        self.assertEqual(self.client.post(f"/api/assuntos/{self.assunto['id']}/inativar").status_code,200)
        filtros['pagina']=1
        self.assertEqual(self.aluno.get(url,query_string=filtros).get_json()['itens'],[])
        self.assertEqual(self.iniciar().status_code,409)

    def test_permissoes_filtros_invalidos_head_csrf_e_rotas_legadas(self):
        for url in ['/api/aluno/questoes','/api/aluno/praticas','/api/aluno/praticas/1']:
            self.assertEqual(self.app.test_client().get(url).status_code,401)
            self.assertEqual(self.client.get(url).status_code,403)
            self.assertEqual(self.aluno.head(url).status_code,404 if url.endswith('/1') else 200)
        for url in ['/api/aluno/questoes','/api/aluno/praticas']:
            for filtro in [{'pagina':''},{'pagina':0},{'por_pagina':101},{'assunto_id':'x'},
                           {'usuario_id':self.outro_id},{'assunto_id':-1},{'assunto_id':'1.5'}]:
                self.assertEqual(self.aluno.get(url,query_string=filtro).status_code,400)
            self.assertEqual(self.aluno.get(url+'?pagina=1&pagina=2').status_code,400)
        self.assertEqual(self.aluno.get('/api/questoes/por-assunto?assunto_id=1').status_code,403)
        corpo={'questao_versao_id':self.versao,'chave_envio':str(uuid4())}
        self.assertEqual(self.aluno.post('/api/aluno/praticas',json=corpo,headers={'X-CSRF-Token':'errado'}).status_code,403)
        self.assertEqual(self.aluno.post('/api/aluno/praticas',json=corpo,headers={'Origin':'https://outra.test'}).status_code,403)
        self.assertEqual(self.aluno.get('/api/aluno/inexistente').status_code,404)
        self.assertEqual(self.aluno.put('/api/aluno/praticas').status_code,405)

    def test_inicio_replay_versao_superada_e_repeticao_real(self):
        chave=str(uuid4()); r=self.iniciar(chave); self.assertEqual(r.status_code,201)
        t=r.get_json(); self.assertNotIn('gabarito',t); self.assertNotIn('explicacao',t['questao'])
        replay=self.iniciar(chave.upper()); self.assertEqual(replay.status_code,200); self.assertEqual(replay.get_json(),t)
        self.assertNotEqual(self.iniciar().get_json()['id'],t['id'])
        self.assertEqual(self.client.put(self.qpath,json={'revisao':1,'resposta_correta':'B','enunciado':'Nova revisão'}).status_code,200)
        nova=self.publicar(2)
        self.assertEqual(self.iniciar(chave, nova).status_code,409)
        self.assertEqual(self.iniciar().status_code,409)
        self.assertEqual(self.iniciar(chave).get_json(),t)
        self.assertEqual(self.iniciar(versao=2147483647).status_code,404)
        self.assertEqual(self.responder(t['id']).get_json()['gabarito'],'A')

    def test_resposta_definitiva_historico_fatos_e_novo_login(self):
        ids=[]
        for alternativa in 'ABCDE':
            t=self.iniciar().get_json()['id']; ids.append(t)
            r=self.responder(t,alternativa); self.assertEqual(r.status_code,200)
            dados=r.get_json(); self.assertEqual(dados['correta'],alternativa=='A')
            self.assertIsNone(dados['explicacao']); self.assertTrue(dados['respondida_em'].endswith('Z'))
            self.assertEqual(self.responder(t,alternativa).get_json(),dados)
            self.assertEqual(self.responder(t,'B' if alternativa=='A' else 'A').status_code,409)
            self.assertEqual(self.aluno.get(f'/api/aluno/praticas/{t}').get_json(),dados)
        self.iniciar()  # Em andamento nunca integra histórico/fatos.
        url='/api/aluno/praticas?assunto_id='+str(self.assunto['id'])
        historico=self.aluno.get(url).get_json()
        self.assertEqual([t['id'] for t in historico['itens']],ids[::-1])
        self.assertEqual(self.aluno.get(url+'&por_pagina=2&pagina=2').get_json()['itens'][0]['id'],ids[2])
        with self.app.app_context():
            agora=agora_utc(); fatos=ConsultarFatosPraticasService.executar(self.usuario,agora-timedelta(days=1),agora)
            self.assertEqual([f['id'] for f in fatos],ids)
            self.assertEqual(sum(f['correta'] for f in fatos),1)
            self.assertEqual(ConsultarFatosPraticasService.executar(self.outro_id,agora-timedelta(days=1),agora),[])
            self.assertEqual(ConsultarFatosPraticasService.executar(self.usuario,agora,agora+timedelta(days=1)),[])
        self.assertEqual(self.aluno.post('/api/auth/logout').status_code,204)
        self.aluno.csrf=self.aluno.get('/api/auth/csrf').get_json()['csrf_token']
        r=self.aluno.post('/api/auth/login',json={'email':self.email,'senha':self.senha})
        self.assertEqual(r.status_code,200); self.aluno.csrf=r.get_json()['csrf_token']
        self.assertEqual(self.aluno.get(url).get_json(),historico)

    def test_propriedade_e_classificacao_historica_apos_transferencia_arquivamento(self):
        t=self.iniciar().get_json()['id']
        path=f'/api/aluno/praticas/{t}'
        ausente=self.outro.get('/api/aluno/praticas/9223372036854775807')
        self.assertEqual(self.outro.get(path).get_json(),ausente.get_json())
        self.assertEqual(self.outro.post(path+'/resposta',json={'alternativa':'A'}).status_code,404)
        self.assertEqual(self.outro.get('/api/aluno/praticas').get_json()['itens'],[])
        m=self.client.post('/api/materias',json={'nome':'Destino '+uuid4().hex,'area_enem_id':4}).get_json()
        # Exercita mudança real do catálogo e retirada de uso da versão capturada.
        with self.app.app_context():
            db.session.execute(text('UPDATE assuntos SET materia_id=:m,nome=:nome WHERE id=:a'),
                {'m':m['id'],'a':self.assunto['id'],'nome':'Nome novo'})
            db.session.execute(text('UPDATE materias SET nome=:nome WHERE id=:m'),{'m':self.materia['id'],'nome':'Renomeada '+uuid4().hex})
            db.session.commit()
        self.assertEqual(self.client.post(self.qpath+'/arquivar',json={'revisao':1,'confirmar':True,'motivo':'Retirada de teste'}).status_code,200)
        r=self.responder(t).get_json()
        self.assertEqual(r['materia']['nome'],self.materia['nome'])
        self.assertEqual(r['assunto']['nome'],self.assunto['nome'])
        self.assertEqual(r['questao']['enunciado'],self.questao['enunciado'])
        self.assertEqual(self.iniciar().status_code,409)

    def test_entradas_invalidas_e_rollback_real_antes_do_commit(self):
        for corpo in [None,{},[],{'questao_versao_id':True,'chave_envio':str(uuid4())},
            {'questao_versao_id':self.versao,'chave_envio':'invalida'},
            {'questao_versao_id':self.versao,'chave_envio':None},
            {'questao_versao_id':self.versao,'chave_envio':str(uuid4()),'usuario_id':self.usuario}]:
            self.assertEqual(self.aluno.post('/api/aluno/praticas',json=corpo).status_code,400)
        t=self.iniciar().get_json()['id']; path=f'/api/aluno/praticas/{t}'
        for corpo in [None,{},[],{'alternativa':'a'},{'alternativa':None},{'alternativa':[]},
                      {'alternativa':'AA'},{'alternativa':'A','correta':True}]:
            self.assertEqual(self.aluno.post(path+'/resposta',json=corpo).status_code,400)
        def falhar(mapper, connection, target):
            raise RuntimeError('Falha controlada no flush real')
        event.listen(PraticaTentativa,'after_update',falhar)
        try:
            self.assertEqual(self.responder(t).status_code,500)
        finally:
            event.remove(PraticaTentativa,'after_update',falhar)
        self.assertEqual(self.aluno.get(path).get_json()['estado'],'em_andamento')
        self.assertEqual(self.responder(t).status_code,200)
        event.listen(PraticaTentativa,'after_insert',falhar)
        chave=str(uuid4())
        try:
            self.assertEqual(self.iniciar(chave).status_code,500)
        finally:
            event.remove(PraticaTentativa,'after_insert',falhar)
        self.assertEqual(self.iniciar(chave).status_code,201)

    def test_concorrencia_inicio_e_respostas_iguais_ou_conflitantes(self):
        chave=str(uuid4()); barreira=Barrier(2)
        def iniciar(_):
            with self.app.app_context():
                barreira.wait(timeout=10)
                return IniciarPraticaService.executar(self.usuario,{'questao_versao_id':self.versao,'chave_envio':chave})
        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados=list(pool.map(iniciar,range(2)))
        self.assertEqual(sorted(r[1] for r in resultados),[200,201])
        self.assertEqual(resultados[0][0]['id'],resultados[1][0]['id'])
        for alternativas in [('A','A'),('A','B')]:
            t=self.iniciar().get_json()['id']; barreira=Barrier(2)
            def responder(alternativa):
                with self.app.app_context():
                    barreira.wait(timeout=10)
                    try:
                        return ResponderPraticaService.executar(self.usuario,t,{'alternativa':alternativa})
                    except ConflitoError:
                        return 409
            with ThreadPoolExecutor(max_workers=2) as pool:
                respostas=list(pool.map(responder,alternativas))
            if alternativas[0]==alternativas[1]:
                self.assertEqual(respostas[0],respostas[1])
            else:
                self.assertEqual(respostas.count(409),1)
            self.assertEqual(self.aluno.get(f'/api/aluno/praticas/{t}').get_json()['estado'],'respondida')
