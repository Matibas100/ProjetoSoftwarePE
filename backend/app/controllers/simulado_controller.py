from flask import current_app, g, jsonify, request
from app.exceptions import ErroAplicacao
from app.services.gestao_simulado_service import (ListarSimuladosAdminService, ConsultarSimuladoAdminService,
    CriarSimuladoService, EditarSimuladoService, PublicarSimuladoService, ArquivarSimuladoService)
from app.services.consultar_simulado_service import (ListarSimuladosAlunoService,
    ListarHistoricoSimuladosService, ConsultarTentativaSimuladoService)
from app.services.iniciar_simulado_service import IniciarSimuladoService
from app.services.responder_simulado_service import ResponderSimuladoService
from app.services.finalizar_simulado_service import FinalizarSimuladoService


class SimuladoController:
    @staticmethod
    def _responder(operacao):
        try:
            dados = operacao()
            payload, status = dados if isinstance(dados, tuple) else (dados, 200)
            return jsonify(payload), status
        except ErroAplicacao as erro:
            return jsonify(erro.to_dict()), erro.status_code
        except Exception:
            current_app.logger.error("Falha interna ao processar simulado.")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500

    @staticmethod
    def admin_lista():
        return SimuladoController._responder(lambda: ListarSimuladosAdminService.executar(request.args))

    @staticmethod
    def criar():
        return SimuladoController._responder(lambda: CriarSimuladoService.executar(request.get_json(silent=True), g.auth_sessao.usuario_id))

    @staticmethod
    def admin_detalhe(simulado_id):
        return SimuladoController._responder(lambda: ConsultarSimuladoAdminService.executar(simulado_id))

    @staticmethod
    def editar(simulado_id):
        return SimuladoController._responder(lambda: EditarSimuladoService.executar(simulado_id, request.get_json(silent=True), g.auth_sessao.usuario_id))

    @staticmethod
    def publicar(simulado_id):
        return SimuladoController._responder(lambda: PublicarSimuladoService.executar(simulado_id, request.get_json(silent=True), g.auth_sessao.usuario_id))

    @staticmethod
    def arquivar(simulado_id):
        return SimuladoController._responder(lambda: ArquivarSimuladoService.executar(simulado_id, request.get_json(silent=True), g.auth_sessao.usuario_id))

    @staticmethod
    def catalogo():
        return SimuladoController._responder(lambda: ListarSimuladosAlunoService.executar(g.auth_sessao.usuario_id, request.args))

    @staticmethod
    def iniciar():
        return SimuladoController._responder(lambda: IniciarSimuladoService.executar(g.auth_sessao.usuario_id, request.get_json(silent=True)))

    @staticmethod
    def historico():
        return SimuladoController._responder(lambda: ListarHistoricoSimuladosService.executar(g.auth_sessao.usuario_id, request.args))

    @staticmethod
    def tentativa(tentativa_id, modo=None):
        return SimuladoController._responder(lambda: ConsultarTentativaSimuladoService.executar(g.auth_sessao.usuario_id, tentativa_id, modo))

    @staticmethod
    def responder(tentativa_id, item_id):
        return SimuladoController._responder(lambda: ResponderSimuladoService.executar(g.auth_sessao.usuario_id, tentativa_id, item_id, request.get_json(silent=True)))

    @staticmethod
    def finalizar(tentativa_id):
        return SimuladoController._responder(lambda: FinalizarSimuladoService.executar(g.auth_sessao.usuario_id, tentativa_id, request.get_json(silent=True)))
