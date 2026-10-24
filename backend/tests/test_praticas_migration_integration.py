from database import migrate
from tests.migration_integration_support import MySQLMigrationTestCase


class PraticasMigrationIntegrationTest(MySQLMigrationTestCase):
    def test_upgrade_006_sem_historico_ficticio_e_reexecucao(self):
        migrate.run_up(self.connection,self.settings,self.migrations[:7])
        self.assertEqual(migrate.detect_legacy_prefix(self.connection),'006')
        self.assertEqual(migrate.run_up(self.connection,self.settings,self.migrations[:8]),1)
        self.assertEqual(migrate.run_up(self.connection,self.settings,self.migrations[:8]),0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection),'007')
        with self.connection.cursor() as c:
            c.execute('SELECT COUNT(*) AS total FROM pratica_tentativas')
            self.assertEqual(c.fetchone()['total'],0)
            c.execute("INSERT INTO usuarios (nome,email,senha_hash,perfil,ativo,criado_em) "
                "VALUES ('Teste','pratica@teste.local','hash','aluno',1,UTC_TIMESTAMP(6))")
            usuario=c.lastrowid
            c.execute("INSERT INTO materias(nome,area_enem_id) VALUES ('Teste',4)")
            materia=c.lastrowid
            c.execute("INSERT INTO assuntos(nome,nome_normalizado,materia_id) VALUES ('Teste','teste',%s)",(materia,))
            assunto=c.lastrowid
            c.execute("INSERT INTO questoes(enunciado,alternativa_a,alternativa_b,alternativa_c,alternativa_d,alternativa_e,resposta_correta,dificuldade,assunto_id) "
                "VALUES ('Q','A','B','C','D','E','A','media',%s)",(assunto,))
            questao=c.lastrowid
            c.execute("INSERT INTO questao_versoes(questao_id,numero,revisao_origem,estado,enunciado,alternativa_a,alternativa_b,alternativa_c,alternativa_d,alternativa_e,resposta_correta,dificuldade,assunto_id,assunto_nome,materia_id,materia_nome,area_enem_id,area_enem_nome,origem,criado_em) "
                "VALUES (%s,1,1,'publicada','Q','A','B','C','D','E','A','media',%s,'Teste',%s,'Teste',4,'Matemática','manual',UTC_TIMESTAMP(6))",(questao,assunto,materia))
            versao=c.lastrowid
            insert="INSERT INTO pratica_tentativas(usuario_id,questao_versao_id,chave_envio,estado,iniciada_em,assunto_id,assunto_nome,materia_id,materia_nome) VALUES (%s,%s,'00000000-0000-0000-0000-000000000001','em_andamento',UTC_TIMESTAMP(6),%s,'Teste',%s,'Teste')"
            c.execute(insert,(usuario,versao,assunto,materia)); tentativa=c.lastrowid
            with self.assertRaises(Exception): c.execute(insert,(usuario,versao,assunto,materia))
            for update in ["estado='invalido'","estado='respondida'","resposta_escolhida='A'",
                "estado='respondida',resposta_escolhida='Z',correta=0,respondida_em=iniciada_em",
                "estado='respondida',resposta_escolhida='a',correta=0,respondida_em=iniciada_em",
                "estado='respondida',resposta_escolhida='A',correta=2,respondida_em=iniciada_em"]:
                with self.assertRaises(Exception): c.execute('UPDATE pratica_tentativas SET '+update+' WHERE id=%s',(tentativa,))
            for tabela,id_ in [('usuarios',usuario),('questao_versoes',versao),('materias',materia),('assuntos',assunto)]:
                with self.assertRaises(Exception): c.execute('DELETE FROM '+tabela+' WHERE id=%s',(id_,))
            c.execute("UPDATE pratica_tentativas SET estado='respondida',resposta_escolhida='A',correta=1,respondida_em=iniciada_em WHERE id=%s",(tentativa,))

    def test_fingerprint_recusa_drift_de_praticas(self):
        for sql in ["ALTER TABLE pratica_tentativas DROP FOREIGN KEY fk_pratica_tentativas_usuario",
                    "ALTER TABLE pratica_tentativas DROP CHECK ck_pratica_tentativas_estado",
                    "ALTER TABLE pratica_tentativas MODIFY chave_envio VARCHAR(36) NOT NULL",
                    "ALTER TABLE pratica_tentativas DROP INDEX ix_pratica_tentativas_historico"]:
            self.recreate_schema()
            migrate.run_up(self.connection,self.settings,self.migrations)
            with self.connection.cursor() as c: c.execute(sql)
            with self.assertRaises(migrate.MigrationError): migrate.detect_legacy_prefix(self.connection)
