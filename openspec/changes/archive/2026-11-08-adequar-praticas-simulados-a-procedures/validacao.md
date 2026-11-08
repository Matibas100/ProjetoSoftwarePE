# Validação — Práticas e Simulados por procedures

## Preflight (07/11/2026)

- Schema `spec-driven`, 0/11 tarefas inicialmente. Dependência 013 aplicada, verificada, sincronizada e arquivada em `../archive/2026-11-07-adequar-catalogo-editorial-a-procedures/`; capability principal `catalogo-editorial-mysql` e prefixo 013 presentes.
- Nenhuma migration 014 existente. Inventário fechado: dezesseis métodos/procedures, conforme [inventário](inventario-procedures.md). Propriedade/replay/histórico/fatos de Práticas alimentam iniciar/responder/consultar/listar e API de fatos; Simulados alimenta gestão/catálogo, início/retomada, salvar/finalizar/correção, histórico e API de fatos. Projeções de compatibilidade de Desempenho já foram substituídas pelas views 012 no caminho executável.
- Lidas conventions, arquitetura mestre e ADRs 001–006/008–011. Contratos HTTP e APIs/Models preservados. Mudanças externas de 011–013, documentação/modelagem e demais changes já estavam presentes; snapshot de 614 arquivos em `tmp/praticas-baseline.json` para comparação final. Sem leitura/exibição de `.env`, credenciais ou dados pessoais.
- Testes usam somente schemas MySQL descartáveis; nenhuma instalação no banco operacional. CALL textual ORM caracterizado antes da conversão, inclusive tripla, tipos, identidade, leitura corrente e rollback.

## Hashes SHA-256 iniciais das migrations

- `backend/database/migrations/011_consultas_admin_procedures.sql`: `2fc6aace67b5e6121d44d3e1840baaa00582332f6bdd3a8bffd37e655fe5e665`
- `backend/database/migrations/012_desempenho_procedures.sql`: `0fb8b07c76e5428bef37a06daefc206cdc55a115257d81e263064cbcb34734b8`
- `backend/database/migrations/013_catalogo_editorial_procedures.sql`: `8db9ea8917cb621d68ce9679828fc1a3f5dcd9364b51ca3dfd0a702e2bc1d2dd`
- `backend/database/migrations/000_create_mvp_schema.sql`: `1e51d54b93a4d8125961a17e283e2933fa3fe1f0b8b385b6d50ede1bcdf868a8`
- `backend/database/migrations/001_restrict_delete_assuntos.sql`: `329594db44e2ee7f6a71b4c8a871cc5efb1dd849642ed4397b49a3ae7dca0b5d`
- `backend/database/migrations/002_create_sp_questoes_por_assunto.sql`: `7d19427eaed0f6e63ec4116aee0aa56cf07a2e12b6e559c2a09f5409414abd38`
- `backend/database/migrations/003_prepare_catalogo_academico.sql`: `dd27f63de40fd06585c4a3cbd33a9f164574ae983b3eeb3cffb8ff91a8decbd4`
- `backend/database/migrations/004_restrict_catalogo_academico.sql`: `de6bedc463391556498fe641cb61fe74a59717b421c59e0dfcb1d6ff71a804d8`
- `backend/database/migrations/005_create_autenticacao_escolar.sql`: `a650da20e8785b4de919e0324928844a282f63b76bacce0f752fdb55332fb8c2`
- `backend/database/migrations/006_create_questoes_versionadas.sql`: `97160b8fb019d8dc59e7f83452808b5fefd9a1944f20850d6336880822e2b36c`
- `backend/database/migrations/007_create_pratica_tentativas.sql`: `2ca7fc6c974dfa2e0011d72bc532a00a0e4cca8d9ab0055cdd9c4b93f58c3161`
- `backend/database/migrations/008_create_simulados.sql`: `b21286bbfcb77ba6bad04c1eda72d7fbc71b39dc825c847238cce1b73d71fe36`
- `backend/database/migrations/009_create_planos_estudo.sql`: `22763b2c463d65995f79a93aaa34a6ff3a760f591d94cfb19822be646126a624`
- `backend/database/migrations/010_create_registros_privacidade.sql`: `d91e31207a77afc6077c7dc7002b08fa7f2180f6df2dbe43a920d2107915d2dc`

