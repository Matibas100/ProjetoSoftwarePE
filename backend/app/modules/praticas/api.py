"""Projeções de leitura do proprietário para agregação consistente."""
from app.modules.praticas.repositories.pratica_repository import PraticaRepository as _Repo



def projecao_desempenho(usuario_id, inicio, fim):
    return _Repo.projecao_desempenho(usuario_id, inicio, fim)


def projecao_atividades(usuario_id, inicio, fim):
    return _Repo.projecao_atividades(usuario_id, inicio, fim)


__all__ = ['projecao_desempenho', 'projecao_atividades']
