"""Fronteira de versões, classificação e contagens; sem exportação ORM."""
from app.modules.conteudo.services.gestao_questao_service import ConsultarVersaoElegivelService as _ConsultarVersaoElegivelService
from app.modules.conteudo.services.gestao_questao_service import ConsultarVersaoHistoricaService as _ConsultarVersaoHistoricaService
from app.modules.conteudo.services.gestao_questao_service import ConsultarVersoesElegiveisService as _ConsultarVersoesElegiveisService
from app.modules.conteudo.services.gestao_questao_service import ConsultarVersoesHistoricasService as _ConsultarVersoesHistoricasService
from app.modules.conteudo.repositories.questao_repository import QuestaoRepository as _Questoes
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository as _Catalogo

ConsultarVersaoElegivelService = _ConsultarVersaoElegivelService
ConsultarVersaoHistoricaService = _ConsultarVersaoHistoricaService
ConsultarVersoesElegiveisService = _ConsultarVersoesElegiveisService
ConsultarVersoesHistoricasService = _ConsultarVersoesHistoricasService

def pares_elegiveis_plano(assunto_ids, bloquear=False):
    return _Questoes.pares_elegiveis_plano(assunto_ids, bloquear=bloquear)


def projecao_classificacao_historica():
    return _Questoes.projecao_classificacao_historica()


def contagens_questoes(contexto):
    return _Questoes.contagens_dashboard(contexto)


def contagens_catalogo(contexto):
    return _Catalogo.contagens_dashboard(contexto)


__all__ = ['ConsultarVersaoElegivelService', 'ConsultarVersaoHistoricaService', 'ConsultarVersoesElegiveisService', 'ConsultarVersoesHistoricasService', 'pares_elegiveis_plano', 'projecao_classificacao_historica', 'contagens_questoes', 'contagens_catalogo']
