## Why

O banco da Plataforma ENEM ainda evolui por scripts SQL executados manualmente, sem registro confiável de versão, ordem ou integridade. A infraestrutura oficial precisa tornar essas mudanças reproduzíveis e auditáveis no MySQL 8, preservando o schema, os dados e o comportamento já validados no MVP.

## What Changes

- Instituir um runner mínimo em Python, apoiado apenas nas dependências MySQL já existentes, para orquestrar migrations escritas exclusivamente em SQL puro.
- Versionar e executar arquivos SQL em ordem determinística, rejeitando versões duplicadas, arquivos inválidos e inserções retroativas no histórico.
- Criar e manter `schema_migrations` com versão, arquivo, checksum SHA-256, estado e datas da execução.
- Impedir reexecução, alteração ou desaparecimento de migrations já aplicadas por meio da conferência de histórico e checksum.
- Serializar execuções concorrentes com lock consultivo do MySQL e bloquear o avanço após execução interrompida ou malsucedida até reparo explícito.
- Suportar Stored Procedures e diretivas `DELIMITER`, preservando `sp_questoes_por_assunto` e seu acesso exclusivo pelo Repository.
- Adotar com segurança bancos existentes: validar o schema MVP antes de registrar o baseline, sem reaplicar cegamente as migrations legadas `001` e `002` nem alterar dados.
- Permitir que um banco vazio alcance o mesmo estado consolidado por uma sequência completa de migrations.
- Manter `create_database.sql` como snapshot de bootstrap compatível e validar sua equivalência com o resultado das migrations.
- Atualizar ADR-001 e documentos derivados para oficializar o runner SQL como decisão final, sem Alembic ou Flask-Migrate.
- Documentar operação, falhas, recuperação, irreversibilidade e uso sem exposição de credenciais.
- Ampliar testes unitários e de integração MySQL para a infraestrutura, preservando as 29 integrações originais e toda a suíte automatizada atual.

Fora de escopo:

- Alterar contratos HTTP, funcionalidades, telas, Models ou regras de negócio do MVP.
- Introduzir Alembic, Flask-Migrate ou outra biblioteca de migrations.
- Automatizar downgrade destrutivo; reversões serão tratadas por backup ou migration compensatória documentada.
- Aplicar futuras mudanças de domínio previstas na Modelagem Mestre.

## Capabilities

### New Capabilities

- `migrations-sql`: Descoberta, validação, execução, baseline, auditoria e tratamento de falhas das migrations SQL versionadas no MySQL.

### Modified Capabilities

Nenhuma. Ainda não existem capabilities principais publicadas em `openspec/specs/`.

## Impact

- **Código e scripts:** `backend/database/`, testes do backend, comandos operacionais, `Makefile`, `.gitattributes` e documentação de preparação do banco.
- **Banco:** nova tabela técnica `schema_migrations`; nenhuma alteração funcional nas tabelas `materias`, `assuntos` e `questoes` nem nos dados existentes.
- **Stored Procedure:** `sp_questoes_por_assunto` continuará disponível e chamada somente por `QuestaoRepository`.
- **API e telas:** nenhuma rota, resposta HTTP ou artefato visual será alterado.
- **Dependências:** nenhuma nova dependência; o runner reutilizará PyMySQL e a configuração MySQL atual, sem registrar ou exibir credenciais.
- **Decisões:** ADR-001, índice de ADRs, pacote/mapa de decisões e registro de decisões abertas deverão refletir a escolha definitiva pelo runner SQL.
- **Compatibilidade:** instalações vazias e bancos MVP existentes deverão convergir para o mesmo schema; as 10 funcionalidades, os 29 testes de integração originais e a suíte ampliada permanecerão como regressão obrigatória.
