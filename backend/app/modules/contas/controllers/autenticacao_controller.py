import math
from flask import current_app, g, jsonify, request

from app.core.relogio import agora_utc
from app.modules.contas.domain.autenticacao import AutenticacaoError, token_assinado
from app.http_response import responder_http
from app.modules.contas.services.autenticacao_service import (
    CadastrarAlunoService, LoginService, LogoutService,
    PrepararCsrfService, ReautenticarService, destino,
)


COOKIE = "enem_session"


def cookie_sessao(resposta, identificador=None, autenticada=False, expira_em=None):
    duracao = 28800 if autenticada else 600
    if expira_em is not None:
        duracao = min(duracao, max(0, math.ceil((expira_em - agora_utc()).total_seconds())))
    resposta.set_cookie(COOKIE, identificador or "", httponly=True,
        secure=current_app.config["AUTH_COOKIE_SECURE"], samesite="Lax", path="/api",
        max_age=duracao if identificador else 0)
    return resposta


def resposta_erro(erro):
    resposta = jsonify(erro.to_dict())
    resposta.status_code = erro.status_code
    if erro.codigo == "sessao_invalida":
        cookie_sessao(resposta)
    if erro.retry_after is not None:
        resposta.headers["Retry-After"] = str(erro.retry_after)
    return resposta


class AutenticacaoController:
    @staticmethod
    def csrf():
        def operacao():
            identificador, sessao, token = PrepararCsrfService.executar(
                request.cookies.get(COOKIE), current_app.config["AUTH_KEY_BYTES"])
            return cookie_sessao(jsonify({"csrf_token": token}), identificador,
                                sessao.usuario_id is not None, sessao.expira_em)
        return AutenticacaoController._responder(operacao)

    @staticmethod
    def cadastro():
        return AutenticacaoController._responder(lambda: (
            jsonify({"usuario": CadastrarAlunoService.executar(request.get_json(silent=True))}), 201))

    @staticmethod
    def login():
        def operacao():
            identificador, sessao, dados = LoginService.executar(request.get_json(silent=True),
                g.auth_sessao, current_app.config["AUTH_KEY_BYTES"])
            return cookie_sessao(jsonify(dados), identificador, True, sessao.expira_em)
        return AutenticacaoController._responder(operacao)

    @staticmethod
    def sessao():
        usuario = g.auth_sessao.usuario
        return jsonify({"usuario": usuario.to_dict(), "destino": destino(usuario),
            "csrf_token": token_assinado(current_app.config["AUTH_KEY_BYTES"], request.cookies[COOKIE])})

    @staticmethod
    def logout():
        def operacao():
            LogoutService.executar(g.auth_sessao)
            resposta = current_app.response_class(status=204)
            return cookie_sessao(resposta)
        return AutenticacaoController._responder(operacao)

    @staticmethod
    def reautenticar():
        def operacao():
            ReautenticarService.executar(request.get_json(silent=True), g.auth_sessao,
                                        current_app.config["AUTH_KEY_BYTES"])
            return jsonify({"csrf_token": token_assinado(
                current_app.config["AUTH_KEY_BYTES"], request.cookies[COOKIE])})
        return AutenticacaoController._responder(operacao)

    @staticmethod
    def _responder(operacao):
        return responder_http(operacao, contexto="Falha interna de autenticacao.",
            adaptar_sucesso=lambda resposta: resposta, tipo_erro=AutenticacaoError,
            adaptar_erro=resposta_erro, adaptar_falha=lambda: resposta_erro(
                AutenticacaoError("Não foi possível concluir a operação.", 500, "erro_interno")))
