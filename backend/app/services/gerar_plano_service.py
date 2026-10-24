from app.domain.autenticacao import agora_utc
from app.exceptions import ConflitoError
from app.models.plano_estudo import PlanoEstudo, PlanoEstudoItem
from app.repositories.plano_estudo_repository import PlanoEstudoRepository as Repo
from app.services.consultar_plano_service import plano_dto
from app.services.plano_validacao import operacao
from app.services.selecionar_plano_service import SelecionarPlanoService
from app.transaction_manager import TransactionManager


def gerar(usuario_id, dados, recalcular=False):
    chave, anterior_id = operacao(dados, recalcular)
    tipo = "recalcular" if recalcular else "gerar"

    def executar():
        Repo.bloquear_usuario(usuario_id)
        existente = Repo.por_chave(usuario_id, chave)
        if existente is not None:
            if existente.operacao != tipo or existente.plano_anterior_id != anterior_id:
                raise ConflitoError("Chave já utilizada para outra operação ou plano.")
            return {"estado": "disponivel", "plano": plano_dto(existente)}, 200
        atual = Repo.atual(usuario_id, bloquear=True)
        if recalcular:
            if atual is None or atual.id != anterior_id:
                raise ConflitoError("O plano atual mudou. Consulte o plano antes de recalcular.")
        elif atual is not None:
            raise ConflitoError("Já existe um plano. Consulte-o ou confirme o recálculo.")
        instante = agora_utc()
        with Repo.contexto(instante) as contexto:
            periodo, itens = SelecionarPlanoService.executar(usuario_id, contexto, instante)
        if not itens:
            return {"estado": "sem_base_suficiente", "plano": plano_dto(atual)}, 200
        # Seleção pronta antes de desativar; qualquer falha reverte toda a troca.
        if atual is not None:
            atual.atual = False
            atual.salvar(confirmar=False)
        plano = PlanoEstudo(usuario_id=usuario_id, geracao=atual.geracao + 1 if atual else 1,
            atual=True, periodo=periodo, gerado_em=instante, chave_envio=chave, operacao=tipo,
            plano_anterior_id=anterior_id).salvar(confirmar=False)
        for snapshot in itens:
            PlanoEstudoItem(plano_id=plano.id, assunto_id=snapshot["assunto_id"], materia_id=snapshot["materia_id"],
                posicao=snapshot["posicao"], snapshot=snapshot, estado="pendente").salvar(confirmar=False)
        return {"estado": "disponivel", "plano": plano_dto(plano)}, 201

    return TransactionManager.executar(executar)


class GerarPlanoService:
    @staticmethod
    def executar(usuario_id, dados):
        return gerar(usuario_id, dados)
