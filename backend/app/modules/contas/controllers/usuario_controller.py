"""Adaptação HTTP da gestão exclusiva de contas de Aluno."""
from flask import request
from werkzeug.exceptions import RequestEntityTooLarge
from app.http_composition import servicos
from app.http_response import responder_http, resposta_json
from app.modules.contas.controllers.autenticacao_controller import resposta_erro
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.modules.contas.services.criar_aluno_admin_service import CriarAlunoAdminService
from app.modules.contas.services.buscar_aluno_admin_service import BuscarAlunoAdminService
from app.modules.contas.services.atualizar_aluno_admin_service import AtualizarAlunoAdminService
from app.modules.contas.services.desativar_aluno_service import DesativarAlunoService
from app.modules.contas.services.reativar_aluno_service import ReativarAlunoService
from app.modules.contas.services.excluir_aluno_admin_service import ExcluirAlunoAdminService


def corpo():
    request.max_content_length = 16*1024
    try:
        return request.get_json(silent=True)
    except RequestEntityTooLarge:
        raise AutenticacaoError(
            'Corpo da requisição muito grande.',
            413,
            'corpo_muito_grande'
        ) from None


def responder(operacao, status=200):
    return responder_http(
        operacao,
        contexto='Falha na gestão de Alunos.',
        adaptar_sucesso=lambda dados: resposta_json(dados, status),
        tipo_erro=AutenticacaoError,
        adaptar_erro=resposta_erro,
        adaptar_falha=lambda: resposta_erro(AutenticacaoError(
            'Não foi possível concluir a operação.',
            500,
            'erro_interno'
        ))
    )


class UsuarioController:
    @staticmethod
    def listar():
        return responder(lambda: servicos().alunos_admin.executar(request.args))

    @staticmethod
    def criar():
        return responder(lambda: CriarAlunoAdminService.executar(corpo()), 201)

    @staticmethod
    def buscar(usuario_id):
        return responder(lambda: BuscarAlunoAdminService.executar(usuario_id))

    @staticmethod
    def atualizar(usuario_id):
        return responder(lambda: AtualizarAlunoAdminService.executar(usuario_id, corpo()))

    @staticmethod
    def desativar(usuario_id):
        return responder(lambda: DesativarAlunoService.executar(usuario_id, corpo()))

    @staticmethod
    def reativar(usuario_id):
        return responder(lambda: ReativarAlunoService.executar(usuario_id, corpo()))

    @staticmethod
    def excluir(usuario_id):
        return responder(lambda: ExcluirAlunoAdminService.executar(usuario_id, corpo()), 204)
