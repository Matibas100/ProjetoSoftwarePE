# Validação: melhorar legibilidade e documentação

## Escopo e baseline — 06/11/2026

Aplicação pelo schema `spec-driven`, com specs dispensadas (`skip_specs: true`).
Lidos proposta, design, tarefas, AGENTS.md, as cinco conventions, arquitetura
mestre e ADRs 001/005/006/008. Escopo fechado conferido: oito HTML, cinco CSS,
oito Controllers, um Service e três documentos (25 arquivos).

Baseline não sensível em `test-results/legibilidade/`: cópias dos 25 arquivos,
AST Python, representações DOM/textos/literais e CSS, hashes SHA-256 dos
arquivos rastreados e dos três módulos locais de migrations, estado Git e
diff preexistente. Nenhum conteúdo de `.env` ou `tmp/` foi copiado ou exposto.

Alterações já presentes antes desta execução: README com a nova estrutura de
migrations; `backend/database/migrate.py`; `backend/tests/unit/test_migrations.py`;
novos `legacy_schema.py`, `migration_types.py` e `sql_scripts.py`; arquivamento
`2026-11-06-organizar-runner-de-migrations`; esta change, a change
`mover-join-assuntos-para-repository` e `tmp/`. Essas alterações não pertencem
ao delta de implementação desta change e devem ser preservadas.

Ferramentas existentes: Python, Node, jsdom, PostCSS, css-tree, Playwright e
GitHub CLI. Nenhuma dependência instalada ou configuração alterada.

## Evidência remota somente leitura

Consultas `gh api` ao commit e à execução indicados pelo design confirmaram:

- SHA `37b9b0ccf0bb4640527628b7f719c14ec987e0fe`, publicado em
  `2026-11-06T23:51:30Z` (06/11/2026, horário de Brasília).
- [Actions 42315102152](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42315102152):
  `completed`, `success`, mesmo SHA, conclusão `2026-11-06T23:59:27Z`.

Isso comprova somente o checkpoint consultado, sem validar o delta local ou
afirmar que ele corresponde ao HEAD remoto atual. Nenhuma operação Git de
escrita foi executada.

## Execução

### Validações incrementais

- `node test-results/legibilidade/frontend-qa.mjs format-css`: cinco CSS
  formatados com PostCSS existente; estrutura, ordem de regras/declarações,
  seletores, valores, prioridades, media queries e comentários comparados por
  AST PostCSS, além de tokens por css-tree. Espaço inicial das propriedades
  customizadas foi preservado para manter seus tokens originais.
- DOM pertinente a CSS: `npm run test:unit --` com `auth`, `admin-pages`,
  `navigation` e `html-contract`: **45 testes aprovados**.
- `node test-results/legibilidade/frontend-qa.mjs format-html`: oito páginas
  com dois espaços, comparadas por jsdom. Whitespace ignorado apenas nas
  fronteiras de blocos/flex conhecidas; textos, espaços inline, literais,
  conteúdo pre-wrap, elementos e atributos preservados. A comparação foi
  refinada durante o QA para preservar essas fronteiras, sem alterar textos.
- DOM de Práticas, Simulados, Desempenho, Plano, navegação e contrato HTML:
  **80 testes aprovados** após a formatação final. A mensagem jsdom
  `Not implemented: navigation to another Document` não reprovou a suíte.
- Pesquisa de consumidores/patches em `backend`, `frontend` e `scripts`:
  nenhum dos 14 imports removidos era consumido/reexportado. Permanecem as
  classes, Services efetivamente usados e `COOKIE`/`resposta_erro` usados por
  `auth_http`. A AST restante dos oito Controllers é idêntica.
- Unitários de HTTP, Controllers/Models/Repository, autenticação e Simulado,
  carregados com o ambiente isolado de `run_unit.py`: **39 testes aprovados**.
- AST de `FinalizarSimuladoService` idêntica após mapear somente `t/r/i/q/valor`
  para `tentativa/resposta/item/versao_historica/revisao_recebida`. Ordem de
  execução, chamadas, atributos, parâmetros, imports e fórmula preservados.
- Documentação: links locais válidos, vinte itens do README e vinte linhas da
  matriz idênticos ao baseline; bloco preexistente de migrations preservado.
  Distinção entre as duas atividades e relatórios históricos mantida.

### Regressão integrada

Invólucro temporário `test-results/legibilidade/run_validation.py`, usando o
loader existente autorizado no trabalho anterior, sem abertura manual ou
exposição de `.env`. Configuração repassada somente aos processos, dotenv
desabilitado nos filhos e logs com redaction. Nenhuma escrita no banco
operacional: integrações e E2E criaram seus próprios schemas descartáveis.

| Execução nova | Resultado |
| --- | --- |
| `python backend/tests/run_backend_coverage.py`, com os dois opt-ins MySQL | **145 unitários + 115 integrações**, saída 0 |
| Gate backend | **97,47% linhas (3615/3709), 91,24% branches (812/890)** |
| `npm run test:coverage` | **143 testes / 14 arquivos**, saída 0 |
| Gate frontend | **99,21% linhas (1750/1764), 88,19% branches (1202/1363)** |
| `npm run test:e2e`, runner oficial intacto | **2 testes aprovados em 48,4 s**, saída 0 |

