"""Leituras MySQL pelos contratos históricos publicados pelos proprietários."""
from app.core.procedures_mysql import conferir_resultados
from app.modules.simulados.api import contagens_dashboard as contagens_simulados
from app.modules.conteudo.api import contagens_catalogo, contagens_questoes


METRICAS = ('total_respostas', 'acertos', 'pratica', 'simulado')
GRUPOS = ('materia_id', 'materia_nome', 'assunto_id', 'assunto_nome') + METRICAS + ('posicao',)


class DesempenhoRepository:
    @staticmethod
    def agregar(contexto, usuario_id, inicio, fim):
        resultados = contexto.executar_resultados(
            "CALL sp_desempenho_resumo(%s,%s,%s)", (usuario_id, inicio, fim))
        gerais, materias, assuntos = conferir_resultados(resultados, [METRICAS, GRUPOS, GRUPOS])
        geral, = gerais
        return geral, list(materias), list(assuntos)

    @staticmethod
    def atividades(contexto, usuario_id, inicio, fim):
        resultados = contexto.executar_resultados(
            "CALL sp_atividades_recentes(%s,%s,%s)", (usuario_id, inicio, fim))
        linhas, = conferir_resultados(resultados, [('tipo', 'id', 'ocorrido_em', 'titulo')])
        return list(linhas)

    @staticmethod
    def administrativo(contexto):
        catalogo = contagens_catalogo(contexto)
        questoes = contagens_questoes(contexto)
        simulados, finalizadas = contagens_simulados(contexto)
        return {"catalogo": catalogo, "questoes": questoes, "simulados": simulados,
            "tentativas_simulado_finalizadas": finalizadas}
