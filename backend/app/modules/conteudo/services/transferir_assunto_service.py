from sqlalchemy.exc import IntegrityError

from app.exceptions import (
    ConflitoError,
    DadosInvalidosError,
    RecursoNaoEncontradoError,
)
from app.modules.conteudo.models.assunto_transferencia import AssuntoTransferencia
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository
from app.modules.conteudo.services.catalogo_validacao import validar_id
from app.modules.conteudo.services.catalogo_validacao import validar_descricao, validar_nome
from app.modules.conteudo.domain.catalogo import normalizar_nome_assunto
from app.transaction_manager import TransactionManager


class TransferirAssuntoService:
    @staticmethod
    def previa(assunto_id, materia_destino_id):
        validar_id(materia_destino_id, "materia_destino_id")
        assunto = Assunto.buscar_por_id(assunto_id)
        if assunto is None:
            raise RecursoNaoEncontradoError("Assunto nao encontrado.")
        origem = Materia.buscar_por_id(assunto.materia_id)
        destino = Materia.buscar_por_id(materia_destino_id)
        if destino is None:
            raise RecursoNaoEncontradoError("Materia de destino nao encontrada.")
        if destino.id == assunto.materia_id:
            raise DadosInvalidosError("A materia de destino deve ser diferente da origem.")
        if destino.status != "ativa":
            raise DadosInvalidosError("A materia de destino precisa estar ativa.")
        if CatalogoRepository.existe_assunto_equivalente(
            destino.id,
            assunto.nome_normalizado,
            ignorar_id=assunto.id
        ):
            raise ConflitoError("Ja existe um assunto equivalente na materia de destino.")
        return {
            "assunto_id": assunto.id,
            "materia_origem": origem.to_dict(),
            "materia_destino": destino.to_dict(),
            "impacto": {
                "questoes": CatalogoRepository.impacto_assunto(assunto.id)["questoes"]
            },
        }

    @staticmethod
    def executar(assunto_id, dados, atualizacoes=None):
        if not isinstance(dados, dict):
            raise DadosInvalidosError("Envie os dados da transferencia em formato JSON.")
        destino_id = validar_id(dados.get("materia_destino_id"), "materia_destino_id")
        if atualizacoes is None:
            atualizacoes = {}
            if "nome" in dados:
                nome = validar_nome(dados["nome"], "do assunto", 150)
                atualizacoes.update(
                    {"nome": nome, "nome_normalizado": normalizar_nome_assunto(nome)}
                )
            if "descricao" in dados:
                atualizacoes["descricao"] = validar_descricao(dados["descricao"])
        esperado = dados.get("impacto_esperado")
        if (
            not isinstance(esperado, dict)
            or not isinstance(esperado.get("questoes"), int)
            or isinstance(esperado.get("questoes"), bool)
            or esperado["questoes"] < 0
        ):
            raise DadosInvalidosError("Informe impacto_esperado.questoes valido.")

        def operacao():
            assunto = CatalogoRepository.buscar_assunto_para_atualizacao(assunto_id)
            if assunto is None:
                raise RecursoNaoEncontradoError("Assunto nao encontrado.")
            materias = CatalogoRepository.buscar_materias_para_atualizacao(
                {assunto.materia_id, destino_id}
            )
            por_id = {materia.id: materia for materia in materias}
            origem = por_id.get(assunto.materia_id)
            destino = por_id.get(destino_id)
            if destino is None:
                raise RecursoNaoEncontradoError("Materia de destino nao encontrada.")
            if destino.id == assunto.materia_id:
                raise DadosInvalidosError("A materia de destino deve ser diferente da origem.")
            if destino.status != "ativa":
                raise DadosInvalidosError("A materia de destino precisa estar ativa.")
            nome_normalizado = atualizacoes.get(
                "nome_normalizado",
                assunto.nome_normalizado
            )
            if CatalogoRepository.existe_assunto_equivalente(
                destino.id,
                nome_normalizado,
                ignorar_id=assunto.id
            ):
                raise ConflitoError("Ja existe um assunto equivalente na materia de destino.")
            impacto = CatalogoRepository.impacto_assunto(assunto.id)["questoes"]
            previa = {
                "assunto_id": assunto.id,
                "materia_origem": origem.to_dict(),
                "materia_destino": destino.to_dict(),
                "impacto": {"questoes": impacto},
            }
            if impacto != esperado["questoes"]:
                raise ConflitoError(
                    "O impacto mudou; confirme novamente a transferencia.",
                    detalhes={"previa": previa},
                )
            origem_id = assunto.materia_id
            assunto.atualizar(
                confirmar=False,
                materia_id=destino.id,
                **atualizacoes
            )
            AssuntoTransferencia(
                assunto_id=assunto.id,
                materia_origem_id=origem_id,
                materia_destino_id=destino.id,
                questoes_impactadas=impacto,
            ).salvar(confirmar=False)
            return assunto.to_dict()

        try:
            return TransactionManager.executar(operacao)
        except IntegrityError as erro:
            raise ConflitoError(
                "Nao foi possivel transferir o assunto por conflito de integridade."
            ) from erro
