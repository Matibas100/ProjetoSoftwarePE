"""HTTP local: autenticação já conferida pelo hook de Contas."""
import json
from flask import g, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge
from app.exceptions import ErroAplicacao
from app.http_composition import servicos
from app.http_response import registrar_falha
from app.modules.tutor_ia.domain.tutoria import TutoriaError


class TutoriaController:
    @staticmethod
    def gerar():
        try:
            usuario_id = g.auth_sessao.usuario_id  # Primitivo antes de encerrar a leitura.
            request.max_content_length = 16384
            if request.content_length is not None and request.content_length > 16384:
                raise RequestEntityTooLarge()
            corpo = request.stream.read(16385)
            if len(corpo) > 16384:
                raise RequestEntityTooLarge()
            if not request.is_json:
                raise TutoriaError('Envie um objeto JSON com os quatro campos de estudo.')
            try:
                dados = json.loads(corpo)
            except (ValueError, UnicodeError):
                raise TutoriaError('Envie um objeto JSON válido.') from None
            return jsonify(servicos().gerar_tutoria.executar(usuario_id, dados)), 200
        except RequestEntityTooLarge:
            return jsonify({'erro': 'O corpo deve ter no máximo 16 KiB.', 'codigo': 'corpo_muito_grande'}), 413
        except ErroAplicacao as erro:
            resposta = jsonify(erro.to_dict())
            if getattr(erro, 'retry_after', None) is not None:
                resposta.headers['Retry-After'] = str(erro.retry_after)
            return resposta, erro.status_code
        except Exception as erro:
            registrar_falha('Falha interna: tutoria.', erro)
            return jsonify({'erro': 'Não foi possível gerar a tutoria.', 'codigo': 'erro_interno'}), 500
