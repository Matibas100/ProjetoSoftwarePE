# ADR-001 — Estratégia de migrations

## 1. Status

**ACEITO**

## 2. Data da decisão

2026-08-29

Decisão final atualizada em 2026-09-04.

## 3. Contexto

O MVP usa MySQL 8, Flask-SQLAlchemy e três scripts SQL: um baseline em `create_database.sql` e duas migrations manuais, uma para a FK de Questão e outra para `sp_questoes_por_assunto`. Não existe tabela de controle de versão, runner formal, downgrade automatizado ou verificação de ordem. A Modelagem Mestre ampliará o schema sem poder perder os dados atuais.

## 4. Problema

Definir um mecanismo reproduzível para criar e evoluir tabelas, colunas, índices, constraints e recursos específicos do MySQL em ambientes diferentes, preservando o banco existente e a Stored Procedure.

## 5. Restrições do projeto e da disciplina

- MySQL e Flask-SQLAlchemy são obrigatórios.
- Stored Procedures devem continuar encapsuladas por Repository na aplicação.
- O histórico precisa ser apresentável e auditável pelo professor.
- `create_database.sql`, dados atuais e 29 testes precisam permanecer aproveitáveis.
- Esta proposta não instala ferramenta nem autoriza migration.

## 6. Opções analisadas

- **A — Flask-Migrate/Alembic:** revisions Python geradas e revisadas para o schema SQLAlchemy.
- **B — Runner próprio:** scripts SQL numerados, checksum, tabela de controle e execução ordenada.
- **C — Híbrido:** Alembic para tabelas/colunas/índices/constraints e scripts SQL versionados para procedures e recursos MySQL.
- **D — Scripts manuais:** execução humana sem runner nem controle formal.

## 7. Vantagens de cada opção

- **A:** histórico padrão, upgrade/downgrade, integração com Models e ecossistema Flask.
- **B:** SQL explícito, controle total do MySQL e demonstração direta ao professor.
- **C:** combina rastreabilidade do Alembic com fidelidade para procedures, delimitadores e SQL específico.
- **D:** menor preparação inicial e continuidade imediata do formato atual.

## 8. Desvantagens de cada opção

- **A:** autogenerate não compreende toda semântica de procedures e exige revisão humana; adiciona ferramenta.
- **B:** runner, locks, checksums, falhas parciais e downgrade teriam de ser projetados e mantidos pela equipe.
- **C:** exige convenção rigorosa para não executar a mesma mudança por dois mecanismos.
- **D:** não garante ordem, idempotência, ambiente aplicado ou rollback; aumenta risco operacional.

## 9. Riscos

Autogenerate destrutivo não revisado; divergência entre metadata e banco; script procedural parcialmente aplicado; downgrade que perde dados; baseline diferente entre banco novo e existente; duas fontes de verdade no modelo híbrido.

## 10. Impacto no MVP atual

O MVP permanece intacto. `create_database.sql` pode continuar como baseline de instalação limpa enquanto o banco existente é marcado em uma revisão-base após auditoria. As migrations `001` e `002` precisam ser reconhecidas no histórico futuro sem serem reexecutadas cegamente.

## 11. Impacto nas 60 telas

Não há mudança visual direta. Todas as telas dependem indiretamente de implantações consistentes; telas administrativas de importação, revisão, usuários e conteúdo sofreriam mais com schema divergente.

## 12. Impacto no MySQL

Passará a existir, se aprovado, um histórico versionado e uma regra de baseline. Procedures, views ou triggers continuarão em SQL explícito. Toda migration deverá declarar pré-condições, preservação/backfill e estratégia de rollback ou irreversibilidade justificada.

## 13. Impacto na API

Nenhum contrato atual muda por esta decisão. Evoluções de API só podem depender de schema após a migration correspondente estar aplicada e validada.

## 14. Impacto nos testes

Será necessário testar instalação do zero, upgrade de uma cópia do MVP, idempotência operacional, schema resultante e execução das procedures. Os 29 testes permanecem como regressão obrigatória após cada evolução.

## 15. Impacto em segurança

Credenciais não entram em scripts. O executor deve usar privilégio mínimo, registrar versão/checksum sem registrar segredos e impedir execução concorrente da mesma migration.

## 16. Recomendação técnica

Fica aceita a **opção B — runner próprio com migrations MySQL em SQL puro**:

- `backend/database/migrate.py` será o único runner oficial;
- arquivos `NNN_descricao_em_snake_case.sql` formarão uma sequência única e consecutiva;
- `schema_migrations` registrará versão, arquivo, checksum SHA-256, estado e datas;
- ordem, reexecução, drift e concorrência serão verificados antes de qualquer migration pendente;
- `GET_LOCK` serializará runners oficiais por schema;
- Stored Procedures e outros recursos específicos do MySQL permanecerão em SQL explícito com suporte a `DELIMITER`;
- bancos existentes serão adotados somente por baseline explícito após fingerprint do estado histórico;
- `create_database.sql` permanecerá como snapshot consolidado e deverá ser equivalente à sequência;
- falha ou interrupção bloqueará o avanço até reconciliação consciente;
- migrations críticas exigirão backup e validações pré e pós-execução.

Alembic e Flask-Migrate não serão utilizados.

## 17. Consequências da recomendação

O projeto passa a manter o próprio runner pequeno e seus testes. Não haverá downgrade automático: reversões usarão restauração de backup ou migration compensatória documentada. `create_database.sql` não será alterado isoladamente e deverá representar o mesmo estado final das migrations.

## 18. Estratégia de adoção gradual

1. Criar e testar o runner sem acoplá-lo ao startup Flask.
2. Formalizar a migration `000` e incorporar `001` e `002` ao histórico.
3. Validar banco vazio e equivalência com `create_database.sql`.
4. Fazer backup e ensaiar o baseline em cópia do MVP.
5. Adotar o histórico no banco existente sem reexecutar DDL comprovado.
6. Executar regressão antes de cada merge.

## 19. Critérios de aceite

- Um banco vazio e um banco MVP chegam ao mesmo schema esperado.
- A versão aplicada é consultável e ordenada.
- `sp_questoes_por_assunto` continua funcional.
- Nenhuma credencial é versionada.
- Upgrade é repetível; rollback ou irreversibilidade é documentado.
- Os 29 testes continuam aprovados.

## 20. Pontos operacionais

Cada ambiente deverá definir responsáveis por backup, revisão dos scripts e autorização do baseline. Toda migration futura deverá registrar pré-condições, preservação/backfill e irreversibilidade ou compensação, sem alterar a decisão pela infraestrutura SQL.

## 21. Decisão final

**ACEITO — runner próprio com migrations MySQL em SQL puro, sem Alembic ou Flask-Migrate.**
