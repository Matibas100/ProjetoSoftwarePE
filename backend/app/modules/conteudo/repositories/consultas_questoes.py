"""Leituras especializadas; nenhuma entidade ORM atravessa os contratos."""
from app.contracts.catalogo import FiltrosCatalogo
from app.contracts.questoes import QuestaoAdministrativa, QuestaoSegura
from app.modules.conteudo.repositories.questao_repository import QuestaoRepository


class ConsultaQuestoesPorAssuntoMySQL:
    def buscar_por_assunto(self, assunto_id: int) -> list[QuestaoAdministrativa]:
        return QuestaoRepository.buscar_por_assunto(assunto_id)


class ConsultaQuestoesElegiveisMySQL:
    def listar(self, filtros: FiltrosCatalogo, pagina: int, limite: int) -> tuple[list[QuestaoSegura], int]:
        versoes, total = QuestaoRepository.listar_elegiveis(filtros, pagina, limite)
        return [v.conteudo() for v in versoes], total
