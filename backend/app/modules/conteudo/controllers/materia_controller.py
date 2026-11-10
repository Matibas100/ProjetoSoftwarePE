from flask import request

from app.http_response import responder_http, resposta_json
from app.modules.conteudo.services.buscar_materia_por_id_service import BuscarMateriaPorIdService
from app.modules.conteudo.services.atualizar_materia_service import AtualizarMateriaService
from app.modules.conteudo.services.criar_materia_service import CriarMateriaService
from app.modules.conteudo.services.deletar_materia_service import DeletarMateriaService
from app.modules.conteudo.services.listar_materias_service import ListarMateriasService
from app.modules.conteudo.services.alterar_status_catalogo_service import AlterarStatusMateriaService
from app.modules.conteudo.services.impacto_catalogo_service import ImpactoMateriaService
from app.http_composition import servicos


class MateriaController:
    """Recebe HTTP e delega os casos de uso do recurso Materia."""

    @staticmethod
    def buscar_por_id(materia_id):
        return MateriaController._responder(
            lambda: BuscarMateriaPorIdService.executar(materia_id)
        )

    @staticmethod
    def cadastrar():
        dados = request.get_json(silent=True)
        return MateriaController._responder(
            lambda: CriarMateriaService.executar(dados),
            status_sucesso=201,
        )

    @staticmethod
    def listar():
        incluir_inativos = request.args.get("status") == "todos"
        return MateriaController._responder(
            lambda: ListarMateriasService.executar(incluir_inativos)
        )

    @staticmethod
    def listar_admin():
        parametros = request.args.to_dict()
        return MateriaController._responder(
            lambda: servicos().materias_admin.executar(parametros)
        )

    @staticmethod
    def impacto(materia_id):
        return MateriaController._responder(
            lambda: ImpactoMateriaService.executar(materia_id)
        )

    @staticmethod
    def alterar_status(materia_id, acao):
        return MateriaController._responder(
            lambda: AlterarStatusMateriaService.executar(materia_id, acao)
        )

    @staticmethod
    def atualizar(materia_id):
        dados = request.get_json(silent=True)
        return MateriaController._responder(
            lambda: AtualizarMateriaService.executar(materia_id, dados)
        )

    @staticmethod
    def deletar(materia_id):
        return MateriaController._responder(
            lambda: DeletarMateriaService.executar(materia_id),
            status_sucesso=204,
        )

    @staticmethod
    def _responder(operacao, status_sucesso=200):
        return responder_http(
            operacao,
            contexto="Falha interna: materia.",
            adaptar_sucesso=lambda dados: resposta_json(dados, status_sucesso)
        )
