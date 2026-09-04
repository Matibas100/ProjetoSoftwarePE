-- Pre-condicao: migration 000 aplicada com fk_questoes_assuntos em CASCADE.
-- Preservacao: altera somente a politica de exclusao, sem remover dados.
-- Reversao: recriar a foreign key com ON DELETE CASCADE, ciente do risco de perda.

ALTER TABLE questoes
    DROP FOREIGN KEY fk_questoes_assuntos;

ALTER TABLE questoes
    ADD CONSTRAINT fk_questoes_assuntos
        FOREIGN KEY (assunto_id)
        REFERENCES assuntos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT;
