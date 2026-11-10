"""Casos de uso de autenticacao: coordenacao sem SQL ou db.session."""
import hmac
import math
import secrets
from uuid import uuid4
from datetime import timedelta

from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.relogio import agora_utc
from app.modules.contas.domain.autenticacao import (
    AutenticacaoError,
    hash_identificador,
    token_assinado,
    validar_cadastro,
    validar_dados,
    validar_email,
    validar_senha,
)
from app.modules.contas.models.sessao import Sessao
from app.modules.contas.models.usuario import Usuario
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade
from app.modules.contas.services.privacidade_validacao import validar_versao
from app.modules.contas.repositories.autenticacao_repository import AutenticacaoRepository as Repo
from app.transaction_manager import TransactionManager


HASH_FICTICIO = generate_password_hash(secrets.token_urlsafe(32), method="scrypt:32768:8:1")


def sessao_invalida():
    return AutenticacaoError("Sua sessão expirou. Entre novamente.", 401, "sessao_invalida")


def destino(usuario):
    return "/admin/materias.html" if usuario.perfil == "administrador" else "/aluno/inicio.html"


class ConsultarSessaoService:
    @staticmethod
    def executar(identificador, autenticada=True):
        if not isinstance(
            identificador,
            str
        ) or len(identificador) != 43 or not identificador.isascii():
            raise sessao_invalida()
        sessao = Repo.consultar_sessao(hash_identificador(identificador))
        agora = agora_utc()
        if (sessao is None or sessao.revogada_em is not None or agora >= sessao.expira_em
            or (sessao.usuario_id is not None and (
                agora >= sessao.ultimo_acesso_em + timedelta(minutes=30)
                or not sessao.usuario.ativo))
            or (autenticada and sessao.usuario_id is None)):
            raise sessao_invalida()
        return sessao

    @staticmethod
    def renovar(sessao):
        if not TransactionManager.executar(lambda: Repo.renovar_acesso(sessao.id, agora_utc())):
            raise sessao_invalida()


class PrepararCsrfService:
    @staticmethod
    def executar(identificador, chave):
        try:
            sessao = ConsultarSessaoService.executar(identificador, autenticada=False)
        except AutenticacaoError:
            identificador, sessao = CriarSessaoService.executar(None)
        return identificador, sessao, token_assinado(chave, identificador)


class CriarSessaoService:
    @staticmethod
    def executar(usuario, anterior=None, email_esperado=None):
        identificador = secrets.token_urlsafe(32)
        agora = agora_utc()
        sessao = Sessao(
            usuario_id=usuario.id if usuario else None,
            identificador_hash=hash_identificador(identificador),
            criada_em=agora,
            ultimo_acesso_em=agora,
            expira_em=agora + (
                timedelta(hours=8) if usuario else timedelta(minutes=10)),
            reautenticada_em=agora if usuario else None
        )

        def persistir():
            if usuario is not None:
                atual = Repo.usuario_ativo_bloqueado(usuario.id)
                if email_esperado is not None and (atual is None or atual.email != email_esperado):
                    raise AutenticacaoError(
                        "E-mail ou senha inválidos.",
                        401,
                        "credenciais_invalidas"
                    )
                if atual is None:
                    raise sessao_invalida()
            sessao.salvar(confirmar=False)
            if anterior is not None:
                Repo.revogar(anterior.id, agora)
            return identificador, sessao
        return TransactionManager.executar(persistir)


class CadastrarAlunoService:
    @staticmethod
    def executar(dados):
        validar_dados(dados, {"nome", "email", "senha", "senha_confirmacao", "termos_uso"})
        termos = dados["termos_uso"]
        validar_dados(termos, {"versao", "aceito"})
        if termos["aceito"] is not True or not isinstance(termos["versao"], str):
            raise AutenticacaoError("Confirme explicitamente o Termo de Uso.")
        doc = validar_versao("uso", termos["versao"])
        usuario = preparar_usuario({k: v for k, v in dados.items() if k != "termos_uso"}, "aluno")

        def cadastrar():
            usuario.salvar(confirmar=False)
            RegistroPrivacidade(
                usuario_id=usuario.id,
                tipo="uso",
                acao="aceitar",
                versao=doc["versao"],
                documento_sha256=doc["sha256"],
                chave_envio=str(uuid4()),
                revisao_base=0
            ).salvar(confirmar=False)
            return usuario.to_dict()
        return persistir_usuario(cadastrar)


def preparar_usuario(dados, perfil):
    nome, email, senha = validar_cadastro(dados)
    if perfil not in {"aluno", "administrador"}:
        raise AutenticacaoError("Perfil inválido.")
    return Usuario(
        nome=nome,
        email=email,
        perfil=perfil,
        ativo=True,
        senha_hash=generate_password_hash(senha, method="scrypt:32768:8:1"),
        criado_em=agora_utc()
    )


def persistir_usuario(operacao):
    try:
        return TransactionManager.executar(operacao)
    except IntegrityError as erro:
        # Só uma violação da chave do e-mail é duplicidade de cadastro.
        if "uq_usuarios_email" in str(erro.orig):
            raise AutenticacaoError(
                "Este e-mail já está cadastrado. Entre na sua conta.",
                409,
                "email_em_uso"
            ) from None
        raise


