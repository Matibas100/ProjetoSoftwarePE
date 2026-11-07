"""Agregação no MySQL somente pelos contratos de leitura dos módulos de origem."""
from sqlalchemy import select, union_all, func, case
from app.modules.praticas.api import projecao_desempenho as fatos_praticas, projecao_atividades as atividades_praticas
from app.modules.simulados.api import projecao_desempenho as fatos_simulados, projecao_atividades as atividades_simulados, contagens_dashboard as contagens_simulados
from app.modules.conteudo.api import contagens_catalogo, contagens_questoes


class DesempenhoRepository:
    @staticmethod
    def fatos(usuario_id, inicio, fim):
        return union_all(fatos_praticas(usuario_id, inicio, fim),
            fatos_simulados(usuario_id, inicio, fim)).cte("fatos")

    @staticmethod
    def agregar(contexto, usuario_id, inicio, fim):
        fatos = DesempenhoRepository.fatos(usuario_id, inicio, fim)
        c = fatos.c
        contagens = {"total_respostas": func.count(), "acertos": func.coalesce(func.sum(case((c.correta == True, 1), else_=0)), 0),
            "pratica": func.coalesce(func.sum(case((c.tipo == "pratica", 1), else_=0)), 0),
            "simulado": func.coalesce(func.sum(case((c.tipo == "simulado", 1), else_=0)), 0)}
        geral = dict(contexto.executar(select(*(v.label(k) for k, v in contagens.items())).select_from(fatos)).mappings().one())

        def grupos(campos):
            particao = [getattr(c, campo) for campo in campos]
            ordem = [c.ocorrido_em.desc(), c.tipo.desc(), c.id.desc()]
            classificacao = [c.materia_id, c.materia_nome, c.assunto_id, c.assunto_nome]
            totais = [func.count().over(partition_by=particao).label("total_respostas"),
                func.sum(case((c.correta == True, 1), else_=0)).over(partition_by=particao).label("acertos"),
                func.sum(case((c.tipo == "pratica", 1), else_=0)).over(partition_by=particao).label("pratica"),
                func.sum(case((c.tipo == "simulado", 1), else_=0)).over(partition_by=particao).label("simulado")]
            ranking = select(*classificacao, *totais,
                func.row_number().over(partition_by=particao, order_by=ordem).label("posicao")).subquery()
            return [dict(r) for r in contexto.executar(select(ranking).where(ranking.c.posicao == 1)
                .order_by(*(getattr(ranking.c, campo) for campo in campos))).mappings().all()]
        return geral, grupos(["materia_id"]), grupos(["materia_id", "assunto_id"])

    @staticmethod
    def atividades(contexto, usuario_id, inicio, fim):
        origens = union_all(atividades_praticas(usuario_id, inicio, fim),
            atividades_simulados(usuario_id, inicio, fim)).subquery()
        return [dict(r) for r in contexto.executar(select(origens).order_by(origens.c.ocorrido_em.desc(),
            origens.c.tipo.desc(), origens.c.id.desc()).limit(5)).mappings().all()]

    @staticmethod
    def administrativo(contexto):
        catalogo = contagens_catalogo(contexto)
        questoes = contagens_questoes(contexto)
        simulados, finalizadas = contagens_simulados(contexto)
        return {"catalogo": catalogo, "questoes": questoes, "simulados": simulados,
            "tentativas_simulado_finalizadas": finalizadas}
