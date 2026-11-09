"""Adaptacao HTTP de identidade; toda regra de sessao fica nos Services."""
from flask import current_app, g, request

from app.modules.contas.controllers.autenticacao_controller import COOKIE, resposta_erro
from app.modules.contas.domain.autenticacao import AutenticacaoError
from app.http_response import registrar_falha
from app.modules.contas.services.autenticacao_service import AutorizarService, ConsultarSessaoService, ValidarCsrfService


def proteger_api():
    if request.url_rule is None or request.method == "OPTIONS" or not request.path.startswith("/api/"):
        return None
    if request.path in {"/api/health", "/api/auth/csrf"}:
        return None
    if request.path == "/api/termos" and request.method in {"GET", "HEAD"}:
        return None
    identificador = request.cookies.get(COOKIE)
    chave = current_app.config["AUTH_KEY_BYTES"]
    origens = current_app.config["CORS_ORIGINS"]
    origem = request.headers.get("Origin")
    csrf = request.headers.get("X-CSRF-Token")
    try:
        if request.path in {"/api/auth/login", "/api/auth/cadastro", "/api/auth/logout"}:
            if origem not in origens:
                raise AutenticacaoError("Origem não autorizada.", 403, "origem_nao_permitida")
            try:
                g.auth_sessao = ConsultarSessaoService.executar(identificador, autenticada=False)
            except AutenticacaoError:
                if request.path != "/api/auth/logout":
                    raise
                g.auth_sessao = None
            if g.auth_sessao is not None:
                ValidarCsrfService.executar(identificador, origem, origens, csrf, chave)
                if request.path != "/api/auth/logout" and g.auth_sessao.usuario_id is not None:
                    raise AutenticacaoError("Você já está autenticado.", 409, "ja_autenticado")
            return None
        leitura_catalogo = request.method in {"GET", "HEAD"} and request.path in {
            "/api/areas-enem", "/api/materias", "/api/assuntos"}
        rota_auth = request.path.startswith("/api/auth/")
        rota_tutoria = request.path == "/api/tutoria"
        rota_aluno = request.path.startswith("/api/aluno/") or rota_tutoria
        admin = not rota_auth and not rota_aluno and (not leitura_catalogo or request.args.get("status") == "todos")
        mutacao = request.method not in {"GET", "HEAD"}
        gestao_usuarios = request.path == "/api/admin/usuarios" or request.path.startswith("/api/admin/usuarios/")
        dados = None if rota_tutoria or gestao_usuarios else request.get_json(silent=True)
        sensivel = (gestao_usuarios and mutacao) or not rota_auth and (request.method == "DELETE" or
            request.path.rsplit("/", 1)[-1] in {"inativar", "arquivar", "reativar", "transferir", "publicar"} or
            (request.method == "PUT" and isinstance(dados, dict) and (
                ("/materias/" in request.path and bool({"status", "area_enem_id"} & dados.keys())) or
                ("/assuntos/" in request.path and "materia_id" in dados))))
        g.auth_sessao = AutorizarService.executar(identificador, admin, mutacao, origem,
            origens, csrf, chave, sensivel)
        if rota_aluno and g.auth_sessao.usuario.perfil != "aluno":
            raise AutenticacaoError("Você não tem acesso a esta operação.", 403, "acesso_negado")
    except AutenticacaoError as erro:
        return resposta_erro(erro)
    except Exception as erro:
        registrar_falha("Falha interna ao verificar identidade.", erro)
        return resposta_erro(AutenticacaoError("Não foi possível verificar sua sessão.", 500, "erro_interno"))
    return None


def sem_cache_auth(resposta):
    detalhe_catalogo = request.endpoint in {
        "api.conteudo.buscar_materia_por_id", "api.conteudo.buscar_assunto_por_id"}
    if detalhe_catalogo or request.path in {"/api/termos", "/api/tutoria"} or request.path.startswith(("/api/auth/", "/api/aluno/", "/api/admin/")) or getattr(g, "auth_sessao", None) is not None:
        resposta.headers["Cache-Control"] = "no-store"
    return resposta
