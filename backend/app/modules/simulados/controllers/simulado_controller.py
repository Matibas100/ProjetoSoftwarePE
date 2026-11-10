from flask import g, request
from app.http_response import responder_http, resposta_json_dinamica
from app.modules.simulados.services.gestao_simulado_service import (
    ListarSimuladosAdminService,
    ConsultarSimuladoAdminService,
    CriarSimuladoService,
    EditarSimuladoService,
    PublicarSimuladoService,
    ArquivarSimuladoService
)
from app.modules.simulados.services.consultar_simulado_service import ConsultarTentativaSimuladoService
from app.http_composition import servicos
from app.modules.simulados.services.iniciar_simulado_service import IniciarSimuladoService
from app.modules.simulados.services.responder_simulado_service import ResponderSimuladoService
from app.modules.simulados.services.finalizar_simulado_service import FinalizarSimuladoService


class SimuladoController:
    @staticmethod
    def _responder(operacao):
        return responder_http(
            operacao,
            contexto="Falha interna: simulado.",
            adaptar_sucesso=resposta_json_dinamica
        )

    @staticmethod
    def admin_lista():
        return SimuladoController._responder(lambda: ListarSimuladosAdminService.executar(request.args))

    @staticmethod
    def criar():
        return SimuladoController._responder(lambda: CriarSimuladoService.executar(
            request.get_json(silent=True),
            g.auth_sessao.usuario_id
        ))

    @staticmethod
    def admin_detalhe(simulado_id):
        return SimuladoController._responder(lambda: ConsultarSimuladoAdminService.executar(simulado_id))

    @staticmethod
    def editar(simulado_id):
        return SimuladoController._responder(lambda: EditarSimuladoService.executar(
            simulado_id,
            request.get_json(silent=True),
            g.auth_sessao.usuario_id
        ))

    @staticmethod
    def publicar(simulado_id):
        return SimuladoController._responder(lambda: PublicarSimuladoService.executar(
            simulado_id,
            request.get_json(silent=True),
            g.auth_sessao.usuario_id
        ))

    @staticmethod
    def arquivar(simulado_id):
        return SimuladoController._responder(lambda: ArquivarSimuladoService.executar(
            simulado_id,
            request.get_json(silent=True),
            g.auth_sessao.usuario_id
        ))

    @staticmethod
    def catalogo():
        return SimuladoController._responder(lambda: servicos().simulados_aluno.executar(
            g.auth_sessao.usuario_id,
            request.args
        ))

    @staticmethod
    def iniciar():
        return SimuladoController._responder(lambda: IniciarSimuladoService.executar(
            g.auth_sessao.usuario_id,
            request.get_json(silent=True)
        ))

    @staticmethod
    def historico():
        return SimuladoController._responder(lambda: servicos().historico_simulados.executar(
            g.auth_sessao.usuario_id,
            request.args
        ))

    @staticmethod
    def tentativa(tentativa_id, modo=None):
        return SimuladoController._responder(lambda: ConsultarTentativaSimuladoService.executar(
            g.auth_sessao.usuario_id,
            tentativa_id,
            modo
        ))

    @staticmethod
    def responder(tentativa_id, item_id):
        return SimuladoController._responder(lambda: ResponderSimuladoService.executar(
            g.auth_sessao.usuario_id,
            tentativa_id,
            item_id,
            request.get_json(silent=True)
        ))

    @staticmethod
    def finalizar(tentativa_id):
        return SimuladoController._responder(lambda: FinalizarSimuladoService.executar(
            g.auth_sessao.usuario_id,
            tentativa_id,
            request.get_json(silent=True)
        ))
