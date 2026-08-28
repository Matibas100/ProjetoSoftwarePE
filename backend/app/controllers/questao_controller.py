from flask import current_app, jsonify, request

from app.exceptions import ErroAplicacao
from app.services.buscar_questoes_por_assunto_service import (
    BuscarQuestoesPorAssuntoService,
)
from app.services.criar_questao_service import CriarQuestaoService


class QuestaoController:
    """Recebe HTTP e delega os casos de uso do recurso Questao."""

    @staticmethod
    def cadastrar():
        dados = request.get_json(silent=True)
        return QuestaoController._responder(
            lambda: CriarQuestaoService.executar(dados),
            status_sucesso=201,
        )

    @staticmethod
    def buscar_por_assunto():
        assunto_id = request.args.get("assunto_id")
        return QuestaoController._responder(
            lambda: BuscarQuestoesPorAssuntoService.executar(assunto_id)
        )

    @staticmethod
    def _responder(operacao, status_sucesso=200):
        try:
            return jsonify(operacao()), status_sucesso
        except ErroAplicacao as erro:
            return jsonify({"erro": str(erro)}), erro.status_code
        except Exception:
            current_app.logger.exception("Erro inesperado ao processar questao")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500
