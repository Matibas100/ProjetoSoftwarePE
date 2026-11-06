# Validação: consolidar entrega acadêmica

## Ambiente e preservação

Execução local em **2026-11-06**, Windows, Python **3.14.0**, Node **25.2.1**,
npm **11.6.2**, MySQL **8.0.46** em Docker e Playwright **1.65.0**/Chromium.
O workflow remoto usa Python 3.12 e Node 22; essas versões não foram executadas
localmente. A execução remota permanece pendente até push autorizado.

Preflight somente leitura: artefatos, AGENTS.md, cinco conventions,
arquitetura mestre e ADRs 001–006. Estado inicial: somente esta change,
`openspec/changes/mover-join-assuntos-para-repository/` e `tmp/` não rastreados.
A change preexistente, seus metadados, os temporários e os binários oficiais
de `docs/design/desktop-v1/` foram preservados. Não houve edição de schema,
bootstrap, migrations, procedure ou `frontend/index.html`.

Nenhum conteúdo de `.env` foi lido/exposto. Testes usaram
`PYTHON_DOTENV_DISABLED=1`; configuração MySQL foi fornecida apenas pelo
ambiente dos processos. Container exclusivo com senha aleatória, porta restrita
a loopback e schemas aleatórios rigidamente validados; nenhum banco operacional
foi utilizado. Credenciais não aparecem em comandos, relatórios ou capturas.

## Comandos e resultados

| Validação | Comando | Resultado observado |
| --- | --- | --- |
| Caracterização anterior | `python -m unittest backend.tests.unit.test_catalogo backend.tests.unit.test_services backend.tests.unit.test_models_repository_controllers backend.tests.unit.test_http_controllers -q` | 66 aprovados antes das edições; 67 após catálogo |
| Catálogo MySQL | `python -m unittest backend.tests.test_materias_integration backend.tests.test_assuntos_integration backend.tests.test_catalogo_admin_integration -q` | 23 aprovados; novo cenário de filtros/status/ordem/delegação também aprovado separadamente |
| Questões/Práticas/Simulados | `python -m unittest backend.tests.test_questoes_integration backend.tests.test_questoes_versionadas_integration backend.tests.test_praticas_integration backend.tests.test_simulados_integration -q` | 40 aprovados, incluindo SELECTs constantes por página/composição |
| HTTP/autenticação MySQL | `python -m unittest backend.tests.test_autenticacao_integration backend.tests.test_materias_integration backend.tests.test_assuntos_integration backend.tests.test_catalogo_admin_integration -q` | 35 aprovados |
| Backend completo com cobertura | `python backend/tests/run_backend_coverage.py`, com os dois opt-ins MySQL no processo | **128 unitários + 114 integrações aprovados**, incluindo os 29 originais e migrations 000–009; **97,38% linhas**, **91,14% branches** |
| Dependências Node | `npm ci` | Lockfile reproduzido; nenhuma dependência de produção acrescentada |
| Frontend completo com cobertura | `npm run test:coverage` | **143 testes aprovados**; **99,21% linhas**, **88,19% branches** pelo validador agregado; novo menu 100% linhas/branches |
| Servidor público | `python -m unittest discover -s scripts/tests -v` | **7 aprovados** |
| Descoberta do navegador | `npm run test:e2e:list` | Uma suíte encadeada, com vinte passos numerados e regressões adicionais, separada do Vitest |
| Navegador real | `RUN_MYSQL_E2E=1 npm run test:e2e` (sintaxe POSIX; configuração MySQL por ambiente) | **Suíte aprovada** no Chromium, vinte percursos; última execução 29,3 s, schema removido |
| Bloqueio E2E | `python scripts/run_e2e.py` sem opt-in | Recusado antes de conectar/criar schema; seis unitários validam guardrails/limpeza |
| Workflow | `actionlint 1.7.12 .github/workflows/testes.yml` | Sem erros; ferramentas auxiliares somente em `test-results/` ignorado |
| Diagramas | `mmdc -i docs/technical/diagrama-de-classes.md -o test-results/diagrama.md -b white` | Cinco blocos Mermaid renderizados em SVG/PNG e inspecionados |
| Documentação | Verificação de links locais, numeração e classes por AST | Links válidos; README com 20 entradas; diagrama cobre as 20 Models concretas |
| Dependências Python | `python -m pip check` | Sem requisitos quebrados |
| Diff | `git diff --check` e conferência de áreas protegidas | Sem erro de whitespace; áreas protegidas sem diff |

