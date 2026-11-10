from flask import g, request
from app.http_response import responder_http, resposta_json_dinamica
from app.http_composition import servicos
from app.modules.praticas.services.iniciar_pratica_service import IniciarPraticaService
from app.modules.praticas.services.consultar_pratica_service import ConsultarPraticaService
from app.modules.praticas.services.responder_pratica_service import ResponderPraticaService
from app.modules.praticas.services.listar_praticas_service import ListarPraticasService


class PraticaController:
    @staticmethod
    def _responder(operacao):
        return responder_http(
            operacao,
            contexto="Falha interna: pratica.",
            adaptar_sucesso=resposta_json_dinamica
        )

    @staticmethod
    def questoes():
        return PraticaController._responder(lambda: servicos().questoes_aluno.executar(request.args))

    @staticmethod
    def iniciar():
        return PraticaController._responder(lambda: IniciarPraticaService.executar(
            g.auth_sessao.usuario_id,
            request.get_json(silent=True)
        ))

    @staticmethod
    def historico():
        return PraticaController._responder(lambda: ListarPraticasService.executar(
            g.auth_sessao.usuario_id,
            request.args
        ))

    @staticmethod
    def detalhe(tentativa_id):
        return PraticaController._responder(lambda: ConsultarPraticaService.executar(
            g.auth_sessao.usuario_id,
            tentativa_id
        ))

    @staticmethod
    def responder(tentativa_id):
        return PraticaController._responder(lambda: ResponderPraticaService.executar(
            g.auth_sessao.usuario_id,
            tentativa_id,
            request.get_json(silent=True)
        ))
