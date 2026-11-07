# Validação: corrigir resposta JSON inválida

## Preflight

Execução local em 06/11/2026, schema `spec-driven`. Proposta, design, spec,
tarefas, AGENTS.md, cinco conventions, arquitetura mestre, ADR-002, ADR-006
e requisitos/operação de autenticação lidos antes da primeira edição.
Orientações de apply compatíveis com o escopo; nenhuma exceção adotada.

A change `melhorar-legibilidade-e-documentacao` está verificada e arquivada
em `2026-11-06-melhorar-legibilidade-e-documentacao`, com nove tarefas
concluídas e relatório sem achados críticos. Não foram encontrados runners
de validação ou apply concorrente no preflight; nenhum subagente iniciado.

Baseline fresco em `test-results/json-invalido/manifest.json`: SHA-256 de
493 arquivos não sensíveis rastreados/novos, incluindo deltas anteriores,
changes, migrations, `tmp/` e visuais oficiais. Cópias dos dois arquivos
existentes do escopo em `baseline/`; estado Git em `git-status.txt`.
Arquivos de configuração sensível não foram abertos ou copiados.

Escopo de implementação: `frontend/js/api.js`, `frontend/tests/api.test.js`
e novo `docs/technical/cliente-api-frontend.md`, além dos artefatos desta
change. Preservar as alterações locais preexistentes e as demais changes.
Nenhuma escrita no banco operacional, publicação ou operação Git de escrita.

## Resultados

### Implementação e validações concluídas

- `frontend/js/api.js`: somente a leitura de JSON passou a usar `try/catch`
  delimitado. Sucesso ilegível gera `ApiError` com status real,
  `resposta_invalida`, detalhes nulos e mensagem fixa. Erro HTTP ilegível
  preserva status e mensagem genérica, com código/detalhes nulos.
- `frontend/tests/api.test.js`: caracterização antiga substituída;
  preservação de objetos/listas, 204 sem parser, erro 409 estruturado,
  sucesso ilegível 200/201, erros ilegíveis 401/500, ausência de exposição
  de corpo/parser, POST sem reenvio/evento/recuperação, token preservado,
  consulta posterior e bootstrap CSRF concorrente com nova tentativa explícita.
  Casos anteriores de conexão, credenciais e sessão mantidos. O teste 204
  agora prepara CSRF válido antes do DELETE e proíbe leitura do corpo.
- Novo [documento técnico](../../../../docs/technical/cliente-api-frontend.md):
  tabela de respostas, status original e consulta antes de repetir gravação;
  links locais e âncora de operação de autenticação conferidos.

| Comando | Resultado |
| --- | --- |
| `npm run test:unit -- frontend/tests/api.test.js` após 2.1 | 15 testes aprovados |
| Mesmo comando após 3.1 | 18 testes aprovados |
| `npm run test:coverage` | 151 testes, 14 arquivos, saída 0 |
| Gate frontend | 99,21% linhas (1752/1766), 88,08% branches (1204/1367) |
| `python scripts/run_e2e.py`, opt-in e configuração transitória | 2 testes aprovados em 36,4 s, saída 0 |
| Conferência complementar de logout com runner oficial e navegador real | Login 200, logout 204, retorno a `/login` e sessão revogada (401); saída 0 |
| Limpeza E2E | Schema removido pelo runner; listas de schemas descartáveis vazias antes/depois; sem processos remanescentes |
| `openspec validate corrigir-resposta-json-invalida --strict` | Aprovado |
| `git diff --check` e whitespace dos arquivos novos | Aprovados |
| SHA-256 contra baseline | 490 arquivos idênticos; somente dois arquivos de código/testes e `tasks.md` alterados |

Gates existentes de 90%/85% e verificação de arquivo executável sem cobertura
preservados. `api.js` atingiu 100% de linhas e 92,5% de branches no relatório
Vitest. Logs e inventário em `test-results/json-invalido/`.

### E2E — configuração e retomada

Na tentativa inicial, o ambiente da sessão não disponibilizava `DATABASE_URL` nem o conjunto completo
`DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD`. Consultados somente nomes
e presença das variáveis, sem exposição de valores. O usuário escolheu
disponibilizar a configuração no ambiente e retomar, mantendo `.env` fechado.

Após essa escolha, o runner oficial `python scripts/run_e2e.py` foi invocado
em processo filho com `RUN_MYSQL_E2E=1`, `PYTHON_DOTENV_DISABLED=1` e ambiente
transitório. Saída 1, `MigrationError` no carregamento da configuração.
Nenhum schema foi criado, nenhuma conexão foi aberta e nenhum servidor foi
iniciado: o erro ocorreu antes de `executar_suite`. Conferência de processos
não encontrou API/frontend/Playwright remanescentes.

Na retomada, o usuário forneceu a configuração de conexão e autorizou executar
os testes. Os valores foram usados somente no ambiente dos processos filhos,
sem abertura de `.env` nem gravação de credenciais em arquivos. O invólucro
temporário `test-results/json-invalido/run_e2e_validation.py` executou o runner
oficial intacto, com opt-in e dotenv desabilitado, e consultou somente metadados
para conferir os schemas descartáveis antes/depois. Logs receberam redaction.

