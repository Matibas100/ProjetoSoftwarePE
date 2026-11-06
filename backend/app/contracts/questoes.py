from typing import Iterable, Protocol, TypedDict
from app.contracts.catalogo import FiltrosCatalogo, Referencia


class TextoQuestao(TypedDict):
    enunciado: str
    alternativa_a: str
    alternativa_b: str
    alternativa_c: str
    alternativa_d: str
    alternativa_e: str
    dificuldade: str
    assunto_id: int


class QuestaoAdministrativa(TextoQuestao):
    id: int
    resposta_correta: str
    explicacao: str | None


class QuestaoSegura(TextoQuestao):
    questao_id: int
    questao_versao_id: int
    assunto: Referencia
    materia: Referencia
    area_enem: Referencia


class ConsultaQuestoesPorAssunto(Protocol):
    def buscar_por_assunto(self, assunto_id: int) -> list[QuestaoAdministrativa]: ...


class ConsultaQuestoesElegiveis(Protocol):
    def listar(self, filtros: FiltrosCatalogo, pagina: int, limite: int) -> tuple[list[QuestaoSegura], int]: ...


class ConsultaElegibilidadeVersoes(Protocol):
    def executar(self, ids: Iterable[int]) -> dict[int, QuestaoSegura]: ...
