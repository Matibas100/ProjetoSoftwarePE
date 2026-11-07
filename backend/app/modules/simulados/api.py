"""Projeções de leitura do proprietário para agregação consistente."""
from app.modules.simulados.repositories.simulado_repository import SimuladoRepository as _Repo



def projecao_desempenho(usuario_id, inicio, fim):
    return _Repo.projecao_desempenho(usuario_id, inicio, fim)


def projecao_atividades(usuario_id, inicio, fim):
    return _Repo.projecao_atividades(usuario_id, inicio, fim)


def contagens_dashboard(contexto):
    return _Repo.contagens_dashboard(contexto)


__all__ = ['projecao_desempenho', 'projecao_atividades', 'contagens_dashboard']
