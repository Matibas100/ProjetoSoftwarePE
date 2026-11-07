"""Reconhecimento dos schemas históricos aceitos pelo baseline oficial."""

from __future__ import annotations

import hashlib
import re

from database.migration_types import MigrationError


HISTORY_TABLE = "schema_migrations"


def _user_tables(connection) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT TABLE_NAME AS table_name FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'"
        )
        return {
            row["table_name"]
            for row in cursor.fetchall()
            if row["table_name"] != HISTORY_TABLE
        }


EXPECTED_COLUMNS = {
    "materias": [
        ("id", "int", "NO", None, "auto_increment"),
        ("nome", "varchar(100)", "NO", None, ""),
        ("descricao", "text", "YES", None, ""),
    ],
    "assuntos": [
        ("id", "int", "NO", None, "auto_increment"),
        ("nome", "varchar(150)", "NO", None, ""),
        ("descricao", "text", "YES", None, ""),
        ("materia_id", "int", "NO", None, ""),
    ],
    "questoes": [
        ("id", "int", "NO", None, "auto_increment"),
        ("enunciado", "text", "NO", None, ""),
        ("alternativa_a", "text", "NO", None, ""),
        ("alternativa_b", "text", "NO", None, ""),
        ("alternativa_c", "text", "NO", None, ""),
        ("alternativa_d", "text", "NO", None, ""),
        ("alternativa_e", "text", "NO", None, ""),
        ("resposta_correta", "char(1)", "NO", None, ""),
        ("explicacao", "text", "YES", None, ""),
        ("dificuldade", "varchar(10)", "NO", None, ""),
        ("assunto_id", "int", "NO", None, ""),
    ],
}


EXPECTED_INDEXES = {
    ("materias", "PRIMARY", 0, 1, "id"),
    ("materias", "uq_materias_nome", 0, 1, "nome"),
    ("assuntos", "PRIMARY", 0, 1, "id"),
    ("assuntos", "ix_assuntos_materia_id", 1, 1, "materia_id"),
    ("questoes", "PRIMARY", 0, 1, "id"),
    ("questoes", "ix_questoes_assunto_id", 1, 1, "assunto_id"),
}


EXPECTED_PROCEDURE_BODY = """
BEGIN
    SELECT id, enunciado, alternativa_a, alternativa_b, alternativa_c,
           alternativa_d, alternativa_e, resposta_correta, explicacao,
           dificuldade, assunto_id
    FROM questoes
    WHERE assunto_id = p_assunto_id
    ORDER BY id;
END
"""


def _sql_tokens(value: str) -> list[str]:
    return re.findall(r"[a-z_][a-z0-9_]*|\d+|'[^']*'|[<>!]=?|[,();=]", value.lower().replace("`", ""))


def _check_tokens(value: str) -> list[str]:
    unescaped = value.lower().replace("\\'", "'")
    without_charset = re.sub(r"_[a-z0-9]+(?=')", "", unescaped)
    return [token for token in _sql_tokens(without_charset) if token not in {"(", ")"}]


