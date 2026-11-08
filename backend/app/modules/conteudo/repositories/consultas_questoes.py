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
        # Lista de apresentação: whitelist equivalente a conteudo(correcao=False).
        campos = ('enunciado', 'alternativa_a', 'alternativa_b', 'alternativa_c',
                  'alternativa_d', 'alternativa_e', 'dificuldade', 'assunto_id')
        return [{**{campo: v[campo] for campo in campos},
                 'questao_id': v['questao_id'], 'questao_versao_id': v['id'],
                 'assunto': {'id': v['assunto_id'], 'nome': v['assunto_nome']},
                 'materia': {'id': v['materia_id'], 'nome': v['materia_nome']},
                 'area_enem': {'id': v['area_enem_id'], 'nome': v['area_enem_nome']}}
                for v in versoes], total
