from flask import current_app, jsonify, request

from app.exceptions import ErroAplicacao
from app.services.atualizar_assunto_service import AtualizarAssuntoService
from app.services.criar_assunto_service import CriarAssuntoService
from app.services.deletar_assunto_service import DeletarAssuntoService
from app.services.listar_assuntos_service import ListarAssuntosService
from app.services.alterar_status_catalogo_service import AlterarStatusAssuntoService
from app.services.impacto_catalogo_service import ImpactoAssuntoService
from app.services.listar_catalogo_admin_service import ListarAssuntosAdminService
from app.services.transferir_assunto_service import TransferirAssuntoService


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
        incluir_inativos = request.args.get("status") == "todos"
        materia_id = request.args.get("materia_id", type=int)
        return AssuntoController._responder(
            lambda: ListarAssuntosService.executar(incluir_inativos, materia_id)
        )

    @staticmethod
    def listar_admin():
        parametros = request.args.to_dict()
        return AssuntoController._responder(
            lambda: ListarAssuntosAdminService.executar(parametros)
        )

    @staticmethod
    def impacto(assunto_id):
        return AssuntoController._responder(
            lambda: ImpactoAssuntoService.executar(assunto_id)
        )

    @staticmethod
    def previa_transferencia(assunto_id):
        destino_id = request.args.get("materia_destino_id", type=int)
        return AssuntoController._responder(
            lambda: TransferirAssuntoService.previa(assunto_id, destino_id)
        )

    @staticmethod
    def transferir(assunto_id):
        dados = request.get_json(silent=True)
        return AssuntoController._responder(
            lambda: TransferirAssuntoService.executar(assunto_id, dados)
        )

    @staticmethod
    def alterar_status(assunto_id, acao):
        return AssuntoController._responder(
            lambda: AlterarStatusAssuntoService.executar(assunto_id, acao)
        )

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
            return jsonify(erro.to_dict()), erro.status_code
        except Exception:
            current_app.logger.exception("Erro inesperado ao processar assunto")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500
