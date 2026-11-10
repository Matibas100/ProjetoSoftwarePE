from typing import Iterable, Protocol, TypedDict


class SimuladoCatalogoRegistro(TypedDict):
    id: int
    simulado_versao_id: int
    titulo: str


class ResultadoSimulado(TypedDict):
    total: int
    respondidas: int
    acertos: int
    erros: int
    em_branco: int
    percentual_acerto: float
    finalizada_em: str


class HistoricoSimuladoRegistro(SimuladoCatalogoRegistro):
    resultado: ResultadoSimulado


class ConsultaCatalogoSimulados(Protocol):
    def listar(self, pagina: int, limite: int) -> tuple[list[SimuladoCatalogoRegistro], int]:
        ...

    def composicoes(self, versao_ids: Iterable[int]) -> dict[int, list[int]]:
        ...

    def andamentos(self, usuario_id: int, versao_ids: Iterable[int]) -> dict[int, int]:
        ...


class ConsultaHistoricoSimulados(Protocol):
    def listar(
        self,
        usuario_id: int,
        pagina: int,
        limite: int
    ) -> tuple[
        list[HistoricoSimuladoRegistro],
        int
    ]:
        ...
