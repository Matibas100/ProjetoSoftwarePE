DELIMITER $$
-- Pré-condição: 016 íntegro. Somente routines; sem alteração de dados ou FKs.
-- DDL não possui rollback transacional. Aplicar após backup validado.
-- Compensação: restaurar backup ou remover as duas routines em migration revisada.
CREATE PROCEDURE sp_alunos_admin(
    IN p_busca VARCHAR(254), IN p_ativo TINYINT,
    IN p_offset BIGINT, IN p_limite INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_offset IS NULL OR p_offset < 0 OR p_limite IS NULL OR
       p_limite < 1 OR p_limite > 100 OR
       (p_ativo IS NOT NULL AND p_ativo NOT IN (0,1)) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Parâmetros de consulta inválidos';
    END IF;
    SELECT id,nome,email,perfil,ativo,criado_em FROM usuarios
    WHERE perfil='aluno' AND (p_ativo IS NULL OR ativo=p_ativo)
      AND (p_busca IS NULL OR p_busca='' OR LOCATE(p_busca,nome)>0 OR LOCATE(LOWER(p_busca),email)>0)
    ORDER BY criado_em DESC,id DESC LIMIT p_limite OFFSET p_offset;
    SELECT COUNT(*) AS total_itens FROM usuarios
    WHERE perfil='aluno' AND (p_ativo IS NULL OR ativo=p_ativo)
      AND (p_busca IS NULL OR p_busca='' OR LOCATE(p_busca,nome)>0 OR LOCATE(LOWER(p_busca),email)>0);
END$$

CREATE PROCEDURE sp_usuario_gestao_bloqueado(IN p_usuario_id INT)
READS SQL DATA
SQL SECURITY INVOKER
BEGIN
    IF p_usuario_id IS NULL OR p_usuario_id < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Identificador inválido';
    END IF;
    SELECT id,nome,email,senha_hash,perfil,ativo,criado_em FROM usuarios
    WHERE id=p_usuario_id FOR UPDATE;
END$$
DELIMITER ;
