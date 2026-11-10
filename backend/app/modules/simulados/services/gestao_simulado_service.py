"""Casos de uso administrativos da composição manual fixa."""
from app.core.validacao import confirmacao_editorial as _confirmacao
from app.core.relogio import agora_utc
from app.exceptions import DadosInvalidosError, ConflitoError, RecursoNaoEncontradoError
from app.modules.simulados.models.simulado import (
    Simulado,
    SimuladoRascunhoItem,
    SimuladoVersao,
    SimuladoVersaoItem,
    SimuladoEvento,
)
from app.modules.simulados.repositories.simulado_repository import SimuladoRepository as Repo
from app.modules.conteudo.api import ConsultarVersaoElegivelService, ConsultarVersaoHistoricaService
from app.core.paginacao import envelope_paginado
from app.modules.simulados.services.simulado_validacao import (
    composicao,
    revisao,
    conferir_revisao,
    paginacao,
)
from app.transaction_manager import TransactionManager


def exigir(simulado):
    if simulado is None:
        raise RecursoNaoEncontradoError("Simulado não encontrado.")
    return simulado


def detalhe(simulado, itens=None):
    if itens is None:
        itens = Repo.itens(versao_id=simulado.simulado_versao_id) if simulado.simulado_versao_id else Repo.itens(simulado_id=simulado.id)
    return {
        "id": simulado.id,
        "titulo": simulado.titulo,
        "estado": simulado.estado,
        "revisao": simulado.revisao,
        "simulado_versao_id": simulado.simulado_versao_id,
        "itens": [{"posicao": i.posicao, "questao_versao_id": i.questao_versao_id} for i in itens]
    }


def elegiveis(ids):
    identidades = [ConsultarVersaoHistoricaService.executar(i)["questao_id"] for i in ids]
    if len(set(identidades)) != len(ids):
        raise DadosInvalidosError("Versões da mesma Questão não podem coexistir.")
    versoes = []
    # Bloqueio na fronteira de Questões protege elegibilidade contra retirada concorrente.
    for id_ in sorted(ids):
        versoes.append(ConsultarVersaoElegivelService.executar(id_, bloquear=True))
    por_id = {v["questao_versao_id"]: v for v in versoes}
    if len({v["questao_id"] for v in versoes}) != len(ids):
        raise DadosInvalidosError("Versões da mesma Questão não podem coexistir.")
    return [por_id[i] for i in ids]


def evento(simulado, ator_id, acao, motivo, instante, versao_id=None):
    SimuladoEvento(
        simulado_id=simulado.id,
        versao_id=versao_id,
        ator_id=ator_id,
        acao=acao,
        motivo=motivo,
        criado_em=instante
    ).salvar(confirmar=False)


class ListarSimuladosAdminService:
    @staticmethod
    def executar(filtros):
        valores, estado = paginacao(filtros, admin=True)
        linhas, total = Repo.listar(valores["pagina"], valores["por_pagina"], estado)
        rascunhos = Repo.itens_em_lote(simulado_ids=[s.id for s in linhas if not s.simulado_versao_id])
        publicados = Repo.itens_em_lote(versao_ids=[s.simulado_versao_id for s in linhas if s.simulado_versao_id])
        return envelope_paginado(
            [detalhe(
                s,
                publicados.get(
                    s.simulado_versao_id,
                    []
                ) if s.simulado_versao_id
                else rascunhos.get(
                    s.id,
                    []
                )
            ) for s in linhas],
            valores["pagina"],
            valores["por_pagina"],
            total
        )


class ConsultarSimuladoAdminService:
    @staticmethod
    def executar(simulado_id):
        return detalhe(exigir(Simulado.buscar_por_id(simulado_id)))


