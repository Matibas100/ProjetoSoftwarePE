from app.domain.privacidade import documento_vigente


class ConsultarTermosService:
    @staticmethod
    def executar():
        return {"termos_uso": documento_vigente("uso"), "consentimento_plano": documento_vigente("plano")}
