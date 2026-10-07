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
