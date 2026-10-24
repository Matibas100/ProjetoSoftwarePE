from database import migrate
from tests.migration_integration_support import MySQLMigrationTestCase


class PlanosMigrationIntegrationTest(MySQLMigrationTestCase):
    def test_upgrade_vazio_reexecucao_constraints_e_historico(self):
        migrate.run_up(self.connection, self.settings, self.migrations[:9])
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), '008')
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 1)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations), 0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), '009')
        with self.connection.cursor() as c:
            for table in migrate.PLANOS_FINGERPRINTS:
                c.execute('SELECT COUNT(*) AS n FROM '+table); self.assertEqual(c.fetchone()['n'], 0)
            c.execute("INSERT INTO usuarios(nome,email,senha_hash,perfil,ativo,criado_em) VALUES('Teste','plano@teste.local','hash','aluno',1,UTC_TIMESTAMP(6))");u=c.lastrowid
            c.execute("INSERT INTO materias(nome,area_enem_id) VALUES('Plano',4)");m=c.lastrowid
            c.execute("INSERT INTO assuntos(nome,nome_normalizado,materia_id) VALUES('Plano','plano',%s)",(m,));a=c.lastrowid
            sql="INSERT INTO planos_estudo(usuario_id,geracao,atual,periodo,gerado_em,chave_envio,operacao,plano_anterior_id) VALUES(%s,%s,1,JSON_OBJECT(),UTC_TIMESTAMP(6),%s,%s,%s)"
            c.execute(sql,(u,1,'00000000-0000-0000-0000-000000000001','gerar',None));p=c.lastrowid
            for dados in [(u,2,'00000000-0000-0000-0000-000000000002','recalcular',p),
                (999999,1,'00000000-0000-0000-0000-000000000003','gerar',None)]:
                with self.assertRaises(Exception):c.execute(sql,dados)
            item="INSERT INTO plano_estudo_itens(plano_id,assunto_id,materia_id,posicao,snapshot,estado) VALUES(%s,%s,%s,%s,JSON_OBJECT(),'pendente')"
            c.execute(item,(p,a,m,1));i=c.lastrowid
            for args in [(p,a,m,1),(p,a,m,2),(p,a,m,4),(999999,a,m,1),(p,999999,m,2)]:
                with self.assertRaises(Exception):c.execute(item,args)
            with self.assertRaises(Exception):c.execute("UPDATE plano_estudo_itens SET estado='concluido' WHERE id=%s",(i,))
            c.execute("UPDATE plano_estudo_itens SET estado='concluido',concluido_em=UTC_TIMESTAMP(6) WHERE id=%s",(i,))
            c.execute('UPDATE planos_estudo SET atual=0 WHERE id=%s',(p,))
            c.execute(sql,(u,2,'00000000-0000-0000-0000-000000000002','recalcular',p))
            for args in [(u,2,'00000000-0000-0000-0000-000000000003','gerar',None),
                (u,3,'00000000-0000-0000-0000-000000000001','gerar',None)]:
                with self.assertRaises(Exception):c.execute(sql,args)
            for table,id_ in [('usuarios',u),('materias',m),('assuntos',a),('planos_estudo',p)]:
                with self.assertRaises(Exception):c.execute('DELETE FROM '+table+' WHERE id=%s',(id_,))
            c.execute('SELECT estado,concluido_em FROM plano_estudo_itens WHERE id=%s',(i,))
            r=c.fetchone();self.assertEqual(r['estado'],'concluido');self.assertIsNotNone(r['concluido_em'])

    def test_fingerprint_recusa_drift_e_tabela_parcial(self):
        for sql in ['ALTER TABLE planos_estudo DROP INDEX uq_plano_atual',
            'ALTER TABLE plano_estudo_itens DROP CHECK ck_plano_item_posicao',
            'ALTER TABLE plano_estudo_itens DROP FOREIGN KEY fk_plano_item_assunto']:
            self.recreate_schema();migrate.run_up(self.connection,self.settings,self.migrations)
            with self.connection.cursor() as c:c.execute(sql)
            with self.assertRaises(migrate.MigrationError):migrate.detect_legacy_prefix(self.connection)
        self.recreate_schema();migrate.run_up(self.connection,self.settings,self.migrations[:9])
        with self.connection.cursor() as c:c.execute('CREATE TABLE planos_estudo(id INT PRIMARY KEY)')
        with self.assertRaises(migrate.MigrationError):migrate.detect_legacy_prefix(self.connection)
