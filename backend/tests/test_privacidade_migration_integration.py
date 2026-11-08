from pathlib import Path
from uuid import uuid4

from database import migrate
from tests.migration_integration_support import MySQLMigrationTestCase


class PrivacidadeMigrationIntegrationTest(MySQLMigrationTestCase):
    def test_upgrade_sem_backfill_preserva_planos_e_reexecuta(self):
        migrate.run_up(self.connection, self.settings, self.migrations[:10])
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), "009")
        with self.connection.cursor() as c:
            c.execute("INSERT INTO materias(nome,area_enem_id) VALUES('Upgrade privacidade',4)");materia=c.lastrowid
            c.execute("INSERT INTO assuntos(nome,nome_normalizado,materia_id) VALUES('Upgrade','upgrade',%s)",(materia,));assunto=c.lastrowid
            c.execute("INSERT INTO questoes(enunciado,alternativa_a,alternativa_b,alternativa_c,alternativa_d,alternativa_e,resposta_correta,dificuldade,assunto_id) VALUES('Upgrade','A','B','C','D','E','A','media',%s)",(assunto,));questao=c.lastrowid
            c.execute("INSERT INTO questao_versoes(questao_id,numero,revisao_origem,estado,enunciado,alternativa_a,alternativa_b,alternativa_c,alternativa_d,alternativa_e,resposta_correta,dificuldade,assunto_id,assunto_nome,materia_id,materia_nome,area_enem_id,area_enem_nome,origem,criado_em) VALUES(%s,1,1,'publicada','Upgrade','A','B','C','D','E','A','media',%s,'Upgrade',%s,'Upgrade privacidade',4,'Matemática','manual',UTC_TIMESTAMP(6))",(questao,assunto,materia));versao=c.lastrowid
            for n in range(2):
                c.execute("INSERT INTO usuarios(nome,email,senha_hash,perfil,ativo,criado_em) VALUES('Teste',%s,'hash','aluno',1,UTC_TIMESTAMP(6))", (f'{n}@teste.local',))
                u = c.lastrowid
                c.execute("INSERT INTO planos_estudo(usuario_id,geracao,atual,periodo,gerado_em,chave_envio,operacao) VALUES(%s,1,1,JSON_OBJECT(),UTC_TIMESTAMP(6),%s,'gerar')", (u,str(uuid4())))
                plano=c.lastrowid
                c.execute("INSERT INTO plano_estudo_itens(plano_id,assunto_id,materia_id,posicao,snapshot,estado) VALUES(%s,%s,%s,1,JSON_OBJECT(),'pendente')",(plano,assunto,materia))
                c.execute("INSERT INTO pratica_tentativas(usuario_id,questao_versao_id,chave_envio,estado,resposta_escolhida,correta,iniciada_em,respondida_em,assunto_id,assunto_nome,materia_id,materia_nome) VALUES(%s,%s,%s,'respondida','A',1,'2026-11-06 12:00:00','2026-11-06 12:01:00',%s,'Upgrade',%s,'Upgrade privacidade')",(u,versao,str(uuid4()),assunto,materia))
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations[:11]), 1)
        self.assertEqual(migrate.run_up(self.connection, self.settings, self.migrations[:11]), 0)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection), "010")
        with self.connection.cursor() as c:
            for table, expected in (("usuarios",2),("planos_estudo",2),("plano_estudo_itens",2),("pratica_tentativas",2),("registros_privacidade",0)):
                c.execute(f"SELECT COUNT(*) AS n FROM {table}"); self.assertEqual(c.fetchone()['n'], expected)
            c.execute("SELECT resposta_escolhida,correta,respondida_em FROM pratica_tentativas ORDER BY id")
            for row in c.fetchall():
                self.assertEqual((row['resposta_escolhida'],row['correta']),('A',1))
                self.assertEqual(row['respondida_em'].isoformat(),'2026-11-06T12:01:00')

    def test_constraints_obrigatoriedade_usuario_e_combinacoes(self):
        migrate.run_up(self.connection, self.settings, self.migrations)
        with self.connection.cursor() as c:
            c.execute("INSERT INTO usuarios(nome,email,senha_hash,perfil,ativo,criado_em) VALUES('Teste','registro@teste.local','hash','aluno',1,UTC_TIMESTAMP(6))")
            usuario = c.lastrowid
            sql = "INSERT INTO registros_privacidade(usuario_id,tipo,acao,versao,documento_sha256,registrado_em,chave_envio,revisao_base) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
            from datetime import datetime
            valido = [usuario,'uso','aceitar','1.0','a'*64,datetime(2026,11,6),str(uuid4()),0]
            c.execute(sql, valido)
            with self.assertRaises(Exception): c.execute(sql, valido)
            for index, value in [(0,999999),(1,'invalido'),(2,'recusar'),(2,'revogar'),(7,-1)]+[(i,None) for i in range(8)]:
                dados = valido.copy(); dados[6] = str(uuid4()); dados[index] = value
                with self.subTest(index=index,value=value), self.assertRaises(Exception): c.execute(sql,dados)
            for acao in ('aceitar','recusar','revogar'):
                dados=valido.copy(); dados[1]='plano';dados[2]=acao;dados[6]=str(uuid4()); c.execute(sql,dados)
            with self.assertRaises(Exception): c.execute('DELETE FROM usuarios WHERE id=%s',(usuario,))

    def test_snapshot_baseline_equivalencia_drift_e_instalacao_vazia(self):
        migrate.run_up(self.connection, self.settings, self.migrations)
        self.assertEqual(migrate.detect_legacy_prefix(self.connection),'016')
        with self.connection.cursor() as c:
            c.execute('SHOW CREATE TABLE registros_privacidade'); ddl=c.fetchone()['Create Table']
        self.recreate_schema()
        snapshot=(Path(__file__).resolve().parents[1]/'database/create_database.sql').read_text(encoding='utf-8')
        statements=[s for s in migrate.split_sql(snapshot) if not s.upper().startswith(('CREATE DATABASE','USE '))]
        migrate.execute_statements(self.connection,migrate.validate_statements(statements))
        self.assertEqual(migrate.run_baseline(self.connection,self.settings,self.migrations,confirmed=True),'016')
        self.assertEqual(migrate.run_up(self.connection,self.settings,self.migrations),0)
        with self.connection.cursor() as c:
            c.execute('SHOW CREATE TABLE registros_privacidade'); self.assertEqual(c.fetchone()['Create Table'],ddl)
            c.execute('ALTER TABLE registros_privacidade DROP CHECK ck_privacidade_revisao')
        with self.assertRaises(migrate.MigrationError): migrate.detect_legacy_prefix(self.connection)
