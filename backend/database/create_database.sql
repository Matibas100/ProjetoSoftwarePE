CREATE DATABASE IF NOT EXISTS plataforma_enem
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE plataforma_enem;

CREATE TABLE IF NOT EXISTS areas_enem (
    id INT NOT NULL,
    codigo VARCHAR(50) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    ordem SMALLINT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_areas_enem_codigo UNIQUE (codigo),
    CONSTRAINT uq_areas_enem_nome UNIQUE (nome),
    CONSTRAINT uq_areas_enem_ordem UNIQUE (ordem)
) ENGINE = InnoDB;

INSERT INTO areas_enem (id, codigo, nome, ordem) VALUES
    (1, 'linguagens', 'Linguagens', 1),
    (2, 'ciencias-humanas', 'Ciências Humanas', 2),
    (3, 'ciencias-natureza', 'Ciências da Natureza', 3),
    (4, 'matematica', 'Matemática', 4);

CREATE TABLE IF NOT EXISTS materias (
    id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT NULL,
    area_enem_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ativa',
    criado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    INDEX ix_materias_area_enem_id (area_enem_id),
    INDEX ix_materias_status (status),
    CONSTRAINT uq_materias_nome UNIQUE (nome),
    CONSTRAINT ck_materias_status CHECK (status IN ('ativa', 'inativa', 'arquivada')),
    CONSTRAINT fk_materias_areas_enem FOREIGN KEY (area_enem_id)
        REFERENCES areas_enem (id) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS assuntos (
    id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    nome_normalizado VARCHAR(150)
        CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    descricao TEXT NULL,
    materia_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ativa',
    criado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    INDEX ix_assuntos_materia_id (materia_id),
    INDEX ix_assuntos_status (status),
    CONSTRAINT uq_assuntos_materia_nome_normalizado
        UNIQUE (materia_id, nome_normalizado),
    CONSTRAINT ck_assuntos_status CHECK (status IN ('ativa', 'inativa', 'arquivada')),
    CONSTRAINT fk_assuntos_materias FOREIGN KEY (materia_id)
        REFERENCES materias (id) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS questoes (
    id INT NOT NULL AUTO_INCREMENT,
    enunciado TEXT NOT NULL,
    alternativa_a TEXT NOT NULL,
    alternativa_b TEXT NOT NULL,
    alternativa_c TEXT NOT NULL,
    alternativa_d TEXT NOT NULL,
    alternativa_e TEXT NOT NULL,
    resposta_correta CHAR(1) NOT NULL,
    explicacao TEXT NULL,
    dificuldade VARCHAR(10) NOT NULL,
    assunto_id INT NOT NULL,
    PRIMARY KEY (id),
    INDEX ix_questoes_assunto_id (assunto_id),
    CONSTRAINT ck_questoes_resposta_correta
        CHECK (resposta_correta IN ('A', 'B', 'C', 'D', 'E')),
    CONSTRAINT ck_questoes_dificuldade
        CHECK (dificuldade IN ('facil', 'media', 'dificil')),
    CONSTRAINT fk_questoes_assuntos FOREIGN KEY (assunto_id)
        REFERENCES assuntos (id) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS assunto_transferencias (
    id BIGINT NOT NULL AUTO_INCREMENT,
    assunto_id INT NOT NULL,
    materia_origem_id INT NOT NULL,
    materia_destino_id INT NOT NULL,
    questoes_impactadas INT NOT NULL,
    criado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    INDEX ix_transferencias_assunto_id (assunto_id),
    INDEX ix_transferencias_origem_id (materia_origem_id),
    INDEX ix_transferencias_destino_id (materia_destino_id),
    CONSTRAINT ck_transferencias_questoes CHECK (questoes_impactadas >= 0),
    CONSTRAINT ck_transferencias_materias CHECK (materia_origem_id <> materia_destino_id),
    CONSTRAINT fk_transferencias_assunto FOREIGN KEY (assunto_id)
        REFERENCES assuntos (id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_transferencias_origem FOREIGN KEY (materia_origem_id)
        REFERENCES materias (id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_transferencias_destino FOREIGN KEY (materia_destino_id)
        REFERENCES materias (id) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE = InnoDB;

DROP PROCEDURE IF EXISTS sp_questoes_por_assunto;

DELIMITER $$

CREATE PROCEDURE sp_questoes_por_assunto(IN p_assunto_id INT)
BEGIN
    SELECT
        id,
        enunciado,
        alternativa_a,
        alternativa_b,
        alternativa_c,
        alternativa_d,
        alternativa_e,
        resposta_correta,
        explicacao,
        dificuldade,
        assunto_id
    FROM questoes
    WHERE assunto_id = p_assunto_id
    ORDER BY id;
END$$

DELIMITER ;

-- Pre-condicao: migrations 000 a 004 aplicadas e backup validado.
-- Preservacao: somente tabelas novas, sem contas ou senhas padrao.
-- Reversao: backup validado ou migration compensatoria; sem downgrade automatico.
CREATE TABLE usuarios (
    id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(254) COLLATE utf8mb4_bin NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    perfil VARCHAR(20) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_usuarios_email UNIQUE (email),
    CONSTRAINT ck_usuarios_perfil CHECK (perfil IN ('aluno', 'administrador')),
    CONSTRAINT ck_usuarios_ativo CHECK (ativo IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE sessoes (
    id BIGINT NOT NULL AUTO_INCREMENT,
    usuario_id INT NULL,
    identificador_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    criada_em DATETIME(6) NOT NULL,
    ultimo_acesso_em DATETIME(6) NOT NULL,
    expira_em DATETIME(6) NOT NULL,
    reautenticada_em DATETIME(6) NULL,
    revogada_em DATETIME(6) NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_sessoes_identificador UNIQUE (identificador_hash),
    INDEX ix_sessoes_usuario (usuario_id),
    INDEX ix_sessoes_expiracao (expira_em),
    CONSTRAINT fk_sessoes_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE auth_limites (
    chave_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    falhas SMALLINT UNSIGNED NOT NULL,
    janela_inicio DATETIME(6) NOT NULL,
    bloqueado_ate DATETIME(6) NULL,
    PRIMARY KEY (chave_hash)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Gest?o versionada: estrutura equivalente ? migration 006.
ALTER TABLE questoes
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'rascunho',
    ADD COLUMN revisao INT NOT NULL DEFAULT 1,
    ADD COLUMN criado_em DATETIME(6) NULL,
    ADD COLUMN atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    ADD COLUMN versao_publicada_id INT NULL,
    ADD CONSTRAINT ck_questoes_status CHECK (status IN ('rascunho', 'publicada', 'arquivada')),
    ADD CONSTRAINT ck_questoes_revisao CHECK (revisao >= 1),
    ADD INDEX ix_questoes_status (status);

CREATE TABLE questao_versoes (
    id INT NOT NULL AUTO_INCREMENT,
    questao_id INT NOT NULL,
    numero INT NOT NULL,
    revisao_origem INT NOT NULL,
    estado VARCHAR(20) NOT NULL,
    enunciado TEXT NOT NULL,
    alternativa_a TEXT NOT NULL,
    alternativa_b TEXT NOT NULL,
    alternativa_c TEXT NOT NULL,
    alternativa_d TEXT NOT NULL,
    alternativa_e TEXT NOT NULL,
    resposta_correta CHAR(1) NOT NULL,
    explicacao TEXT NULL,
    dificuldade VARCHAR(10) NOT NULL,
    assunto_id INT NOT NULL,
    assunto_nome VARCHAR(150) NOT NULL,
    materia_id INT NOT NULL,
    materia_nome VARCHAR(100) NOT NULL,
    area_enem_id INT NOT NULL,
    area_enem_nome VARCHAR(100) NOT NULL,
    ator_id INT NULL,
    origem VARCHAR(20) NOT NULL,
    criado_em DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_questao_versoes_numero UNIQUE (questao_id, numero),
    CONSTRAINT ck_questao_versoes_numero CHECK (numero >= 1 AND revisao_origem >= 1),
    CONSTRAINT ck_questao_versoes_estado CHECK (estado IN ('rascunho', 'publicada')),
    CONSTRAINT ck_questao_versoes_origem CHECK (origem IN ('legado', 'manual')),
    CONSTRAINT ck_questao_versoes_resposta CHECK (resposta_correta IN ('A','B','C','D','E')),
    CONSTRAINT ck_questao_versoes_dificuldade CHECK (dificuldade IN ('facil','media','dificil')),
    CONSTRAINT fk_questao_versoes_questao FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_versoes_assunto FOREIGN KEY (assunto_id) REFERENCES assuntos(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_versoes_materia FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_versoes_area FOREIGN KEY (area_enem_id) REFERENCES areas_enem(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_versoes_ator FOREIGN KEY (ator_id) REFERENCES usuarios(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB;

ALTER TABLE questoes ADD CONSTRAINT fk_questoes_versao_publicada
    FOREIGN KEY (versao_publicada_id) REFERENCES questao_versoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE TABLE questao_eventos (
    id BIGINT NOT NULL AUTO_INCREMENT,
    questao_id INT NOT NULL,
    versao_id INT NULL,
    ator_id INT NULL,
    acao VARCHAR(20) NOT NULL,
    motivo VARCHAR(500) NOT NULL,
    criado_em DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    INDEX ix_questao_eventos_questao (questao_id),
    CONSTRAINT ck_questao_eventos_acao CHECK (acao IN ('cadastro','edicao','revisao','aprovacao','publicacao','arquivamento')),
    CONSTRAINT fk_questao_eventos_questao FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_eventos_versao FOREIGN KEY (versao_id) REFERENCES questao_versoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_eventos_ator FOREIGN KEY (ator_id) REFERENCES usuarios(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB;

INSERT INTO questao_versoes (questao_id, numero, revisao_origem, estado,
    enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_e,
    resposta_correta, explicacao, dificuldade, assunto_id, assunto_nome,
    materia_id, materia_nome, area_enem_id, area_enem_nome, ator_id, origem, criado_em)
SELECT q.id, 1, 1, 'rascunho', q.enunciado, q.alternativa_a, q.alternativa_b,
    q.alternativa_c, q.alternativa_d, q.alternativa_e, q.resposta_correta, q.explicacao,
    q.dificuldade, a.id, a.nome, m.id, m.nome, ar.id, ar.nome, NULL, 'legado', UTC_TIMESTAMP(6)
FROM questoes q JOIN assuntos a ON a.id=q.assunto_id
JOIN materias m ON m.id=a.materia_id JOIN areas_enem ar ON ar.id=m.area_enem_id;

INSERT INTO questao_eventos (questao_id, versao_id, ator_id, acao, motivo, criado_em)
SELECT questao_id, id, NULL, 'cadastro', 'Backfill da migration 006; autoria historica desconhecida.', criado_em
FROM questao_versoes WHERE origem='legado';

-- Prática individual: sem backfill. Reversão por backup/compensação.
CREATE TABLE pratica_tentativas (
    id BIGINT NOT NULL AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    questao_versao_id INT NOT NULL,
    chave_envio CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    estado VARCHAR(20) NOT NULL,
    resposta_escolhida CHAR(1) CHARACTER SET ascii COLLATE ascii_bin NULL,
    correta BOOLEAN NULL,
    iniciada_em DATETIME(6) NOT NULL,
    respondida_em DATETIME(6) NULL,
    assunto_id INT NOT NULL,
    assunto_nome VARCHAR(150) NOT NULL,
    materia_id INT NOT NULL,
    materia_nome VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_pratica_tentativas_chave UNIQUE (usuario_id, chave_envio),
    INDEX ix_pratica_tentativas_historico (usuario_id, respondida_em, id),
    CONSTRAINT ck_pratica_tentativas_estado CHECK (
        (estado = 'em_andamento' AND resposta_escolhida IS NULL AND correta IS NULL AND respondida_em IS NULL)
        OR (estado = 'respondida' AND resposta_escolhida IS NOT NULL
            AND resposta_escolhida IN ('A','B','C','D','E') AND correta IS NOT NULL
            AND correta IN (0,1) AND respondida_em IS NOT NULL AND respondida_em >= iniciada_em)
    ),
    CONSTRAINT fk_pratica_tentativas_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_pratica_tentativas_versao FOREIGN KEY (questao_versao_id) REFERENCES questao_versoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_pratica_tentativas_assunto FOREIGN KEY (assunto_id) REFERENCES assuntos(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_pratica_tentativas_materia FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pré-condição: prefixo 007 completo. Tabelas vazias, sem backfill.
-- Reversão: backup ou migration compensatória; preservar tentativas concluídas.
CREATE TABLE simulados (
	id INTEGER NOT NULL AUTO_INCREMENT,
	titulo VARCHAR(150) NOT NULL,
	estado VARCHAR(20) NOT NULL,
	revisao INTEGER NOT NULL,
	autor_id INTEGER NOT NULL,
	criado_em DATETIME(6) NOT NULL,
	atualizado_em DATETIME(6) NOT NULL,
	simulado_versao_id INTEGER,
	PRIMARY KEY (id),
	CONSTRAINT ck_simulados_estado CHECK (estado IN ('rascunho','publicado','arquivado')),
	CONSTRAINT ck_simulados_revisao CHECK (revisao >= 1),
	CONSTRAINT fk_simulados_autor_id FOREIGN KEY(autor_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_rascunho_itens (
	id INTEGER NOT NULL AUTO_INCREMENT,
	simulado_id INTEGER NOT NULL,
	posicao INTEGER NOT NULL,
	questao_id INTEGER NOT NULL,
	questao_versao_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_rascunho_posicao UNIQUE (simulado_id, posicao),
	CONSTRAINT uq_sim_rascunho_questao UNIQUE (simulado_id, questao_id),
	CONSTRAINT ck_sim_rascunho_posicao CHECK (posicao BETWEEN 1 AND 180),
	CONSTRAINT fk_simulado_rascunho_itens_simulado_id FOREIGN KEY(simulado_id) REFERENCES simulados (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_rascunho_itens_questao_id FOREIGN KEY(questao_id) REFERENCES questoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_rascunho_itens_questao_versao_id FOREIGN KEY(questao_versao_id) REFERENCES questao_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_versoes (
	id INTEGER NOT NULL AUTO_INCREMENT,
	simulado_id INTEGER NOT NULL,
	numero INTEGER NOT NULL,
	revisao_origem INTEGER NOT NULL,
	titulo VARCHAR(150) NOT NULL,
	autor_id INTEGER NOT NULL,
	criado_em DATETIME(6) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_versao_numero UNIQUE (simulado_id, numero),
	CONSTRAINT uq_sim_versao_revisao UNIQUE (simulado_id, revisao_origem),
	CONSTRAINT ck_sim_versao_numero CHECK (numero >= 1 AND revisao_origem >= 1),
	CONSTRAINT fk_simulado_versoes_simulado_id FOREIGN KEY(simulado_id) REFERENCES simulados (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_versoes_autor_id FOREIGN KEY(autor_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_versao_itens (
	id INTEGER NOT NULL AUTO_INCREMENT,
	simulado_versao_id INTEGER NOT NULL,
	posicao INTEGER NOT NULL,
	questao_id INTEGER NOT NULL,
	questao_versao_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_item_posicao UNIQUE (simulado_versao_id, posicao),
	CONSTRAINT uq_sim_item_questao UNIQUE (simulado_versao_id, questao_id),
	CONSTRAINT ck_sim_item_posicao CHECK (posicao BETWEEN 1 AND 180),
	CONSTRAINT fk_simulado_versao_itens_simulado_versao_id FOREIGN KEY(simulado_versao_id) REFERENCES simulado_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_versao_itens_questao_id FOREIGN KEY(questao_id) REFERENCES questoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_versao_itens_questao_versao_id FOREIGN KEY(questao_versao_id) REFERENCES questao_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_eventos (
	id BIGINT NOT NULL AUTO_INCREMENT,
	simulado_id INTEGER NOT NULL,
	versao_id INTEGER,
	ator_id INTEGER NOT NULL,
	acao VARCHAR(30) NOT NULL,
	motivo VARCHAR(500) NOT NULL,
	criado_em DATETIME(6) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT fk_simulado_eventos_simulado_id FOREIGN KEY(simulado_id) REFERENCES simulados (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_eventos_versao_id FOREIGN KEY(versao_id) REFERENCES simulado_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_eventos_ator_id FOREIGN KEY(ator_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_tentativas (
	id BIGINT NOT NULL AUTO_INCREMENT,
	usuario_id INTEGER NOT NULL,
	simulado_versao_id INTEGER NOT NULL,
	estado VARCHAR(20) NOT NULL,
	revisao INTEGER NOT NULL,
	chave_envio CHAR(36) COLLATE ascii_bin NOT NULL,
	iniciada_em DATETIME(6) NOT NULL,
	finalizada_em DATETIME(6),
	total INTEGER,
	respondidas INTEGER,
	acertos INTEGER,
	erros INTEGER,
	em_branco INTEGER,
	percentual_acerto NUMERIC(5, 2),
	em_andamento_marcador INTEGER GENERATED ALWAYS AS (CASE WHEN estado = 'em_andamento' THEN 1 ELSE NULL END) STORED,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_tentativa_chave UNIQUE (usuario_id, chave_envio),
	CONSTRAINT uq_sim_tentativa_andamento UNIQUE (usuario_id, simulado_versao_id, em_andamento_marcador),
	CONSTRAINT ck_sim_tentativa_revisao CHECK (revisao >= 1),
	CONSTRAINT ck_sim_tentativa_estado CHECK ((estado = 'em_andamento' AND finalizada_em IS NULL AND total IS NULL AND respondidas IS NULL AND acertos IS NULL AND erros IS NULL AND em_branco IS NULL AND percentual_acerto IS NULL) OR (estado = 'finalizada' AND finalizada_em IS NOT NULL AND finalizada_em >= iniciada_em AND total IS NOT NULL AND total BETWEEN 1 AND 180 AND respondidas IS NOT NULL AND acertos IS NOT NULL AND erros IS NOT NULL AND em_branco IS NOT NULL AND percentual_acerto IS NOT NULL AND acertos >= 0 AND erros >= 0 AND em_branco >= 0 AND total = acertos + erros + em_branco AND respondidas = acertos + erros AND percentual_acerto = ROUND(100 * acertos / total, 2))),
	CONSTRAINT fk_simulado_tentativas_usuario_id FOREIGN KEY(usuario_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_tentativas_simulado_versao_id FOREIGN KEY(simulado_versao_id) REFERENCES simulado_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE INDEX ix_sim_tentativa_historico ON simulado_tentativas (usuario_id, finalizada_em, id);

CREATE TABLE simulado_respostas (
	id BIGINT NOT NULL AUTO_INCREMENT,
	tentativa_id BIGINT NOT NULL,
	item_id INTEGER NOT NULL,
	alternativa CHAR(1) COLLATE ascii_bin,
	correta BOOL,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_resposta_item UNIQUE (tentativa_id, item_id),
	CONSTRAINT ck_sim_resposta_alternativa CHECK (alternativa IS NULL OR alternativa IN ('A','B','C','D','E')),
	CONSTRAINT ck_sim_resposta_correta CHECK (correta IS NULL OR correta IN (0,1)),
	CONSTRAINT fk_simulado_respostas_tentativa_id FOREIGN KEY(tentativa_id) REFERENCES simulado_tentativas (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_respostas_item_id FOREIGN KEY(item_id) REFERENCES simulado_versao_itens (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

ALTER TABLE simulados ADD CONSTRAINT fk_simulados_simulado_versao_id FOREIGN KEY (simulado_versao_id) REFERENCES simulado_versoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Pré-condição: prefixo 008 completo. Sem backfill e sem planos artificiais.
-- Reversão: restaurar backup ou migration compensatória que preserve o histórico.
CREATE TABLE planos_estudo (
    id BIGINT NOT NULL AUTO_INCREMENT,
    usuario_id INTEGER NOT NULL,
    geracao INTEGER NOT NULL,
    atual BOOL NOT NULL,
    usuario_atual INTEGER GENERATED ALWAYS AS (CASE WHEN atual = 1 THEN usuario_id ELSE NULL END) STORED,
    periodo JSON NOT NULL,
    gerado_em DATETIME(6) NOT NULL,
    chave_envio CHAR(36) COLLATE ascii_bin NOT NULL,
    operacao VARCHAR(12) NOT NULL,
    plano_anterior_id BIGINT,
    PRIMARY KEY (id),
    CONSTRAINT uq_plano_geracao UNIQUE (usuario_id, geracao),
    CONSTRAINT uq_plano_chave UNIQUE (usuario_id, chave_envio),
    CONSTRAINT uq_plano_atual UNIQUE (usuario_atual),
    CONSTRAINT ck_plano_geracao CHECK (geracao >= 1 AND atual IN (0,1)),
    CONSTRAINT ck_plano_operacao CHECK ((operacao = 'gerar' AND plano_anterior_id IS NULL) OR (operacao = 'recalcular' AND plano_anterior_id IS NOT NULL)),
    CONSTRAINT fk_plano_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_plano_anterior FOREIGN KEY (plano_anterior_id) REFERENCES planos_estudo(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE plano_estudo_itens (
    id BIGINT NOT NULL AUTO_INCREMENT,
    plano_id BIGINT NOT NULL,
    assunto_id INTEGER NOT NULL,
    materia_id INTEGER NOT NULL,
    posicao INTEGER NOT NULL,
    snapshot JSON NOT NULL,
    estado VARCHAR(12) NOT NULL,
    concluido_em DATETIME(6),
    PRIMARY KEY (id),
    CONSTRAINT uq_plano_item_posicao UNIQUE (plano_id, posicao),
    CONSTRAINT uq_plano_item_assunto UNIQUE (plano_id, assunto_id),
    CONSTRAINT ck_plano_item_posicao CHECK (posicao BETWEEN 1 AND 3),
    CONSTRAINT ck_plano_item_estado CHECK ((estado = 'pendente' AND concluido_em IS NULL) OR (estado = 'concluido' AND concluido_em IS NOT NULL)),
    CONSTRAINT fk_plano_item_plano FOREIGN KEY (plano_id) REFERENCES planos_estudo(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_plano_item_assunto FOREIGN KEY (assunto_id) REFERENCES assuntos(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_plano_item_materia FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

-- Pré-condição: schema 009. Aditiva, sem backfill ou alteração de planos.
-- Compensação: preservar evidências; não há downgrade automático.
CREATE TABLE registros_privacidade (
    id BIGINT NOT NULL AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    tipo VARCHAR(8) NOT NULL,
    acao VARCHAR(8) NOT NULL,
    versao VARCHAR(20) NOT NULL,
    documento_sha256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    registrado_em DATETIME(6) NOT NULL,
    chave_envio CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    revisao_base BIGINT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_privacidade_chave (usuario_id, chave_envio),
    KEY ix_privacidade_ultima (usuario_id, tipo, id),
    CONSTRAINT fk_privacidade_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_privacidade_tipo CHECK (tipo IN ('uso','plano')),
    CONSTRAINT ck_privacidade_acao CHECK (acao IN ('aceitar','recusar','revogar')),
    CONSTRAINT ck_privacidade_combinacao CHECK (tipo = 'plano' OR acao = 'aceitar'),
    CONSTRAINT ck_privacidade_revisao CHECK (revisao_base >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



DELIMITER $$
-- Pré-condição: prefixo 010 íntegro. Privilégios: CREATE ROUTINE e SELECT.
-- Preservação: somente definições; sem DML funcional, tabelas ou backfill.
-- Compensação: voltar ao código anterior e restaurar backup ou remover estas
-- quatro routines por migration revisada, sem apagar histórico/checksums/dados.
-- DDL não tem rollback transacional. Não aplicar automaticamente no startup.

CREATE PROCEDURE sp_materias_admin(
    IN p_busca VARCHAR(100),
    IN p_status VARCHAR(20),
    IN p_area_enem_id BIGINT UNSIGNED,
    IN p_pagina BIGINT UNSIGNED,
    IN p_por_pagina INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_deslocamento BIGINT UNSIGNED;
    IF p_pagina IS NULL OR
       p_pagina < 1 OR
       p_por_pagina IS NULL OR
       p_por_pagina < 1 OR
       p_por_pagina > 100 OR
       (p_area_enem_id IS NOT NULL AND p_area_enem_id < 1) OR
       (p_status IS NOT NULL AND p_status NOT IN ('ativa','inativa','arquivada')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Parâmetros de consulta inválidos';
    END IF;
    SET v_deslocamento=(p_pagina-1)*p_por_pagina;
    SELECT m.id AS m_id,
        m.nome AS m_nome,
        m.descricao AS m_descricao,
        m.area_enem_id AS m_area_enem_id,
        m.status AS m_status,
        m.criado_em AS m_criado_em,
        m.atualizado_em AS m_atualizado_em,
        a.id AS a_id,
        a.codigo AS a_codigo,
        a.nome AS a_nome,
        a.ordem AS a_ordem,
        COUNT(DISTINCT s.id) AS assuntos, COUNT(DISTINCT q.id) AS questoes
    FROM materias m JOIN areas_enem a ON a.id=m.area_enem_id LEFT JOIN assuntos s ON s.materia_id=m.id LEFT JOIN questoes q ON q.assunto_id=s.id
    WHERE (p_busca IS NULL OR p_busca='' OR m.nome LIKE CONCAT('%',p_busca,'%') OR m.descricao LIKE CONCAT('%',p_busca,'%')) AND
        (p_status IS NULL OR m.status = p_status) AND
        (p_area_enem_id IS NULL OR m.area_enem_id = p_area_enem_id)
    GROUP BY m.id,a.id
    ORDER BY m.nome, m.id
    LIMIT p_por_pagina OFFSET v_deslocamento;
    SELECT COUNT(*) AS total FROM materias m JOIN areas_enem a ON a.id=m.area_enem_id
    WHERE (p_busca IS NULL OR p_busca='' OR m.nome LIKE CONCAT('%',p_busca,'%') OR m.descricao LIKE CONCAT('%',p_busca,'%')) AND
        (p_status IS NULL OR m.status = p_status) AND
        (p_area_enem_id IS NULL OR m.area_enem_id = p_area_enem_id);
END$$

CREATE PROCEDURE sp_assuntos_admin(
    IN p_busca VARCHAR(100),
    IN p_status VARCHAR(20),
    IN p_area_enem_id BIGINT UNSIGNED,
    IN p_materia_id BIGINT UNSIGNED,
    IN p_pagina BIGINT UNSIGNED,
    IN p_por_pagina INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_deslocamento BIGINT UNSIGNED;
    IF p_pagina IS NULL OR
       p_pagina < 1 OR
       p_por_pagina IS NULL OR
       p_por_pagina < 1 OR
       p_por_pagina > 100 OR
       (p_area_enem_id IS NOT NULL AND p_area_enem_id < 1) OR
       (p_materia_id IS NOT NULL AND p_materia_id < 1) OR
       (p_status IS NOT NULL AND p_status NOT IN ('ativa','inativa','arquivada')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Parâmetros de consulta inválidos';
    END IF;
    SET v_deslocamento=(p_pagina-1)*p_por_pagina;
    SELECT s.id AS s_id,
        s.nome AS s_nome,
        s.nome_normalizado AS s_nome_normalizado,
        s.descricao AS s_descricao,
        s.materia_id AS s_materia_id,
        s.status AS s_status,
        s.criado_em AS s_criado_em,
        s.atualizado_em AS s_atualizado_em,
        m.id AS m_id,
        m.nome AS m_nome,
        m.descricao AS m_descricao,
        m.area_enem_id AS m_area_enem_id,
        m.status AS m_status,
        m.criado_em AS m_criado_em,
        m.atualizado_em AS m_atualizado_em,
        a.id AS a_id,
        a.codigo AS a_codigo,
        a.nome AS a_nome,
        a.ordem AS a_ordem,
        COUNT(q.id) AS questoes
    FROM assuntos s JOIN materias m ON m.id=s.materia_id JOIN areas_enem a ON a.id=m.area_enem_id LEFT JOIN questoes q ON q.assunto_id=s.id
    WHERE (p_busca IS NULL OR p_busca='' OR s.nome LIKE CONCAT('%',p_busca,'%') OR s.descricao LIKE CONCAT('%',p_busca,'%')) AND
        (p_status IS NULL OR s.status = p_status) AND
        (p_area_enem_id IS NULL OR m.area_enem_id = p_area_enem_id) AND
        (p_materia_id IS NULL OR s.materia_id = p_materia_id)
    GROUP BY s.id,m.id,a.id
    ORDER BY s.nome_normalizado, s.id
    LIMIT p_por_pagina OFFSET v_deslocamento;
    SELECT COUNT(*) AS total FROM assuntos s JOIN materias m ON m.id=s.materia_id JOIN areas_enem a ON a.id=m.area_enem_id
    WHERE (p_busca IS NULL OR p_busca='' OR s.nome LIKE CONCAT('%',p_busca,'%') OR s.descricao LIKE CONCAT('%',p_busca,'%')) AND
        (p_status IS NULL OR s.status = p_status) AND
        (p_area_enem_id IS NULL OR m.area_enem_id = p_area_enem_id) AND
        (p_materia_id IS NULL OR s.materia_id = p_materia_id);
END$$

CREATE PROCEDURE sp_questoes_admin(
    IN p_busca VARCHAR(100),
    IN p_status VARCHAR(20),
    IN p_dificuldade VARCHAR(10),
    IN p_area_enem_id BIGINT UNSIGNED,
    IN p_materia_id BIGINT UNSIGNED,
    IN p_assunto_id BIGINT UNSIGNED,
    IN p_pagina BIGINT UNSIGNED,
    IN p_por_pagina INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_deslocamento BIGINT UNSIGNED;
    IF p_pagina IS NULL OR
       p_pagina < 1 OR
       p_por_pagina IS NULL OR
       p_por_pagina < 1 OR
       p_por_pagina > 100 OR
       (p_area_enem_id IS NOT NULL AND p_area_enem_id < 1) OR
       (p_materia_id IS NOT NULL AND p_materia_id < 1) OR
       (p_assunto_id IS NOT NULL AND p_assunto_id < 1) OR
       (p_status IS NOT NULL AND p_status NOT IN ('rascunho','publicada','arquivada')) OR
       (p_dificuldade IS NOT NULL AND p_dificuldade NOT IN ('facil','media','dificil')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Parâmetros de consulta inválidos';
    END IF;
    SET v_deslocamento=(p_pagina-1)*p_por_pagina;
    SELECT q.id AS q_id,
        q.enunciado AS q_enunciado,
        q.alternativa_a AS q_alternativa_a,
        q.alternativa_b AS q_alternativa_b,
        q.alternativa_c AS q_alternativa_c,
        q.alternativa_d AS q_alternativa_d,
        q.alternativa_e AS q_alternativa_e,
        q.resposta_correta AS q_resposta_correta,
        q.explicacao AS q_explicacao,
        q.dificuldade AS q_dificuldade,
        q.assunto_id AS q_assunto_id,
        q.status AS q_status,
        q.revisao AS q_revisao,
        q.versao_publicada_id AS q_versao_publicada_id,
        s.id AS s_id,
        s.nome AS s_nome,
        s.nome_normalizado AS s_nome_normalizado,
        s.descricao AS s_descricao,
        s.materia_id AS s_materia_id,
        s.status AS s_status,
        s.criado_em AS s_criado_em,
        s.atualizado_em AS s_atualizado_em,
        m.id AS m_id,
        m.nome AS m_nome,
        m.descricao AS m_descricao,
        m.area_enem_id AS m_area_enem_id,
        m.status AS m_status,
        m.criado_em AS m_criado_em,
        m.atualizado_em AS m_atualizado_em,
        a.id AS a_id,
        a.codigo AS a_codigo,
        a.nome AS a_nome,
        a.ordem AS a_ordem
    FROM questoes q JOIN assuntos s ON s.id=q.assunto_id JOIN materias m ON m.id=s.materia_id JOIN areas_enem a ON a.id=m.area_enem_id
    WHERE (p_busca IS NULL OR p_busca='' OR q.enunciado LIKE CONCAT('%',REPLACE(REPLACE(REPLACE(p_busca,'/','//'),'%','/%'),'_','/_'),'%') ESCAPE '/') AND
        (p_status IS NULL OR q.status = p_status) AND
        (p_dificuldade IS NULL OR q.dificuldade = p_dificuldade) AND
        (p_area_enem_id IS NULL OR a.id = p_area_enem_id) AND
        (p_materia_id IS NULL OR m.id = p_materia_id) AND
        (p_assunto_id IS NULL OR q.assunto_id = p_assunto_id)
    ORDER BY q.id DESC
    LIMIT p_por_pagina OFFSET v_deslocamento;
    SELECT COUNT(*) AS total FROM questoes q JOIN assuntos s ON s.id=q.assunto_id JOIN materias m ON m.id=s.materia_id JOIN areas_enem a ON a.id=m.area_enem_id
    WHERE (p_busca IS NULL OR p_busca='' OR q.enunciado LIKE CONCAT('%',REPLACE(REPLACE(REPLACE(p_busca,'/','//'),'%','/%'),'_','/_'),'%') ESCAPE '/') AND
        (p_status IS NULL OR q.status = p_status) AND
        (p_dificuldade IS NULL OR q.dificuldade = p_dificuldade) AND
        (p_area_enem_id IS NULL OR a.id = p_area_enem_id) AND
        (p_materia_id IS NULL OR m.id = p_materia_id) AND
        (p_assunto_id IS NULL OR q.assunto_id = p_assunto_id);
END$$

CREATE PROCEDURE sp_conteudo_contagens_dashboard()
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    SELECT (SELECT COUNT(*) FROM materias WHERE status='ativa') AS materias_ativas,
        (SELECT COUNT(*) FROM assuntos WHERE status='ativa') AS assuntos_ativos,
        (SELECT COUNT(*) FROM questoes WHERE status='rascunho') AS questoes_rascunhos,
        (SELECT COUNT(*) FROM questoes WHERE status='publicada') AS questoes_publicadas,
        (SELECT COUNT(*) FROM questoes WHERE status='arquivada') AS questoes_arquivadas;
END$$
DELIMITER ;

-- Pré-condição: prefixo 011 íntegro. CREATE VIEW/CREATE ROUTINE e SELECT necessários.
-- Preservação: somente definições; sem tabelas, alterações de dados ou backfill.
-- Compensação revisada após retorno ao código anterior: restaurar backup ou
-- remover procedures, views consumidoras e depois views de origem, preservando
-- dados, procedure legada e histórico. DDL não possui rollback transacional.
CREATE SQL SECURITY INVOKER VIEW vw_conteudo_classificacao_historica AS
SELECT id AS questao_versao_id, materia_id, materia_nome, assunto_id, assunto_nome
FROM questao_versoes WHERE estado='publicada';

CREATE SQL SECURITY INVOKER VIEW vw_praticas_fatos_desempenho AS
SELECT 'pratica' AS tipo, id, id AS atividade_id, usuario_id,
    respondida_em AS ocorrido_em, correta, materia_id, materia_nome, assunto_id, assunto_nome
FROM pratica_tentativas WHERE estado='respondida';

CREATE SQL SECURITY INVOKER VIEW vw_simulados_fatos_desempenho AS
SELECT 'simulado' AS tipo, r.id, t.id AS atividade_id, t.usuario_id,
    t.finalizada_em AS ocorrido_em, r.correta,
    q.materia_id, q.materia_nome, q.assunto_id, q.assunto_nome
FROM simulado_respostas r JOIN simulado_tentativas t ON t.id=r.tentativa_id
JOIN simulado_versao_itens i ON i.id=r.item_id
JOIN vw_conteudo_classificacao_historica q ON q.questao_versao_id=i.questao_versao_id
WHERE t.estado='finalizada' AND r.alternativa IS NOT NULL;

CREATE SQL SECURITY INVOKER VIEW vw_simulados_atividades AS
SELECT 'simulado' AS tipo, t.id, t.usuario_id, t.finalizada_em AS ocorrido_em, v.titulo
FROM simulado_tentativas t JOIN simulado_versoes v ON v.id=t.simulado_versao_id
WHERE t.estado='finalizada';

DELIMITER $$
CREATE PROCEDURE sp_desempenho_resumo(
    IN p_usuario_id INT, IN p_inicio DATETIME(6), IN p_fim DATETIME(6))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id < 1 OR p_inicio IS NULL OR p_fim IS NULL OR p_inicio >= p_fim THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Usuário e intervalo inválidos';
    END IF;
    WITH fatos AS (
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_praticas_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
        UNION ALL
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_simulados_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
    )
    SELECT COUNT(*) AS total_respostas,
        COALESCE(SUM(CASE WHEN correta=1 THEN 1 ELSE 0 END),0) AS acertos,
        COALESCE(SUM(CASE WHEN tipo='pratica' THEN 1 ELSE 0 END),0) AS pratica,
        COALESCE(SUM(CASE WHEN tipo='simulado' THEN 1 ELSE 0 END),0) AS simulado FROM fatos;
    WITH fatos AS (
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_praticas_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
        UNION ALL
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_simulados_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
    ), ranking AS (
        SELECT materia_id, materia_nome, assunto_id, assunto_nome,
            COUNT(*) OVER (PARTITION BY materia_id) AS total_respostas,
            SUM(CASE WHEN correta=1 THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id) AS acertos,
            SUM(CASE WHEN tipo='pratica' THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id) AS pratica,
            SUM(CASE WHEN tipo='simulado' THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id) AS simulado,
            ROW_NUMBER() OVER (PARTITION BY materia_id ORDER BY ocorrido_em DESC,tipo DESC,id DESC) AS posicao
        FROM fatos
    )
    SELECT materia_id,materia_nome,assunto_id,assunto_nome,total_respostas,acertos,pratica,simulado,posicao
    FROM ranking WHERE posicao=1 ORDER BY materia_id;
    WITH fatos AS (
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_praticas_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
        UNION ALL
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_simulados_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
    ), ranking AS (
        SELECT materia_id, materia_nome, assunto_id, assunto_nome,
            COUNT(*) OVER (PARTITION BY materia_id, assunto_id) AS total_respostas,
            SUM(CASE WHEN correta=1 THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id, assunto_id) AS acertos,
            SUM(CASE WHEN tipo='pratica' THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id, assunto_id) AS pratica,
            SUM(CASE WHEN tipo='simulado' THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id, assunto_id) AS simulado,
            ROW_NUMBER() OVER (PARTITION BY materia_id, assunto_id ORDER BY ocorrido_em DESC,tipo DESC,id DESC) AS posicao
        FROM fatos
    )
    SELECT materia_id,materia_nome,assunto_id,assunto_nome,total_respostas,acertos,pratica,simulado,posicao
    FROM ranking WHERE posicao=1 ORDER BY materia_id, assunto_id;
END$$

CREATE PROCEDURE sp_atividades_recentes(
    IN p_usuario_id INT, IN p_inicio DATETIME(6), IN p_fim DATETIME(6))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id < 1 OR p_inicio IS NULL OR p_fim IS NULL OR p_inicio >= p_fim THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Usuário e intervalo inválidos';
    END IF;
    SELECT tipo,id,ocorrido_em,titulo FROM (
        SELECT tipo,atividade_id AS id,ocorrido_em,CONCAT(materia_nome,' · ',assunto_nome) AS titulo
        FROM vw_praticas_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
        UNION ALL
        SELECT tipo,id,ocorrido_em,titulo FROM vw_simulados_atividades
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
    ) atividades ORDER BY ocorrido_em DESC,tipo DESC,id DESC LIMIT 5;
END$$

CREATE PROCEDURE sp_simulados_contagens_dashboard()
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    SELECT (SELECT COUNT(*) FROM simulados WHERE estado='rascunho') AS rascunhos,
        (SELECT COUNT(*) FROM simulados WHERE estado='publicado') AS publicados,
        (SELECT COUNT(*) FROM simulados WHERE estado='arquivado') AS arquivados,
        (SELECT COUNT(*) FROM simulado_tentativas WHERE estado='finalizada') AS finalizadas;
END$$
DELIMITER ;

DELIMITER $$
-- Pré-condição: prefixo 012 íntegro. CREATE ROUTINE e SELECT necessários.
-- Preservação: somente definições; sem DML, tabelas, FKs, índices ou backfill.
-- As leituras bloqueantes participam da transação externa, sem encerrá-la.
-- Compensação: retornar ao código anterior e restaurar backup ou remover as
-- quinze routines por migration revisada. Preservar dados e histórico/checksums.
-- Não há rollback DDL transacional nem instalação automática no startup.

CREATE PROCEDURE sp_areas_enem_ordenadas()
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    SELECT a.id AS id,
        a.codigo AS codigo,
        a.nome AS nome,
        a.ordem AS ordem FROM areas_enem a ORDER BY a.ordem,a.id;
END$$

CREATE PROCEDURE sp_materias_ativas()
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    SELECT m.id AS id,
        m.nome AS nome,
        m.descricao AS descricao,
        m.area_enem_id AS area_enem_id,
        m.status AS status,
        m.criado_em AS criado_em,
        m.atualizado_em AS atualizado_em FROM materias m WHERE m.status='ativa' ORDER BY m.nome,m.id;
END$$

CREATE PROCEDURE sp_assuntos_ativos(IN p_materia_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF (p_materia_id IS NOT NULL AND p_materia_id<1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT s.id AS id,
        s.nome AS nome,
        s.nome_normalizado AS nome_normalizado,
        s.descricao AS descricao,
        s.materia_id AS materia_id,
        s.status AS status,
        s.criado_em AS criado_em,
        s.atualizado_em AS atualizado_em
    FROM assuntos s JOIN materias m ON m.id=s.materia_id
    WHERE s.status='ativa' AND m.status='ativa' AND (p_materia_id IS NULL OR s.materia_id=p_materia_id)
    ORDER BY s.nome_normalizado,s.id;
END$$

CREATE PROCEDURE sp_impacto_materia(IN p_materia_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_materia_id IS NULL OR p_materia_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT (SELECT COUNT(*) FROM assuntos WHERE materia_id=p_materia_id) AS assuntos,
        (SELECT COUNT(*) FROM questoes q JOIN assuntos s ON s.id=q.assunto_id WHERE s.materia_id=p_materia_id) AS questoes,
        (SELECT COUNT(*) FROM assunto_transferencias WHERE materia_origem_id=p_materia_id OR materia_destino_id=p_materia_id) AS transferencias;
END$$

CREATE PROCEDURE sp_impacto_assunto(IN p_assunto_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_assunto_id IS NULL OR p_assunto_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT (SELECT COUNT(*) FROM questoes WHERE assunto_id=p_assunto_id) AS questoes,
        (SELECT COUNT(*) FROM assunto_transferencias WHERE assunto_id=p_assunto_id) AS transferencias;
END$$

CREATE PROCEDURE sp_assuntos_nao_arquivados(IN p_materia_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_materia_id IS NULL OR p_materia_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT COUNT(*) AS total FROM assuntos WHERE materia_id=p_materia_id AND status<>'arquivada';
END$$

CREATE PROCEDURE sp_bloquear_assunto(IN p_assunto_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_assunto_id IS NULL OR p_assunto_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT s.id AS id,
        s.nome AS nome,
        s.nome_normalizado AS nome_normalizado,
        s.descricao AS descricao,
        s.materia_id AS materia_id,
        s.status AS status,
        s.criado_em AS criado_em,
        s.atualizado_em AS atualizado_em FROM assuntos s WHERE s.id=p_assunto_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_bloquear_materias(IN p_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_ids_json IS NULL OR JSON_TYPE(p_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT m.id AS id,
        m.nome AS nome,
        m.descricao AS descricao,
        m.area_enem_id AS area_enem_id,
        m.status AS status,
        m.criado_em AS criado_em,
        m.atualizado_em AS atualizado_em FROM materias m WHERE m.id IN (SELECT DISTINCT id FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids) ORDER BY m.id FOR UPDATE;
END$$

CREATE PROCEDURE sp_assunto_equivalente(IN p_materia_id BIGINT UNSIGNED, IN p_nome_normalizado VARCHAR(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci, IN p_ignorar_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_materia_id IS NULL OR p_materia_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF (p_ignorar_id IS NOT NULL AND p_ignorar_id<1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_nome_normalizado IS NULL OR p_nome_normalizado='' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Nome normalizado obrigatório';
    END IF;
    SELECT EXISTS(SELECT 1 FROM assuntos s WHERE s.materia_id=p_materia_id
        AND s.nome_normalizado=p_nome_normalizado AND (p_ignorar_id IS NULL OR s.id<>p_ignorar_id)) AS existe;
END$$

CREATE PROCEDURE sp_bloquear_questao(IN p_questao_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_questao_id IS NULL OR p_questao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT q.id AS id,
        q.status AS status,
        q.revisao AS revisao,
        q.criado_em AS criado_em,
        q.atualizado_em AS atualizado_em,
        q.versao_publicada_id AS versao_publicada_id,
        q.enunciado AS enunciado,
        q.alternativa_a AS alternativa_a,
        q.alternativa_b AS alternativa_b,
        q.alternativa_c AS alternativa_c,
        q.alternativa_d AS alternativa_d,
        q.alternativa_e AS alternativa_e,
        q.resposta_correta AS resposta_correta,
        q.explicacao AS explicacao,
        q.dificuldade AS dificuldade,
        q.assunto_id AS assunto_id FROM questoes q WHERE q.id=p_questao_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_versoes_questao(IN p_questao_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_questao_id IS NULL OR p_questao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v WHERE v.questao_id=p_questao_id ORDER BY v.numero;
END$$

CREATE PROCEDURE sp_questao_versao_elegivel(IN p_versao_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_versao_id IS NULL OR p_versao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Flag de lock inválida';
    END IF;
    IF p_bloquear=1 THEN
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND v.id=p_versao_id FOR UPDATE;
    ELSE
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND v.id=p_versao_id;
    END IF;
END$$

CREATE PROCEDURE sp_questoes_elegiveis(IN p_assunto_id BIGINT UNSIGNED, IN p_materia_id BIGINT UNSIGNED, IN p_pagina BIGINT UNSIGNED, IN p_limite INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_deslocamento BIGINT UNSIGNED;
    IF (p_assunto_id IS NOT NULL AND p_assunto_id<1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF (p_materia_id IS NOT NULL AND p_materia_id<1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_pagina IS NULL OR p_pagina<1 OR p_limite IS NULL OR p_limite<1 OR p_limite>100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Paginação inválida';
    END IF;
    SET v_deslocamento=(p_pagina-1)*p_limite;
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND (p_assunto_id IS NULL OR v.assunto_id=p_assunto_id) AND (p_materia_id IS NULL OR v.materia_id=p_materia_id) ORDER BY v.questao_id LIMIT p_limite OFFSET v_deslocamento;
    SELECT COUNT(*) AS total FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND (p_assunto_id IS NULL OR v.assunto_id=p_assunto_id) AND (p_materia_id IS NULL OR v.materia_id=p_materia_id);
END$$

CREATE PROCEDURE sp_questoes_versoes_elegiveis(IN p_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_ids_json IS NULL OR JSON_TYPE(p_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND v.id IN (SELECT DISTINCT id FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids);
END$$

CREATE PROCEDURE sp_questoes_versoes_historicas(IN p_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_ids_json IS NULL OR JSON_TYPE(p_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v
    JOIN vw_conteudo_classificacao_historica c ON c.questao_versao_id=v.id
    WHERE v.id IN (SELECT DISTINCT id FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids);
END$$

DELIMITER ;

DELIMITER $$
-- Interfaces especializadas de Práticas e Simulados; transação pertence ao chamador.

CREATE PROCEDURE sp_pratica_por_chave(IN p_usuario_id BIGINT UNSIGNED, IN p_chave CHAR(36) CHARACTER SET ascii COLLATE ascii_bin, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_chave IS NULL OR CHAR_LENGTH(p_chave)<>36 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Chave inválida'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.chave_envio=p_chave FOR UPDATE;
    ELSE
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.chave_envio=p_chave;
    END IF;
END$$

CREATE PROCEDURE sp_pratica_propria(IN p_usuario_id BIGINT UNSIGNED, IN p_tentativa_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_tentativa_id IS NULL OR p_tentativa_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.id=p_tentativa_id FOR UPDATE;
    ELSE
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.id=p_tentativa_id;
    END IF;
END$$

CREATE PROCEDURE sp_praticas_historico(IN p_usuario_id BIGINT UNSIGNED, IN p_assunto_id BIGINT UNSIGNED, IN p_pagina BIGINT UNSIGNED, IN p_limite INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_offset BIGINT UNSIGNED;
    IF p_pagina IS NULL OR p_pagina<1 OR p_limite IS NULL OR p_limite<1 OR p_limite>100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Paginação inválida';
    END IF;
    SET v_offset=(p_pagina-1)*p_limite;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_assunto_id IS NOT NULL AND p_assunto_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.estado='respondida' AND (p_assunto_id IS NULL OR p.assunto_id=p_assunto_id) ORDER BY p.respondida_em DESC,p.id DESC LIMIT v_offset,p_limite;
    SELECT COUNT(*) AS total FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.estado='respondida' AND (p_assunto_id IS NULL OR p.assunto_id=p_assunto_id);
END$$

CREATE PROCEDURE sp_praticas_fatos(IN p_usuario_id BIGINT UNSIGNED, IN p_inicio DATETIME(6), IN p_fim DATETIME(6))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_inicio IS NULL OR p_fim IS NULL OR p_inicio>=p_fim THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Intervalo inválido'; END IF;
    SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.estado='respondida' AND p.respondida_em>=p_inicio AND p.respondida_em<p_fim ORDER BY p.respondida_em,p.id;
END$$

CREATE PROCEDURE sp_bloquear_simulado(IN p_simulado_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_simulado_id IS NULL OR p_simulado_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT s.id AS id,
        s.titulo AS titulo,
        s.estado AS estado,
        s.revisao AS revisao,
        s.autor_id AS autor_id,
        s.criado_em AS criado_em,
        s.atualizado_em AS atualizado_em,
        s.simulado_versao_id AS simulado_versao_id FROM simulados s WHERE s.id=p_simulado_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_simulado_itens(IN p_simulado_id BIGINT UNSIGNED, IN p_versao_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_versao_id IS NULL THEN
        SELECT i.id AS id,
        i.simulado_id AS simulado_id,
        i.posicao AS posicao,
        i.questao_id AS questao_id,
        i.questao_versao_id AS questao_versao_id FROM simulado_rascunho_itens i WHERE i.simulado_id=p_simulado_id ORDER BY i.posicao;
    ELSE
        SELECT i.id AS id,
        i.simulado_versao_id AS simulado_versao_id,
        i.posicao AS posicao,
        i.questao_id AS questao_id,
        i.questao_versao_id AS questao_versao_id FROM simulado_versao_itens i WHERE i.simulado_versao_id=p_versao_id ORDER BY i.posicao;
    END IF;
END$$

CREATE PROCEDURE sp_simulados_itens_lote(IN p_simulado_ids_json JSON, IN p_versao_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_versao_ids_json IS NULL THEN
        IF p_simulado_ids_json IS NULL OR JSON_TYPE(p_simulado_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_simulado_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
        SELECT i.id AS id,
        i.simulado_id AS simulado_id,
        i.posicao AS posicao,
        i.questao_id AS questao_id,
        i.questao_versao_id AS questao_versao_id FROM simulado_rascunho_itens i WHERE i.simulado_id IN (SELECT DISTINCT id FROM JSON_TABLE(p_simulado_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids) ORDER BY i.simulado_id,i.posicao;
    ELSE
        IF p_versao_ids_json IS NULL OR JSON_TYPE(p_versao_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
        SELECT i.id AS id,
        i.simulado_versao_id AS simulado_versao_id,
        i.posicao AS posicao,
        i.questao_id AS questao_id,
        i.questao_versao_id AS questao_versao_id FROM simulado_versao_itens i WHERE i.simulado_versao_id IN (SELECT DISTINCT id FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids) ORDER BY i.simulado_versao_id,i.posicao;
    END IF;
END$$

CREATE PROCEDURE sp_simulados_andamentos_lote(IN p_usuario_id BIGINT UNSIGNED, IN p_versao_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_versao_ids_json IS NULL OR JSON_TYPE(p_versao_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.simulado_versao_id IN (SELECT DISTINCT id FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids) AND t.estado='em_andamento';
END$$

CREATE PROCEDURE sp_simulados_titulos_lote(IN p_versao_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_versao_ids_json IS NULL OR JSON_TYPE(p_versao_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT v.id AS id,v.titulo AS titulo FROM simulado_versoes v WHERE v.id IN (SELECT DISTINCT id FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids);
END$$

CREATE PROCEDURE sp_simulados_listar(IN p_pagina BIGINT UNSIGNED, IN p_limite INT, IN p_estado VARCHAR(20))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_offset BIGINT UNSIGNED;
    IF p_pagina IS NULL OR p_pagina<1 OR p_limite IS NULL OR p_limite<1 OR p_limite>100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Paginação inválida';
    END IF;
    SET v_offset=(p_pagina-1)*p_limite;
    SELECT s.id AS id,
        s.titulo AS titulo,
        s.estado AS estado,
        s.revisao AS revisao,
        s.autor_id AS autor_id,
        s.criado_em AS criado_em,
        s.atualizado_em AS atualizado_em,
        s.simulado_versao_id AS simulado_versao_id FROM simulados s WHERE (p_estado IS NULL OR s.estado=p_estado) ORDER BY s.id DESC LIMIT v_offset,p_limite;
    SELECT COUNT(*) AS total FROM simulados s WHERE (p_estado IS NULL OR s.estado=p_estado);
END$$

CREATE PROCEDURE sp_simulado_tentativa_propria(IN p_usuario_id BIGINT UNSIGNED, IN p_tentativa_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_tentativa_id IS NULL OR p_tentativa_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.id=p_tentativa_id FOR UPDATE;
    ELSE
        SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.id=p_tentativa_id;
    END IF;
END$$

CREATE PROCEDURE sp_simulado_tentativa_por_chave(IN p_usuario_id BIGINT UNSIGNED, IN p_chave CHAR(36) CHARACTER SET ascii COLLATE ascii_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_chave IS NULL OR CHAR_LENGTH(p_chave)<>36 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Chave inválida'; END IF;
    SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.chave_envio=p_chave FOR UPDATE;
END$$

CREATE PROCEDURE sp_simulado_em_andamento(IN p_usuario_id BIGINT UNSIGNED, IN p_versao_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_versao_id IS NULL OR p_versao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.simulado_versao_id=p_versao_id AND t.estado='em_andamento' FOR UPDATE;
END$$

CREATE PROCEDURE sp_simulado_respostas(IN p_tentativa_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_tentativa_id IS NULL OR p_tentativa_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT r.id AS r_id,
        r.tentativa_id AS r_tentativa_id,
        r.item_id AS r_item_id,
        r.alternativa AS r_alternativa,
        r.correta AS r_correta,
        i.id AS i_id,
        i.simulado_versao_id AS i_simulado_versao_id,
        i.posicao AS i_posicao,
        i.questao_id AS i_questao_id,
        i.questao_versao_id AS i_questao_versao_id FROM simulado_respostas r JOIN simulado_versao_itens i ON i.id=r.item_id WHERE r.tentativa_id=p_tentativa_id ORDER BY i.posicao FOR UPDATE;
    ELSE
        SELECT r.id AS r_id,
        r.tentativa_id AS r_tentativa_id,
        r.item_id AS r_item_id,
        r.alternativa AS r_alternativa,
        r.correta AS r_correta,
        i.id AS i_id,
        i.simulado_versao_id AS i_simulado_versao_id,
        i.posicao AS i_posicao,
        i.questao_id AS i_questao_id,
        i.questao_versao_id AS i_questao_versao_id FROM simulado_respostas r JOIN simulado_versao_itens i ON i.id=r.item_id WHERE r.tentativa_id=p_tentativa_id ORDER BY i.posicao;
    END IF;
END$$

CREATE PROCEDURE sp_simulados_historico(IN p_usuario_id BIGINT UNSIGNED, IN p_pagina BIGINT UNSIGNED, IN p_limite INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_offset BIGINT UNSIGNED;
    IF p_pagina IS NULL OR p_pagina<1 OR p_limite IS NULL OR p_limite<1 OR p_limite>100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Paginação inválida';
    END IF;
    SET v_offset=(p_pagina-1)*p_limite;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.estado='finalizada' ORDER BY t.finalizada_em DESC,t.id DESC LIMIT v_offset,p_limite;
    SELECT COUNT(*) AS total FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.estado='finalizada';
END$$

CREATE PROCEDURE sp_simulados_fatos(IN p_usuario_id BIGINT UNSIGNED, IN p_inicio DATETIME(6), IN p_fim DATETIME(6))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_inicio IS NULL OR p_fim IS NULL OR p_inicio>=p_fim THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Intervalo inválido'; END IF;
    SELECT r.id AS r_id,
        r.tentativa_id AS r_tentativa_id,
        r.item_id AS r_item_id,
        r.alternativa AS r_alternativa,
        r.correta AS r_correta,
        i.id AS i_id,
        i.simulado_versao_id AS i_simulado_versao_id,
        i.posicao AS i_posicao,
        i.questao_id AS i_questao_id,
        i.questao_versao_id AS i_questao_versao_id,
        t.id AS t_id,
        t.usuario_id AS t_usuario_id,
        t.simulado_versao_id AS t_simulado_versao_id,
        t.estado AS t_estado,
        t.revisao AS t_revisao,
        t.chave_envio AS t_chave_envio,
        t.iniciada_em AS t_iniciada_em,
        t.finalizada_em AS t_finalizada_em,
        t.total AS t_total,
        t.respondidas AS t_respondidas,
        t.acertos AS t_acertos,
        t.erros AS t_erros,
        t.em_branco AS t_em_branco,
        t.percentual_acerto AS t_percentual_acerto,
        t.em_andamento_marcador AS t_em_andamento_marcador FROM simulado_respostas r JOIN simulado_versao_itens i ON i.id=r.item_id JOIN simulado_tentativas t ON t.id=r.tentativa_id WHERE t.usuario_id=p_usuario_id AND t.estado='finalizada' AND r.alternativa IS NOT NULL AND t.finalizada_em>=p_inicio AND t.finalizada_em<p_fim ORDER BY t.finalizada_em,r.id;
END$$

DELIMITER ;

DELIMITER $$
-- Pré-condição: prefixo 014 íntegro; somente definições, sem DML funcional.
-- CREATE ROUTINE no instalador; EXECUTE e privilégios das tabelas no invocador.
-- Sem downgrade automático: restaurar/compensar somente as seis routines após
-- retornar o código à versão anterior. Preservar dados e histórico/checksums.
CREATE PROCEDURE sp_plano_atual(IN p_usuario_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.geracao AS geracao,
        p.atual AS atual,
        p.usuario_atual AS usuario_atual,
        p.periodo AS periodo,
        p.gerado_em AS gerado_em,
        p.chave_envio AS chave_envio,
        p.operacao AS operacao,
        p.plano_anterior_id AS plano_anterior_id FROM planos_estudo p WHERE p.usuario_id=p_usuario_id AND p.atual=1 FOR UPDATE;
    ELSE
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.geracao AS geracao,
        p.atual AS atual,
        p.usuario_atual AS usuario_atual,
        p.periodo AS periodo,
        p.gerado_em AS gerado_em,
        p.chave_envio AS chave_envio,
        p.operacao AS operacao,
        p.plano_anterior_id AS plano_anterior_id FROM planos_estudo p WHERE p.usuario_id=p_usuario_id AND p.atual=1;
    END IF;
END$$

CREATE PROCEDURE sp_plano_por_chave(IN p_usuario_id BIGINT UNSIGNED, IN p_chave CHAR(36) CHARACTER SET ascii COLLATE ascii_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_chave IS NULL OR CHAR_LENGTH(p_chave)<>36 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Chave inválida'; END IF;
    SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.geracao AS geracao,
        p.atual AS atual,
        p.usuario_atual AS usuario_atual,
        p.periodo AS periodo,
        p.gerado_em AS gerado_em,
        p.chave_envio AS chave_envio,
        p.operacao AS operacao,
        p.plano_anterior_id AS plano_anterior_id FROM planos_estudo p WHERE p.usuario_id=p_usuario_id AND p.chave_envio=p_chave FOR UPDATE;
END$$

CREATE PROCEDURE sp_plano_itens(IN p_plano_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_plano_id IS NULL OR p_plano_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT i.id AS id,
        i.plano_id AS plano_id,
        i.assunto_id AS assunto_id,
        i.materia_id AS materia_id,
        i.posicao AS posicao,
        i.snapshot AS snapshot,
        i.estado AS estado,
        i.concluido_em AS concluido_em FROM plano_estudo_itens i WHERE i.plano_id=p_plano_id ORDER BY i.posicao FOR UPDATE;
END$$

CREATE PROCEDURE sp_plano_item_proprio(IN p_usuario_id BIGINT UNSIGNED, IN p_item_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_item_id IS NULL OR p_item_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT i.id AS i_id,
        i.plano_id AS i_plano_id,
        i.assunto_id AS i_assunto_id,
        i.materia_id AS i_materia_id,
        i.posicao AS i_posicao,
        i.snapshot AS i_snapshot,
        i.estado AS i_estado,
        i.concluido_em AS i_concluido_em,
        p.id AS p_id,
        p.usuario_id AS p_usuario_id,
        p.geracao AS p_geracao,
        p.atual AS p_atual,
        p.usuario_atual AS p_usuario_atual,
        p.periodo AS p_periodo,
        p.gerado_em AS p_gerado_em,
        p.chave_envio AS p_chave_envio,
        p.operacao AS p_operacao,
        p.plano_anterior_id AS p_plano_anterior_id
    FROM plano_estudo_itens i JOIN planos_estudo p ON p.id=i.plano_id
    WHERE p.usuario_id=p_usuario_id AND i.id=p_item_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_pares_elegiveis_plano(IN p_assunto_ids JSON, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_assunto_ids IS NULL OR JSON_TYPE(p_assunto_ids)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista inválida';
    END IF;
    IF EXISTS(SELECT 1 FROM JSON_TABLE(p_assunto_ids, '$[*]' COLUMNS(valor JSON PATH '$')) ids
        WHERE ids.valor IS NULL OR JSON_TYPE(ids.valor)<>'INTEGER' OR CAST(ids.valor AS DECIMAL(20,0))<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido';
    END IF;
    IF p_bloquear=1 THEN
        SELECT v.assunto_id AS assunto_id, v.materia_id AS materia_id FROM questao_versoes v
        JOIN questoes q ON q.id=v.questao_id
        JOIN assuntos a ON a.id=v.assunto_id
        JOIN materias m ON m.id=v.materia_id
        WHERE v.assunto_id IN (SELECT ids.id FROM JSON_TABLE(p_assunto_ids, '$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$')) ids)
          AND v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id
          AND a.status='ativa' AND m.status='ativa' AND a.materia_id=m.id FOR SHARE;
    ELSE
        SELECT v.assunto_id AS assunto_id, v.materia_id AS materia_id FROM questao_versoes v
        JOIN questoes q ON q.id=v.questao_id
        JOIN assuntos a ON a.id=v.assunto_id
        JOIN materias m ON m.id=v.materia_id
        WHERE v.assunto_id IN (SELECT ids.id FROM JSON_TABLE(p_assunto_ids, '$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$')) ids)
          AND v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id
          AND a.status='ativa' AND m.status='ativa' AND a.materia_id=m.id;
    END IF;
END$$

CREATE PROCEDURE sp_eliminar_planos_proprios(IN p_usuario_id BIGINT UNSIGNED)
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_fim BOOLEAN DEFAULT FALSE;
    DECLARE v_plano_id BIGINT UNSIGNED;
    DECLARE v_planos BIGINT UNSIGNED DEFAULT 0;
    DECLARE v_itens BIGINT UNSIGNED DEFAULT 0;
    DECLARE planos CURSOR FOR SELECT id FROM planos_estudo
        WHERE usuario_id=p_usuario_id ORDER BY id DESC FOR UPDATE;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fim=TRUE;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    -- O participante já possui o lock de identidade; a decisão controla a transação.
    OPEN planos;
    eliminar: LOOP
        FETCH planos INTO v_plano_id;
        IF v_fim THEN LEAVE eliminar; END IF;
        DELETE i FROM plano_estudo_itens i JOIN planos_estudo p ON p.id=i.plano_id
            WHERE i.plano_id=v_plano_id AND p.usuario_id=p_usuario_id;
        SET v_itens=v_itens+ROW_COUNT();
        DELETE FROM planos_estudo WHERE id=v_plano_id AND usuario_id=p_usuario_id;
        SET v_planos=v_planos+ROW_COUNT();
    END LOOP;
    CLOSE planos;
    SELECT v_planos AS planos_eliminados, v_itens AS itens_eliminados;
END$$

DELIMITER ;

DELIMITER $$
-- Pré-condição: prefixo 015 íntegro. Instalação somente de definições.
-- Instalador: CREATE ROUTINE; invocador: EXECUTE e privilégios das tabelas.
-- Sem transação própria, DML de instalação ou mudança de retenção.
-- Reversão: código anterior e restauração/compensação revisada das onze routines;
-- preservar tabelas, dados, evidências, recursos anteriores e histórico/checksums.
CREATE PROCEDURE sp_usuario_por_email(IN p_email VARCHAR(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_email IS NULL OR CHAR_LENGTH(p_email)<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='E-mail inválido'; END IF;
    SELECT u.id, u.nome, u.email, u.senha_hash, u.perfil, u.ativo, u.criado_em
    FROM usuarios u WHERE u.email=p_email;
END$$

CREATE PROCEDURE sp_consultar_sessao(IN p_identificador_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_identificador_hash IS NULL OR CHAR_LENGTH(p_identificador_hash)<>64 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Hash inválido'; END IF;
    SELECT s.id AS s_id, s.usuario_id AS s_usuario_id, s.identificador_hash AS s_identificador_hash,
        s.criada_em AS s_criada_em, s.ultimo_acesso_em AS s_ultimo_acesso_em,
        s.expira_em AS s_expira_em, s.reautenticada_em AS s_reautenticada_em, s.revogada_em AS s_revogada_em,
        u.id AS u_id, u.nome AS u_nome, u.email AS u_email, u.senha_hash AS u_senha_hash,
        u.perfil AS u_perfil, u.ativo AS u_ativo, u.criado_em AS u_criado_em
    FROM sessoes s LEFT JOIN usuarios u ON u.id=s.usuario_id
    WHERE s.identificador_hash=p_identificador_hash;
END$$

CREATE PROCEDURE sp_renovar_acesso_sessao(IN p_sessao_id BIGINT UNSIGNED, IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_id BIGINT UNSIGNED DEFAULT NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_id=NULL;
    IF p_sessao_id IS NULL OR p_sessao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    SELECT id INTO v_id FROM sessoes WHERE id=p_sessao_id AND revogada_em IS NULL
        AND expira_em>p_agora AND ultimo_acesso_em>p_agora-INTERVAL 30 MINUTE FOR UPDATE;
    IF v_id IS NOT NULL THEN
        UPDATE sessoes SET ultimo_acesso_em=p_agora WHERE id=v_id;
    END IF;
    SELECT (v_id IS NOT NULL) AS correspondencias;
END$$

CREATE PROCEDURE sp_revogar_sessao(IN p_sessao_id BIGINT UNSIGNED, IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_afetadas BIGINT UNSIGNED;
    IF p_sessao_id IS NULL OR p_sessao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    UPDATE sessoes SET revogada_em=p_agora WHERE id=p_sessao_id AND revogada_em IS NULL;
    SET v_afetadas=ROW_COUNT();
    SELECT v_afetadas AS afetadas;
END$$

CREATE PROCEDURE sp_revogar_sessoes_usuario(IN p_usuario_id BIGINT UNSIGNED, IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_afetadas BIGINT UNSIGNED;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    UPDATE sessoes SET revogada_em=p_agora WHERE usuario_id=p_usuario_id AND revogada_em IS NULL;
    SET v_afetadas=ROW_COUNT();
    SELECT v_afetadas AS afetadas;
END$$

CREATE PROCEDURE sp_usuario_ativo_bloqueado(IN p_usuario_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT u.id, u.nome, u.email, u.senha_hash, u.perfil, u.ativo, u.criado_em
    FROM usuarios u WHERE u.id=p_usuario_id AND u.ativo=1 FOR UPDATE;
END$$

CREATE PROCEDURE sp_preparar_limite_autenticacao(IN p_chave_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin, IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_chave_hash IS NULL OR CHAR_LENGTH(p_chave_hash)<>64 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Hash inválido'; END IF;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    INSERT INTO auth_limites(chave_hash,falhas,janela_inicio) VALUES(p_chave_hash,0,p_agora)
        ON DUPLICATE KEY UPDATE chave_hash=p_chave_hash;
    SELECT chave_hash, falhas, janela_inicio, bloqueado_ate FROM auth_limites
        WHERE chave_hash=p_chave_hash FOR UPDATE;
END$$

CREATE PROCEDURE sp_limpar_autenticacao(IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_corte DATETIME(6);
    DECLARE v_sessoes BIGINT UNSIGNED;
    DECLARE v_limites BIGINT UNSIGNED;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    SET v_corte=p_agora-INTERVAL 24 HOUR;
    DELETE FROM sessoes WHERE expira_em<v_corte OR revogada_em<v_corte
        OR (usuario_id IS NOT NULL AND ultimo_acesso_em<v_corte-INTERVAL 30 MINUTE);
    SET v_sessoes=ROW_COUNT();
    DELETE FROM auth_limites WHERE janela_inicio<v_corte-INTERVAL 15 MINUTE
        AND (bloqueado_ate IS NULL OR bloqueado_ate<v_corte);
    SET v_limites=ROW_COUNT();
    SELECT v_sessoes AS sessoes, v_limites AS limites;
END$$

CREATE PROCEDURE sp_bloquear_identidade_privacidade(IN p_usuario_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT id FROM usuarios WHERE id=p_usuario_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_ultimas_decisoes_privacidade(IN p_usuario_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_uso_id BIGINT DEFAULT NULL;
    DECLARE v_uso_usuario_id INT;
    DECLARE v_uso_tipo VARCHAR(8);
    DECLARE v_uso_acao VARCHAR(8);
    DECLARE v_uso_versao VARCHAR(20);
    DECLARE v_uso_documento_sha256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin;
    DECLARE v_uso_registrado_em DATETIME(6);
    DECLARE v_uso_chave_envio CHAR(36) CHARACTER SET ascii COLLATE ascii_bin;
    DECLARE v_uso_revisao_base BIGINT;
    DECLARE v_plano_id BIGINT DEFAULT NULL;
    DECLARE v_plano_usuario_id INT;
    DECLARE v_plano_tipo VARCHAR(8);
    DECLARE v_plano_acao VARCHAR(8);
    DECLARE v_plano_versao VARCHAR(20);
    DECLARE v_plano_documento_sha256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin;
    DECLARE v_plano_registrado_em DATETIME(6);
    DECLARE v_plano_chave_envio CHAR(36) CHARACTER SET ascii COLLATE ascii_bin;
    DECLARE v_plano_revisao_base BIGINT;
    DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    -- Duas leituras correntes, nesta ordem; a projeção final não relê tabelas.
    SELECT id,usuario_id,tipo,acao,versao,documento_sha256,registrado_em,chave_envio,revisao_base
        INTO v_uso_id,v_uso_usuario_id,v_uso_tipo,v_uso_acao,v_uso_versao,v_uso_documento_sha256,
             v_uso_registrado_em,v_uso_chave_envio,v_uso_revisao_base
        FROM registros_privacidade WHERE usuario_id=p_usuario_id AND tipo='uso'
        ORDER BY id DESC LIMIT 1 FOR UPDATE;
    SELECT id,usuario_id,tipo,acao,versao,documento_sha256,registrado_em,chave_envio,revisao_base
        INTO v_plano_id,v_plano_usuario_id,v_plano_tipo,v_plano_acao,v_plano_versao,v_plano_documento_sha256,
             v_plano_registrado_em,v_plano_chave_envio,v_plano_revisao_base
        FROM registros_privacidade WHERE usuario_id=p_usuario_id AND tipo='plano'
        ORDER BY id DESC LIMIT 1 FOR UPDATE;
    SELECT decisoes.id, decisoes.usuario_id, decisoes.tipo, decisoes.acao, decisoes.versao,
        decisoes.documento_sha256, decisoes.registrado_em, decisoes.chave_envio, decisoes.revisao_base
    FROM (
        SELECT v_uso_id AS id, v_uso_usuario_id AS usuario_id, v_uso_tipo AS tipo,
            v_uso_acao AS acao, v_uso_versao AS versao, v_uso_documento_sha256 AS documento_sha256,
            v_uso_registrado_em AS registrado_em, v_uso_chave_envio AS chave_envio, v_uso_revisao_base AS revisao_base
        WHERE v_uso_id IS NOT NULL
        UNION ALL
        SELECT v_plano_id, v_plano_usuario_id, v_plano_tipo, v_plano_acao, v_plano_versao,
            v_plano_documento_sha256, v_plano_registrado_em, v_plano_chave_envio, v_plano_revisao_base
        WHERE v_plano_id IS NOT NULL
    ) decisoes ORDER BY FIELD(decisoes.tipo,'uso','plano');
END$$

CREATE PROCEDURE sp_decisao_privacidade_por_chave(IN p_usuario_id BIGINT UNSIGNED, IN p_chave CHAR(36) CHARACTER SET ascii COLLATE ascii_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_chave IS NULL OR CHAR_LENGTH(p_chave)<>36 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Chave inválida'; END IF;
    SELECT id,usuario_id,tipo,acao,versao,documento_sha256,registrado_em,chave_envio,revisao_base
    FROM registros_privacidade WHERE usuario_id=p_usuario_id AND chave_envio=p_chave FOR UPDATE;
END$$

DELIMITER ;

DELIMITER $$
-- Pré-condição: 016 íntegro. Somente routines; sem alteração de dados ou FKs.
-- DDL não possui rollback transacional. Aplicar após backup validado.
-- Compensação: restaurar backup ou remover as duas routines em migration revisada.
CREATE PROCEDURE sp_alunos_admin(
    IN p_busca VARCHAR(254), IN p_ativo TINYINT,
    IN p_offset BIGINT, IN p_limite INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_offset IS NULL OR p_offset < 0 OR p_limite IS NULL OR
       p_limite < 1 OR p_limite > 100 OR
       (p_ativo IS NOT NULL AND p_ativo NOT IN (0,1)) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Parâmetros de consulta inválidos';
    END IF;
    SELECT id,nome,email,perfil,ativo,criado_em FROM usuarios
    WHERE perfil='aluno' AND (p_ativo IS NULL OR ativo=p_ativo)
      AND (p_busca IS NULL OR p_busca='' OR LOCATE(p_busca,nome)>0 OR LOCATE(LOWER(p_busca),email)>0)
    ORDER BY criado_em DESC,id DESC LIMIT p_limite OFFSET p_offset;
    SELECT COUNT(*) AS total_itens FROM usuarios
    WHERE perfil='aluno' AND (p_ativo IS NULL OR ativo=p_ativo)
      AND (p_busca IS NULL OR p_busca='' OR LOCATE(p_busca,nome)>0 OR LOCATE(LOWER(p_busca),email)>0);
END$$

CREATE PROCEDURE sp_usuario_gestao_bloqueado(IN p_usuario_id INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Identificador inválido';
    END IF;
    SELECT id,nome,email,senha_hash,perfil,ativo,criado_em FROM usuarios
    WHERE id=p_usuario_id FOR UPDATE;
END$$
DELIMITER ;
