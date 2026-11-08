-- Pré-condição: prefixo 011 íntegro. CREATE VIEW/CREATE ROUTINE e SELECT necessários.
-- Preservação: somente definições; sem tabelas, alterações de dados ou backfill.
-- Compensação revisada após retorno ao código anterior: restaurar backup ou
-- remover procedures, views consumidoras e depois views de origem, preservando
-- dados, procedure legada e histórico. DDL não possui rollback transacional.
CREATE SQL SECURITY INVOKER VIEW vw_conteudo_classificacao_historica AS
SELECT id AS questao_versao_id, materia_id, materia_nome, assunto_id, assunto_nome
FROM questao_versoes WHERE estado='publicada';

CREATE SQL SECURITY INVOKER VIEW vw_praticas_fatos_desempenho AS
SELECT 'pratica' AS tipo, id, id AS atividade_id, usuario_id,
    respondida_em AS ocorrido_em, correta, materia_id, materia_nome, assunto_id, assunto_nome
FROM pratica_tentativas WHERE estado='respondida';

CREATE SQL SECURITY INVOKER VIEW vw_simulados_fatos_desempenho AS
SELECT 'simulado' AS tipo, r.id, t.id AS atividade_id, t.usuario_id,
    t.finalizada_em AS ocorrido_em, r.correta,
    q.materia_id, q.materia_nome, q.assunto_id, q.assunto_nome
FROM simulado_respostas r JOIN simulado_tentativas t ON t.id=r.tentativa_id
JOIN simulado_versao_itens i ON i.id=r.item_id
JOIN vw_conteudo_classificacao_historica q ON q.questao_versao_id=i.questao_versao_id
WHERE t.estado='finalizada' AND r.alternativa IS NOT NULL;

CREATE SQL SECURITY INVOKER VIEW vw_simulados_atividades AS
SELECT 'simulado' AS tipo, t.id, t.usuario_id, t.finalizada_em AS ocorrido_em, v.titulo
FROM simulado_tentativas t JOIN simulado_versoes v ON v.id=t.simulado_versao_id
WHERE t.estado='finalizada';

DELIMITER $$
CREATE PROCEDURE sp_desempenho_resumo(
    IN p_usuario_id INT, IN p_inicio DATETIME(6), IN p_fim DATETIME(6))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id < 1 OR p_inicio IS NULL OR p_fim IS NULL OR p_inicio >= p_fim THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Usuário e intervalo inválidos';
    END IF;
    WITH fatos AS (
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_praticas_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
        UNION ALL
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_simulados_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
    )
    SELECT COUNT(*) AS total_respostas,
        COALESCE(SUM(CASE WHEN correta=1 THEN 1 ELSE 0 END),0) AS acertos,
        COALESCE(SUM(CASE WHEN tipo='pratica' THEN 1 ELSE 0 END),0) AS pratica,
        COALESCE(SUM(CASE WHEN tipo='simulado' THEN 1 ELSE 0 END),0) AS simulado FROM fatos;
    WITH fatos AS (
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_praticas_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
        UNION ALL
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_simulados_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
    ), ranking AS (
        SELECT materia_id, materia_nome, assunto_id, assunto_nome,
            COUNT(*) OVER (PARTITION BY materia_id) AS total_respostas,
            SUM(CASE WHEN correta=1 THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id) AS acertos,
            SUM(CASE WHEN tipo='pratica' THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id) AS pratica,
            SUM(CASE WHEN tipo='simulado' THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id) AS simulado,
            ROW_NUMBER() OVER (PARTITION BY materia_id ORDER BY ocorrido_em DESC,tipo DESC,id DESC) AS posicao
        FROM fatos
    )
    SELECT materia_id,materia_nome,assunto_id,assunto_nome,total_respostas,acertos,pratica,simulado,posicao
    FROM ranking WHERE posicao=1 ORDER BY materia_id;
    WITH fatos AS (
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_praticas_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
        UNION ALL
        SELECT tipo, id, atividade_id, usuario_id, ocorrido_em, correta,
            materia_id, materia_nome, assunto_id, assunto_nome
        FROM vw_simulados_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
    ), ranking AS (
        SELECT materia_id, materia_nome, assunto_id, assunto_nome,
            COUNT(*) OVER (PARTITION BY materia_id, assunto_id) AS total_respostas,
            SUM(CASE WHEN correta=1 THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id, assunto_id) AS acertos,
            SUM(CASE WHEN tipo='pratica' THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id, assunto_id) AS pratica,
            SUM(CASE WHEN tipo='simulado' THEN 1 ELSE 0 END) OVER (PARTITION BY materia_id, assunto_id) AS simulado,
            ROW_NUMBER() OVER (PARTITION BY materia_id, assunto_id ORDER BY ocorrido_em DESC,tipo DESC,id DESC) AS posicao
        FROM fatos
    )
    SELECT materia_id,materia_nome,assunto_id,assunto_nome,total_respostas,acertos,pratica,simulado,posicao
    FROM ranking WHERE posicao=1 ORDER BY materia_id, assunto_id;
END$$

CREATE PROCEDURE sp_atividades_recentes(
    IN p_usuario_id INT, IN p_inicio DATETIME(6), IN p_fim DATETIME(6))
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id < 1 OR p_inicio IS NULL OR p_fim IS NULL OR p_inicio >= p_fim THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Usuário e intervalo inválidos';
    END IF;
    SELECT tipo,id,ocorrido_em,titulo FROM (
        SELECT tipo,atividade_id AS id,ocorrido_em,CONCAT(materia_nome,' · ',assunto_nome) AS titulo
        FROM vw_praticas_fatos_desempenho
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
        UNION ALL
        SELECT tipo,id,ocorrido_em,titulo FROM vw_simulados_atividades
        WHERE usuario_id=p_usuario_id AND ocorrido_em>=p_inicio AND ocorrido_em<p_fim
    ) atividades ORDER BY ocorrido_em DESC,tipo DESC,id DESC LIMIT 5;
END$$

CREATE PROCEDURE sp_simulados_contagens_dashboard()
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    SELECT (SELECT COUNT(*) FROM simulados WHERE estado='rascunho') AS rascunhos,
        (SELECT COUNT(*) FROM simulados WHERE estado='publicado') AS publicados,
        (SELECT COUNT(*) FROM simulados WHERE estado='arquivado') AS arquivados,
        (SELECT COUNT(*) FROM simulado_tentativas WHERE estado='finalizada') AS finalizadas;
END$$
DELIMITER ;