def _detect_catalogo_prefix(connection, tables: set[str]) -> str:
    expected = {"areas_enem", "materias", "assuntos", "questoes", "assunto_transferencias"}
    if tables != expected:
        raise MigrationError("Schema nao corresponde as tabelas conhecidas do catalogo.")
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, codigo, nome, ordem FROM areas_enem ORDER BY ordem")
        areas = [tuple(row.values()) for row in cursor.fetchall()]
        if areas != [
            (1, "linguagens", "Linguagens", 1),
            (2, "ciencias-humanas", "Ciências Humanas", 2),
            (3, "ciencias-natureza", "Ciências da Natureza", 3),
            (4, "matematica", "Matemática", 4),
        ]:
            raise MigrationError("Catalogo fixo de Areas do ENEM diverge do esperado.")
        cursor.execute(
            "SELECT TABLE_NAME AS table_name, COLUMN_NAME AS column_name, "
            "IS_NULLABLE AS is_nullable, COLLATION_NAME AS collation_name "
            "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() "
            "AND (TABLE_NAME, COLUMN_NAME) IN "
            "(('materias', 'area_enem_id'), ('materias', 'status'), "
            "('assuntos', 'nome_normalizado'), ('assuntos', 'status'))"
        )
        columns = {
            (row["table_name"], row["column_name"]): (
                row["is_nullable"], row["collation_name"]
            )
            for row in cursor.fetchall()
        }
        if set(columns) != {
            ("materias", "area_enem_id"),
            ("materias", "status"),
            ("assuntos", "nome_normalizado"),
            ("assuntos", "status"),
        } or columns[("assuntos", "nome_normalizado")][1] != "utf8mb4_0900_ai_ci":
            raise MigrationError("Colunas principais do catalogo divergem do esperado.")
        cursor.execute(
            "SELECT rc.TABLE_NAME AS table_name, rc.DELETE_RULE AS delete_rule, "
            "kcu.COLUMN_NAME AS column_name FROM information_schema.REFERENTIAL_CONSTRAINTS rc "
            "JOIN information_schema.KEY_COLUMN_USAGE kcu "
            "ON kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA "
            "AND kcu.TABLE_NAME = rc.TABLE_NAME "
            "AND kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME "
            "WHERE rc.CONSTRAINT_SCHEMA = DATABASE()"
        )
        delete_rules = {
            (row["table_name"], row["column_name"]): row["delete_rule"]
            for row in cursor.fetchall()
        }
        cursor.execute(
            "SELECT COUNT(*) AS total FROM information_schema.ROUTINES "
            "WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE' "
            "AND ROUTINE_NAME = 'sp_questoes_por_assunto'"
        )
        if cursor.fetchone()["total"] != 1:
            raise MigrationError("Stored Procedure obrigatoria diverge do esperado.")
        cursor.execute(
            "SELECT COUNT(*) AS total FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'assuntos' "
            "AND INDEX_NAME = 'uq_assuntos_materia_nome_normalizado' AND NON_UNIQUE = 0"
        )
        unique_final = cursor.fetchone()["total"] == 2

    preparatorio = (
        columns[("materias", "area_enem_id")][0] == "YES"
        and columns[("assuntos", "nome_normalizado")][0] == "YES"
        and delete_rules.get(("assuntos", "materia_id")) == "CASCADE"
        and not unique_final
    )
    final = (
        columns[("materias", "area_enem_id")][0] == "NO"
        and columns[("assuntos", "nome_normalizado")][0] == "NO"
        and delete_rules.get(("materias", "area_enem_id")) == "RESTRICT"
        and delete_rules.get(("assuntos", "materia_id")) == "RESTRICT"
        and delete_rules.get(("questoes", "assunto_id")) == "RESTRICT"
        and unique_final
    )
    if preparatorio:
        return "003"
    if final:
        return "004"
    raise MigrationError("Schema combina estados historicos incompatíveis.")


