"""Caracterização de Contas e do mapeamento textual no MySQL real."""
from datetime import datetime, timedelta
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from pymysql import MySQLError

from sqlalchemy import inspect, select, text
from sqlalchemy.orm import contains_eager

from app.extensions import db
from app.modules.contas.domain.autenticacao import hash_identificador
from app.modules.contas.models.sessao import Sessao
from app.modules.contas.models.usuario import Usuario
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade as Registro
from app.modules.contas.models.auth_limite import AuthLimite
from app.modules.contas.repositories.autenticacao_repository import AutenticacaoRepository as Repo
from app.modules.contas.repositories.privacidade_repository import PrivacidadeRepository as Privacidade
from app.transaction_manager import TransactionManager
from sqlalchemy.exc import DBAPIError
from tests.integration_support import MySQLIntegrationTestCase
from tests import test_autenticacao_integration as fixture


class ContasProceduresIntegrationTest(MySQLIntegrationTestCase):
    autenticar_administrador = False
    setUp = fixture.AutenticacaoIntegrationTest.setUp
    request = fixture.AutenticacaoIntegrationTest.request
    cadastro = fixture.AutenticacaoIntegrationTest.cadastro
    login = fixture.AutenticacaoIntegrationTest.login

    def usuario_sintetico(self):
        return Usuario(nome='Sintético', email=uuid4().hex+'@teste.local', senha_hash='sintetico',
            perfil='aluno', ativo=True, criado_em=datetime(2026, 11, 8)).salvar()

    def sessao_sintetica(self, usuario_id, agora, **campos):
        valores = dict(usuario_id=usuario_id, identificador_hash=uuid4().hex*2,
            criada_em=agora-timedelta(hours=8), ultimo_acesso_em=agora,
            expira_em=agora+timedelta(hours=1), reautenticada_em=None, revogada_em=None)
        valores.update(campos)
        return Sessao(**valores).salvar()

    def test_limites_exatos_renovacao_inalterada_revogacao_contagens_e_rollback(self):
        agora = datetime(2026, 11, 8, 12, 0, 0, 123456)
        with self.app.app_context():
            usuario, outro = self.usuario_sintetico(), self.usuario_sintetico()
            uid, oid = usuario.id, outro.id
            limite = self.sessao_sintetica(uid, agora, expira_em=agora)
            inativa = self.sessao_sintetica(uid, agora, ultimo_acesso_em=agora-timedelta(minutes=30))
            valida = self.sessao_sintetica(uid, agora, expira_em=agora+timedelta(microseconds=1),
                ultimo_acesso_em=agora-timedelta(minutes=30)+timedelta(microseconds=1))
            alheia = self.sessao_sintetica(oid, agora)
            anonima = self.sessao_sintetica(None, agora)
            self.assertFalse(Repo.renovar_acesso(limite.id, agora))  # 8h exatas.
            self.assertFalse(Repo.renovar_acesso(inativa.id, agora))  # 30min exatos.
            self.assertFalse(Repo.renovar_acesso(2**31+1, agora))
            self.assertTrue(Repo.renovar_acesso(valida.id, agora))
            self.assertEqual(valida.ultimo_acesso_em, agora)
            self.assertTrue(Repo.renovar_acesso(valida.id, agora))  # Valor já igual.
            self.assertTrue(Repo.renovar_acesso(anonima.id, agora))
            # A sincronização da renovação não apaga a reautenticação pendente.
            instante_reauth = agora-timedelta(minutes=1)
            valida.reautenticada_em = instante_reauth
            self.assertTrue(Repo.renovar_acesso(valida.id, agora))
            self.assertEqual(valida.reautenticada_em, instante_reauth)
            self.assertIsNone(Repo.revogar(valida.id, agora))
            self.assertEqual(valida.revogada_em, agora)
            self.assertIsNone(Repo.revogar(valida.id, agora+timedelta(seconds=1)))
            self.assertEqual(valida.revogada_em, agora)
            self.assertFalse(Repo.renovar_acesso(valida.id, agora))
            self.assertEqual(Repo.revogar_usuario(uid, agora), 2)
            self.assertEqual(Repo.revogar_usuario(uid, agora), 0)
            self.assertEqual(limite.revogada_em, agora)
            self.assertIsNone(alheia.revogada_em)
            self.assertIsNone(anonima.revogada_em)
            db.session.rollback()
            self.assertIsNone(valida.revogada_em)
            self.assertIsNone(valida.reautenticada_em)
            self.assertEqual(valida.ultimo_acesso_em, agora-timedelta(minutes=30)+timedelta(microseconds=1))
            self.assertIsNone(limite.revogada_em)

    def test_limite_gerenciado_preserva_contador_e_criacao_participante(self):
        agora = datetime(2026, 11, 8, 12)
        chave = uuid4().hex*2
        with self.app.app_context():
            limite = Repo.limite_bloqueado(chave, agora)
            self.assertTrue(inspect(limite).persistent)
            self.assertEqual(limite.falhas, 0)
            limite.atualizar(confirmar=False, falhas=4, bloqueado_ate=agora+timedelta(minutes=15))
            self.assertIs(Repo.limite_bloqueado(chave, agora+timedelta(minutes=1)), limite)
            self.assertEqual(limite.falhas, 4)
            self.assertEqual(limite.janela_inicio, agora)
            db.session.rollback()
            self.assertIsNone(db.session.get(AuthLimite, chave))
            limite = Repo.limite_bloqueado(chave, agora)
            limite.atualizar(confirmar=False, falhas=3)
            db.session.commit()
            limite.atualizar(confirmar=False, falhas=4)
            db.session.rollback()
            self.assertEqual(Repo.limite_bloqueado(chave, agora).falhas, 3)

    def test_limpeza_cortes_igualdades_contagens_e_rollback_entre_deletes(self):
        agora = datetime(2026, 11, 8, 12)
        corte, epsilon = agora-timedelta(hours=24), timedelta(microseconds=1)
        with self.app.app_context():
            usuario = self.usuario_sintetico()
            uid = usuario.id
            outro = self.usuario_sintetico()
            oid = outro.id
            apagar = [self.sessao_sintetica(uid, agora, expira_em=corte-epsilon),
                self.sessao_sintetica(uid, agora, revogada_em=corte-epsilon),
                self.sessao_sintetica(uid, agora, ultimo_acesso_em=corte-timedelta(minutes=30)-epsilon)]
            manter = [self.sessao_sintetica(uid, agora, expira_em=corte),
                self.sessao_sintetica(uid, agora, revogada_em=corte),
                self.sessao_sintetica(uid, agora, ultimo_acesso_em=corte-timedelta(minutes=30)),
                self.sessao_sintetica(None, agora, ultimo_acesso_em=corte-timedelta(days=1)),
                self.sessao_sintetica(oid, agora)]
            apagar_ids, manter_ids = [s.id for s in apagar], [s.id for s in manter]
            limites = []
            for janela, bloqueio in ((corte-timedelta(minutes=15)-epsilon, None),
                    (corte-timedelta(minutes=15)-epsilon, corte-epsilon),
                    (corte-timedelta(minutes=15), None),
                    (corte-timedelta(minutes=15)-epsilon, corte),
                    (corte-timedelta(minutes=15)-epsilon, agora)):
                limites.append(AuthLimite(chave_hash=uuid4().hex*2, falhas=1,
                    janela_inicio=janela, bloqueado_ate=bloqueio).salvar())
            chaves = [l.chave_hash for l in limites]
            evidencia = Registro(usuario_id=uid, tipo='uso', acao='aceitar', versao='1.0',
                documento_sha256='a'*64, registrado_em=corte-timedelta(days=100),
                chave_envio=str(uuid4()), revisao_base=0).salvar()
            evidencia_id = evidencia.id
            antes_sessoes = db.session.execute(select(Sessao.id)).scalars().all()
            antes_limites = db.session.execute(select(AuthLimite.chave_hash)).scalars().all()
            db.session.rollback()
            engine = db.engine
            with engine.begin() as ddl:
                ddl.exec_driver_sql('CREATE TRIGGER falhar_limpeza_016 BEFORE DELETE ON auth_limites '
                    "FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Falha sintética entre DELETEs'")
            try:
                with self.assertRaises(MySQLError):
                    TransactionManager.executar(lambda: Repo.limpar(agora))
                self.assertEqual(db.session.execute(select(Sessao.id)).scalars().all(), antes_sessoes)
                self.assertEqual(db.session.execute(select(AuthLimite.chave_hash)).scalars().all(), antes_limites)
            finally:
                db.session.rollback()
                with engine.begin() as ddl:
                    ddl.exec_driver_sql('DROP TRIGGER falhar_limpeza_016')
            contagens = Repo.limpar(agora)
            self.assertGreaterEqual(contagens['sessoes'], 3)
            self.assertGreaterEqual(contagens['limites'], 2)
            for id_ in apagar_ids:
                self.assertIsNone(db.session.get(Sessao, id_))
            for id_ in manter_ids:
                self.assertIsNotNone(db.session.get(Sessao, id_))
            for chave in chaves[:2]:
                self.assertIsNone(db.session.get(AuthLimite, chave))
            for chave in chaves[2:]:
                self.assertIsNotNone(db.session.get(AuthLimite, chave))
            self.assertIsNotNone(db.session.get(Registro, evidencia_id))
            self.assertIsNotNone(db.session.get(Usuario, uid))
            # Contagens correspondem às remoções efetivas de cada tabela.
            self.assertEqual(contagens['sessoes'], len(antes_sessoes)-len(db.session.execute(select(Sessao.id)).all()))
            self.assertEqual(contagens['limites'], len(antes_limites)-len(db.session.execute(select(AuthLimite.chave_hash)).all()))
            db.session.rollback()
            self.assertIsNotNone(db.session.get(Sessao, apagar_ids[0]))
            self.assertIsNotNone(db.session.get(AuthLimite, chaves[0]))

    def test_lock_identidade_inativa_replay_por_dono_e_evidencia_gerenciada(self):
        with self.app.app_context():
            usuario, outro = self.usuario_sintetico(), self.usuario_sintetico()
            uid, oid = usuario.id, outro.id
            usuario.atualizar(ativo=False)
            chave = str(uuid4())
            registros = [Registro(usuario_id=id_, tipo='uso', acao='aceitar', versao='1.0',
                documento_sha256='a'*64, chave_envio=chave, revisao_base=0).salvar() for id_ in (uid, oid)]
            Privacidade.bloquear_usuario(uid)
            self.assertIsNone(Repo.usuario_ativo_bloqueado(uid))
            self.assertIs(Privacidade.por_chave(uid, chave), registros[0])
            self.assertIs(Privacidade.por_chave(oid, chave), registros[1])
            self.assertIsNone(Privacidade.por_chave(uid, str(uuid4())))
            self.assertEqual(Privacidade.ultimas(uid), {'uso': registros[0], 'plano': None})
            def tentar_atualizar():
                with self.app.app_context():
                    try:
                        db.session.execute(text('SET innodb_lock_wait_timeout=1'))
                        db.session.execute(text('UPDATE usuarios SET ativo=1 WHERE id=:id'), {'id': uid})
                    except DBAPIError as erro:
                        return erro.orig.args[0]
                    finally:
                        db.session.rollback()
            with ThreadPoolExecutor(1) as pool:
                self.assertEqual(pool.submit(tentar_atualizar).result(timeout=5), 1205)
            db.session.rollback()
            self.assertIs(Usuario.buscar_por_id(uid).ativo, False)

    def test_routines_indisponiveis_falham_sem_fallback_ou_detalhes_sensiveis(self):
        self.assertEqual(self.cadastro().status_code, 201)
        self.assertEqual(self.login().status_code, 200)
        csrf = self.client.get('/api/auth/sessao').json['csrf_token']
        headers = {'Origin': fixture.ORIGIN, 'X-CSRF-Token': csrf}
        with self.app.app_context():
            usuario_id = Usuario.buscar_por_email(self.email).id
            engine = db.engine
        operacoes = {
            'sp_consultar_sessao': lambda: self.client.get('/api/auth/sessao'),
            'sp_renovar_acesso_sessao': lambda: self.client.get('/api/auth/sessao'),
            'sp_revogar_sessao': lambda: self.client.post('/api/auth/logout', headers=headers),
            'sp_usuario_ativo_bloqueado': lambda: self.client.post('/api/auth/reautenticar',
                json={'senha': fixture.SENHA}, headers=headers),
            'sp_preparar_limite_autenticacao': lambda: self.client.post('/api/auth/reautenticar',
                json={'senha': fixture.SENHA}, headers=headers),
            'sp_bloquear_identidade_privacidade': lambda: self.client.get('/api/aluno/privacidade'),
            'sp_ultimas_decisoes_privacidade': lambda: self.client.get('/api/aluno/privacidade'),
            'sp_decisao_privacidade_por_chave': lambda: self.client.post(
                '/api/aluno/privacidade/consentimento-plano/aceitar',
                json={'versao': '1.0', 'revisao': 0, 'chave_envio': str(uuid4())}, headers=headers),
        }
        # Login exige sua própria sessão anônima; preparar antes de retirar a routine.
        anonimo = self.app.test_client()
        token = anonimo.get('/api/auth/csrf').json['csrf_token']
        operacoes['sp_usuario_por_email'] = lambda: anonimo.post('/api/auth/login',
            json={'email': self.email, 'senha': fixture.SENHA},
            headers={'Origin': fixture.ORIGIN, 'X-CSRF-Token': token})
        for nome in (*operacoes, 'sp_revogar_sessoes_usuario', 'sp_limpar_autenticacao'):
            with self.subTest(nome=nome), self.app.app_context():
                db.session.remove()
                with engine.begin() as ddl:
                    original = ddl.exec_driver_sql('SHOW CREATE PROCEDURE '+nome).one()._mapping['Create Procedure']
                    ddl.exec_driver_sql('DROP PROCEDURE '+nome)
                try:
                    if nome == 'sp_revogar_sessoes_usuario':
                        with self.assertRaises(MySQLError):
                            TransactionManager.executar(lambda: Repo.revogar_usuario(usuario_id, datetime(2026, 11, 8)))
                    elif nome == 'sp_limpar_autenticacao':
                        resultado = self.app.test_cli_runner().invoke(args=['limpar-autenticacao'])
                        self.assertNotEqual(resultado.exit_code, 0)
                        self.assertNotIn(nome, resultado.output)
                        self.assertNotIn(self.email, resultado.output)
                    else:
                        resposta = operacoes[nome]()
                        self.assertEqual(resposta.status_code, 500)
                        for segredo in (nome, self.email, fixture.SENHA, 'senha_hash', 'identificador_hash', 'CALL '):
                            self.assertNotIn(segredo, resposta.get_data(as_text=True))
                finally:
                    db.session.remove()
                    with engine.begin() as ddl:
                        ddl.exec_driver_sql(original)
        self.assertEqual(self.client.get('/api/auth/sessao').status_code, 200)

    def test_prova_ultimas_conjunto_unico_vazios_tipos_identidade_e_snapshot(self):
        from uuid import uuid4
        with self.app.app_context():
            usuario = Usuario(nome='Sintético', email=self.email, senha_hash='sintetico',
                perfil='aluno', ativo=True, criado_em=datetime(2026, 11, 8)).salvar()
            usuario_id = usuario.id
            def consultar():
                resultado = db.session.execute(select(Registro).from_statement(
                    text('CALL sp_ultimas_decisoes_privacidade(:id)').columns(*Registro.__table__.columns))
                    .execution_options(populate_existing=True), {'id': usuario_id})
                try:
                    return resultado.scalars().all()
                finally:
                    resultado.close()
            def criar(tipo):
                return Registro(usuario_id=usuario_id, tipo=tipo, acao='aceitar', versao='1.0',
                    documento_sha256='a'*64, registrado_em=datetime(2026, 11, 8, 12, 0, 0, 123456),
                    chave_envio=str(uuid4()), revisao_base=0).salvar()
            self.assertEqual(consultar(), [])
            self.assertEqual(Privacidade.ultimas(usuario_id), {'uso': None, 'plano': None})
            db.session.rollback()
            plano = criar('plano')
            self.assertEqual(consultar(), [plano])
            self.assertEqual(Privacidade.ultimas(usuario_id), {'uso': None, 'plano': plano})
            db.session.rollback()
            uso = criar('uso')
            self.assertEqual(consultar(), [uso, plano])
            self.assertEqual(Privacidade.ultimas(usuario_id), {'uso': uso, 'plano': plano})
            self.assertEqual(uso.registrado_em.microsecond, 123456)
            self.assertIsInstance(plano.registrado_em, datetime)
            self.assertIsInstance(plano.revisao_base, int)
            self.assertTrue(all(inspect(r).persistent for r in (uso, plano)))
            db.session.rollback()
            # Um snapshot consistente antigo não pode ocultar a decisão posterior.
            antigo = db.session.get(Registro, uso.id)
            plano = db.session.get(Registro, plano.id)
            with db.engine.begin() as outra:
                outra.execute(text('INSERT INTO registros_privacidade '
                    '(usuario_id,tipo,acao,versao,documento_sha256,registrado_em,chave_envio,revisao_base) '
                    "VALUES(:id,'uso','aceitar','1.0',:hash,:agora,:chave,:revisao)"),
                    {'id': usuario_id, 'hash': 'a'*64, 'agora': datetime(2026, 11, 8, 13),
                     'chave': str(uuid4()), 'revisao': antigo.id})
            novo, mesmo_plano = consultar()
            self.assertGreater(novo.id, antigo.id)
            self.assertIs(mesmo_plano, plano)
            self.assertIs(db.session.get(Registro, novo.id), novo)
            self.assertEqual(db.session.execute(text('SELECT 7')).scalar_one(), 7)
            db.session.rollback()

    def test_caracterizacao_email_sessao_anonima_identidade_e_rollback(self):
        self.assertEqual(self.cadastro().status_code, 201)
        anonimo = self.client.get_cookie('enem_session', path='/api').value
        with self.app.app_context():
            sessao = Repo.consultar_sessao(hash_identificador(anonimo))
            self.assertIsNone(sessao.usuario)
            self.assertIsNone(sessao.usuario_id)
            self.assertIsNone(Repo.consultar_sessao('f' * 64))
        self.assertEqual(self.login().status_code, 200)
        identificador = self.client.get_cookie('enem_session', path='/api').value
        with self.app.app_context():
            usuario = Usuario.buscar_por_email(self.email)
            self.assertIsNone(Usuario.buscar_por_email(self.email.upper()))
            self.assertIsNone(Usuario.buscar_por_email("' OR 1=1 --@teste.local"))
            sessao = Repo.consultar_sessao(hash_identificador(identificador))
            self.assertIs(sessao.usuario, usuario)
            self.assertIs(Repo.usuario_ativo_bloqueado(usuario.id), usuario)
            self.assertIsInstance(usuario.ativo, bool)
            self.assertIsInstance(sessao.criada_em, datetime)
            self.assertTrue(inspect(sessao).persistent)
            usuario.atualizar(confirmar=False, ativo=False)
            self.assertIsNone(Repo.usuario_ativo_bloqueado(usuario.id))
            db.session.rollback()
            self.assertTrue(Repo.usuario_ativo_bloqueado(usuario.id).ativo)
            db.session.rollback()
        resposta = self.client.get('/api/auth/sessao')
        self.assertEqual(resposta.status_code, 200)
        for campo in ('senha_hash', 'identificador_hash', 'revogada_em'):
            self.assertNotIn(campo, resposta.get_data(as_text=True))

    def test_prova_call_join_corrente_relacao_gerenciada_vazio_e_drenagem(self):
        self.assertEqual(self.cadastro().status_code, 201)
        anonimo = self.client.get_cookie('enem_session', path='/api').value
        self.assertEqual(self.login().status_code, 200)
        identificador = self.client.get_cookie('enem_session', path='/api').value
        with self.app.app_context():
            engine = db.engine
            # Identificadores/colunas vêm exclusivamente dos mappers do teste.
            colunas = ', '.join(
                f'{alias}.{c.name} AS {alias}_{c.name}'
                for modelo, alias in ((Sessao, 's'), (Usuario, 'u'))
                for c in modelo.__table__.columns)
            with engine.begin() as ddl:
                ddl.exec_driver_sql('CREATE PROCEDURE sp_teste_contas_join_016(IN p_hash CHAR(64)) '
                    'READS SQL DATA SQL SECURITY INVOKER SELECT ' + colunas +
                    ' FROM sessoes s LEFT JOIN usuarios u ON u.id=s.usuario_id '
                    'WHERE s.identificador_hash=p_hash FOR UPDATE')
            try:
                usuario = Usuario.buscar_por_email(self.email)
                sessao = Repo.consultar_sessao(hash_identificador(identificador))
                with engine.begin() as outra:
                    outra.execute(text('UPDATE usuarios SET ativo=0 WHERE id=:id'), {'id': usuario.id})
                comando = text('CALL sp_teste_contas_join_016(:hash)').columns(
                    *Sessao.__table__.columns, *Usuario.__table__.columns)
                consulta = select(Sessao).options(contains_eager(Sessao.usuario)).from_statement(comando)
                for chave, vazio in ((hash_identificador(identificador), False), ('f' * 64, True),
                                     (hash_identificador(anonimo), False)):
                    resultado = db.session.execute(consulta.execution_options(populate_existing=True),
                        {'hash': chave})
                    try:
                        atual = resultado.scalar_one_or_none()
                    finally:
                        resultado.close()
                    if vazio:
                        self.assertIsNone(atual)
                    elif chave == hash_identificador(identificador):
                        self.assertIs(atual, sessao)
                        self.assertIs(atual.usuario, usuario)
                        self.assertIs(usuario.ativo, False)
                        self.assertIsInstance(atual.expira_em, datetime)
                        self.assertTrue(inspect(usuario).persistent)
                    else:
                        self.assertIsNone(atual.usuario)
                usuario.atualizar(confirmar=False, ativo=True)
                db.session.rollback()
                self.assertIs(Usuario.buscar_por_email(self.email).ativo, False)
                self.assertEqual(db.session.execute(text('SELECT 7')).scalar_one(), 7)
            finally:
                db.session.rollback()
                with engine.begin() as ddl:
                    ddl.exec_driver_sql('DROP PROCEDURE sp_teste_contas_join_016')
