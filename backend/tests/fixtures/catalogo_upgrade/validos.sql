INSERT INTO materias (id, nome, descricao) VALUES
    (910001, 'Matemática', 'Descrição preservada'),
    (910002, 'História', NULL);
INSERT INTO assuntos (id, nome, descricao, materia_id) VALUES
    (920001, ' Geometria   Plana ', 'Assunto preservado', 910001),
    (920002, 'Brasil Colônia', NULL, 910002);
INSERT INTO questoes (
    id, enunciado, alternativa_a, alternativa_b, alternativa_c,
    alternativa_d, alternativa_e, resposta_correta, explicacao,
    dificuldade, assunto_id
) VALUES (
    930001, 'Enunciado preservado', 'A', 'B', 'C', 'D', 'E',
    'A', 'Explicação preservada', 'facil', 920001
);
