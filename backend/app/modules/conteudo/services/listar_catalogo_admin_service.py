from app.modules.conteudo.domain.catalogo import STATUS_CATALOGO
from app.exceptions import DadosInvalidosError
from app.contracts.catalogo import ConsultaMateriasAdmin, ConsultaAssuntosAdmin
from app.core.paginacao import inteiro_filtro, envelope_paginado


def _parametros(parametros):
    pagina = inteiro_filtro(parametros.get("pagina", 1), "pagina")
    por_pagina = inteiro_filtro(
        parametros.get("por_pagina", 20), "por_pagina", maximo=100
    )
    busca = (parametros.get("busca") or "").strip()
    if len(busca) > 100:
        raise DadosInvalidosError("A busca deve possuir no maximo 100 caracteres.")
    status = parametros.get("status") or None
    if status is not None and status not in STATUS_CATALOGO:
        raise DadosInvalidosError("Status de catalogo invalido.")
    return pagina, por_pagina, busca, status


class ListarMateriasAdminService:
    def __init__(self, consulta: ConsultaMateriasAdmin):
        self._consulta = consulta

    def executar(self, parametros):
        pagina, por_pagina, busca, status = _parametros(parametros)
        filtros = {
            "busca": busca,
            "status": status,
            "area_enem_id": inteiro_filtro(
                parametros.get("area_enem_id"), "area_enem_id"
            ),
        }
        itens, total = self._consulta.listar(
            filtros, pagina, por_pagina
        )
        return envelope_paginado(itens, pagina, por_pagina, total)


class ListarAssuntosAdminService:
    def __init__(self, consulta: ConsultaAssuntosAdmin):
        self._consulta = consulta

    def executar(self, parametros):
        pagina, por_pagina, busca, status = _parametros(parametros)
        filtros = {
            "busca": busca,
            "status": status,
            "area_enem_id": inteiro_filtro(
                parametros.get("area_enem_id"), "area_enem_id"
            ),
            "materia_id": inteiro_filtro(parametros.get("materia_id"), "materia_id"),
        }
        linhas, total = self._consulta.listar(
            filtros, pagina, por_pagina
        )
        itens = [{**linha, 'resumos': None} for linha in linhas]
        return envelope_paginado(itens, pagina, por_pagina, total)
