from sqlalchemy import text

from app.extensions import db


class QuestaoRepository:
    """Executa a consulta especializada de Questoes por Assunto."""

    @staticmethod
    def buscar_por_assunto(assunto_id):
        resultado = db.session.execute(
            text("CALL sp_questoes_por_assunto(:assunto_id)"),
            {"assunto_id": assunto_id},
        )
        try:
            return [dict(linha) for linha in resultado.mappings().all()]
        finally:
            resultado.close()
