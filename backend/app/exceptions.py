class ErroAplicacao(Exception):
    """Erro esperado da aplicacao que pode ser convertido em resposta HTTP."""

    status_code = 500


class DadosInvalidosError(ErroAplicacao):
    status_code = 400


class RecursoNaoEncontradoError(ErroAplicacao):
    status_code = 404


class ConflitoError(ErroAplicacao):
    status_code = 409
