"""Projeções de leitura do catálogo administrativo, sem entidades ORM."""
from datetime import datetime

MATERIA = ('id', 'nome', 'descricao', 'area_enem_id', 'status', 'criado_em', 'atualizado_em')
ASSUNTO = (
    'id',
    'nome',
    'nome_normalizado',
    'descricao',
    'materia_id',
    'status',
    'criado_em',
    'atualizado_em'
)
AREA = ('id', 'codigo', 'nome', 'ordem')
QUESTAO = (
    'id',
    'enunciado',
    'alternativa_a',
    'alternativa_b',
    'alternativa_c',
    'alternativa_d',
    'alternativa_e',
    'resposta_correta',
    'explicacao',
    'dificuldade',
    'assunto_id',
    'status',
    'revisao',
    'versao_publicada_id'
)
CONTAGENS = (
    'materias_ativas',
    'assuntos_ativos',
    'questoes_rascunhos',
    'questoes_publicadas',
    'questoes_arquivadas'
)


def colunas(*recursos, extras=()):
    return tuple(prefixo + '_' + campo for prefixo, campos in recursos for campo in campos) + extras


def registro(linha, prefixo, campos):
    dados = {campo: linha[prefixo + '_' + campo] for campo in campos}
    return {
        campo: valor.isoformat() if isinstance(valor, datetime) else valor
        for campo,
        valor in dados.items()
    }


def materia_admin(linha):
    return {
        **registro(linha, 'm', MATERIA),
        'area_enem': registro(linha, 'a', AREA),
        'assuntos': int(linha['assuntos']),
        'questoes': int(linha['questoes'])
    }


def assunto_admin(linha):
    return {
        **registro(linha, 's', ASSUNTO),
        'materia': registro(linha, 'm', MATERIA),
        'area_enem': registro(linha, 'a', AREA),
        'questoes': int(linha['questoes'])
    }


def questao_admin(linha):
    return {
        **registro(linha, 'q', QUESTAO),
        'assunto': registro(linha, 's', ASSUNTO),
        'materia': registro(linha, 'm', MATERIA),
        'area_enem': registro(linha, 'a', AREA)
    }
