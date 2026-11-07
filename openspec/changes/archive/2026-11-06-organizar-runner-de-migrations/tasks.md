# Tarefas: organizar o runner de migrations

## 1. Preflight e preservação

- [x] 1.1 Conferir proposta/design, AGENTS.md, conventions, ADR-001, arquitetura e spec `migrations-sql`; inventariar os símbolos de `database.migrate` usados por testes e runner. Registrar baseline não sensível, hashes das migrations/bootstrap e estado local em QA ignorado (`test-results/organizar-migrations/`) e contexto em `validacao.md`. Verificar ausência de mudanças não previstas e preservar aplicação, specs, configurações, `tmp/`, change antiga vazia e binários oficiais; não abrir/expor `.env` nem escrever no banco operacional.

## 2. Tipos compartilhados e scripts SQL

- [x] 2.1 Criar `migration_types.py` com as definições existentes de `MigrationError`/`Migration` e `sql_scripts.py` com as funções/constantes descritas no design; ajustar imports/reexportações explícitas de `migrate.py`, preservando configuração, coordenação e CLI. Conferir corpos/constantes contra o baseline e executar os unitários existentes de migrations, verificando sequência/checksum, DELIMITER/literais/comentários, execução/falha e CLI sem alterar seus asserts ou instalar dependências.
- [x] 2.2 Preservar execução direta por caminho e em pacote, com bootstrap estático de `backend` apenas quando `__package__` estiver vazio. Ampliar `backend/tests/unit/test_migrations.py` com importação sem efeitos de configuração/banco e subprocessos `--help` nos dois modos, a partir de diretório temporário, conforme o design. Executar os novos casos junto aos anteriores e acrescentar no README a responsabilidade de tipos/leitura SQL, mantendo comandos e paths oficiais.

## 3. Reconhecimento de bancos históricos

- [x] 3.1 Extrair para `legacy_schema.py` os helpers, constantes/fingerprints e reconhecimento de versões definidos no design; mover `HISTORY_TABLE` com `_user_tables`, com definição única/reexportação. Manter `run_baseline` coordenando no módulo original, sem ciclos ou reescrita de SQL/condições. Conferir corpos e hashes/fingerprints contra baseline, executar unitários de migrations/autenticação/runner e verificar que todos os consumidores seguem usando os nomes anteriores, sem alterar integrações/runners para contornar incompatibilidade.
- [x] 3.2 Completar no README a árvore e explicação curta do reconhecimento histórico versus execução; conferir links, manutenção dos comandos `status/up/baseline/reconcile` e dos limites operacionais. Revisar os quatro módulos para responsabilidades claras, imports explícitos e ausência de wrappers/framework/cópia de lógica; comprovar descoberta das migrations `000`–`009` com os mesmos checksums, sem escrever no banco.

## 4. Verificação integrada e fechamento

- [x] 4.1 Executar `python backend/tests/run_backend_coverage.py` com `RUN_MYSQL_INTEGRATION=1` e `RUN_MYSQL_MIGRATION_INTEGRATION=1` somente no processo, MySQL real e configuração segura pelos mecanismos autorizados. Conferir aprovação dos unitários, 29 integrações originais e regressões ampliadas, incluindo instalação, baseline de todos os prefixos, drift, procedure, concorrência, falha/reconciliação e equivalência do bootstrap; manter gates de 90% linhas/85% branches e nenhum executável novo zerado. Registrar comandos/resultados novos e limpeza, sem usar mocks/SQLite em integrações ou apresentar evidência histórica como execução atual.
- [x] 4.2 Executar os dois testes de navegador pelo runner E2E oficial (`RUN_MYSQL_E2E=1 npm run test:e2e`, com opt-in apenas no processo e configuração por ambiente), verificando integração da API Python de migrations com o runner intacto, os vinte casos anteriores e o percurso Plano/Simulado. Confirmar remoção do schema descartável e encerramento dos processos; registrar limitações/bloqueios reais e nunca apontar execução ao banco operacional.
- [x] 4.3 Aplicar `openspec-verify-change`, executar `openspec validate organizar-runner-de-migrations --strict`, conferir links/whitespace e comparar hashes com o baseline. Consolidar em `validacao.md` escopo de seis arquivos e artefatos da change, responsabilidades finais e preservação de migrations SQL/bootstrap, contratos, histórico, aplicação/frontend, testes anteriores, runners, dependências, CI, specs e visuais. Resolver achados críticos da extração antes de concluir; descoberta que exija alterar comportamento deve revisar o escopo em vez de corrigir silenciosamente.

## Workflow follow-up

- Sync de specs não aplicável: `skip_specs: true`, refatoração interna sem deltas funcionais.
- Arquivar pela skill apropriada somente após tarefas concluídas e verificação sem achados críticos; conferir os links relativos da documentação no destino arquivado.
- Commit/push/merge, implantação AWS, guia de estudo, slides e vídeo permanecem fora desta change.
