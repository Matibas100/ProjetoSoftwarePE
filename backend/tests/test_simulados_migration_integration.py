from database import migrate
from tests.migration_integration_support import MySQLMigrationTestCase


class SimuladosMigrationIntegrationTest(MySQLMigrationTestCase):
    def setUp(self):
        super().setUp()
        self.migrations = self.migrations[:9]  # Este contrato valida especificamente o prefixo 008.

    def test_upgrade_007_vazio_reexecucao_e_marcador_gerado(self):
        migrate.run_up(self.connection,self.settings,self.migrations[:8])
        self.assertEqual(migrate.detect_legacy_prefix(self.connection),'007')
        self.assertEqual(migrate.run_up(self.connection,self.settings,self.migrations),1)
        self.assertEqual(migrate.run_up(self.connection,self.settings,self.migrations),0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection),'008')
        with self.connection.cursor() as c:
            for table in migrate.SIMULADOS_FINGERPRINTS:
                c.execute('SELECT COUNT(*) AS total FROM '+table)
                self.assertEqual(c.fetchone()['total'],0)
            c.execute("INSERT INTO usuarios(nome,email,senha_hash,perfil,ativo,criado_em) VALUES('Teste','teste@teste.local','hash','aluno',1,UTC_TIMESTAMP(6))")
            u=c.lastrowid
            c.execute("INSERT INTO simulados(titulo,estado,revisao,autor_id,criado_em,atualizado_em) VALUES('Teste','rascunho',1,%s,UTC_TIMESTAMP(6),UTC_TIMESTAMP(6))",(u,));s=c.lastrowid
            c.execute("INSERT INTO simulado_versoes(simulado_id,numero,revisao_origem,titulo,autor_id,criado_em) VALUES(%s,1,1,'Teste',%s,UTC_TIMESTAMP(6))",(s,u));v=c.lastrowid
            sql="INSERT INTO simulado_tentativas(usuario_id,simulado_versao_id,estado,revisao,chave_envio,iniciada_em) VALUES(%s,%s,'em_andamento',1,%s,UTC_TIMESTAMP(6))"
            c.execute(sql,(u,v,'00000000-0000-0000-0000-000000000001'));t=c.lastrowid
            with self.assertRaises(Exception):c.execute(sql,(u,v,'00000000-0000-0000-0000-000000000002'))
            for update in ["estado='finalizada'", "revisao=0", "estado='invalido'", "total=3"]:
                with self.assertRaises(Exception):c.execute('UPDATE simulado_tentativas SET '+update+' WHERE id=%s',(t,))
            for table,id_ in [('usuarios',u),('simulado_versoes',v),('simulados',s)]:
                with self.assertRaises(Exception):c.execute('DELETE FROM '+table+' WHERE id=%s',(id_,))
            c.execute("UPDATE simulado_tentativas SET estado='finalizada',finalizada_em=iniciada_em,total=3,respondidas=2,acertos=1,erros=1,em_branco=1,percentual_acerto=33.33 WHERE id=%s",(t,))
            c.execute(sql,(u,v,'00000000-0000-0000-0000-000000000002'))
            with self.assertRaises(Exception):c.execute(sql,(u,v,'00000000-0000-0000-0000-000000000001'))
        self.assertEqual(migrate.detect_legacy_prefix(self.connection),'008')

    def test_fingerprint_recusa_drift_e_tabela_parcial(self):
        for sql in ["ALTER TABLE simulado_tentativas DROP CHECK ck_sim_tentativa_estado",
            "ALTER TABLE simulado_tentativas DROP INDEX uq_sim_tentativa_andamento",
            "ALTER TABLE simulado_respostas DROP FOREIGN KEY fk_simulado_respostas_item_id",
            "ALTER TABLE simulado_versao_itens DROP CHECK ck_sim_item_posicao",
            "ALTER TABLE simulado_tentativas MODIFY chave_envio VARCHAR(36) NOT NULL"]:
            self.recreate_schema();migrate.run_up(self.connection,self.settings,self.migrations)
            with self.connection.cursor() as c:c.execute(sql)
            with self.assertRaises(migrate.MigrationError):migrate.detect_legacy_prefix(self.connection)
        self.recreate_schema();migrate.run_up(self.connection,self.settings,self.migrations[:8])
        with self.connection.cursor() as c:c.execute('CREATE TABLE simulados(id INT PRIMARY KEY)')
        with self.assertRaises(migrate.MigrationError):migrate.detect_legacy_prefix(self.connection)
