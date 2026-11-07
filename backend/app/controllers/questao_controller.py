from flask import g, jsonify, request

from app.http_response import responder_http, resposta_json
from app.http_composition import servicos
from app.services.criar_questao_service import CriarQuestaoService
from app.services.gestao_questao_service import (
    ListarQuestoesAdminService, ConsultarQuestaoService, EditarQuestaoService,
    PublicarQuestaoService, ArquivarQuestaoService,
)


class QuestaoController:
    """Recebe HTTP e delega os casos de uso do recurso Questao."""

    @staticmethod
    def cadastrar():
        dados = request.get_json(silent=True)
        return QuestaoController._responder(
            lambda: CriarQuestaoService.executar(dados, g.auth_sessao.usuario_id),
            status_sucesso=201,
        )

    @staticmethod
    def buscar_por_assunto():
        assunto_id = request.args.get("assunto_id")
        return QuestaoController._responder(
            lambda: servicos().questoes_por_assunto.executar(assunto_id)
        )

    @staticmethod
    def listar_admin():
        return QuestaoController._responder(lambda: ListarQuestoesAdminService.executar(request.args))

    @staticmethod
    def detalhe(questao_id):
        return QuestaoController._responder(lambda: ConsultarQuestaoService.executar(questao_id))

    @staticmethod
    def editar(questao_id):
        return QuestaoController._responder(lambda: EditarQuestaoService.executar(
            questao_id, request.get_json(silent=True), g.auth_sessao.usuario_id))

    @staticmethod
    def publicar(questao_id):
        return QuestaoController._responder(lambda: PublicarQuestaoService.executar(
            questao_id, request.get_json(silent=True), g.auth_sessao.usuario_id))

    @staticmethod
    def arquivar(questao_id):
        return QuestaoController._responder(lambda: ArquivarQuestaoService.executar(
            questao_id, request.get_json(silent=True), g.auth_sessao.usuario_id))

    @staticmethod
    def _responder(operacao, status_sucesso=200):
        return responder_http(operacao, contexto="Falha interna: questao.",
            adaptar_sucesso=lambda dados: resposta_json(dados, status_sucesso),
            adaptar_erro=lambda erro: (jsonify({"erro": str(erro)}), erro.status_code))
