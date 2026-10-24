# Validação — Gestão básica de Questões

Data: 07/10/2026. Change: `gestao-basica-questoes`; schema: `spec-driven`.

## Verificação OpenSpec

| Dimensão | Resultado |
| --- | --- |
| Completude | Requisitos dos dois deltas implementados; tarefas 1.1–5.1 verificadas e fechamento 5.2 concluído com sincronização e arquivamento. |
| Correção | Fluxos, validações, permissões, concorrência, rollback e compatibilidade exercitados; suites e gates aprovados. |
| Coerência | Camadas existentes, TransactionManager, ADRs 001–006 e Desktop V1 preservados; sem módulo externo, mídia ou publicação automática. |

Nenhum achado CRÍTICO ou AVISO pendente. A implementação está apta ao fechamento. A implantação no banco operacional exige o upgrade documentado; os testes não executaram esse upgrade.

## Evidências por requisito

| Requisito | Implementação e evidência |
| --- | --- |
| Listagem e detalhe administrativos | Services de listagem/detalhe, Repository e rotas; teste MySQL de filtros, paginação, HEAD, 400/404 e 401/403; testes DOM da listagem. |
| Cadastro e edição compatíveis | CriarQuestaoService e EditarQuestaoService; regressão legada, edição inválida/obsoleta, rollback de cadastro e concorrência real. |
| Publicação explícita imutável | PublicarQuestaoService, Models de versões/eventos e TransactionManager; replay, nova versão, locks, falha da última gravação e rejeição de mutação ORM. |
| Arquivamento sem perda | ArquivarQuestaoService; replay, conflito, preservação da procedure e leitura histórica; teste de confirmação no frontend. |
| Elegibilidade e legado | Services de leitura elegível/histórica e migration 006; catálogo indisponível, DTO sem correção, backfill não publicado, FKs e equivalência de schema. |
| Gestão mínima utilizável | Telas e admin-questoes.js; testes DOM de dados reais, erros, descarte, expiração/troca de identidade e ausência de replay; inspeção de navegador a 1440 px. |

Os testes de integração estão em `backend/tests/test_questoes_versionadas_integration.py`, `test_questoes_integration.py`, `test_migrations_integration.py` e `test_autenticacao_integration.py`. O frontend está coberto por `frontend/tests/admin-questoes.test.js` e pelas suites existentes de catálogo/autenticação.

## Comandos e resultados

| Comando | Resultado |
| --- | --- |
| `python backend/tests/run_unit.py` | 106 testes aprovados. |
| `python backend/tests/run_backend_coverage.py` com os dois opt-ins MySQL somente no processo | 106 unitários e 68 integrações aprovados, sem skips; linhas 95,98% (2170/2261), branches 88,36% (539/610). |
| `npm run test:coverage` em `frontend/` | 65 testes, 9 arquivos aprovados; linhas 98,81% (1082/1095), branches 87,52% (512/585). |
| `openspec validate gestao-basica-questoes --strict` | Aprovado. |
| `openspec validate --specs` | Cinco capacidades aprovadas. |
| `git diff --check` | Sem erros de whitespace. |

Gates exigidos: linhas ≥90% e branches ≥85% em cada camada. Opt-ins utilizados: `RUN_MYSQL_INTEGRATION=1` e `RUN_MYSQL_MIGRATION_INTEGRATION=1`, sem persistência no `.env`. MySQL real 8.0.44, schemas descartáveis; nenhuma integração substituída por mocks ou SQLite. Casos originais do MVP, autenticação e catálogo permanecem nas suites executadas.

## Demonstração e inspeção visual

Navegador isolado e sessão administrativa real em schema temporário: criar Questão, salvar edição (revisão 2), confirmar publicação (versão 1), recarregar, confirmar arquivamento e localizar o item pelo filtro. Estado persistido, histórico preservado e edição bloqueada após arquivamento. Servidores temporários encerrados e schema removido ao finalizar.

Listagem e editor inspecionados com largura interna de 1440 px contra ADM-QUE-001/002 do Protótipo, Inventário e Handoff. Sem overflow horizontal; campos rotulados, foco inicial seguro da confirmação, navegação por Tab e confirmação contextual. Os binários oficiais não foram editados. Importação, IA, upload e módulos futuros permanecem indisponíveis.

## Sincronização e operação

Cinco requisitos adicionados à capacidade `questoes-versionadas` e um à capacidade `gestao-administrativa-conteudo`. Comparação integral dos blocos confirmou correspondência com todos os deltas; conteúdo anterior da spec administrativa e seu Purpose preservados. As specs principais usam uma única seção Requirements.

Antes de disponibilizar estas telas no ambiente atual, aplique a migration 006 pelo runner, com backup e verificações de `docs/technical/operacao-questoes.md`. Não houve commit, push ou merge. Alterações locais anteriores foram preservadas.