def _detect_auth_prefix(connection, tables: set[str]) -> str:
    auth_tables = {"usuarios", "sessoes", "auth_limites"}
    if _detect_catalogo_prefix(connection, tables - auth_tables) != "004":
        raise MigrationError("Autenticacao exige catalogo final 004.")
    expected_columns = {
        "usuarios": [("id", "int", "NO", None, "auto_increment", None),
            ("nome", "varchar(100)", "NO", None, "", "utf8mb4_unicode_ci"),
            ("email", "varchar(254)", "NO", None, "", "utf8mb4_bin"),
            ("senha_hash", "varchar(255)", "NO", None, "", "utf8mb4_unicode_ci"),
            ("perfil", "varchar(20)", "NO", None, "", "utf8mb4_unicode_ci"),
            ("ativo", "tinyint(1)", "NO", "1", "", None),
            ("criado_em", "datetime(6)", "NO", None, "", None)],
        "sessoes": [("id", "bigint", "NO", None, "auto_increment", None),
            ("usuario_id", "int", "YES", None, "", None),
            ("identificador_hash", "char(64)", "NO", None, "", "ascii_bin"),
            *[(name, "datetime(6)", null, None, "", None) for name, null in
              [("criada_em", "NO"), ("ultimo_acesso_em", "NO"), ("expira_em", "NO"),
               ("reautenticada_em", "YES"), ("revogada_em", "YES")]]],
        "auth_limites": [("chave_hash", "char(64)", "NO", None, "", "ascii_bin"),
            ("falhas", "smallint unsigned", "NO", None, "", None),
            ("janela_inicio", "datetime(6)", "NO", None, "", None),
            ("bloqueado_ate", "datetime(6)", "YES", None, "", None)],
    }
    with connection.cursor() as cursor:
        cursor.execute("SELECT TABLE_NAME, ENGINE, TABLE_COLLATION FROM information_schema.TABLES "
                       "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME IN ('usuarios','sessoes','auth_limites')")
        if {tuple(row.values()) for row in cursor.fetchall()} != {
            (table, "InnoDB", "utf8mb4_unicode_ci") for table in auth_tables
        }:
            raise MigrationError("Tabelas de autenticacao divergentes.")
        cursor.execute("SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, "
                       "EXTRA, COLLATION_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
                       "AND TABLE_NAME IN ('usuarios','sessoes','auth_limites') ORDER BY TABLE_NAME, ORDINAL_POSITION")
        actual = {table: [] for table in auth_tables}
        for row in cursor.fetchall():
            values = list(row.values())
            actual[values[0]].append(tuple(values[1:]))
        if actual != expected_columns:
            raise MigrationError("Colunas de autenticacao divergentes.")
        cursor.execute("SELECT TABLE_NAME, INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME "
                       "FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=DATABASE() "
                       "AND TABLE_NAME IN ('usuarios','sessoes','auth_limites')")
        if {tuple(row.values()) for row in cursor.fetchall()} != {
            ("usuarios", "PRIMARY", 0, 1, "id"), ("usuarios", "uq_usuarios_email", 0, 1, "email"),
            ("sessoes", "PRIMARY", 0, 1, "id"), ("sessoes", "uq_sessoes_identificador", 0, 1, "identificador_hash"),
            ("sessoes", "ix_sessoes_usuario", 1, 1, "usuario_id"),
            ("sessoes", "ix_sessoes_expiracao", 1, 1, "expira_em"),
            ("auth_limites", "PRIMARY", 0, 1, "chave_hash"),
        }:
            raise MigrationError("Indices de autenticacao divergentes.")
        cursor.execute("SELECT tc.TABLE_NAME, tc.CONSTRAINT_NAME, cc.CHECK_CLAUSE "
                       "FROM information_schema.TABLE_CONSTRAINTS tc JOIN information_schema.CHECK_CONSTRAINTS cc "
                       "ON cc.CONSTRAINT_SCHEMA=tc.CONSTRAINT_SCHEMA AND cc.CONSTRAINT_NAME=tc.CONSTRAINT_NAME "
                       "WHERE tc.TABLE_SCHEMA=DATABASE() AND tc.TABLE_NAME IN ('usuarios','sessoes','auth_limites')")
        checks = {(row["TABLE_NAME"], row["CONSTRAINT_NAME"]): _check_tokens(row["CHECK_CLAUSE"])
                  for row in cursor.fetchall()}
        if checks != {("usuarios", "ck_usuarios_perfil"): _check_tokens("perfil IN ('aluno','administrador')"),
                      ("usuarios", "ck_usuarios_ativo"): _check_tokens("ativo IN (0,1)")}:
            raise MigrationError("Checks de autenticacao divergentes.")
        cursor.execute("SELECT rc.TABLE_NAME, rc.CONSTRAINT_NAME, rc.UPDATE_RULE, rc.DELETE_RULE, "
                       "k.COLUMN_NAME, k.REFERENCED_TABLE_NAME, k.REFERENCED_COLUMN_NAME "
                       "FROM information_schema.REFERENTIAL_CONSTRAINTS rc JOIN information_schema.KEY_COLUMN_USAGE k "
                       "ON k.CONSTRAINT_SCHEMA=rc.CONSTRAINT_SCHEMA AND k.CONSTRAINT_NAME=rc.CONSTRAINT_NAME "
                       "WHERE rc.CONSTRAINT_SCHEMA=DATABASE() AND rc.TABLE_NAME IN ('usuarios','sessoes','auth_limites')")
        if {tuple(row.values()) for row in cursor.fetchall()} != {
            ("sessoes", "fk_sessoes_usuario", "RESTRICT", "RESTRICT", "usuario_id", "usuarios", "id")
        }:
            raise MigrationError("Foreign keys de autenticacao divergentes.")
    return "005"


