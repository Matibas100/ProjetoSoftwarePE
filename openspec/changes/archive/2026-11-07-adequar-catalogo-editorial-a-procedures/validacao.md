# Validação — Catálogo editorial por procedures

## Preflight — 07/11/2026

Schema: `spec-driven`. Início com 0/11 tarefas. Dependência `adequar-consultas-academicas-a-procedures`: 17/17 tarefas; verificação concluída nesta sessão sem achados críticos (completude, correção e coerência). Conferidas evidências finais de 183 unitários, 148 integrações, frontend/E2E, hashes e fontes; 17 testes focados passaram novamente. As duas specs foram sincronizadas e `openspec validate --specs` aprovou 12 specs. Prefixo oficial anterior 012; não há colisão com 013. Nenhum DDL no banco de uso.

## Alterações anteriores a esta aplicação

```text
 M README.md
 M backend/app/contexto_leitura.py
 M backend/app/modules/conteudo/repositories/catalogo_repository.py
 M backend/app/modules/conteudo/repositories/consultas_catalogo.py
 M backend/app/modules/conteudo/repositories/questao_repository.py
 M backend/app/modules/conteudo/services/gestao_questao_service.py
 M backend/app/modules/desempenho/repositories/desempenho_repository.py
 M backend/app/modules/simulados/repositories/simulado_repository.py
 M backend/database/create_database.sql
 M backend/database/legacy_schema.py
 M backend/tests/integration_support.py
 M backend/tests/test_desempenho_integration.py
 M backend/tests/test_migrations_integration.py
 M backend/tests/test_planos_integration.py
 M backend/tests/test_privacidade_migration_integration.py
 M backend/tests/test_schema_portavel_integration.py
 M docs/technical/adr/README.md
 M docs/technical/diagrama-de-classes.md
 M docs/technical/entrega-academica.md
 M openspec/specs/migrations-sql/spec.md
?? backend/app/core/procedures_mysql.py
?? backend/app/modules/conteudo/repositories/registros_admin.py
?? backend/database/migrations/011_consultas_admin_procedures.sql
?? backend/database/migrations/012_desempenho_procedures.sql
?? backend/database/sql_resources.py
?? backend/database/sql_resources_reference.json
?? backend/tests/sql_observer.py
?? backend/tests/test_consultas_academicas_integration.py
?? backend/tests/test_consultas_migrations_integration.py
?? backend/tests/unit/test_procedures_mysql.py
?? backend/tests/unit/test_sql_resources.py
?? docs/technical/adr/ADR-011-interfaces-sql-de-leitura.md
?? docs/technical/consultas-academicas-mysql.md
?? docs/technical/matriz-crud.md
?? docs/technical/modelagem-de-dominio.md
?? openspec/changes/adequar-catalogo-editorial-a-procedures/
?? openspec/changes/adequar-consultas-academicas-a-procedures/
?? openspec/changes/adequar-contas-privacidade-a-procedures/
?? openspec/changes/adequar-plano-estudos-a-procedures/
?? openspec/changes/adequar-praticas-simulados-a-procedures/
?? openspec/changes/archive/2026-11-07-formalizar-modelagem-e-cobertura-crud/
?? openspec/specs/consultas-academicas-mysql/
?? tmp/
```

As alterações anteriores incluem a dependência aplicada e documentação externa; serão preservadas. As próximas changes 014–016 não serão aplicadas em paralelo.

## Inventário conferido

Ver [inventário fechado](inventario-procedures.md): 15 routines. Seletores são consumidos por Models/delegações e Services de catálogo; impactos/equivalência/locks por exclusão/status/transferência e publicação. QuestaoRepository atende gestão editorial e APIs públicas de versões; adaptador de listagem segura atende Práticas. Simulados/Plano consomem as APIs públicas sem importar persistência privada. `pares_elegiveis_plano` permanece reservado à 015. Sem novas rotas/tabelas/Models.

## SHA-256 do estado inicial

