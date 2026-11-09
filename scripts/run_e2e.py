"""Executa Chromium com API/frontend locais e schema MySQL descartável."""
from __future__ import annotations

import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import time
from dataclasses import replace
from urllib.parse import quote_plus
from urllib.request import urlopen
from uuid import uuid4

import pymysql

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from database import migrate

PREFIX = "plataforma_enem_e2e_test_"
SAFE_SCHEMA = re.compile(rf"{PREFIX}[a-f0-9]{{12}}")


def validar_schema(nome):
    if not isinstance(nome, str) or not SAFE_SCHEMA.fullmatch(nome):
        raise ValueError("Nome de schema E2E recusado.")
    return nome


def exigir_opt_in(environment):
    if environment.get("RUN_MYSQL_E2E") != "1":
        raise RuntimeError("E2E bloqueado: defina RUN_MYSQL_E2E=1 somente no processo.")


def porta_livre():
    with socket.socket() as connection:
        connection.bind(("127.0.0.1", 0))
        return connection.getsockname()[1]


def aguardar_http(url, processo):
    limite = time.monotonic() + 30
    while time.monotonic() < limite:
        if processo.poll() is not None:
            raise RuntimeError("Servidor local E2E encerrou antes de iniciar.")
        try:
            with urlopen(url, timeout=1) as resposta:
                if resposta.status == 200:
                    return
        except (OSError, TimeoutError):
            time.sleep(.1)
    raise RuntimeError("Servidor local E2E não ficou disponível.")


def encerrar(processos):
    for processo in reversed(processos):
        if processo.poll() is None:
            processo.terminate()
            try:
                processo.wait(timeout=10)
            except subprocess.TimeoutExpired:
                processo.kill()
                processo.wait(timeout=10)


def executar_suite(base, environment, comando=None):
    exigir_opt_in(environment)
    nome = validar_schema(PREFIX + uuid4().hex[:12])
    settings = replace(base, name=nome)
    api_port, frontend_port = porta_livre(), porta_livre()
    while frontend_port == api_port:
        frontend_port = porta_livre()
    frontend = f"http://127.0.0.1:{frontend_port}"
    api = f"http://127.0.0.1:{api_port}"
    env = {**environment, "PYTHON_DOTENV_DISABLED": "1", "PYTHONPATH": str(ROOT / "backend"),
        "DATABASE_URL": f"mysql+pymysql://{quote_plus(settings.user)}:{quote_plus(settings.password)}"
            f"@{settings.host}:{settings.port}/{nome}?charset={settings.charset}",
        "AUTH_SECRET_KEY": secrets.token_hex(32), "AUTH_COOKIE_SECURE": "false",
        "FLASK_DEBUG": "false", "CORS_ORIGINS": frontend, "APP_HOST": "127.0.0.1",
        "APP_PORT": str(api_port), "E2E_BASE_URL": frontend, "E2E_API_URL": api + "/api",
        "E2E_ADMIN_EMAIL": f"operador-{uuid4().hex[:12]}@teste.local",
        "E2E_ADMIN_PASSWORD": secrets.token_urlsafe(24), "E2E_SCHEMA": nome}
    env.pop('GEMINI_API_KEY', None)
    env['TUTOR_IA_ENABLED'] = 'false'
    env["E2E_STUDENT_EMAIL"] = f"aluno-{uuid4().hex[:12]}@teste.local"
    env["E2E_STUDENT_PASSWORD"] = secrets.token_urlsafe(24)
    env['E2E_TUTOR_EMAIL'] = f"tutor-{uuid4().hex[:12]}@teste.local"
    env['E2E_TUTOR_PASSWORD'] = secrets.token_urlsafe(24)
    admin = pymysql.connect(host=base.host, port=base.port, user=base.user,
        password=base.password, charset=base.charset, autocommit=True)
    criado = False
    processos = []
    try:
        with admin.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE `{nome}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        criado = True
        connection = migrate.connect(settings)
        try:
            migrate.run_up(connection, settings, migrate.discover_migrations())
        finally:
            connection.close()
        # O setup cria somente o operador; os casos avaliados usam a interface.
        seed = """import os
from app import create_app
from app.extensions import db
from app.modules.contas.services.autenticacao_service import CriarUsuarioService
from app.modules.contas.domain.privacidade import DOCUMENTOS
from app.modules.contas.models.registro_privacidade import RegistroPrivacidade
from uuid import uuid4
app = create_app()
with app.app_context():
    senha = os.environ['E2E_ADMIN_PASSWORD']
    CriarUsuarioService.executar({'nome':'Operador sintético', 'email':os.environ['E2E_ADMIN_EMAIL'],
        'senha':senha, 'senha_confirmacao':senha}, 'administrador')
    senha_tutor = os.environ['E2E_TUTOR_PASSWORD']
    legado = CriarUsuarioService.executar({'nome':'Estudante de revisão', 'email':os.environ['E2E_TUTOR_EMAIL'],
        'senha':senha_tutor, 'senha_confirmacao':senha_tutor}, 'aluno')
    doc = DOCUMENTOS['uso']['1.0']
    RegistroPrivacidade(usuario_id=legado['id'], tipo='uso', acao='aceitar', versao='1.0',
        documento_sha256=doc['sha256'], chave_envio=str(uuid4()), revisao_base=0).salvar()
    db.session.remove()
    db.engine.dispose()
"""
        subprocess.run([sys.executable, "-c", seed], cwd=ROOT, env=env, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for args, url in (([sys.executable, "backend/run.py"], api + "/api/health"),
                          ([sys.executable, "scripts/serve_frontend.py", "--port", str(frontend_port)], frontend + "/login")):
            processo = subprocess.Popen(args, cwd=ROOT, env=env,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            processos.append(processo)
            aguardar_http(url, processo)
        print("E2E: MySQL descartável preparado; API/frontend locais disponíveis.", flush=True)
        args = comando or ["node", "node_modules/@playwright/test/cli.js", "test"]
        return subprocess.run(args, cwd=ROOT, env=env, timeout=900).returncode
    finally:
        try:
            encerrar(processos)
        finally:
            try:
                if criado:
                    with admin.cursor() as cursor:
                        cursor.execute(f"DROP DATABASE `{validar_schema(nome)}`")
                    print("E2E: schema descartável removido.", flush=True)
            finally:
                admin.close()


def main():
    try:
        env = dict(os.environ)
        exigir_opt_in(env)
        return executar_suite(migrate.load_database_settings(env), env)
    except KeyboardInterrupt:
        print("E2E interrompido; limpeza executada.", file=sys.stderr)
        return 130
    except Exception as erro:
        # Não revelar mensagem/SQL/parâmetros/credenciais de infraestrutura.
        print(f"E2E falhou ({type(erro).__name__}). Confira opt-in, MySQL e instalação do Chromium.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
