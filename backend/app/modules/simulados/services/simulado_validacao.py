"""Validação estrita de composição, revisões e paginação."""
from app.exceptions import DadosInvalidosError, ConflitoError
from app.core.validacao import corpo, parametros, referencia


def revisao(dados):
    valor = dados.get("revisao") if isinstance(dados, dict) else None
    if type(valor) is not int or not 1 <= valor <= 2147483647:
        raise DadosInvalidosError("Revisão deve ser um inteiro positivo.")
    return valor


def conferir_revisao(registro, valor):
    if registro.revisao != valor:
        raise ConflitoError("A revisão mudou. Recarregue antes de tentar novamente.")


def composicao(dados, editar=False):
    corpo(dados, {"titulo", "questao_versao_ids", *({"revisao"} if editar else set())})
    titulo, ids = dados["titulo"], dados["questao_versao_ids"]
    if not isinstance(titulo, str) or not 3 <= len(titulo.strip()) <= 150:
        raise DadosInvalidosError("Título deve ter de 3 a 150 caracteres.")
    if not isinstance(ids, list) or not 1 <= len(ids) <= 180 or any(type(i) is not int or not 1 <= i <= 2147483647 for i in ids):
        raise DadosInvalidosError("Selecione de 1 a 180 versões de Questões.")
    if len(set(ids)) != len(ids):
        raise DadosInvalidosError("Não repita Questões na composição.")
    return titulo.strip(), ids


def paginacao(filtros, admin=False):
    estado = filtros.get("status") if admin else None
    if admin and "status" in filtros and estado not in {"rascunho", "publicado", "arquivado"}:
        raise DadosInvalidosError("Estado inválido.")
    # Remover status somente depois de verificar parâmetros repetidos.
    if hasattr(filtros, "getlist") and any(len(filtros.getlist(k)) != 1 for k in filtros):
        raise DadosInvalidosError("Filtro repetido.")
    copia = dict(filtros)
    if admin:
        copia.pop("status", None)
    return parametros(copia, set()), estado


def inicio_simulado(dados):
    corpo(dados, {"simulado_versao_id", "chave_envio"})
    return referencia(dados, "simulado_versao_id")
