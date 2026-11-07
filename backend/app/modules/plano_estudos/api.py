"""Participante interno de eliminação, sem endpoint nem transação própria."""
from app.modules.plano_estudos.services.eliminar_planos_proprios_service import EliminarPlanosPropriosService as _Eliminar

EliminarPlanosPropriosService = _Eliminar
__all__ = ['EliminarPlanosPropriosService']
