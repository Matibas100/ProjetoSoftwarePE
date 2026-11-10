"""Rotas do proprietário, sem regra de negócio."""
from flask import Blueprint

from app.modules.simulados.controllers.simulado_controller import SimuladoController

blueprint = Blueprint("simulados", __name__)

for caminho, nome, metodo in (
    ("/admin/simulados", "admin_lista", "GET"),
    (
        "/admin/simulados",
        "criar",
        "POST"
    ),
    (
        "/admin/simulados/<int:simulado_id>",
        "admin_detalhe",
        "GET"
    ),
    ("/admin/simulados/<int:simulado_id>", "editar", "PUT"),
    ("/admin/simulados/<int:simulado_id>/publicar", "publicar", "POST"),
    ("/admin/simulados/<int:simulado_id>/arquivar", "arquivar", "POST"),
    ("/aluno/simulados", "catalogo", "GET"),
    ("/aluno/tentativas-simulado", "iniciar", "POST"),
    ("/aluno/tentativas-simulado", "historico", "GET"),
    ("/aluno/tentativas-simulado/<int:tentativa_id>", "tentativa", "GET"),
    ("/aluno/tentativas-simulado/<int:tentativa_id>/respostas/<int:item_id>", "responder", "PUT"),
    ("/aluno/tentativas-simulado/<int:tentativa_id>/finalizar", "finalizar", "POST")
):
    blueprint.add_url_rule(
        caminho,
        endpoint=f"simulado_{nome}",
        view_func=getattr(
            SimuladoController,
            nome
        ),
        methods=[metodo]
    )

for modo in ("resultado", "correcao"):
    blueprint.add_url_rule(
        f"/aluno/tentativas-simulado/<int:tentativa_id>/{modo}",
        endpoint=f"simulado_{modo}",
        view_func=SimuladoController.tentativa,
        defaults={"modo": modo},
        methods=["GET"]
    )
