# Validação — Plano de Estudos por procedures

## Preflight — 08/11/2026

- Schema `spec-driven`; 0/11 tarefas no início. Change 014 aplicada/verificada/sincronizada/arquivada em `archive/2026-11-08-adequar-praticas-simulados-a-procedures`, conforme relatório e spec principal. Versão 015 livre; nenhuma aplicação simultânea.
- Estado inicial completo e hashes dos arquivos preexistentes em `tmp/plano-status-inicial.txt` e `tmp/plano-baseline.json` (evidência local). Alterações externas de 011–014, catálogo, desempenho, práticas/simulados, infraestrutura/testes e documentação preservadas. Sem leitura de `.env`, exposição de credenciais ou DDL no banco de uso.
- Inventário: `atual`/`por_chave` → gerar/recalcular/consultar; `itens` → `plano_dto`; `item_proprio` → concluir; `pares_elegiveis_plano` de Conteúdo → seleção e DTOs pela API pública; `eliminar_planos_proprios` → participante injetado em recusa/revogação de Contas. Contratos HTTP, 21 Models e lock de identidade não mudam.
- Lidos proposal, design, duas delta specs, tasks, inventário, AGENTS, cinco conventions, architecture-master e ADRs 001/009/010/011. Aplicadas as quatro orientações do CLI: preflight somente leitura, escopo mínimo, pausa para conflito de design e conclusão somente com validação.

### SHA-256 dos SQLs anteriores

| Arquivo | SHA-256 inicial |
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
| `backend/database/migrations/013_catalogo_editorial_procedures.sql` | `8db9ea8917cb621d68ce9679828fc1a3f5dcd9364b51ca3dfd0a702e2bc1d2dd` |
| `backend/database/migrations/014_praticas_simulados_procedures.sql` | `fb63b6c3ba688157dd9e48cecb1ab89a31408c0b0020d9c754e0b31359d951a9` |

## Caracterização e conversão

- `RUN_MYSQL_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_plano_procedures_integration -v`: **2 testes aprovados**, 5,358 s, antes da conversão (`tmp/plano-caracterizacao.log`). MySQL real/sintético: tipos JSON/Boolean/DATETIME(6), JOIN textual de CALL com identidade gerenciada, leitura corrente, vazio, cursor fechado, conexão reutilizada e mutação/rollback na mesma sessão.
- Após a conversão: `python -m unittest tests.test_plano_procedures_integration tests.test_planos_integration tests.test_privacidade_integration -v`: **23 testes aprovados**, 34,185 s (`tmp/plano-conversao.log`). Inclui três prioridades determinísticas, falta de base, replay/histórico, 404 alheio, autorização, conclusão imutável, snapshot/instante externo, rollback de geração/negativa e concorrência. Sem SQLite/mocks nas integrações.
- Seis routines estáticas; cinco READS SQL DATA e uma MODIFIES SQL DATA, todas SQL SECURITY INVOKER. Repositories usam parâmetros vinculados, mesma sessão/conexão e fechamento em finally/helper existente. Services/Models/diagnóstico/DTOs/rotas permanecem intactos: permissão após lock de Contas precede qualquer derivado. Ranking/limite de três e escrita individual continuam nos Services/Models.
- Eliminação: cursor de gerações decrescente FOR UPDATE; itens antes de cada geração, dono repetido no DELETE. Sem controle transacional interno. Expiração seletiva das entidades derivadas carregadas, inclusive item isolado, preserva evidências pendentes e rollback do chamador. O participante continua sem retorno HTTP/endpoint.
- As 42 referências SQL anteriores foram conferidas e preservadas; seis novas derivadas somente por execução das migrations oficiais em schema descartável. Durante desenvolvimento corrigidos posicionamento de DELIMITER exigido pelo parser e rejeição explícita de JSON null, antes de concluir os gates.

## Regressões específicas e instalação

- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_plano_procedures_integration tests.test_plano_procedures_migrations_integration -v`: **12 testes aprovados**, 62,597 s (`tmp/plano-procedures.log`).
- Inclui FOR SHARE concorrendo com publicação/transferência, revogação concorrente com recálculo/conclusão, entidades correntes, contagens de duas gerações/itens e RESTRICT, outra conta, expiração seletiva/item isolado e rollback. Ausência de cada leitura gera HTTP 500 seguro; 403 precede CALL de qualquer derivado/diagnóstico. Regressões existentes também exercitam falha MySQL após exclusão de itens, evidências/respostas preservadas e replay antigo após nova autorização.
- Instalação vazia e bootstrap equivalentes, upgrade 014→015 com plano/item sintéticos, baseline/restauração e repetição zero. Ausência/corpo/assinatura/segurança/dependência divergentes rejeitados. O runner rejeita drift de tabela/legada/014 e indícios parciais/completos de 015 antes de RUNNING/DDL, conserva dados/histórico/objetos e libera lock; reparação permite upgrade. Validação de listas/flags/IDs e conexão após erros reais cobertas. Metadados indisponíveis permanecem protegidos pela infraestrutura/gates existentes.
- Regressões de 014 mantêm seu recorte fixado até 014; gerais/restauração/privacidade ampliam as expectativas até 015, sem remover prefixos anteriores. Bootstrap somente acrescenta definições da 015; conteúdo anterior preservado, com normalização de finais de linha.
- README, documento SQL, ADR-011 e matrizes acadêmica/CRUD atualizados. Conferidos links locais, seis correspondências/proprietários/rotas/Services/telas e vinte IDs sem renumeração. Contas permanece reservada à 016; nenhuma promessa de aceite acadêmico.

## Frontend, navegador e revisão

- `npm run test:coverage`: **15 arquivos / 182 testes aprovados**. Linhas **99,26% (1879/1893)**; branches **87,98% (1325/1506)**; gates preservados (`tmp/plano-frontend-coverage.log`).
- `scripts.run_e2e.executar_suite(settings, ambiente)` com `RUN_MYSQL_E2E=1`: **3 E2Es aprovados**, 52,7 s, saída 0 (`tmp/plano-e2e.log`). Configuração existente transmitida somente no ambiente, sem imprimir credenciais. Vinte funcionalidades, geração/conclusão/recálculo de Plano, Simulado e privacidade com persistência MySQL real. Runner removeu schema/processos descartáveis.
- `openspec validate adequar-plano-estudos-a-procedures --strict`, `git diff --check` e auditoria de escopo/links/UTF-8/hashes: aprovados até aqui. Migrations 000–014, Models/guards, contratos, hashes legais, frontend e visuais conservam os hashes iniciais. CALLs de produção acrescentados somente nos Repositories; sem novo endpoint ou DDL no banco de uso.
- O relatório foi regravado em UTF-8 após detectar conversão de acentos pelo pipe do PowerShell. Fontes novos são UTF-8; SQL e referências gerados a partir de arquivos UTF-8, sem converter textos SQL pelo pipe.
- Os três schemas vazios deixados pelo preflight da primeira tentativa (erro de DELIMITER) foram removidos nesta sessão após conferir seus identificadores descartáveis, janela exata da criação, prefixo 014 e ausência de contas. Os schemas das execuções posteriores e do E2E foram limpos pelas fixtures/runners. Nenhuma limpeza alcançou banco de uso ou schema de outra tarefa.
- Revisão final de 5.2: `openspec validate ... --strict` e `git diff --check` aprovados; conferidos os 15 hashes de migrations anteriores, frontend/legais/visuais, contratos e Models/guards. Somente Repositories de Plano e elegibilidade de Conteúdo, definição/reconhecimento/preflight da 015, regressões e cinco documentos do recorte foram alterados, além dos artefatos desta change. Alterações externas mantidas; sem segredos nos fontes novos, alteração de contrato, operação Git ou DDL no banco de uso.

## Resultado da aplicação

- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; python backend/tests/run_backend_coverage.py`: **183 unitários + 184 integrações MySQL aprovados**, sem integrações puladas, saída 0 (`tmp/plano-backend-coverage.log`). Unitários em **2,566 s**, integrações em **587,588 s**; incluídas as 29 originais, gates de arquitetura, Plano, Privacidade, Desempenho, todas as migrations e suíte ampliada.
- Cobertura backend: **97,57% de linhas (4297/4404)** e **91,96% de branches (892/970)**; gate de arquivo executável sem cobertura aprovado. Frontend: **182 testes**, **99,26% de linhas / 87,98% de branches**. Navegador: **3 E2Es** com MySQL real. Nenhum gate reduzido.
- Os **13 testes novos** estão incluídos na execução completa: oito de procedures/Plano (incluindo falha MySQL após desativar a geração e criar a sucessora, revertendo toda a troca) e cinco de instalação/reconhecimento. Preservados locks, permissão antes de derivados, snapshot/instante, identidade gerenciada, replay, guards e transação única da negativa.
- **11/11 tarefas concluídas**, schema `spec-driven`: seis procedures, migration/bootstrap 015, Repositories, reconhecimento/preflight, regressões e documentação implementados. Banco de uso não migrado; disponibilizar o código nesse ambiente exige aplicar e validar a 015 previamente, conforme operação documentada.
- Próxima etapa: verificar a implementação contra os artefatos; depois sincronizar os dois deltas e arquivar sem achados críticos. Esta aplicação não executou sincronização, arquivamento, commit, push, merge ou deploy.

