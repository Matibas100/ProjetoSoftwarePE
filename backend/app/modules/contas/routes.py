"""Rotas do proprietário, sem regra de negócio."""
from flask import Blueprint

from app.modules.contas.controllers.autenticacao_controller import AutenticacaoController
from app.modules.contas.controllers.privacidade_controller import PrivacidadeController
from app.modules.contas.controllers.usuario_controller import UsuarioController

blueprint = Blueprint("contas", __name__)

blueprint.add_url_rule('/admin/usuarios',view_func=UsuarioController.listar,methods=['GET'])
blueprint.add_url_rule('/admin/usuarios',view_func=UsuarioController.criar,methods=['POST'])
blueprint.add_url_rule('/admin/usuarios/<int:usuario_id>',view_func=UsuarioController.buscar,methods=['GET'])
blueprint.add_url_rule('/admin/usuarios/<int:usuario_id>',view_func=UsuarioController.atualizar,methods=['PUT'])
blueprint.add_url_rule('/admin/usuarios/<int:usuario_id>',view_func=UsuarioController.excluir,methods=['DELETE'])
blueprint.add_url_rule('/admin/usuarios/<int:usuario_id>/desativar',view_func=UsuarioController.desativar,methods=['POST'])
blueprint.add_url_rule('/admin/usuarios/<int:usuario_id>/reativar',view_func=UsuarioController.reativar,methods=['POST'])

for nome, metodo in (("csrf", "GET"), ("cadastro", "POST"), ("login", "POST"),
                     ("sessao", "GET"), ("logout", "POST"), ("reautenticar", "POST")):
    blueprint.add_url_rule(f"/auth/{nome}", endpoint=f"auth_{nome}",
        view_func=getattr(AutenticacaoController, nome), methods=[metodo])

blueprint.add_url_rule("/termos", view_func=PrivacidadeController.termos, methods=["GET"])

blueprint.add_url_rule("/aluno/privacidade", view_func=PrivacidadeController.consultar, methods=["GET"])

blueprint.add_url_rule("/aluno/privacidade/termos-uso", view_func=PrivacidadeController.aceitar_uso, methods=["POST"])

blueprint.add_url_rule("/aluno/privacidade/consentimento-plano/aceitar", view_func=PrivacidadeController.consentir, methods=["POST"])

blueprint.add_url_rule("/aluno/privacidade/consentimento-plano/recusar", view_func=PrivacidadeController.recusar, methods=["POST"])

blueprint.add_url_rule("/aluno/privacidade/consentimento-plano/revogar", view_func=PrivacidadeController.revogar, methods=["POST"])
