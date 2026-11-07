from flask import Flask

from app.config import Config
from app.extensions import cors, db


def create_app(config_class=Config):
    """Cria e configura uma instancia da aplicacao Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config.setdefault("AUTH_SECRET_KEY", Config.AUTH_SECRET_KEY)
    app.config.setdefault("AUTH_COOKIE_SECURE", Config.AUTH_COOKIE_SECURE)
    from app.modules.contas.domain.autenticacao import configurar_autenticacao
    configurar_autenticacao(app)

    db.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "X-CSRF-Token"],
    )

    # O import registra as tabelas nos metadados do SQLAlchemy.
    from app import models  # noqa: F401
    from app.composition import compor
    app.extensions['servicos'] = compor()
    from app.routes import api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api")
    from app.modules.contas.auth_http import proteger_api, sem_cache_auth
    from app.modules.contas.auth_cli import registrar_comandos
    app.before_request(proteger_api)
    app.after_request(sem_cache_auth)
    registrar_comandos(app)

    return app