| Arquivo | SHA-256 |
|---|---|
| `backend/database/migrations/000_create_mvp_schema.sql` | `1e51d54b93a4d8125961a17e283e2933fa3fe1f0b8b385b6d50ede1bcdf868a8` |
| `backend/database/migrations/001_restrict_delete_assuntos.sql` | `329594db44e2ee7f6a71b4c8a871cc5efb1dd849642ed4397b49a3ae7dca0b5d` |
| `backend/database/migrations/002_create_sp_questoes_por_assunto.sql` | `7d19427eaed0f6e63ec4116aee0aa56cf07a2e12b6e559c2a09f5409414abd38` |
| `backend/database/migrations/003_prepare_catalogo_academico.sql` | `dd27f63de40fd06585c4a3cbd33a9f164574ae983b3eeb3cffb8ff91a8decbd4` |
| `backend/database/migrations/004_restrict_catalogo_academico.sql` | `de6bedc463391556498fe641cb61fe74a59717b421c59e0dfcb1d6ff71a804d8` |
| `backend/database/migrations/005_create_autenticacao_escolar.sql` | `a650da20e8785b4de919e0324928844a282f63b76bacce0f752fdb55332fb8c2` |
| `backend/database/migrations/006_create_questoes_versionadas.sql` | `97160b8fb019d8dc59e7f83452808b5fefd9a1944f20850d6336880822e2b36c` |
| `backend/database/migrations/007_create_pratica_tentativas.sql` | `2ca7fc6c974dfa2e0011d72bc532a00a0e4cca8d9ab0055cdd9c4b93f58c3161` |
| `backend/database/migrations/008_create_simulados.sql` | `b21286bbfcb77ba6bad04c1eda72d7fbc71b39dc825c847238cce1b73d71fe36` |
| `backend/database/migrations/009_create_planos_estudo.sql` | `22763b2c463d65995f79a93aaa34a6ff3a760f591d94cfb19822be646126a624` |
| `backend/database/migrations/010_create_registros_privacidade.sql` | `d91e31207a77afc6077c7dc7002b08fa7f2180f6df2dbe43a920d2107915d2dc` |
| `backend/database/migrations/011_consultas_admin_procedures.sql` | `2fc6aace67b5e6121d44d3e1840baaa00582332f6bdd3a8bffd37e655fe5e665` |
| `backend/database/migrations/012_desempenho_procedures.sql` | `0fb8b07c76e5428bef37a06daefc206cdc55a115257d81e263064cbcb34734b8` |
| `backend/app/contracts/__init__.py` | `b8192eb073bff89e062128bf863108a1af090b8f73c767372fb78cdc1693eef7` |
| `backend/app/contracts/catalogo.py` | `254796eb1d93e925adfd64d7c6032df011f86fa60979533edd6783373023833e` |
| `backend/app/contracts/desempenho.py` | `e76fc41c0c3df5122ca96c50cdf0f59f78c446d6b0c4e7a25e2689e61ad19391` |
| `backend/app/contracts/questoes.py` | `47831dfc93bbc1a96d982c5b4d6d0808f13b5273488693c682685ba786913f44` |
| `backend/app/contracts/simulados.py` | `f895f1f34f52ae62aead79d61ef008be735540586ebf590c2776da226f2737f7` |
| `docs/design/desktop-v1/ERRATA.md` | `73bb5a35ebf96dec7aac843ea859f888344493daf368563969df1e5249481171` |
| `docs/design/desktop-v1/Plataforma_ENEM_Handoff_Mestre_Desktop_FINAL.pdf` | `f99f7656901fa552f06dd47286b8dd30475941b86516adb5d773c0247b089d87` |
| `docs/design/desktop-v1/Plataforma_ENEM_Inventario_Mestre_Desktop_FINAL.xlsx` | `bf8d051467c6620eb88132cb56f8ed72d3c1ea6142fa9f415319a7b898fbb22e` |
| `docs/design/desktop-v1/Plataforma_ENEM_Logo_Oficial_SVG_FINAL.zip` | `ce4aeba68a05f607942b711341c7ba1cbb77598cadea06d14199df921809456e` |
| `docs/design/desktop-v1/Plataforma_ENEM_Prototipo_Clicavel_Desktop_FINAL.pdf` | `2c673428337bb14330406a28a9c16dba1f4634335b5c68e5c918bdb78a853a52` |
| `docs/design/desktop-v1/README.md` | `ce74102e5c860ff123acb9840594230d285d27a484f4634a59ff321ed8ed361c` |
| `backend/database/create_database.sql` | `7d4f837e1e7585001496727b337fec6a51a86af1b6408820c871740cec3aba7f` |
| `backend/database/sql_resources_reference.json` | `f319a996ca6e691ad118b665a21e3b49f82ca7b727804b7ffd1614d5426e000c` |
| `backend/app/routes.py` | `91e79070ece940db108b4e1ca37a178fd5e42520b69195637fe8d77fb239f6eb` |
| `backend/app/models/__init__.py` | `bf2e84b8c2c38919e9475057d2f7a41156d96bd0ff31c0f29c94f842b466f56e` |
| `README.md` | `92e14729d638a57059f188391a244562425cc5b92970afd895551c883d7f49e2` |
| `docs/technical/entrega-academica.md` | `40d386e72c0215531770963662f8893db828075d827187a6a10adafad05cf73f` |
| `docs/technical/matriz-crud.md` | `4ecd9c9566838bbe7598a6ae8393c11d47baecc86bd470999259488c38a28775` |
| `docs/technical/diagrama-de-classes.md` | `c94966b7ed9685c915d401c2f8e377330e276fc248798c658048da8a3d8282d9` |
| `docs/technical/modelagem-de-dominio.md` | `cc60004f4cc9bf1ea8cdf00e475a10f1462bb2fe6983872e944aba2bc565828a` |
| `docs/technical/consultas-academicas-mysql.md` | `d0c0f15d21a8620696cfbed75e18cbe21f67a73dd1018cf80e4354f33da1f3e9` |
| `openspec/specs/consultas-academicas-mysql/spec.md` | `3f98b4264db657ebb02d3158b4beea7df0474cc697d82fb7d8bcde4571a1cd9f` |

