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
