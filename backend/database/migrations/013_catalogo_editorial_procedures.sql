DELIMITER $$
-- Pré-condição: prefixo 012 íntegro. CREATE ROUTINE e SELECT necessários.
-- Preservação: somente definições; sem DML, tabelas, FKs, índices ou backfill.
-- As leituras bloqueantes participam da transação externa, sem encerrá-la.
-- Compensação: retornar ao código anterior e restaurar backup ou remover as
-- quinze routines por migration revisada. Preservar dados e histórico/checksums.
-- Não há rollback DDL transacional nem instalação automática no startup.

CREATE PROCEDURE sp_areas_enem_ordenadas()
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    SELECT a.id AS id,
        a.codigo AS codigo,
        a.nome AS nome,
        a.ordem AS ordem FROM areas_enem a ORDER BY a.ordem,a.id;
END$$

CREATE PROCEDURE sp_materias_ativas()
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    SELECT m.id AS id,
        m.nome AS nome,
        m.descricao AS descricao,
        m.area_enem_id AS area_enem_id,
        m.status AS status,
        m.criado_em AS criado_em,
        m.atualizado_em AS atualizado_em FROM materias m WHERE m.status='ativa' ORDER BY m.nome,m.id;
END$$

CREATE PROCEDURE sp_assuntos_ativos(IN p_materia_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF (p_materia_id IS NOT NULL AND p_materia_id<1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT s.id AS id,
        s.nome AS nome,
        s.nome_normalizado AS nome_normalizado,
        s.descricao AS descricao,
        s.materia_id AS materia_id,
        s.status AS status,
        s.criado_em AS criado_em,
        s.atualizado_em AS atualizado_em
    FROM assuntos s JOIN materias m ON m.id=s.materia_id
    WHERE s.status='ativa' AND m.status='ativa' AND (p_materia_id IS NULL OR s.materia_id=p_materia_id)
    ORDER BY s.nome_normalizado,s.id;
END$$

CREATE PROCEDURE sp_impacto_materia(IN p_materia_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_materia_id IS NULL OR p_materia_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT (SELECT COUNT(*) FROM assuntos WHERE materia_id=p_materia_id) AS assuntos,
        (SELECT COUNT(*) FROM questoes q JOIN assuntos s ON s.id=q.assunto_id WHERE s.materia_id=p_materia_id) AS questoes,
        (SELECT COUNT(*) FROM assunto_transferencias WHERE materia_origem_id=p_materia_id OR materia_destino_id=p_materia_id) AS transferencias;
END$$

CREATE PROCEDURE sp_impacto_assunto(IN p_assunto_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_assunto_id IS NULL OR p_assunto_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT (SELECT COUNT(*) FROM questoes WHERE assunto_id=p_assunto_id) AS questoes,
        (SELECT COUNT(*) FROM assunto_transferencias WHERE assunto_id=p_assunto_id) AS transferencias;
END$$

CREATE PROCEDURE sp_assuntos_nao_arquivados(IN p_materia_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_materia_id IS NULL OR p_materia_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT COUNT(*) AS total FROM assuntos WHERE materia_id=p_materia_id AND status<>'arquivada';
END$$

CREATE PROCEDURE sp_bloquear_assunto(IN p_assunto_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_assunto_id IS NULL OR p_assunto_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT s.id AS id,
        s.nome AS nome,
        s.nome_normalizado AS nome_normalizado,
        s.descricao AS descricao,
        s.materia_id AS materia_id,
        s.status AS status,
        s.criado_em AS criado_em,
        s.atualizado_em AS atualizado_em FROM assuntos s WHERE s.id=p_assunto_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_bloquear_materias(IN p_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_ids_json IS NULL OR JSON_TYPE(p_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT m.id AS id,
        m.nome AS nome,
        m.descricao AS descricao,
        m.area_enem_id AS area_enem_id,
        m.status AS status,
        m.criado_em AS criado_em,
        m.atualizado_em AS atualizado_em FROM materias m WHERE m.id IN (SELECT DISTINCT id FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids) ORDER BY m.id FOR UPDATE;
END$$

CREATE PROCEDURE sp_assunto_equivalente(IN p_materia_id BIGINT UNSIGNED, IN p_nome_normalizado VARCHAR(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci, IN p_ignorar_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_materia_id IS NULL OR p_materia_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF (p_ignorar_id IS NOT NULL AND p_ignorar_id<1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_nome_normalizado IS NULL OR p_nome_normalizado='' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Nome normalizado obrigatório';
    END IF;
    SELECT EXISTS(SELECT 1 FROM assuntos s WHERE s.materia_id=p_materia_id
        AND s.nome_normalizado=p_nome_normalizado AND (p_ignorar_id IS NULL OR s.id<>p_ignorar_id)) AS existe;
END$$

CREATE PROCEDURE sp_bloquear_questao(IN p_questao_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_questao_id IS NULL OR p_questao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT q.id AS id,
        q.status AS status,
        q.revisao AS revisao,
        q.criado_em AS criado_em,
        q.atualizado_em AS atualizado_em,
        q.versao_publicada_id AS versao_publicada_id,
        q.enunciado AS enunciado,
        q.alternativa_a AS alternativa_a,
        q.alternativa_b AS alternativa_b,
        q.alternativa_c AS alternativa_c,
        q.alternativa_d AS alternativa_d,
        q.alternativa_e AS alternativa_e,
        q.resposta_correta AS resposta_correta,
        q.explicacao AS explicacao,
        q.dificuldade AS dificuldade,
        q.assunto_id AS assunto_id FROM questoes q WHERE q.id=p_questao_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_versoes_questao(IN p_questao_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_questao_id IS NULL OR p_questao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v WHERE v.questao_id=p_questao_id ORDER BY v.numero;
END$$

CREATE PROCEDURE sp_questao_versao_elegivel(IN p_versao_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_versao_id IS NULL OR p_versao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Flag de lock inválida';
    END IF;
    IF p_bloquear=1 THEN
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND v.id=p_versao_id FOR UPDATE;
    ELSE
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND v.id=p_versao_id;
    END IF;
END$$

CREATE PROCEDURE sp_questoes_elegiveis(IN p_assunto_id BIGINT UNSIGNED, IN p_materia_id BIGINT UNSIGNED, IN p_pagina BIGINT UNSIGNED, IN p_limite INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_deslocamento BIGINT UNSIGNED;
    IF (p_assunto_id IS NOT NULL AND p_assunto_id<1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF (p_materia_id IS NOT NULL AND p_materia_id<1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_pagina IS NULL OR p_pagina<1 OR p_limite IS NULL OR p_limite<1 OR p_limite>100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Paginação inválida';
    END IF;
    SET v_deslocamento=(p_pagina-1)*p_limite;
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND (p_assunto_id IS NULL OR v.assunto_id=p_assunto_id) AND (p_materia_id IS NULL OR v.materia_id=p_materia_id) ORDER BY v.questao_id LIMIT p_limite OFFSET v_deslocamento;
    SELECT COUNT(*) AS total FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND (p_assunto_id IS NULL OR v.assunto_id=p_assunto_id) AND (p_materia_id IS NULL OR v.materia_id=p_materia_id);
END$$

CREATE PROCEDURE sp_questoes_versoes_elegiveis(IN p_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_ids_json IS NULL OR JSON_TYPE(p_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v JOIN questoes q ON q.id=v.questao_id
    JOIN assuntos s ON s.id=v.assunto_id JOIN materias m ON m.id=v.materia_id WHERE v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id AND s.status='ativa' AND m.status='ativa' AND v.id IN (SELECT DISTINCT id FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids);
END$$

CREATE PROCEDURE sp_questoes_versoes_historicas(IN p_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_ids_json IS NULL OR JSON_TYPE(p_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT v.id AS id,
        v.questao_id AS questao_id,
        v.numero AS numero,
        v.revisao_origem AS revisao_origem,
        v.estado AS estado,
        v.enunciado AS enunciado,
        v.alternativa_a AS alternativa_a,
        v.alternativa_b AS alternativa_b,
        v.alternativa_c AS alternativa_c,
        v.alternativa_d AS alternativa_d,
        v.alternativa_e AS alternativa_e,
        v.resposta_correta AS resposta_correta,
        v.explicacao AS explicacao,
        v.dificuldade AS dificuldade,
        v.assunto_id AS assunto_id,
        v.assunto_nome AS assunto_nome,
        v.materia_id AS materia_id,
        v.materia_nome AS materia_nome,
        v.area_enem_id AS area_enem_id,
        v.area_enem_nome AS area_enem_nome,
        v.ator_id AS ator_id,
        v.origem AS origem,
        v.criado_em AS criado_em FROM questao_versoes v
    JOIN vw_conteudo_classificacao_historica c ON c.questao_versao_id=v.id
    WHERE v.id IN (SELECT DISTINCT id FROM JSON_TABLE(p_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids);
END$$

DELIMITER ;
