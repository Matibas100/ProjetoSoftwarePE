from app.contracts.simulados import ConsultaHistoricoSimulados
from app.core.paginacao import envelope_paginado
from app.modules.simulados.services.simulado_validacao import paginacao


class ListarHistoricoSimuladosService:
    def __init__(self, consulta: ConsultaHistoricoSimulados):
        self._consulta = consulta

    def executar(self, usuario_id, filtros):
        valores, _ = paginacao(filtros)
        linhas, total = self._consulta.listar(usuario_id, valores['pagina'], valores['por_pagina'])
        return envelope_paginado(linhas, valores['pagina'], valores['por_pagina'], total)
