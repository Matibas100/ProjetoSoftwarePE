from uuid import UUID
from app.exceptions import DadosInvalidosError
from app.core.validacao import corpo


def confirmacao(dados):
    corpo(dados, {"confirmar"})
    if dados["confirmar"] is not True:
        raise DadosInvalidosError("Confirmação explícita obrigatória.")


def operacao(dados, recalcular=False):
    corpo(dados, {"chave_envio", "plano_atual_id", "confirmar"} if recalcular else {"chave_envio"})
    chave = dados["chave_envio"]
    try:
        if not isinstance(chave, str) or len(chave) != 36 or chave.lower() != str(UUID(chave)):
            raise ValueError()
    except ValueError as erro:
        raise DadosInvalidosError("Chave de envio deve ser UUID.") from erro
    anterior = dados.get("plano_atual_id")
    if recalcular:
        confirmacao({"confirmar": dados["confirmar"]})
        if type(anterior) is not int or not 1 <= anterior <= 9223372036854775807:
            raise DadosInvalidosError("Plano atual deve ser um inteiro positivo.")
    return chave.lower(), anterior
