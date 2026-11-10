"""Resultados múltiplos na Connection SQLAlchemy emprestada, sem encerrá-la.

O chamador fornece SQL fixo e parâmetros vinculados. Conjuntos com colunas,
mesmo vazios, são úteis; o conjunto terminal do protocolo não é retornado.
Não há commit, rollback, criação de conexão ou conhecimento de domínio aqui.
"""


class ConjuntoResultado(list):
    """Linhas com a descrição disponível inclusive quando não há registros."""

    def __init__(self, colunas, linhas):
        self.colunas = tuple(colunas)
        super().__init__(dict(zip(self.colunas, linha)) for linha in linhas)


def executar_resultados(conexao, comando, parametros=()):
    cursor = conexao.connection.driver_connection.cursor()
    resultados = []
    try:
        cursor.execute(comando, parametros)
        while True:
            if cursor.description is not None:
                nomes = [coluna[0] for coluna in cursor.description]
                linhas = cursor.fetchall()
                resultados.append(ConjuntoResultado(nomes, linhas))
            try:
                seguinte = cursor.nextset()
            except Exception:
                conexao.invalidate()
                raise
            if not seguinte:
                break
        return resultados
    finally:
        try:
            # Também libera conjuntos pendentes se execute/fetchall falhar.
            while cursor.nextset():
                if cursor.description is not None:
                    cursor.fetchall()
        except Exception:
            conexao.invalidate()
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                conexao.invalidate()
                raise


def conferir_resultados(resultados, contratos):
    """Recusa número/colunas incompatíveis; contratos são definidos no Repository."""
    if len(resultados) != len(contratos):
        raise ValueError("Resultados SQL incompatíveis.")
    for linhas, colunas in zip(resultados, contratos):
        if len(linhas.colunas) != len(colunas) or set(linhas.colunas) != set(colunas):
            raise ValueError("Colunas SQL incompatíveis.")
    return resultados
