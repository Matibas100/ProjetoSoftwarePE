from app.modules.praticas.repositories.pratica_repository import PraticaRepository
from app.core.paginacao import envelope_paginado
from app.modules.praticas.services.pratica_validacao import parametros


class ListarPraticasService:
    @staticmethod
    def executar(usuario_id, filtros):
        valores = parametros(filtros, {"assunto_id"})
        linhas, total = PraticaRepository.historico(
            usuario_id,
            valores["assunto_id"],
            valores["pagina"],
            valores["por_pagina"]
        )
        return envelope_paginado(
            [linha.resumo() for linha in linhas],
            valores["pagina"],
            valores["por_pagina"],
            total
        )


class ConsultarFatosPraticasService:
    @staticmethod
    def executar(usuario_id, inicio, fim):
        return [{
            "id": t.id,
            "usuario_id": t.usuario_id,
            "questao_versao_id": t.questao_versao_id,
            "respondida_em": t.respondida_em,
            "alternativa": t.resposta_escolhida,
            "correta": t.correta,
            "classificacao": t.classificacao()
        }
            for t in PraticaRepository.fatos(usuario_id, inicio, fim)]
