from fractions import Fraction
from app.modules.conteudo.api import pares_elegiveis_plano
from app.contracts.desempenho import DiagnosticoAluno


class SelecionarPlanoService:
    def __init__(self, diagnostico: DiagnosticoAluno):
        self._diagnostico = diagnostico

    def executar(self, usuario_id, contexto, instante):
        diagnostico = self._diagnostico.executar(usuario_id, contexto=contexto, instante=instante)
        limiar = diagnostico["limiar_amostra"]
        grupos = [a for a in diagnostico["assuntos"] if a["total_respostas"] >= limiar]
        pares = pares_elegiveis_plano([a["assunto_id"] for a in grupos], bloquear=True)
        grupos = [a for a in grupos if (a["assunto_id"], a["materia_id"]) in pares]
        grupos.sort(key=lambda a: (
            Fraction(
                a["acertos"],
                a["total_respostas"]
            ),
            -a["total_respostas"],
            a["assunto_id"]
        ))
        itens = []
        for posicao, a in enumerate(grupos[: 3], 1):
            texto = (f"{a['acertos']} {'acerto' if a['acertos'] == 1 else 'acertos'} em {a['total_respostas']} respostas nos últimos 30 dias UTC. "
                "Prioridade relativa entre os assuntos praticados, pela menor taxa de acerto; "
                "em empate, maior amostra e menor ID do Assunto. O limiar é operacional, sem comprovar domínio.")
            itens.append({k: a[k] for k in (
                "assunto_id",
                "assunto_nome",
                "materia_id",
                "materia_nome",
                "acertos",
                "total_respostas",
                "percentual_acerto"
            )}
                | {
                    "periodo": diagnostico["periodo"],
                    "limiar_amostra": limiar,
                    "posicao": posicao,
                    "justificativa": texto
                })
        return diagnostico["periodo"], itens
