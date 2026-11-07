"""Diagnóstico público pelo mesmo contrato injetado no plano."""
from app.modules.desempenho.services.consultar_desempenho_service import ConsultarDesempenhoService as _Diagnostico

ConsultarDesempenhoService = _Diagnostico
__all__ = ['ConsultarDesempenhoService']
