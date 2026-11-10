from datetime import timedelta
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from app import create_app
from app.core.relogio import agora_utc
from app.modules.contas.domain.autenticacao import (
    AutenticacaoError,
    configurar_autenticacao,
    validar_cadastro,
    validar_dados,
    validar_email,
    validar_senha,
    token_assinado,
)
from app.modules.contas.services import autenticacao_service as service
from app.modules.contas.controllers.autenticacao_controller import AutenticacaoController
from database import migrate


class AutenticacaoUnitTest(unittest.TestCase):
    def test_validacao_sem_transformar_senha(self):
        self.assertEqual(validar_email("  ALUNO+tag@TESTE.local "), "aluno+tag@teste.local")
        for value in (
            None,
            2,
            "",
            "a@b",
            "a@@b.c",
            "a@.b.c",
            "a@b.c.",
            "a..b@c.d",
            "a b@c.d",
            "á@b.c",
            "a\x00@b.c",
            "a" * 255 + "@b.c"
        ):
            with self.subTest(value=value), self.assertRaises(AutenticacaoError):
                validar_email(value)
        for value in (None, [], "curta", "a" * 129):
            with self.assertRaises(AutenticacaoError):
                validar_senha(value)
        self.assertEqual(validar_senha(" espaços "), " espaços ")
        for value in ([], {}, {"perfil": "administrador"}):
            with self.assertRaises(AutenticacaoError):
                validar_dados(value, {"email", "senha"})
        dados = {
            "nome": " Aluno ",
            "email": "a@b.c",
            "senha": "abcdefgh",
            "senha_confirmacao": "abcdefgh"
        }
        self.assertEqual(validar_cadastro(dados), ("Aluno", "a@b.c", "abcdefgh"))
        for extra in ({"nome": 2}, {"nome": "x"}, {"senha_confirmacao": "abcdefgi"}):
            with self.assertRaises(AutenticacaoError):
                validar_cadastro({**dados, **extra})
        self.assertNotEqual(
            token_assinado(
                b"test",
                "identificador"
            ),
            token_assinado(
                b"test",
                "identificador",
                "login-limite"
            )
        )

    def test_configuracao_exige_chave_e_origens_explicitas(self):
        for chave in (None, "", "x" * 64, "ab" * 31 + "  "):
            with self.assertRaises(RuntimeError):
                configurar_autenticacao(SimpleNamespace(config={
                    "AUTH_SECRET_KEY": chave,
                    "CORS_ORIGINS": []
                }))
        for origem in (
            "*",
            "http://a.test/",
            "http://a.test?q=1",
            "http://u@a.test",
            "ftp://a.test",
            "null",
            "http://a.test#x"
        ):
            with self.assertRaises(RuntimeError):
                configurar_autenticacao(SimpleNamespace(config={
                    "AUTH_SECRET_KEY": "ab" * 32,
                    "CORS_ORIGINS": [origem]
                }))
        configurar_autenticacao(SimpleNamespace(config={
            "AUTH_SECRET_KEY": "ab" * 32,
            "CORS_ORIGINS": []
        }))

    @patch.object(service.Repo, "consultar_sessao")
    def test_sessao_invalida_em_todos_limites(self, consultar):
        now = agora_utc()
        session = SimpleNamespace(
            usuario_id=1,
            usuario=SimpleNamespace(ativo=True),
            revogada_em=None,
            expira_em=now + timedelta(hours=1),
            ultimo_acesso_em=now
        )
        consultar.return_value = session
        for token in (None, "curto", "á" * 43):
            with self.assertRaises(AutenticacaoError):
                service.ConsultarSessaoService.executar(token)
        self.assertIs(service.ConsultarSessaoService.executar("a" * 43), session)
        for field, value in (
            ("revogada_em", now),
            ("expira_em", now),
            ("ultimo_acesso_em", now - timedelta(minutes=30)),
            ("usuario_id", None)
        ):
            original = getattr(session, field)
            setattr(session, field, value)
            with self.assertRaises(AutenticacaoError):
                service.ConsultarSessaoService.executar("a" * 43)
            setattr(session, field, original)
        session.usuario.ativo = False
        with self.assertRaises(AutenticacaoError):
            service.ConsultarSessaoService.executar("a" * 43)
        consultar.return_value = None
        with self.assertRaises(AutenticacaoError):
            service.ConsultarSessaoService.executar("a" * 43)

    @patch.object(service.TransactionManager, "executar", side_effect=lambda fn: fn())
    @patch.object(service.Repo, "renovar_acesso", return_value=False)
    def test_renovacao_nao_reativa_revogada(self, _, __):
        with self.assertRaises(AutenticacaoError):
            service.ConsultarSessaoService.renovar(SimpleNamespace(id=1))

    @patch.object(service.ConsultarSessaoService, "executar")
    def test_csrf_e_permissoes_unitarios(self, consultar):
        session = SimpleNamespace(usuario=SimpleNamespace(perfil="aluno"), reautenticada_em=None)
        consultar.return_value = session
        with self.assertRaises(AutenticacaoError) as error:
            service.AutorizarService.executar("a", perfil_admin=True)
        self.assertEqual(error.exception.codigo, "acesso_negado")
        with self.assertRaises(AutenticacaoError):
            service.AutorizarService.executar("a", sensivel=True)
        with self.assertRaises(AutenticacaoError):
            service.ValidarCsrfService.executar("a", None, [], "x", b"a")
        with self.assertRaises(AutenticacaoError):
            service.ValidarCsrfService.executar("a", "o", ["o"], None, b"a")
        service.ValidarCsrfService.executar("a", "o", ["o"], token_assinado(b"a", "a"), b"a")

    def test_erros_http_neutros_sem_excecao_sensivel(self):
        from tests.unit.test_config_and_app import TestConfig
        app = create_app(TestConfig)
        with app.test_request_context():
            with patch.object(
                service.PrepararCsrfService,
                "executar",
                side_effect=RuntimeError("segredo-sentinela")
            ):
                response = AutenticacaoController.csrf()
                self.assertEqual(response.status_code, 500)
                self.assertNotIn("segredo-sentinela", response.get_data(as_text=True))
            with patch.object(
                service.PrepararCsrfService,
                "executar",
                side_effect=AutenticacaoError("erro")
            ):
                self.assertEqual(AutenticacaoController.csrf().status_code, 400)

    @patch.object(service.TransactionManager, "executar", side_effect=RuntimeError("commit falhou"))
    def test_criar_sessao_falha_sem_credencial_parcial(self, transaction):
        with self.assertRaises(RuntimeError):
            service.CriarSessaoService.executar(None)

    @patch.object(migrate, "_detect_catalogo_prefix", return_value="003")
    def test_baseline_auth_recusa_catalogo_preparatorio(self, _):
        with self.assertRaises(migrate.MigrationError):
            migrate._detect_auth_prefix(None, set())

    def test_perfil_invalido_nao_cria_usuario(self):
        with self.assertRaises(AutenticacaoError):
            service.CriarUsuarioService.executar(
                {
                    "nome": "Aluno",
                    "email": "a@b.c",
                    "senha": "abcdefgh",
                    "senha_confirmacao": "abcdefgh"
                },
                "inventado"
            )

    def test_cli_nao_expoe_excecao_interna(self):
        from tests.unit.test_config_and_app import TestConfig
        app = create_app(TestConfig)
        runner = app.test_cli_runner()
        for method, command, entrada in (
            (
                "CriarUsuarioService",
                "criar-administrador",
                "Teste\na@b.c\nabcdefgh\nabcdefgh\n"
            ),
            ("LimparAutenticacaoService", "limpar-autenticacao", "")
        ):
            with patch.object(
                getattr(
                    service,
                    method
                ),
                "executar",
                side_effect=RuntimeError("segredo-sentinela")
            ):
                result = runner.invoke(args=[command], input=entrada)
                self.assertNotEqual(result.exit_code, 0)
                self.assertNotIn("segredo-sentinela", result.output)
