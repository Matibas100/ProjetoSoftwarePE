"""Autenticacao completa em MySQL real, sem mocks ou atalhos de autorizacao."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import uuid4
from threading import Barrier

from sqlalchemy import text

from app.domain.autenticacao import agora_utc, hash_identificador
from app.extensions import db
from app.models.usuario import Usuario
from app.repositories.autenticacao_repository import AutenticacaoRepository
from app.services.autenticacao_service import CriarUsuarioService
from app.transaction_manager import TransactionManager
from tests.integration_support import MySQLIntegrationTestCase


ORIGIN = "http://frontend.test"
SENHA = "Senha de teste 123"


class AutenticacaoIntegrationTest(MySQLIntegrationTestCase):
    autenticar_administrador = False

    def setUp(self):
        self.client = self.app.test_client()
        self.email = f"aluno-{uuid4().hex}@teste.local"

    def request(self, path, dados=None, client=None, token=None):
        client = client or self.client
        if token is None:
            token = client.get("/api/auth/csrf").get_json()["csrf_token"]
        return client.post(path, json=dados, headers={"Origin": ORIGIN, "X-CSRF-Token": token})

    def cadastro(self, email=None, client=None):
        return self.request("/api/auth/cadastro", {"nome": "Aluno teste", "email": email or self.email,
            "senha": SENHA, "senha_confirmacao": SENHA}, client)

    def login(self, email=None, client=None, senha=SENHA):
        return self.request("/api/auth/login", {"email": email or self.email, "senha": senha}, client)

    def admin(self, client=None):
        email = f"admin-{uuid4().hex}@teste.local"
        with self.app.app_context():
            CriarUsuarioService.executar({"nome": "Admin teste", "email": email,
                "senha": SENHA, "senha_confirmacao": SENHA}, "administrador")
        self.assertEqual(self.login(email, client).status_code, 200)
        return email

    def datas(self, coluna, tempo, email=None):
        # Coluna vem exclusivamente dos literais abaixo definidos pelo teste.
        self.assertIn(coluna, {"ultimo_acesso_em", "expira_em", "reautenticada_em"})
        with self.app.app_context():
            db.session.execute(text(f"UPDATE sessoes s JOIN usuarios u ON u.id=s.usuario_id "
                f"SET s.{coluna}=:data WHERE u.email=:email"), {"data": tempo, "email": email or self.email})
            db.session.commit()

    def test_cadastro_login_cookie_identidade_logout(self):
        token_antes = self.client.get("/api/auth/csrf").get_json()["csrf_token"]
        self.assertEqual(self.cadastro().status_code, 201)
        self.assertEqual(self.client.get("/api/auth/sessao").status_code, 401)
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(token_antes, response.json["csrf_token"])
        self.assertEqual(response.json["usuario"]["perfil"], "aluno")
        self.assertEqual(response.json["destino"], "/aluno/inicio.html")
        cookie = response.headers["Set-Cookie"]
        for flag in ("HttpOnly", "SameSite=Lax", "Path=/api", "Max-Age=28800"):
            self.assertIn(flag, cookie)
        self.assertNotIn("Domain=", cookie)
        self.assertEqual(self.client.get("/api/auth/sessao").json["usuario"]["email"], self.email)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(self.request("/api/auth/logout").status_code, 204)
        self.assertEqual(self.request("/api/auth/logout").status_code, 204)
        self.assertEqual(self.client.get("/api/materias").status_code, 401)

    def test_validacao_duplicidade_e_perfil(self):
        dados = {"nome": "Teste", "email": self.email, "senha": SENHA, "senha_confirmacao": SENHA}
        for alteracao in ({"perfil": "administrador"}, {"nome": " "}, {"email": "a@b"},
                          {"senha": "curta"}, {"senha_confirmacao": "outra"}):
            self.assertEqual(self.request("/api/auth/cadastro", {**dados, **alteracao}).status_code, 400)
        self.assertEqual(self.request("/api/auth/cadastro", []).status_code, 400)
        self.assertEqual(self.cadastro().status_code, 201)
        self.assertEqual(self.cadastro("  " + self.email.upper() + "  ").status_code, 409)
        self.login()
        self.assertEqual(self.cadastro().json["codigo"], "ja_autenticado")
        self.assertEqual(self.login().json["codigo"], "ja_autenticado")

    def test_autorizacao_todas_rotas_existentes(self):
        self.cadastro(); self.login()
        for rule in self.app.url_map.iter_rules():
            if not rule.rule.startswith("/api/") or rule.rule.startswith("/api/auth/"):
                continue
            path = rule.rule
            for argumento in rule.arguments - set(rule.defaults or {}):
                path = path.replace(f"<int:{argumento}>", "2147483647")
            for method in rule.methods - {"OPTIONS"}:
                public = path == "/api/health"
                leitura = method in {"GET", "HEAD"} and path in {"/api/areas-enem", "/api/materias", "/api/assuntos"}
                anonymous = self.app.test_client().open(path, method=method)
                self.assertEqual(anonymous.status_code, 200 if public else 401, (path, method))
                headers = {"Origin": ORIGIN}
                esperado = 200 if public or leitura else 403
                if path.startswith('/api/aluno/'):
                    headers['X-CSRF-Token'] = self.client.get('/api/auth/sessao').json['csrf_token']
                    esperado = (404 if '/2147483647' in path else 200) if method in {'GET','HEAD'} else 400
                aluno = self.client.open(path, method=method, json={}, headers=headers)
                self.assertEqual(aluno.status_code, esperado, (path, method))
        for path in ("/api/materias?status=todos", "/api/assuntos?status=todos"):
            self.assertEqual(self.client.get(path).status_code, 403)
        self.assertEqual(self.client.get("/api/inexistente").status_code, 404)
        self.assertEqual(self.client.post("/api/areas-enem").status_code, 405)
        preflight = self.app.test_client().options("/api/materias", headers={"Origin": ORIGIN,
            "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "X-CSRF-Token"})
        self.assertEqual(preflight.status_code, 200)
        self.assertEqual(preflight.headers["Access-Control-Allow-Credentials"], "true")

    def test_csrf_origins_e_cookie_secure(self):
        self.assertEqual(self.client.post("/api/auth/login", json={}).status_code, 403)
        self.assertEqual(self.request("/api/auth/login", {}, token="errado").status_code, 401)
        self.client.get("/api/auth/csrf")
        self.assertEqual(self.request("/api/auth/login", {}, token="errado").json["codigo"], "csrf_invalido")
        self.cadastro(); self.login()
        token = self.client.get("/api/auth/sessao").json["csrf_token"]
        for origin in (None, "null", "http://nao-permitido.test"):
            headers = {"X-CSRF-Token": token}
            if origin is not None: headers["Origin"] = origin
            self.assertEqual(self.client.post("/api/auth/logout", headers=headers).status_code, 403)
        outro = self.app.test_client().get("/api/auth/csrf").json["csrf_token"]
        self.assertEqual(self.request("/api/auth/logout", token=outro).status_code, 403)
        self.assertEqual(self.client.get("/api/auth/sessao").status_code, 200)
        self.app.config["AUTH_COOKIE_SECURE"] = True
        try:
            self.assertIn("Secure", self.app.test_client().get("/api/auth/csrf").headers["Set-Cookie"])
        finally: self.app.config["AUTH_COOKIE_SECURE"] = False

    def test_expiracao_absoluta_inatividade_e_reautenticacao(self):
        email = self.admin()
        self.datas("reautenticada_em", agora_utc() - timedelta(minutes=15), email)
        token = self.client.get("/api/auth/sessao").json["csrf_token"]
        for method, path, body in (("DELETE", "/api/materias/1", {}),
                ("POST", "/api/assuntos/1/transferir", {}), ("POST", "/api/materias/1/inativar", {}),
                ("POST", "/api/assuntos/1/arquivar", {}), ("POST", "/api/assuntos/1/reativar", {}),
                ("PUT", "/api/assuntos/1", {"materia_id": 1}),
                ("PUT", "/api/materias/1", {"status": "ativa"}),
                ("PUT", "/api/materias/1", {"area_enem_id": 4})):
            response = self.client.open(path, method=method, json=body, headers={"Origin": ORIGIN, "X-CSRF-Token": token})
            self.assertEqual(response.json["codigo"], "reautenticacao_necessaria")
        self.assertEqual(self.request("/api/auth/reautenticar", {"senha": "incorreta"}).json["codigo"], "credenciais_invalidas")
        self.assertEqual(self.client.get("/api/auth/sessao").status_code, 200)
        self.assertEqual(self.request("/api/auth/reautenticar", {"senha": SENHA}).status_code, 200)
        self.assertEqual(self.client.delete("/api/materias/2147483647", headers={"Origin": ORIGIN,
            "X-CSRF-Token": token}).status_code, 404)
        self.datas("ultimo_acesso_em", agora_utc() - timedelta(minutes=30), email)
        self.assertEqual(self.client.get("/api/auth/sessao").status_code, 401)
        self.login(email)
        self.datas("expira_em", agora_utc(), email)
        self.assertEqual(self.client.get("/api/materias").status_code, 401)

    def test_limite_senha_inativa_e_retomada(self):
        self.cadastro()
        for attempt in range(5):
            r = self.login(senha="errada")
            self.assertEqual(r.status_code, 401 if attempt < 4 else 429)
        self.assertEqual(self.login().status_code, 429)
        self.assertIn("Retry-After", self.login().headers)
        with self.app.app_context():
            db.session.execute(text("UPDATE auth_limites SET janela_inicio=:data, bloqueado_ate=:data"),
                               {"data": agora_utc() - timedelta(minutes=16)})
            db.session.commit()
        self.assertEqual(self.login().status_code, 200)
        for attempt in range(5):
            r = self.request("/api/auth/reautenticar", {"senha": "errada"})
            self.assertEqual(r.status_code, 401 if attempt < 4 else 429)
        self.request("/api/auth/logout")
        with self.app.app_context():
            Usuario.buscar_por_email(self.email).atualizar(ativo=False)
        self.assertEqual(self.login().json["erro"], "E-mail ou senha inválidos.")
        self.assertEqual(self.login("naoexiste@teste.local").json["erro"], "E-mail ou senha inválidos.")

    def test_cli_conta_limpeza_e_revogacao(self):
        email = f"cli-{uuid4().hex}@teste.local"
        runner = self.app.test_cli_runner()
        r = runner.invoke(args=["criar-administrador"], input=f"Teste CLI\n{email}\n{SENHA}\n{SENHA}\n")
        self.assertEqual(r.exit_code, 0, r.output)
        self.assertNotIn(SENHA, r.output)
        self.assertEqual(self.login(email).json["usuario"]["perfil"], "administrador")
        duplicate = runner.invoke(args=["criar-administrador"], input=f"Teste CLI\n{email}\n{SENHA}\n{SENHA}\n")
        self.assertNotEqual(duplicate.exit_code, 0)
        mismatch = runner.invoke(args=["criar-administrador"], input=f"Teste CLI\n{email}\n{SENHA}\nerrada\n")
        self.assertNotEqual(mismatch.exit_code, 0)
        outro = self.app.test_client(); self.login(email, outro)
        self.request("/api/auth/logout")
        self.assertEqual(outro.get("/api/auth/sessao").status_code, 200)
        with self.app.app_context():
            user = Usuario.buscar_por_email(email)
            TransactionManager.executar(lambda: AutenticacaoRepository.revogar_usuario(user.id, agora_utc()))
        self.assertEqual(outro.get("/api/auth/sessao").status_code, 401)
        self.login(email)
        with self.app.app_context():
            db.session.execute(text("UPDATE sessoes SET revogada_em=:data WHERE revogada_em IS NOT NULL"),
                               {"data": agora_utc() - timedelta(days=2)})
            db.session.execute(text("UPDATE auth_limites SET janela_inicio=:data, bloqueado_ate=NULL"),
                               {"data": agora_utc() - timedelta(days=2)})
            db.session.commit()
        clean = runner.invoke(args=["limpar-autenticacao"])
        self.assertEqual(clean.exit_code, 0, clean.output)
        self.assertEqual(self.client.get("/api/auth/sessao").status_code, 200)

    def test_concorrencia_cadastro_e_contador(self):
        def criar(_):
            return self.cadastro(client=self.app.test_client()).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(criar, range(2))), [201, 409])
        def falhar(_):
            return self.login(client=self.app.test_client(), senha="errada").status_code
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(falhar, range(5)))
        self.assertEqual(sorted(results), [401, 401, 401, 401, 429])

    def test_cli_duplicado_preserva_aluno_senha_e_catalogo(self):
        self.cadastro()
        with self.app.app_context():
            antes = {t: db.session.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar_one()
                for t in ("usuarios", "materias", "assuntos", "questoes", "assunto_transferencias")}
        runner = self.app.test_cli_runner()
        duplicate = runner.invoke(args=["criar-administrador"], input=f"Outro nome\n{self.email}\nOutra senha 123\nOutra senha 123\n")
        self.assertNotEqual(duplicate.exit_code, 0)
        self.assertEqual(self.login().json["usuario"]["perfil"], "aluno")
        clean = runner.invoke(args=["limpar-autenticacao"])
        self.assertEqual(clean.exit_code, 0)
        with self.app.app_context():
            self.assertEqual(Usuario.buscar_por_email(self.email).nome, "Aluno teste")
            depois = {t: db.session.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar_one() for t in antes}
            self.assertEqual(antes, depois)

    def test_revogacao_concorrente_nao_ressuscita_sessao(self):
        self.cadastro(); self.login()
        identificador = self.client.get_cookie("enem_session", path="/api").value
        with self.app.app_context():
            sessao_id = AutenticacaoRepository.consultar_sessao(hash_identificador(identificador)).id
        barrier = Barrier(2)
        def operar(revogar):
            with self.app.app_context():
                barrier.wait(timeout=10)
                def transacao():
                    if revogar:
                        AutenticacaoRepository.revogar(sessao_id, agora_utc())
                    else:
                        AutenticacaoRepository.renovar_acesso(sessao_id, agora_utc())
                TransactionManager.executar(transacao)
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(operar, [True, False]))
        self.assertEqual(self.client.get("/api/auth/sessao").status_code, 401)

    def test_rotacao_reverte_nova_sessao_se_revogacao_falhar(self):
        self.cadastro()
        identificador = self.client.get_cookie("enem_session", path="/api").value
        with self.app.app_context():
            anterior = AutenticacaoRepository.consultar_sessao(hash_identificador(identificador)).id
            # Falha MySQL real na segunda escrita: a primeira tambem deve ser revertida.
            db.session.execute(text("CREATE TRIGGER auth_test_rotation BEFORE UPDATE ON sessoes "
                "FOR EACH ROW BEGIN IF OLD.id = :id THEN "
                "SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='falha de teste'; END IF; END"), {"id": anterior})
            db.session.commit()
        try:
            response = self.login()
            self.assertEqual(response.status_code, 500)
            self.assertNotIn("falha de teste", response.get_data(as_text=True))
            with self.app.app_context():
                sessao = AutenticacaoRepository.consultar_sessao(hash_identificador(identificador))
                self.assertIsNone(sessao.revogada_em)
                self.assertEqual(db.session.execute(text("SELECT COUNT(*) FROM sessoes s JOIN usuarios u "
                    "ON u.id=s.usuario_id WHERE u.email=:email"), {"email": self.email}).scalar_one(), 0)
        finally:
            with self.app.app_context():
                db.session.execute(text("DROP TRIGGER auth_test_rotation")); db.session.commit()
        self.assertEqual(self.login().status_code, 200)
