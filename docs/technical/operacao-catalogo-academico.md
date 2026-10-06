# Operação do catálogo acadêmico administrativo

## Execução local

Com o MySQL 8 configurado no `.env`, execute em terminais separados:

```powershell
python backend/database/migrate.py status
python backend/database/migrate.py up
python backend/run.py
python -m http.server 5500 --directory frontend
```

Telas:

- `http://127.0.0.1:5500/admin/materias.html` — ADM-CON-001;
- `http://127.0.0.1:5500/admin/assuntos.html` — ADM-CON-002.

## Migrations e auditoria

O catálogo usa somente SQL puro em `backend/database/migrations/`:

- `003_prepare_catalogo_academico.sql`: cria Áreas, campos de status e
  normalização, faz o backfill fechado e cria o histórico de transferências;
- `004_restrict_catalogo_academico.sql`: executa prechecks e aplica `NOT NULL`,
  unicidade e foreign keys `RESTRICT`.

Antes do upgrade de um banco existente, faça e valide um backup. Depois,
execute no cliente MySQL autenticado as consultas somente leitura de
`backend/database/audits/catalogo_academico.sql`. Elas exibem apenas IDs,
nomes e causas de pendência. Classificações desconhecidas e colisões
normalizadas devem ser resolvidas explicitamente; `004` interrompe a execução
sem remover dados quando encontra qualquer pendência.

Não use Alembic nem Flask-Migrate. Não edite uma migration já aplicada.

## Rotas administrativas

Todas as rotas têm prefixo `/api`.

| Método | Rota | Finalidade |
| --- | --- | --- |
| `GET` | `/areas-enem` | Quatro Áreas fixas e ordenadas |
| `GET` | `/admin/materias` | Filtros, paginação e contagens de Matérias |
| `GET` | `/admin/assuntos` | Filtros, paginação e contagens de Assuntos |
| `GET` | `/materias/<id>/impacto-exclusao` | Impacto antes da exclusão |
| `POST` | `/materias/<id>/{inativar,arquivar,reativar}` | Ciclo de vida |
| `GET` | `/assuntos/<id>/impacto-exclusao` | Impacto antes da exclusão |
| `GET` | `/assuntos/<id>/impacto-transferencia?materia_destino_id=<id>` | Prévia da transferência |
| `POST` | `/assuntos/<id>/transferir` | Transferência atômica confirmada |
| `POST` | `/assuntos/<id>/{inativar,arquivar,reativar}` | Ciclo de vida |

As rotas legadas de Matérias, Assuntos e Questões permanecem compatíveis. Suas
listagens oferecem somente itens ativos por padrão.

## Testes

```powershell
python backend/tests/run_unit.py
npm run test:coverage

$env:RUN_MYSQL_INTEGRATION = "1"
$env:RUN_MYSQL_MIGRATION_INTEGRATION = "1"
python backend/tests/run_backend_coverage.py
Remove-Item Env:RUN_MYSQL_MIGRATION_INTEGRATION
Remove-Item Env:RUN_MYSQL_INTEGRATION
```

Os testes de integração criam e removem apenas schemas MySQL descartáveis com
nomes rigidamente validados. Não usam SQLite nem mocks de persistência.
