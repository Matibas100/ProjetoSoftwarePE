# Validação — busca de Matéria e Assunto por ID

Execução em 09/11/2026. Change `buscar-materias-assuntos-por-id`, schema
`spec-driven`. Aplicação restrita aos dois detalhes e aos formulários existentes.

## Evidências por tarefa

| Tarefa | Implementação e comprovação |
| --- | --- |
| 1.1–1.2 | Services próprios validam inteiro positivo não booleano até 2147483647, consultam a Model e serializam `to_dict`. Controllers usam `_responder`; GET no Blueprint existente, com HEAD/OPTIONS do Flask. Unidade cobre limites sem consulta persistente, três estados, descrição nula, ausência, delegação e 500 genérico. |
| 1.3 | Três novos testes de integração MySQL com schema próprio descartável: GET/HEAD, payload básico igual à Model, normalização/vínculo, três estados, ausência de mutação e leitura sem CSRF/senha recente; 400/401/403/404, queries, limite máximo e `no-store`. Dez testes afetados passaram (três novos e sete do catálogo administrativo). README documenta contrato. |
| 2.1–2.3 | 66 novos testes DOM passaram: detalhe diferente da linha, PUT explícito, rascunho/ID/guard preservados em falhas, ausência de fallback/retry, descarte cancelado sem GET, token/abort e A/B fora de ordem, erro/finally antigo, digitação/Novo/Cancelar/Salvar, bloqueio/troca/revalidação de identidade e dependências de seletores. Assunto usa a origem atual e só oferece ativas mais a Matéria corrente, inclusive inativa/arquivada/nova. |
| 3.1 | Chromium com API e MySQL descartáveis, sem interceptação: alterações de Matéria em segunda aba aparecem ao Editar na primeira. Assunto é renomeado/transferido na segunda aba para Matéria criada depois da abertura; essa Matéria é inativada. A primeira aba recebe vínculo/nome/descrição atuais e envia PUT explícito, sem transferência fictícia. As cinco suítes E2E passaram, incluindo os vinte casos originais. |
| 3.2 | Coberturas aprovadas: backend 95,18% de linhas e 85,87% de branches; frontend 99,34% de linhas e 90,31% de branches. Backend: 197 unitários aprovados e 203 integrações descobertas, 152 executadas/aprovadas e 51 ignoradas pelo opt-in de migrations. Frontend: 286 testes aprovados em 17 arquivos. Gate modular confirma sete módulos e 21 mappers. |
| 3.3 | Validação OpenSpec estrita aprovada. Diff, links locais e UTF-8 verificados; sem segredos, acesso direto à sessão em Controller/Service ou nova persistência. Apenas F02 resolvida; testes originais, contratos de escrita e superfícies congeladas preservados. |

## Navegador e composição existente

O cenário em [catalogo-detalhe.spec.js](../../../../frontend/e2e/catalogo-detalhe.spec.js)
observa as respostas reais e as mutações da página. Nenhuma escrita ocorre
ao clicar Editar; foco termina no nome. A mensagem existente tem `role=status`
e `aria-live=polite`; a leitura usa esse bloco e `aria-busy` no formulário.

- [Matéria: linha antiga e editor com detalhe atual](validacao-visual/materia-detalhe-atual.png).
- [Assunto: linha antiga e editor com vínculo atual](validacao-visual/assunto-vinculo-atual.png).

Capturas revisadas visualmente, com dados sintéticos. Os binários oficiais
do Desktop V1 permanecem intactos. Não foram gerados traces, HAR, vídeo ou
estado autenticado persistido. O runner removeu processos e schema no `finally`.

## Comandos e reprodução

- Unidade afetada: `python -m unittest tests.unit.test_buscar_catalogo_por_id -v`,
  usando o bootstrap de ambiente sintético de `tests.run_unit`: 3 testes aprovados.
- Integração afetada: `python -m unittest tests.test_buscar_catalogo_por_id_integration tests.test_catalogo_admin_integration -v`,
  com `PYTHONPATH=backend` e `RUN_MYSQL_INTEGRATION=1` somente no processo: 10 testes aprovados.
