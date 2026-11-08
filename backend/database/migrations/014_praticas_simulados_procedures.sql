DELIMITER $$
-- Interfaces especializadas de Práticas e Simulados; transação pertence ao chamador.

CREATE PROCEDURE sp_pratica_por_chave(IN p_usuario_id BIGINT UNSIGNED, IN p_chave CHAR(36) CHARACTER SET ascii COLLATE ascii_bin, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_chave IS NULL OR CHAR_LENGTH(p_chave)<>36 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Chave inválida'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.chave_envio=p_chave FOR UPDATE;
    ELSE
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.chave_envio=p_chave;
    END IF;
END$$

CREATE PROCEDURE sp_pratica_propria(IN p_usuario_id BIGINT UNSIGNED, IN p_tentativa_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_tentativa_id IS NULL OR p_tentativa_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.id=p_tentativa_id FOR UPDATE;
    ELSE
        SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.id=p_tentativa_id;
    END IF;
END$$

CREATE PROCEDURE sp_praticas_historico(IN p_usuario_id BIGINT UNSIGNED, IN p_assunto_id BIGINT UNSIGNED, IN p_pagina BIGINT UNSIGNED, IN p_limite INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_offset BIGINT UNSIGNED;
    IF p_pagina IS NULL OR p_pagina<1 OR p_limite IS NULL OR p_limite<1 OR p_limite>100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Paginação inválida';
    END IF;
    SET v_offset=(p_pagina-1)*p_limite;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_assunto_id IS NOT NULL AND p_assunto_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.estado='respondida' AND (p_assunto_id IS NULL OR p.assunto_id=p_assunto_id) ORDER BY p.respondida_em DESC,p.id DESC LIMIT v_offset,p_limite;
    SELECT COUNT(*) AS total FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.estado='respondida' AND (p_assunto_id IS NULL OR p.assunto_id=p_assunto_id);
END$$

CREATE PROCEDURE sp_praticas_fatos(IN p_usuario_id BIGINT UNSIGNED, IN p_inicio DATETIME(6), IN p_fim DATETIME(6))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_inicio IS NULL OR p_fim IS NULL OR p_inicio>=p_fim THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Intervalo inválido'; END IF;
    SELECT p.id AS id,
        p.usuario_id AS usuario_id,
        p.questao_versao_id AS questao_versao_id,
        p.chave_envio AS chave_envio,
        p.estado AS estado,
        p.resposta_escolhida AS resposta_escolhida,
        p.correta AS correta,
        p.iniciada_em AS iniciada_em,
        p.respondida_em AS respondida_em,
        p.assunto_id AS assunto_id,
        p.assunto_nome AS assunto_nome,
        p.materia_id AS materia_id,
        p.materia_nome AS materia_nome FROM pratica_tentativas p WHERE p.usuario_id=p_usuario_id AND p.estado='respondida' AND p.respondida_em>=p_inicio AND p.respondida_em<p_fim ORDER BY p.respondida_em,p.id;
END$$

CREATE PROCEDURE sp_bloquear_simulado(IN p_simulado_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_simulado_id IS NULL OR p_simulado_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT s.id AS id,
        s.titulo AS titulo,
        s.estado AS estado,
        s.revisao AS revisao,
        s.autor_id AS autor_id,
        s.criado_em AS criado_em,
        s.atualizado_em AS atualizado_em,
        s.simulado_versao_id AS simulado_versao_id FROM simulados s WHERE s.id=p_simulado_id FOR UPDATE;
END$$

CREATE PROCEDURE sp_simulado_itens(IN p_simulado_id BIGINT UNSIGNED, IN p_versao_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_versao_id IS NULL THEN
        SELECT i.id AS id,
        i.simulado_id AS simulado_id,
        i.posicao AS posicao,
        i.questao_id AS questao_id,
        i.questao_versao_id AS questao_versao_id FROM simulado_rascunho_itens i WHERE i.simulado_id=p_simulado_id ORDER BY i.posicao;
    ELSE
        SELECT i.id AS id,
        i.simulado_versao_id AS simulado_versao_id,
        i.posicao AS posicao,
        i.questao_id AS questao_id,
        i.questao_versao_id AS questao_versao_id FROM simulado_versao_itens i WHERE i.simulado_versao_id=p_versao_id ORDER BY i.posicao;
    END IF;
END$$

CREATE PROCEDURE sp_simulados_itens_lote(IN p_simulado_ids_json JSON, IN p_versao_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_versao_ids_json IS NULL THEN
        IF p_simulado_ids_json IS NULL OR JSON_TYPE(p_simulado_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_simulado_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
        SELECT i.id AS id,
        i.simulado_id AS simulado_id,
        i.posicao AS posicao,
        i.questao_id AS questao_id,
        i.questao_versao_id AS questao_versao_id FROM simulado_rascunho_itens i WHERE i.simulado_id IN (SELECT DISTINCT id FROM JSON_TABLE(p_simulado_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids) ORDER BY i.simulado_id,i.posicao;
    ELSE
        IF p_versao_ids_json IS NULL OR JSON_TYPE(p_versao_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
        SELECT i.id AS id,
        i.simulado_versao_id AS simulado_versao_id,
        i.posicao AS posicao,
        i.questao_id AS questao_id,
        i.questao_versao_id AS questao_versao_id FROM simulado_versao_itens i WHERE i.simulado_versao_id IN (SELECT DISTINCT id FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids) ORDER BY i.simulado_versao_id,i.posicao;
    END IF;
END$$

CREATE PROCEDURE sp_simulados_andamentos_lote(IN p_usuario_id BIGINT UNSIGNED, IN p_versao_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_versao_ids_json IS NULL OR JSON_TYPE(p_versao_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.simulado_versao_id IN (SELECT DISTINCT id FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids) AND t.estado='em_andamento';
END$$

CREATE PROCEDURE sp_simulados_titulos_lote(IN p_versao_ids_json JSON)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_versao_ids_json IS NULL OR JSON_TYPE(p_versao_ids_json)<>'ARRAY' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lista de IDs inválida';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) j WHERE j.id IS NULL OR j.id<1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID de lote inválido';
    END IF;
    SELECT v.id AS id,v.titulo AS titulo FROM simulado_versoes v WHERE v.id IN (SELECT DISTINCT id FROM JSON_TABLE(p_versao_ids_json,'$[*]' COLUMNS(id BIGINT UNSIGNED PATH '$' ERROR ON EMPTY ERROR ON ERROR)) ids);
END$$

CREATE PROCEDURE sp_simulados_listar(IN p_pagina BIGINT UNSIGNED, IN p_limite INT, IN p_estado VARCHAR(20))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_offset BIGINT UNSIGNED;
    IF p_pagina IS NULL OR p_pagina<1 OR p_limite IS NULL OR p_limite<1 OR p_limite>100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Paginação inválida';
    END IF;
    SET v_offset=(p_pagina-1)*p_limite;
    SELECT s.id AS id,
        s.titulo AS titulo,
        s.estado AS estado,
        s.revisao AS revisao,
        s.autor_id AS autor_id,
        s.criado_em AS criado_em,
        s.atualizado_em AS atualizado_em,
        s.simulado_versao_id AS simulado_versao_id FROM simulados s WHERE (p_estado IS NULL OR s.estado=p_estado) ORDER BY s.id DESC LIMIT v_offset,p_limite;
    SELECT COUNT(*) AS total FROM simulados s WHERE (p_estado IS NULL OR s.estado=p_estado);
END$$

CREATE PROCEDURE sp_simulado_tentativa_propria(IN p_usuario_id BIGINT UNSIGNED, IN p_tentativa_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_tentativa_id IS NULL OR p_tentativa_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.id=p_tentativa_id FOR UPDATE;
    ELSE
        SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.id=p_tentativa_id;
    END IF;
END$$

CREATE PROCEDURE sp_simulado_tentativa_por_chave(IN p_usuario_id BIGINT UNSIGNED, IN p_chave CHAR(36) CHARACTER SET ascii COLLATE ascii_bin)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_chave IS NULL OR CHAR_LENGTH(p_chave)<>36 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Chave inválida'; END IF;
    SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.chave_envio=p_chave FOR UPDATE;
END$$

CREATE PROCEDURE sp_simulado_em_andamento(IN p_usuario_id BIGINT UNSIGNED, IN p_versao_id BIGINT UNSIGNED)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_versao_id IS NULL OR p_versao_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.simulado_versao_id=p_versao_id AND t.estado='em_andamento' FOR UPDATE;
END$$

CREATE PROCEDURE sp_simulado_respostas(IN p_tentativa_id BIGINT UNSIGNED, IN p_bloquear TINYINT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_tentativa_id IS NULL OR p_tentativa_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_bloquear IS NULL OR p_bloquear NOT IN (0,1) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lock inválido'; END IF;
    IF p_bloquear=1 THEN
        SELECT r.id AS r_id,
        r.tentativa_id AS r_tentativa_id,
        r.item_id AS r_item_id,
        r.alternativa AS r_alternativa,
        r.correta AS r_correta,
        i.id AS i_id,
        i.simulado_versao_id AS i_simulado_versao_id,
        i.posicao AS i_posicao,
        i.questao_id AS i_questao_id,
        i.questao_versao_id AS i_questao_versao_id FROM simulado_respostas r JOIN simulado_versao_itens i ON i.id=r.item_id WHERE r.tentativa_id=p_tentativa_id ORDER BY i.posicao FOR UPDATE;
    ELSE
        SELECT r.id AS r_id,
        r.tentativa_id AS r_tentativa_id,
        r.item_id AS r_item_id,
        r.alternativa AS r_alternativa,
        r.correta AS r_correta,
        i.id AS i_id,
        i.simulado_versao_id AS i_simulado_versao_id,
        i.posicao AS i_posicao,
        i.questao_id AS i_questao_id,
        i.questao_versao_id AS i_questao_versao_id FROM simulado_respostas r JOIN simulado_versao_itens i ON i.id=r.item_id WHERE r.tentativa_id=p_tentativa_id ORDER BY i.posicao;
    END IF;
END$$

CREATE PROCEDURE sp_simulados_historico(IN p_usuario_id BIGINT UNSIGNED, IN p_pagina BIGINT UNSIGNED, IN p_limite INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_offset BIGINT UNSIGNED;
    IF p_pagina IS NULL OR p_pagina<1 OR p_limite IS NULL OR p_limite<1 OR p_limite>100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Paginação inválida';
    END IF;
    SET v_offset=(p_pagina-1)*p_limite;
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    SELECT t.id AS id,
        t.usuario_id AS usuario_id,
        t.simulado_versao_id AS simulado_versao_id,
        t.estado AS estado,
        t.revisao AS revisao,
        t.chave_envio AS chave_envio,
        t.iniciada_em AS iniciada_em,
        t.finalizada_em AS finalizada_em,
        t.total AS total,
        t.respondidas AS respondidas,
        t.acertos AS acertos,
        t.erros AS erros,
        t.em_branco AS em_branco,
        t.percentual_acerto AS percentual_acerto,
        t.em_andamento_marcador AS em_andamento_marcador FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.estado='finalizada' ORDER BY t.finalizada_em DESC,t.id DESC LIMIT v_offset,p_limite;
    SELECT COUNT(*) AS total FROM simulado_tentativas t WHERE t.usuario_id=p_usuario_id AND t.estado='finalizada';
END$$

CREATE PROCEDURE sp_simulados_fatos(IN p_usuario_id BIGINT UNSIGNED, IN p_inicio DATETIME(6), IN p_fim DATETIME(6))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id<1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='ID inválido'; END IF;
    IF p_inicio IS NULL OR p_fim IS NULL OR p_inicio>=p_fim THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Intervalo inválido'; END IF;
    SELECT r.id AS r_id,
        r.tentativa_id AS r_tentativa_id,
        r.item_id AS r_item_id,
        r.alternativa AS r_alternativa,
        r.correta AS r_correta,
        i.id AS i_id,
        i.simulado_versao_id AS i_simulado_versao_id,
        i.posicao AS i_posicao,
        i.questao_id AS i_questao_id,
        i.questao_versao_id AS i_questao_versao_id,
        t.id AS t_id,
        t.usuario_id AS t_usuario_id,
        t.simulado_versao_id AS t_simulado_versao_id,
        t.estado AS t_estado,
        t.revisao AS t_revisao,
        t.chave_envio AS t_chave_envio,
        t.iniciada_em AS t_iniciada_em,
        t.finalizada_em AS t_finalizada_em,
        t.total AS t_total,
        t.respondidas AS t_respondidas,
        t.acertos AS t_acertos,
        t.erros AS t_erros,
        t.em_branco AS t_em_branco,
        t.percentual_acerto AS t_percentual_acerto,
        t.em_andamento_marcador AS t_em_andamento_marcador FROM simulado_respostas r JOIN simulado_versao_itens i ON i.id=r.item_id JOIN simulado_tentativas t ON t.id=r.tentativa_id WHERE t.usuario_id=p_usuario_id AND t.estado='finalizada' AND r.alternativa IS NOT NULL AND t.finalizada_em>=p_inicio AND t.finalizada_em<p_fim ORDER BY t.finalizada_em,r.id;
END$$

DELIMITER ;
