-- Auditoria somente leitura. Retorna apenas identificadores, nomes e causas.
SELECT
    m.id AS materia_id,
    m.nome AS materia_nome,
    'materia_nao_classificada' AS causa
FROM materias AS m
WHERE m.area_enem_id IS NULL
ORDER BY m.id;

SELECT
    a.materia_id,
    a.nome_normalizado,
    GROUP_CONCAT(a.id ORDER BY a.id) AS assunto_ids,
    GROUP_CONCAT(a.nome ORDER BY a.id SEPARATOR ' | ') AS assunto_nomes,
    'nome_normalizado_conflitante' AS causa
FROM assuntos AS a
GROUP BY a.materia_id, a.nome_normalizado
HAVING COUNT(*) > 1
ORDER BY a.materia_id, MIN(a.id);
