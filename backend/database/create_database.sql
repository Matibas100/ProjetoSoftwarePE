CREATE DATABASE IF NOT EXISTS plataforma_enem
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE plataforma_enem;

CREATE TABLE IF NOT EXISTS materias (
    id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_materias_nome UNIQUE (nome)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS assuntos (
    id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT NULL,
    materia_id INT NOT NULL,
    PRIMARY KEY (id),
    INDEX ix_assuntos_materia_id (materia_id),
    CONSTRAINT fk_assuntos_materias
        FOREIGN KEY (materia_id)
        REFERENCES materias (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
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
    CONSTRAINT fk_questoes_assuntos
        FOREIGN KEY (assunto_id)
        REFERENCES assuntos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
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
