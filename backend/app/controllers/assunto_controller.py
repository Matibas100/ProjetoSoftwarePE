from flask import current_app, jsonify, request

from app.exceptions import ErroAplicacao
from app.services.atualizar_assunto_service import AtualizarAssuntoService
from app.services.criar_assunto_service import CriarAssuntoService
from app.services.deletar_assunto_service import DeletarAssuntoService
from app.services.listar_assuntos_service import ListarAssuntosService


class AssuntoController:
    """Recebe HTTP e delega os casos de uso do recurso Assunto."""

    @staticmethod
    def cadastrar():
        dados = request.get_json(silent=True)
        return AssuntoController._responder(
            lambda: CriarAssuntoService.executar(dados),
            status_sucesso=201,
        )

    @staticmethod
    def listar():
        return AssuntoController._responder(ListarAssuntosService.executar)

    @staticmethod
    def atualizar(assunto_id):
        dados = request.get_json(silent=True)
        return AssuntoController._responder(
            lambda: AtualizarAssuntoService.executar(assunto_id, dados)
        )

    @staticmethod
    def deletar(assunto_id):
        return AssuntoController._responder(
            lambda: DeletarAssuntoService.executar(assunto_id),
            status_sucesso=204,
        )

    @staticmethod
    def _responder(operacao, status_sucesso=200):
        try:
            resultado = operacao()
            if status_sucesso == 204:
                return "", 204
            return jsonify(resultado), status_sucesso
        except ErroAplicacao as erro:
            return jsonify({"erro": str(erro)}), erro.status_code
        except Exception:
            current_app.logger.exception("Erro inesperado ao processar assunto")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500
