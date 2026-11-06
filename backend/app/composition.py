"""Ligações explícitas por aplicação; nenhum estado de requisição ou conexão."""
from dataclasses import dataclass
from app.repositories.consultas_catalogo import ConsultaMateriasMySQL, ConsultaAssuntosMySQL
from app.services.listar_catalogo_admin_service import ListarMateriasAdminService, ListarAssuntosAdminService
from app.models.assunto import Assunto
from app.repositories.consultas_questoes import ConsultaQuestoesPorAssuntoMySQL, ConsultaQuestoesElegiveisMySQL
from app.services.buscar_questoes_por_assunto_service import BuscarQuestoesPorAssuntoService
from app.services.listar_questoes_aluno_service import ListarQuestoesAlunoService
from app.repositories.consultas_simulados import ConsultaCatalogoSimuladosMySQL, ConsultaHistoricoSimuladosMySQL
from app.services.listar_simulados_aluno_service import ListarSimuladosAlunoService
from app.services.listar_historico_simulados_service import ListarHistoricoSimuladosService
from app.services.gestao_questao_service import ConsultarVersoesElegiveisService
from app.repositories.consultas_desempenho import EscoposLeituraMySQL, ConsultaMetricasMySQL, ConsultaAtividadesMySQL, ConsultaContagensMySQL
from app.services.consultar_desempenho_service import ConsultarDesempenhoService
from app.services.dashboard_service import ConsultarDashboardAlunoService, ConsultarDashboardAdminService
from app.services.selecionar_plano_service import SelecionarPlanoService
from app.services.gerar_plano_service import GerarPlanoService
from app.services.recalcular_plano_service import RecalcularPlanoService


@dataclass
class Composicao:
    """Colaboradores sem estado; ligações acrescentadas por domínio convertido."""
    materias_admin: ListarMateriasAdminService
    assuntos_admin: ListarAssuntosAdminService
    questoes_por_assunto: BuscarQuestoesPorAssuntoService
    questoes_aluno: ListarQuestoesAlunoService
    simulados_aluno: ListarSimuladosAlunoService
    historico_simulados: ListarHistoricoSimuladosService
    desempenho: ConsultarDesempenhoService
    dashboard_aluno: ConsultarDashboardAlunoService
    dashboard_admin: ConsultarDashboardAdminService
    gerar_plano: GerarPlanoService
    recalcular_plano: RecalcularPlanoService


def compor() -> Composicao:
    escopos = EscoposLeituraMySQL()
    diagnostico = ConsultarDesempenhoService(ConsultaMetricasMySQL(), escopos)
    seletor = SelecionarPlanoService(diagnostico)
    return Composicao(
        materias_admin=ListarMateriasAdminService(ConsultaMateriasMySQL()),
        assuntos_admin=ListarAssuntosAdminService(ConsultaAssuntosMySQL()),
        questoes_por_assunto=BuscarQuestoesPorAssuntoService(
            ConsultaQuestoesPorAssuntoMySQL(), lambda id_: Assunto.buscar_por_id(id_) is not None),
        questoes_aluno=ListarQuestoesAlunoService(ConsultaQuestoesElegiveisMySQL()),
        simulados_aluno=ListarSimuladosAlunoService(ConsultaCatalogoSimuladosMySQL(), ConsultarVersoesElegiveisService()),
        historico_simulados=ListarHistoricoSimuladosService(ConsultaHistoricoSimuladosMySQL()),
        desempenho=diagnostico,
        dashboard_aluno=ConsultarDashboardAlunoService(diagnostico, ConsultaAtividadesMySQL(), escopos),
        dashboard_admin=ConsultarDashboardAdminService(ConsultaContagensMySQL(), escopos),
        gerar_plano=GerarPlanoService(seletor),
        recalcular_plano=RecalcularPlanoService(seletor),
    )
