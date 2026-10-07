"""Validacoes e primitivas da identidade escolar, sem acesso ao banco."""
import hashlib
import hmac
from datetime import datetime, timezone
from urllib.parse import urlsplit

from app.exceptions import ErroAplicacao


class AutenticacaoError(ErroAplicacao):
    def __init__(self, mensagem, status=400, codigo="dados_invalidos", retry_after=None):
        super().__init__(mensagem)
        self.status_code = status
        self.codigo = codigo
        self.retry_after = retry_after

    def to_dict(self):
        return {"erro": str(self), "codigo": self.codigo}


def agora_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def validar_email(valor):
    if not isinstance(valor, str):
        raise AutenticacaoError("Informe um e-mail válido.")
    email = valor.strip().lower()
    partes = email.split("@")
    if (not email.isascii() or len(email) > 254 or len(partes) != 2
            or not all(partes) or "." not in partes[-1] or ".." in email
            or any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in email)
            or partes[-1].startswith(".") or partes[-1].endswith(".")):
        raise AutenticacaoError("Informe um e-mail válido.")
    return email


def validar_dados(dados, campos):
    if not isinstance(dados, dict) or set(dados) != set(campos):
        raise AutenticacaoError("Informe somente os campos solicitados.")


def validar_senha(senha, minimo=8):
    if not isinstance(senha, str) or not minimo <= len(senha) <= 128:
        raise AutenticacaoError(f"A senha deve ter entre {minimo} e 128 caracteres.")
    return senha


def validar_cadastro(dados):
    validar_dados(dados, {"nome", "email", "senha", "senha_confirmacao"})
    nome = dados["nome"]
    if not isinstance(nome, str) or not 2 <= len(nome.strip()) <= 100:
        raise AutenticacaoError("O nome deve ter entre 2 e 100 caracteres.")
    senha = validar_senha(dados["senha"])
    if senha != dados["senha_confirmacao"]:
        raise AutenticacaoError("As senhas não coincidem.")
    return nome.strip(), validar_email(dados["email"]), senha


def hash_identificador(identificador):
    return hashlib.sha256(identificador.encode("ascii")).hexdigest()


def token_assinado(chave, identificador, proposito="csrf"):
    return hmac.new(chave, f"{proposito}:{identificador}".encode(), hashlib.sha256).hexdigest()


def configurar_autenticacao(app):
    chave = app.config.get("AUTH_SECRET_KEY", "")
    if not isinstance(chave, str) or len(chave) != 64:
        raise RuntimeError("Configure AUTH_SECRET_KEY com 64 caracteres hexadecimais aleatórios.")
    try:
        app.config["AUTH_KEY_BYTES"] = bytes.fromhex(chave)
        if len(app.config["AUTH_KEY_BYTES"]) != 32:
            raise ValueError("Chave incompleta")
    except ValueError:
        raise RuntimeError("AUTH_SECRET_KEY possui formato inválido.") from None
    origens = app.config["CORS_ORIGINS"]
    for origem in origens:
        url = urlsplit(origem)
        if (url.scheme not in {"http", "https"} or not url.netloc or url.path
                or url.query or url.fragment or url.username or "*" in origem):
            raise RuntimeError("CORS_ORIGINS exige origens HTTP/HTTPS explícitas, sem caminho.")
