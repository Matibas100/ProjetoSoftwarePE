"""Reconhecimento conservador dos contratos SQL oficiais de 011–017.

Referências versionadas são geradas a partir das migrations em schema descartável,
nunca a partir do banco a adotar. Nenhum DDL é executado neste módulo.
"""
import hashlib
import json
from pathlib import Path
import re

import pymysql
from database.migration_types import MigrationError

PROCEDURES_011 = frozenset({
    'sp_materias_admin',
    'sp_assuntos_admin',
    'sp_questoes_admin',
    'sp_conteudo_contagens_dashboard'
})
PROCEDURES_012 = frozenset({
    'sp_desempenho_resumo',
    'sp_atividades_recentes',
    'sp_simulados_contagens_dashboard'
})
VIEWS_012 = frozenset({
    'vw_conteudo_classificacao_historica',
    'vw_praticas_fatos_desempenho',
    'vw_simulados_fatos_desempenho',
    'vw_simulados_atividades'
})
PROCEDURES_013 = frozenset({
    'sp_areas_enem_ordenadas',
    'sp_materias_ativas',
    'sp_assuntos_ativos',
    'sp_impacto_materia',
    'sp_impacto_assunto',
    'sp_assuntos_nao_arquivados',
    'sp_bloquear_assunto',
    'sp_bloquear_materias',
    'sp_assunto_equivalente',
    'sp_bloquear_questao',
    'sp_versoes_questao',
    'sp_questao_versao_elegivel',
    'sp_questoes_elegiveis',
    'sp_questoes_versoes_elegiveis',
    'sp_questoes_versoes_historicas'
})
PROCEDURES_014 = frozenset({
    'sp_pratica_por_chave',
    'sp_pratica_propria',
    'sp_praticas_historico',
    'sp_praticas_fatos',
    'sp_bloquear_simulado',
    'sp_simulado_itens',
    'sp_simulados_itens_lote',
    'sp_simulados_andamentos_lote',
    'sp_simulados_titulos_lote',
    'sp_simulados_listar',
    'sp_simulado_tentativa_propria',
    'sp_simulado_tentativa_por_chave',
    'sp_simulado_em_andamento',
    'sp_simulado_respostas',
    'sp_simulados_historico',
    'sp_simulados_fatos'
})
PROCEDURES_015 = frozenset({
    'sp_plano_atual',
    'sp_plano_por_chave',
    'sp_plano_itens',
    'sp_plano_item_proprio',
    'sp_pares_elegiveis_plano',
    'sp_eliminar_planos_proprios'
})
PROCEDURES_016 = frozenset({
    'sp_usuario_por_email',
    'sp_consultar_sessao',
    'sp_renovar_acesso_sessao',
    'sp_revogar_sessao',
    'sp_revogar_sessoes_usuario',
    'sp_usuario_ativo_bloqueado',
    'sp_preparar_limite_autenticacao',
    'sp_limpar_autenticacao',
    'sp_bloquear_identidade_privacidade',
    'sp_ultimas_decisoes_privacidade',
    'sp_decisao_privacidade_por_chave'
})
PROCEDURES_017 = frozenset({'sp_alunos_admin', 'sp_usuario_gestao_bloqueado'})
NOMES = PROCEDURES_011 | PROCEDURES_012 | VIEWS_012 | PROCEDURES_013 | PROCEDURES_014 | PROCEDURES_015 | PROCEDURES_016 | PROCEDURES_017
REFERENCIA = Path(__file__).with_name('sql_resources_reference.json')


def normalizar_schema(sql, schema):
    # Reconhece somente literais e identificadores qualificados; nunca modifica
    # conteúdo de strings, destinos externos, predicados ou segurança.
    if not isinstance(sql, str) or not sql:
        raise ValueError('Definição SQL indisponível.')
    identificador = '`' + schema.replace('`', '``') + '`'
    return re.sub(
        r"'(?:[^'\\]|\\.|'')*'|`(?:[^`]|``)*`(?=\.)",
        lambda m: '`<local>`' if m.group() == identificador else m.group(),
        sql
    )


def inventariar(connection):
    with connection.cursor() as c:
        c.execute('SELECT ROUTINE_NAME AS nome FROM information_schema.ROUTINES '
            'WHERE ROUTINE_SCHEMA=DATABASE()')
        routines = {r['nome'] for r in c.fetchall()}
        c.execute("SELECT TABLE_NAME AS nome FROM information_schema.VIEWS WHERE TABLE_SCHEMA=DATABASE()")
        views = {r['nome'] for r in c.fetchall()}
    return routines, views


def possui_recursos(connection):
    try:
        routines, views = inventariar(connection)
        return bool((routines | views) & NOMES)
    except (pymysql.MySQLError, KeyError, TypeError):
        raise MigrationError('Inventário dos recursos SQL indisponível.') from None


