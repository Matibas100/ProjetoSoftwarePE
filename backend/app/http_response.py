"""Adaptação HTTP compartilhada, sem regras de negócio ou dados da requisição."""
from flask import current_app, jsonify

from app.exceptions import ErroAplicacao


def resposta_json(dados, status=200):
    if status == 204:
        return "", 204
    return jsonify(dados), status


def resposta_json_dinamica(dados):
    payload, status = dados if isinstance(dados, tuple) else (dados, 200)
    return resposta_json(payload, status)


def erro_json(erro):
    return jsonify(erro.to_dict()), erro.status_code


def falha_json():
    return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500


def registrar_falha(contexto, erro):
    # Contexto é uma constante do adaptador; nunca incluir mensagem/traceback.
    current_app.logger.error("%s (%s)", contexto, type(erro).__name__)


def responder_http(operacao, *, contexto, adaptar_sucesso=resposta_json,
                   tipo_erro=ErroAplicacao, adaptar_erro=erro_json, adaptar_falha=falha_json):
    try:
        return adaptar_sucesso(operacao())
    except tipo_erro as erro:
        return adaptar_erro(erro)
    except Exception as erro:
        registrar_falha(contexto, erro)
        return adaptar_falha()
