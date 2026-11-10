"""Privacidade com API, transações e locks do MySQL real, sem mocks."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
from uuid import uuid4

from sqlalchemy import select, text
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.domain.privacidade import documento_vigente
from app.exceptions import ConflitoError
from app.extensions import db
from app.modules.contas.models.usuario import Usuario
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade
from app.modules.plano_estudos.models.plano_estudo import PlanoEstudo, PlanoEstudoItem
from app.modules.contas.services.consentir_plano_service import ConsentirPlanoService
from app.modules.contas.services.consultar_privacidade_service import ConsultarPrivacidadeService
from app.http_composition import servicos
from tests.integration_support import MySQLIntegrationTestCase
from tests import test_praticas_integration as praticas
from tests import test_planos_integration as planos


class PrivacidadeIntegrationTest(MySQLIntegrationTestCase):
    conta = praticas.PraticasIntegrationTest.conta
    publicar = praticas.PraticasIntegrationTest.publicar
    setUp = praticas.PraticasIntegrationTest.setUp
    base = planos.PlanosIntegrationTest.base
    gerar = planos.PlanosIntegrationTest.gerar
    recalcular = planos.PlanosIntegrationTest.recalcular
    url = '/api/aluno/plano'
    privacy = '/api/aluno/privacidade'

    def decidir(self, acao, cliente=None, **extra):
        cliente = cliente or self.aluno
        estado=cliente.get(self.privacy).json
        tipo='termos_uso' if acao=='termos-uso' else 'consentimento_plano'
        registro=estado[tipo]['registro']
        body={
            'versao': registro['versao'] if acao=='revogar' and registro else estado[tipo]['versao_vigente'],
            'chave_envio': str(uuid4()),
            'revisao': registro['id'] if registro else 0
        }
        if acao in ('recusar', 'revogar'):
            body['confirmar']=True
        body.update(extra)
        path=self.privacy+('/termos-uso' if acao=='termos-uso' else '/consentimento-plano/'+acao)
        return cliente.post(path, json=body), body

    def test_metadados_head_publico_politicas_e_estado_inicial(self):
        anonimo=self.app.test_client()
        for method in ('get', 'head'):
            r=getattr(anonimo, method)('/api/termos')
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.headers['Cache-Control'], 'no-store')
            if method=='head':
                self.assertEqual(r.data, b'')
            r=getattr(anonimo, method)(self.privacy)
            self.assertEqual(r.status_code, 401)
        self.assertEqual(anonimo.post('/api/termos').status_code, 405)
        self.assertEqual(anonimo.get('/api/termos/desconhecido').status_code, 404)
        self.assertEqual(self.client.get(self.privacy).status_code, 403)
        r=self.aluno.get(self.privacy)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json['termos_uso']['aceite_vigente'])
        self.assertIsNone(r.json['consentimento_plano']['registro'])
        self.assertFalse(r.json['plano_liberado'])
        self.assertEqual(r.headers['Cache-Control'], 'no-store')
        for acao in ('termos-uso', 'aceitar', 'recusar', 'revogar'):
            path=self.privacy+('/termos-uso' if acao=='termos-uso' else '/consentimento-plano/'+acao)
            self.assertEqual(anonimo.post(path, json={}).status_code, 401)
            self.assertEqual(self.client.post(path, json={}).status_code, 403)
            self.assertEqual(
                self.aluno.post(
                    path,
                    json={},
                    headers={'Origin': 'http://outra.test'}
                ).status_code,
                403
            )
            self.assertEqual(
                self.aluno.post(
                    path,
                    json={},
                    headers={'X-CSRF-Token': 'invalido'}
                ).status_code,
                403
            )

    def test_validacoes_versao_revisao_chave_transicoes_e_isolamento(self):
        for extra in (
            {'usuario_id': self.outro_id},
            {'revisao': True},
            {'revisao': -1},
            {'chave_envio': 'INVALIDA'},
            {'versao': False},
            {'versao': ''},
            {'documento_sha256': 'a'*64}
        ):
            r, _=self.decidir('aceitar', **extra)
            self.assertEqual(r.status_code, 400)
        r, _=self.decidir('aceitar', versao='0.9')
        self.assertEqual(r.json['codigo'], 'termo_desatualizado')
        r, _=self.decidir('aceitar', revisao=999)
        self.assertEqual(r.json['codigo'], 'decisao_desatualizada')
        r, _=self.decidir('revogar')
        self.assertEqual(r.json['codigo'], 'decisao_invalida')
        for confirmacao in (None, False, 1, 'true'):
            r, _=self.decidir('recusar', confirmar=confirmacao)
            self.assertEqual(r.status_code, 400)
        r, corpo=self.decidir('recusar')
        self.assertEqual(r.status_code, 201)
        rejeicao=r.json['registro']
        self.assertEqual(rejeicao['documento_sha256'], documento_vigente('plano')['sha256'])
        r, _=self.decidir('aceitar')
        self.assertTrue(r.json['privacidade']['plano_liberado'])
        self.assertIsNone(self.outro.get(self.privacy).json['consentimento_plano']['registro'])
        r, _=self.decidir('recusar')
        self.assertEqual(r.json['codigo'], 'decisao_invalida')
        replay=self.aluno.post(self.privacy+'/consentimento-plano/recusar', json=corpo)
        self.assertEqual(replay.status_code, 200)
        self.assertEqual(replay.json['registro'], rejeicao)
        self.assertTrue(replay.json['privacidade']['plano_liberado'])
        corpo['revisao']+=1
        self.assertEqual(
            self.aluno.post(
                self.privacy+'/consentimento-plano/recusar',
                json=corpo
            ).status_code,
            409
        )

    def test_conta_legada_aceite_uso_replay_e_versao_antiga_revogavel(self):
        # Simula uma conta anterior sem inventar aceite via cadastro administrativo.
        from app.modules.contas.services.autenticacao_service import CriarUsuarioService
        cliente=self.app.test_client()
        cliente.csrf=cliente.get('/api/auth/csrf').json['csrf_token']
        email=uuid4().hex+'@teste.local'
        with self.app.app_context():
            CriarUsuarioService.executar(
                {
                    'nome': 'Legado',
                    'email': email,
                    'senha': self.senha,
                    'senha_confirmacao': self.senha
                },
                'aluno'
            )
        r=cliente.post('/api/auth/login', json={'email': email, 'senha': self.senha})
        cliente.csrf=r.json['csrf_token']
        estado=cliente.get(self.privacy).json
        self.assertIsNone(estado['termos_uso']['registro'])
        r, _=self.decidir('aceitar', cliente)
        self.assertEqual(r.json['codigo'], 'termos_uso_pendentes')
        r, corpo=self.decidir('termos-uso', cliente)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(cliente.post(self.privacy+'/termos-uso', json=corpo).status_code, 200)
        r, _=self.decidir('aceitar', cliente)
        registro=r.json['registro']
        with self.app.app_context():
            db.session.execute(
                text("UPDATE registros_privacidade SET versao='versao-retirada',documento_sha256=:hash WHERE id=:id"),
                {'id': registro['id'], 'hash': 'b'*64}
            )
            db.session.commit()
        self.assertEqual(
            cliente.get(self.privacy).json['consentimento_plano']['estado'],
            'desatualizado'
        )
        self.assertEqual(cliente.get(self.url).status_code, 403)
        r, _=self.decidir('revogar', cliente)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json['registro']['versao'], 'versao-retirada')
        self.assertEqual(r.json['registro']['documento_sha256'], 'b'*64)

    def test_model_utc_imutavel_e_sem_capacidades_de_mutacao(self):
        self.decidir('aceitar')
        with self.app.app_context():
            registro=db.session.execute(select(RegistroPrivacidade).where(RegistroPrivacidade.usuario_id==self.usuario)).scalars().first()
            self.assertIsNone(registro.registrado_em.tzinfo)
            from app.core.relogio import agora_utc
            self.assertLess(abs((registro.registrado_em-agora_utc()).total_seconds()), 30)
            self.assertFalse(hasattr(registro, 'atualizar'))
            self.assertFalse(hasattr(registro, 'deletar'))
            registro.acao='recusar'
            with self.assertRaises(ConflitoError):
                registro.salvar(confirmar=False)
            db.session.rollback()
            db.session.delete(registro)
            with self.assertRaises(ConflitoError):
                db.session.flush()
            db.session.rollback()

    def test_upgrade_uso_preserva_plano_decisoes_e_evidencia_antiga(self):
        from app.modules.contas.domain.privacidade import DOCUMENTOS
        self.decidir('aceitar')
        self.base()
        plano = self.gerar().json['plano']
        with self.app.app_context():
            registro = db.session.execute(select(RegistroPrivacidade).where(
                RegistroPrivacidade.usuario_id == self.usuario,
                RegistroPrivacidade.tipo == 'uso'
            )).scalar_one()
            antigo_id = registro.id
            # Fixture de conta publicada antes do upgrade; nenhum backfill de produção.
            db.session.execute(
                text('UPDATE registros_privacidade SET versao=:v,documento_sha256=:h WHERE id=:id'),
                {'v': '1.0', 'h': DOCUMENTOS['uso']['1.0']['sha256'], 'id': antigo_id}
            )
            db.session.commit()
        antes = self.aluno.get(self.privacy).json
        self.assertFalse(antes['termos_uso']['aceite_vigente'])
        self.assertEqual(self.aluno.get(self.url).status_code, 403)
        for path in ('questoes', 'simulados', 'desempenho'):
            self.assertEqual(self.aluno.get('/api/aluno/' + path).status_code, 200)
        resposta, _ = self.decidir('termos-uso')
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json['registro']['versao'], '2.0')
        self.assertEqual(
            resposta.json['privacidade']['consentimento_plano'],
            antes['consentimento_plano']
        )
        self.assertEqual(self.aluno.get(self.url).json['plano'], plano)
        with self.app.app_context():
            antigo = db.session.get(RegistroPrivacidade, antigo_id)
            self.assertEqual(
                (antigo.versao, antigo.documento_sha256),
                ('1.0', DOCUMENTOS['uso']['1.0']['sha256'])
            )
            registros = db.session.execute(select(RegistroPrivacidade).where(
                RegistroPrivacidade.usuario_id == self.usuario)).scalars().all()
            self.assertEqual(len(registros), 3)

    def test_guard_uniforme_e_sem_efeitos_antes_de_consentir(self):
        for path, body in [
            (self.url, None),
            (self.url+'/gerar', {'chave_envio': str(uuid4())}),
            (
                self.url+'/recalcular',
                {
                    'chave_envio': str(uuid4()),
                    'plano_atual_id': 1,
                    'confirmar': True
                }
            ),
            (self.url+'/itens/999/concluir', {'confirmar': True})
        ]:
            r=self.aluno.get(path) if body is None else self.aluno.post(path, json=body)
            self.assertEqual(
                (
                    r.status_code,
                    r.json['codigo']
                ),
                (
                    403,
                    'consentimento_plano_necessario'
                )
            )
        r, _=self.decidir('aceitar')
        self.assertTrue(r.json['privacidade']['plano_liberado'])
        self.assertEqual(self.aluno.get(self.url).json['estado'], 'sem_plano')
        self.assertEqual(
            self.aluno.post(
                self.url+'/itens/999/concluir',
                json={'confirmar': True}
            ).status_code,
            404
        )
        self.decidir('revogar')
        self.assertEqual(self.aluno.get('/api/aluno/desempenho').status_code, 200)
        self.assertEqual(self.aluno.get('/api/aluno/questoes').status_code, 200)
        self.assertEqual(self.aluno.get('/api/aluno/simulados').status_code, 200)

    def test_elimina_todas_geracoes_preserva_fatos_e_outra_conta_replay_nao_apaga_novo(self):
        self.decidir('aceitar')
        self.decidir('aceitar', self.outro)
        self.base()
        primeiro=self.gerar().json['plano']
        self.aluno.post(
            self.url+f"/itens/{primeiro['itens'][0]['id']}/concluir",
            json={'confirmar': True}
        )
        segundo=self.recalcular(primeiro).json['plano']
        self.recalcular(segundo)
        with self.app.app_context():
            # Plano legado da outra conta, preservado pela eliminação especializada.
            PlanoEstudo(
                usuario_id=self.outro_id,
                geracao=1,
                atual=True,
                periodo={},
                gerado_em=__import__('datetime').datetime.now(),
                chave_envio=str(uuid4()),
                operacao='gerar'
            ).salvar()
        antes=self.aluno.get('/api/aluno/desempenho').json
        r, corpo=self.decidir('revogar')
        self.assertEqual(r.status_code, 201)
        with self.app.app_context():
            self.assertEqual(
                db.session.execute(select(PlanoEstudo).where(PlanoEstudo.usuario_id==self.usuario)).scalars().all(),
                []
            )
            self.assertEqual(
                len(db.session.execute(select(PlanoEstudo).where(PlanoEstudo.usuario_id==self.outro_id)).scalars().all()),
                1
            )
            self.assertIsNone(db.session.get(PlanoEstudoItem, primeiro['itens'][0]['id']))
        depois=self.aluno.get('/api/aluno/desempenho').json
        for chave in ('geral', 'base', 'assuntos', 'materias'):
            self.assertEqual(depois[chave], antes[chave])
        self.decidir('aceitar')
        novo=self.gerar().json['plano']
        self.assertEqual(novo['geracao'], 1)
        replay=self.aluno.post(self.privacy+'/consentimento-plano/revogar', json=corpo)
        self.assertEqual(replay.status_code, 200)
        self.assertTrue(replay.json['privacidade']['plano_liberado'])
        self.assertEqual(self.aluno.get(self.url).json['plano'], novo)

    def test_rollback_real_de_negativa_e_cadastro(self):
        self.decidir('aceitar')
        self.base()
        p=self.gerar().json['plano']
        self.recalcular(p)
        with self.app.app_context():
            db.session.execute(text(f"CREATE TRIGGER falhar_privacidade_delete BEFORE DELETE ON planos_estudo FOR EACH ROW BEGIN IF OLD.id = {p['id']} THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='falha de teste'; END IF; END"))
            db.session.commit()
        try:
            r, _=self.decidir('revogar')
            self.assertEqual(r.status_code, 500)
            self.assertTrue(self.aluno.get(self.privacy).json['plano_liberado'])
            with self.app.app_context():
                self.assertEqual(
                    len(db.session.execute(select(PlanoEstudo).where(PlanoEstudo.usuario_id==self.usuario)).scalars().all()),
                    2
                )
                self.assertIsNotNone(db.session.get(PlanoEstudoItem, p['itens'][0]['id']))
        finally:
            with self.app.app_context():
                db.session.execute(text('DROP TRIGGER falhar_privacidade_delete'))
                db.session.commit()
        cliente=self.app.test_client()
        cliente.csrf=cliente.get('/api/auth/csrf').json['csrf_token']
        dados={
            'nome': 'Falha real',
            'email': uuid4().hex+'@teste.local',
            'senha': self.senha,
            'senha_confirmacao': self.senha,
            'termos_uso': {'versao': "2.0", 'aceito': True}
        }
        with self.app.app_context():
            db.session.execute(text("CREATE TRIGGER falhar_privacidade_insert BEFORE INSERT ON registros_privacidade FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='falha de teste'"))
            db.session.commit()
        try:
            self.assertEqual(cliente.post('/api/auth/cadastro', json=dados).status_code, 500)
            with self.app.app_context():
                self.assertIsNone(Usuario.buscar_por_email(dados['email']))
        finally:
            with self.app.app_context():
                db.session.execute(text('DROP TRIGGER falhar_privacidade_insert'))
                db.session.commit()

    def test_recusa_reverte_evidencia_quando_eliminacao_participante_falha(self):
        from app.core.relogio import agora_utc
        with self.app.app_context():
            plano = PlanoEstudo(
                usuario_id=self.usuario,
                geracao=1,
                atual=True,
                periodo={},
                gerado_em=agora_utc(),
                chave_envio=str(uuid4()),
                operacao='gerar'
            ).salvar()
            plano_id = plano.id
            db.session.execute(text("CREATE TRIGGER falhar_recusa_delete BEFORE DELETE ON planos_estudo "
                "FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='falha real do participante'"))
            db.session.commit()
        try:
            resposta, corpo = self.decidir('recusar')
            self.assertEqual(resposta.status_code, 500)
            estado = self.aluno.get(self.privacy).json
            self.assertIsNone(estado['consentimento_plano']['registro'])
            with self.app.app_context():
                self.assertIsNotNone(db.session.get(PlanoEstudo, plano_id))
                registros = db.session.execute(select(RegistroPrivacidade).where(
                    RegistroPrivacidade.usuario_id == self.usuario,
                    RegistroPrivacidade.chave_envio == corpo['chave_envio']
                )).scalars().all()
                self.assertEqual(registros, [])
        finally:
            with self.app.app_context():
                db.session.execute(text('DROP TRIGGER falhar_recusa_delete'))
                db.session.commit()
        resposta = self.aluno.post(self.privacy + '/consentimento-plano/recusar', json=corpo)
        self.assertEqual(resposta.status_code, 201)
        with self.app.app_context():
            self.assertIsNone(db.session.get(PlanoEstudo, plano_id))

    def test_cadastro_sem_aceite_ou_invalido_nao_cria_conta(self):
        cliente=self.app.test_client()
        cliente.csrf=cliente.get('/api/auth/csrf').json['csrf_token']
        base={
            'nome': 'Sem aceite',
            'email': uuid4().hex+'@teste.local',
            'senha': self.senha,
            'senha_confirmacao': self.senha
        }
        for termos in [
            None,
            {},
            False,
            {
                'versao': '1.0',
                'aceito': False
            },
            {
                'versao': '1.0',
                'aceito': 1
            },
            {
                'versao': '1.0',
                'aceito': True,
                'extra': 1
            }
        ]:
            dados=base if termos is None else {**base, 'termos_uso': termos}
            self.assertEqual(cliente.post('/api/auth/cadastro', json=dados).status_code, 400)
        self.assertEqual(
            cliente.post(
                '/api/auth/cadastro',
                json={
                    **base,
                    'termos_uso': {
                        'versao': '0.9',
                        'aceito': True
                    }
                }
            ).status_code,
            409
        )
        with self.app.app_context():
            self.assertIsNone(Usuario.buscar_por_email(base['email']))

    def test_recusa_elimina_legado_e_falha_de_leitura_fecha_acesso(self):
        from app.core.relogio import agora_utc
        with self.app.app_context():
            plano=PlanoEstudo(
                usuario_id=self.usuario,
                geracao=1,
                atual=True,
                periodo={},
                gerado_em=agora_utc(),
                chave_envio=str(uuid4()),
                operacao='gerar'
            ).salvar()
            item=PlanoEstudoItem(
                plano_id=plano.id,
                assunto_id=self.assunto['id'],
                materia_id=self.materia['id'],
                posicao=1,
                snapshot={},
                estado='pendente'
            ).salvar()
            plano_id, item_id=plano.id, item.id
            db.session.execute(text('RENAME TABLE registros_privacidade TO registros_privacidade_indisponivel'))
            db.session.commit()
        try:
            for path, body in [
                (self.url, None),
                (self.url+'/gerar', {'chave_envio': str(uuid4())}),
                (
                    self.url+'/recalcular',
                    {
                        'chave_envio': str(uuid4()),
                        'plano_atual_id': plano_id,
                        'confirmar': True
                    }
                ),
                (self.url+f'/itens/{item_id}/concluir', {'confirmar': True})
            ]:
                r=self.aluno.get(path) if body is None else self.aluno.post(path, json=body)
                self.assertEqual(r.status_code, 500)
                self.assertNotIn('snapshot', r.json)
        finally:
            with self.app.app_context():
                db.session.execute(text('RENAME TABLE registros_privacidade_indisponivel TO registros_privacidade'))
                db.session.commit()
        r, _=self.decidir('recusar')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json['privacidade']['consentimento_plano']['estado'], 'recusado')
        with self.app.app_context():
            self.assertIsNone(db.session.get(PlanoEstudo, plano_id))
            self.assertIsNone(db.session.get(PlanoEstudoItem, item_id))

    def test_concorrencia_decisoes_e_snapshot_antigo(self):
        barreira=Barrier(2)

        def decidir():
            with self.app.app_context():
                # Consulta de autenticação inicia um snapshot antes da disputa.
                db.session.get(Usuario, self.usuario)
                barreira.wait(timeout=10)
                try:
                    return ConsentirPlanoService.executar(
                        self.usuario,
                        {
                            'versao': '1.0',
                            'revisao': 0,
                            'chave_envio': str(uuid4())
                        }
                    )[1]
                except AutenticacaoError as e:
                    return e.status_code
        with ThreadPoolExecutor(2) as pool:
            resultados=list(pool.map(lambda _: decidir(), range(2)))
        self.assertEqual(sorted(resultados), [201, 409])
        snapshot_pronto, continuar=Event(), Event()

        def consultar_antigo():
            with self.app.app_context():
                db.session.execute(select(RegistroPrivacidade).where(RegistroPrivacidade.usuario_id==self.usuario)).scalars().all()
                snapshot_pronto.set()
                self.assertTrue(continuar.wait(10))
                return ConsultarPrivacidadeService.executar(self.usuario)['plano_liberado']
        for acao, esperado in (('revogar', False), ('aceitar', True)):
            snapshot_pronto.clear()
            continuar.clear()
            with ThreadPoolExecutor(1) as pool:
                futuro=pool.submit(consultar_antigo)
                self.assertTrue(snapshot_pronto.wait(10))
                self.decidir(acao)
                continuar.set()
                self.assertEqual(futuro.result(timeout=10), esperado)

    def test_negativa_concorrente_com_geracao_ou_recalculo(self):
        for recalcular in (False, True):
            r, _=self.decidir('aceitar')
            revisao=r.json['registro']['id']
            if not recalcular:
                self.base()
            atual=self.gerar().json['plano'] if recalcular else None
            barreira=Barrier(2)

            def gerar():
                with self.app.app_context():
                    db.session.get(Usuario, self.usuario)
                    barreira.wait(timeout=10)
                    try:
                        if atual:
                            return servicos().recalcular_plano.executar(
                                self.usuario,
                                {
                                    'chave_envio': str(uuid4()),
                                    'plano_atual_id': atual['id'],
                                    'confirmar': True
                                }
                            )[1]
                        return servicos().gerar_plano.executar(
                            self.usuario,
                            {'chave_envio': str(uuid4())}
                        )[1]
                    except AutenticacaoError as e:
                        return e.status_code

            def revogar():
                with self.app.app_context():
                    db.session.get(Usuario, self.usuario)
                    barreira.wait(timeout=10)
                    return servicos().revogar_consentimento_plano.executar(
                        self.usuario,
                        {
                            'versao': '1.0',
                            'revisao': revisao,
                            'chave_envio': str(uuid4()),
                            'confirmar': True
                        }
                    )[1]
            with ThreadPoolExecutor(2) as pool:
                geracao=pool.submit(gerar)
                negativa=pool.submit(revogar)
                self.assertIn(geracao.result(timeout=20), (201, 403))
                self.assertEqual(negativa.result(timeout=20), 201)
            with self.app.app_context():
                self.assertEqual(
                    db.session.execute(select(PlanoEstudo).where(PlanoEstudo.usuario_id==self.usuario)).scalars().all(),
                    []
                )
