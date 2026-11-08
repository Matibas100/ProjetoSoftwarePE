DELIMITER $$
-- Pré-condição: prefixo 014 íntegro; somente definições, sem DML funcional.
-- CREATE ROUTINE no instalador; EXECUTE e privilégios das tabelas no invocador.
-- Sem downgrade automático: restaurar/compensar somente as seis routines após
-- retornar o código à versão anterior. Preservar dados e histórico/checksums.
CREATE PROCEDURE sp_plano_atual(IN p_usuario_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.geracao AS geracao,
        p.atual AS atual,
        p.usuario_atual AS usuario_atual,
        p.periodo AS periodo,
        p.gerado_em AS gerado_em,
        p.chave_envio AS chave_envio,
        p.operacao AS operacao,
        p.plano_anterior_id AS plano_anterior_id FROM planos_estudo p WHERE p.usuario_id=p_usuario_id AND p.atual=1 FOR UPDATE;
    ELSE
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.geracao AS geracao,
        p.atual AS atual,
        p.usuario_atual AS usuario_atual,
        p.periodo AS periodo,
        p.gerado_em AS gerado_em,
        p.chave_envio AS chave_envio,
        p.operacao AS operacao,
        p.plano_anterior_id AS plano_anterior_id FROM planos_estudo p WHERE p.usuario_id=p_usuario_id AND p.atual=1;
    END IF;
END$$

CREATE PROCEDURE sp_plano_por_chave(IN p_usuario_id BIGINT UNSIGNED, IN p_chave CHAR(36) CHARACTER SET ascii COLLATE ascii_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_chave IS NULL OR CHAR_LENGTH(p_chave)<>36 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Chave inválida'; END IF;
    SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.geracao AS geracao,
        p.atual AS atual,
        p.usuario_atual AS usuario_atual,
        p.periodo AS periodo,
        p.gerado_em AS gerado_em,
        p.chave_envio AS chave_envio,
        p.operacao AS operacao,
        p.plano_anterior_id AS plano_anterior_id FROM planos_estudo p WHERE p.usuario_id=p_usuario_id AND p.chave_envio=p_chave FOR UPDATE;
END$$

CREATE PROCEDURE sp_plano_itens(IN p_plano_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_plano_id IS NULL OR p_plano_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT i.id AS id,
        i.plano_id AS plano_id,
        i.assunto_id AS assunto_id,
        i.materia_id AS materia_id,
        i.posicao AS posicao,
        i.snapshot AS snapshot,
        i.estado AS estado,
        i.concluido_em AS concluido_em FROM plano_estudo_itens i WHERE i.plano_id=p_plano_id ORDER BY i.posicao FOR UPDATE;
END$$

CREATE PROCEDURE sp_plano_item_proprio(IN p_usuario_id BIGINT UNSIGNED, IN p_item_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_item_id IS NULL OR p_item_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT i.id AS i_id,
        i.plano_id AS i_plano_id,
        i.assunto_id AS i_assunto_id,
        i.materia_id AS i_materia_id,
        i.posicao AS i_posicao,
        i.snapshot AS i_snapshot,
        i.estado AS i_estado,
        i.concluido_em AS i_concluido_em,
        p.id AS p_id,
        p.usuario_id AS p_usuario_id,
        p.geracao AS p_geracao,
        p.atual AS p_atual,
        p.usuario_atual AS p_usuario_atual,
        p.periodo AS p_periodo,
        p.gerado_em AS p_gerado_em,
        p.chave_envio AS p_chave_envio,
        p.operacao AS p_operacao,
        p.plano_anterior_id AS p_plano_anterior_id
    FROM plano_estudo_itens i JOIN planos_estudo p ON p.id=i.plano_id
    WHERE p.usuario_id=p_usuario_id AND i.id=p_item_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_pares_elegiveis_plano(IN p_assunto_ids JSON, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_assunto_ids IS NULL OR JSON_TYPE(p_assunto_ids)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista inválida';
    END IF;
    IF EXISTS(SELECT 1 FROM JSON_TABLE(p_assunto_ids, '$[*]' COLUMNS(valor JSON PATH '$')) ids
        WHERE ids.valor IS NULL OR JSON_TYPE(ids.valor)<>'INTEGER' OR CAST(ids.valor AS DECIMAL(20,0))<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido';
    END IF;
    IF p_bloquear=1 THEN
        SELECT v.assunto_id AS assunto_id, v.materia_id AS materia_id FROM questao_versoes v
        JOIN questoes q ON q.id=v.questao_id
        JOIN assuntos a ON a.id=v.assunto_id
        JOIN materias m ON m.id=v.materia_id
        WHERE v.assunto_id IN (SELECT ids.id FROM JSON_TABLE(p_assunto_ids, '$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$')) ids)
          AND v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id
          AND a.status='ativa' AND m.status='ativa' AND a.materia_id=m.id FOR SHARE;
    ELSE
        SELECT v.assunto_id AS assunto_id, v.materia_id AS materia_id FROM questao_versoes v
        JOIN questoes q ON q.id=v.questao_id
        JOIN assuntos a ON a.id=v.assunto_id
        JOIN materias m ON m.id=v.materia_id
        WHERE v.assunto_id IN (SELECT ids.id FROM JSON_TABLE(p_assunto_ids, '$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$')) ids)
          AND v.estado='publicada' AND q.status<>'arquivada' AND q.versao_publicada_id=v.id
          AND a.status='ativa' AND m.status='ativa' AND a.materia_id=m.id;
    END IF;
END$$

CREATE PROCEDURE sp_eliminar_planos_proprios(IN p_usuario_id BIGINT UNSIGNED)
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_fim BOOLEAN DEFAULT FALSE;
    DECLARE v_plano_id BIGINT UNSIGNED;
    DECLARE v_planos BIGINT UNSIGNED DEFAULT 0;
    DECLARE v_itens BIGINT UNSIGNED DEFAULT 0;
    DECLARE planos CURSOR FOR SELECT id FROM planos_estudo
        WHERE usuario_id=p_usuario_id ORDER BY id DESC FOR UPDATE;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fim=TRUE;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    -- O participante já possui o lock de identidade; a decisão controla a transação.
    OPEN planos;
    eliminar: LOOP
        FETCH planos INTO v_plano_id;
        IF v_fim THEN LEAVE eliminar; END IF;
        DELETE i FROM plano_estudo_itens i JOIN planos_estudo p ON p.id=i.plano_id
            WHERE i.plano_id=v_plano_id AND p.usuario_id=p_usuario_id;
        SET v_itens=v_itens+ROW_COUNT();
        DELETE FROM planos_estudo WHERE id=v_plano_id AND usuario_id=p_usuario_id;
        SET v_planos=v_planos+ROW_COUNT();
    END LOOP;
    CLOSE planos;
    SELECT v_planos AS planos_eliminados, v_itens AS itens_eliminados;
END$$

DELIMITER ;
