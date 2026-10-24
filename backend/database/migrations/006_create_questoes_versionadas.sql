ALTER TABLE questoes
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'rascunho',
    ADD COLUMN revisao INT NOT NULL DEFAULT 1,
    ADD COLUMN criado_em DATETIME(6) NULL,
    ADD COLUMN atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    ADD COLUMN versao_publicada_id INT NULL,
    ADD CONSTRAINT ck_questoes_status CHECK (status IN ('rascunho', 'publicada', 'arquivada')),
    ADD CONSTRAINT ck_questoes_revisao CHECK (revisao >= 1),
    ADD INDEX ix_questoes_status (status);

CREATE TABLE questao_versoes (
    id INT NOT NULL AUTO_INCREMENT,
    questao_id INT NOT NULL,
    numero INT NOT NULL,
    revisao_origem INT NOT NULL,
    estado VARCHAR(20) NOT NULL,
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
    assunto_nome VARCHAR(150) NOT NULL,
    materia_id INT NOT NULL,
    materia_nome VARCHAR(100) NOT NULL,
    area_enem_id INT NOT NULL,
    area_enem_nome VARCHAR(100) NOT NULL,
    ator_id INT NULL,
    origem VARCHAR(20) NOT NULL,
    criado_em DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_questao_versoes_numero UNIQUE (questao_id, numero),
    CONSTRAINT ck_questao_versoes_numero CHECK (numero >= 1 AND revisao_origem >= 1),
    CONSTRAINT ck_questao_versoes_estado CHECK (estado IN ('rascunho', 'publicada')),
    CONSTRAINT ck_questao_versoes_origem CHECK (origem IN ('legado', 'manual')),
    CONSTRAINT ck_questao_versoes_resposta CHECK (resposta_correta IN ('A','B','C','D','E')),
    CONSTRAINT ck_questao_versoes_dificuldade CHECK (dificuldade IN ('facil','media','dificil')),
    CONSTRAINT fk_questao_versoes_questao FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_versoes_assunto FOREIGN KEY (assunto_id) REFERENCES assuntos(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_versoes_materia FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_versoes_area FOREIGN KEY (area_enem_id) REFERENCES areas_enem(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_versoes_ator FOREIGN KEY (ator_id) REFERENCES usuarios(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB;

ALTER TABLE questoes ADD CONSTRAINT fk_questoes_versao_publicada
    FOREIGN KEY (versao_publicada_id) REFERENCES questao_versoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE TABLE questao_eventos (
    id BIGINT NOT NULL AUTO_INCREMENT,
    questao_id INT NOT NULL,
    versao_id INT NULL,
    ator_id INT NULL,
    acao VARCHAR(20) NOT NULL,
    motivo VARCHAR(500) NOT NULL,
    criado_em DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    INDEX ix_questao_eventos_questao (questao_id),
    CONSTRAINT ck_questao_eventos_acao CHECK (acao IN ('cadastro','edicao','revisao','aprovacao','publicacao','arquivamento')),
    CONSTRAINT fk_questao_eventos_questao FOREIGN KEY (questao_id) REFERENCES questoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_eventos_versao FOREIGN KEY (versao_id) REFERENCES questao_versoes(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_questao_eventos_ator FOREIGN KEY (ator_id) REFERENCES usuarios(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB;

INSERT INTO questao_versoes (questao_id, numero, revisao_origem, estado,
    enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_e,
    resposta_correta, explicacao, dificuldade, assunto_id, assunto_nome,
    materia_id, materia_nome, area_enem_id, area_enem_nome, ator_id, origem, criado_em)
SELECT q.id, 1, 1, 'rascunho', q.enunciado, q.alternativa_a, q.alternativa_b,
    q.alternativa_c, q.alternativa_d, q.alternativa_e, q.resposta_correta, q.explicacao,
    q.dificuldade, a.id, a.nome, m.id, m.nome, ar.id, ar.nome, NULL, 'legado', UTC_TIMESTAMP(6)
FROM questoes q JOIN assuntos a ON a.id=q.assunto_id
JOIN materias m ON m.id=a.materia_id JOIN areas_enem ar ON ar.id=m.area_enem_id;

INSERT INTO questao_eventos (questao_id, versao_id, ator_id, acao, motivo, criado_em)
SELECT questao_id, id, NULL, 'cadastro', 'Backfill da migration 006; autoria historica desconhecida.', criado_em
FROM questao_versoes WHERE origem='legado';
