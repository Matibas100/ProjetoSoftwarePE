"""Reservas atômicas por aplicação; guarda somente IDs, contagens e instantes."""
from dataclasses import dataclass
from math import ceil
from threading import Lock
from time import monotonic
from app.modules.tutor_ia.domain.tutoria import TutoriaError


@dataclass
class Janela:
    inicio: float
    tentativas: int = 0
    em_andamento: bool = False


class LimiteTutoria:
    def __init__(self, relogio=monotonic, capacidade=1024):
        self._relogio, self._capacidade = relogio, capacidade
        self._lock, self._contas, self._ativas = Lock(), {}, 0

    @staticmethod
    def _negar(espera=1):
        raise TutoriaError(
            'Limite de tutoria atingido. Aguarde antes de enviar novamente.',
            429,
            'limite_tutoria',
            max(1, ceil(espera))
        )

    def reservar(self, conta):
        with self._lock:
            agora = self._relogio()
            self._contas = {
                id_: j for id_,
                j in self._contas.items()
                if j.em_andamento or agora - j.inicio < 60
            }
            janela = self._contas.get(conta)
            if janela is not None and janela.em_andamento:
                self._negar()
            if self._ativas >= 2:
                self._negar()
            if janela is None:
                if len(self._contas) >= self._capacidade:
                    self._negar(min(j.inicio + 60 - agora for j in self._contas.values()))
                janela = Janela(agora)
                self._contas[conta] = janela
            if janela.tentativas >= 4:
                self._negar(janela.inicio + 60 - agora)
            janela.tentativas += 1
            janela.em_andamento = True
            self._ativas += 1

    def liberar(self, conta):
        with self._lock:
            janela = self._contas.get(conta)
            if janela is not None and janela.em_andamento:
                janela.em_andamento = False
                self._ativas -= 1