## Caracterização antes da conversão

`RUN_MYSQL_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_catalogo_procedures_integration -v`: 2 testes aprovados, 5,335 s. JOIN textual de CALL mapeou Assunto/Matéria gerenciados na mesma sessão, com identidade preservada, leitura corrente após outra conexão, JSON/Boolean/datas tipados, mutação/rollback, vazio e SELECT posterior após fechar/drenar resultados extras. A fixture passou a usar BIGINT UNSIGNED para testar ID acima de 2^31. Seletores, impacto com duas Questões, equivalência normalizada e arquivada, ignorar próprio ID e estados ativos foram caracterizados antes da troca.

## Conversão de Catálogo e editorial

- `python -m unittest tests.test_catalogo_procedures_integration tests.test_catalogo_admin_integration tests.test_materias_integration tests.test_assuntos_integration -v` com opt-in: 26 testes aprovados, 11,495 s. Seletores, quatro Áreas, ativos/todos, impacto, equivalência, status, transferência e RESTRICT preservados.
- `python -m unittest tests.test_questoes_versionadas_integration tests.test_praticas_integration -v`: 15 testes aprovados, 11,272 s. Publicação/replay, guards, revisão/motivo, rollback, classificação/versões e conteúdo seguro mantidos.
- `python -m unittest tests.test_catalogo_procedures_integration -v`: 7 testes aprovados, 6,815 s. Inclui duas conexões reais, identidade corrente, aquisição Assunto→Matérias ordenadas, publicação bloqueada atrás de transferência (snapshot na classificação nova), trigger sintético que provoca erro real na última gravação e rollback integral, batches vazios/repetidos, versões antigas, total em página vazia e ausência de routines sem fallback.
- Documentação atualizada por grupo com os quinze contratos, tipos, rotas/consumidores e distinção disponibilidade/histórico. As mesmas validações de Services permanecem. `pares_elegiveis_plano` fica reservado à 015.
- Referências de 013 geradas por instalação das migrations oficiais em schema descartável e remoção em finally: 26 recursos SQL. Conferida igualdade exata das onze referências anteriores; reconhecimento retornou 013. Nenhum DDL no banco de uso.

