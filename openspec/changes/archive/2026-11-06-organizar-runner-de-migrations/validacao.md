# Validação: organizar o runner de migrations

## Preflight — 6 de novembro de 2026

- Lidos proposta, design, tarefas, AGENTS.md, cinco conventions, arquitetura mestre, ADR-001 e spec `migrations-sql`.
- Estado inicial: apenas esta change, `mover-join-assuntos-para-repository/` e `tmp/` não rastreados; sem alterações rastreadas. A pasta antiga vazia também será preservada.
- Baseline não sensível em `test-results/organizar-migrations/`, ignorado pelo Git: hashes SHA-256 de 406 arquivos rastreados, cópias dos três arquivos existentes no escopo, estado Git, inventário de nove consumidores e checksums das migrations `000`–`009`.
- Inventário inclui `DatabaseSettings` importado diretamente pelo unitário do runner, helpers privados, fingerprints e pontos de patch da CLI em `database.migrate`.
- Nenhum `.env` foi aberto, nenhuma configuração sensível foi exibida e nenhuma escrita no MySQL foi executada no preflight.
- Configuração MySQL inicialmente ausente no ambiente do processo. Após o usuário delegar a escolha, foi usado o loader existente, com repasse somente ao ambiente dos processos de teste. Nenhum conteúdo de `.env` foi exibido ou persistido nos registros.

## Escopo e resultados

O delta de produto/teste/documentação contém exatamente seis arquivos:

| Arquivo | Responsabilidade final |
| --- | --- |
| `backend/database/migrate.py` | Configuração/conexão, histórico, locks, coordenação e CLI; reexportações explícitas preservam consumidores. |
| `backend/database/migration_types.py` | Definições únicas e inalteradas de `MigrationError` e `Migration`. |
| `backend/database/sql_scripts.py` | Leitura, canonicalização/checksum, descoberta, parser, validação e execução de instruções SQL. |
| `backend/database/legacy_schema.py` | Reconhecimento histórico, helpers, fingerprints e definição única de `HISTORY_TABLE`. |
| `backend/tests/unit/test_migrations.py` | Três testes novos de importação isolada e CLI por caminho/pacote, fora da raiz. |
| `README.md` | Árvore e explicação curta da separação, preservando comandos e limites operacionais. |

## Execuções atuais — 6 de novembro de 2026

Python da `.venv` existente, sem instalação de dependências. MySQL real 8.0.44.

1. Após extrair tipos/scripts: `.venv/Scripts/python.exe -m unittest discover -s backend/tests/unit -p test_migrations.py -v`, com `PYTHONPATH=backend` e dotenv desabilitado somente no processo: **15 testes anteriores aprovados**.
2. Com os testes novos e após extração histórica: mesmo comando de migrations, mais descobertas `-p test_autenticacao.py` e `-p test_e2e_runner.py`, com configuração fictícia e dotenv desabilitado: **18 + 10 + 6 aprovados**. A importação dos três módulos novos e do runner é verificada com carregamento de configuração, conexão e CLI bloqueados por mocks exclusivamente unitários.
3. `.venv/Scripts/python.exe backend/tests/run_backend_coverage.py`, pelo invólucro QA ignorado `test-results/organizar-migrations/run_validation.py backend`, que repassa configuração e `RUN_MYSQL_INTEGRATION=1`/`RUN_MYSQL_MIGRATION_INTEGRATION=1` apenas ao processo: **145 unitários + 115 integrações aprovados**, saída 0. Inclui a regressão original e ampliada, instalação, baseline de todos os prefixos, drift/fingerprints, procedure, lock concorrente, falha/reconciliação e equivalência do bootstrap. Conferidos individualmente todos os casos atuais dos três módulos originais: **7 Matéria + 10 Assunto + 13 Questão**. A referência histórica a 29 integrações permanece preservada; o arquivo atual de Questão já continha 13 casos antes desta change.
4. Cobertura validada pelo gate oficial intacto: **97,46% de linhas (3608/3702)** e **91,24% de branches (812/890)**. Limites 90%/85% preservados; nenhum executável de produção zerado, incluindo os módulos extraídos.
5. Limpeza do backend: lista de schemas descartáveis vazia antes e depois. Somente os schemas aleatórios validados pelos runners receberam escritas; nenhuma operação `up`, `baseline` ou `reconcile` foi apontada ao banco operacional.
6. `npm run test:e2e`, pelo mesmo invólucro QA no modo `e2e`, com `RUN_MYSQL_E2E=1` somente no processo e configuração repassada por ambiente ao runner intacto: **2 testes Playwright aprovados em 34,8 s**, saída 0. Exercitados os vinte casos anteriores e o percurso Plano/Simulado, com persistência real e migrations oficiais.
7. Limpeza do E2E: schema descartável removido pelo `finally`; listas de schemas vazias antes/depois. Comparação dos processos Python/Node antes/depois: **zero processos novos remanescentes**. Nenhum trace, HAR, vídeo ou storage state foi solicitado.

