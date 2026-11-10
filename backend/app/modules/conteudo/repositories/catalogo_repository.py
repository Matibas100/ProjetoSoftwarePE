from app.core.procedures_mysql import executar_resultados, conferir_resultados
from app.modules.conteudo.repositories.registros_admin import (
    MATERIA,
    ASSUNTO,
    AREA,
    CONTAGENS,
    colunas,
    materia_admin,
    assunto_admin
)
import json
from sqlalchemy import select, text

from app.extensions import db
from app.modules.conteudo.models.assunto import Assunto
from app.modules.conteudo.models.area_enem import AreaEnem
from app.modules.conteudo.models.materia import Materia


class CatalogoRepository:
    """Consultas especializadas, agregacoes e locks do catalogo."""

    @staticmethod
    def listar_areas_ordenadas():
        db.session.flush()
        resultado = db.session.execute(select(AreaEnem).from_statement(
            text("CALL sp_areas_enem_ordenadas()").columns(*AreaEnem.__table__.columns)))
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()

    @staticmethod
    def listar_materias_ativas():
        db.session.flush()
        resultado = db.session.execute(select(Materia).from_statement(
            text("CALL sp_materias_ativas()").columns(*Materia.__table__.columns)))
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()

    @staticmethod
    def listar_assuntos_ativos(materia_id=None):
        db.session.flush()
        resultado = db.session.execute(
            select(Assunto).from_statement(
                text("CALL sp_assuntos_ativos(:materia_id)").columns(*Assunto.__table__.columns)),
            {'materia_id': materia_id}
        )
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()

    @staticmethod
    def contagens_dashboard(contexto):
        resultados = contexto.executar_resultados("CALL sp_conteudo_contagens_dashboard()")
        linhas, = conferir_resultados(resultados, [CONTAGENS])
        linha, = linhas
        return {campo: int(linha[campo]) for campo in ('materias_ativas', 'assuntos_ativos')}

    @staticmethod
    def listar_materias_admin(filtros, pagina, por_pagina):
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            "CALL sp_materias_admin(%s,%s,%s,%s,%s)",
            (
                filtros.get('busca') or None,
                filtros.get('status'),
                filtros.get('area_enem_id'),
                pagina,
                por_pagina
            )
        )
        linhas, totais = conferir_resultados(
            resultados,
            [colunas(('m', MATERIA), ('a', AREA), extras=('assuntos', 'questoes')), ('total',)]
        )
        total, = totais
        return [materia_admin(linha) for linha in linhas], int(total['total'])

    @staticmethod
    def listar_assuntos_admin(filtros, pagina, por_pagina):
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            "CALL sp_assuntos_admin(%s,%s,%s,%s,%s,%s)",
            (
                filtros.get('busca') or None,
                filtros.get('status'),
                filtros.get('area_enem_id'),
                filtros.get('materia_id'),
                pagina,
                por_pagina
            )
        )
        linhas, totais = conferir_resultados(
            resultados,
            [
                colunas(
                    (
                        's',
                        ASSUNTO
                    ),
                    (
                        'm',
                        MATERIA
                    ),
                    (
                        'a',
                        AREA
                    ),
                    extras=(
                        'questoes',
                    )
                ),
                (
                    'total',
                )
            ]
        )
        total, = totais
        return [assunto_admin(linha) for linha in linhas], int(total['total'])

    @staticmethod
    def impacto_materia(materia_id):
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            "CALL sp_impacto_materia(%s)",
            (
                materia_id,
            )
        )
        linhas, = conferir_resultados(resultados, [('assuntos', 'questoes', 'transferencias')])
        linha, = linhas
        return {campo: int(valor) for campo, valor in linha.items()}

    @staticmethod
    def impacto_assunto(assunto_id):
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            "CALL sp_impacto_assunto(%s)",
            (
                assunto_id,
            )
        )
        linhas, = conferir_resultados(resultados, [('questoes', 'transferencias')])
        linha, = linhas
        return {campo: int(valor) for campo, valor in linha.items()}

    @staticmethod
    def contar_assuntos_nao_arquivados(materia_id):
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            "CALL sp_assuntos_nao_arquivados(%s)",
            (
                materia_id,
            )
        )
        linhas, = conferir_resultados(resultados, [('total',)])
        linha, = linhas
        return int(linha['total'])

    @staticmethod
    def buscar_assunto_para_atualizacao(assunto_id):
        db.session.flush()
        resultado = db.session.execute(
            select(Assunto).from_statement(
                text("CALL sp_bloquear_assunto(:id)").columns(*Assunto.__table__.columns))
            .execution_options(populate_existing=True),
            {'id': assunto_id}
        )
        try:
            return resultado.scalar_one_or_none()
        finally:
            resultado.close()

    @staticmethod
    def buscar_materias_para_atualizacao(ids):
        db.session.flush()
        resultado = db.session.execute(
            select(Materia).from_statement(
                text("CALL sp_bloquear_materias(:ids)").columns(*Materia.__table__.columns))
            .execution_options(populate_existing=True),
            {'ids': json.dumps(sorted(set(ids)))}
        )
        try:
            return resultado.scalars().all()
        finally:
            resultado.close()

    @staticmethod
    def existe_assunto_equivalente(materia_id, nome_normalizado, ignorar_id=None):
        db.session.flush()
        resultados = executar_resultados(
            db.session.connection(),
            "CALL sp_assunto_equivalente(%s,%s,%s)",
            (materia_id, nome_normalizado, ignorar_id)
        )
        linhas, = conferir_resultados(resultados, [('existe',)])
        linha, = linhas
        return bool(linha['existe'])