def _detect_questoes_prefix(connection, tables: set[str]) -> str:
    editorial = {"questao_versoes", "questao_eventos"}
    _detect_auth_prefix(connection, tables - editorial)
    expected = {
        "questoes": [(name, kind, null) for name, kind, null, *_ in EXPECTED_COLUMNS["questoes"]]
            + [("status", "varchar(20)", "NO"), ("revisao", "int", "NO"),
               ("criado_em", "datetime(6)", "YES"), ("atualizado_em", "datetime(6)", "NO"),
               ("versao_publicada_id", "int", "YES")],
        "questao_versoes": [("id", "int", "NO"), ("questao_id", "int", "NO"),
            ("numero", "int", "NO"), ("revisao_origem", "int", "NO"), ("estado", "varchar(20)", "NO"),
            *[(name, kind, null) for name, kind, null, *_ in EXPECTED_COLUMNS["questoes"][1:]],
            ("assunto_nome", "varchar(150)", "NO"), ("materia_id", "int", "NO"),
            ("materia_nome", "varchar(100)", "NO"), ("area_enem_id", "int", "NO"),
            ("area_enem_nome", "varchar(100)", "NO"), ("ator_id", "int", "YES"),
            ("origem", "varchar(20)", "NO"), ("criado_em", "datetime(6)", "NO")],
        "questao_eventos": [("id", "bigint", "NO"), ("questao_id", "int", "NO"),
            ("versao_id", "int", "YES"), ("ator_id", "int", "YES"),
            ("acao", "varchar(20)", "NO"), ("motivo", "varchar(500)", "NO"),
            ("criado_em", "datetime(6)", "NO")],
    }
    with connection.cursor() as cursor:
        cursor.execute("SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE "
            "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
            "AND TABLE_NAME IN ('questoes','questao_versoes','questao_eventos') "
            "ORDER BY TABLE_NAME, ORDINAL_POSITION")
        actual = {name: [] for name in expected}
        for row in cursor.fetchall():
            actual[row['TABLE_NAME']].append((row['COLUMN_NAME'], row['COLUMN_TYPE'], row['IS_NULLABLE']))
        if actual != expected:
            raise MigrationError("Colunas de questoes versionadas divergentes.")
        cursor.execute("SELECT TABLE_NAME, ENGINE, TABLE_COLLATION FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME IN ('questao_versoes','questao_eventos')")
        if any(row['ENGINE'] != 'InnoDB' or row['TABLE_COLLATION'] != 'utf8mb4_unicode_ci'
               for row in cursor.fetchall()):
            raise MigrationError("Engine/collation editorial divergentes.")
        cursor.execute("SELECT rc.TABLE_NAME, k.COLUMN_NAME, k.REFERENCED_TABLE_NAME, "
            "rc.DELETE_RULE, rc.UPDATE_RULE FROM information_schema.REFERENTIAL_CONSTRAINTS rc "
            "JOIN information_schema.KEY_COLUMN_USAGE k ON k.CONSTRAINT_SCHEMA=rc.CONSTRAINT_SCHEMA "
            "AND k.CONSTRAINT_NAME=rc.CONSTRAINT_NAME AND k.TABLE_NAME=rc.TABLE_NAME "
            "WHERE rc.CONSTRAINT_SCHEMA=DATABASE() "
            "AND rc.TABLE_NAME IN ('questoes','questao_versoes','questao_eventos')")
        links = {tuple(row.values()) for row in cursor.fetchall()}
        expected_links = {('questoes','assunto_id','assuntos','RESTRICT','RESTRICT'),
                          ('questoes','versao_publicada_id','questao_versoes','RESTRICT','RESTRICT')}
        for name, fields in {
            'questao_versoes': {'questao_id':'questoes','assunto_id':'assuntos','materia_id':'materias',
                               'area_enem_id':'areas_enem','ator_id':'usuarios'},
            'questao_eventos': {'questao_id':'questoes','versao_id':'questao_versoes','ator_id':'usuarios'},
        }.items():
            expected_links.update((name, field, target, 'RESTRICT', 'RESTRICT') for field,target in fields.items())
        if links != expected_links:
            raise MigrationError("Foreign keys editoriais divergentes.")
        cursor.execute("SELECT INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME "
            "FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='questao_versoes'")
        unique = {(r['INDEX_NAME'], r['SEQ_IN_INDEX'], r['COLUMN_NAME'])
                  for r in cursor.fetchall() if r['NON_UNIQUE'] == 0}
        if unique != {('PRIMARY',1,'id'),('uq_questao_versoes_numero',1,'questao_id'),
                      ('uq_questao_versoes_numero',2,'numero')}:
            raise MigrationError("Unicidade de versoes divergente.")
        cursor.execute("SELECT tc.TABLE_NAME, tc.CONSTRAINT_NAME, cc.CHECK_CLAUSE "
            "FROM information_schema.TABLE_CONSTRAINTS tc JOIN information_schema.CHECK_CONSTRAINTS cc "
            "ON cc.CONSTRAINT_SCHEMA=tc.CONSTRAINT_SCHEMA AND cc.CONSTRAINT_NAME=tc.CONSTRAINT_NAME "
            "WHERE tc.TABLE_SCHEMA=DATABASE() AND tc.TABLE_NAME IN ('questoes','questao_versoes','questao_eventos')")
        checks = {(r['TABLE_NAME'],r['CONSTRAINT_NAME']): _check_tokens(r['CHECK_CLAUSE']) for r in cursor.fetchall()}
        required_checks = {
            ('questoes','ck_questoes_status'): "status IN ('rascunho','publicada','arquivada')",
            ('questoes','ck_questoes_revisao'): 'revisao >= 1',
            ('questoes','ck_questoes_resposta_correta'): "resposta_correta IN ('A','B','C','D','E')",
            ('questoes','ck_questoes_dificuldade'): "dificuldade IN ('facil','media','dificil')",
            ('questao_versoes','ck_questao_versoes_numero'): 'numero >= 1 AND revisao_origem >= 1',
            ('questao_versoes','ck_questao_versoes_estado'): "estado IN ('rascunho','publicada')",
            ('questao_versoes','ck_questao_versoes_origem'): "origem IN ('legado','manual')",
            ('questao_versoes','ck_questao_versoes_resposta'): "resposta_correta IN ('A','B','C','D','E')",
            ('questao_versoes','ck_questao_versoes_dificuldade'): "dificuldade IN ('facil','media','dificil')",
            ('questao_eventos','ck_questao_eventos_acao'): "acao IN ('cadastro','edicao','revisao','aprovacao','publicacao','arquivamento')",
        }
        if checks != {key:_check_tokens(value) for key,value in required_checks.items()}:
            raise MigrationError("Checks editoriais divergentes.")
    return "006"


