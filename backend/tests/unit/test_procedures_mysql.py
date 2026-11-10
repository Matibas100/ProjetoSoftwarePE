"""Protocolo do cursor e propriedade da conexão, sem MySQL."""
import unittest
from unittest.mock import MagicMock

from app.core.procedures_mysql import conferir_resultados, executar_resultados


class ProceduresMySQLTest(unittest.TestCase):
    def preparar(self, conjuntos):
        conexao = MagicMock()
        cursor = conexao.connection.driver_connection.cursor.return_value
        posicao = [0]
        cursor.description = conjuntos[0][0]
        cursor.fetchall.side_effect = lambda: conjuntos[posicao[0]][1]

        def proximo():
            posicao[0] += 1
            if posicao[0] >= len(conjuntos):
                return None
            cursor.description = conjuntos[posicao[0]][0]
            return True

        cursor.nextset.side_effect = proximo
        return conexao, cursor

    def test_vazio_util_terminal_parametros_e_conexao_emprestada(self):
        conexao, cursor = self.preparar([
            ([('id',)], []),
            ([('total',)], [(8,)]),
            (None, [])
        ])
        valores = ("' OR 1=1 --",)
        resultado = executar_resultados(conexao, 'comando %s', valores)
        self.assertEqual(resultado, [[], [{'total': 8}]])
        conferir_resultados(resultado, [('id',), ('total',)])
        cursor.execute.assert_called_once_with('comando %s', valores)
        cursor.close.assert_called_once()
        for operacao in ['commit', 'rollback', 'close', 'invalidate']:
            getattr(conexao, operacao).assert_not_called()

    def test_falha_no_consumo_drena_e_libera_sem_mascarar(self):
        conexao, cursor = self.preparar([([('id',)], []), (None, [])])
        cursor.fetchall.side_effect = RuntimeError('consumo')
        with self.assertRaisesRegex(RuntimeError, 'consumo'):
            executar_resultados(conexao, 'comando', ())
        cursor.close.assert_called_once()
        conexao.invalidate.assert_not_called()

    def test_falha_de_protocolo_invalida_conexao_e_fecha_cursor(self):
        conexao, cursor = self.preparar([([('id',)], [])])
        cursor.nextset.side_effect = RuntimeError('protocolo')
        with self.assertRaisesRegex(RuntimeError, 'protocolo'):
            executar_resultados(conexao, 'comando')
        self.assertTrue(conexao.invalidate.called)
        cursor.close.assert_called_once()

    def test_resultados_inesperados_inclusive_colunas_no_vazio(self):
        conexao, _ = self.preparar([([('id',)], [])])
        resultado = executar_resultados(conexao, 'comando')
        for contratos in [[], [('total',)], [('id', 'outra')]]:
            with self.assertRaises(ValueError):
                conferir_resultados(resultado, contratos)

    def test_erro_ao_fechar_invalida(self):
        conexao, cursor = self.preparar([(None, [])])
        cursor.close.side_effect = RuntimeError('close')
        with self.assertRaisesRegex(RuntimeError, 'close'):
            executar_resultados(conexao, 'comando')
        conexao.invalidate.assert_called_once()
