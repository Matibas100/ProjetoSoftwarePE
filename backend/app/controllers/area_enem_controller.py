from app.http_response import responder_http
from app.services.listar_areas_enem_service import ListarAreasEnemService


class AreaEnemController:
    @staticmethod
    def listar():
        return responder_http(ListarAreasEnemService.executar,
            contexto="Falha interna: areas ENEM.")
