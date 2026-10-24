from flask import Blueprint

from app.controllers.assunto_controller import AssuntoController
from app.controllers.area_enem_controller import AreaEnemController
from app.controllers.health_controller import HealthController
from app.controllers.materia_controller import MateriaController
from app.controllers.questao_controller import QuestaoController
from app.controllers.autenticacao_controller import AutenticacaoController
from app.controllers.pratica_controller import PraticaController
from app.controllers.simulado_controller import SimuladoController
from app.controllers.desempenho_controller import DesempenhoController
from app.controllers.plano_estudo_controller import PlanoEstudoController


api_blueprint = Blueprint("api", __name__)

for caminho, nome, metodo in (("/aluno/plano", "consultar", "GET"),
    ("/aluno/plano/gerar", "gerar", "POST"), ("/aluno/plano/recalcular", "recalcular", "POST"),
    ("/aluno/plano/itens/<int:item_id>/concluir", "concluir", "POST")):
    api_blueprint.add_url_rule(caminho, endpoint=f"plano_{nome}", view_func=getattr(PlanoEstudoController, nome), methods=[metodo])

for caminho, nome in (("/aluno/desempenho", "diagnostico"), ("/aluno/dashboard", "aluno"), ("/admin/dashboard", "admin")):
    api_blueprint.add_url_rule(caminho, endpoint=f"desempenho_{nome}", view_func=getattr(DesempenhoController, nome), methods=["GET"])

for caminho, nome, metodo in (("/admin/simulados", "admin_lista", "GET"),
    ("/admin/simulados", "criar", "POST"), ("/admin/simulados/<int:simulado_id>", "admin_detalhe", "GET"),
    ("/admin/simulados/<int:simulado_id>", "editar", "PUT"),
    ("/admin/simulados/<int:simulado_id>/publicar", "publicar", "POST"),
    ("/admin/simulados/<int:simulado_id>/arquivar", "arquivar", "POST"),
    ("/aluno/simulados", "catalogo", "GET"), ("/aluno/tentativas-simulado", "iniciar", "POST"),
    ("/aluno/tentativas-simulado", "historico", "GET"),
    ("/aluno/tentativas-simulado/<int:tentativa_id>", "tentativa", "GET"),
    ("/aluno/tentativas-simulado/<int:tentativa_id>/respostas/<int:item_id>", "responder", "PUT"),
    ("/aluno/tentativas-simulado/<int:tentativa_id>/finalizar", "finalizar", "POST")):
    api_blueprint.add_url_rule(caminho, endpoint=f"simulado_{nome}", view_func=getattr(SimuladoController, nome), methods=[metodo])
for modo in ("resultado", "correcao"):
    api_blueprint.add_url_rule(f"/aluno/tentativas-simulado/<int:tentativa_id>/{modo}",
        endpoint=f"simulado_{modo}", view_func=SimuladoController.tentativa, defaults={"modo": modo}, methods=["GET"])

for caminho, nome, metodo in (("/aluno/questoes", "questoes", "GET"),
    ("/aluno/praticas", "iniciar", "POST"), ("/aluno/praticas", "historico", "GET"),
    ("/aluno/praticas/<int:tentativa_id>", "detalhe", "GET"),
    ("/aluno/praticas/<int:tentativa_id>/resposta", "responder", "POST")):
    api_blueprint.add_url_rule(caminho, endpoint=f"pratica_{nome}",
        view_func=getattr(PraticaController, nome), methods=[metodo])

api_blueprint.add_url_rule("/admin/questoes", endpoint="listar_questoes_admin",
    view_func=QuestaoController.listar_admin, methods=["GET"])
for nome, metodo in (("detalhe", "GET"), ("editar", "PUT")):
    api_blueprint.add_url_rule("/questoes/<int:questao_id>", endpoint=f"questao_{nome}",
        view_func=getattr(QuestaoController, nome), methods=[metodo])
for nome in ("publicar", "arquivar"):
    api_blueprint.add_url_rule(f"/questoes/<int:questao_id>/{nome}", endpoint=f"questao_{nome}",
        view_func=getattr(QuestaoController, nome), methods=["POST"])

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
