DELIMITER $$
-- Pré-condição: prefixo 010 íntegro. Privilégios: CREATE ROUTINE e SELECT.
-- Preservação: somente definições; sem DML funcional, tabelas ou backfill.
-- Compensação: voltar ao código anterior e restaurar backup ou remover estas
-- quatro routines por migration revisada, sem apagar histórico/checksums/dados.
-- DDL não tem rollback transacional. Não aplicar automaticamente no startup.

CREATE PROCEDURE sp_materias_admin(
    IN p_busca VARCHAR(100),
    IN p_status VARCHAR(20),
    IN p_area_enem_id BIGINT UNSIGNED,
    IN p_pagina BIGINT UNSIGNED,
    IN p_por_pagina INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_deslocamento BIGINT UNSIGNED;
    IF p_pagina IS NULL OR
       p_pagina < 1 OR
       p_por_pagina IS NULL OR
       p_por_pagina < 1 OR
       p_por_pagina > 100 OR
       (p_area_enem_id IS NOT NULL AND p_area_enem_id < 1) OR
       (p_status IS NOT NULL AND p_status NOT IN ('ativa','inativa','arquivada')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Parâmetros de consulta inválidos';
    END IF;
    SET v_deslocamento=(p_pagina-1)*p_por_pagina;
    SELECT m.id AS m_id,
        m.nome AS m_nome,
        m.descricao AS m_descricao,
        m.area_enem_id AS m_area_enem_id,
        m.status AS m_status,
        m.criado_em AS m_criado_em,
        m.atualizado_em AS m_atualizado_em,
        a.id AS a_id,
        a.codigo AS a_codigo,
        a.nome AS a_nome,
        a.ordem AS a_ordem,
        COUNT(DISTINCT s.id) AS assuntos, COUNT(DISTINCT q.id) AS questoes
    FROM materias m JOIN areas_enem a ON a.id=m.area_enem_id LEFT JOIN assuntos s ON s.materia_id=m.id LEFT JOIN questoes q ON q.assunto_id=s.id
    WHERE (p_busca IS NULL OR p_busca='' OR m.nome LIKE CONCAT('%',p_busca,'%') OR m.descricao LIKE CONCAT('%',p_busca,'%')) AND
        (p_status IS NULL OR m.status = p_status) AND
        (p_area_enem_id IS NULL OR m.area_enem_id = p_area_enem_id)
    GROUP BY m.id,a.id
    ORDER BY m.nome, m.id
    LIMIT p_por_pagina OFFSET v_deslocamento;
    SELECT COUNT(*) AS total FROM materias m JOIN areas_enem a ON a.id=m.area_enem_id
    WHERE (p_busca IS NULL OR p_busca='' OR m.nome LIKE CONCAT('%',p_busca,'%') OR m.descricao LIKE CONCAT('%',p_busca,'%')) AND
        (p_status IS NULL OR m.status = p_status) AND
        (p_area_enem_id IS NULL OR m.area_enem_id = p_area_enem_id);
END$$

CREATE PROCEDURE sp_assuntos_admin(
    IN p_busca VARCHAR(100),
    IN p_status VARCHAR(20),
    IN p_area_enem_id BIGINT UNSIGNED,
    IN p_materia_id BIGINT UNSIGNED,
    IN p_pagina BIGINT UNSIGNED,
    IN p_por_pagina INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_deslocamento BIGINT UNSIGNED;
    IF p_pagina IS NULL OR
       p_pagina < 1 OR
       p_por_pagina IS NULL OR
       p_por_pagina < 1 OR
       p_por_pagina > 100 OR
       (p_area_enem_id IS NOT NULL AND p_area_enem_id < 1) OR
       (p_materia_id IS NOT NULL AND p_materia_id < 1) OR
       (p_status IS NOT NULL AND p_status NOT IN ('ativa','inativa','arquivada')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Parâmetros de consulta inválidos';
    END IF;
    SET v_deslocamento=(p_pagina-1)*p_por_pagina;
    SELECT s.id AS s_id,
        s.nome AS s_nome,
        s.nome_normalizado AS s_nome_normalizado,
        s.descricao AS s_descricao,
        s.materia_id AS s_materia_id,
        s.status AS s_status,
        s.criado_em AS s_criado_em,
        s.atualizado_em AS s_atualizado_em,
        m.id AS m_id,
        m.nome AS m_nome,
        m.descricao AS m_descricao,
        m.area_enem_id AS m_area_enem_id,
        m.status AS m_status,
        m.criado_em AS m_criado_em,
        m.atualizado_em AS m_atualizado_em,
        a.id AS a_id,
        a.codigo AS a_codigo,
        a.nome AS a_nome,
        a.ordem AS a_ordem,
        COUNT(q.id) AS questoes
    FROM assuntos s JOIN materias m ON m.id=s.materia_id JOIN areas_enem a ON a.id=m.area_enem_id LEFT JOIN questoes q ON q.assunto_id=s.id
    WHERE (p_busca IS NULL OR p_busca='' OR s.nome LIKE CONCAT('%',p_busca,'%') OR s.descricao LIKE CONCAT('%',p_busca,'%')) AND
        (p_status IS NULL OR s.status = p_status) AND
        (p_area_enem_id IS NULL OR m.area_enem_id = p_area_enem_id) AND
        (p_materia_id IS NULL OR s.materia_id = p_materia_id)
    GROUP BY s.id,m.id,a.id
    ORDER BY s.nome_normalizado, s.id
    LIMIT p_por_pagina OFFSET v_deslocamento;
    SELECT COUNT(*) AS total FROM assuntos s JOIN materias m ON m.id=s.materia_id JOIN areas_enem a ON a.id=m.area_enem_id
    WHERE (p_busca IS NULL OR p_busca='' OR s.nome LIKE CONCAT('%',p_busca,'%') OR s.descricao LIKE CONCAT('%',p_busca,'%')) AND
        (p_status IS NULL OR s.status = p_status) AND
        (p_area_enem_id IS NULL OR m.area_enem_id = p_area_enem_id) AND
        (p_materia_id IS NULL OR s.materia_id = p_materia_id);
END$$

CREATE PROCEDURE sp_questoes_admin(
    IN p_busca VARCHAR(100),
    IN p_status VARCHAR(20),
    IN p_dificuldade VARCHAR(10),
    IN p_area_enem_id BIGINT UNSIGNED,
    IN p_materia_id BIGINT UNSIGNED,
    IN p_assunto_id BIGINT UNSIGNED,
    IN p_pagina BIGINT UNSIGNED,
    IN p_por_pagina INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    DECLARE v_deslocamento BIGINT UNSIGNED;
    IF p_pagina IS NULL OR
       p_pagina < 1 OR
       p_por_pagina IS NULL OR
       p_por_pagina < 1 OR
       p_por_pagina > 100 OR
       (p_area_enem_id IS NOT NULL AND p_area_enem_id < 1) OR
       (p_materia_id IS NOT NULL AND p_materia_id < 1) OR
       (p_assunto_id IS NOT NULL AND p_assunto_id < 1) OR
       (p_status IS NOT NULL AND p_status NOT IN ('rascunho','publicada','arquivada')) OR
       (p_dificuldade IS NOT NULL AND p_dificuldade NOT IN ('facil','media','dificil')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Parâmetros de consulta inválidos';
    END IF;
    SET v_deslocamento=(p_pagina-1)*p_por_pagina;
    SELECT q.id AS q_id,
        q.enunciado AS q_enunciado,
        q.alternativa_a AS q_alternativa_a,
        q.alternativa_b AS q_alternativa_b,
        q.alternativa_c AS q_alternativa_c,
        q.alternativa_d AS q_alternativa_d,
        q.alternativa_e AS q_alternativa_e,
        q.resposta_correta AS q_resposta_correta,
        q.explicacao AS q_explicacao,
        q.dificuldade AS q_dificuldade,
        q.assunto_id AS q_assunto_id,
        q.status AS q_status,
        q.revisao AS q_revisao,
        q.versao_publicada_id AS q_versao_publicada_id,
        s.id AS s_id,
        s.nome AS s_nome,
        s.nome_normalizado AS s_nome_normalizado,
        s.descricao AS s_descricao,
        s.materia_id AS s_materia_id,
        s.status AS s_status,
        s.criado_em AS s_criado_em,
        s.atualizado_em AS s_atualizado_em,
        m.id AS m_id,
        m.nome AS m_nome,
        m.descricao AS m_descricao,
        m.area_enem_id AS m_area_enem_id,
        m.status AS m_status,
        m.criado_em AS m_criado_em,
        m.atualizado_em AS m_atualizado_em,
        a.id AS a_id,
        a.codigo AS a_codigo,
        a.nome AS a_nome,
        a.ordem AS a_ordem
    FROM questoes q JOIN assuntos s ON s.id=q.assunto_id JOIN materias m ON m.id=s.materia_id JOIN areas_enem a ON a.id=m.area_enem_id
    WHERE (p_busca IS NULL OR p_busca='' OR q.enunciado LIKE CONCAT('%',REPLACE(REPLACE(REPLACE(p_busca,'/','//'),'%','/%'),'_','/_'),'%') ESCAPE '/') AND
        (p_status IS NULL OR q.status = p_status) AND
        (p_dificuldade IS NULL OR q.dificuldade = p_dificuldade) AND
        (p_area_enem_id IS NULL OR a.id = p_area_enem_id) AND
        (p_materia_id IS NULL OR m.id = p_materia_id) AND
        (p_assunto_id IS NULL OR q.assunto_id = p_assunto_id)
    ORDER BY q.id DESC
    LIMIT p_por_pagina OFFSET v_deslocamento;
    SELECT COUNT(*) AS total FROM questoes q JOIN assuntos s ON s.id=q.assunto_id JOIN materias m ON m.id=s.materia_id JOIN areas_enem a ON a.id=m.area_enem_id
    WHERE (p_busca IS NULL OR p_busca='' OR q.enunciado LIKE CONCAT('%',REPLACE(REPLACE(REPLACE(p_busca,'/','//'),'%','/%'),'_','/_'),'%') ESCAPE '/') AND
        (p_status IS NULL OR q.status = p_status) AND
        (p_dificuldade IS NULL OR q.dificuldade = p_dificuldade) AND
        (p_area_enem_id IS NULL OR a.id = p_area_enem_id) AND
        (p_materia_id IS NULL OR m.id = p_materia_id) AND
        (p_assunto_id IS NULL OR q.assunto_id = p_assunto_id);
END$$

CREATE PROCEDURE sp_conteudo_contagens_dashboard()
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    SELECT (SELECT COUNT(*) FROM materias WHERE status='ativa') AS materias_ativas,
        (SELECT COUNT(*) FROM assuntos WHERE status='ativa') AS assuntos_ativos,
        (SELECT COUNT(*) FROM questoes WHERE status='rascunho') AS questoes_rascunhos,
        (SELECT COUNT(*) FROM questoes WHERE status='publicada') AS questoes_publicadas,
        (SELECT COUNT(*) FROM questoes WHERE status='arquivada') AS questoes_arquivadas;
END$$
DELIMITER ;
