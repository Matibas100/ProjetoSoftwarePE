"""Validação e apresentação administrativas, sem persistência."""
from app.modules.contas.domain.autenticacao import AutenticacaoError, validar_email


def validar_id(valor):
    if type(valor) is not int or not 1 <= valor <= 2147483647:
        raise AutenticacaoError('Identificador inválido.')
    return valor


def exigir_aluno(usuario):
    if usuario is None or usuario.perfil != 'aluno':
        raise AutenticacaoError('Usuário não encontrado.',404,'usuario_nao_encontrado')
    return usuario


def email_mascarado(email):
    try:
        normalizado = validar_email(email)
    except AutenticacaoError:
        return '***'
    local, dominio = normalizado.split('@')
    return local[0]+'***@'+dominio


def apresentar_usuario(usuario):
    return {'id': usuario.id, 'nome': usuario.nome, 'email': usuario.email,
        'perfil': usuario.perfil, 'ativo': bool(usuario.ativo),
        'criado_em': usuario.criado_em.isoformat()+'Z'}


def apresentar_linha(linha):
    return {'id': linha['id'], 'nome': linha['nome'],
        'email_mascarado': email_mascarado(linha['email']), 'perfil': linha['perfil'],
        'ativo': bool(linha['ativo']), 'criado_em': linha['criado_em'].isoformat()+'Z'}
