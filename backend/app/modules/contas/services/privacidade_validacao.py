"""Validações e serialização comuns às decisões explícitas de privacidade."""
from uuid import UUID

from app.modules.contas.domain.autenticacao import AutenticacaoError, validar_dados
from app.modules.contas.domain.privacidade import documento_vigente, estado_privacidade, registro_dto


def conflito_decisao():
    return AutenticacaoError("A decisão mudou. Consulte a privacidade antes de decidir novamente.", 409, "decisao_desatualizada")


def validar_corpo(dados, negativa=False):
    campos = {"versao", "chave_envio", "revisao"} | ({"confirmar"} if negativa else set())
    validar_dados(dados, campos)
    if (not isinstance(dados["versao"], str) or not 1 <= len(dados["versao"]) <= 20
            or type(dados["revisao"]) is not int or not 0 <= dados["revisao"] <= 9223372036854775807
            or (negativa and dados["confirmar"] is not True)):
        raise AutenticacaoError("Confira a versão, revisão e confirmação.")
    try:
        if not isinstance(dados["chave_envio"], str) or str(UUID(dados["chave_envio"])) != dados["chave_envio"]:
            raise ValueError()
    except (ValueError, AttributeError):
        raise AutenticacaoError("Informe uma chave UUID canônica.") from None
    return dados


def validar_versao(tipo, versao):
    doc = documento_vigente(tipo)
    if versao != doc["versao"]:
        raise AutenticacaoError("O documento mudou. Leia a versão vigente e confirme novamente.", 409, "termo_desatualizado")
    return doc


def validar_revisao(registro, revisao):
    if revisao != (registro.id if registro else 0):
        raise conflito_decisao()


def resposta_reenvio(registro, dados, tipo, acao, registros):
    if (registro.tipo, registro.acao, registro.versao, registro.revisao_base) != (
            tipo, acao, dados["versao"], dados["revisao"]):
        raise conflito_decisao()
    return {"registro": registro_dto(registro), "privacidade": estado_privacidade(registros)}, 200


def resposta_nova(registro, registros):
    registros[registro.tipo] = registro
    return {"registro": registro_dto(registro), "privacidade": estado_privacidade(registros)}, 201
