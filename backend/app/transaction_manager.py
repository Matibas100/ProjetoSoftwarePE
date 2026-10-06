from app.extensions import db


class TransactionManager:
    """Confirma ou reverte um caso de uso composto em uma unica fronteira."""

    @staticmethod
    def executar(operacao):
        sessao = db.session()
        try:
            if not sessao.in_transaction():
                sessao.begin()
            resultado = operacao()
            sessao.commit()
            return resultado
        except Exception:
            sessao.rollback()
            raise
