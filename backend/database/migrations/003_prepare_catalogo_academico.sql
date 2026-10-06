-- Pre-condicao: migrations 000 a 002 aplicadas em MySQL 8.
-- Preservacao: somente adiciona estruturas e preenche dados derivaveis com seguranca.
-- Reversao: restaurar backup ou usar migration compensatoria revisada.

CREATE TABLE areas_enem (
    id INT NOT NULL,
    codigo VARCHAR(50) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    ordem SMALLINT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_areas_enem_codigo UNIQUE (codigo),
    CONSTRAINT uq_areas_enem_nome UNIQUE (nome),
    CONSTRAINT uq_areas_enem_ordem UNIQUE (ordem)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

INSERT INTO areas_enem (id, codigo, nome, ordem) VALUES
    (1, 'linguagens', 'Linguagens', 1),
    (2, 'ciencias-humanas', 'Ciências Humanas', 2),
    (3, 'ciencias-natureza', 'Ciências da Natureza', 3),
    (4, 'matematica', 'Matemática', 4);

ALTER TABLE materias
    ADD COLUMN area_enem_id INT NULL AFTER descricao,
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'ativa' AFTER area_enem_id,
    ADD COLUMN criado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) AFTER status,
    ADD COLUMN atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6) AFTER criado_em;

ALTER TABLE assuntos
    ADD COLUMN nome_normalizado VARCHAR(150)
        CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER nome,
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'ativa' AFTER materia_id,
    ADD COLUMN criado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) AFTER status,
    ADD COLUMN atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6) AFTER criado_em;

UPDATE assuntos
SET nome_normalizado = LOWER(REGEXP_REPLACE(TRIM(nome), '[[:space:]]+', ' '));

UPDATE materias
SET area_enem_id = CASE
    WHEN CONVERT(LOWER(REGEXP_REPLACE(TRIM(nome), '[[:space:]]+', ' ')) USING utf8mb4)
        COLLATE utf8mb4_0900_ai_ci IN (
            'português', 'língua portuguesa', 'literatura', 'inglês',
            'língua inglesa', 'espanhol', 'língua espanhola', 'artes',
            'educação física', 'tecnologias da informação e comunicação'
        ) THEN 1
    WHEN CONVERT(LOWER(REGEXP_REPLACE(TRIM(nome), '[[:space:]]+', ' ')) USING utf8mb4)
        COLLATE utf8mb4_0900_ai_ci IN (
            'história', 'geografia', 'filosofia', 'sociologia'
        ) THEN 2
    WHEN CONVERT(LOWER(REGEXP_REPLACE(TRIM(nome), '[[:space:]]+', ' ')) USING utf8mb4)
        COLLATE utf8mb4_0900_ai_ci IN ('biologia', 'física', 'química') THEN 3
    WHEN CONVERT(LOWER(REGEXP_REPLACE(TRIM(nome), '[[:space:]]+', ' ')) USING utf8mb4)
        COLLATE utf8mb4_0900_ai_ci = 'matemática' THEN 4
    ELSE NULL
END;

CREATE TABLE assunto_transferencias (
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
) ENGINE = InnoDB
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
