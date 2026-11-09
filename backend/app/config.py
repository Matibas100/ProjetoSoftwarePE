import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _database_uri():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    variable_names = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    missing = [name for name in variable_names if not os.getenv(name)]
    if missing:
        variables = ", ".join(missing)
        raise RuntimeError(
            f"Configuracao do MySQL incompleta. Defina no .env: {variables}."
        )

    user = quote_plus(os.environ["DB_USER"])
    password = quote_plus(os.environ["DB_PASSWORD"])
    host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    database = os.environ["DB_NAME"]
    charset = os.getenv("DB_CHARSET", "utf8mb4")

    return (
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        f"?charset={charset}"
    )


def _cors_origins():
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


class Config:
    TUTOR_IA_ENABLED = _as_bool(os.getenv('TUTOR_IA_ENABLED', 'false'))
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')
    AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "")
    AUTH_COOKIE_SECURE = _as_bool(os.getenv("AUTH_COOKIE_SECURE", "false"))
    DEBUG = _as_bool(os.getenv("FLASK_DEBUG", "false"))
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    CORS_ORIGINS = _cors_origins()
