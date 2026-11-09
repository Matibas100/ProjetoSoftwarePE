"""Ligações explícitas por aplicação; nenhum estado de requisição ou conexão."""
from dataclasses import dataclass
from app.modules.contas.api import ValidarPermissaoTutoriaService
from app.modules.tutor_ia.services.gerar_tutoria_service import GerarTutoriaService
from app.modules.tutor_ia.services.gemini_service import GeminiService
from app.modules.tutor_ia.services.limite_tutoria import LimiteTutoria
from app.modules.contas.services.recusar_consentimento_plano_service import RecusarConsentimentoPlanoService
from app.modules.contas.services.revogar_consentimento_plano_service import RevogarConsentimentoPlanoService
from app.modules.plano_estudos.api import EliminarPlanosPropriosService

from app.modules.conteudo.repositories.consultas_catalogo import ConsultaMateriasMySQL, ConsultaAssuntosMySQL
from app.modules.conteudo.services.listar_catalogo_admin_service import ListarMateriasAdminService, ListarAssuntosAdminService
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.repositories.consultas_questoes import ConsultaQuestoesPorAssuntoMySQL, ConsultaQuestoesElegiveisMySQL
from app.modules.conteudo.services.buscar_questoes_por_assunto_service import BuscarQuestoesPorAssuntoService
from app.modules.praticas.services.listar_questoes_aluno_service import ListarQuestoesAlunoService
from app.modules.simulados.repositories.consultas_simulados import ConsultaCatalogoSimuladosMySQL, ConsultaHistoricoSimuladosMySQL
from app.modules.simulados.services.listar_simulados_aluno_service import ListarSimuladosAlunoService
from app.modules.simulados.services.listar_historico_simulados_service import ListarHistoricoSimuladosService
from app.modules.conteudo.services.gestao_questao_service import ConsultarVersoesElegiveisService
from app.modules.desempenho.repositories.consultas_desempenho import EscoposLeituraMySQL, ConsultaMetricasMySQL, ConsultaAtividadesMySQL, ConsultaContagensMySQL
from app.modules.desempenho.services.consultar_desempenho_service import ConsultarDesempenhoService
from app.modules.desempenho.services.dashboard_service import ConsultarDashboardAlunoService, ConsultarDashboardAdminService
from app.modules.plano_estudos.services.selecionar_plano_service import SelecionarPlanoService
from app.modules.plano_estudos.services.gerar_plano_service import GerarPlanoService
from app.modules.plano_estudos.services.recalcular_plano_service import RecalcularPlanoService


@dataclass
class Composicao:
    """Colaboradores sem estado; ligações acrescentadas por domínio convertido."""
    recusar_consentimento_plano: RecusarConsentimentoPlanoService
    revogar_consentimento_plano: RevogarConsentimentoPlanoService
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
    gerar_tutoria: GerarTutoriaService


def compor(config=None) -> Composicao:
    config = config or {}
    escopos = EscoposLeituraMySQL()
    diagnostico = ConsultarDesempenhoService(ConsultaMetricasMySQL(), escopos)
    seletor = SelecionarPlanoService(diagnostico)
    eliminador = EliminarPlanosPropriosService()
    return Composicao(
        gerar_tutoria=GerarTutoriaService(GeminiService(
            habilitado=config.get('TUTOR_IA_ENABLED', False),
            chave=config.get('GEMINI_API_KEY', ''),
            modelo=config.get('GEMINI_MODEL', 'gemini-3.6-flash')),
            ValidarPermissaoTutoriaService.executar, LimiteTutoria()),
        recusar_consentimento_plano=RecusarConsentimentoPlanoService(eliminador.executar),
        revogar_consentimento_plano=RevogarConsentimentoPlanoService(eliminador.executar),
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
