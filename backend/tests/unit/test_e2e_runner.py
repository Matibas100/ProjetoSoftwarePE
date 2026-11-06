"""Guardrails e limpeza do runner; integração de produto usa MySQL/Chromium reais."""
import os
import unittest
from unittest.mock import MagicMock, patch

from database.migrate import DatabaseSettings
from scripts import run_e2e as runner


class E2ERunnerTest(unittest.TestCase):
    def test_sem_opt_in_nao_conecta(self):
        with patch.object(runner.pymysql, 'connect') as conectar:
            with self.assertRaises(RuntimeError):
                runner.executar_suite(None, {})
            conectar.assert_not_called()

    def test_schema_recusa_nomes_operacionais_e_injecao(self):
        for name in (None, '', 'plataforma_enem', runner.PREFIX + 'a'*11,
                     runner.PREFIX + 'a'*13, runner.PREFIX+'A'*12,
                     runner.PREFIX+'a'*12+'; DROP DATABASE x', runner.PREFIX+'a'*12+'\n'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                runner.validar_schema(name)
        self.assertEqual(runner.validar_schema(runner.PREFIX+'a'*12), runner.PREFIX+'a'*12)

    def ambiente(self, falha=None, retorno=0):
        base = DatabaseSettings('127.0.0.1', 3306, 'operacional', 'test', 'senha-sentinela')
        admin = MagicMock()
        processo = MagicMock()
        processo.poll.return_value = None
        with patch.object(runner.pymysql, 'connect', return_value=admin), \
             patch.object(runner.migrate, 'connect') as conectar, \
             patch.object(runner.migrate, 'run_up', side_effect=falha), \
             patch.object(runner.subprocess, 'Popen', return_value=processo), \
             patch.object(runner.subprocess, 'run', side_effect=[MagicMock(returncode=0), MagicMock(returncode=retorno)]), \
             patch.object(runner, 'aguardar_http'):
            if falha:
                with self.assertRaises(RuntimeError):
                    runner.executar_suite(base, {'RUN_MYSQL_E2E':'1'})
            else:
                self.assertEqual(runner.executar_suite(base, {'RUN_MYSQL_E2E':'1'}), retorno)
                self.assertEqual(processo.terminate.call_count, 2)
            conectar.return_value.close.assert_called_once()
        statements = [call.args[0] for call in admin.cursor.return_value.__enter__.return_value.execute.call_args_list]
        self.assertEqual(len(statements), 2)
        self.assertTrue(statements[0].startswith('CREATE DATABASE `'+runner.PREFIX))
        self.assertTrue(statements[1].startswith('DROP DATABASE `'+runner.PREFIX))
        self.assertNotIn('operacional', ''.join(statements))
        admin.close.assert_called_once()

    def test_limpa_apos_sucesso(self):
        self.ambiente()

    def test_limpa_apos_falha_browser(self):
        self.ambiente(retorno=1)

    def test_limpa_apos_falha_migration(self):
        self.ambiente(falha=RuntimeError('sentinela'))

    def test_main_nao_expoe_excecao(self):
        with patch.dict(os.environ, {}, clear=True), patch('builtins.print') as print_:
            self.assertEqual(runner.main(), 1)
            self.assertNotIn('senha-sentinela', str(print_.call_args))
