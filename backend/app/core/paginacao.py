from math import ceil

from app.exceptions import DadosInvalidosError


def inteiro_filtro(valor, campo, minimo=1, maximo=None):
    if valor in (None, ""):
        return None
    try:
        numero = int(valor)
    except (TypeError, ValueError) as erro:
        raise DadosInvalidosError(f"{campo} deve ser um inteiro valido.") from erro
    if numero < minimo or (maximo is not None and numero > maximo):
        raise DadosInvalidosError(f"{campo} esta fora do intervalo permitido.")
    return numero


def envelope_paginado(itens, pagina, por_pagina, total):
    return {
        "itens": itens,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total_itens": total,
        "total_paginas": ceil(total / por_pagina) if total else 0,
    }
