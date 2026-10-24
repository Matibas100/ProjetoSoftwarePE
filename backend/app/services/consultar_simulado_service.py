"""DTOs próprios e contrato de fatos concluídos, sem correção antecipada."""
from app.exceptions import RecursoNaoEncontradoError, ConflitoError
from app.models.simulado import SimuladoVersao
from app.repositories.simulado_repository import SimuladoRepository as Repo
from app.services.gestao_questao_service import ConsultarVersaoHistoricaService, ConsultarVersaoElegivelService
from app.services.listar_catalogo_admin_service import _envelope
from app.services.simulado_validacao import paginacao


def propria(usuario_id, tentativa_id, bloquear=False):
    t = Repo.propria(usuario_id, tentativa_id, bloquear)
    if t is None:
        raise RecursoNaoEncontradoError("Tentativa não encontrada.")
    return t


def detalhe(t, correcao=False, bloquear=False):
    v = SimuladoVersao.buscar_por_id(t.simulado_versao_id)
    itens = []
    for r, i in Repo.respostas(t.id, bloquear=bloquear):
        linha = {"item_id": i.id, "posicao": i.posicao, "alternativa": r.alternativa,
            "questao": ConsultarVersaoHistoricaService.executar(i.questao_versao_id, correcao=correcao)}
        if correcao:
            linha.update(correta=r.correta, gabarito=linha["questao"]["resposta_correta"], explicacao=linha["questao"]["explicacao"])
        itens.append(linha)
    dados = {"id": t.id, "estado": t.estado, "revisao": t.revisao,
        "simulado_versao_id": v.id, "titulo": v.titulo, "itens": itens}
    if t.estado == "finalizada":
        dados["resultado"] = t.resultado()
    return dados


class ConsultarTentativaSimuladoService:
    @staticmethod
    def executar(usuario_id, tentativa_id, modo=None):
        t = propria(usuario_id, tentativa_id)
        if modo and t.estado != "finalizada":
            raise ConflitoError("Finalize a tentativa para consultar resultado e correção.")
        if modo == "resultado":
            return t.resultado()
        return detalhe(t, correcao=modo == "correcao")


class ListarSimuladosAlunoService:
    @staticmethod
    def executar(usuario_id, filtros):
        valores, _ = paginacao(filtros)
        linhas, total = Repo.listar(valores["pagina"], valores["por_pagina"], "publicado")
        itens = []
        for s in linhas:
            composicao = Repo.itens(versao_id=s.simulado_versao_id)
            disponivel = bool(composicao)
            for i in composicao:
                try:
                    ConsultarVersaoElegivelService.executar(i.questao_versao_id)
                except (ConflitoError, RecursoNaoEncontradoError):
                    disponivel = False
            tentativa = Repo.andamento(usuario_id, s.simulado_versao_id)
            itens.append({"id": s.id, "simulado_versao_id": s.simulado_versao_id, "titulo": s.titulo,
                "total_questoes": len(composicao), "disponivel": disponivel,
                "tentativa_em_andamento_id": tentativa.id if tentativa else None})
        return _envelope(itens, valores["pagina"], valores["por_pagina"], total)


class ListarHistoricoSimuladosService:
    @staticmethod
    def executar(usuario_id, filtros):
        valores, _ = paginacao(filtros)
        linhas, total = Repo.historico(usuario_id, valores["pagina"], valores["por_pagina"])
        return _envelope([{"id": t.id, "titulo": SimuladoVersao.buscar_por_id(t.simulado_versao_id).titulo,
            "simulado_versao_id": t.simulado_versao_id, "resultado": t.resultado()} for t in linhas],
            valores["pagina"], valores["por_pagina"], total)


class ConsultarFatosSimuladosService:
    @staticmethod
    def executar(usuario_id, inicio, fim):
        fatos = []
        for r, i, t in Repo.fatos(usuario_id, inicio, fim):
            q = ConsultarVersaoHistoricaService.executar(i.questao_versao_id)
            fatos.append({"id": r.id, "atividade_id": t.id, "usuario_id": t.usuario_id,
                "questao_versao_id": i.questao_versao_id, "finalizada_em": t.finalizada_em,
                "alternativa": r.alternativa, "correta": r.correta,
                "classificacao": {"materia": q["materia"], "assunto": q["assunto"]}})
        return fatos
