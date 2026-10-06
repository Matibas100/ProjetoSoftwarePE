-- Pre-condicao: migration 003 aplicada e auditorias sem pendencias.
-- Preservacao: os prechecks interrompem antes do DDL final, sem apagar ou mesclar dados.
-- Reversao: restaurar backup ou criar migration compensatoria; nunca restaurar cascata destrutiva.

DROP PROCEDURE IF EXISTS sp_precheck_catalogo_004;

DELIMITER $$

CREATE PROCEDURE sp_precheck_catalogo_004()
BEGIN
    IF (SELECT COUNT(*) FROM areas_enem) <> 4 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'CATALOGO_004_AREAS_FIXAS_INVALIDAS';
    END IF;

    IF EXISTS (SELECT 1 FROM materias WHERE area_enem_id IS NULL) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'CATALOGO_004_MATERIAS_NAO_CLASSIFICADAS';
    END IF;

    IF EXISTS (
        SELECT 1 FROM assuntos
        WHERE nome_normalizado IS NULL OR CHAR_LENGTH(TRIM(nome_normalizado)) = 0
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'CATALOGO_004_ASSUNTOS_SEM_NOME_NORMALIZADO';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM assuntos
        GROUP BY materia_id, nome_normalizado
        HAVING COUNT(*) > 1
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'CATALOGO_004_ASSUNTOS_NORMALIZADOS_CONFLITANTES';
    END IF;
END$$

DELIMITER ;

CALL sp_precheck_catalogo_004();
DROP PROCEDURE sp_precheck_catalogo_004;

ALTER TABLE materias
    MODIFY COLUMN area_enem_id INT NOT NULL,
    ADD INDEX ix_materias_area_enem_id (area_enem_id),
    ADD INDEX ix_materias_status (status),
    ADD CONSTRAINT ck_materias_status
        CHECK (status IN ('ativa', 'inativa', 'arquivada')),
    ADD CONSTRAINT fk_materias_areas_enem FOREIGN KEY (area_enem_id)
        REFERENCES areas_enem (id) ON UPDATE RESTRICT ON DELETE RESTRICT;

ALTER TABLE assuntos
    DROP FOREIGN KEY fk_assuntos_materias;

ALTER TABLE assuntos
    MODIFY COLUMN nome_normalizado VARCHAR(150)
        CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
    ADD INDEX ix_assuntos_status (status),
    ADD CONSTRAINT uq_assuntos_materia_nome_normalizado
        UNIQUE (materia_id, nome_normalizado),
    ADD CONSTRAINT ck_assuntos_status
        CHECK (status IN ('ativa', 'inativa', 'arquivada')),
    ADD CONSTRAINT fk_assuntos_materias FOREIGN KEY (materia_id)
        REFERENCES materias (id) ON UPDATE RESTRICT ON DELETE RESTRICT;

ALTER TABLE questoes
    DROP FOREIGN KEY fk_questoes_assuntos;

ALTER TABLE questoes
    ADD CONSTRAINT fk_questoes_assuntos FOREIGN KEY (assunto_id)
        REFERENCES assuntos (id) ON UPDATE RESTRICT ON DELETE RESTRICT;
