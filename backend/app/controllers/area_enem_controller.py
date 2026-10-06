from flask import current_app, jsonify

from app.exceptions import ErroAplicacao
from app.services.listar_areas_enem_service import ListarAreasEnemService


class AreaEnemController:
    @staticmethod
    def listar():
        try:
            return jsonify(ListarAreasEnemService.executar()), 200
        except ErroAplicacao as erro:
            return jsonify(erro.to_dict()), erro.status_code
        except Exception:
            current_app.logger.exception("Erro inesperado ao listar Areas do ENEM")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500
