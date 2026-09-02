"""Infraestrutura segura compartilhada pelos testes MySQL."""

from __future__ import annotations

import os
import unittest

from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db


class MySQLIntegrationTestCase(unittest.TestCase):
    required_tables = {"materias", "assuntos", "questoes"}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if os.getenv("RUN_MYSQL_INTEGRATION") != "1":
            raise RuntimeError(
                "Integracoes MySQL bloqueadas. Defina RUN_MYSQL_INTEGRATION=1 "
                "somente no processo de teste para autorizar conexao e escrita."
            )

        cls.app = create_app()
        cls.app.config.update(TESTING=True)
        cls.app.logger.disabled = True
        cls.client = cls.app.test_client()
        try:
            with cls.app.app_context():
                db.session.execute(text("SELECT 1"))
                tables = set(inspect(db.engine).get_table_names())
                missing = cls.required_tables - tables
                if missing:
                    raise RuntimeError(
                        "Infraestrutura MySQL incompleta: tabelas obrigatorias ausentes."
                    )
                procedure = db.session.execute(
                    text(
                        "SELECT COUNT(*) FROM information_schema.ROUTINES "
                        "WHERE ROUTINE_SCHEMA = DATABASE() "
                        "AND ROUTINE_TYPE = 'PROCEDURE' "
                        "AND ROUTINE_NAME = 'sp_questoes_por_assunto'"
                    )
                ).scalar_one()
                if procedure != 1:
                    raise RuntimeError(
                        "Infraestrutura MySQL incompleta: Stored Procedure obrigatoria ausente."
                    )
        except Exception as error:
            raise RuntimeError(
                "Preflight MySQL falhou. Verifique servidor, schema, tabelas e Stored Procedure."
            ) from error
