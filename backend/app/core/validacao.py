"""Validação pura de forma; políticas permanecem nos proprietários."""
from uuid import UUID
from app.exceptions import DadosInvalidosError
from app.core.paginacao import inteiro_filtro


def parametros(parametros, filtros):
    permitidos = {"pagina", "por_pagina", *filtros}
    repetidos = hasattr(
        parametros,
        "getlist"
    ) and any(len(parametros.getlist(k)) != 1 for k in parametros)
    if set(parametros) - permitidos or repetidos:
        raise DadosInvalidosError("Filtro desconhecido ou repetido.")
    valores = {}
    for campo in permitidos:
        padrao = "1" if campo == "pagina" else "20" if campo == "por_pagina" else None
        valor = parametros.get(campo, padrao)
        if (valor is not None or campo in parametros) and (not isinstance(
            valor,
            str
        ) or len(valor) > 10 or not valor.isascii() or not valor.isdecimal()):
            raise DadosInvalidosError(f"{campo} deve ser um inteiro positivo.")
        valores[campo] = inteiro_filtro(
            valor,
            campo,
            maximo=100 if campo == "por_pagina" else 2147483647
        )
    return valores


def corpo(dados, campos):
    if not isinstance(dados, dict) or set(dados) != set(campos):
        raise DadosInvalidosError("Informe somente os campos obrigatórios.")


def referencia(dados, campo):
    corpo(dados, {campo, "chave_envio"})
    versao_id = dados[campo]
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


def revisao_editorial(dados):
    if not isinstance(dados, dict):
        raise DadosInvalidosError("Envie um objeto JSON.")
    valor = dados.get("revisao")
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < 1:
        raise DadosInvalidosError("Revisão deve ser um inteiro positivo.")
    return valor


def confirmacao_editorial(dados):
    revisao = revisao_editorial(dados)
    if set(dados) != {"revisao", "confirmar", "motivo"} or dados.get("confirmar") is not True:
        raise DadosInvalidosError("Informe revisão, confirmação explícita e motivo.")
    motivo = dados.get("motivo")
    if not isinstance(motivo, str) or not 3 <= len(motivo.strip()) <= 500:
        raise DadosInvalidosError("Motivo deve ter de 3 a 500 caracteres.")
    return revisao, motivo.strip()
