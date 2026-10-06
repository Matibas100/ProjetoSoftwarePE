"""Infraestrutura segura compartilhada pelos testes MySQL da API."""

from __future__ import annotations

import os
import re
import unittest
from dataclasses import replace
from urllib.parse import quote_plus
from uuid import uuid4

import pymysql
from pymysql.cursors import DictCursor
from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db
from database import migrate


API_TEST_PREFIX = "plataforma_enem_api_test_"
SAFE_API_TEST_SCHEMA = re.compile(rf"^{API_TEST_PREFIX}[a-f0-9]{{12}}$")


def validate_api_test_schema(name):
    if not SAFE_API_TEST_SCHEMA.fullmatch(name):
        raise RuntimeError("Nome de schema descartavel recusado por seguranca.")
    return name


class MySQLIntegrationTestCase(unittest.TestCase):
    required_tables = {
        "areas_enem", "materias", "assuntos", "questoes", "assunto_transferencias"
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if os.getenv("RUN_MYSQL_INTEGRATION") != "1":
            raise RuntimeError(
                "Integracoes MySQL bloqueadas. Defina RUN_MYSQL_INTEGRATION=1 "
                "somente no processo de teste para autorizar conexao e escrita."
            )
        base = migrate.load_database_settings()
        cls.schema_name = validate_api_test_schema(API_TEST_PREFIX + uuid4().hex[:12])
        cls.admin_connection = pymysql.connect(
            host=base.host,
            port=base.port,
            user=base.user,
            password=base.password,
            charset=base.charset,
            autocommit=True,
            cursorclass=DictCursor,
        )
        with cls.admin_connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE `{cls.schema_name}` CHARACTER SET utf8mb4 "
                "COLLATE utf8mb4_unicode_ci"
            )
        settings = replace(base, name=cls.schema_name)
        connection = migrate.connect(settings)
        try:
            migrate.run_up(connection, settings, migrate.discover_migrations())
        finally:
            connection.close()

        class TestConfig:
            TESTING = True
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{quote_plus(settings.user)}:{quote_plus(settings.password)}"
                f"@{settings.host}:{settings.port}/{settings.name}?charset={settings.charset}"
            )
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            CORS_ORIGINS = []

        cls.app = create_app(TestConfig)
        cls.app.logger.disabled = True
        cls.client = cls.app.test_client()
        try:
            with cls.app.app_context():
                db.session.execute(text("SELECT 1"))
                tables = set(inspect(db.engine).get_table_names())
                if cls.required_tables - tables:
                    raise RuntimeError("Infraestrutura MySQL incompleta.")
        except Exception as error:
            cls._drop_schema()
            raise RuntimeError("Preflight MySQL falhou no schema descartavel.") from error

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "app"):
            with cls.app.app_context():
                db.session.remove()
                db.engine.dispose()
        cls._drop_schema()
        super().tearDownClass()

    @classmethod
    def _drop_schema(cls):
        if not hasattr(cls, "admin_connection"):
            return
        name = validate_api_test_schema(cls.schema_name)
        try:
            with cls.admin_connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS `{name}`")
        finally:
            cls.admin_connection.close()