## Caracterização antes da conversão

- `RUN_MYSQL_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_praticas_integration tests.test_simulados_integration -v`: **20 testes aprovados**, 26,836 s (`tmp/praticas-baseline.log`).
- `python -m unittest tests.test_praticas_simulados_procedures_integration -v`, com o mesmo opt-in: **2 testes aprovados**, 5,277 s (`tmp/praticas-caracterizacao.log`). Páginas vazias com total, UTC [início,fim), lotes vazios/repetidos, dono, tipos Boolean/Decimal/datetime, tripla ORM de CALL, JSON tipado, identidade/estado corrente, escrita e rollback na mesma sessão; close drena conjunto útil adicional e terminal, permitindo SELECT seguinte. Fixture inicialmente usou atualizar onde a Model exige atribuição/salvar; corrigida sem mudar produção.

## Conversão e validações por grupo

- `python -m unittest tests.test_praticas_simulados_procedures_integration tests.test_praticas_integration tests.test_simulados_integration -v`: **22 testes aprovados**, 45,436 s (`tmp/praticas-conversao.log`), agora usando as dezesseis routines oficiais. Contratos, replay, 404, versões retiradas, revisão, branco, concorrência de início/respostas/finalização, guards e rollback preservados.
- `python -m unittest tests.test_praticas_simulados_procedures_integration -v`: **7 testes aprovados**, 18,789 s (`tmp/praticas-procedures.log`). Inclui leitura corrente/identidade nos locks reais, bloqueio de responder por replay e rollback, concorrência de início com chaves distintas, trigger MySQL falhando após correção parcial e routine ausente com HTTP 500 seguro/sem fallback.
- Acrescentada caracterização de ordenação em empate de datas, dono/chave compartilhada, total/página vazia, precedência rascunho/versão, lotes repetidos e estado textual vinculado. Junto ao teste de consultas constantes: **2 testes aprovados**, 10,596 s (`tmp/praticas-ordem.log`). A instrumentação desse teste conta SELECT e CALL reais pelo driver, incluindo o helper de múltiplos conjuntos, sem substituir resultados.
- `python -m unittest tests.test_praticas_simulados_migrations_integration tests.test_migrations_integration.MigrationRunnerIntegrationTest.test_bootstrap_consolidado_equivale_as_migrations -v`, com ambos os opt-ins: **4 testes aprovados**, 35,058 s (`tmp/praticas-migrations.log`). Upgrade 013→014 com dados, baseline/restauração, idempotência, JSON/flags inválidos, recurso ausente/corpo/assinatura/segurança/dependência divergentes e bootstrap equivalente. Ajustado posicionamento de DELIMITER durante o ensaio inicial, respeitando o parser existente.
- Referências geradas exclusivamente por instalação oficial em schema descartável: **42 recursos**, com as **26 referências anteriores idênticas**. Reconhecidos 013 antes e 014 após o upgrade. Prefixo do bootstrap anterior preservado byte a byte; nenhum SQL 000–013 alterado.
- `python backend/tests/run_unit.py`: **183 testes aprovados**, 5,968 s (`tmp/praticas-unit.log`), incluindo arquitetura/metadata/guards. Nenhuma Model, contrato ou tela alterada.
- README, matrizes acadêmica/CRUD, documento SQL e adendo ao ADR-011 atualizados com métodos, predicados, locks, saídas, Controller/Service/tela, instalação, privilégios e compensação. Os vinte IDs são mantidos; Plano/Contas continuam pendentes.

## Revisão de escopo e validação estática

