from math import ceil

from app.domain.catalogo import STATUS_CATALOGO
from app.exceptions import DadosInvalidosError
from app.contracts.catalogo import ConsultaMateriasAdmin, ConsultaAssuntosAdmin


def _inteiro_filtro(valor, campo, minimo=1, maximo=None):
    if valor in (None, ""):
        return None
    try:
        numero = int(valor)
    except (TypeError, ValueError) as erro:
        raise DadosInvalidosError(f"{campo} deve ser um inteiro valido.") from erro
    if numero < minimo or (maximo is not None and numero > maximo):
        raise DadosInvalidosError(f"{campo} esta fora do intervalo permitido.")
    return numero


def _parametros(parametros):
    pagina = _inteiro_filtro(parametros.get("pagina", 1), "pagina")
    por_pagina = _inteiro_filtro(
        parametros.get("por_pagina", 20), "por_pagina", maximo=100
    )
    busca = (parametros.get("busca") or "").strip()
    if len(busca) > 100:
        raise DadosInvalidosError("A busca deve possuir no maximo 100 caracteres.")
    status = parametros.get("status") or None
    if status is not None and status not in STATUS_CATALOGO:
        raise DadosInvalidosError("Status de catalogo invalido.")
    return pagina, por_pagina, busca, status


def _envelope(itens, pagina, por_pagina, total):
    return {
        "itens": itens,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total_itens": total,
        "total_paginas": ceil(total / por_pagina) if total else 0,
    }


class ListarMateriasAdminService:
    def __init__(self, consulta: ConsultaMateriasAdmin):
        self._consulta = consulta

    def executar(self, parametros):
        pagina, por_pagina, busca, status = _parametros(parametros)
        filtros = {
            "busca": busca,
            "status": status,
            "area_enem_id": _inteiro_filtro(
                parametros.get("area_enem_id"), "area_enem_id"
            ),
        }
        itens, total = self._consulta.listar(
            filtros, pagina, por_pagina
        )
        return _envelope(itens, pagina, por_pagina, total)


class ListarAssuntosAdminService:
    def __init__(self, consulta: ConsultaAssuntosAdmin):
        self._consulta = consulta

    def executar(self, parametros):
        pagina, por_pagina, busca, status = _parametros(parametros)
        filtros = {
            "busca": busca,
            "status": status,
            "area_enem_id": _inteiro_filtro(
                parametros.get("area_enem_id"), "area_enem_id"
            ),
            "materia_id": _inteiro_filtro(parametros.get("materia_id"), "materia_id"),
        }
        linhas, total = self._consulta.listar(
            filtros, pagina, por_pagina
        )
        itens = [{**linha, 'resumos': None} for linha in linhas]
        return _envelope(itens, pagina, por_pagina, total)
