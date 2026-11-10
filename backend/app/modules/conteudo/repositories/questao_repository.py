from app.core.procedures_mysql import executar_resultados, conferir_resultados
from app.modules.conteudo.repositories.registros_admin import (
    QUESTAO,
    ASSUNTO,
    MATERIA,
    AREA,
    CONTAGENS,
    colunas,
    questao_admin
)
import json
from sqlalchemy import text, select

from app.extensions import db
from app.modules.conteudo.models.questao import Questao
from app.modules.conteudo.models.questao_versao import QuestaoVersao
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.models.materia import Materia
from app.modules.conteudo.models.area_enem import AreaEnem
from app.modules.conteudo.repositories.catalogo_repository import CatalogoRepository


class QuestaoRepository:
    """Executa a consulta especializada de Questoes por Assunto."""

    @staticmethod
    def pares_elegiveis_plano(assunto_ids, bloquear=False):
        """Disponibilidade atual por classificação, sem expor conteúdo ou gabarito.

        Na geração, a leitura final compartilha locks com retirada/transferência.
        O vínculo atual deve coincidir também com o snapshot da versão publicada.
        """
        if not assunto_ids:
            return set()
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            'CALL sp_pares_elegiveis_plano(%s,%s)',
            (
                json.dumps(sorted(set(assunto_ids))),
                int(bloquear)
            )
        )
        linhas, = conferir_resultados(resultados, [('assunto_id', 'materia_id')])
        return {(r['assunto_id'], r['materia_id']) for r in linhas}

    @staticmethod
    def contagens_dashboard(contexto):
        resultados = contexto.executar_resultados("CALL sp_conteudo_contagens_dashboard()")
        linhas, = conferir_resultados(resultados, [CONTAGENS])
        linha, = linhas
        return {estado: int(linha['questoes_' + estado]) for estado in (
            'rascunhos',
            'publicadas',
            'arquivadas'
        )}

    @staticmethod
    def projecao_classificacao_historica():
        """Contrato de leitura de classificação das versões publicadas imutáveis."""
        q = QuestaoVersao
        return select(
            q.id.label("questao_versao_id"),
            q.materia_id,
            q.materia_nome,
            q.assunto_id,
            q.assunto_nome
        ).where(q.estado == "publicada")

    @staticmethod
    def bloquear(questao_id):
        db.session.flush()
        resultado = db.session.execute(
            select(Questao).from_statement(
                text("CALL sp_bloquear_questao(:id)").columns(*Questao.__table__.columns))
            .execution_options(populate_existing=True),
            {'id': questao_id}
        )
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def bloquear_classificacao(assunto_id):
        # Preserva a sequência: Assunto e somente depois sua Matéria corrente.
        assunto = CatalogoRepository.buscar_assunto_para_atualizacao(assunto_id)
        if assunto is None:
            return None
        materia, = CatalogoRepository.buscar_materias_para_atualizacao([assunto.materia_id])
        area = AreaEnem.buscar_por_id(materia.area_enem_id)
        return assunto, materia, area

    @staticmethod
    def versoes(questao_id):
        db.session.flush()
        resultado = db.session.execute(
            select(QuestaoVersao).from_statement(
                text("CALL sp_versoes_questao(:id)").columns(*QuestaoVersao.__table__.columns)),
            {'id': questao_id}
        )
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()

    @staticmethod
    def listar_admin(filtros, pagina, por_pagina):
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            "CALL sp_questoes_admin(%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                filtros.get('busca') or None,
                filtros.get('status'),
                filtros.get('dificuldade'),
                filtros.get('area_enem_id'),
                filtros.get('materia_id'),
                filtros.get('assunto_id'),
                pagina,
                por_pagina
            )
        )
        linhas, totais = conferir_resultados(
            resultados,
            [colunas(('q', QUESTAO), ('s', ASSUNTO), ('m', MATERIA), ('a', AREA)), ('total',)]
        )
        total, = totais
        return [questao_admin(linha) for linha in linhas], int(total['total'])

    @staticmethod
    def versao_elegivel(versao_id, bloquear=False):
        db.session.flush()
        consulta = select(QuestaoVersao).from_statement(
            text("CALL sp_questao_versao_elegivel(:id,:bloquear)").columns(*QuestaoVersao.__table__.columns))
        if bloquear:
            consulta = consulta.execution_options(populate_existing=True)
        resultado = db.session.execute(consulta, {'id': versao_id, 'bloquear': int(bloquear)})
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def listar_elegiveis(filtros, pagina, limite):
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            "CALL sp_questoes_elegiveis(%s,%s,%s,%s)",
            (filtros.get('assunto_id'), filtros.get('materia_id'), pagina, limite)
        )
        linhas, totais = conferir_resultados(
            resultados,
            [tuple(c.name for c in QuestaoVersao.__table__.columns), ('total',)]
        )
        total, = totais
        return list(linhas), int(total['total'])

    @staticmethod
    def versoes_elegiveis(ids):
        if not ids:
            return []
        db.session.flush()
        resultado = db.session.execute(
            select(QuestaoVersao).from_statement(
                text("CALL sp_questoes_versoes_elegiveis(:ids)").columns(*QuestaoVersao.__table__.columns)),
            {'ids': json.dumps(sorted(set(ids)))}
        )
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()

    @staticmethod
    def versoes_historicas(ids):
        if not ids:
            return []
        db.session.flush()
        resultado = db.session.execute(
            select(QuestaoVersao).from_statement(
                text("CALL sp_questoes_versoes_historicas(:ids)").columns(*QuestaoVersao.__table__.columns)),
            {'ids': json.dumps(sorted(set(ids)))}
        )
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()

    @staticmethod
    def buscar_por_assunto(assunto_id):
        resultado = db.session.execute(
            text("CALL sp_questoes_por_assunto(:assunto_id)"),
            {"assunto_id": assunto_id},
        )
        try:
            return [dict(linha) for linha in resultado.mappings().all()]
        finally:
            resultado.close()
