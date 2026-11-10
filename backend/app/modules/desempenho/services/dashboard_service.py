from app.exceptions import DadosInvalidosError
from app.contracts.desempenho import (
    DiagnosticoAluno,
    ConsultaAtividadesAluno,
    ConsultaContagensAdmin,
    EscoposLeitura,
)
from app.modules.desempenho.services.desempenho_validacao import periodo


class ConsultarDashboardAlunoService:
    def __init__(
        self,
        diagnostico: DiagnosticoAluno,
        atividades: ConsultaAtividadesAluno,
        escopos: EscoposLeitura
    ):
        self._diagnostico = diagnostico
        self._atividades = atividades
        self._escopos = escopos

    def executar(self, usuario_id, filtros):
        with self._escopos.usar() as leitura:
            diagnostico = self._diagnostico.executar(usuario_id, filtros, leitura, leitura.instante)
            _, inicio, fim = periodo(filtros, leitura.instante)
            atividades = self._atividades.atividades(leitura, usuario_id, inicio, fim)
            for a in atividades:
                a["ocorrido_em"] = a["ocorrido_em"].isoformat() + "Z"
                destino = "questao" if a["tipo"] == "pratica" else "simulado"
                a["url"] = f"/aluno/{destino}.html?tentativa_id={a['id']}"
            return {"desempenho": diagnostico, "ultimas_atividades": atividades}


class ConsultarDashboardAdminService:
    def __init__(self, contagens: ConsultaContagensAdmin, escopos: EscoposLeitura):
        self._contagens = contagens
        self._escopos = escopos

    def executar(self, filtros):
        if filtros:
            raise DadosInvalidosError("O dashboard administrativo não aceita filtros.")
        with self._escopos.usar() as leitura:
            return {
                "calculado_em": leitura.instante.isoformat() + "Z",
                **self._contagens.administrativo(leitura)
            }
