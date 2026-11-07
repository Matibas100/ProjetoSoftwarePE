from flask import g, request
from app.http_response import responder_http, resposta_json
from app.http_composition import servicos


class DesempenhoController:
    @staticmethod
    def _responder(operacao):
        return responder_http(operacao, contexto="Falha interna: desempenho.",
            adaptar_sucesso=resposta_json)

    @staticmethod
    def diagnostico():
        return DesempenhoController._responder(lambda: servicos().desempenho.executar(g.auth_sessao.usuario_id, request.args))

    @staticmethod
    def aluno():
        return DesempenhoController._responder(lambda: servicos().dashboard_aluno.executar(g.auth_sessao.usuario_id, request.args))

    @staticmethod
    def admin():
        return DesempenhoController._responder(lambda: servicos().dashboard_admin.executar(request.args))
