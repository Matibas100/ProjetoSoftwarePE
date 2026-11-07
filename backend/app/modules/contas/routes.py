"""Rotas do proprietário, sem regra de negócio."""
from flask import Blueprint

from app.modules.contas.controllers.autenticacao_controller import AutenticacaoController
from app.modules.contas.controllers.privacidade_controller import PrivacidadeController

blueprint = Blueprint("contas", __name__)

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
