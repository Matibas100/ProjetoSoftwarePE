"""Rotas do proprietário, sem regra de negócio."""
from flask import Blueprint

from app.modules.plano_estudos.controllers.plano_estudo_controller import PlanoEstudoController

blueprint = Blueprint("plano_estudos", __name__)

for caminho, nome, metodo in (
    ("/aluno/plano", "consultar", "GET"),
    ("/aluno/plano/gerar", "gerar", "POST"),
    ("/aluno/plano/recalcular", "recalcular", "POST"),
    ("/aluno/plano/itens/<int:item_id>/concluir", "concluir", "POST")
):
    blueprint.add_url_rule(
        caminho,
        endpoint=f"plano_{nome}",
        view_func=getattr(
            PlanoEstudoController,
            nome
        ),
        methods=[metodo]
    )
