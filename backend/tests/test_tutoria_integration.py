"""HTTP/privacidade em MySQL real; Tutor desabilitado, sem provedor falso."""
from uuid import uuid4
import json
from sqlalchemy import text
from app.extensions import db
from app.modules.contas.api import ValidarPermissaoTutoriaService
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.domain.privacidade import DOCUMENTOS
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade
from app.modules.contas.services.autenticacao_service import CriarUsuarioService
from tests.integration_support import MySQLIntegrationTestCase
from tests import test_praticas_integration as fixture


ENTRADA = {
    'disciplina': 'Física',
    'nivel': 'ensino_medio',
    'assunto': 'Eletricidade',
    'duvida': 'Qual a diferença entre corrente e tensão?'
}


class TutoriaIntegrationTest(MySQLIntegrationTestCase):
    conta = fixture.PraticasIntegrationTest.conta

    def setUp(self):
        self.senha = 'Senha sintética para tutoria 123'
        self.aluno, self.usuario, _ = self.conta()

    def test_contrato_http_autorizacao_antes_do_corpo_e_no_store(self):
        anonimo = self.app.test_client()
        for corpo in (b'{', b'x'*17000):
            for cliente, headers, status in (
                (anonimo, {}, 401),
                (self.client, {}, 403),
                (self.aluno, {'Origin': 'http://outra.test'}, 403),
                (self.aluno, {'X-CSRF-Token': 'invalido'}, 403)
            ):
                r = cliente.post(
                    '/api/tutoria',
                    data=corpo,
                    content_type='application/json',
                    headers=headers
                )
                self.assertEqual(r.status_code, status)
                self.assertEqual(r.headers['Cache-Control'], 'no-store')
        for corpo, content_type in (
            (b'{', 'application/json'),
            (b'null', 'application/json'),
            (b'[]', 'application/json'),
            (b'{}', 'application/json'),
            (b'<html>', 'text/html'),
            (b'', 'application/json')
        ):
            r = self.aluno.post('/api/tutoria', data=corpo, content_type=content_type)
            self.assertEqual((r.status_code, r.json['codigo']), (400, 'dados_invalidos'))
        r = self.aluno.post('/api/tutoria', data=b'x'*16385, content_type='application/json')
        self.assertEqual((r.status_code, r.json['codigo']), (413, 'corpo_muito_grande'))
        self.assertIsNone(self.app.config.get('MAX_CONTENT_LENGTH'))
        r = self.aluno.post('/api/tutoria', json=ENTRADA)
        self.assertEqual((r.status_code, r.json['codigo']), (503, 'tutor_indisponivel'))
        self.assertEqual(r.headers['Cache-Control'], 'no-store')
        corpo = json.dumps(ENTRADA).encode()
        r = self.aluno.post(
            '/api/tutoria',
            data=corpo + b' '*(16384-len(corpo)),
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 503)  # Limite inclusivo de bytes, sem rede.
        self.assertEqual(self.aluno.post('/api/tutoria-outra', json=ENTRADA).status_code, 404)
        self.assertEqual(self.aluno.post('/api/materias', json={}).status_code, 403)
        self.assertEqual(self.client.get('/api/materias?status=todos').status_code, 200)
        self.assertEqual(self.aluno.options('/api/tutoria').status_code, 200)

    def test_sem_uso_antigo_e_plano_negativo_independente_sem_transacao_retida(self):
        with self.app.app_context():
            legado = CriarUsuarioService.executar(
                {
                    'nome': 'Legado sintético',
                    'email': uuid4().hex+'@teste.local',
                    'senha': self.senha,
                    'senha_confirmacao': self.senha
                },
                'aluno'
            )
            legado_id = legado['id']
            for versao in (None, '1.0', '2.0'):
                if versao:
                    doc = DOCUMENTOS['uso'][versao]
                    RegistroPrivacidade(
                        usuario_id=legado_id,
                        tipo='uso',
                        acao='aceitar',
                        versao=versao,
                        documento_sha256=doc['sha256'],
                        chave_envio=str(uuid4()),
                        revisao_base=0
                    ).salvar()
                if versao != '2.0':
                    with self.assertRaises(AutenticacaoError) as cm:
                        ValidarPermissaoTutoriaService.executar(legado_id)
                    self.assertEqual(
                        (
                            cm.exception.status_code,
                            cm.exception.codigo
                        ),
                        (
                            409,
                            'termos_uso_pendentes'
                        )
                    )
                else:
                    self.assertIsNone(ValidarPermissaoTutoriaService.executar(legado_id))
                self.assertFalse(db.session().in_transaction())
                self.assertEqual(db.engine.pool.checkedout(), 0)
        # Teste HTTP de uso antigo com sessão real, sem substituir serviço/provedor.
        with self.app.app_context():
            db.session.execute(
                text('UPDATE registros_privacidade SET versao=:v,documento_sha256=:h '
                    "WHERE usuario_id=:id AND tipo='uso'"),
                {'v': '1.0', 'h': DOCUMENTOS['uso']['1.0']['sha256'], 'id': self.usuario}
            )
            db.session.commit()
        r = self.aluno.post('/api/tutoria', json=ENTRADA)
        self.assertEqual((r.status_code, r.json['codigo']), (409, 'termos_uso_pendentes'))
        estado = self.aluno.get('/api/aluno/privacidade').json
        self.assertIsNone(estado['consentimento_plano']['registro'])
        self.assertEqual(
            self.aluno.post(
                '/api/aluno/privacidade/termos-uso',
                json={
                    'versao': '2.0',
                    'revisao': estado['termos_uso']['registro']['id'],
                    'chave_envio': str(uuid4())
                }
            ).status_code,
            201
        )
        for acao in ('recusar', 'aceitar', 'revogar'):
            estado = self.aluno.get('/api/aluno/privacidade').json
            registro = estado['consentimento_plano']['registro']
            dados = {
                'versao': '1.0',
                'revisao': registro['id'] if registro else 0,
                'chave_envio': str(uuid4())
            }
            if acao != 'aceitar':
                dados['confirmar'] = True
            self.assertEqual(
                self.aluno.post(
                    '/api/aluno/privacidade/consentimento-plano/'+acao,
                    json=dados
                ).status_code,
                201
            )
            with self.app.app_context():
                ValidarPermissaoTutoriaService.executar(self.usuario)
                self.assertFalse(db.session().in_transaction())
                self.assertEqual(db.engine.pool.checkedout(), 0)
            self.assertEqual(self.aluno.post('/api/tutoria', json=ENTRADA).status_code, 503)
            depois = self.aluno.get('/api/aluno/privacidade').json
            self.assertEqual(depois['consentimento_plano']['registro']['acao'], acao)
