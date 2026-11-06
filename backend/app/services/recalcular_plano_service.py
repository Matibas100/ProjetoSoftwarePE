from app.services.gerar_plano_service import gerar
from app.services.selecionar_plano_service import SelecionarPlanoService


class RecalcularPlanoService:
    def __init__(self, seletor: SelecionarPlanoService):
        self._seletor = seletor

    def executar(self, usuario_id, dados):
        return gerar(usuario_id, dados, self._seletor, recalcular=True)
