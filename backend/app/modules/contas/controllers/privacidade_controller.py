from flask import g, request
from app.http_composition import servicos
from app.http_response import responder_http, resposta_json_dinamica
from app.modules.contas.services.consultar_termos_service import ConsultarTermosService
from app.modules.contas.services.consultar_privacidade_service import ConsultarPrivacidadeService
from app.modules.contas.services.aceitar_termos_uso_service import AceitarTermosUsoService
from app.modules.contas.services.consentir_plano_service import ConsentirPlanoService


class PrivacidadeController:
    @staticmethod
    def _responder(operacao):
        return responder_http(
            operacao,
            contexto="Falha interna: privacidade.",
            adaptar_sucesso=resposta_json_dinamica
        )

    @staticmethod
    def termos():
        return PrivacidadeController._responder(ConsultarTermosService.executar)

    @staticmethod
    def consultar():
        return PrivacidadeController._responder(lambda: ConsultarPrivacidadeService.executar(g.auth_sessao.usuario_id))

    @staticmethod
    def aceitar_uso():
        return PrivacidadeController._responder(lambda: AceitarTermosUsoService.executar(
            g.auth_sessao.usuario_id,
            request.get_json(silent=True)
        ))

    @staticmethod
    def consentir():
        return PrivacidadeController._responder(lambda: ConsentirPlanoService.executar(
            g.auth_sessao.usuario_id,
            request.get_json(silent=True)
        ))

    @staticmethod
    def recusar():
        return PrivacidadeController._responder(lambda: servicos().recusar_consentimento_plano.executar(
            g.auth_sessao.usuario_id,
            request.get_json(silent=True)
        ))

    @staticmethod
    def revogar():
        return PrivacidadeController._responder(lambda: servicos().revogar_consentimento_plano.executar(
            g.auth_sessao.usuario_id,
            request.get_json(silent=True)
        ))
