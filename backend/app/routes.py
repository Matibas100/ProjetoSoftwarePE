from flask import Blueprint

from app.controllers.assunto_controller import AssuntoController
from app.controllers.area_enem_controller import AreaEnemController
from app.controllers.health_controller import HealthController
from app.controllers.materia_controller import MateriaController
from app.controllers.questao_controller import QuestaoController
from app.controllers.autenticacao_controller import AutenticacaoController


api_blueprint = Blueprint("api", __name__)

for nome, metodo in (("csrf", "GET"), ("cadastro", "POST"), ("login", "POST"),
                     ("sessao", "GET"), ("logout", "POST"), ("reautenticar", "POST")):
    api_blueprint.add_url_rule(f"/auth/{nome}", endpoint=f"auth_{nome}",
        view_func=getattr(AutenticacaoController, nome), methods=[metodo])

api_blueprint.add_url_rule(
    "/areas-enem", endpoint="listar_areas_enem", view_func=AreaEnemController.listar,
    methods=["GET"],
)

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
    "/admin/materias", endpoint="listar_materias_admin",
    view_func=MateriaController.listar_admin, methods=["GET"],
)

api_blueprint.add_url_rule(
    "/materias/<int:materia_id>/impacto-exclusao", endpoint="impacto_materia",
    view_func=MateriaController.impacto, methods=["GET"],
)

for acao_materia in ("inativar", "arquivar", "reativar"):
    api_blueprint.add_url_rule(
        f"/materias/<int:materia_id>/{acao_materia}",
        endpoint=f"{acao_materia}_materia",
        view_func=MateriaController.alterar_status,
        defaults={"acao": acao_materia},
        methods=["POST"],
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
    "/admin/assuntos", endpoint="listar_assuntos_admin",
    view_func=AssuntoController.listar_admin, methods=["GET"],
)

api_blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>/impacto-exclusao", endpoint="impacto_assunto",
    view_func=AssuntoController.impacto, methods=["GET"],
)

api_blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>/impacto-transferencia",
    endpoint="impacto_transferencia_assunto",
    view_func=AssuntoController.previa_transferencia,
    methods=["GET"],
)

api_blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>/transferir", endpoint="transferir_assunto",
    view_func=AssuntoController.transferir, methods=["POST"],
)

for acao_assunto in ("inativar", "arquivar", "reativar"):
    api_blueprint.add_url_rule(
        f"/assuntos/<int:assunto_id>/{acao_assunto}",
        endpoint=f"{acao_assunto}_assunto",
        view_func=AssuntoController.alterar_status,
        defaults={"acao": acao_assunto},
        methods=["POST"],
    )

api_blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>",
    endpoint="deletar_assunto",
    view_func=AssuntoController.deletar,
    methods=["DELETE"],
)
