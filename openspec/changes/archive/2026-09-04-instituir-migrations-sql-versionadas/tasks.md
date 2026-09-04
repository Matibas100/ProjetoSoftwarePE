## 1. Contratos de arquivos e configuração

- [x] 1.1 Fixar UTF-8/LF para `backend/database/**/*.sql` em `.gitattributes` e verificar com `git ls-files --eol backend/database`.
- [x] 1.2 Implementar leitura segura de `DATABASE_URL` ou variáveis `DB_*`, seleção explícita do schema e mensagens sem valores sensíveis; verificar casos válidos, ausentes e inválidos em testes unitários.
- [x] 1.3 Implementar descoberta de `NNN_descricao_em_snake_case.sql`, sequência consecutiva, rejeição de duplicidade/lacuna/versão retroativa e SHA-256 canônico; verificar todas as regras em testes unitários.

## 2. Parser e executor SQL

- [x] 2.1 Implementar divisão de instruções com `DELIMITER`, aspas, crases e comentários, recusando comandos de cliente não permitidos; verificar procedimentos e casos-limite em testes unitários.
- [x] 2.2 Implementar execução sequencial e drenagem de resultados pelo PyMySQL, sem Alembic, Flask-Migrate ou nova dependência; verificar sucesso e interrupção no primeiro erro com testes unitários.
- [x] 2.3 Remover `USE plataforma_enem` das migrations oficiais e garantir que todo SQL opere somente no schema configurado; verificar os arquivos e a seleção do banco em teste MySQL isolado.

## 3. Histórico, lock e falhas

- [x] 3.1 Criar `schema_migrations` InnoDB com versão, arquivo, descrição, checksum, estado, tentativas e datas; verificar criação repetível e constraints em MySQL 8 real.
- [x] 3.2 Implementar a máquina `RUNNING`/`APPLIED`/`FAILED`, registrando início antes do SQL e sucesso apenas ao final; verificar sucesso, erro e interrupção simulada em testes unitários e de integração.
- [x] 3.3 Implementar validação integral do prefixo aplicado e bloqueio por drift, arquivo ausente, estado inconclusivo ou falho; verificar que nenhum SQL pendente roda após inconsistência.
- [x] 3.4 Implementar `GET_LOCK`/`RELEASE_LOCK` por schema, com timeout e liberação em `finally`; verificar concorrência entre duas conexões MySQL reais.
- [x] 3.5 Implementar reconciliação explícita e conservadora de execução falha, sem rollback DDL automático; verificar que exige versão, confirmação e estado permitido e que não exibe SQL ou credenciais.

## 4. Sequência histórica e baseline

- [x] 4.1 Criar `000_create_mvp_schema.sql` com o estado anterior às migrations legadas e verificar que `000 -> 001 -> 002` funciona em schema MySQL 8 vazio.
- [x] 4.2 Implementar fingerprints dos estados `000`, `000..001` e `000..002` usando `information_schema`; verificar tabelas, colunas, índices, checks, FKs e Stored Procedure em integrações reais.
- [x] 4.3 Implementar baseline confirmado que registra apenas o prefixo comprovado e não altera tabelas funcionais ou dados; verificar adoção dos três estados e recusa de schema divergente.
- [x] 4.4 Comparar o resultado consolidado das migrations com `create_database.sql` e verificar equivalência estrutural e funcionamento de `sp_questoes_por_assunto`.

## 5. Interface operacional

- [x] 5.1 Implementar `backend/database/migrate.py` com `status`, `up`, `baseline` e reconciliação, códigos de saída consistentes e ajuda; verificar cada comando em testes de CLI.
- [x] 5.2 Adicionar atalhos operacionais ao `Makefile` sem acoplar migrations ao startup Flask; verificar que os alvos encaminham argumentos e códigos de saída corretamente.
- [x] 5.3 Garantir que logs informem schema, versão e estado necessários, mas nunca senha ou URL autenticada; verificar sanitização com credenciais sentinela em testes.

## 6. Testes e regressão

- [x] 6.1 Adicionar infraestrutura de teste com schema descartável de nome estritamente validado e opt-in explícito antes de criação/limpeza; verificar que ela recusa qualquer alvo não seguro e nunca usa SQLite ou mocks na integração.
- [x] 6.2 Cobrir instalação vazia, idempotência, baseline, checksum, ordem, falha, interrupção, lock e Stored Procedure em MySQL 8 real; verificar com o runner de integração autorizado.
- [x] 6.3 Executar as 29 integrações originais e os testes adicionais atuais após a adoção, registrando quantidade e resultado sem declarar sucesso se o MySQL estiver indisponível.
- [x] 6.4 Executar `python backend/tests/run_unit.py`, `python backend/tests/run_backend_coverage.py` e `npm run test:coverage`, confirmando os gates de 90% de linhas e 85% de branches por stack.

## 7. Decisão e documentação

- [x] 7.1 Atualizar ADR-001 para `ACEITO` com runner SQL como decisão final e alinhar índice de ADRs, pacote/mapa de impactos e `open-decisions-v1.md`; verificar que não resta pendência por Alembic.
- [x] 7.2 Atualizar README com instalação vazia, `status`, `baseline`, `up`, lock, privilégios, backup e recuperação de falhas; revisar que nenhum exemplo contém credencial real.
- [x] 7.3 Validar a change com `openspec validate instituir-migrations-sql-versionadas --strict` e revisar o diff final para confirmar ausência de mudanças em contratos HTTP, Models, dados e artefatos visuais.
