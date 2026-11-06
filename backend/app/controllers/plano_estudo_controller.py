from flask import g, jsonify, request
from app.http_response import responder_http, resposta_json, resposta_json_dinamica
from app.services.consultar_plano_service import ConsultarPlanoService
from app.http_composition import servicos
from app.services.concluir_plano_item_service import ConcluirPlanoItemService


class PlanoEstudoController:
    @staticmethod
    def _responder(operacao):
        return responder_http(operacao, contexto="Falha interna: plano_estudo.",
            adaptar_sucesso=resposta_json_dinamica)

    @staticmethod
    def consultar():
        return PlanoEstudoController._responder(lambda: ConsultarPlanoService.executar(g.auth_sessao.usuario_id, request.args))

    @staticmethod
    def gerar():
        return PlanoEstudoController._responder(lambda: servicos().gerar_plano.executar(g.auth_sessao.usuario_id, request.get_json(silent=True)))

    @staticmethod
    def recalcular():
        return PlanoEstudoController._responder(lambda: servicos().recalcular_plano.executar(g.auth_sessao.usuario_id, request.get_json(silent=True)))

    @staticmethod
    def concluir(item_id):
        return PlanoEstudoController._responder(lambda: ConcluirPlanoItemService.executar(g.auth_sessao.usuario_id, item_id, request.get_json(silent=True)))
