"""Gestão administrativa com HTTP, FKs, falhas e concorrência MySQL reais."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from threading import Event
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from werkzeug.security import check_password_hash
from app.extensions import db
from app.core.relogio import agora_utc
from app.contexto_leitura import ContextoLeitura
from app.modules.contas.models.usuario import Usuario
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.repositories.usuario_repository import UsuarioRepository
from app.modules.contas.services.autenticacao_service import CriarSessaoService, ValidarSenhaService
from app.modules.contas.services.atualizar_aluno_admin_service import AtualizarAlunoAdminService
from app.modules.contas.services.desativar_aluno_service import DesativarAlunoService
from app.modules.contas.services.excluir_aluno_admin_service import ExcluirAlunoAdminService
from tests.integration_support import MySQLIntegrationTestCase

BASE='/api/admin/usuarios'
SENHA='Senha sintética 123'


class GestaoAlunosIntegrationTest(MySQLIntegrationTestCase):
    def criar(self,nome='Aluno sintético'):
        dados={'nome':nome,'email':uuid4().hex+'@teste.local','senha':SENHA,'senha_confirmacao':SENHA}
        r=self.client.post(BASE,json=dados)
        self.assertEqual(r.status_code,201,r.json)
        return r.json

    def entrar(self,aluno):
        c=self.app.test_client()
        token=c.get('/api/auth/csrf').json['csrf_token']
        r=c.post('/api/auth/login',json={'email':aluno['email'],'senha':SENHA},
            headers={'Origin':'http://frontend.test','X-CSRF-Token':token})
        self.assertEqual(r.status_code,200,r.json)
        c.csrf=r.json['csrf_token']
        return c

    def test_crud_sem_sessao_aceite_e_contratos(self):
        operador=self.client.get('/api/auth/sessao').json['usuario']
        aluno=self.criar('  Novo aluno  ')
        uid=aluno['id']
        self.assertEqual(set(aluno),{'id','nome','email','perfil','ativo','criado_em'})
        self.assertEqual(aluno['nome'],'Novo aluno')
        self.assertEqual(aluno['perfil'],'aluno')
        self.assertTrue(aluno['criado_em'].endswith('Z'))
        with self.app.app_context():
            u=Usuario.buscar_por_id(uid)
            self.assertTrue(check_password_hash(u.senha_hash,SENHA))
            for tabela in ['sessoes','registros_privacidade']:
                self.assertEqual(db.session.execute(text(f'SELECT COUNT(*) FROM {tabela} WHERE usuario_id=:id'),{'id':uid}).scalar(),0)
        self.assertEqual(self.client.get('/api/auth/sessao').json['usuario'],operador)
        self.assertEqual(self.client.get(f'{BASE}/{uid}').json,aluno)
        dados={'nome':'Nome corrigido','email':aluno['email'].upper()}
        self.assertEqual(self.client.put(f'{BASE}/{uid}',json=dados).status_code,200)
        r=self.client.get(BASE,query_string={'busca':aluno['email'],'por_pagina':1})
        self.assertEqual(r.json['total_itens'],1)
        self.assertEqual(set(r.json['itens'][0]),{'id','nome','email_mascarado','perfil','ativo','criado_em'})
        self.assertNotIn(aluno['email'],r.get_data(as_text=True))
        self.assertEqual(self.client.head(f'{BASE}/{uid}').data,b'')
        self.assertEqual(self.client.delete(f'{BASE}/{uid}',json={'confirmar':True}).status_code,204)
        self.assertEqual(self.client.get(f'{BASE}/{uid}').status_code,404)

    def test_autorizacao_corpos_filtros_ids_e_no_store(self):
        anonimo=self.app.test_client()
        for metodo in ['get','post','put','delete','head']:
            caminho=BASE if metodo in ['get','post'] else BASE+'/1'
            r=getattr(anonimo,metodo)(caminho,data=b'x'*17000,content_type='application/json')
            self.assertEqual(r.status_code,401)
            self.assertEqual(r.headers['Cache-Control'],'no-store')
        aluno=self.criar()
        estudante=self.entrar(aluno)
        self.assertEqual(estudante.get(BASE).status_code,403)
        self.assertEqual(estudante.post(BASE,data=b'{',content_type='application/json').status_code,403)
        admin=self.client.get('/api/auth/sessao').json['usuario']['id']
        for uid in [admin,2147483647]:
            for metodo in ['get','put','delete']:
                r=getattr(self.client,metodo)(f'{BASE}/{uid}',json={'confirmar':True})
                self.assertEqual(r.status_code,404)
                self.assertEqual(r.json['codigo'],'usuario_nao_encontrado')
        for uid in [0,2147483648]: self.assertEqual(self.client.get(f'{BASE}/{uid}').status_code,400)
        for uid in ['-1','abc']: self.assertEqual(self.client.get(f'{BASE}/{uid}').status_code,404)
        for filtros in [{'perfil':'aluno'},{'status':'x'},{'pagina':''},{'pagina':'1.1'},{'por_pagina':'101'},{'busca':'x'*255}]:
            self.assertEqual(self.client.get(BASE,query_string=filtros).status_code,400)
        for dados in [[],None,{'perfil':'administrador'},{'confirmar':False}]:
            self.assertEqual(self.client.post(BASE,json=dados).status_code,400)
        self.assertEqual(self.client.post(BASE,data=b'x'*17000,content_type='application/json').status_code,413)
        self.assertEqual(self.client.post(BASE,data=b'{',content_type='application/json').status_code,400)
        self.assertEqual(self.client.options(BASE).status_code,200)
        r=self.client.post(BASE,json={},headers={'Origin':'http://invalida.test'})
        self.assertEqual(r.json['codigo'],'origem_nao_permitida')
        r=self.client.post(BASE,json={},headers={'X-CSRF-Token':'invalido'})
        self.assertEqual(r.json['codigo'],'csrf_invalido')
        with self.app.app_context():
            db.session.execute(text('UPDATE sessoes SET reautenticada_em=:data WHERE usuario_id=:id'),
                {'data':agora_utc()-timedelta(minutes=16),'id':admin})
            db.session.commit()
        try:
            self.assertEqual(self.client.post(BASE,json={}).json['codigo'],'reautenticacao_necessaria')
        finally:
            with self.app.app_context():
                db.session.execute(text('UPDATE sessoes SET reautenticada_em=:data WHERE usuario_id=:id'),{'data':agora_utc(),'id':admin})
                db.session.commit()

    def test_nome_noop_email_sessoes_status_e_vinculos(self):
        aluno=self.criar()
        uid=aluno['id']
        c1,c2=self.entrar(aluno),self.entrar(aluno)
        for nome in [aluno['nome'],'Outro nome']:
            self.assertEqual(self.client.put(f'{BASE}/{uid}',json={'nome':nome,'email':aluno['email']}).status_code,200)
            self.assertEqual(c1.get('/api/auth/sessao').status_code,200)
        novo=uuid4().hex+'@teste.local'
        self.assertEqual(self.client.put(f'{BASE}/{uid}',json={'nome':'Outro nome','email':novo}).status_code,200)
        for c in [c1,c2]: self.assertEqual(c.get('/api/auth/sessao').status_code,401)
        aluno['email']=novo
        c1=self.entrar(aluno)
        self.assertEqual(self.client.delete(f'{BASE}/{uid}',json={'confirmar':True}).json['codigo'],'usuario_com_vinculos')
        for _ in range(2):
            r=self.client.post(f'{BASE}/{uid}/desativar',json={'confirmar':True})
            self.assertFalse(r.json['ativo'])
        self.assertEqual(c1.get('/api/auth/sessao').status_code,401)
        r=self.client.post(f'{BASE}/{uid}/reativar',json={'confirmar':True})
        self.assertTrue(r.json['ativo'])
        self.assertEqual(c1.get('/api/auth/sessao').status_code,401)
        self.assertEqual(self.entrar(aluno).get('/api/auth/sessao').status_code,200)
        with self.app.app_context():
            self.assertGreater(db.session.execute(text('SELECT COUNT(*) FROM sessoes WHERE usuario_id=:id AND revogada_em IS NOT NULL'),{'id':uid}).scalar(),1)

    def test_snapshot_literal_total_e_lock_corrente(self):
        a=self.criar('Nome %_\\ literal')
        uid=a['id']
        r=self.client.get(BASE,query_string={'busca':'%_\\'})
        self.assertEqual([x['id'] for x in r.json['itens']],[uid])
        r=self.client.get(BASE,query_string={'busca':a['email'],'pagina':99})
        self.assertEqual(r.json['itens'],[])
        self.assertEqual(r.json['total_itens'],1)
        with self.app.app_context():
            with ContextoLeitura() as ctx:
                antes=ctx.executar_resultados('CALL sp_alunos_admin(%s,%s,%s,%s)',(a['email'],None,0,20))
                with db.engine.begin() as outra:
                    outra.execute(text('UPDATE usuarios SET nome=:nome,ativo=0 WHERE id=:id'),{'nome':'Corrente','id':uid})
                depois=ctx.executar_resultados('CALL sp_alunos_admin(%s,%s,%s,%s)',(a['email'],None,0,20))
                self.assertEqual(antes,depois)
            antigo=Usuario.buscar_por_id(uid)
            with db.engine.begin() as outra:
                outra.execute(text('UPDATE usuarios SET nome=:nome WHERE id=:id'),{'nome':'Mais recente','id':uid})
            corrente=UsuarioRepository.bloquear(uid)
            self.assertIs(corrente,antigo)
            self.assertEqual(corrente.nome,'Mais recente')
            self.assertFalse(corrente.ativo)
            db.session.rollback()

    def test_duplicidade_concorrente_e_rollback_real_revogacao_commit(self):
        a,b=self.criar(),self.criar()
        uid=a['id']
        self.entrar(a)
        barreira=Barrier(2)
        email=uuid4().hex+'@teste.local'
        def editar(aluno):
            with self.app.app_context():
                barreira.wait(timeout=10)
                try:
                    AtualizarAlunoAdminService.executar(aluno['id'],{'nome':'Concorrente','email':email})
                    return 200
                except AutenticacaoError as e: return e.status_code
        with ThreadPoolExecutor(2) as pool:
            self.assertEqual(sorted(pool.map(editar,[a,b])),[200,409])
        with self.app.app_context():
            atual=Usuario.buscar_por_id(uid)
            email_atual=atual.email
            db.session.remove()
            engine=db.engine
            for acao in ['email','status']:
                with engine.begin() as ddl:
                    ddl.exec_driver_sql("CREATE TRIGGER falhar_gestao BEFORE UPDATE ON sessoes FOR EACH ROW "
                        "SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Falha sintética'")
                # A sessão anterior pode ter sido revogada pela corrida; criar uma nova.
                try:
                    usuario=Usuario.buscar_por_id(uid)
                    CriarSessaoService.executar(usuario)
                    try:
                        if acao=='status': DesativarAlunoService.executar(uid,{'confirmar':True})
                        else: AtualizarAlunoAdminService.executar(uid,{'nome':'Parcial','email':uuid4().hex+'@teste.local'})
                    except Exception: pass
                    else: self.fail('A falha real deveria reverter a operação.')
                    db.session.remove()
                    self.assertEqual(Usuario.buscar_por_id(uid).email,email_atual)
                    self.assertTrue(Usuario.buscar_por_id(uid).ativo)
                    self.assertGreater(db.session.execute(text('SELECT COUNT(*) FROM sessoes WHERE usuario_id=:id AND revogada_em IS NULL'),{'id':uid}).scalar(),0)
                finally:
                    db.session.remove()
                    with engine.begin() as ddl: ddl.exec_driver_sql('DROP TRIGGER falhar_gestao')

    def test_login_antigo_nos_dois_intervalos_e_desativacao(self):
        for etapa in ['senha','sessao','desativar']:
            a=self.criar()
            with self.app.app_context():
                antigo=Usuario.buscar_por_id(a['id'])
                if etapa!='senha':
                    ValidarSenhaService.executar(antigo,SENHA,uuid4().hex*2,email_esperado=a['email'])
                # Uma segunda transação confirma a mutação entre as etapas reais do login.
                def mudar():
                    with self.app.app_context():
                        if etapa=='desativar': DesativarAlunoService.executar(a['id'],{'confirmar':True})
                        else: AtualizarAlunoAdminService.executar(a['id'],{'nome':'Alterado','email':uuid4().hex+'@teste.local'})
                with ThreadPoolExecutor(1) as pool: pool.submit(mudar).result(timeout=10)
                with self.assertRaises(AutenticacaoError):
                    if etapa=='senha': ValidarSenhaService.executar(antigo,SENHA,uuid4().hex*2,email_esperado=a['email'])
                    else: CriarSessaoService.executar(antigo,email_esperado=a['email'])
                self.assertEqual(db.session.execute(text('SELECT COUNT(*) FROM sessoes WHERE usuario_id=:id'),{'id':a['id']}).scalar(),0)

    def test_fk_aceite_autoria_e_lock_transitorio(self):
        a=self.criar()
        uid=a['id']
        with self.app.app_context():
            usuario=UsuarioRepository.bloquear(uid)
            def excluir_bloqueado():
                with self.app.app_context():
                    db.session.execute(text('SET innodb_lock_wait_timeout=1'))
                    try: ExcluirAlunoAdminService.executar(uid,{'confirmar':True})
                    except AutenticacaoError as e: return e.codigo
            with ThreadPoolExecutor(1) as pool:
                self.assertEqual(pool.submit(excluir_bloqueado).result(timeout=6),'operacao_concorrente')
            db.session.rollback()
            with db.engine.begin() as c:
                c.execute(text("INSERT INTO registros_privacidade(usuario_id,tipo,acao,versao,documento_sha256,chave_envio,revisao_base,registrado_em) "
                    "VALUES(:id,'uso','aceitar','2.0',:hash,:chave,0,UTC_TIMESTAMP(6))"),{'id':uid,'hash':'a'*64,'chave':str(uuid4())})
        self.assertEqual(self.client.delete(f'{BASE}/{uid}',json={'confirmar':True}).json['codigo'],'usuario_com_vinculos')

    def test_routine_ausente_e_erro_sanitizado(self):
        a=self.criar()
        with self.app.app_context():
            engine=db.engine
            for nome in ['sp_alunos_admin','sp_usuario_gestao_bloqueado']:
                with engine.begin() as c:
                    original=c.exec_driver_sql('SHOW CREATE PROCEDURE '+nome).one()._mapping['Create Procedure']
                    c.exec_driver_sql('DROP PROCEDURE '+nome)
                try:
                    r=self.client.get(BASE) if nome=='sp_alunos_admin' else self.client.put(f"{BASE}/{a['id']}",json={'nome':'Teste','email':a['email']})
                    self.assertEqual(r.status_code,500)
                    self.assertEqual(r.json['codigo'],'erro_interno')
                    self.assertNotIn(nome,r.get_data(as_text=True))
                    self.assertNotIn(a['email'],r.get_data(as_text=True))
                finally:
                    db.session.remove()
                    with engine.begin() as c:
                        c.exec_driver_sql(original, execution_options={"no_parameters": True})

    def test_criacao_duplicada_campos_exatos_e_edicao_inativa(self):
        a=self.criar()
        dados={'nome':'Outro Aluno','email':' '+a['email'].upper()+' ','senha':SENHA,'senha_confirmacao':SENHA}
        self.assertEqual(self.client.post(BASE,json=dados).json['codigo'],'email_em_uso')
        for extra in ['perfil','ativo','senha_hash','termos_uso','operador_id']:
            self.assertEqual(self.client.post(BASE,json={**dados,extra:True}).status_code,400)
        uid=a['id']
        self.assertEqual(self.client.post(f'{BASE}/{uid}/desativar',json={'confirmar':1}).status_code,400)
        self.assertEqual(self.client.post(f'{BASE}/{uid}/desativar',json={'confirmar':True}).status_code,200)
        c=self.app.test_client();token=c.get('/api/auth/csrf').json['csrf_token']
        self.assertEqual(c.post('/api/auth/login',json={'email':a['email'],'senha':SENHA},
            headers={'Origin':'http://frontend.test','X-CSRF-Token':token}).status_code,401)
        self.assertEqual(self.client.put(f'{BASE}/{uid}',json={'nome':'Conta inativa editada','email':a['email']}).status_code,200)
        for dados in [{'nome':'Correto'},{'nome':'Correto','email':a['email'],'ativo':True}]:
            self.assertEqual(self.client.put(f'{BASE}/{uid}',json=dados).status_code,400)

    def test_status_preserva_plano_decisoes_e_autoria_que_impedem_delete(self):
        a=self.criar();uid=a['id']
        with self.app.app_context():
            with db.engine.begin() as c:
                c.execute(text("INSERT INTO planos_estudo(usuario_id,geracao,atual,periodo,gerado_em,chave_envio,operacao) "
                    "VALUES(:id,1,1,JSON_OBJECT(),UTC_TIMESTAMP(),:chave,'gerar')"),{'id':uid,'chave':str(uuid4())})
                c.execute(text("INSERT INTO simulados(titulo,estado,revisao,autor_id,criado_em,atualizado_em) "
                    "VALUES('Autoria preservada','rascunho',1,:id,UTC_TIMESTAMP(),UTC_TIMESTAMP())"),{'id':uid})
                c.execute(text("INSERT INTO registros_privacidade(usuario_id,tipo,acao,versao,documento_sha256,chave_envio,revisao_base,registrado_em) "
                    "VALUES(:id,'plano','aceitar','1.0',:hash,:chave,0,UTC_TIMESTAMP(6))"),{'id':uid,'hash':'a'*64,'chave':str(uuid4())})
            def estado():
                return {t:db.session.execute(text(f'SELECT * FROM {t} WHERE {fk}=:id ORDER BY id'),{'id':uid}).all()
                    for t,fk in [('planos_estudo','usuario_id'),('registros_privacidade','usuario_id'),('simulados','autor_id')]}
            antes=estado();db.session.rollback()
            DesativarAlunoService.executar(uid,{'confirmar':True})
            from app.modules.contas.services.reativar_aluno_service import ReativarAlunoService
            ReativarAlunoService.executar(uid,{'confirmar':True})
            self.assertEqual(estado(),antes);db.session.rollback()
            with self.assertRaises(AutenticacaoError) as erro: ExcluirAlunoAdminService.executar(uid,{'confirmar':True})
            self.assertEqual(erro.exception.codigo,'usuario_com_vinculos')
            self.assertEqual(estado(),antes)

    def test_referencia_concorrente_com_delete_nao_cria_orfao(self):
        a=self.criar();uid=a['id'];iniciou=Event()
        with self.app.app_context():
            UsuarioRepository.bloquear(uid)
            def referenciar():
                with self.app.app_context():
                    iniciou.set()
                    try:
                        with db.engine.begin() as c:
                            c.execute(text('INSERT INTO sessoes(usuario_id,identificador_hash,criada_em,ultimo_acesso_em,expira_em) '
                                'VALUES(:id,:hash,UTC_TIMESTAMP(),UTC_TIMESTAMP(),UTC_TIMESTAMP()+INTERVAL 1 HOUR)'),{'id':uid,'hash':uuid4().hex*2})
                        return 200
                    except DBAPIError as erro: return erro.orig.args[0]
            with ThreadPoolExecutor(1) as pool:
                pendente=pool.submit(referenciar)
                self.assertTrue(iniciou.wait(timeout=5))
                ExcluirAlunoAdminService.executar(uid,{'confirmar':True})
                self.assertEqual(pendente.result(timeout=10),1452)
            self.assertIsNone(Usuario.buscar_por_id(uid))
            self.assertEqual(db.session.execute(text('SELECT COUNT(*) FROM sessoes WHERE usuario_id=:id'),{'id':uid}).scalar(),0)

    def test_lock_na_revogacao_participante_retorna_409_e_reverte_ativo(self):
        a=self.criar();uid=a['id'];self.entrar(a)
        with self.app.app_context():
            with db.engine.connect() as bloqueio:
                bloqueio.execute(text('SELECT id FROM sessoes WHERE usuario_id=:id FOR UPDATE'),{'id':uid}).all()
                def desativar():
                    with self.app.app_context():
                        db.session.execute(text('SET innodb_lock_wait_timeout=1'))
                        try: DesativarAlunoService.executar(uid,{'confirmar':True})
                        except AutenticacaoError as erro: return erro.codigo
                with ThreadPoolExecutor(1) as pool:
                    self.assertEqual(pool.submit(desativar).result(timeout=6),'operacao_concorrente')
                bloqueio.rollback()
            self.assertTrue(Usuario.buscar_por_id(uid).ativo)
            self.assertEqual(db.session.execute(text('SELECT COUNT(*) FROM sessoes WHERE usuario_id=:id AND revogada_em IS NULL'),{'id':uid}).scalar(),1)
