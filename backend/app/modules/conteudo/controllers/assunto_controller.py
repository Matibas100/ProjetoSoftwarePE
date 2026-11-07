from flask import request

from app.http_response import responder_http, resposta_json
from app.modules.conteudo.services.atualizar_assunto_service import AtualizarAssuntoService
from app.modules.conteudo.services.criar_assunto_service import CriarAssuntoService
from app.modules.conteudo.services.deletar_assunto_service import DeletarAssuntoService
from app.modules.conteudo.services.listar_assuntos_service import ListarAssuntosService
from app.modules.conteudo.services.alterar_status_catalogo_service import AlterarStatusAssuntoService
from app.modules.conteudo.services.impacto_catalogo_service import ImpactoAssuntoService
from app.http_composition import servicos
from app.modules.conteudo.services.transferir_assunto_service import TransferirAssuntoService


class AssuntoController:
    """Recebe HTTP e delega os casos de uso do recurso Assunto."""

    @staticmethod
    def cadastrar():
        dados = request.get_json(silent=True)
        return AssuntoController._responder(
            lambda: CriarAssuntoService.executar(dados),
            status_sucesso=201,
        )

    @staticmethod
    def listar():
        incluir_inativos = request.args.get("status") == "todos"
        materia_id = request.args.get("materia_id", type=int)
        return AssuntoController._responder(
            lambda: ListarAssuntosService.executar(incluir_inativos, materia_id)
        )

    @staticmethod
    def listar_admin():
        parametros = request.args.to_dict()
        return AssuntoController._responder(
            lambda: servicos().assuntos_admin.executar(parametros)
        )

    @staticmethod
    def impacto(assunto_id):
        return AssuntoController._responder(
            lambda: ImpactoAssuntoService.executar(assunto_id)
        )

    @staticmethod
    def previa_transferencia(assunto_id):
        destino_id = request.args.get("materia_destino_id", type=int)
        return AssuntoController._responder(
            lambda: TransferirAssuntoService.previa(assunto_id, destino_id)
        )

    @staticmethod
    def transferir(assunto_id):
        dados = request.get_json(silent=True)
        return AssuntoController._responder(
            lambda: TransferirAssuntoService.executar(assunto_id, dados)
        )

    @staticmethod
    def alterar_status(assunto_id, acao):
        return AssuntoController._responder(
            lambda: AlterarStatusAssuntoService.executar(assunto_id, acao)
        )

    @staticmethod
    def atualizar(assunto_id):
        dados = request.get_json(silent=True)
        return AssuntoController._responder(
            lambda: AtualizarAssuntoService.executar(assunto_id, dados)
        )

    @staticmethod
    def deletar(assunto_id):
        return AssuntoController._responder(
            lambda: DeletarAssuntoService.executar(assunto_id),
            status_sucesso=204,
        )

    @staticmethod
    def _responder(operacao, status_sucesso=200):
        return responder_http(operacao, contexto="Falha interna: assunto.",
            adaptar_sucesso=lambda dados: resposta_json(dados, status_sucesso))
