USE plataforma_enem;

ALTER TABLE questoes
    DROP FOREIGN KEY fk_questoes_assuntos;

ALTER TABLE questoes
    ADD CONSTRAINT fk_questoes_assuntos
        FOREIGN KEY (assunto_id)
        REFERENCES assuntos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT;
