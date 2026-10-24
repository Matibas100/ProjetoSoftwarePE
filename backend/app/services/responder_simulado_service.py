from app.exceptions import DadosInvalidosError, ConflitoError, RecursoNaoEncontradoError
from app.services.pratica_validacao import corpo
from app.services.simulado_validacao import revisao, conferir_revisao
from app.services.consultar_simulado_service import propria
from app.repositories.simulado_repository import SimuladoRepository as Repo
from app.transaction_manager import TransactionManager


class ResponderSimuladoService:
    @staticmethod
    def executar(usuario_id, tentativa_id, item_id, dados):
        corpo(dados, {"alternativa", "revisao"})
        valor = revisao(dados); alternativa = dados["alternativa"]
        if alternativa is not None and (not isinstance(alternativa, str) or alternativa not in {"A", "B", "C", "D", "E"}):
            raise DadosInvalidosError("Alternativa deve ser A–E ou null.")
        def operacao():
            t = propria(usuario_id, tentativa_id, bloquear=True)
            resposta = next((r for r, i in Repo.respostas(t.id, bloquear=True) if i.id == item_id), None)
            if resposta is None:
                raise RecursoNaoEncontradoError("Item não encontrado.")
            if t.estado != "em_andamento":
                raise ConflitoError("Tentativa já finalizada.")
            conferir_revisao(t, valor)
            resposta.alternativa = alternativa; resposta.salvar(confirmar=False)
            t.revisao += 1; t.salvar(confirmar=False)
            return {"item_id": item_id, "alternativa": alternativa, "revisao": t.revisao}
        return TransactionManager.executar(operacao)
