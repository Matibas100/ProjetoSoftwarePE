# Testes e validação

## Regra central

Os 29 testes originais são integrações contra o MySQL real. A suíte ampliada
também possui testes unitários Python e testes DOM com Vitest. Mocks são
permitidos somente nos testes unitários; nunca substituem as integrações.

## Regressão atual

| Recurso | Testes |
|---|---:|
| Matéria | 7 |
| Assunto | 10 |
| Questão | 12 |
| Total | 29 |

## Organização

- `backend/tests/unit/`: testes Python sem `.env` e sem conexão MySQL.
- `backend/tests/*_integration.py`: 29 integrações originais preservadas e
  complementos de regressão com MySQL 8 real.
- `frontend/tests/`: contrato HTML e testes DOM dos quatro scripts clássicos.
- `scripts/`: validadores agregados de cobertura por stack.

## Pré-requisitos de desenvolvimento

- Python 3.10 ou superior e `backend/requirements-dev.txt`.
- Node `>=22.9.0` e npm `11.6.2`; use `npm ci` com o lockfile.
- GNU Make opcional para os atalhos. Confirme com `make --version`.

## Comandos

| Alvo Make | Comando equivalente |
| --- | --- |
| `make test-unit` | `python backend/tests/run_unit.py` e `npm run test:unit` |
| `make test-integration` | `python backend/tests/run_integration.py` |
| `make test-backend` | `python backend/tests/run_backend_coverage.py` |
| `make test-frontend` | `npm run test:coverage` |
| `make test-coverage` | runner backend e `npm run test:coverage` |
| `make test` | igual a `make test-coverage` |
| `make test-e2e` | `python scripts/run_e2e.py` |

As integrações e qualquer alvo que as inclua exigem opt-in somente no processo:

```powershell
$env:RUN_MYSQL_INTEGRATION = "1"
python backend/tests/run_integration.py
Remove-Item Env:RUN_MYSQL_INTEGRATION
```

O preflight confirma conexão, tabelas e `sp_questoes_por_assunto` antes dos
testes. Nunca persista o opt-in no `.env` nem exiba configuração sensível.

Cada stack exige pelo menos 90% de linhas e 85% de branches agregados. Os
validadores também reprovam arquivo executável de produção com zero linhas
cobertas.

## Regras para changes

- Durante o apply, rode primeiro a menor validação que prove a tarefa.
- Antes de concluir uma mudança de backend, execute a regressão afetada e, quando aplicável, a suíte completa.
- Testes devem criar e limpar seus próprios dados temporários.
- Não leia nem mostre o conteúdo do `.env`.
- Não declare sucesso quando o MySQL estiver indisponível.
- Mudança somente documental ou de configuração não exige executar a suíte da aplicação.
- Registre no fechamento comandos, resultados e limitações reais.

## Navegador real

Instale as dependências com `npm ci` e o browser com
`npx playwright install chromium` (em Linux CI: `--with-deps chromium`).
`npm run test:e2e:list` apenas descobre a suíte, separada dos testes Vitest.

O E2E exige `RUN_MYSQL_E2E=1` somente no processo e configuração MySQL por
ambiente (`DATABASE_URL` ou variáveis `DB_*`). O runner não lê `.env`; cria
schema com prefixo `plataforma_enem_e2e_test_` e sufixo aleatório validado,
aplica migrations oficiais, cria operador sintético e inicia API/frontend
em portas locais livres. Os vinte casos usam a interface com persistência real.

```powershell
$env:RUN_MYSQL_E2E = "1"
npm run test:e2e
Remove-Item Env:RUN_MYSQL_E2E
```

É necessário privilégio de criar/remover schemas descartáveis. Processos e
schema são limpos em `finally`, também após falha. Não há fallback para mocks,
SQLite ou banco operacional. Relatórios/capturas ficam em `test-results/`,
ignorado pelo Git. Não gerar traces, HAR, vídeo ou storage state autenticado.
