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