Os gates de **90% linhas / 85% branches** e o bloqueio de arquivo executável
zerado foram mantidos e aprovados. Não houve SQLite nem mocks de integração.

## Evidências por frente

- Catálogo: JOIN somente no Repository, Service coordena; Model mantém
  delegação compatível e CRUD. Filtros de status de Matéria/Assunto,
  filtro opcional e ordenação preservados.
- Lote: DTO sem correção antecipada, versões retiradas/superadas, histórico,
  ordem, propriedade e estados mistos. Medição compara leituras pequenas e
  grandes sem contar renovação de sessão; nenhum FOR UPDATE nas leituras.
  Escritas mantêm contratos unitários, locks, replay, rollback e snapshots.
- HTTP: status 200/201/204, detalhes, envelope legado de Questões, respostas
  Flask prontas, cookies, CSRF, `codigo`, Retry-After e no-store preservados.
  Sentinelas de senha/token/SQL/parâmetros não aparecem em logs/respostas;
  logs inesperados contêm somente contexto fixo e classe, sem traceback.
- Navegação: oito páginas do Aluno e sete administrativas, destinos corretos,
  indicação atual única, indisponíveis sem ação, inicialização antes da sessão.
  DOM mantém cenários de troca/expiração/recuperação; Chromium verifica foco
  visível com Tab/Shift+Tab e abertura do plano por Enter em todas as oito.
- E2E: vinte ações avaliadas pela UI e API/banco reais; exclusões vinculadas
  retornam 409; prática não antecipa correção; arquivamento preserva histórico;
  cancelar saída para o plano conserva alternativa local sem salvar/finalizar.
- Runner: sucesso e falhas de browser limparam processos/schema reais; unitários
  também cobrem falha de migration e recusa de nomes inseguros. Operador é setup
  por Service existente; Aluno/conteúdo dos casos são cadastrados na interface.

`test-results/e2e.json` e as capturas `plano-1440.png`, `plano-390.png`,
`admin-1440.png`, `admin-390.png` em `test-results/browser/` são evidências
locais sintéticas, ignoradas pelo Git. Capturas finais aguardam dados carregados.
Não foram produzidos traces, HAR, vídeo ou storage state. Diagramas derivados
em `test-results/` também não alteram os binários oficiais.

## Ajustes durante a validação

A primeira invocação unitária sem configuração fictícia foi recusada na
importação e corrigida com ambiente exclusivo. A preparação do novo teste de
catálogo foi corrigida para cadastrar Assunto antes de inativar sua Matéria.
Os testes DOM passaram a renderizar o menu compartilhado antes das asserções.

Nas primeiras iterações E2E, a coleta de corpo após redirecionamento e algumas
expectativas/seletores não correspondiam ao fluxo existente. O teste passou a
usar status e leitura independente após redirecionar, aguardar a URL persistida
do Simulado e verificar a classificação realmente mostrada no histórico.
Nenhum contrato de produto foi alterado para acomodar os testes.
Uma invocação de cobertura com argumento encaminhado ao validador foi repetida
pelo comando oficial completo, com sucesso.

## Limitações e pendências externas

- Admin mantém a largura mínima desktop e rolagem horizontal a 390 px;
  isso foi observado nas capturas e não é apresentado como redesign mobile.
- CI foi validado estaticamente e seus comandos reproduzidos localmente;
  execução no GitHub/Linux/Python 3.12/Node 22 ainda não ocorreu.
- Vídeo obrigatório: gravação/envio pelo usuário. Commit, push e merge não
  autorizados. Sync e archive são etapas posteriores à aplicação/verificação.

## Fechamento técnico

[Verificação](verificacao.md) concluída sem achados críticos. Aplicação com
18/18 tarefas concluídas. Conferência final: zero schemas descartáveis restantes;
container exclusivo de testes encerrado. Pronta para sync e posterior archive.

## Sincronização e arquivamento

Em **2026-11-06**, a delta de `plano-estudos-basico` foi sincronizada:
um requisito e quatro cenários acrescentados, com conteúdo anterior preservado.
`openspec validate --specs`: nove specs aprovadas, com avisos preexistentes
sobre descrições longas.

A change foi arquivada pelo CLI em
`openspec/changes/archive/2026-11-06-consolidar-entrega-academica/`, com
18/18 tarefas completas e sem achados críticos. O conteúdo já sincronizado
foi conferido antes do archive; todos os arquivos, inclusive `.openspec.yaml`,
foram preservados integralmente durante a movimentação. Links do README e
da matriz foram ajustados ao novo destino. CI remoto e vídeo seguem pendentes;
nenhum commit, push ou merge foi executado.