- `openspec validate adequar-praticas-simulados-a-procedures --strict` e `git diff --check`: aprovados. Aviso de normalização CRLF do Git no bootstrap não representa alteração do prefixo protegido; o hash do prefixo anterior foi reconstituído e conferido byte a byte.
- Comparação com snapshot inicial: somente os dois Repositories do inventário, dois registros de apresentação novos, instalação/reconhecimento/preflight, testes correspondentes, cinco documentos do escopo e esta change foram alterados. Alterações externas preservadas; migrations 000–013, contratos e visuais têm hashes idênticos aos iniciais. O teste de 013 fica explicitamente limitado às migrations até 013; a regressão geral amplia reconhecimento até 014 sem remover prefixos anteriores.
- Links locais dos documentos atualizados conferidos, vinte IDs da matriz inalterados. Fontes novos em UTF-8 sem BOM/whitespace; corrigida a codificação do relatório após detectar conversão do pipe do PowerShell. Sem segredos/dados pessoais nos novos fontes. CALLs de produção permanecem somente nos Repositories. Nenhuma operação Git, deploy ou DDL no banco de uso.

## Frontend e navegador real

- `npm run test:coverage`: **15 arquivos / 182 testes aprovados** (50,70 s). Linhas **99,26% (1879/1893)**, branches **87,98% (1325/1506)**; gates mantidos (`tmp/praticas-frontend-coverage.log`).
- `scripts/run_e2e.executar_suite(settings, ambiente)` com `RUN_MYSQL_E2E=1`: **3 E2Es aprovados (1,0 min)**, saída 0. Configuração existente transmitida somente no ambiente, sem imprimir credenciais; o runner inicia API/frontend e usa schema descartável. Vinte funcionalidades, Plano/Simulado e Privacidade com persistência real; schema e processos removidos em finally (`tmp/praticas-e2e.log`). Nenhuma alteração visual ou mock de integração.

## Resultado da aplicação

- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; python backend/tests/run_backend_coverage.py`: **183 unitários + 169 integrações MySQL aprovados**, incluindo as 29 originais, sem integrações puladas. Integrações em **531,526 s**; saída 0 (`tmp/praticas-backend-coverage.log`). Inclui Práticas/Simulados, migrations correspondentes, Desempenho, catálogo, Plano, privacidade e todos os prefixos históricos.
- Backend: **97,55% de linhas (4263/4370)** e **91,75% de branches (879/958)**; gate de arquivo executável sem cobertura aprovado. Frontend: **182 testes**, **99,26% de linhas / 87,98% de branches**. Navegador: **3 E2Es** com MySQL real. Nenhum gate reduzido.
- **11/11 tarefas concluídas** no schema `spec-driven`. Dezesseis procedures, migration/bootstrap 014, Repositories, registros de apresentação, reconhecimento/preflight, regressões e documentação implementados. Locks, transações, versões, autorização, guards, 21 Models e contratos preservados.
- Aplicação concluída; próxima etapa do workflow: verificar, sincronizar os dois deltas e arquivar. Nenhuma sincronização, arquivamento, commit/push/merge, deploy ou DDL no banco de uso foi executado nesta aplicação.

## Correção do achado da verificação — 08/11/2026

- A verificação identificou um achado CRÍTICO: com histórico válido até 013, remover `sp_bloquear_assunto` ainda permitia ao runner aplicar 014 e registrar APPLIED. O detector rejeitava o prefixo físico, mas não era chamado antes do DDL. O resultado anterior de aplicação não comprovava esse cenário; sincronização/arquivamento ficaram impedidos.
- Correção autorizada pelo usuário na mesma change. Reabertas 4.1/5.1/5.2 e explicitado o cenário já exigido de integridade da dependência. `run_up` agora exige exatamente 013 pelo detector físico existente, sob o lock e após as proteções de histórico, antes de registrar RUNNING ou executar 014. Não altera SQLs, referências, regras funcionais ou prefixos anteriores.
- Teste de regressão executado antes da correção: **1 falha esperada**, `MigrationError not raised` (`tmp/praticas-fix-red.log`). Casos adicionais exercitam recurso ausente, corpo/assinatura/segurança divergentes, procedure legada, tabela alterada e indícios parciais de 014, verificando preservação de dados/histórico/objetos e liberação do lock. Reparar a dependência deve permitir upgrade normal e repetição idempotente.
- `python -m unittest tests.test_praticas_simulados_migrations_integration -v`, com ambos os opt-ins: **5 testes aprovados**, 50,036 s (`tmp/praticas-fix-migrations.log`). Acrescentado também à suíte final o caso de recursos completos de 014 ainda sem registro no histórico: ele deve bloquear em vez de aceitar prefixo físico diferente de 013.
- `openspec validate adequar-praticas-simulados-a-procedures --strict` e `git diff --check`: aprovados após a correção. Conferidos preflight dentro do lock/antes do DDL e hashes protegidos de migrations anteriores, contratos e visuais. Documento SQL, design e cenário da spec agora explicitam o bloqueio prévio.
- E2E após a correção: **3 testes aprovados (56,7 s)**, saída 0, schema/processos descartáveis removidos (`tmp/praticas-fix-e2e.log`). Código frontend permanece o mesmo da coleta de 182 testes/99,26% de linhas/87,98% de branches anterior.
- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; python backend/tests/run_backend_coverage.py`: **183 unitários + 171 integrações MySQL aprovados**, sem integrações puladas, saída 0. Integrações em **458,447 s** (`tmp/praticas-fix-backend-coverage.log`), incluindo os oito cenários de drift/pré-condição e reparação seguida de upgrade/idempotência.
- Cobertura final do backend: **97,55% de linhas (4265/4372)** e **91,77% de branches (881/960)**, com os gates mantidos. Os prefixos antigos, checksums, locks e bloqueios RUNNING/FAILED continuam cobertos.

