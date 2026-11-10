"""Rotas do proprietário, sem regra de negócio."""
from flask import Blueprint

from app.modules.conteudo.controllers.assunto_controller import AssuntoController
from app.modules.conteudo.controllers.area_enem_controller import AreaEnemController
from app.modules.conteudo.controllers.materia_controller import MateriaController
from app.modules.conteudo.controllers.questao_controller import QuestaoController

blueprint = Blueprint("conteudo", __name__)

blueprint.add_url_rule(
    "/materias/<int:materia_id>",
    endpoint="buscar_materia_por_id",
    view_func=MateriaController.buscar_por_id,
    methods=["GET"]
)
blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>",
    endpoint="buscar_assunto_por_id",
    view_func=AssuntoController.buscar_por_id,
    methods=["GET"]
)

blueprint.add_url_rule(
    "/admin/questoes",
    endpoint="listar_questoes_admin",
    view_func=QuestaoController.listar_admin,
    methods=["GET"]
)

for nome, metodo in (("detalhe", "GET"), ("editar", "PUT")):
    blueprint.add_url_rule(
        "/questoes/<int:questao_id>",
        endpoint=f"questao_{nome}",
        view_func=getattr(QuestaoController, nome),
        methods=[metodo]
    )

for nome in ("publicar", "arquivar"):
    blueprint.add_url_rule(
        f"/questoes/<int:questao_id>/{nome}",
        endpoint=f"questao_{nome}",
        view_func=getattr(QuestaoController, nome),
        methods=["POST"]
    )

blueprint.add_url_rule(
    "/areas-enem",
    endpoint="listar_areas_enem",
    view_func=AreaEnemController.listar,
    methods=["GET"],
)

blueprint.add_url_rule(
    "/materias",
    endpoint="cadastrar_materia",
    view_func=MateriaController.cadastrar,
    methods=["POST"],
)

blueprint.add_url_rule(
    "/materias",
    endpoint="listar_materias",
    view_func=MateriaController.listar,
    methods=["GET"],
)

blueprint.add_url_rule(
    "/materias/<int:materia_id>",
    endpoint="atualizar_materia",
    view_func=MateriaController.atualizar,
    methods=["PUT"],
)

blueprint.add_url_rule(
    "/admin/materias",
    endpoint="listar_materias_admin",
    view_func=MateriaController.listar_admin,
    methods=["GET"],
)

blueprint.add_url_rule(
    "/materias/<int:materia_id>/impacto-exclusao",
    endpoint="impacto_materia",
    view_func=MateriaController.impacto,
    methods=["GET"],
)

for acao_materia in ("inativar", "arquivar", "reativar"):
    blueprint.add_url_rule(
        f"/materias/<int:materia_id>/{acao_materia}",
        endpoint=f"{acao_materia}_materia",
        view_func=MateriaController.alterar_status,
        defaults={"acao": acao_materia},
        methods=["POST"],
    )

blueprint.add_url_rule(
    "/materias/<int:materia_id>",
    endpoint="deletar_materia",
    view_func=MateriaController.deletar,
    methods=["DELETE"],
)

blueprint.add_url_rule(
    "/questoes",
    endpoint="cadastrar_questao",
    view_func=QuestaoController.cadastrar,
    methods=["POST"],
)

blueprint.add_url_rule(
    "/questoes/por-assunto",
    endpoint="buscar_questoes_por_assunto",
    view_func=QuestaoController.buscar_por_assunto,
    methods=["GET"],
)

blueprint.add_url_rule(
    "/assuntos",
    endpoint="cadastrar_assunto",
    view_func=AssuntoController.cadastrar,
    methods=["POST"],
)

blueprint.add_url_rule(
    "/assuntos",
    endpoint="listar_assuntos",
    view_func=AssuntoController.listar,
    methods=["GET"],
)

blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>",
    endpoint="atualizar_assunto",
    view_func=AssuntoController.atualizar,
    methods=["PUT"],
)

blueprint.add_url_rule(
    "/admin/assuntos",
    endpoint="listar_assuntos_admin",
    view_func=AssuntoController.listar_admin,
    methods=["GET"],
)

blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>/impacto-exclusao",
    endpoint="impacto_assunto",
    view_func=AssuntoController.impacto,
    methods=["GET"],
)

blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>/impacto-transferencia",
    endpoint="impacto_transferencia_assunto",
    view_func=AssuntoController.previa_transferencia,
    methods=["GET"],
)

blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>/transferir",
    endpoint="transferir_assunto",
    view_func=AssuntoController.transferir,
    methods=["POST"],
)

for acao_assunto in ("inativar", "arquivar", "reativar"):
    blueprint.add_url_rule(
        f"/assuntos/<int:assunto_id>/{acao_assunto}",
        endpoint=f"{acao_assunto}_assunto",
        view_func=AssuntoController.alterar_status,
        defaults={"acao": acao_assunto},
        methods=["POST"],
    )

blueprint.add_url_rule(
    "/assuntos/<int:assunto_id>",
    endpoint="deletar_assunto",
    view_func=AssuntoController.deletar,
    methods=["DELETE"],
)