def _detect_praticas_prefix(connection, tables: set[str]) -> str:
    _detect_questoes_prefix(connection, tables - {"pratica_tentativas"})
    with connection.cursor() as cursor:
        cursor.execute("SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLLATION_NAME,EXTRA "
            "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
            "AND TABLE_NAME='pratica_tentativas' ORDER BY ORDINAL_POSITION")
        columns = cursor.fetchall()
        expected = [('id','bigint','NO'),('usuario_id','int','NO'),('questao_versao_id','int','NO'),
            ('chave_envio','char(36)','NO'),('estado','varchar(20)','NO'),('resposta_escolhida','char(1)','YES'),
            ('correta','tinyint(1)','YES'),('iniciada_em','datetime(6)','NO'),('respondida_em','datetime(6)','YES'),
            ('assunto_id','int','NO'),('assunto_nome','varchar(150)','NO'),('materia_id','int','NO'),
            ('materia_nome','varchar(100)','NO')]
        if [(r['COLUMN_NAME'],r['COLUMN_TYPE'],r['IS_NULLABLE']) for r in columns] != expected:
            raise MigrationError("Colunas de praticas divergentes.")
        if columns[0]['EXTRA'] != 'auto_increment' or any(
            r['COLLATION_NAME'] != 'ascii_bin' for r in columns if r['COLUMN_NAME'] in {'chave_envio','resposta_escolhida'}):
            raise MigrationError("Identidade/collation de praticas divergente.")
        cursor.execute("SELECT ENGINE,TABLE_COLLATION FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='pratica_tentativas'")
        if tuple(cursor.fetchone().values()) != ('InnoDB','utf8mb4_unicode_ci'):
            raise MigrationError("Engine/collation de praticas divergente.")
        cursor.execute("SELECT k.COLUMN_NAME,k.REFERENCED_TABLE_NAME,k.REFERENCED_COLUMN_NAME,rc.DELETE_RULE,rc.UPDATE_RULE "
            "FROM information_schema.REFERENTIAL_CONSTRAINTS rc JOIN information_schema.KEY_COLUMN_USAGE k "
            "ON k.CONSTRAINT_SCHEMA=rc.CONSTRAINT_SCHEMA AND k.CONSTRAINT_NAME=rc.CONSTRAINT_NAME "
            "AND k.TABLE_NAME=rc.TABLE_NAME WHERE rc.CONSTRAINT_SCHEMA=DATABASE() AND rc.TABLE_NAME='pratica_tentativas'")
        if {tuple(r.values()) for r in cursor.fetchall()} != {
            (c,t,'id','RESTRICT','RESTRICT') for c,t in [('usuario_id','usuarios'),
            ('questao_versao_id','questao_versoes'),('assunto_id','assuntos'),('materia_id','materias')]}:
            raise MigrationError("Foreign keys de praticas divergentes.")
        cursor.execute("SELECT INDEX_NAME,NON_UNIQUE,SEQ_IN_INDEX,COLUMN_NAME FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='pratica_tentativas'")
        indexes = {tuple(r.values()) for r in cursor.fetchall()}
        required = {('PRIMARY',0,1,'id'),('uq_pratica_tentativas_chave',0,1,'usuario_id'),
            ('uq_pratica_tentativas_chave',0,2,'chave_envio'),('ix_pratica_tentativas_historico',1,1,'usuario_id'),
            ('ix_pratica_tentativas_historico',1,2,'respondida_em'),('ix_pratica_tentativas_historico',1,3,'id')}
        if not required <= indexes or {r for r in indexes if r[1] == 0} != {r for r in required if r[1] == 0}:
            raise MigrationError("Indices de praticas divergentes.")
        cursor.execute("SELECT cc.CHECK_CLAUSE,tc.ENFORCED FROM information_schema.TABLE_CONSTRAINTS tc "
            "JOIN information_schema.CHECK_CONSTRAINTS cc ON cc.CONSTRAINT_SCHEMA=tc.CONSTRAINT_SCHEMA "
            "AND cc.CONSTRAINT_NAME=tc.CONSTRAINT_NAME WHERE tc.TABLE_SCHEMA=DATABASE() AND tc.TABLE_NAME='pratica_tentativas'")
        checks = cursor.fetchall()
        expected_check = "(estado = 'em_andamento' AND resposta_escolhida IS NULL AND correta IS NULL AND respondida_em IS NULL) OR (estado = 'respondida' AND resposta_escolhida IS NOT NULL AND resposta_escolhida IN ('A','B','C','D','E') AND correta IS NOT NULL AND correta IN (0,1) AND respondida_em IS NOT NULL AND respondida_em >= iniciada_em)"
        if len(checks) != 1 or checks[0]['ENFORCED'] != 'YES' or _check_tokens(checks[0]['CHECK_CLAUSE']) != _check_tokens(expected_check):
            raise MigrationError("Check de praticas divergente.")
    return "007"