- DOM afetado: `npx vitest run frontend/tests/admin-catalogo-detalhe.test.js frontend/tests/admin-pages.test.js --coverage=false`.
- Coberturas: `RUN_MYSQL_INTEGRATION=1 python backend/tests/run_backend_coverage.py`
  e `npm run test:coverage` (no PowerShell, definir o opt-in como variável do processo).
  Backend: linhas **4507/4735 (95,18%)**, branches **924/1076 (85,87%)**;
  frontend: linhas **2107/2121 (99,34%)**, branches **1557/1724 (90,31%)**.
  Ambos superam 90% de linhas e 85% de branches, sem arquivo executável de
  produção com zero linhas cobertas. Unitários backend em 8,0 s; integração
  backend em 174,1 s. Os 29 testes originais passaram sem modificação.
- E2E: `scripts.run_e2e.executar_suite`, com configuração existente carregada em
  memória por `migrate.load_database_settings()` e transmitida por ambiente,
  `RUN_MYSQL_E2E=1`, comando padrão Playwright. O runner não lê `.env`; cria
  schema aleatório, aplica migrations e limpa tudo. Primeiro foi executado
  apenas `catalogo-detalhe.spec.js`; depois, os cinco arquivos completos:
  **5 aprovados em 44,0 s**.
- `openspec validate buscar-materias-assuntos-por-id --strict`: aprovada.
- `git diff --check`: aprovado. Auditoria dos Markdown modificados e artefatos
  da change: links locais existentes e UTF-8 válido, sem caracteres de substituição.

## Verificação final

| Dimensão | Resultado |
| --- | --- |
| Completude | Nove tarefas implementadas e validadas; requisitos e cenários dos dois delta specs representados nos testes e na documentação. |
| Correção | Unidade, integração real, DOM e Chromium aprovados; dados atuais, rascunho, concorrência, identidade e escrita explícita comprovados. |
| Coerência | Fluxo Route → Controller → Service → Model → MySQL; CRUD Active Record, sete módulos e 21 mappers preservados, sem mudança de banco/dependência ou cliente HTTP global. |

Sem achado crítico. Em 09/11/2026, as duas capabilities foram sincronizadas:
três requisitos adicionados em `catalogo-academico` e quatro em
`gestao-administrativa-conteudo`, preservando os requisitos anteriores.
`openspec validate --specs` aprovou as 17 specs e a comparação confirmou todos
os blocos dos deltas. Após essa sincronização, a change foi arquivada pelo CLI
em `2026-11-09-buscar-materias-assuntos-por-id`, com 9/9 tarefas concluídas.

## Ajustes encontrados e limites

A revisão constatou que falhas de autenticação anteriores à atribuição de
`g.auth_sessao` não recebiam `no-store`. O hook de cache passou a reconhecer
somente os dois novos endpoints, incluindo 401/403; as exceções e regras de
autorização não mudaram. A integração real comprova o comportamento.

O teste unitário da factory fixava 68 regras. Foi atualizado para 70, com
assertiva de um GET por caminho. Os 29 testes originais não foram alterados.
Uma primeira invocação unitária sem o bootstrap sintético não iniciou por falta
de configuração; foi repetida corretamente sem conexão ou leitura de `.env`.
Falhas nas primeiras versões dos testes DOM/E2E foram corrigidas antes das
execuções aprovadas; os relatórios acima descrevem o estado final.

F02 está resolvida pela prova ponta a ponta. F01 e E01–E03 continuam abertas.
Não há gestão de usuários, alteração de exclusão, schema/migration/procedure,
dependência, Model ou Repository novo. A consulta não fornece versionamento
otimista: alterações entre GET e PUT continuam sujeitas às validações de escrita
existentes. Não foi exercitado Gemini externo nesta change.

Os 51 testes de migrations exigem `RUN_MYSQL_MIGRATION_INTEGRATION=1` e não
foram habilitados: não houve alteração de SQL, schema ou runner nesta change.
As migrations oficiais foram aplicadas nos schemas descartáveis usados pelas
integrações executadas e pelo E2E. Os resultados não alegam execução desses
51 ensaios especializados nem aceite acadêmico integral.
