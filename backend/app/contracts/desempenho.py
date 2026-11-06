from contextlib import AbstractContextManager
from datetime import datetime
from typing import Mapping, Protocol, TypedDict


class ContextoConsulta(Protocol):
    """Opaco ao Service: somente o instante, sem conexão ou execução SQL."""
    @property
    def instante(self) -> datetime: ...


class EscoposLeitura(Protocol):
    def usar(self, contexto: ContextoConsulta | None = None, instante: datetime | None = None) -> AbstractContextManager[ContextoConsulta]: ...


class ContagemMetrica(TypedDict):
    total_respostas: int
    acertos: int
    pratica: int
    simulado: int


class GrupoMateria(ContagemMetrica):
    materia_id: int
    materia_nome: str


class GrupoAssunto(GrupoMateria):
    assunto_id: int
    assunto_nome: str


class ConsultaMetricasDesempenho(Protocol):
    def agregar(self, contexto: ContextoConsulta, usuario_id: int, inicio: datetime, fim: datetime) -> tuple[ContagemMetrica, list[GrupoMateria], list[GrupoAssunto]]: ...


class AtividadeAluno(TypedDict):
    id: int
    tipo: str
    ocorrido_em: datetime
    titulo: str


class ConsultaAtividadesAluno(Protocol):
    def atividades(self, contexto: ContextoConsulta, usuario_id: int, inicio: datetime, fim: datetime) -> list[AtividadeAluno]: ...


class ContagensCatalogo(TypedDict):
    materias_ativas: int
    assuntos_ativos: int


class ContagensQuestoes(TypedDict):
    rascunhos: int
    publicadas: int
    arquivadas: int


class ContagensSimulados(TypedDict):
    rascunhos: int
    publicados: int
    arquivados: int


class ContagensAdmin(TypedDict):
    catalogo: ContagensCatalogo
    questoes: ContagensQuestoes
    simulados: ContagensSimulados
    tentativas_simulado_finalizadas: int


class ConsultaContagensAdmin(Protocol):
    def administrativo(self, contexto: ContextoConsulta) -> ContagensAdmin: ...


class PeriodoDiagnostico(TypedDict):
    inicio: str
    fim: str
    timezone: str


class BaseMetrica(TypedDict):
    pratica: int
    simulado: int


class MetricaDiagnostico(TypedDict):
    total_respostas: int
    acertos: int
    erros: int
    percentual_acerto: float | None
    estado_amostra: str
    base: BaseMetrica


class MateriaDiagnostico(MetricaDiagnostico):
    materia_id: int
    materia_nome: str


class AssuntoDiagnostico(MateriaDiagnostico):
    assunto_id: int
    assunto_nome: str


class DiagnosticoRegistro(TypedDict):
    periodo: PeriodoDiagnostico
    calculado_em: str
    limiar_amostra: int
    base: BaseMetrica
    geral: MetricaDiagnostico
    materias: list[MateriaDiagnostico]
    assuntos: list[AssuntoDiagnostico]


class DiagnosticoAluno(Protocol):
    def executar(self, usuario_id: int, filtros: Mapping[str, str] | None = None, contexto: ContextoConsulta | None = None, instante: datetime | None = None) -> DiagnosticoRegistro: ...
