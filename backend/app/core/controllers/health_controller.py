from flask import jsonify

from app.core.services.health_check_service import HealthCheckService


class HealthController:
    """Adapta a requisicao HTTP de saude para o respectivo caso de uso."""

    @staticmethod
    def status():
        resultado = HealthCheckService.executar()
        return jsonify(resultado), 200
