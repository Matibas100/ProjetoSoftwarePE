"""Rotas do proprietário, sem regra de negócio."""
from flask import Blueprint

from app.modules.praticas.controllers.pratica_controller import PraticaController

blueprint = Blueprint("praticas", __name__)

for caminho, nome, metodo in (
    ("/aluno/questoes", "questoes", "GET"),
    ("/aluno/praticas", "iniciar", "POST"),
    ("/aluno/praticas", "historico", "GET"),
    ("/aluno/praticas/<int:tentativa_id>", "detalhe", "GET"),
    ("/aluno/praticas/<int:tentativa_id>/resposta", "responder", "POST")
):
    blueprint.add_url_rule(
        caminho,
        endpoint=f"pratica_{nome}",
        view_func=getattr(PraticaController, nome),
        methods=[metodo]
    )
