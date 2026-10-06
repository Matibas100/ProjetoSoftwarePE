class ErroAplicacao(Exception):
    """Erro esperado da aplicacao que pode ser convertido em resposta HTTP."""

    status_code = 500

    def __init__(self, mensagem, detalhes=None):
        super().__init__(mensagem)
        self.detalhes = detalhes

    def to_dict(self):
        resposta = {"erro": str(self)}
        if self.detalhes is not None:
            resposta["detalhes"] = self.detalhes
        return resposta


class DadosInvalidosError(ErroAplicacao):
    status_code = 400


class RecursoNaoEncontradoError(ErroAplicacao):
    status_code = 404


class ConflitoError(ErroAplicacao):
    status_code = 409
