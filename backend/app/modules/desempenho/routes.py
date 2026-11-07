"""Rotas do proprietário, sem regra de negócio."""
from flask import Blueprint

from app.modules.desempenho.controllers.desempenho_controller import DesempenhoController

blueprint = Blueprint("desempenho", __name__)

for caminho, nome in (("/aluno/desempenho", "diagnostico"), ("/aluno/dashboard", "aluno"), ("/admin/dashboard", "admin")):
    blueprint.add_url_rule(caminho, endpoint=f"desempenho_{nome}", view_func=getattr(DesempenhoController, nome), methods=["GET"])