Gates 90%/85% e validadores de arquivo executável zerado passaram sem mudanças
de configuração, dependências ou testes. Integrações incluem Controllers,
propriedade, revisão, branco, correção persistida, replay, concorrência,
rollback na última gravação, migrations e procedure com MySQL real.
E2E incluiu os vinte casos e o percurso completo Plano/Simulado, persistência,
cancelamentos sem POST e foco restaurado/após finalização.

O backend e o E2E foram executados em paralelo, com schemas distintos. Por
isso, os snapshots globais do invólucro E2E viram schemas de integração
diferentes antes/depois e não servem isoladamente como comparação de limpeza.
O runner registrou remoção de seu schema; o backend terminou com listas de
schemas vazias antes/depois. A conferência final deve também estar vazia.

### QA visual complementar

Capturas oficiais de Plano/Admin em 1440/390 px foram produzidas pelo E2E.
O QA complementar usa `executar_suite` intacto com comando temporário, schema
novo e fatos sintéticos persistidos via API real, sem repetir os dois testes.
Baseline HTML/CSS é servido somente na página de QA e comparado à versão
formatada com os mesmos fatos.

Durante o QA houve bloqueio de acesso loopback do Chromium para documentos
fornecidos por `route.fulfill`. Resolvido concedendo `local-network-access`
somente à origem local do contexto temporário, sem mudar app/config/runner.
Outra comparação detectou apenas o segundo diferente do campo “calculado em”
de duas consultas reais de desempenho. O QA verifica a legenda restante
integralmente e fixa somente esse instante ao primeiro valor observado para
comparar capturas; métricas, requisições e respostas não são simuladas.

Inspecionadas as capturas de login, gestão de Matérias, Plano com prioridade,
Desempenho com dados, resolução e resultado de Simulado, todas em **1440 e
390 px**. Os **12 pares** finais têm textos, geometria dos elementos visíveis
e PNG idênticos ao baseline, com a normalização exclusiva de instante descrita
acima no Desempenho. Resultado persistido: 1 acerto, 1 erro, 1 branco, 33,33%;
o enunciado sintético com segunda linha confirma preservação de pre-wrap.

Capturas em `test-results/legibilidade/*-{before,after}.png`; comparação em
`visual-comparison.json` e limpeza em `visual-result.json`. O relatório de
comparação foi reconstituído dos 24 PNGs e do log após detectar colisão do
nome com o resumo do invólucro; os nomes temporários foram separados.
As capturas oficiais complementam Plano sem geração e
Admin. Mantida a largura desktop preexistente da Administração em viewport
390 px; a inspeção comprova preservação, sem redesign responsivo.

Último QA visual: saída 0; listas de schemas antes/depois vazias; `finally`
registrou remoção do schema. Conferência por processos não encontrou API,
servidor frontend, runner E2E ou QA Node remanescentes. Nenhum trace, HAR,
vídeo ou storage state foi gerado. Console 401 no login anônimo é esperado.

## Verificação final — openspec-verify-change

Status/instruções apply consultados novamente, contextFiles e conventions
conferidos frente ao delta final, sem necessidade de alterar proposta/design.
`openspec validate melhorar-legibilidade-e-documentacao --strict` aprovado;
o único INFO informa que zero deltas são aceitos com `skip_specs: true`.
`git diff --check`, links locais e comparações finais AST/DOM/CSS aprovados.

| Dimensão | Resultado |
| --- | --- |
| Completude | Oito tarefas anteriores concluídas; tarefa 5.3 comprovada nesta revisão. Todos os 25 arquivos previstos tratados, com evidências incrementais, cobertura, E2E e inspeção visual. |
| Correção | AST Python equivalente no delta permitido; DOM/textos/literais e CSS/tokens preservados; 260 testes backend, 143 frontend e dois E2E aprovados; 12 pares de capturas equivalentes. |
| Coerência | Lista fechada, arquitetura e ADRs preservados; documentação ligada ao checkpoint real; sem mudanças de contrato, schema, layout, dependências ou testes. |

**Achados:** nenhum crítico e nenhum aviso introduzido pela limpeza. Os
ajustes dos scripts temporários de QA foram resolvidos e não alteraram o
produto nem os runners/testes versionados.

Preservação comprovada por SHA-256 de **383 arquivos fora do escopo**, entre
rastreados e os três novos módulos locais de migrations. Inclui banco/SQL,
`migrate.py`, testes (inclusive a alteração local de migrations), JS/API,
helpers, `styles.css`, configs/lockfile, specs e visuais oficiais. README
mantém integralmente o conteúdo preexistente sobre migrations. Arquivos
temporários anteriores, a outra change e o arquivo da change arquivada não
foram editados.

Não houve escrita no banco operacional, exposição de configuração sensível,
instalação, commit, push, merge ou publicação. O resultado remoto citado
continua restrito ao SHA consultado; os resultados desta execução são locais.
Sync não aplicável (`skip_specs: true`). Aplicação e verificação concluídas.

## Arquivamento

Change arquivada em `2026-11-06-melhorar-legibilidade-e-documentacao` pelo CLI
OpenSpec, com nove tarefas concluídas e `.openspec.yaml` preservado. Sem delta
specs, alterações das specs principais ou pendências críticas. Links relativos
internos conferidos no destino. Nenhum commit, push ou merge foi executado.
