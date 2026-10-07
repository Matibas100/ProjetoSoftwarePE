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
