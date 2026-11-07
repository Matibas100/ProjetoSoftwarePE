"""Agregação dos seis Blueprints e health de infraestrutura."""
from flask import Blueprint
from app.core.controllers.health_controller import HealthController
from app.modules.conteudo.routes import blueprint as conteudo_blueprint
from app.modules.praticas.routes import blueprint as praticas_blueprint
from app.modules.simulados.routes import blueprint as simulados_blueprint
from app.modules.desempenho.routes import blueprint as desempenho_blueprint
from app.modules.contas.routes import blueprint as contas_blueprint
from app.modules.plano_estudos.routes import blueprint as plano_estudos_blueprint


api_blueprint = Blueprint("api", __name__)

api_blueprint.add_url_rule(
    "/health",
    endpoint="health",
    view_func=HealthController.status,
    methods=["GET"],
)

api_blueprint.register_blueprint(conteudo_blueprint)

api_blueprint.register_blueprint(praticas_blueprint)

api_blueprint.register_blueprint(simulados_blueprint)

api_blueprint.register_blueprint(desempenho_blueprint)

api_blueprint.register_blueprint(contas_blueprint)

api_blueprint.register_blueprint(plano_estudos_blueprint)
