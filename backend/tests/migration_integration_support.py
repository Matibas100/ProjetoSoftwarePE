"""Suporte isolado e destrutivo somente para integrações do runner SQL."""

from __future__ import annotations

import os
import re
import unittest
from dataclasses import replace
from uuid import uuid4

import pymysql
from pymysql.cursors import DictCursor

from database import migrate


MIGRATION_TEST_PREFIX = "plataforma_enem_migration_test_"
SAFE_MIGRATION_TEST_SCHEMA = re.compile(
    rf"^{MIGRATION_TEST_PREFIX}[a-f0-9]{{12}}$"
)


def validate_migration_test_schema(name: str) -> str:
    if not SAFE_MIGRATION_TEST_SCHEMA.fullmatch(name):
        raise RuntimeError("Nome de schema descartavel recusado por seguranca.")
    return name


@unittest.skipUnless(
    os.getenv("RUN_MYSQL_MIGRATION_INTEGRATION") == "1",
    "Migrations MySQL exigem RUN_MYSQL_MIGRATION_INTEGRATION=1.",
)
class MySQLMigrationTestCase(unittest.TestCase):
    """Cria e remove somente um schema aleatório reconhecido como descartável."""

    def setUp(self):
        super().setUp()
        if os.getenv("RUN_MYSQL_INTEGRATION") != "1":
            self.fail("RUN_MYSQL_INTEGRATION=1 tambem e obrigatorio.")
        self.base_settings = migrate.load_database_settings()
        self.schema_name = validate_migration_test_schema(
            MIGRATION_TEST_PREFIX + uuid4().hex[:12]
        )
        self.admin_connection = pymysql.connect(
            host=self.base_settings.host,
            port=self.base_settings.port,
            user=self.base_settings.user,
            password=self.base_settings.password,
            charset=self.base_settings.charset,
            autocommit=True,
            cursorclass=DictCursor,
        )
        self._create_schema()
        self.settings = replace(self.base_settings, name=self.schema_name)
        self.connection = migrate.connect(self.settings)
        self.migrations = migrate.discover_migrations()

    def tearDown(self):
        if hasattr(self, "connection"):
            self.connection.close()
        if hasattr(self, "admin_connection"):
            try:
                self._drop_schema()
            finally:
                self.admin_connection.close()
        super().tearDown()

    def _create_schema(self):
        name = validate_migration_test_schema(self.schema_name)
        with self.admin_connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4 "
                "COLLATE utf8mb4_unicode_ci"
            )

    def _drop_schema(self):
        name = validate_migration_test_schema(self.schema_name)
        with self.admin_connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{name}`")

    def recreate_schema(self):
        self.connection.close()
        self._drop_schema()
        self._create_schema()
        self.connection = migrate.connect(self.settings)

    def apply_without_history(self, last_version: str):
        for item in self.migrations[: int(last_version) + 1]:
            migrate.execute_statements(
                self.connection,
                migrate.validate_statements(migrate.split_sql(item.sql)),
            )
