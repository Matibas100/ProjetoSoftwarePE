from app.services.gerar_plano_service import gerar


class RecalcularPlanoService:
    @staticmethod
    def executar(usuario_id, dados):
        return gerar(usuario_id, dados, recalcular=True)