def assinatura(connection, nome):
    """Inclui assinatura/corpo/segurança e tipos/dependências das views."""
    try:
        with connection.cursor() as c:
            c.execute('SELECT DATABASE() AS nome')
            schema = c.fetchone()['nome']
            if not schema:
                raise ValueError('Schema ausente.')
            if nome in VIEWS_012:
                c.execute(
                    'SELECT VIEW_DEFINITION, CHECK_OPTION, IS_UPDATABLE, SECURITY_TYPE, '
                    'CHARACTER_SET_CLIENT, COLLATION_CONNECTION FROM information_schema.VIEWS '
                    'WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s',
                    (nome,)
                )
                meta = c.fetchone()
                if not meta or any(v is None for v in meta.values()):
                    raise ValueError('View incompleta.')
                meta['VIEW_DEFINITION'] = normalizar_schema(meta['VIEW_DEFINITION'], schema)
                c.execute(
                    'SELECT ORDINAL_POSITION,COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE, '
                    'CHARACTER_SET_NAME,COLLATION_NAME FROM information_schema.COLUMNS '
                    'WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s ORDER BY ORDINAL_POSITION',
                    (
                        nome,
                    )
                )
                colunas = c.fetchall()
                if not colunas:
                    raise ValueError('Colunas ausentes.')
                c.execute(
                    'SELECT TABLE_SCHEMA,TABLE_NAME FROM information_schema.VIEW_TABLE_USAGE '
                    'WHERE VIEW_SCHEMA=DATABASE() AND VIEW_NAME=%s ORDER BY TABLE_SCHEMA,TABLE_NAME',
                    (
                        nome,
                    )
                )
                dependencias = c.fetchall()
                if not dependencias:
                    raise ValueError('Dependências indisponíveis.')
                for d in dependencias:
                    d['TABLE_SCHEMA'] = (['local'] if d['TABLE_SCHEMA'] == schema
                        else ['external', d['TABLE_SCHEMA']])
                meta.update(colunas=colunas, dependencias=dependencias)
            elif nome in NOMES - VIEWS_012:
                c.execute(
                    'SELECT ROUTINE_TYPE,ROUTINE_DEFINITION,IS_DETERMINISTIC,SQL_DATA_ACCESS, '
                    'SECURITY_TYPE,SQL_MODE,CHARACTER_SET_CLIENT,COLLATION_CONNECTION,DATABASE_COLLATION '
                    'FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=DATABASE() AND ROUTINE_NAME=%s',
                    (
                        nome,
                    )
                )
                meta = c.fetchone()
                if not meta or any(v is None for v in meta.values()):
                    raise ValueError('Routine incompleta.')
                meta['ROUTINE_DEFINITION'] = normalizar_schema(meta['ROUTINE_DEFINITION'], schema)
                c.execute(
                    'SELECT ORDINAL_POSITION,PARAMETER_MODE,PARAMETER_NAME,DTD_IDENTIFIER, '
                    'CHARACTER_SET_NAME,COLLATION_NAME FROM information_schema.PARAMETERS '
                    'WHERE SPECIFIC_SCHEMA=DATABASE() AND SPECIFIC_NAME=%s ORDER BY ORDINAL_POSITION',
                    (
                        nome,
                    )
                )
                meta['parametros'] = c.fetchall()
            else:
                raise ValueError('Recurso não previsto.')
        canonical = json.dumps(meta, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    except (pymysql.MySQLError, KeyError, TypeError, ValueError, AttributeError):
        raise MigrationError('Metadados SQL indisponíveis: ' + nome + '.') from None


def detectar_prefixo(connection):
    try:
        routines, views = inventariar(connection)
        presentes = (routines | views) & NOMES
        if not presentes:
            return None
        prefixo = ('017' if presentes & PROCEDURES_017 else
            '016' if presentes & PROCEDURES_016 else
            '015' if presentes & PROCEDURES_015 else
            '014' if presentes & PROCEDURES_014 else
            '013' if presentes & PROCEDURES_013 else
            '012' if presentes & (PROCEDURES_012 | VIEWS_012) else '011')
        esperados = PROCEDURES_011 | (PROCEDURES_012 | VIEWS_012 if prefixo >= '012' else frozenset())
        if prefixo >= '013':
            esperados |= PROCEDURES_013
        if prefixo >= '014':
            esperados |= PROCEDURES_014
        if prefixo >= '015':
            esperados |= PROCEDURES_015
        if prefixo >= '016':
            esperados |= PROCEDURES_016
        if prefixo >= '017':
            esperados |= PROCEDURES_017
        if presentes != esperados:
            raise MigrationError('Recursos SQL parciais do prefixo ' + prefixo + '.')
        referencia = json.loads(REFERENCIA.read_text(encoding='utf-8'))
        for nome in sorted(esperados):
            if assinatura(connection, nome) != referencia[nome]:
                raise MigrationError('Contrato SQL divergente: ' + nome + '.')
        return prefixo
    except (pymysql.MySQLError, KeyError, TypeError, OSError, ValueError):
        raise MigrationError('Referências ou metadados SQL indisponíveis.') from None
