-- Pré-condição: prefixo 007 completo. Tabelas vazias, sem backfill.
-- Reversão: backup ou migration compensatória; preservar tentativas concluídas.
CREATE TABLE simulados (
	id INTEGER NOT NULL AUTO_INCREMENT,
	titulo VARCHAR(150) NOT NULL,
	estado VARCHAR(20) NOT NULL,
	revisao INTEGER NOT NULL,
	autor_id INTEGER NOT NULL,
	criado_em DATETIME(6) NOT NULL,
	atualizado_em DATETIME(6) NOT NULL,
	simulado_versao_id INTEGER,
	PRIMARY KEY (id),
	CONSTRAINT ck_simulados_estado CHECK (estado IN ('rascunho','publicado','arquivado')),
	CONSTRAINT ck_simulados_revisao CHECK (revisao >= 1),
	CONSTRAINT fk_simulados_autor_id FOREIGN KEY(autor_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_rascunho_itens (
	id INTEGER NOT NULL AUTO_INCREMENT,
	simulado_id INTEGER NOT NULL,
	posicao INTEGER NOT NULL,
	questao_id INTEGER NOT NULL,
	questao_versao_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_rascunho_posicao UNIQUE (simulado_id, posicao),
	CONSTRAINT uq_sim_rascunho_questao UNIQUE (simulado_id, questao_id),
	CONSTRAINT ck_sim_rascunho_posicao CHECK (posicao BETWEEN 1 AND 180),
	CONSTRAINT fk_simulado_rascunho_itens_simulado_id FOREIGN KEY(simulado_id) REFERENCES simulados (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_rascunho_itens_questao_id FOREIGN KEY(questao_id) REFERENCES questoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_rascunho_itens_questao_versao_id FOREIGN KEY(questao_versao_id) REFERENCES questao_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_versoes (
	id INTEGER NOT NULL AUTO_INCREMENT,
	simulado_id INTEGER NOT NULL,
	numero INTEGER NOT NULL,
	revisao_origem INTEGER NOT NULL,
	titulo VARCHAR(150) NOT NULL,
	autor_id INTEGER NOT NULL,
	criado_em DATETIME(6) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_versao_numero UNIQUE (simulado_id, numero),
	CONSTRAINT uq_sim_versao_revisao UNIQUE (simulado_id, revisao_origem),
	CONSTRAINT ck_sim_versao_numero CHECK (numero >= 1 AND revisao_origem >= 1),
	CONSTRAINT fk_simulado_versoes_simulado_id FOREIGN KEY(simulado_id) REFERENCES simulados (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_versoes_autor_id FOREIGN KEY(autor_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_versao_itens (
	id INTEGER NOT NULL AUTO_INCREMENT,
	simulado_versao_id INTEGER NOT NULL,
	posicao INTEGER NOT NULL,
	questao_id INTEGER NOT NULL,
	questao_versao_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_item_posicao UNIQUE (simulado_versao_id, posicao),
	CONSTRAINT uq_sim_item_questao UNIQUE (simulado_versao_id, questao_id),
	CONSTRAINT ck_sim_item_posicao CHECK (posicao BETWEEN 1 AND 180),
	CONSTRAINT fk_simulado_versao_itens_simulado_versao_id FOREIGN KEY(simulado_versao_id) REFERENCES simulado_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_versao_itens_questao_id FOREIGN KEY(questao_id) REFERENCES questoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_versao_itens_questao_versao_id FOREIGN KEY(questao_versao_id) REFERENCES questao_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_eventos (
	id BIGINT NOT NULL AUTO_INCREMENT,
	simulado_id INTEGER NOT NULL,
	versao_id INTEGER,
	ator_id INTEGER NOT NULL,
	acao VARCHAR(30) NOT NULL,
	motivo VARCHAR(500) NOT NULL,
	criado_em DATETIME(6) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT fk_simulado_eventos_simulado_id FOREIGN KEY(simulado_id) REFERENCES simulados (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_eventos_versao_id FOREIGN KEY(versao_id) REFERENCES simulado_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_eventos_ator_id FOREIGN KEY(ator_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE TABLE simulado_tentativas (
	id BIGINT NOT NULL AUTO_INCREMENT,
	usuario_id INTEGER NOT NULL,
	simulado_versao_id INTEGER NOT NULL,
	estado VARCHAR(20) NOT NULL,
	revisao INTEGER NOT NULL,
	chave_envio CHAR(36) COLLATE ascii_bin NOT NULL,
	iniciada_em DATETIME(6) NOT NULL,
	finalizada_em DATETIME(6),
	total INTEGER,
	respondidas INTEGER,
	acertos INTEGER,
	erros INTEGER,
	em_branco INTEGER,
	percentual_acerto NUMERIC(5, 2),
	em_andamento_marcador INTEGER GENERATED ALWAYS AS (CASE WHEN estado = 'em_andamento' THEN 1 ELSE NULL END) STORED,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_tentativa_chave UNIQUE (usuario_id, chave_envio),
	CONSTRAINT uq_sim_tentativa_andamento UNIQUE (usuario_id, simulado_versao_id, em_andamento_marcador),
	CONSTRAINT ck_sim_tentativa_revisao CHECK (revisao >= 1),
	CONSTRAINT ck_sim_tentativa_estado CHECK ((estado = 'em_andamento' AND finalizada_em IS NULL AND total IS NULL AND respondidas IS NULL AND acertos IS NULL AND erros IS NULL AND em_branco IS NULL AND percentual_acerto IS NULL) OR (estado = 'finalizada' AND finalizada_em IS NOT NULL AND finalizada_em >= iniciada_em AND total IS NOT NULL AND total BETWEEN 1 AND 180 AND respondidas IS NOT NULL AND acertos IS NOT NULL AND erros IS NOT NULL AND em_branco IS NOT NULL AND percentual_acerto IS NOT NULL AND acertos >= 0 AND erros >= 0 AND em_branco >= 0 AND total = acertos + erros + em_branco AND respondidas = acertos + erros AND percentual_acerto = ROUND(100 * acertos / total, 2))),
	CONSTRAINT fk_simulado_tentativas_usuario_id FOREIGN KEY(usuario_id) REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_tentativas_simulado_versao_id FOREIGN KEY(simulado_versao_id) REFERENCES simulado_versoes (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

CREATE INDEX ix_sim_tentativa_historico ON simulado_tentativas (usuario_id, finalizada_em, id);

CREATE TABLE simulado_respostas (
	id BIGINT NOT NULL AUTO_INCREMENT,
	tentativa_id BIGINT NOT NULL,
	item_id INTEGER NOT NULL,
	alternativa CHAR(1) COLLATE ascii_bin,
	correta BOOL,
	PRIMARY KEY (id),
	CONSTRAINT uq_sim_resposta_item UNIQUE (tentativa_id, item_id),
	CONSTRAINT ck_sim_resposta_alternativa CHECK (alternativa IS NULL OR alternativa IN ('A','B','C','D','E')),
	CONSTRAINT ck_sim_resposta_correta CHECK (correta IS NULL OR correta IN (0,1)),
	CONSTRAINT fk_simulado_respostas_tentativa_id FOREIGN KEY(tentativa_id) REFERENCES simulado_tentativas (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
	CONSTRAINT fk_simulado_respostas_item_id FOREIGN KEY(item_id) REFERENCES simulado_versao_itens (id) ON DELETE RESTRICT ON UPDATE RESTRICT
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_unicode_ci;

ALTER TABLE simulados ADD CONSTRAINT fk_simulados_simulado_versao_id FOREIGN KEY (simulado_versao_id) REFERENCES simulado_versoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT;
