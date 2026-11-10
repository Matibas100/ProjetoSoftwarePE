import unittest
from unittest.mock import Mock, patch

from database import sql_resources as recursos
from database.migration_types import MigrationError


class RecursosSQLTest(unittest.TestCase):
    @patch.object(recursos, 'inventariar')
    def test_presenca_e_indisponibilidade_do_inventario(self, inventario):
        inventario.return_value = ({'sp_materias_admin'}, set())
        self.assertTrue(recursos.possui_recursos(Mock()))
        inventario.return_value = (set(), set())
        self.assertFalse(recursos.possui_recursos(Mock()))
        inventario.side_effect = KeyError('metadado')
        with self.assertRaisesRegex(MigrationError, 'indisponível'):
            recursos.possui_recursos(Mock())

    def test_normaliza_so_schema_identificador_local(self):
        sql = "SELECT `origem`.`id`, `externo`.`id`, '`origem`.literal', 'A\\'B' FROM `origem`.`t`"
        normalizado = recursos.normalizar_schema(sql, 'origem')
        self.assertEqual(
            normalizado,
            "SELECT `<local>`.`id`, `externo`.`id`, '`origem`.literal', 'A\\'B' FROM `<local>`.`t`"
        )
        for valor in ['', None]:
            with self.assertRaises(ValueError):
                recursos.normalizar_schema(valor, 'origem')

    @patch.object(recursos, 'inventariar')
    def test_ausente_historico_e_parcial_sem_recuo(self, inventario):
        inventario.return_value = ({'sp_questoes_por_assunto'}, set())
        self.assertIsNone(recursos.detectar_prefixo(Mock()))
        for nomes in [{'sp_materias_admin'}, recursos.PROCEDURES_011 | {'sp_desempenho_resumo'}]:
            inventario.return_value = (nomes, set())
            with self.assertRaisesRegex(MigrationError, 'parciais'):
                recursos.detectar_prefixo(Mock())

    @patch.object(recursos, 'assinatura', return_value='divergente')
    @patch.object(recursos, 'inventariar', return_value=(recursos.PROCEDURES_011, set()))
    def test_corpo_ou_assinatura_divergente_recusados(self, inventario, assinatura):
        with self.assertRaisesRegex(MigrationError, 'divergente'):
            recursos.detectar_prefixo(Mock())

    def test_metadados_ausentes_falham_fechado(self):
        # Um gerenciador real de mock para evitar qualquer conexão/ambiente.
        from unittest.mock import MagicMock
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value.fetchone.return_value = {}
        with self.assertRaisesRegex(MigrationError, 'indisponíveis'):
            recursos.assinatura(connection, 'sp_materias_admin')
        with self.assertRaisesRegex(MigrationError, 'indisponíveis'):
            recursos.assinatura(connection, 'desconhecido')

    def test_schema_externo_nao_colide_com_marcador_local(self):
        from unittest.mock import MagicMock

        def assinatura(schema_referenciado):
            conexao = MagicMock()
            cursor = conexao.cursor.return_value.__enter__.return_value
            cursor.fetchone.side_effect = [
                {'nome': 'origem'},
                {
                    'VIEW_DEFINITION': f'SELECT `{schema_referenciado}`.`t`.`id` FROM `{schema_referenciado}`.`t`',
                    'CHECK_OPTION': 'NONE',
                    'IS_UPDATABLE': 'YES',
                    'SECURITY_TYPE': 'INVOKER',
                    'CHARACTER_SET_CLIENT': 'utf8mb4',
                    'COLLATION_CONNECTION': 'utf8mb4_unicode_ci'
                },
            ]
            cursor.fetchall.side_effect = [
                [{
                    'ORDINAL_POSITION': 1,
                    'COLUMN_NAME': 'id',
                    'COLUMN_TYPE': 'int',
                    'IS_NULLABLE': 'NO',
                    'CHARACTER_SET_NAME': None,
                    'COLLATION_NAME': None
                }],
                [{'TABLE_SCHEMA': schema_referenciado, 'TABLE_NAME': 't'}],
            ]
            return recursos.assinatura(conexao, 'vw_conteudo_classificacao_historica')

        self.assertNotEqual(assinatura('origem'), assinatura('<local>'))