Os dois E2E passaram: vinte funcionalidades com persistência/regressões de
navegação (16,5 s) e Plano/Simulado com geração, conclusão, finalização e
recálculo persistidos (18,2 s). Total Playwright: 36,4 s, saída 0. Cadastro/login,
exclusões 204 e os percursos válidos foram confirmados com API/MySQL reais.
O runner registrou remoção do schema; listas de schemas descartáveis estavam
vazias antes/depois e a conferência final não encontrou servidores/runners
remanescentes. Evidências em `e2e.log` e `e2e-result.json` no diretório ignorado.

Como os dois E2E existentes não exercitam logout, uma conferência complementar
usou `executar_suite` do mesmo runner intacto, outro schema descartável e
`logout-smoke.mjs` temporário, sem alterar a suíte versionada. Login e Sair
operados pela UI confirmaram POST logout 204, navegação a `/login` e consulta
de sessão 401. Saída 0; schemas antes/depois vazios; limpeza confirmada.
Evidências em `logout.log` e `logout-result.json` no mesmo diretório ignorado.

A primeira tentativa complementar encontrou timeout no login porque o script
temporário não configurava `window.ENEM_API_URL` com a porta aleatória do
runner. Corrigido somente o script de QA com o mesmo `addInitScript` usado
pelos E2E oficiais. A nova execução passou; produto e testes versionados
permaneceram intactos. A limpeza também foi confirmada na tentativa com timeout.

Erros de parser foram provocados somente nos unitários com mocks, como previsto;
o E2E não simula resposta malformada ou falha de proxy. Não houve fallback para
SQLite/mocks de integração nem execução contra banco operacional. O aviso de
precedência de `FORCE_COLOR` sobre `NO_COLOR` não afetou os testes.

### Verificação final — openspec-verify-change

Verificação somente leitura do status, instruções apply, artefatos, código,
testes e conventions concluída; este registro documenta o resultado pela
tarefa de apply já autorizada.

| Dimensão | Resultado |
| --- | --- |
| Completude | Seis tarefas atendidas; requisitos representados na implementação, documentação e testes; execução E2E obrigatória concluída. |
| Correção | 18 testes focados, 151 testes completos, dois E2E reais e logout complementar aprovados, com gates e limpeza confirmados. |
| Coerência | Delta restrito aos três arquivos previstos e registro/checklist da change, conforme design, ADRs e arquitetura. |

**Achados:** nenhum crítico, aviso ou sugestão pendente. O bloqueio inicial de
configuração foi resolvido pela retomada com conexão fornecida pelo usuário.
Nenhum defeito de implementação identificado. Validação OpenSpec estrita,
links, whitespace e hashes conferidos novamente após os E2E.

Aplicação e verificação concluídas, sem exceção ao requisito E2E. Change pronta
para sincronizar a capability `cliente-api-frontend` e depois arquivar pelas
skills correspondentes. Sync/archive não executados neste apply.

### Preservação

O inventário final conferiu 493 hashes do baseline: 490 intactos. As únicas
diferenças são `api.js`, `api.test.js` e `tasks.md`; os únicos arquivos novos
versionáveis desta execução são o documento técnico e este `validacao.md`.
Nenhuma alteração em backend, migrations, outras changes, specs principais,
`tmp/`, README, páginas, CSS ou artefatos visuais oficiais. A conferência
do inventário usa a mesma exclusão de configuração sensível do baseline.

Nenhum `.env` foi aberto, nenhuma dependência instalada e nenhuma alteração
de configuração persistida. Sem cobertura backend repetida, commit, push,
merge, publicação, aplicação de helpers ou arquivamento nesta execução.

## Sincronização das specs

Sincronização solicitada após o apply, usando `openspec-sync-specs`.
Raiz e delta selecionados pelo status do CLI; regras de specs consultadas
uma vez antes da escrita. Criada a spec principal
[`cliente-api-frontend`](../../../specs/cliente-api-frontend/spec.md) com os quatro
requisitos e nove cenários adicionados, sob uma única seção `Requirements`.
`Purpose` preservado integralmente do delta, sem placeholder ou cabeçalhos
de operação na spec principal. Nenhum requisito removido ou renomeado.

`openspec validate --specs`: dez specs aprovadas, nenhuma reprovada; avisos
de textos longos nas specs preexistentes. A nova capability passou também em
`openspec validate cliente-api-frontend --type spec --strict`, sem avisos.
Hashes confirmam preservação das nove specs anteriores e do delta; comparação
integral confirma propósito, requisitos e cenários sincronizados. Whitespace
e link local conferidos. Sem mudança de implementação ou nova execução dos
testes da aplicação. A change permanece ativa, pronta para arquivamento.

## Arquivamento

Change arquivada em `2026-11-06-corrigir-resposta-json-invalida` pelo CLI,
após nova conferência de seis tarefas concluídas, artefatos completos e
ausência de achados críticos. Os quatro requisitos e nove cenários foram
comparados integralmente com a spec principal e já estavam sincronizados;
`--skip-specs` evitou reescrita redundante. Validação estrita aprovada antes
do arquivamento. `.openspec.yaml` e demais artefatos preservados; links
relativos deste registro ajustados para o destino arquivado. Nenhum commit,
push, merge, mudança de implementação ou nova execução de testes da aplicação.
