class HealthCheckService:
    """Caso de uso tecnico para confirmar que a API esta em execucao."""

    @staticmethod
    def executar():
        return {
            "aplicacao": "Plataforma ENEM",
            "status": "online",
        }
