from app.contracts.questoes import ConsultaQuestoesElegiveis
from app.services.listar_catalogo_admin_service import _envelope
from app.services.pratica_validacao import parametros


class ListarQuestoesAlunoService:
    def __init__(self, consulta: ConsultaQuestoesElegiveis):
        self._consulta = consulta

    def executar(self, filtros):
        valores = parametros(filtros, {"materia_id", "assunto_id"})
        pagina, limite = valores.pop("pagina"), valores.pop("por_pagina")
        registros, total = self._consulta.listar(valores, pagina, limite)
        return _envelope(registros, pagina, limite, total)
