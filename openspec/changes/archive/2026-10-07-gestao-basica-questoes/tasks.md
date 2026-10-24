# Tarefas — 2. Gestão básica de Questões

## 1. Preflight e persistência

- [x] 1.1 Reler proposal/design/deltas, conventions, ADRs e código atual, preservando alterações locais; confirmar item 1 e referências ADM-QUE-001/002 no Inventário/Handoff/Protótipo. Validar ausência de divergência bloqueante antes da primeira edição; divergência exige atualizar a change.
- [x] 1.2 Criar migration consecutiva, snapshot equivalente e Models de versões/eventos/estado/revisão conforme design, com backfill não publicado e IDs preservados. Validar instalação limpa, upgrade de 005, reexecução, FKs e equivalência no MySQL real em `test_migrations_integration.py`/fixtures temporárias.
- [x] 1.3 Documentar backfill, pré/pós-condições, backup e reversão em `docs/technical/operacao-questoes.md`; validar exemplos com runner sem exibir configuração ou executar em banco não autorizado.

## 2. Cadastro, listagem e edição

- [x] 2.1 Adaptar `CriarQuestaoService`/Model para rascunho e eventos atômicos, mantendo payload 201 legado; adicionar testes unitários e integração de cadastro/rollback e executar regressão dos 12 cenários originais de Questão.
- [x] 2.2 Implementar Services/Controller/Repository/rotas de listagem filtrada e detalhe administrativo; validar envelope, paginação, filtros, ordenação, 400/404, 401/403 e procedure intacta com testes unitários e MySQL real.
- [x] 2.3 Implementar edição de rascunho com revisão, validação e lock; testar revisão obsoleta, catálogo indisponível e preservação de versão publicada, incluindo concorrência MySQL; registrar contratos de GET/PUT no documento operacional.

## 3. Publicação e retirada de uso

- [x] 3.1 Implementar publicação revisada com snapshot/classificação/eventos/ponteiro em `TransactionManager`, sem SQL/`db.session` no Service; validar imutabilidade, replay, numeração concorrente e rollback na última gravação com testes unitários e integração real.
- [x] 3.2 Implementar arquivamento auditado sem DELETE/reativação e Services de leitura elegível/histórica; testar retirada de novos usos, replay e preservação das versões e da consulta legada.
- [x] 3.3 Aplicar autorização, CSRF/Origin, no-store e reautenticação para publicar/arquivar em `auth_http.py`; validar 401/403, janela de 15 minutos, HEAD e regressão de catálogo/auth com testes; documentar ações sensíveis e fronteira de conteúdo para itens 3/4.

## 4. Telas administrativas

- [x] 4.1 Implementar `/admin/questoes.html` e `/admin/questao.html` com scripts/CSS incrementais, navegação e dados reais; validar cadastro/filtros/edição/publicação/arquivamento com testes DOM e inspeção visual em 1440 px contra referências oficiais, sem editar binários.
- [x] 4.2 Integrar `AuthUI`, proteção de alterações locais, confirmação, reautenticação contextual e estados acessíveis; testar falha/expiração/troca de conta, teclado/foco e ausência de replay automático; documentar o recorte e recursos indisponíveis.

## 5. Validação integrada e fechamento

- [x] 5.1 Executar `python backend/tests/run_unit.py`, testes frontend e suites de cobertura backend/frontend conforme conventions, com opt-in de MySQL apenas no processo; exigir regressão dos 29 cenários originais, novas integrações reais e limiares de cobertura, registrando comandos/resultados/limitações sem segredos.
- [x] 5.2 Demonstrar criar -> editar -> publicar -> arquivar e compatibilidade do MVP; executar `openspec validate gestao-basica-questoes --strict`, verificar implementação com a skill de verify, corrigir achados, sincronizar specs e arquivar somente com todas as tarefas concluídas, sem commit/push automático.
