from flask import Blueprint

from app.controllers.assunto_controller import AssuntoController
from app.controllers.health_controller import HealthController
from app.controllers.materia_controller import MateriaController
from app.controllers.questao_controller import QuestaoController


api_blueprint = Blueprint("api", __name__)

api_blueprint.add_url_rule(
    "/health",
    endpoint="health",
    view_func=HealthController.status,
    methods=["GET"],
)

api_blueprint.add_url_rule(
    "/materias",
    endpoint="cadastrar_materia",
    view_func=MateriaController.cadastrar,
    methods=["POST"],
)

api_blueprint.add_url_rule(
    "/materias",
    endpoint="listar_materias",
    view_func=MateriaController.listar,
    methods=["GET"],
)

api_blueprint.add_url_rule(
    "/materias/<int:materia_id>",
    endpoint="atualizar_materia",
    view_func=MateriaController.atualizar,
    methods=["PUT"],
)

api_blueprint.add_url_rule(
    "/materias/<int:materia_id>",
    endpoint="deletar_materia",
    view_func=MateriaController.deletar,
    methods=["DELETE"],
)

api_blueprint.add_url_rule(
    "/questoes",
    endpoint="cadastrar_questao",
    view_func=QuestaoController.cadastrar,
    methods=["POST"],
)

api_blueprint.add_url_rule(
    "/questoes/por-assunto",
    endpoint="buscar_questoes_por_assunto",
    view_func=QuestaoController.buscar_por_assunto,
    methods=["GET"],
)

api_blueprint.add_url_rule(
    "/assuntos",
    endpoint="cadastrar_assunto",
    view_func=AssuntoController.cadastrar,
    methods=["POST"],
)

api_blueprint.add_url_rule(
    "/assuntos",
    endpoint="listar_assuntos",
    view_func=AssuntoController.listar,
    methods=["GET"],
)

api_blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>",
    endpoint="atualizar_assunto",
    view_func=AssuntoController.atualizar,
    methods=["PUT"],
)

api_blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>",
    endpoint="deletar_assunto",
    view_func=AssuntoController.deletar,
    methods=["DELETE"],
)