SIMULADOS_FINGERPRINTS = {
    "simulados": "35b91f9a0f2b8d8cf7db2d27b5195d3b6c3dcc5b139fbed5f04fca7d69ba85ba",
    "simulado_rascunho_itens": "fbeaff16680ca7c6ad2293fc76faaf85af4f0e9472f51b64f2185398769b4f93",
    "simulado_versoes": "d46f8f7657f25b26e39c93ecb133e81981751547f962173f5f7ee8dbd01f746a",
    "simulado_versao_itens": "36f689fa5279e4d08a5b79731a8710bd127a6dbd015d8026da410048ebab8070",
    "simulado_eventos": "162c8b96a919ab7e60931323df54f59ca58df11e60181600d9c2fcec794143a7",
    "simulado_tentativas": "bac3364ef64882d18f332a29e57f258cfdfb68c35afe0e332a80aed159c6881a",
    "simulado_respostas": "f0ca66ebf310c61f8610ef13bb3f5ee0d40603621f482c948a7033c68c21343e",
}


def _detect_simulados_prefix(connection, tables: set[str]) -> str:
    novas = set(SIMULADOS_FINGERPRINTS)
    if not novas <= tables:
        raise MigrationError("Schema parcial de simulados.")
    _detect_praticas_prefix(connection, tables - novas)
    with connection.cursor() as cursor:
        for tabela, esperado in SIMULADOS_FINGERPRINTS.items():
            cursor.execute(f"SHOW CREATE TABLE `{tabela}`")
            # Somente o contador de identidades varia com os dados. O DDL inteiro
            # (inclusive generated/checks/FKs/índices) precisa corresponder ao 008.
            ddl = re.sub(r"AUTO_INCREMENT=\d+\s*", "", cursor.fetchone()["Create Table"])
            if hashlib.sha256(ddl.encode("utf-8")).hexdigest() != esperado:
                raise MigrationError("Fingerprint de simulados divergente.")
    return "008"


PLANOS_FINGERPRINTS = {
    "planos_estudo": "00e76e77302334fc04d25c1514adc7ac98a8041a825c5885d601a3aeadd07ba7",
    "plano_estudo_itens": "bb69309f58165b276bb5c2c7914b60c5295b8e7dfee418765be422abafcd1b1b",
}


def _detect_planos_prefix(connection, tables: set[str]) -> str:
    novas = set(PLANOS_FINGERPRINTS)
    if not novas <= tables:
        raise MigrationError("Schema parcial de planos de estudo.")
    _detect_simulados_prefix(connection, tables - novas)
    with connection.cursor() as cursor:
        for tabela, esperado in PLANOS_FINGERPRINTS.items():
            cursor.execute(f"SHOW CREATE TABLE `{tabela}`")
            ddl = re.sub(r"AUTO_INCREMENT=\d+\s*", "", cursor.fetchone()["Create Table"])
            if hashlib.sha256(ddl.encode("utf-8")).hexdigest() != esperado:
                raise MigrationError("Fingerprint de planos de estudo divergente.")
    return "009"