class CriarUsuarioService:
    @staticmethod
    def executar(dados, perfil):
        usuario = preparar_usuario(dados, perfil)
        return persistir_usuario(lambda: usuario.salvar(confirmar=False).to_dict())


class ValidarSenhaService:
    @staticmethod
    def executar(usuario, senha, chave_limite, email_esperado=None):
        hash_anterior = usuario.senha_hash if usuario else HASH_FICTICIO
        correta = check_password_hash(hash_anterior, senha)
        agora = agora_utc()

        def verificar():
            limite = Repo.limite_bloqueado(chave_limite, agora)
            if limite.bloqueado_ate and agora < limite.bloqueado_ate:
                return None, math.ceil((limite.bloqueado_ate - agora).total_seconds())
            if agora >= limite.janela_inicio + timedelta(minutes=15):
                limite.atualizar(confirmar=False, falhas=0, janela_inicio=agora, bloqueado_ate=None)
            atual = Repo.usuario_ativo_bloqueado(usuario.id) if usuario else None
            if (correta and atual is not None and atual.senha_hash == hash_anterior
                and (email_esperado is None or atual.email == email_esperado)):
                limite.atualizar(confirmar=False, falhas=0, janela_inicio=agora, bloqueado_ate=None)
                return atual, None
            falhas = limite.falhas + 1
            bloqueio = agora + timedelta(minutes=15) if falhas >= 5 else None
            limite.atualizar(confirmar=False, falhas=falhas, bloqueado_ate=bloqueio)
            return None, 900 if bloqueio else None
        atual, espera = TransactionManager.executar(verificar)
        if espera is not None:
            raise AutenticacaoError(
                "Muitas tentativas. Aguarde e tente novamente.",
                429,
                "tentativas_excedidas",
                espera
            )
        if atual is None:
            raise AutenticacaoError("E-mail ou senha inválidos.", 401, "credenciais_invalidas")
        return atual


class LoginService:
    @staticmethod
    def executar(dados, anterior, chave):
        validar_dados(dados, {"email", "senha"})
        email = validar_email(dados["email"])
        senha = validar_senha(dados["senha"], minimo=1)
        usuario = ValidarSenhaService.executar(
            Usuario.buscar_por_email(email),
            senha,
            token_assinado(chave, email, "login-limite"),
            email_esperado=email
        )
        identificador, sessao = CriarSessaoService.executar(usuario, anterior, email_esperado=email)
        return identificador, sessao, {
            "usuario": usuario.to_dict(),
            "csrf_token": token_assinado(chave, identificador),
            "destino": destino(usuario)
        }


class LogoutService:
    @staticmethod
    def executar(sessao):
        if sessao is not None:
            TransactionManager.executar(lambda: Repo.revogar(sessao.id, agora_utc()))


class ReautenticarService:
    @staticmethod
    def executar(dados, sessao, chave):
        validar_dados(dados, {"senha"})
        ValidarSenhaService.executar(
            sessao.usuario,
            validar_senha(dados["senha"], minimo=1),
            token_assinado(chave, str(sessao.usuario_id), "reauth-limite")
        )

        def renovar():
            if not Repo.renovar_acesso(sessao.id, agora_utc()):
                raise sessao_invalida()
            sessao.atualizar(confirmar=False, reautenticada_em=agora_utc())
        TransactionManager.executar(renovar)


class AutorizarService:
    @staticmethod
    def executar(
        identificador,
        perfil_admin=False,
        mutacao=False,
        origem=None,
        origens=(),
        csrf=None,
        chave=b"",
        sensivel=False
    ):
        sessao = ConsultarSessaoService.executar(identificador)
        if perfil_admin and sessao.usuario.perfil != "administrador":
            raise AutenticacaoError("Você não tem acesso a esta operação.", 403, "acesso_negado")
        if mutacao:
            ValidarCsrfService.executar(identificador, origem, origens, csrf, chave)
        if sensivel and (sessao.reautenticada_em is None
            or agora_utc() >= sessao.reautenticada_em + timedelta(minutes=15)):
            raise AutenticacaoError(
                "Confirme sua senha para continuar.",
                403,
                "reautenticacao_necessaria"
            )
        ConsultarSessaoService.renovar(sessao)
        return sessao


class ValidarCsrfService:
    @staticmethod
    def executar(identificador, origem, origens, csrf, chave):
        if origem not in origens:
            raise AutenticacaoError("Origem não autorizada.", 403, "origem_nao_permitida")
        ConsultarSessaoService.executar(identificador, autenticada=False)
        if not isinstance(
            csrf,
            str
        ) or not csrf.isascii() or not hmac.compare_digest(
            csrf,
            token_assinado(
                chave,
                identificador
            )
        ):
            raise AutenticacaoError(
                "Atualize sua sessão e confirme a ação novamente.",
                403,
                "csrf_invalido"
            )


class LimparAutenticacaoService:
    @staticmethod
    def executar():
        return TransactionManager.executar(lambda: Repo.limpar(agora_utc()))
