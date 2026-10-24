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
