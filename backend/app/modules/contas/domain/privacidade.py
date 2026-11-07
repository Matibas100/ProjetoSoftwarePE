"""Versões publicadas e estado das decisões, sem acesso a arquivos ou banco."""

DOCUMENTOS = {
    "uso": {"1.0": {"versao": "1.0", "url": "/legal/termo-de-uso-v1.html",
        "sha256": "e5bcdf3f002508592ee44a3e4cea2ec6dafcbe172a6e28996c2a105232cd9dd5"}},
    "plano": {"1.0": {"versao": "1.0", "url": "/legal/termo-de-consentimento-plano-v1.html",
        "sha256": "6233efccc924f73474e3c9b724f05d30729d55ae7fb177f6c47d3282d1d7b233"}},
}
VIGENTES = {"uso": "1.0", "plano": "1.0"}


def documento_vigente(tipo):
    return dict(DOCUMENTOS[tipo][VIGENTES[tipo]])


def registro_dto(registro):
    if registro is None:
        return None
    return {"id": registro.id, "acao": registro.acao, "versao": registro.versao,
        "documento_sha256": registro.documento_sha256,
        "registrado_em": registro.registrado_em.isoformat() + "Z"}


def aceite_vigente(registro, tipo):
    doc = documento_vigente(tipo)
    return bool(registro is not None and registro.acao == "aceitar"
        and registro.versao == doc["versao"] and registro.documento_sha256 == doc["sha256"])


def estado_privacidade(registros):
    uso, plano = registros.get("uso"), registros.get("plano")
    uso_atual, plano_atual = aceite_vigente(uso, "uso"), aceite_vigente(plano, "plano")
    estado = "nao_informado" if plano is None else (
        "aceito" if plano_atual else "desatualizado" if plano.acao == "aceitar"
        else {"recusar": "recusado", "revogar": "revogado"}[plano.acao])
    return {"termos_uso": {"versao_vigente": VIGENTES["uso"],
            "documento_url": documento_vigente("uso")["url"], "registro": registro_dto(uso), "aceite_vigente": uso_atual},
        "consentimento_plano": {"versao_vigente": VIGENTES["plano"],
            "documento_url": documento_vigente("plano")["url"], "registro": registro_dto(plano), "estado": estado},
        "plano_liberado": uso_atual and plano_atual}
