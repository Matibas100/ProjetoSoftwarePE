"""Casos de uso administrativos e fronteira de conteúdo versionado."""
from app.core.validacao import revisao_editorial as _revisao, confirmacao_editorial as _confirmacao
from app.core.relogio import agora_utc
from app.exceptions import ConflitoError, DadosInvalidosError, RecursoNaoEncontradoError
from app.modules.conteudo.models.questao import Questao
from app.modules.conteudo.models.questao_versao import QuestaoVersao
from app.modules.conteudo.models.questao_evento import QuestaoEvento
from app.modules.conteudo.repositories.questao_repository import QuestaoRepository
from app.modules.conteudo.services.criar_questao_service import CriarQuestaoService
from app.core.paginacao import inteiro_filtro, envelope_paginado
from app.transaction_manager import TransactionManager


def _exigir_questao(questao):
    if questao is None:
        raise RecursoNaoEncontradoError("Questão não encontrada.")
    return questao


def _detalhe(questao):
    return {"questao": questao.to_dict(), "status": questao.status, "revisao": questao.revisao,
        "versao_publicada_id": questao.versao_publicada_id,
        "versoes": [{"id": v.id, "numero": v.numero, "estado": v.estado}
                    for v in QuestaoRepository.versoes(questao.id)]}






def _conferir_revisao(questao, revisao):
    if questao.revisao != revisao:
        raise ConflitoError("A revisão mudou. Recarregue antes de tentar novamente.")


def _evento(questao, ator_id, acao, motivo, instante, versao_id=None):
    QuestaoEvento(questao_id=questao.id, versao_id=versao_id, ator_id=ator_id,
        acao=acao, motivo=motivo, criado_em=instante).salvar(confirmar=False)


class ConsultarQuestaoService:
    @staticmethod
    def executar(questao_id):
        return _detalhe(_exigir_questao(Questao.buscar_por_id(questao_id)))


class ListarQuestoesAdminService:
    @staticmethod
    def executar(parametros):
        permitidos = {"pagina", "por_pagina", "busca", "status", "dificuldade",
                      "area_enem_id", "materia_id", "assunto_id"}
        if set(parametros) - permitidos:
            raise DadosInvalidosError("Filtro desconhecido.")
        pagina = inteiro_filtro(parametros.get("pagina", "1"), "pagina")
        limite = inteiro_filtro(parametros.get("por_pagina", "20"), "por_pagina", maximo=100)
        if pagina is None or limite is None:
            raise DadosInvalidosError("Paginação inválida.")
        filtros = {campo: inteiro_filtro(parametros.get(campo), campo)
                   for campo in ("area_enem_id", "materia_id", "assunto_id")}
        for campo, validos in (("status", {"rascunho", "publicada", "arquivada"}),
                               ("dificuldade", CriarQuestaoService.DIFICULDADES_VALIDAS)):
            valor = parametros.get(campo) or None
            if valor and valor not in validos:
                raise DadosInvalidosError(f"{campo} inválido.")
            filtros[campo] = valor
        busca = (parametros.get("busca") or "").strip()
        if len(busca) > 100:
            raise DadosInvalidosError("Busca deve ter até 100 caracteres.")
        filtros["busca"] = busca
        linhas, total = QuestaoRepository.listar_admin(filtros, pagina, limite)
        return envelope_paginado(linhas, pagina, limite, total)


class EditarQuestaoService:
    @staticmethod
    def executar(questao_id, dados, ator_id):
        revisao = _revisao(dados)
        if set(dados) - (Questao.campos_atualizaveis | {"revisao"}) or len(dados) < 2:
            raise DadosInvalidosError("Informe somente campos de conteúdo e revisão.")

        def operacao():
            questao = _exigir_questao(QuestaoRepository.bloquear(questao_id))
            if questao.status == "arquivada":
                raise ConflitoError("Questão arquivada não aceita edição.")
            _conferir_revisao(questao, revisao)
            conteudo = {campo: getattr(questao, campo) for campo in Questao.campos_atualizaveis}
            conteudo.update({campo: valor for campo, valor in dados.items() if campo != "revisao"})
            valores = CriarQuestaoService.validar(conteudo)
            instante = agora_utc()
            # Campos técnicos não entram no adaptador legado de conteúdo.
            for campo, valor in valores.items():
                setattr(questao, campo, valor)
            questao.revisao += 1
            questao.atualizado_em = instante
            questao.salvar(confirmar=False)
            _evento(questao, ator_id, "edicao", "Edição manual de rascunho.", instante)
            return _detalhe(questao)
        return TransactionManager.executar(operacao)


