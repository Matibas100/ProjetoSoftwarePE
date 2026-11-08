DELIMITER $$
-- Pré-condição: prefixo 015 íntegro. Instalação somente de definições.
-- Instalador: CREATE ROUTINE; invocador: EXECUTE e privilégios das tabelas.
-- Sem transação própria, DML de instalação ou mudança de retenção.
-- Reversão: código anterior e restauração/compensação revisada das onze routines;
-- preservar tabelas, dados, evidências, recursos anteriores e histórico/checksums.
CREATE PROCEDURE sp_usuario_por_email(IN p_email VARCHAR(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_email IS NULL OR CHAR_LENGTH(p_email)<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='E-mail inválido'; END IF;
    SELECT u.id, u.nome, u.email, u.senha_hash, u.perfil, u.ativo, u.criado_em
    FROM usuarios u WHERE u.email=p_email;
END$$

CREATE PROCEDURE sp_consultar_sessao(IN p_identificador_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_identificador_hash IS NULL OR CHAR_LENGTH(p_identificador_hash)<>64 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Hash inválido'; END IF;
    SELECT s.id AS s_id, s.usuario_id AS s_usuario_id, s.identificador_hash AS s_identificador_hash,
        s.criada_em AS s_criada_em, s.ultimo_acesso_em AS s_ultimo_acesso_em,
        s.expira_em AS s_expira_em, s.reautenticada_em AS s_reautenticada_em, s.revogada_em AS s_revogada_em,
        u.id AS u_id, u.nome AS u_nome, u.email AS u_email, u.senha_hash AS u_senha_hash,
        u.perfil AS u_perfil, u.ativo AS u_ativo, u.criado_em AS u_criado_em
    FROM sessoes s LEFT JOIN usuarios u ON u.id=s.usuario_id
    WHERE s.identificador_hash=p_identificador_hash;
END$$

CREATE PROCEDURE sp_renovar_acesso_sessao(IN p_sessao_id BIGINT UNSIGNED, IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_id BIGINT UNSIGNED DEFAULT NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_id=NULL;
    IF p_sessao_id IS NULL OR p_sessao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    SELECT id INTO v_id FROM sessoes WHERE id=p_sessao_id AND revogada_em IS NULL
        AND expira_em>p_agora AND ultimo_acesso_em>p_agora-INTERVAL 30 MINUTE FOR UPDATE;
    IF v_id IS NOT NULL THEN
        UPDATE sessoes SET ultimo_acesso_em=p_agora WHERE id=v_id;
    END IF;
    SELECT (v_id IS NOT NULL) AS correspondencias;
END$$

CREATE PROCEDURE sp_revogar_sessao(IN p_sessao_id BIGINT UNSIGNED, IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_afetadas BIGINT UNSIGNED;
    IF p_sessao_id IS NULL OR p_sessao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    UPDATE sessoes SET revogada_em=p_agora WHERE id=p_sessao_id AND revogada_em IS NULL;
    SET v_afetadas=ROW_COUNT();
    SELECT v_afetadas AS afetadas;
END$$

CREATE PROCEDURE sp_revogar_sessoes_usuario(IN p_usuario_id BIGINT UNSIGNED, IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_afetadas BIGINT UNSIGNED;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    UPDATE sessoes SET revogada_em=p_agora WHERE usuario_id=p_usuario_id AND revogada_em IS NULL;
    SET v_afetadas=ROW_COUNT();
    SELECT v_afetadas AS afetadas;
END$$

CREATE PROCEDURE sp_usuario_ativo_bloqueado(IN p_usuario_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT u.id, u.nome, u.email, u.senha_hash, u.perfil, u.ativo, u.criado_em
    FROM usuarios u WHERE u.id=p_usuario_id AND u.ativo=1 FOR UPDATE;
END$$

CREATE PROCEDURE sp_preparar_limite_autenticacao(IN p_chave_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin, IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_chave_hash IS NULL OR CHAR_LENGTH(p_chave_hash)<>64 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Hash inválido'; END IF;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    INSERT INTO auth_limites(chave_hash,falhas,janela_inicio) VALUES(p_chave_hash,0,p_agora)
        ON DUPLICATE KEY UPDATE chave_hash=p_chave_hash;
    SELECT chave_hash, falhas, janela_inicio, bloqueado_ate FROM auth_limites
        WHERE chave_hash=p_chave_hash FOR UPDATE;
END$$

CREATE PROCEDURE sp_limpar_autenticacao(IN p_agora DATETIME(6))
MODIFIES SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_corte DATETIME(6);
    DECLARE v_sessoes BIGINT UNSIGNED;
    DECLARE v_limites BIGINT UNSIGNED;
    IF p_agora IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Instante inválido'; END IF;
    SET v_corte=p_agora-INTERVAL 24 HOUR;
    DELETE FROM sessoes WHERE expira_em<v_corte OR revogada_em<v_corte
        OR (usuario_id IS NOT NULL AND ultimo_acesso_em<v_corte-INTERVAL 30 MINUTE);
    SET v_sessoes=ROW_COUNT();
    DELETE FROM auth_limites WHERE janela_inicio<v_corte-INTERVAL 15 MINUTE
        AND (bloqueado_ate IS NULL OR bloqueado_ate<v_corte);
    SET v_limites=ROW_COUNT();
    SELECT v_sessoes AS sessoes, v_limites AS limites;
END$$

CREATE PROCEDURE sp_bloquear_identidade_privacidade(IN p_usuario_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT id FROM usuarios WHERE id=p_usuario_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_ultimas_decisoes_privacidade(IN p_usuario_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_uso_id BIGINT DEFAULT NULL;
    DECLARE v_uso_usuario_id INT;
    DECLARE v_uso_tipo VARCHAR(8);
    DECLARE v_uso_acao VARCHAR(8);
    DECLARE v_uso_versao VARCHAR(20);
    DECLARE v_uso_documento_sha256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin;
    DECLARE v_uso_registrado_em DATETIME(6);
    DECLARE v_uso_chave_envio CHAR(36) CHARACTER SET ascii COLLATE ascii_bin;
    DECLARE v_uso_revisao_base BIGINT;
    DECLARE v_plano_id BIGINT DEFAULT NULL;
    DECLARE v_plano_usuario_id INT;
    DECLARE v_plano_tipo VARCHAR(8);
    DECLARE v_plano_acao VARCHAR(8);
    DECLARE v_plano_versao VARCHAR(20);
    DECLARE v_plano_documento_sha256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin;
    DECLARE v_plano_registrado_em DATETIME(6);
    DECLARE v_plano_chave_envio CHAR(36) CHARACTER SET ascii COLLATE ascii_bin;
    DECLARE v_plano_revisao_base BIGINT;
    DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    -- Duas leituras correntes, nesta ordem; a projeção final não relê tabelas.
    SELECT id,usuario_id,tipo,acao,versao,documento_sha256,registrado_em,chave_envio,revisao_base
        INTO v_uso_id,v_uso_usuario_id,v_uso_tipo,v_uso_acao,v_uso_versao,v_uso_documento_sha256,
             v_uso_registrado_em,v_uso_chave_envio,v_uso_revisao_base
        FROM registros_privacidade WHERE usuario_id=p_usuario_id AND tipo='uso'
        ORDER BY id DESC LIMIT 1 FOR UPDATE;
    SELECT id,usuario_id,tipo,acao,versao,documento_sha256,registrado_em,chave_envio,revisao_base
        INTO v_plano_id,v_plano_usuario_id,v_plano_tipo,v_plano_acao,v_plano_versao,v_plano_documento_sha256,
             v_plano_registrado_em,v_plano_chave_envio,v_plano_revisao_base
        FROM registros_privacidade WHERE usuario_id=p_usuario_id AND tipo='plano'
        ORDER BY id DESC LIMIT 1 FOR UPDATE;
    SELECT decisoes.id, decisoes.usuario_id, decisoes.tipo, decisoes.acao, decisoes.versao,
        decisoes.documento_sha256, decisoes.registrado_em, decisoes.chave_envio, decisoes.revisao_base
    FROM (
        SELECT v_uso_id AS id, v_uso_usuario_id AS usuario_id, v_uso_tipo AS tipo,
            v_uso_acao AS acao, v_uso_versao AS versao, v_uso_documento_sha256 AS documento_sha256,
            v_uso_registrado_em AS registrado_em, v_uso_chave_envio AS chave_envio, v_uso_revisao_base AS revisao_base
        WHERE v_uso_id IS NOT NULL
        UNION ALL
        SELECT v_plano_id, v_plano_usuario_id, v_plano_tipo, v_plano_acao, v_plano_versao,
            v_plano_documento_sha256, v_plano_registrado_em, v_plano_chave_envio, v_plano_revisao_base
        WHERE v_plano_id IS NOT NULL
    ) decisoes ORDER BY FIELD(decisoes.tipo,'uso','plano');
END$$

CREATE PROCEDURE sp_decisao_privacidade_por_chave(IN p_usuario_id BIGINT UNSIGNED, IN p_chave CHAR(36) CHARACTER SET ascii COLLATE ascii_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_chave IS NULL OR CHAR_LENGTH(p_chave)<>36 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Chave inválida'; END IF;
    SELECT id,usuario_id,tipo,acao,versao,documento_sha256,registrado_em,chave_envio,revisao_base
    FROM registros_privacidade WHERE usuario_id=p_usuario_id AND chave_envio=p_chave FOR UPDATE;
END$$

DELIMITER ;
