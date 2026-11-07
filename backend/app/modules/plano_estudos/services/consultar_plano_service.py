from app.exceptions import DadosInvalidosError
from app.modules.plano_estudos.repositories.plano_estudo_repository import PlanoEstudoRepository as Repo
from app.modules.conteudo.api import pares_elegiveis_plano
from app.modules.contas.api import ValidarPermissaoPlanoService
from app.transaction_manager import TransactionManager


def item_dto(item, pares):
    return {"id": item.id, "posicao": item.posicao, "assunto_id": item.assunto_id, "materia_id": item.materia_id,
        "snapshot": item.snapshot, "estado": item.estado,
        "concluido_em": item.concluido_em.isoformat() + "Z" if item.concluido_em else None,
        "disponivel_para_pratica": (item.assunto_id, item.materia_id) in pares}


def plano_dto(plano):
    if plano is None:
        return None
    itens = Repo.itens(plano.id)
    pares = pares_elegiveis_plano([i.assunto_id for i in itens])
    return {"id": plano.id, "geracao": plano.geracao, "atual": plano.atual, "periodo": plano.periodo,
        "gerado_em": plano.gerado_em.isoformat() + "Z", "itens": [item_dto(i, pares) for i in itens]}


class ConsultarPlanoService:
    @staticmethod
    def executar(usuario_id, filtros=None):
        if filtros:
            raise DadosInvalidosError("A consulta do plano não aceita filtros.")
        def consultar():
            Repo.bloquear_usuario(usuario_id)
            ValidarPermissaoPlanoService.executar(usuario_id)
            plano = Repo.atual(usuario_id, bloquear=True)
            return {"estado": "disponivel" if plano else "sem_plano", "plano": plano_dto(plano)}
        return TransactionManager.executar(consultar)
