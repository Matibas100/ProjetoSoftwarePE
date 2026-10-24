from app.exceptions import DadosInvalidosError
from app.repositories.plano_estudo_repository import PlanoEstudoRepository as Repo
from app.repositories.questao_repository import QuestaoRepository


def item_dto(item, pares):
    return {"id": item.id, "posicao": item.posicao, "assunto_id": item.assunto_id, "materia_id": item.materia_id,
        "snapshot": item.snapshot, "estado": item.estado,
        "concluido_em": item.concluido_em.isoformat() + "Z" if item.concluido_em else None,
        "disponivel_para_pratica": (item.assunto_id, item.materia_id) in pares}


def plano_dto(plano):
    if plano is None:
        return None
    itens = Repo.itens(plano.id)
    pares = QuestaoRepository.pares_elegiveis_plano([i.assunto_id for i in itens])
    return {"id": plano.id, "geracao": plano.geracao, "atual": plano.atual, "periodo": plano.periodo,
        "gerado_em": plano.gerado_em.isoformat() + "Z", "itens": [item_dto(i, pares) for i in itens]}


class ConsultarPlanoService:
    @staticmethod
    def executar(usuario_id, filtros=None):
        if filtros:
            raise DadosInvalidosError("A consulta do plano não aceita filtros.")
        plano = Repo.atual(usuario_id)
        return {"estado": "disponivel" if plano else "sem_plano", "plano": plano_dto(plano)}
