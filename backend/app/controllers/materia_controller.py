from flask import current_app, jsonify, request

from app.exceptions import ErroAplicacao
from app.services.atualizar_materia_service import AtualizarMateriaService
from app.services.criar_materia_service import CriarMateriaService
from app.services.deletar_materia_service import DeletarMateriaService
from app.services.listar_materias_service import ListarMateriasService


class MateriaController:
    """Recebe HTTP e delega os casos de uso do recurso Materia."""

    @staticmethod
    def cadastrar():
        dados = request.get_json(silent=True)
        return MateriaController._responder(
            lambda: CriarMateriaService.executar(dados),
            status_sucesso=201,
        )

    @staticmethod
    def listar():
        return MateriaController._responder(ListarMateriasService.executar)

    @staticmethod
    def atualizar(materia_id):
        dados = request.get_json(silent=True)
        return MateriaController._responder(
            lambda: AtualizarMateriaService.executar(materia_id, dados)
        )

    @staticmethod
    def deletar(materia_id):
        return MateriaController._responder(
            lambda: DeletarMateriaService.executar(materia_id),
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
            current_app.logger.exception("Erro inesperado ao processar materia")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500
