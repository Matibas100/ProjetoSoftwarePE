from decimal import Decimal, ROUND_HALF_UP
from app.contracts.desempenho import ConsultaMetricasDesempenho, EscoposLeitura
from app.services.desempenho_validacao import periodo


def metrica(linha):
    total, acertos = int(linha["total_respostas"]), int(linha["acertos"])
    percentual = float((Decimal(100) * acertos / total).quantize(Decimal(".01"), rounding=ROUND_HALF_UP)) if total else None
    return {"total_respostas": total, "acertos": acertos, "erros": total - acertos,
        "percentual_acerto": percentual, "estado_amostra": "sem_dados" if not total else "amostra_pequena" if total < 5 else "dados_disponiveis",
        "base": {"pratica": int(linha["pratica"]), "simulado": int(linha["simulado"])}}


class ConsultarDesempenhoService:
    def __init__(self, consulta: ConsultaMetricasDesempenho, escopos: EscoposLeitura):
        self._consulta = consulta
        self._escopos = escopos

    def executar(self, usuario_id, filtros=None, contexto=None, instante=None):
        if type(usuario_id) is not int or usuario_id <= 0:
            raise ValueError("Usuário autorizado obrigatório.")
        with self._escopos.usar(contexto, instante) as leitura:
            datas, inicio, fim = periodo({} if filtros is None else filtros, leitura.instante)
            geral, materias, assuntos = self._consulta.agregar(leitura, usuario_id, inicio, fim)
            resumo = metrica(geral)
            return {"periodo": datas, "calculado_em": leitura.instante.isoformat() + "Z", "limiar_amostra": 5,
                "base": resumo["base"], "geral": resumo,
                "materias": [{**{k: r[k] for k in ("materia_id", "materia_nome")}, **metrica(r)} for r in materias],
                "assuntos": [{**{k: r[k] for k in ("materia_id", "materia_nome", "assunto_id", "assunto_nome")}, **metrica(r)} for r in assuntos]}
