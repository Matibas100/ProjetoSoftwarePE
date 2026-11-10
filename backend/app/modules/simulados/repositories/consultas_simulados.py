from typing import Iterable
from app.contracts.simulados import HistoricoSimuladoRegistro, SimuladoCatalogoRegistro
from app.modules.simulados.repositories.simulado_repository import SimuladoRepository


class ConsultaCatalogoSimuladosMySQL:
    def listar(self, pagina: int, limite: int) -> tuple[list[SimuladoCatalogoRegistro], int]:
        linhas, total = SimuladoRepository.listar(pagina, limite, 'publicado')
        return [{'id': s.id, 'simulado_versao_id': s.simulado_versao_id, 'titulo': s.titulo}
            for s in linhas], total

    def composicoes(self, versao_ids: Iterable[int]) -> dict[int, list[int]]:
        return {
            id_: [i.questao_versao_id for i in itens] for id_,
            itens in
            SimuladoRepository.itens_em_lote(versao_ids=versao_ids).items()
        }

    def andamentos(self, usuario_id: int, versao_ids: Iterable[int]) -> dict[int, int]:
        return {
            id_: t.id for id_,
            t in SimuladoRepository.andamentos_em_lote(
                usuario_id,
                versao_ids
            ).items()
        }


class ConsultaHistoricoSimuladosMySQL:
    def listar(
        self,
        usuario_id: int,
        pagina: int,
        limite: int
    ) -> tuple[
        list[HistoricoSimuladoRegistro],
        int
    ]:
        linhas, total = SimuladoRepository.historico(usuario_id, pagina, limite)
        titulos = SimuladoRepository.titulos_em_lote({t.simulado_versao_id for t in linhas})
        return [{
            'id': t.id,
            'simulado_versao_id': t.simulado_versao_id,
            'titulo': titulos[t.simulado_versao_id],
            'resultado': t.resultado()
        }
            for t in linhas], total
