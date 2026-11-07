from app.core.relogio import agora_utc
from app.exceptions import ConflitoError, RecursoNaoEncontradoError
from app.modules.plano_estudos.repositories.plano_estudo_repository import PlanoEstudoRepository as Repo
from app.modules.conteudo.api import pares_elegiveis_plano
from app.modules.plano_estudos.services.consultar_plano_service import item_dto
from app.modules.plano_estudos.services.plano_validacao import confirmacao
from app.transaction_manager import TransactionManager
from app.modules.contas.api import ValidarPermissaoPlanoService


class ConcluirPlanoItemService:
    @staticmethod
    def executar(usuario_id, item_id, dados):
        confirmacao(dados)

        def concluir():
            Repo.bloquear_usuario(usuario_id)
            ValidarPermissaoPlanoService.executar(usuario_id)
            linha = Repo.item_proprio(usuario_id, item_id)
            if linha is None:
                raise RecursoNaoEncontradoError("Item não encontrado.")
            item, plano = linha
            if not plano.atual:
                raise ConflitoError("Itens de planos anteriores não podem ser alterados.")
            if item.estado != "concluido":
                item.estado, item.concluido_em = "concluido", agora_utc()
                item.salvar(confirmar=False)
            pares = pares_elegiveis_plano([item.assunto_id])
            return item_dto(item, pares)

        return TransactionManager.executar(concluir)
