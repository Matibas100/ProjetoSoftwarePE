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
- `frontend/tests/`: suítes de contrato HTML e testes DOM de API, autenticação,
  navegação e áreas do Aluno e da Administração.
- `scripts/`: validadores agregados de cobertura por stack.

## Pré-requisitos de desenvolvimento

- Python 3.10 ou superior e `backend/requirements-dev.txt`.
- Node `>=22.9.0` e npm `11.6.2`; use `npm ci` com o lockfile.

## Comandos

| Finalidade | Comando direto |
| --- | --- |
| Unitários Python e frontend | `python backend/tests/run_unit.py` e `npm run test:unit` |
| Integrações MySQL | `python backend/tests/run_integration.py` |
| Cobertura backend | `python backend/tests/run_backend_coverage.py` |
| Cobertura frontend | `npm run test:coverage` |
| Cobertura das duas pilhas | `python backend/tests/run_backend_coverage.py` e `npm run test:coverage` |
| Navegador | `python scripts/run_e2e.py` ou `npm run test:e2e` |

As integrações e qualquer comando que as inclua exigem opt-in somente no processo:

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

O gate `backend/tests/unit/test_arquitetura_modular.py` protege os sete
proprietários, imports locais/dinâmicos, APIs explícitas, camadas, duas factories
independentes e metadata única. A composição não abre conexão nem lê `.env`.
Regressões de privacidade verificam falha real do participante de eliminação,
incluindo recusa e revogação, no MySQL descartável.

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
