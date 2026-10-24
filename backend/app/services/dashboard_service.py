from app.contexto_leitura import ContextoLeitura
from app.exceptions import DadosInvalidosError
from app.repositories.desempenho_repository import DesempenhoRepository as Repo
from app.services.consultar_desempenho_service import ConsultarDesempenhoService
from app.services.desempenho_validacao import periodo


class ConsultarDashboardAlunoService:
    @staticmethod
    def executar(usuario_id, filtros):
        with ContextoLeitura.usar() as leitura:
            diagnostico = ConsultarDesempenhoService.executar(usuario_id, filtros, leitura, leitura.instante)
            _, inicio, fim = periodo(filtros, leitura.instante)
            atividades = Repo.atividades(leitura, usuario_id, inicio, fim)
            for a in atividades:
                a["ocorrido_em"] = a["ocorrido_em"].isoformat() + "Z"
                destino = "questao" if a["tipo"] == "pratica" else "simulado"
                a["url"] = f"/aluno/{destino}.html?tentativa_id={a['id']}"
            return {"desempenho": diagnostico, "ultimas_atividades": atividades}


class ConsultarDashboardAdminService:
    @staticmethod
    def executar(filtros):
        if filtros:
            raise DadosInvalidosError("O dashboard administrativo não aceita filtros.")
        with ContextoLeitura.usar() as leitura:
            return {"calculado_em": leitura.instante.isoformat() + "Z", **Repo.administrativo(leitura)}
