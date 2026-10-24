from app.repositories.questao_repository import QuestaoRepository
from app.services.gestao_questao_service import ConsultarVersaoElegivelService
from app.services.listar_catalogo_admin_service import _envelope
from app.services.pratica_validacao import parametros


class ListarQuestoesAlunoService:
    @staticmethod
    def executar(filtros):
        valores = parametros(filtros, {"materia_id", "assunto_id"})
        pagina, limite = valores.pop("pagina"), valores.pop("por_pagina")
        versoes, total = QuestaoRepository.listar_elegiveis(valores, pagina, limite)
        return _envelope([ConsultarVersaoElegivelService.executar(v.id) for v in versoes], pagina, limite, total)
