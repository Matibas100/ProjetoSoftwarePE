# Validação: Plano e Simulado pelo navegador

## Baseline e limites

Preflight em 06/11/2026: proposta, design, tarefas, AGENTS.md, cinco conventions,
architecture-master-v1, ADRs 002/005/006/008 e specs de Plano, Simulados e
Desempenho lidos. Seletores e contratos conferidos no código atual.

O workspace já continha alterações de outras changes, arquivos não rastreados
e relatórios históricos. Estado anterior, cópias dos documentos/teste anterior
e hashes SHA-256 de 469 arquivos estão em `test-results/plano-simulado/`,
ignorado pelo Git. Esse baseline separa o delta atual do trabalho preexistente,
incluindo `tmp/`, specs e visuais oficiais.

Delta autorizado: novo `frontend/e2e/plano-simulado.spec.js`, trechos pertinentes
de README e `docs/technical/entrega-academica.md`, mais artefatos desta change.
Não há autorização para commit, push ou merge. No preflight, nenhum `.env` foi lido.
Banco operacional, código de produção, runner, configuração, dependências,
CI, migrations, specs e visuais permanecem fora do escopo.

Após o bloqueio inicial, o usuário orientou executar com o acesso local já
concedido. Essa orientação posterior substituiu a restrição operacional de
não carregar `.env`: somente a configuração MySQL local foi carregada na
memória de um processo Python e repassada por ambiente ao runner. Nenhum
valor foi exibido, gravado em relatório ou persistido nas variáveis do Windows.
O arquivo local e o runner não foram alterados; o runner continua sem carregar
`.env` por conta própria. As escritas acadêmicas ocorreram somente nos schemas
descartáveis, por interface/HTTP real.

## Execução

| Comando/conferência | Resultado em 06/11/2026 |
| --- | --- |
| `npm run test:e2e:list` | Aprovado: dois testes em dois arquivos. Somente descoberta, sem executar cenários. |
| `node --check frontend/e2e/plano-simulado.spec.js` | Aprovado: sintaxe válida. |
| `openspec validate validar-fluxos-de-plano-e-simulado --strict` | Aprovado; `skip_specs: true` aceita ausência de deltas funcionais. |
| Links relativos, lista e matriz dos vinte itens | Aprovados: destinos existentes; lista/matriz idênticas ao baseline. |
| UTF-8, whitespace e `git diff --check` no escopo | Aprovados; aviso Git de conversão LF/CRLF no README, sem erro de whitespace. Arquivos novos também conferidos diretamente. |
| SHA-256 contra baseline e inventário de arquivos novos | Sem alteração inesperada. Evidência local em `test-results/plano-simulado/preservacao.json`. |
| Primeira tentativa: `npm run test:e2e`, com opt-in temporário | Saída 1, `MigrationError` por configuração MySQL ausente; bloqueio posteriormente resolvido. |
| Runner oficial `scripts.run_e2e.main()`, com configuração no processo | Aprovado: 2 testes em 40,0 s, saída 0; teste dos vinte casos e novo teste passaram, cada um em 18,8 s. O runner confirmou remoção do schema. |
| Novo arquivo sozinho via `executar_suite(..., comando=...)` | Aprovado: 1 teste em 21,9 s, cenário em 20,1 s, saída 0; MySQL 8.0.44, nenhum schema E2E novo nem processo Python/Node remanescente. |

O opt-in foi definido somente no processo PowerShell e removido em `finally`:

```powershell
try {
    $env:RUN_MYSQL_E2E = '1'
    npm run test:e2e
} finally {
    Remove-Item Env:RUN_MYSQL_E2E -ErrorAction SilentlyContinue
}
```

Na primeira tentativa, o processo não recebeu `DATABASE_URL` nem o conjunto obrigatório `DB_HOST`,
`DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Conferência somente de presença
também não encontrou essas variáveis nos escopos User/Machine do Windows.
Nessa tentativa não foram exibidos valores nem lidos arquivos de configuração. O runner falhou
em `load_database_settings(env)`, antes de conectar/criar schema ou iniciar
API/frontend/Chromium. Portanto não há schema/processos desta tentativa a
limpar.

Na retomada autorizada, um processo temporário usou `dotenv_values` apenas
para obter a configuração MySQL, sem imprimir valores, e a colocou em
`os.environ`. Definiu `RUN_MYSQL_E2E=1` e `PYTHON_DOTENV_DISABLED=1`, chamou
`scripts.run_e2e.main()` e removeu o opt-in em `finally`. Não houve mudança
em runner, config Playwright, dependências ou código de produção.

A execução completa, aprovada, está resumida em
`test-results/plano-simulado/execucao-completa.json`: 2 testes aprovados,
26 passos no teste anterior (incluindo os vinte numerados) e 10 no novo.
Somente títulos, estados, durações e estatísticas foram guardados nessa
evidência resumida; nenhuma configuração de conexão ou sessão.

A verificação isolada usou o próprio `executar_suite` com o comando
`node node_modules/@playwright/test/cli.js test frontend/e2e/plano-simulado.spec.js`,
mantendo guard, migrations, operador sintético, URLs/portas isoladas e limpeza
do runner. Conferiu somente `SELECT VERSION()` e schemas com o prefixo E2E em
`information_schema`, antes/depois; nenhuma consulta ao banco operacional.
Evidência em `test-results/plano-simulado/execucao-isolada.json`. O PowerShell
também comparou os PIDs Python/Node antes/depois: zero processos novos
remanescentes. O novo teste passou com os dados do teste anterior presentes
na suíte completa e sem eles na execução isolada; não depende de IDs ou
conta criados pelo primeiro. A ordem inversa não foi executada separadamente.

O passo de replay é uma verificação técnica auxiliar por `apiRequest` HTTP real,
sem botão, reaproveitando o corpo/chave original somente em memória. Não
substitui as ações de geração e recálculo da interface. Não são exportados
cookies, tokens, credenciais, storage state, HAR ou traces.

Concorrência, rollback e falha de commit continuam cobertos pelas integrações
históricas; o novo E2E não constitui nova evidência desses cenários.

## Verificação OpenSpec

Aplicada a skill `openspec-verify-change`, com status/instruções atuais,
artefatos, conventions, código e evidências disponíveis.

| Dimensão | Resultado |
| --- | --- |
| Completude | 11/11 tarefas concluídas após execução completa, isolada e conferências finais; cenários previstos presentes nos dez passos do novo teste. |
| Correção | Dois testes aprovados no Chromium/MySQL 8 real; novo teste também aprovado sozinho. Confirmados cálculos, persistência, cancelamentos sem POST e histórico por replay técnico. |
| Coerência | Delta restrito aos três arquivos previstos e registros da change. Sem mudanças de contratos, camadas ou decisões dos ADRs. Carregamento local da configuração autorizado posteriormente pelo usuário e limitado ao processo. |

**Achado inicial resolvido:** o bloqueio de configuração (`MigrationError`)
foi superado pelo carregamento local autorizado; a suíte completa e o novo
teste isolado passaram com o runner intacto. Não houve falha funcional que
exigisse mudança em produção, mocks, SQLite ou fallback operacional.

Sem achados críticos ou avisos pendentes. Hashes confirmam preservação
do teste dos vinte casos, produção, runner, Playwright, dependências, CI,
`tmp/`, specs, demais changes/relatórios e artefatos visuais preexistentes.

**Estado:** aplicação/verificação concluídas; pronta para arquivamento pela
skill apropriada. Sincronização de specs não se aplica (`skip_specs: true`).
Não houve arquivamento, commit, push ou merge nesta aplicação.
