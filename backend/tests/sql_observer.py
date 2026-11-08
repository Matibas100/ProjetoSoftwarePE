"""Instrumentação do driver real para barreiras/falhas, sem substituir resultados.

CALL usa cursor DBAPI diretamente e não passa pelos eventos de execução ORM.
Os callbacks acompanham o mesmo SQL real, inclusive em conexões concorrentes.
"""
from sqlalchemy import event

_observadores = {}


def listen(engine, fase, callback):
    originais = {}

    def configurar(driver, registro, proxy):
        if driver in originais:
            return
        original = driver.cursorclass
        originais[driver] = original

        class CursorObservado(original):
            def execute(self, comando, parametros=None):
                argumentos = (None, self, comando, parametros, None, False)
                if fase == 'before_cursor_execute':
                    callback(*argumentos)
                resultado = super().execute(comando, parametros)
                if fase == 'after_cursor_execute':
                    callback(*argumentos)
                return resultado

        driver.cursorclass = CursorObservado

    _observadores[engine, fase, callback] = (configurar, originais)
    if hasattr(engine, 'pool'):
        event.listen(engine, 'checkout', configurar)
    else:
        configurar(engine.connection.driver_connection, None, None)


def remove(engine, fase, callback):
    configurar, originais = _observadores.pop((engine, fase, callback))
    if hasattr(engine, 'pool'):
        event.remove(engine, 'checkout', configurar)
    for driver, original in originais.items():
        driver.cursorclass = original
