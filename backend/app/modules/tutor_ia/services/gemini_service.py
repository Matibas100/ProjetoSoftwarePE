"""Transporte REST fixo, sem retries, identidade ou armazenamento de interação."""
import json
import requests
from app.modules.tutor_ia.domain.tutoria import TutoriaError, resposta_invalida


ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/interactions'
MAX_BYTES = 1024 * 1024


class GeminiService:
    def __init__(self, *, habilitado=False, chave='', modelo='gemini-3.6-flash'):
        self._habilitado, self._chave, self._modelo = habilitado, chave, modelo

    @property
    def disponivel(self):
        return bool(self._habilitado and isinstance(self._chave, str) and self._chave.strip()
                    and isinstance(self._modelo, str) and self._modelo.strip())

    def gerar(self, entrada, instrucao):
        if not self.disponivel:
            raise TutoriaError('Tutor indisponível no momento.', 503, 'tutor_indisponivel')
        payload = {'model': self._modelo, 'system_instruction': instrucao,
                   'input': json.dumps(entrada, ensure_ascii=False), 'store': False,
                   'generation_config': {'max_output_tokens': 4096}}
        try:
            with requests.post(ENDPOINT, headers={'x-goog-api-key': self._chave},
                               json=payload, timeout=(5, 30), allow_redirects=False, stream=True) as resposta:
                if resposta.status_code != 200:
                    raise TutoriaError('Não foi possível consultar o provedor de tutoria.',
                                       502, 'tutor_provedor_indisponivel')
                partes, total = [], 0
                for bloco in resposta.iter_content(chunk_size=8192):
                    total += len(bloco)
                    if total > MAX_BYTES:
                        raise resposta_invalida()
                    partes.append(bloco)
                dados = json.loads(b''.join(partes).decode('utf-8'))
        except requests.Timeout:
            raise TutoriaError('O Tutor excedeu o tempo de espera.', 502, 'tutor_timeout') from None
        except requests.ConnectionError as erro:
            # Requests pode encapsular ReadTimeout durante iter_content em ConnectionError.
            from urllib3.exceptions import ReadTimeoutError
            if erro.args and isinstance(erro.args[0], ReadTimeoutError):
                raise TutoriaError('O Tutor excedeu o tempo de espera.', 502, 'tutor_timeout') from None
            raise TutoriaError('Não foi possível consultar o provedor de tutoria.',
                               502, 'tutor_provedor_indisponivel') from None
        except requests.RequestException:
            raise TutoriaError('Não foi possível consultar o provedor de tutoria.',
                               502, 'tutor_provedor_indisponivel') from None
        except (ValueError, UnicodeError):
            raise resposta_invalida() from None
        return self._extrair(dados)

    @staticmethod
    def _extrair(dados):
        if not isinstance(dados, dict) or dados.get('status') != 'completed':
            raise resposta_invalida()
        etapas = dados.get('steps')
        if not isinstance(etapas, list) or any(not isinstance(e, dict) for e in etapas):
            raise resposta_invalida()
        saidas = [e for e in etapas if e.get('type') == 'model_output']
        if not saidas or not isinstance(saidas[-1].get('content'), list):
            raise resposta_invalida()
        textos = []
        for bloco in saidas[-1]['content']:
            if not isinstance(bloco, dict):
                raise resposta_invalida()
            if bloco.get('type') == 'text':
                if not isinstance(bloco.get('text'), str):
                    raise resposta_invalida()
                textos.append(bloco['text'])
        if not textos or not ''.join(textos).strip():
            raise resposta_invalida()
        return ''.join(textos)
