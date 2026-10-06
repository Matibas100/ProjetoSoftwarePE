from app.domain.catalogo import validar_status
from app.exceptions import DadosInvalidosError


def validar_id(valor, campo):
    if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
        raise DadosInvalidosError(f"{campo} deve ser um numero inteiro valido.")
    return valor


def validar_nome(valor, recurso, limite):
    if not isinstance(valor, str) or not valor.strip():
        raise DadosInvalidosError(f"O nome {recurso} e obrigatorio.")
    nome = valor.strip()
    if len(nome) > limite:
        raise DadosInvalidosError(f"O nome deve possuir no maximo {limite} caracteres.")
    return nome


def validar_descricao(valor):
    if valor is not None and not isinstance(valor, str):
        raise DadosInvalidosError("A descricao deve ser um texto ou nula.")
    return valor.strip() if isinstance(valor, str) else None


def validar_status_catalogo(valor):
    try:
        return validar_status(valor)
    except ValueError as erro:
        raise DadosInvalidosError(str(erro)) from erro
