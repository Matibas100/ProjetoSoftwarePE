from flask import Flask

from app.config import Config
from app.extensions import cors, db


def create_app(config_class=Config):
    """Cria e configura uma instancia da aplicacao Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
    )

    # O import registra as tabelas nos metadados do SQLAlchemy.
    from app import models  # noqa: F401
    from app.routes import api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api")

    return app