### Verificação após a correção

| Dimensão | Resultado |
|---|---|
| Completude | 11/11 tarefas; dezesseis interfaces e bloqueio prévio de 013 cobertos |
| Correção | Ensaio antes da correção falhou; regressões físicas, reparação, suíte MySQL completa e E2E passaram após a correção |
| Coerência | Detector existente reutilizado sob o lock; camadas/contratos/SQLs anteriores preservados |

**Achado CRÍTICO resolvido**, sem outros achados bloqueantes na revisão. Correção limitada a quatro linhas no runner, regressões e documentação da pré-condição já especificada. Pronta para sincronizar os dois deltas e depois arquivar. Nenhuma sincronização/arquivamento, operação Git ou DDL no banco de uso foi executado.

## Sincronização das specs — 08/11/2026

- Sincronizados os cinco requisitos de `praticas-simulados-mysql` em spec principal nova, com Purpose preservado, e o requisito de reconhecimento/instalação de 014 em `migrations-sql`, incluindo o bloqueio da dependência física divergente.
- Comparação completa dos dois deltas com as specs principais: todos os requisitos/cenários idênticos, nenhuma operação pendente. O conteúdo anterior de `migrations-sql` foi preservado byte a byte, inclusive Purpose e requisitos dos prefixos anteriores.
- `openspec validate --specs`: **14 specs aprovadas**. `openspec validate adequar-praticas-simulados-a-procedures --strict` e `git diff --check`: aprovados. 11/11 tarefas, verificação concluída e achado crítico resolvido; fechamento autorizado pelo usuário. Sem alteração de código/testes/banco ou operações Git nesta etapa documental.

## Arquivamento — 08/11/2026

- CLI oficial: `openspec archive adequar-praticas-simulados-a-procedures --skip-specs --yes --json`, saída 0. O flag evita reaplicar specs já sincronizadas e comparadas nesta etapa; não pula validação.
- Arquivada em `openspec/changes/archive/2026-11-08-adequar-praticas-simulados-a-procedures/`, com `.openspec.yaml` e artefatos preservados. Workflow concluído: aplicada, verificada, sincronizada e arquivada, sem tarefas pendentes ou achados críticos.