Logs sanitizados e resultados JSON ficam em `test-results/organizar-migrations/`, ignorado. Os resultados acima são desta execução, não evidência histórica.

## Preservação e revisão estática

- Comparação por AST das **51 definições/constantes originais**, incluindo assinaturas, decorators, condições, SQL e fingerprints: idênticas, sem duplicação. Só importações, docstrings de módulo, comentário de bootstrap e organização foram acrescentados.
- Comparação AST das classes anteriores de testes: integralmente preservadas. Consumidores existentes continuam resolvendo seus nomes em `database.migrate`, incluindo `DatabaseSettings`, helpers privados e fingerprints, sem editar integrações/runners.
- Descoberta de `000`–`009` com os mesmos nomes e checksums; migrations SQL e bootstrap preservados por SHA-256.
- **403 arquivos rastreados fora do delta intactos por SHA-256**, incluindo aplicação/frontend, testes anteriores fora do arquivo ampliado, runners, configurações, dependências, CI, specs, ADRs e binários visuais oficiais. `tmp/`, a outra change e a pasta antiga vazia não foram editados.
- Imports explícitos, dependências sem ciclos, sem wrappers/framework, sem novos diretórios estruturais ou dependências. `run_baseline` e pontos de patch da CLI continuam no runner original; bootstrap de `backend` só quando `__package__` está vazio.
- Links relativos do README e dos artefatos ativos válidos. `git diff --check` aprovado.
- `openspec validate organizar-runner-de-migrations --strict` aprovado; `skip_specs: true` reconhecido pelo CLI. Sync não aplicável, sem deltas funcionais.

## Verificação OpenSpec

Aplicada a skill `openspec-verify-change`: revisão somente leitura dos artefatos, implementação, contratos preservados, evidências dos testes e design. Depois da revisão, o registro e a tarefa de fechamento foram atualizados como previsto no apply autorizado.

| Dimensão | Resultado |
| --- | --- |
| Completude | Oito tarefas atendidas, incluindo regressões MySQL/E2E, documentação e preservação. |
| Correção | 145 unitários, 115 integrações e 2 E2E aprovados; gates oficiais mantidos e satisfeitos. |
| Coerência | Quatro módulos conforme o design, definições/SQL/fingerprints inalterados, API Python e comandos preservados, sem mudança de contrato/schema. |

**Sem achados críticos ou avisos bloqueantes.** A contagem histórica de 29 não foi usada para limitar a descoberta atual: os 30 casos existentes nesses três módulos passaram e seus arquivos permanecem idênticos ao baseline. `openspec validate --strict`, links relativos, UTF-8 e whitespace aprovados.

Change arquivada em `2026-11-06-organizar-runner-de-migrations` pelo CLI OpenSpec, com oito tarefas concluídas e links relativos ajustados e conferidos no destino. Sync não aplicável (`skip_specs: true`), sem alteração das specs principais. Sem bloqueios de ambiente. Suíte DOM/cobertura frontend não repetida, conforme design, pois o frontend foi preservado. Não houve commit, push, merge ou publicação.
