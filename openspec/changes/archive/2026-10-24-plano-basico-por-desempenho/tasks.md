# Tarefas — 6. Plano básico

## 1. Dependências e persistência

- [x] 1.1 Confirmar item 5 encerrado, localizar seu contrato final mesmo arquivado e reler diagnóstico/elegibilidade/prática, conventions/ADRs e ALU-PLA-001 nas fontes oficiais. Validar decisões de três assuntos/cinco respostas/30 dias e ausência de divergências antes de editar código.
- [x] 1.2 Criar migration consecutiva, snapshot e Models de plano/itens com justificativa imutável e chave/referência da operação; testar zero/upgrade/reexecução, FKs, ordem única, um plano atual e preservação de gerações no MySQL real.
- [x] 1.3 Documentar schema, backup/compensação e recorte sem agenda em `docs/technical/operacao-plano-estudos.md`; validar correspondência com design/specs, sem planos fictícios no bootstrap.

## 2. Gerar e consultar

- [x] 2.1 Implementar Service de seleção usando diagnóstico existente e elegibilidade, sem fórmula paralela; testar taxa exata, desempates, limite três, amostra insuficiente, 100%, catálogo transferido/arquivado e diagnóstico indisponível com unitários e integração MySQL.
- [x] 2.2 Implementar geração/consulta própria com snapshots, transação e chave UUID; testar 201/replay 200/chave divergente 409, sem plano no GET, falta de base sem gravação, rollback na última etapa e concorrência de geração no MySQL real.
- [x] 2.3 Aplicar Controllers/rotas/CSRF/Origin/no-store e propriedade; testar campos extras, 401/403 e 404 uniforme de recurso alheio, documentando contratos de geração/consulta.

## 3. Estudar, concluir e recalcular

- [x] 3.1 Implementar disponibilidade atual e conclusão manual idempotente com data preservada; testar conteúdo retirado, item histórico 409 e ausência de mudanças em desempenho/respostas, documentando significado de conclusão.
- [x] 3.2 Implementar recálculo confirmado com ID do plano atual, geração nova e histórico preservado; testar nova ordenação, replay, chave divergente, concorrência 409, falta de candidatos e rollback sem perder plano/conclusões no MySQL real.
- [x] 3.3 Documentar justificativa/ordem/limiar e recálculo explícito no documento operacional; conferir exemplos com diagnóstico do item 5 e demonstrar que nova resposta não recalcula automaticamente.

## 4. Lista de prioridades do Aluno

- [x] 4.1 Implementar `/aluno/plano.html`, link no dashboard e navegação para prática filtrada por Assunto; validar gerar/iniciar/concluir/recalcular com APIs reais, DOM e referência visual em 1440 px, sem calendário ou duração inventados.
- [x] 4.2 Integrar confirmação de substituição, ausência de base, indisponibilidade, falha/recuperação de sessão e teclado/foco; testar preservação de plano e troca de identidade sem replay automático/exposição de dados, documentando fluxo mínimo.

## 5. Validação integrada e fechamento

- [x] 5.1 Executar testes unitários, cobertura backend/frontend e integrações reais com opt-in MySQL só no processo; preservar 29 cenários originais e regressões dos itens 1–5, limiares e proteção de segredos; registrar comandos/resultados/limitações.
- [x] 5.2 Demonstrar diagnóstico real -> plano ordenado -> prática -> conclusão -> recálculo preservando histórico; executar `openspec validate plano-basico-por-desempenho --strict`, verify, sync e archive apenas com tarefas concluídas e sem achados críticos; sem commit/push automático.
