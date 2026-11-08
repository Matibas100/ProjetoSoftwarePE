"""Snapshot MySQL próprio ou participação opaca em transação autorizada."""
from contextlib import contextmanager
from datetime import datetime, timezone
from app.core.relogio import agora_utc
from app.extensions import db
from app.core.procedures_mysql import executar_resultados


def utc(instante):
    if not isinstance(instante, datetime):
        raise ValueError("Relógio de leitura inválido.")
    return instante.astimezone(timezone.utc).replace(tzinfo=None) if instante.tzinfo else instante


class ContextoLeitura:
    def __init__(self, conexao=None, instante=None):
        self._conexao = conexao
        self.instante = utc(instante if instante is not None else agora_utc())
        self._proprio = conexao is None
        self._ativo = False

    def validar(self, instante=None):
        if not self._ativo or self._conexao.closed or not self._conexao.in_transaction():
            raise ValueError("Contexto de leitura inativo.")
        if self._conexao.get_isolation_level().upper() != "REPEATABLE READ":
            raise ValueError("A leitura exige REPEATABLE READ.")
        if instante is not None and utc(instante) != self.instante:
            raise ValueError("O relógio deve ser o mesmo da transação externa.")

    def __enter__(self):
        if self._ativo:
            raise ValueError("Contexto já aberto.")
        try:
            if self._proprio:
                self._conexao = db.engine.connect().execution_options(isolation_level="REPEATABLE READ")
                self._conexao.exec_driver_sql("START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY")
            self._ativo = True
            self.validar()
            return self
        except Exception:
            self._ativo = False
            if self._proprio and self._conexao is not None:
                self._conexao.close()
            raise

    def executar(self, consulta):
        self.validar()
        return self._conexao.execute(consulta)

    def executar_resultados(self, comando, parametros=()):
        self.validar()
        return executar_resultados(self._conexao, comando, parametros)

    def __exit__(self, *erro):
        self._ativo = False
        if self._proprio:
            self._conexao.close()

    @staticmethod
    @contextmanager
    def usar(contexto=None, instante=None):
        if contexto is not None:
            if not isinstance(contexto, ContextoLeitura):
                raise ValueError("Contexto externo inválido.")
            contexto.validar(instante)
            yield contexto
        else:
            with ContextoLeitura(instante=instante) as novo:
                yield novo
