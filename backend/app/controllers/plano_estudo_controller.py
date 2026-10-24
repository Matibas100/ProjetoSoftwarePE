from flask import current_app, g, jsonify, request
from app.exceptions import ErroAplicacao
from app.services.consultar_plano_service import ConsultarPlanoService
from app.services.gerar_plano_service import GerarPlanoService
from app.services.recalcular_plano_service import RecalcularPlanoService
from app.services.concluir_plano_item_service import ConcluirPlanoItemService


class PlanoEstudoController:
    @staticmethod
    def _responder(operacao):
        try:
            dados = operacao()
            payload, status = dados if isinstance(dados, tuple) else (dados, 200)
            return jsonify(payload), status
        except ErroAplicacao as erro:
            return jsonify(erro.to_dict()), erro.status_code
        except Exception:
            current_app.logger.error("Falha interna ao processar plano de estudos.")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500

    @staticmethod
    def consultar():
        return PlanoEstudoController._responder(lambda: ConsultarPlanoService.executar(g.auth_sessao.usuario_id, request.args))

    @staticmethod
    def gerar():
        return PlanoEstudoController._responder(lambda: GerarPlanoService.executar(g.auth_sessao.usuario_id, request.get_json(silent=True)))

    @staticmethod
    def recalcular():
        return PlanoEstudoController._responder(lambda: RecalcularPlanoService.executar(g.auth_sessao.usuario_id, request.get_json(silent=True)))

    @staticmethod
    def concluir(item_id):
        return PlanoEstudoController._responder(lambda: ConcluirPlanoItemService.executar(g.auth_sessao.usuario_id, item_id, request.get_json(silent=True)))
