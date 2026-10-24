"""Validação dos contratos de prática."""
from uuid import UUID
from app.exceptions import DadosInvalidosError
from app.services.listar_catalogo_admin_service import _inteiro_filtro


def parametros(parametros, filtros):
    permitidos = {"pagina", "por_pagina", *filtros}
    repetidos = hasattr(parametros, "getlist") and any(len(parametros.getlist(k)) != 1 for k in parametros)
    if set(parametros) - permitidos or repetidos:
        raise DadosInvalidosError("Filtro desconhecido ou repetido.")
    valores = {}
    for campo in permitidos:
        padrao = "1" if campo == "pagina" else "20" if campo == "por_pagina" else None
        valor = parametros.get(campo, padrao)
        if (valor is not None or campo in parametros) and (not isinstance(valor, str) or len(valor) > 10 or not valor.isascii() or not valor.isdecimal()):
            raise DadosInvalidosError(f"{campo} deve ser um inteiro positivo.")
        valores[campo] = _inteiro_filtro(valor, campo, maximo=100 if campo == "por_pagina" else 2147483647)
    return valores


def corpo(dados, campos):
    if not isinstance(dados, dict) or set(dados) != set(campos):
        raise DadosInvalidosError("Informe somente os campos obrigatórios.")


def inicio(dados):
    corpo(dados, {"questao_versao_id", "chave_envio"})
    versao_id = dados["questao_versao_id"]
    if type(versao_id) is not int or not 1 <= versao_id <= 2147483647:
        raise DadosInvalidosError("Versão deve ser um inteiro positivo.")
    chave = dados["chave_envio"]
    try:
        if not isinstance(chave, str) or len(chave) != 36:
            raise ValueError()
        normalizada = str(UUID(chave))
        if chave.lower() != normalizada:
            raise ValueError()
    except ValueError as erro:
        raise DadosInvalidosError("Chave de envio deve ser UUID.") from erro
    return versao_id, normalizada
