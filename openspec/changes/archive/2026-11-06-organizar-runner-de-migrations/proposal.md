# Proposta: organizar o runner de migrations

## Why

`backend/database/migrate.py` concentra cerca de 1.275 linhas de configuração, leitura de SQL, execução, histórico e reconhecimento de bancos antigos. Separar a leitura dos scripts e a inspeção histórica facilita localizar e explicar responsabilidades, preservando a infraestrutura validada e as proteções aprovadas no ADR-001.

## What Changes

- Manter `migrate.py` como entrada dos comandos `status`, `up`, `baseline` e `reconcile`, além da API Python já usada pelos testes e pelo runner E2E.
- Extrair leitura/validação/separação dos scripts para `sql_scripts.py` e reconhecimento de estruturas históricas para `legacy_schema.py`, ambos em `backend/database/`.
- Compartilhar somente `MigrationError` e o registro `Migration` em `migration_types.py`, para permitir dependências sem ciclos. Reutilizar as classes existentes, sem framework ou hierarquia nova.
- Preservar assinaturas, mensagens, códigos de saída, ordem de execução, caminhos, checksums, locks, estados de falha e critérios de baseline, inclusive os fingerprints existentes.
- Complementar os testes de migrations com verificações de execução direta/importação e atualizar brevemente o README para mostrar a divisão de responsabilidades.

### Fora de escopo

Remover validações; reescrever algoritmos SQL; alterar o reconhecimento de versões; instalar Alembic/Flask-Migrate; criar um framework; mudar migrations SQL, bootstrap, schema, dados, procedure, contratos HTTP, camadas da aplicação ou frontend. Não incluir AWS, guia de estudo, apresentação, commit/push/merge ou publicação. Reduzir o arquivo principal não significa eliminar as regras nem tornar toda a infraestrutura obrigatória na disciplina.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. `migrations-sql` já especifica os comportamentos preservados. A change usa `skip_specs: true` porque altera somente organização interna, testes e documentação, sem novo contrato funcional.

## Impact

- Produção: `backend/database/migrate.py` e três novos módulos adjacentes: `migration_types.py`, `sql_scripts.py`, `legacy_schema.py`. Sem novos diretórios estruturais ou dependências.
- Testes/documentação: ampliar `backend/tests/unit/test_migrations.py` e atualizar README. Integrações existentes e `scripts/run_e2e.py` permanecem consumidores da API de `database.migrate`, sem mudanças para contornar incompatibilidades.
- Módulo afetado: infraestrutura de banco, separada do percurso Frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL. Nenhuma tela ou rota é alterada; SQL operacional de migrations permanece na infraestrutura e consultas da aplicação continuam nos Repositories.
- Decisões preservadas: ADR-001, arquitetura mestre, regressão original, snapshots/versionamento e demais decisões do projeto. Não reescrever ADR histórico para registrar uma extração interna.
- Dependências: ambiente Python/MySQL/Chromium já existente. A validação deverá incluir unitários, cobertura backend com integrações/migrations no MySQL real e os dois E2E no schema descartável. Não escrever no banco operacional nem exibir `.env`/credenciais.
- Preservação: arquivos SQL e bootstrap idênticos por SHA-256; restante da aplicação, testes anteriores, runner/CI/configurações e trabalho legítimo local preservados. Problema funcional identificado durante a extração exige registro e revisão de escopo, sem correção silenciosa.
