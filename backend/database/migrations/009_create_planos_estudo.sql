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
