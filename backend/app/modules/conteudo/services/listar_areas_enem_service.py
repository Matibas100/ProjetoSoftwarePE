from app.modules.conteudo.models.area_enem import AreaEnem


class ListarAreasEnemService:
    @staticmethod
    def executar():
        return [area.to_dict() for area in AreaEnem.listar_ordenadas()]
