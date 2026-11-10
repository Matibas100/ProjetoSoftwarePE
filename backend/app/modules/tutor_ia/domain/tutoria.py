"""Erros seguros e formato pedagógico da resposta."""
import re
import unicodedata
from app.exceptions import ErroAplicacao


TITULOS = (
    '1. Explicação simples',
    '2. Exemplo',
    '3. Verifique sua compreensão',
    '4. Exercício curto'
)


class TutoriaError(ErroAplicacao):
    def __init__(self, mensagem, status=400, codigo='dados_invalidos', retry_after=None):
        super().__init__(mensagem)
        self.status_code, self.codigo, self.retry_after = status, codigo, retry_after

    def to_dict(self):
        return {'erro': str(self), 'codigo': self.codigo}


def resposta_invalida():
    return TutoriaError(
        'O Tutor retornou uma resposta inválida. Tente novamente por ação própria.',
        502,
        'tutor_resposta_invalida'
    )


def validar_entrada(dados):
    if not isinstance(dados, dict) or set(dados) != {'disciplina', 'nivel', 'assunto', 'duvida'}:
        raise TutoriaError('Informe somente disciplina, nivel, assunto e duvida.')
    entrada = {}
    for campo, minimo, maximo in (
        ('disciplina', 1, 100),
        ('nivel', 1, 20),
        ('assunto', 1, 150),
        ('duvida', 10, 2000)
    ):
        valor = dados[campo]
        if not isinstance(valor, str):
            raise TutoriaError(f'O campo {campo} deve ser texto.')
        # Conferir antes do trim para não apagar controles inválidos nas extremidades.
        permitidos = '\t\n\r' if campo == 'duvida' else ''
        if any(unicodedata.category(c).startswith('C') and c not in permitidos for c in valor):
            raise TutoriaError(f'O campo {campo} contém caracteres inválidos.')
        valor = valor.strip()
        if not minimo <= len(valor) <= maximo:
            raise TutoriaError(f'O campo {campo} deve ter entre {minimo} e {maximo} caracteres.')
        entrada[campo] = valor
    if entrada['nivel'] != 'ensino_medio':
        raise TutoriaError('O nível deve ser ensino_medio.')
    return entrada


def validar_resposta(texto):
    if not isinstance(texto, str):
        raise resposta_invalida()
    texto = texto.replace('\r\n', '\n').replace('\r', '\n').strip()
    if not texto or len(texto) > 12000:
        raise resposta_invalida()
    posicoes = []
    for titulo in TITULOS:
        encontrados = list(re.finditer(r'^' + re.escape(titulo) + r'[ \t]*$', texto, re.MULTILINE))
        if len(encontrados) != 1:
            raise resposta_invalida()
        posicoes.append(encontrados[0])
    if posicoes[0].start() != 0 or [p.start() for p in posicoes] != sorted(p.start() for p in posicoes):
        raise resposta_invalida()
    for i, posicao in enumerate(posicoes):
        fim = posicoes[i + 1].start() if i < 3 else len(texto)
        if not texto[posicao.end(): fim].strip():
            raise resposta_invalida()
    return texto
