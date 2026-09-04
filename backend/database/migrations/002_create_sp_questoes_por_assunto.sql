-- Pre-condicao: migrations 000 e 001 aplicadas.
-- Preservacao: substitui apenas a definicao da Stored Procedure.
-- Reversao: restaurar a definicao anterior explicitamente, quando existir.

DROP PROCEDURE IF EXISTS sp_questoes_por_assunto;

DELIMITER $$

CREATE PROCEDURE sp_questoes_por_assunto(IN p_assunto_id INT)
BEGIN
    SELECT
        id,
        enunciado,
        alternativa_a,
        alternativa_b,
        alternativa_c,
        alternativa_d,
        alternativa_e,
        resposta_correta,
        explicacao,
        dificuldade,
        assunto_id
    FROM questoes
    WHERE assunto_id = p_assunto_id
    ORDER BY id;
END$$

DELIMITER ;