class CriarSimuladoService:
    @staticmethod
    def executar(dados, ator_id):
        titulo, ids = composicao(dados)

        def operacao():
            versoes = elegiveis(ids)
            instante = agora_utc()
            s = Simulado(
                titulo=titulo,
                estado="rascunho",
                revisao=1,
                autor_id=ator_id,
                criado_em=instante,
                atualizado_em=instante
            ).salvar(confirmar=False)
            for posicao, v in enumerate(versoes, 1):
                SimuladoRascunhoItem(
                    simulado_id=s.id,
                    posicao=posicao,
                    questao_id=v["questao_id"],
                    questao_versao_id=v["questao_versao_id"]
                ).salvar(confirmar=False)
            evento(s, ator_id, "cadastro", "Composição manual", instante)
            return detalhe(s), 201
        return TransactionManager.executar(operacao)


class EditarSimuladoService:
    @staticmethod
    def executar(simulado_id, dados, ator_id):
        titulo, ids = composicao(dados, editar=True)
        valor = revisao(dados)

        def operacao():
            s = exigir(Repo.bloquear(simulado_id))
            if s.estado != "rascunho":
                raise ConflitoError("Somente rascunhos podem ser editados.")
            conferir_revisao(s, valor)
            versoes = elegiveis(ids)
            for item in Repo.itens(simulado_id=s.id):
                item.deletar(confirmar=False)
            for posicao, v in enumerate(versoes, 1):
                SimuladoRascunhoItem(
                    simulado_id=s.id,
                    posicao=posicao,
                    questao_id=v["questao_id"],
                    questao_versao_id=v["questao_versao_id"]
                ).salvar(confirmar=False)
            s.titulo = titulo
            s.revisao += 1
            s.atualizado_em = agora_utc()
            s.salvar(confirmar=False)
            evento(s, ator_id, "edicao", "Edição de rascunho", s.atualizado_em)
            return detalhe(s)
        return TransactionManager.executar(operacao)


class PublicarSimuladoService:
    @staticmethod
    def executar(simulado_id, dados, ator_id):
        valor, motivo = _confirmacao(dados)

        def operacao():
            s = exigir(Repo.bloquear(simulado_id))
            if s.estado == "publicado" and SimuladoVersao.buscar_por_id(s.simulado_versao_id).revisao_origem == valor:
                return detalhe(s)
            if s.estado != "rascunho":
                raise ConflitoError("Somente rascunhos podem ser publicados.")
            conferir_revisao(s, valor)
            itens = Repo.itens(simulado_id=s.id)
            composicao({
                "titulo": s.titulo,
                "questao_versao_ids": [i.questao_versao_id for i in itens]
            })
            elegiveis([i.questao_versao_id for i in itens])
            instante = agora_utc()
            v = SimuladoVersao(
                simulado_id=s.id,
                numero=1,
                revisao_origem=valor,
                titulo=s.titulo,
                autor_id=ator_id,
                criado_em=instante
            ).salvar(confirmar=False)
            for i in itens:
                SimuladoVersaoItem(
                    simulado_versao_id=v.id,
                    posicao=i.posicao,
                    questao_id=i.questao_id,
                    questao_versao_id=i.questao_versao_id
                ).salvar(confirmar=False)
            for acao in ("revisao", "aprovacao", "publicacao"):
                evento(s, ator_id, acao, motivo, instante, v.id)
            s.simulado_versao_id = v.id
            s.estado = "publicado"
            s.atualizado_em = instante
            s.salvar(confirmar=False)
            return detalhe(s)
        return TransactionManager.executar(operacao)


class ArquivarSimuladoService:
    @staticmethod
    def executar(simulado_id, dados, ator_id):
        valor, motivo = _confirmacao(dados)

        def operacao():
            s = exigir(Repo.bloquear(simulado_id))
            if s.estado == "arquivado":
                return detalhe(s)
            conferir_revisao(s, valor)
            s.estado = "arquivado"
            s.atualizado_em = agora_utc()
            s.salvar(confirmar=False)
            evento(s, ator_id, "arquivamento", motivo, s.atualizado_em, s.simulado_versao_id)
            return detalhe(s)
        return TransactionManager.executar(operacao)
