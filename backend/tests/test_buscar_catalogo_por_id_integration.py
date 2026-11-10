"""GET/HEAD administrativos em MySQL real e schema próprio descartável."""
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import text

from app.core.relogio import agora_utc
from app.extensions import db
from app.modules.contas.services.autenticacao_service import CriarUsuarioService
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.models.assunto import Assunto
from tests.integration_support import MySQLIntegrationTestCase


class BuscarCatalogoPorIdIntegrationTest(MySQLIntegrationTestCase):
    def registros(self):
        materia = self.client.post(
            '/api/materias',
            json={
                'nome': f'Consulta {uuid4().hex}',
                'area_enem_id': 4
            }
        ).json
        assunto = self.client.post(
            '/api/assuntos',
            json={
                'nome': f'  Álgebra   {uuid4().hex}  ',
                'materia_id': materia['id']
            }
        ).json
        return materia, assunto

    def test_get_head_estados_payload_vinculos_sem_mutacao_csrf_ou_senha_recente(self):
        materia, assunto = self.registros()
        # A sessão continua válida; apenas a janela de reautenticação expirou.
        with self.app.app_context():
            db.session.execute(
                text('UPDATE sessoes SET reautenticada_em=:data'),
                {'data': agora_utc() - timedelta(hours=1)}
            )
            db.session.commit()
        csrf = self.client.csrf
        self.client.csrf = None
        try:
            for status in ('ativa', 'inativa', 'arquivada'):
                with self.app.app_context():
                    Materia.buscar_por_id(materia['id']).atualizar(status=status)
                    Assunto.buscar_por_id(assunto['id']).atualizar(status=status)
                    antes = [
                        Materia.buscar_por_id(materia['id']).to_dict(),
                        Assunto.buscar_por_id(assunto['id']).to_dict()
                    ]
                for recurso, registro in zip(('materias', 'assuntos'), antes):
                    path = f"/api/{recurso}/{registro['id']}"
                    for query in ('', '?status=ativa', '?status=todos&materia_id=0'):
                        response = self.client.get(path + query)
                        self.assertEqual(response.status_code, 200, response.json)
                        self.assertEqual(response.json, registro)
                        self.assertIsNone(response.json['descricao'])
                        self.assertEqual(response.headers['Cache-Control'], 'no-store')
                    head = self.client.head(path)
                    self.assertEqual(head.status_code, 200)
                    self.assertEqual(head.data, b'')
                    self.assertEqual(head.headers['Cache-Control'], 'no-store')
                with self.app.app_context():
                    depois = [
                        Materia.buscar_por_id(materia['id']).to_dict(),
                        Assunto.buscar_por_id(assunto['id']).to_dict()
                    ]
                    self.assertEqual(antes, depois)
                self.assertEqual(antes[1]['materia_id'], materia['id'])
                self.assertTrue(antes[1]['nome_normalizado'].startswith('álgebra '))
        finally:
            self.client.csrf = csrf
            with self.app.app_context():
                db.session.execute(
                    text('UPDATE sessoes SET reautenticada_em=:data'),
                    {'data': agora_utc()}
                )
                db.session.commit()

    def test_limites_ausencia_roteamento_e_options(self):
        for recurso in ('materias', 'assuntos'):
            for id_, esperado in (
                (0, 400),
                (2147483648, 400),
                (10**100, 400),
                (2147483647, 404),
                ('abc', 404),
                (-1, 404)
            ):
                for method in ('GET', 'HEAD'):
                    response = self.client.open(f'/api/{recurso}/{id_}', method=method)
                    self.assertEqual(response.status_code, esperado)
                    if isinstance(id_, int) and id_ >= 0:
                        self.assertEqual(response.headers['Cache-Control'], 'no-store')
                        if method == 'GET':
                            self.assertIn('erro', response.json)
            self.assertEqual(self.client.options(f'/api/{recurso}/1').status_code, 200)

    def test_anonimo_aluno_nao_revelam_existencia_mesmo_com_query(self):
        materia, assunto = self.registros()
        aluno = self.app.test_client()
        anonimo = self.app.test_client()
        senha = 'Senha sintética 123'
        email = f'aluno-{uuid4().hex}@teste.local'
        with self.app.app_context():
            CriarUsuarioService.executar(
                {
                    'nome': 'Aluno consulta',
                    'email': email,
                    'senha': senha,
                    'senha_confirmacao': senha
                },
                'aluno'
            )
        token = aluno.get('/api/auth/csrf').json['csrf_token']
        self.assertEqual(
            aluno.post(
                '/api/auth/login',
                json={'email': email, 'senha': senha},
                headers={'Origin': 'http://frontend.test', 'X-CSRF-Token': token}
            ).status_code,
            200
        )
        for recurso, registro in (('materias', materia), ('assuntos', assunto)):
            for id_ in (registro['id'], 0, 2147483647, 2147483648):
                for query in ('', '?status=ativa', '?status=todos'):
                    for client, esperado in ((anonimo, 401), (aluno, 403)):
                        for method in ('GET', 'HEAD'):
                            response = client.open(f'/api/{recurso}/{id_}{query}', method=method)
                            self.assertEqual(response.status_code, esperado)
                            self.assertEqual(response.headers['Cache-Control'], 'no-store')
                            if method == 'GET':
                                self.assertIn('erro', response.json)
                                self.assertNotIn('nome', response.json)