PRIVACIDADE_FINGERPRINT = "e7da6a5f88f3190a8b42f73fb534826898bdd9e56b18025508d830db77ae5698"


def _detect_privacidade_prefix(connection, tables: set[str]) -> str:
    _detect_planos_prefix(connection, tables - {"registros_privacidade"})
    with connection.cursor() as cursor:
        cursor.execute("SHOW CREATE TABLE registros_privacidade")
        ddl = re.sub(r"AUTO_INCREMENT=\d+\s*", "", cursor.fetchone()["Create Table"])
        if hashlib.sha256(ddl.encode("utf-8")).hexdigest() != PRIVACIDADE_FINGERPRINT:
            raise MigrationError("Fingerprint de privacidade divergente.")
    return "010"


def detect_legacy_prefix(connection) -> str:
    expected_tables = set(EXPECTED_COLUMNS)
    user_tables = _user_tables(connection)
    if "registros_privacidade" in user_tables:
        return _detect_privacidade_prefix(connection, user_tables)
    if set(PLANOS_FINGERPRINTS) & user_tables:
        return _detect_planos_prefix(connection, user_tables)
    if set(SIMULADOS_FINGERPRINTS) & user_tables:
        return _detect_simulados_prefix(connection, user_tables)
    if "pratica_tentativas" in user_tables:
        return _detect_praticas_prefix(connection, user_tables)
    if {"questao_versoes", "questao_eventos"} <= user_tables:
        return _detect_questoes_prefix(connection, user_tables)
    if user_tables == {"areas_enem", "materias", "assuntos", "questoes", "assunto_transferencias",
                       "usuarios", "sessoes", "auth_limites"}:
        return _detect_auth_prefix(connection, user_tables)
    if user_tables != expected_tables:
        if user_tables == {
            "areas_enem",
            "materias",
            "assuntos",
            "questoes",
            "assunto_transferencias",
        }:
            return _detect_catalogo_prefix(connection, user_tables)
        raise MigrationError("Schema nao corresponde as tabelas MVP esperadas.")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT TABLE_NAME AS table_name, ENGINE AS engine, "
            "TABLE_COLLATION AS table_collation FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN (%s, %s, %s)",
            tuple(sorted(expected_tables)),
        )
        table_rows = cursor.fetchall()
        actual_tables = {
            row["table_name"]: (row["engine"], row["table_collation"])
            for row in table_rows
        }
        if set(actual_tables) != expected_tables or any(
            engine.lower() != "innodb" or collation != "utf8mb4_unicode_ci"
            for engine, collation in actual_tables.values()
        ):
            raise MigrationError("Schema nao corresponde as tabelas MVP esperadas.")

        cursor.execute(
            "SELECT TABLE_NAME AS table_name, COLUMN_NAME AS column_name, "
            "COLUMN_TYPE AS column_type, IS_NULLABLE AS is_nullable, "
            "COLUMN_DEFAULT AS column_default, EXTRA AS extra "
            "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() "
            "AND TABLE_NAME IN (%s, %s, %s) ORDER BY TABLE_NAME, ORDINAL_POSITION",
            tuple(sorted(expected_tables)),
        )
        actual_columns: dict[str, list[tuple]] = {name: [] for name in expected_tables}
        for row in cursor.fetchall():
            actual_columns[row["table_name"]].append(
                (
                    row["column_name"],
                    row["column_type"].lower(),
                    row["is_nullable"],
                    row["column_default"],
                    row["extra"].lower(),
                )
            )
        if actual_columns != EXPECTED_COLUMNS:
            raise MigrationError("Colunas do schema nao correspondem ao MVP conhecido.")

        cursor.execute(
            "SELECT TABLE_NAME AS table_name, INDEX_NAME AS index_name, "
            "NON_UNIQUE AS non_unique, SEQ_IN_INDEX AS seq_in_index, "
            "COLUMN_NAME AS column_name FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN (%s, %s, %s)",
            tuple(sorted(expected_tables)),
        )
        indexes = {
            (
                row["table_name"],
                row["index_name"],
                int(row["non_unique"]),
                int(row["seq_in_index"]),
                row["column_name"],
            )
            for row in cursor.fetchall()
        }
        if indexes != EXPECTED_INDEXES:
            raise MigrationError("Indices do schema nao correspondem ao MVP conhecido.")

        cursor.execute(
            "SELECT rc.TABLE_NAME AS table_name, "
            "rc.CONSTRAINT_NAME AS constraint_name, rc.UPDATE_RULE AS update_rule, "
            "rc.DELETE_RULE AS delete_rule, kcu.COLUMN_NAME AS column_name, "
            "kcu.REFERENCED_TABLE_NAME AS referenced_table_name, "
            "kcu.REFERENCED_COLUMN_NAME AS referenced_column_name "
            "FROM information_schema.REFERENTIAL_CONSTRAINTS rc "
            "JOIN information_schema.KEY_COLUMN_USAGE kcu "
            "ON kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA "
            "AND kcu.TABLE_NAME = rc.TABLE_NAME "
            "AND kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME "
            "WHERE rc.CONSTRAINT_SCHEMA = DATABASE()"
        )
        foreign_keys = {
            (
                row["table_name"],
                row["constraint_name"],
                row["update_rule"],
                row["delete_rule"],
                row["column_name"],
                row["referenced_table_name"],
                row["referenced_column_name"],
            )
            for row in cursor.fetchall()
            if row["table_name"] in expected_tables
        }
        assunto_fk = (
            "assuntos",
            "fk_assuntos_materias",
            "CASCADE",
            "CASCADE",
            "materia_id",
            "materias",
            "id",
        )
        if assunto_fk not in foreign_keys or len(foreign_keys) != 2:
            raise MigrationError("Foreign keys do schema nao correspondem ao MVP conhecido.")
        questao_fk = next(
            (item for item in foreign_keys if item[0] == "questoes"), None
        )
        if not questao_fk or (
            questao_fk[1],
            questao_fk[2],
            questao_fk[4],
            questao_fk[5],
            questao_fk[6],
        ) != ("fk_questoes_assuntos", "CASCADE", "assunto_id", "assuntos", "id"):
            raise MigrationError("Foreign key de questoes nao corresponde ao MVP conhecido.")

        cursor.execute(
            "SELECT tc.CONSTRAINT_NAME AS constraint_name, cc.CHECK_CLAUSE AS check_clause "
            "FROM information_schema.TABLE_CONSTRAINTS tc "
            "JOIN information_schema.CHECK_CONSTRAINTS cc "
            "ON cc.CONSTRAINT_SCHEMA = tc.CONSTRAINT_SCHEMA "
            "AND cc.CONSTRAINT_NAME = tc.CONSTRAINT_NAME "
            "WHERE tc.TABLE_SCHEMA = DATABASE() AND tc.TABLE_NAME = 'questoes' "
            "AND tc.CONSTRAINT_TYPE = 'CHECK'"
        )
        checks = {
            row["constraint_name"]: _check_tokens(row["check_clause"])
            for row in cursor.fetchall()
        }
        expected_checks = {
            "ck_questoes_resposta_correta": _check_tokens(
                "resposta_correta IN ('A', 'B', 'C', 'D', 'E')"
            ),
            "ck_questoes_dificuldade": _check_tokens(
                "dificuldade IN ('facil', 'media', 'dificil')"
            ),
        }
        if checks != expected_checks:
            raise MigrationError("Checks do schema nao correspondem ao MVP conhecido.")

        cursor.execute(
            "SELECT ROUTINE_DEFINITION AS routine_definition FROM information_schema.ROUTINES "
            "WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE' "
            "AND ROUTINE_NAME = 'sp_questoes_por_assunto'"
        )
        procedure = cursor.fetchone()
        procedure_exists = procedure is not None
        if procedure_exists:
            cursor.execute(
                "SELECT PARAMETER_MODE AS parameter_mode, PARAMETER_NAME AS parameter_name, "
                "DTD_IDENTIFIER AS dtd_identifier FROM information_schema.PARAMETERS "
                "WHERE SPECIFIC_SCHEMA = DATABASE() "
                "AND SPECIFIC_NAME = 'sp_questoes_por_assunto' "
                "ORDER BY ORDINAL_POSITION"
            )
            parameters = cursor.fetchall()
            if len(parameters) != 1 or (
                parameters[0]["parameter_mode"],
                parameters[0]["parameter_name"],
                parameters[0]["dtd_identifier"].lower(),
            ) != ("IN", "p_assunto_id", "int"):
                raise MigrationError("Assinatura da Stored Procedure diverge do MVP conhecido.")
            if _sql_tokens(procedure["routine_definition"]) != _sql_tokens(
                EXPECTED_PROCEDURE_BODY
            ):
                raise MigrationError("Corpo da Stored Procedure diverge do MVP conhecido.")

    delete_rule = questao_fk[3]
    if delete_rule == "CASCADE" and not procedure_exists:
        return "000"
    if delete_rule == "RESTRICT" and not procedure_exists:
        return "001"
    if delete_rule == "RESTRICT" and procedure_exists:
        return "002"
    raise MigrationError("Schema combina estados historicos incompatíveis.")