class PublicarQuestaoService:
    @staticmethod
    def executar(questao_id, dados, ator_id):
        revisao, motivo = _confirmacao(dados)

        def operacao():
            questao = _exigir_questao(QuestaoRepository.bloquear(questao_id))
            if questao.status == "arquivada":
                raise ConflitoError("Questão arquivada não aceita publicação.")
            _conferir_revisao(questao, revisao)
            versoes = QuestaoRepository.versoes(questao_id)
            if any(v.estado == "publicada" and v.revisao_origem == revisao for v in versoes):
                return _detalhe(questao)
            classificacao = QuestaoRepository.bloquear_classificacao(questao.assunto_id)
            if classificacao is None:
                raise RecursoNaoEncontradoError("Assunto não encontrado.")
            assunto, materia, area = classificacao
            if assunto.status != "ativa" or materia.status != "ativa":
                raise ConflitoError("Catálogo indisponível para publicação.")
            valores = CriarQuestaoService.validar(questao.to_dict())
            instante = agora_utc()
            versao = QuestaoVersao(**valores, questao_id=questao.id,
                numero=max((v.numero for v in versoes), default=0)+1, revisao_origem=revisao,
                estado="publicada", assunto_nome=assunto.nome, materia_id=materia.id,
                materia_nome=materia.nome, area_enem_id=area.id, area_enem_nome=area.nome,
                ator_id=ator_id, origem="manual", criado_em=instante)
            versao.salvar(confirmar=False)
            for acao in ("revisao", "aprovacao", "publicacao"):
                _evento(questao, ator_id, acao, motivo, instante, versao.id)
            questao.versao_publicada_id = versao.id
            questao.status = "publicada"
            questao.atualizado_em = instante
            questao.salvar(confirmar=False)
            return _detalhe(questao)
        return TransactionManager.executar(operacao)


class ArquivarQuestaoService:
    @staticmethod
    def executar(questao_id, dados, ator_id):
        revisao, motivo = _confirmacao(dados)

        def operacao():
            questao = _exigir_questao(QuestaoRepository.bloquear(questao_id))
            if questao.status == "arquivada":
                return _detalhe(questao)
            _conferir_revisao(questao, revisao)
            instante = agora_utc()
            questao.status = "arquivada"
            questao.atualizado_em = instante
            questao.salvar(confirmar=False)
            _evento(questao, ator_id, "arquivamento", motivo, instante, questao.versao_publicada_id)
            return _detalhe(questao)
        return TransactionManager.executar(operacao)


class ConsultarVersaoElegivelService:
    @staticmethod
    def executar(versao_id, bloquear=False):
        versao = QuestaoVersao.buscar_por_id(versao_id)
        if versao is None:
            raise RecursoNaoEncontradoError("Versão não encontrada.")
        elegivel = (QuestaoRepository.versao_elegivel(versao_id, bloquear=True) if bloquear
                    else QuestaoRepository.versao_elegivel(versao_id))
        if elegivel is None:
            raise ConflitoError("Versão indisponível para novo uso.")
        return elegivel.conteudo()


class ConsultarVersaoHistoricaService:
    @staticmethod
    def executar(versao_id, correcao=False):
        # Consumidor interno deve verificar propriedade e conclusão da tentativa.
        versao = QuestaoVersao.buscar_por_id(versao_id)
        if versao is None or versao.estado != "publicada":
            raise RecursoNaoEncontradoError("Versão publicada não encontrada.")
        return versao.conteudo(correcao=correcao)


class ConsultarVersoesElegiveisService:
    @staticmethod
    def executar(ids):
        """Mapa interno somente das versões disponíveis para novo uso, sem locks."""
        return {v.id: v.conteudo() for v in QuestaoRepository.versoes_elegiveis(set(ids))}


class ConsultarVersoesHistoricasService:
    @staticmethod
    def executar(ids, correcao=False):
        """Consumidor deve autorizar propriedade/conclusão antes desta leitura."""
        ids = set(ids)
        versoes = {v.id: v.conteudo(correcao=correcao)
            for v in QuestaoRepository.versoes_historicas(ids)}
        if ids - versoes.keys():
            raise RecursoNaoEncontradoError("Versão publicada não encontrada.")
        return versoes
