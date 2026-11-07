"""Validação do início de uma prática."""
from app.core.validacao import corpo, parametros, referencia


def inicio(dados):
    return referencia(dados, "questao_versao_id")
