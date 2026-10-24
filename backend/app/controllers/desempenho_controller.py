from flask import current_app, g, jsonify, request
from app.exceptions import ErroAplicacao
from app.services.consultar_desempenho_service import ConsultarDesempenhoService
from app.services.dashboard_service import ConsultarDashboardAlunoService, ConsultarDashboardAdminService


class DesempenhoController:
    @staticmethod
    def _responder(operacao):
        try:
            return jsonify(operacao()), 200
        except ErroAplicacao as erro:
            return jsonify(erro.to_dict()), erro.status_code
        except Exception:
            current_app.logger.error("Falha interna ao consultar desempenho/dashboard.")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500

    @staticmethod
    def diagnostico():
        return DesempenhoController._responder(lambda: ConsultarDesempenhoService.executar(g.auth_sessao.usuario_id, request.args))

    @staticmethod
    def aluno():
        return DesempenhoController._responder(lambda: ConsultarDashboardAlunoService.executar(g.auth_sessao.usuario_id, request.args))

    @staticmethod
    def admin():
        return DesempenhoController._responder(lambda: ConsultarDashboardAdminService.executar(request.args))
