import re
import unicodedata


STATUS_CATALOGO = frozenset({"ativa", "inativa", "arquivada"})


def normalizar_nome_assunto(valor):
    if not isinstance(valor, str):
        raise ValueError("O nome do assunto deve ser um texto.")
    normalizado = unicodedata.normalize("NFC", valor)
    normalizado = re.sub(r"\s+", " ", normalizado.strip()).lower()
    if not normalizado:
        raise ValueError("O nome do assunto e obrigatorio.")
    if len(normalizado) > 150:
        raise ValueError("O nome deve possuir no maximo 150 caracteres.")
    return normalizado


def validar_status(status):
    if status not in STATUS_CATALOGO:
        raise ValueError("Status de catalogo invalido.")
    return status


def esta_disponivel(registro):
    return registro.status == "ativa"
