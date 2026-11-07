"""DTOs próprios e contrato de fatos concluídos, sem correção antecipada."""
from app.exceptions import RecursoNaoEncontradoError, ConflitoError
from app.modules.simulados.models.simulado import SimuladoVersao
from app.modules.simulados.repositories.simulado_repository import SimuladoRepository as Repo
from app.modules.conteudo.api import ConsultarVersaoHistoricaService, ConsultarVersoesHistoricasService


def propria(usuario_id, tentativa_id, bloquear=False):
    t = Repo.propria(usuario_id, tentativa_id, bloquear)
    if t is None:
        raise RecursoNaoEncontradoError("Tentativa não encontrada.")
    return t


def detalhe(t, correcao=False, bloquear=False):
    v = SimuladoVersao.buscar_por_id(t.simulado_versao_id)
    itens = []
    respostas = Repo.respostas(t.id, bloquear=bloquear)
    conteudos = (None if bloquear else ConsultarVersoesHistoricasService.executar(
        [i.questao_versao_id for _, i in respostas], correcao=correcao))
    for r, i in respostas:
        linha = {"item_id": i.id, "posicao": i.posicao, "alternativa": r.alternativa,
            "questao": (ConsultarVersaoHistoricaService.executar(i.questao_versao_id, correcao=correcao)
                if bloquear else conteudos[i.questao_versao_id])}
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


class ConsultarFatosSimuladosService:
    @staticmethod
    def executar(usuario_id, inicio, fim):
        fatos = []
        linhas = Repo.fatos(usuario_id, inicio, fim)
        conteudos = ConsultarVersoesHistoricasService.executar([i.questao_versao_id for _, i, _ in linhas])
        for r, i, t in linhas:
            q = conteudos[i.questao_versao_id]
            fatos.append({"id": r.id, "atividade_id": t.id, "usuario_id": t.usuario_id,
                "questao_versao_id": i.questao_versao_id, "finalizada_em": t.finalizada_em,
                "alternativa": r.alternativa, "correta": r.correta,
                "classificacao": {"materia": q["materia"], "assunto": q["assunto"]}})
        return fatos

# Compatibilidade de imports: as consultas são classes de instância independentes.
from app.modules.simulados.services.listar_simulados_aluno_service import ListarSimuladosAlunoService
from app.modules.simulados.services.listar_historico_simulados_service import ListarHistoricoSimuladosService
