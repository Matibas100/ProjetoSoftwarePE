from flask import current_app, g, jsonify, request
from app.exceptions import ErroAplicacao
from app.services.listar_questoes_aluno_service import ListarQuestoesAlunoService
from app.services.iniciar_pratica_service import IniciarPraticaService
from app.services.consultar_pratica_service import ConsultarPraticaService
from app.services.responder_pratica_service import ResponderPraticaService
from app.services.listar_praticas_service import ListarPraticasService


class PraticaController:
    @staticmethod
    def _responder(operacao):
        try:
            dados = operacao()
            payload, status = dados if isinstance(dados, tuple) else (dados, 200)
            return jsonify(payload), status
        except ErroAplicacao as erro:
            return jsonify(erro.to_dict()), erro.status_code
        except Exception:
            current_app.logger.error("Falha interna ao processar prática.")
            return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500

    @staticmethod
    def questoes():
        return PraticaController._responder(lambda: ListarQuestoesAlunoService.executar(request.args))

    @staticmethod
    def iniciar():
        return PraticaController._responder(lambda: IniciarPraticaService.executar(
            g.auth_sessao.usuario_id, request.get_json(silent=True)))

    @staticmethod
    def historico():
        return PraticaController._responder(lambda: ListarPraticasService.executar(g.auth_sessao.usuario_id, request.args))

    @staticmethod
    def detalhe(tentativa_id):
        return PraticaController._responder(lambda: ConsultarPraticaService.executar(g.auth_sessao.usuario_id, tentativa_id))

    @staticmethod
    def responder(tentativa_id):
        return PraticaController._responder(lambda: ResponderPraticaService.executar(
            g.auth_sessao.usuario_id, tentativa_id, request.get_json(silent=True)))
