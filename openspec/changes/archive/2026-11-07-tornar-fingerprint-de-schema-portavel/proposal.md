# Proposta — Tornar portável a conferência estrutural do banco

## Why

O reconhecimento dos prefixos 008–010 calcula hashes do texto de `SHOW CREATE TABLE`. No ensaio de restauração de MySQL 8.0.44 para 8.0.46, a inclusão redundante de `CHARACTER SET utf8mb4` provocou recusa, embora metadados estruturais e dados fossem iguais. Isso fragiliza baseline e conferência de cópias antes da hospedagem.

## What Changes

- Substituir, somente nos reconhecimentos de Simulados, Plano e Privacidade, o hash do DDL exibido por assinatura determinística de metadados estruturais consultados no MySQL.
- Aceitar o caso conhecido de apresentação implícita/explícita de charset quando os metadados forem iguais, preservando rejeição de colunas, tipos, defaults, collations, índices, FKs, checks e expressões geradas divergentes.
- Manter tabelas esperadas, prefixos históricos, CLI e reexportações existentes. Nos prefixos 008–010, conferir também corpo e parâmetros da procedure, além da existência já verificada, conforme ajuste aprovado durante o apply. Preservar o comportamento dos validadores 000–007. Não remover a verificação nem adotar automaticamente o schema encontrado como referência.
- Cobrir a restauração estrutural em schemas descartáveis, baseline, upgrade/reexecução e diferenças reais de estrutura com testes MySQL, sem depender de `mysqldump` instalado na máquina do avaliador.
- Explicar a assinatura estrutural na documentação operacional e em adendo ao ADR-001, distinguindo-a do checksum dos arquivos SQL e do hash dos documentos legais.

### Fora de escopo

Alterar migrations 000–010, snapshot, schema ou dados existentes; criar migration 011; enfraquecer checksums/histórico, locks ou falhas bloqueantes; normalizar arbitrariamente qualquer SQL; suporte universal a versões futuras/MySQL 5/MariaDB; executar operações no banco local ou restaurar backup real durante o apply; publicar AWS; refatorar o runner inteiro; commit e push.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `migrations-sql`: reconhecer estados históricos estruturalmente equivalentes após restauração, sem confundir apresentação de DDL com mudança real, mantendo baseline conservador e proteção contra drift.

## Impact

- Principalmente `backend/database/legacy_schema.py`: helper de assinatura e referências conhecidas das dez tabelas dos prefixos 008–010. `migrate.py` apenas se necessário para preservar importações existentes, sem mudar comandos ou a fronteira de execução SQL.
- Testes unitários de migrations e integrações de Simulados/Plano/Privacidade, mais um teste integrado de round-trip estrutural utilizando fixtures oficiais e MySQL real.
- Documentação de migrations no README, operação de Plano/Privacidade e adendo ao ADR-001, sem reescrever suas decisões históricas.
- Nenhuma biblioteca, infraestrutura de produção, Model ou contrato HTTP novo. As validações estruturais anteriores a 008 permanecem no recorte atual.
- Não há migração de dados: hashes de reconhecimento são referências internas do código e não correspondem aos checksums persistidos de `schema_migrations`. Todos os arquivos SQL aplicados permanecerão idênticos.
- Aplicação sugerida depois da organização documental. As duas changes não editam a mesma capability: esta altera apenas o contrato de reconhecimento em `migrations-sql`.
