from app.contracts.simulados import ConsultaCatalogoSimulados
from app.contracts.questoes import ConsultaElegibilidadeVersoes
from app.core.paginacao import envelope_paginado
from app.modules.simulados.services.simulado_validacao import paginacao


class ListarSimuladosAlunoService:
    def __init__(
        self,
        consulta: ConsultaCatalogoSimulados,
        elegibilidade: ConsultaElegibilidadeVersoes
    ):
        self._consulta = consulta
        self._elegibilidade = elegibilidade

    def executar(self, usuario_id, filtros):
        valores, _ = paginacao(filtros)
        linhas, total = self._consulta.listar(valores['pagina'], valores['por_pagina'])
        versao_ids = [s['simulado_versao_id'] for s in linhas]
        composicoes = self._consulta.composicoes(versao_ids)
        elegiveis = self._elegibilidade.executar([id_ for grupo in composicoes.values() for id_ in grupo])
        andamentos = self._consulta.andamentos(usuario_id, versao_ids)
        itens = []
        for s in linhas:
            composicao = composicoes.get(s['simulado_versao_id'], [])
            disponivel = bool(composicao) and all(id_ in elegiveis for id_ in composicao)
            itens.append({
                **s,
                'total_questoes': len(composicao),
                'disponivel': disponivel,
                'tentativa_em_andamento_id': andamentos.get(s['simulado_versao_id'])
            })
        return envelope_paginado(itens, valores['pagina'], valores['por_pagina'], total)