## Instalação, documentação e revisão final

- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_catalogo_migrations_integration -v`: 3 testes aprovados, 20,242 s. Upgrade 012→013 com registros, baseline de restauração 013, idempotência, JSON vazio/repetido/inválido, recursos ausentes/corpo/assinatura/segurança alterados e dependência 012 divergente.
- `python backend/tests/run_unit.py`: 183 testes aprovados, 2,782 s, incluindo arquitetura/metadata/guards.
- Links dos documentos atualizados conferidos; IDs 1–20 da matriz preservados. README/matrizes/documento SQL/ADR-011 descrevem o recorte e as pendências 014–016, sem novas funcionalidades ou promessa de aprovação acadêmica.
- Conferida igualdade byte a byte do prefixo completo 012 do bootstrap com seu hash inicial; somente o bloco 013 foi acrescentado. Hashes dos SQLs 000–012, contratos, fontes visuais e documentação externa não prevista permanecem iguais. Onze referências SQL anteriores preservadas.
- `openspec validate adequar-catalogo-editorial-a-procedures --strict` e `git diff --check`: aprovados. Conferidos novos arquivos UTF-8 sem BOM/whitespace, CALLs somente em Repositories, ausência de dados pessoais/segredos e preservação do escopo. Sem DDL no banco de uso, alterações de visuais ou operações Git.

## Frontend e navegador da versão final

- `npm run test:coverage`: 15 arquivos/182 testes aprovados. Linhas **99,26% (1879/1893)**, branches **87,98% (1325/1506)**, sem reduzir gates. Log: `tmp/catalogo-frontend-coverage.log`.
- `python scripts/run_e2e.py`, com `RUN_MYSQL_E2E=1` e configuração transmitida somente no ambiente do processo, sem imprimir credenciais: **3 testes aprovados (1,7 min)**, incluindo vinte funcionalidades, Plano/Simulado e privacidade. Código de saída 0; schema descartável e processos locais removidos. Log: `tmp/catalogo-e2e.log`. Nenhuma alteração visual foi necessária.

## Resultado da aplicação

- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; python backend/tests/run_backend_coverage.py`: **183 unitários + 158 integrações MySQL aprovados**, incluindo as 29 originais, sem integrações puladas. Integrações: **527,152 s**. Log: `tmp/catalogo-backend-coverage.log`.
- Backend: **97,51% de linhas (4194/4301)** e **91,79% de branches (883/962)**; também aprovado o gate de arquivo executável sem cobertura.
- Frontend: **182 testes**; E2E: **3 testes**, com persistência MySQL real. Gates mantidos; sem fallback ORM, mocks/SQLite nas integrações, novas dependências ou alterações visuais.
- **11/11 tarefas concluídas.** Aplicação limitada ao inventário de 013, preservando 000–012, as onze referências SQL anteriores, 21 Models, contratos e alterações externas. As próximas changes 014–016 permanecem pendentes.

## Verificação e sincronização concluídas

| Dimensão | Resultado |
|---|---|
| Completude | 11/11 tarefas; quinze interfaces do inventário representadas |
| Correção | Cenários de contrato, autorização, disponibilidade/histórico, locks, rollback, batches e instalação comprovados pelas 158 integrações e E2E |
| Coerência | Design/ADRs/conventions preservados; entidades gerenciadas, transação externa e fronteiras modulares mantidas |

Sem achados críticos. A verificação foi somente leitura; fontes de produção conferidas como anteriores à coleta final de cobertura. Os onze hashes de recursos SQL anteriores e demais hashes protegidos foram rechecados.

Sincronizados cinco requisitos de `catalogo-editorial-mysql` e o requisito de reconhecimento/instalação de 013 em `migrations-sql`, preservando os requisitos e Purpose anteriores. `openspec validate --specs`: **13 specs aprovadas**. `openspec validate adequar-catalogo-editorial-a-procedures --strict` e `git diff --check` aprovados. As duas changes permanecem ativas, verificadas e sincronizadas; nenhum arquivamento, commit/push/merge ou DDL no banco de uso foi executado.
