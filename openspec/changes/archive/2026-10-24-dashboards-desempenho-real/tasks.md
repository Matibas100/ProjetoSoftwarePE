# Tarefas — 5. Dashboards e desempenho

## 1. Dependências e contratos de leitura

- [x] 1.1 Confirmar itens 3/4 encerrados, localizar contratos finais pelo nome inclusive arquivados e reler conventions/ADRs, snapshots/fatos e fontes ALU-DASH-001/ALU-DES-001/ADM-DASH-001. Confirmar equivalência entre fatos dos Services predecessores e projeções propostas nos Repositories de origem, incluindo identidade do registro/atividade, instante e classificação; validar ausência de schema novo. Divergência deve atualizar planejamento antes de apply.
- [x] 1.2 Implementar projeções especializadas de leitura por origem e união autorizada para desempenho, sem escrita ou acesso a tabelas internas fora do contrato; validar equivalência com Services de origem, filtro obrigatório por usuário/período, práticas corrigidas, itens respondidos finalizados, replay, repetições e exclusão de branco/em andamento em testes unitários e integração MySQL.
- [x] 1.3 Documentar fronteiras, fórmula, denominadores distintos, UTC e limiar operacional em `docs/technical/operacao-desempenho.md`; conferir exemplos contra dados temporários dos testes sem alterar OD-17 geral.

## 2. Diagnóstico e APIs

- [x] 2.1 Implementar Service de diagnóstico, Repository de agregação e `ContextoLeitura` de infraestrutura conforme design, com snapshot `REPEATABLE READ`, relógio único e participação em contexto externo sem commit/rollback próprio. Testar média ponderada por totais, zero/null, contagens por origem, fronteira 4/5, 30/366 dias, limites UTC, transferência/renomeação, resposta concorrente durante leitura, encerramento do contexto próprio em falha e preservação da transação externa com MySQL real; nenhuma sessão/SQL no Service.
- [x] 2.2 Implementar `/api/aluno/desempenho` e `/api/aluno/dashboard`, contratos internos reutilizáveis e cinco atividades próprias no mesmo período; validar campos do resumo, ordem/desempate, uma atividade por tentativa, simulado todo em branco sem resposta no diagnóstico, lista vazia, filtros extras, 400/401/403, erro 500 sem sucesso parcial, ausência de usuário alvo, isolamento A/B e no-store com testes HTTP e integração.
- [x] 2.3 Implementar `/api/admin/dashboard` com contagens globais de estados atuais e nenhuma informação individual de estudante; testar valores reais, estado vazio, perfil insuficiente e consistência de uma resposta; documentar os três contratos e exemplos.

## 3. Telas com dados reais

- [x] 3.1 Evoluir `/aluno/inicio.html` e criar `/aluno/desempenho.html`/`/admin/dashboard.html` sem mudar destinos de login; validar cards/listas com API real, base/período/amostra e links para atividades existentes por DOM e referência visual em 1440 px.
- [x] 3.2 Implementar estados visuais por bloco, sem dados/amostra pequena, erro e recarga conjunta dos blocos do mesmo endpoint, teclado/foco e sessão/troca de identidade; testar remoção de dados anteriores em recarga/troca de período, descarte de respostas atrasadas por período/identidade, navegação durante falha e ausência de percentual fictício ou exposição da conta anterior, documentando recursos ainda indisponíveis.

## 4. Validação integrada e fechamento

- [x] 4.1 Executar testes unitários, cobertura backend/frontend e integrações MySQL com opt-in só no processo; exigir 29 cenários originais e regressões de auth/catálogo/práticas/simulados, métricas conferidas por fixture real e limiares; registrar comandos/resultados/limitações sem segredos.
- [x] 4.2 Demonstrar respostas reais refletidas por Matéria/Assunto e dashboards após recarga, sem alterar correções; executar `openspec validate dashboards-desempenho-real --strict`, verify, sync e archive após tarefas/achados resolvidos; sem commit/push automático.