## Verificação para fechamento — 08/11/2026

Fechamento autorizado pelo usuário após a aplicação: verificar, sincronizar e arquivar. Lidos os artefatos retornados pelo CLI, inventário e conventions; confrontados SQL, Repositories, Services, reconhecimento/preflight e testes. Conferidos os logs da execução completa recém-concluída nesta conversa; não houve nova alteração de implementação que exigisse repeti-la.

| Dimensão | Resultado |
|---|---|
| Completude | 11/11 tarefas; seis requisitos de Plano e um de migrations representados por implementação e cenários |
| Correção | 183 unitários, 184 integrações MySQL (29 originais incluídas), 182 testes frontend e 3 E2Es aprovados; cobertura e gates mantidos |
| Coerência | CALL somente nos Repositories; identidade ORM, permissão antes de derivados, locks/transação externa e participante restrito preservados; sem tabela/Model/contrato novo |

Evidências: `plano_estudo_repository.py` mapeia as quatro leituras completas e expira somente derivados afetados após eliminação; `questao_repository.py` mantém elegibilidade no proprietário Conteúdo; `015_plano_estudos_procedures.sql` implementa cinco leituras e o cursor de eliminação em ordem decrescente sem controle transacional. `migrate.run_up` verifica 014 físico íntegro sob o lock antes de RUNNING/DDL da 015; detector compara as 48 referências oficiais. Os treze testes novos e regressões de Plano/Privacidade/Desempenho cobrem tipos, vazios, replay, erros seguros, snapshots, concorrência, rollback e instalação/restauração/drift.

Reexecutados nesta etapa `openspec validate adequar-plano-estudos-a-procedures --strict`, `git diff --check` e auditoria de escopo/hashes/links/UTF-8/vinte IDs: aprovados. Os arquivos de implementação/testes permaneceram como na coleta completa da aplicação. Snapshot adicional em `tmp/plano-fechamento-snapshot.json` protege as alterações externas durante a finalização.

**Sem achados CRÍTICOS ou AVISOS bloqueantes. Pronta para sincronização e arquivamento.** Nenhum código, task ou decisão de design foi alterado durante a verificação. Banco de uso, operações Git e deploy permanecem fora deste fechamento.

## Sincronização das specs — 08/11/2026

- Criada a spec principal `plano-estudos-mysql` com os seis requisitos e Purpose original. Acrescentado o requisito do prefixo 015 em `migrations-sql`, preservando byte a byte seu conteúdo anterior, inclusive Purpose e requisitos históricos.
- Comparação integral dos dois deltas contra as specs principais: sete requisitos e seus cenários idênticos; nenhuma operação pendente. Nenhum cabeçalho de operação delta foi levado às specs principais. Aplicadas as regras atuais do CLI sobre comportamento observável, cenários testáveis e keywords normativas, sem alterar decisões.
- `openspec validate --specs`: **15 specs aprovadas**. `openspec validate adequar-plano-estudos-a-procedures --strict` e `git diff --check`: aprovados. Snapshot do fechamento confirmou preservação de implementação, testes, artefatos anteriores e demais alterações externas.
- Usuário autorizou as três etapas do fechamento. 11/11 tarefas, sem achado crítico e com deltas sincronizados; pronta para arquivar pelo CLI, sem nova confirmação. Nenhum código, banco ou operação Git alterado neste fechamento.

## Arquivamento — 08/11/2026

- `openspec archive adequar-plano-estudos-a-procedures --skip-specs --yes --json`: saída 0. O flag `--skip-specs` evitou reaplicar os dois deltas já sincronizados e comparados; não suprimiu validação.
- Arquivada em `openspec/changes/archive/2026-11-08-adequar-plano-estudos-a-procedures/`, com `.openspec.yaml` e todos os artefatos preservados. Comparação dos hashes do fechamento confirmou os demais arquivos intactos e a ausência da antiga pasta ativa.
- Workflow concluído: aplicada, verificada, sincronizada e arquivada, com **11/11 tarefas** e sem achado crítico. Specs principais validadas; sem commit, push, merge, deploy ou DDL no banco de uso.
