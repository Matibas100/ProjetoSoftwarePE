"""Adaptação das métricas e do escopo consistente já existentes."""
from app.contexto_leitura import ContextoLeitura
from app.modules.desempenho.repositories.desempenho_repository import DesempenhoRepository


class EscoposLeituraMySQL:
    def usar(self, contexto=None, instante=None):
        return ContextoLeitura.usar(contexto, instante)


class ConsultaMetricasMySQL:
    def agregar(self, contexto, usuario_id, inicio, fim):
        geral, materias, assuntos = DesempenhoRepository.agregar(contexto, usuario_id, inicio, fim)

        def registro(linha):
            return {**linha, **{k: int(linha[k]) for k in ('total_respostas', 'acertos', 'pratica', 'simulado')}}

        return registro(geral), [registro(r) for r in materias], [registro(r) for r in assuntos]


class ConsultaAtividadesMySQL:
    def atividades(self, contexto, usuario_id, inicio, fim):
        return DesempenhoRepository.atividades(contexto, usuario_id, inicio, fim)


class ConsultaContagensMySQL:
    def administrativo(self, contexto):
        return DesempenhoRepository.administrativo(contexto)
