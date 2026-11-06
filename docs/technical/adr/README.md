# Índice de decisões arquiteturais — Pacote 1

Este índice consolida as decisões arquiteturais do projeto. A aceitação dos ADRs autoriza o direcionamento arquitetural, mas não autoriza implementação, migration ou alteração do banco.

| ADR | Título | Status | Data | Resumo da decisão |
|---|---|---|---|---|
| [ADR-001](ADR-001-estrategia-de-migrations.md) | Estratégia de migrations | **Aceito** | 2026-09-04 | Runner próprio, histórico em `schema_migrations` e migrations MySQL em SQL puro, sem Alembic ou Flask-Migrate. |
| [ADR-002](ADR-002-estrategia-de-autenticacao.md) | Estratégia de autenticação | **Aceito** | 2026-08-29 | Sessões reais no servidor, identificadas por cookie opaco e protegidas por CSRF, expiração e revogação. |
| [ADR-003](ADR-003-politica-de-exclusao-catalogo.md) | Política de exclusão do catálogo | **Aceito** | 2026-08-29 | Bloqueio de exclusão vinculada, arquivamento e transferência explícita e auditada preservam o histórico. |
| [ADR-004](ADR-004-unicidade-de-assunto.md) | Unicidade de Assunto | **Aceito** | 2026-08-29 | Assunto terá nome original e normalizado, único por Matéria inclusive diante de registro arquivado. |
| [ADR-005](ADR-005-versionamento-editorial.md) | Versionamento editorial | **Aceito** | 2026-08-29 | Conteúdo usa entidade lógica e versões; versões aprovadas ou publicadas são imutáveis e referenciadas pelo histórico. |
| [ADR-006](ADR-006-fronteira-de-transacoes.md) | Fronteira de transações | **Aceito** | 2026-08-29 | O Service delimita o caso de uso por TransactionManager/UnitOfWork, preservando Active Record e isolando a sessão na infraestrutura. |
| [ADR-007](ADR-007-armazenamento-de-midias.md) | Mídias e arquivos | **Aceito** | 2026-08-29 | StorageService abstrai armazenamento local e de objetos; o MySQL guarda metadados e `storage_key`, não os bytes por padrão. |
| [ADR-008](ADR-008-contratos-e-capacidades-de-persistencia.md) | Contratos e capacidades de persistência | **Aceito** | 2026-11-06 | Nove consultas por contratos/composição e três bases abstratas por capacidade, preservando API, Active Record e transações. |

## Pendência condicionante

O ADR-001 oficializa o runner SQL versionado com ordem, checksum, lock, baseline e bloqueio seguro após falha.
