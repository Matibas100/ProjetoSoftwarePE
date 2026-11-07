# Validação — Corrigir respostas nulas e revisar a entrega

Data: 07/11/2026. Implementação local, sem commit, push ou alteração do CI publicado.

## Baseline atual

Preflight somente leitura: proposal, design, delta, tasks, AGENTS, cinco conventions,
architecture-master-v1, ADR-001/002/008, diagrama, Models, migrations e os dez arquivos
do escopo. As referências do README foram confrontadas sem conexão ao banco.

`test-results/corrigir-respostas-nulas-e-revisar-entrega/` é ignorado pelo Git.
Contém `baseline.json` (estado Git inicial e SHA-256 dos arquivos presentes) e
`files/` (cópias exatas dos dez arquivos do escopo, incluindo README e sete HTMLs).
Essas cópias vêm do working tree atual, sem depender de HEAD. Nenhum `.env`,
credencial, dado de usuário real ou sessão exportada foi usado no baseline visual.

Estado Git anterior: README; legacy_schema; suporte de integração de migrations;
testes unitários de migrations; ADR-001; entrega acadêmica; operações de Plano e
Privacidade; config OpenSpec; oito specs principais. Já existiam também o teste
de schema portável, duas changes arquivadas, esta change e `tmp/`.
O estado completo com os caminhos está no baseline ignorado.

Referência visual anterior: `node test-results/corrigir-respostas-nulas-e-revisar-entrega/visual.mjs before`.
Chromium real, sete páginas, 1440×1000 e 390×1000, screenshots de página inteira
e geometria/texto/estado dos elementos visíveis. Fixtures sintéticas adaptadas das
suítes DOM existentes; servidor HTTP local sem acesso ao banco. São conferências
DOM/visuais isoladas, não evidência de integração. Scripts/CSS reais executados,
com carregamento, formulário/foco quando presente, modal/cancelamento e navegação.
Sem trace, HAR, vídeo ou storage state.

## Resultados

### Cliente da API — tarefas 1.2/1.3

- `npm run test:unit -- frontend/tests/api.test.js`, antes da correção:
  **10 falhas / 21 sucessos**, demonstrando `TypeError` nos sete status nulos,
  bootstrap nulo e POSTs nulos 200/201 (`api-red.log`, ignorado).
- Mesmo comando após o guard estrito `dados === null`: **31/31 testes aprovados**
  (`api-green.log`). Reaproveitado o envelope de erro já existente, antes da
  leitura de `csrf_token`; nenhum novo tipo de payload validado.
- 200/201: ApiError, status original, `resposta_invalida`, detalhes nulos e
  orientação para conferir dados. 400/401/403/409/500: mensagem genérica atual,
  código/detalhes nulos, sem inferir evento/recuperação de sessão.
- Objetos/listas com nulos internos preservados. DELETE e logout 204 sem leitura
  do corpo. JSON ilegível e erro estruturado 409 continuam cobertos.
- Bootstrap nulo compartilhado: uma consulta, duas rejeições, zero POSTs;
  tentativa explícita posterior obtém token e envia só sua mutação.
- POST nulo 200/201: apenas envio original, sem retry/recuperação; GET posterior
  independente e nova ação explícita mantêm o token válido. Erro estruturado
  real de sessão conserva sinalização e exige nova confirmação.

### HTML — tarefas 2.1/2.2/2.3

Formatação individual com dois espaços, tags/atributos originais preservados.
Comparador temporário com jsdom confronta DOM, ordem, atributos e texto
significativo com as cópias atuais; `textarea/pre/script/style` mantêm conteúdo
literal. Comparação adicional do código ignora somente whitespace entre tags.
Os espaços de texto misto/inline permanecem literais. Detectado e corrigido,
durante a conferência, whitespace significativo entre Sair e Trocar de ambiente.
Não foram acrescentados testes permanentes que espelham formatação.

`node test-results/corrigir-respostas-nulas-e-revisar-entrega/format.mjs <página>`
e `node test-results/corrigir-respostas-nulas-e-revisar-entrega/visual.mjs after <página>`
executados individualmente, antes da página seguinte.

| Página | Suítes existentes após formatação | Resultado |
| --- | --- | --- |
| Matérias | admin-pages, navigation | 25/25 |
| Assuntos | admin-pages, navigation | 25/25 |
| Dashboard | desempenho, html-contract, navigation | 31/31 |
| Questões | admin-questoes, html-contract, navigation | 31/31 |
| Editor de Questão | admin-questoes, html-contract, navigation | 31/31 |
| Simulados | simulados, html-contract, navigation | 37/37 |
| Editor de Simulado | simulados, html-contract, navigation | 37/37 |

Todos os nomes acima correspondem a `frontend/tests/<nome>.test.js`, chamados
com `npm run test:unit -- <arquivos>`. Logs por página no diretório ignorado.

Conferência real em Chromium: DOM/atributos e geometria/estado/texto dos elementos
visíveis idênticos a 1440/390 px, com os mesmos dados sintéticos. Screenshots
incluem carregamento, formulário preenchido/foco e modal. Cancelamento restaura
foco e navegação pelo menu chega à URL esperada. Preservados os avisos de recursos
indisponíveis, formulários, scripts e sua ordem.

Limitação observada: antialiasing do texto em controles nativos varia entre
execuções do Chromium. O replay **da mesma cópia anterior de Assuntos**, sem
editar seu HTML, variou em 767 pixels a 390 px. Quando há diferença de PNG, a
conferência exige geometria/texto/valores idênticos e menos de 0,1% da imagem
diferentes, restritos a input/select/textarea. Fora desses controles, aceita-se
somente variação de até 1 em cada canal RGB: por exemplo, 18 pixels na borda
arredondada sob o backdrop do modal de Simulados. Mudanças de posição reais
causaram reprovação e foram corrigidas, inclusive na paginação dos Simulados.
Isso não é alteração de CSS nem redesign mobile;
overflow existente em telas estreitas permanece visível e preservado.

### README — tarefa 3.1

Conferência estática por AST: 21 Models concretas; 11 arquivos SQL consecutivos
000–010. Herança confrontada com crud_mixin, diagrama e ADR-008. Corrigidos apenas
contagem, caminho único de persistência e duas instruções que terminavam em 009.
Lista das vinte funcionalidades comparada literalmente à cópia anterior;
27 links locais apontam para destinos existentes. Seções históricas, CI,
privacidade e fingerprint mantidas. Nenhum banco executado nesta conferência.

### Cobertura — tarefa 4.1

`npm run test:coverage`: **15 suítes / 182 testes aprovados**. Linhas:
**99,26% (1879/1893)**; branches: **87,98% (1325/1506)**. Gates 90%/85%
aprovados pelo validador existente; nenhum arquivo executável sem cobertura.
`api.js`: 100% de linhas e 92,85% de branches. Log em `coverage.log` (ignorado).
Não executada cobertura backend, conforme o escopo desta change.

### Correspondência dos cenários do delta — tarefa 4.2

Todos em `frontend/tests/api.test.js`:

| Cenário | Evidência |
| --- | --- |
| Leitura HTML/JSON ilegível | `rejeita JSON ilegivel`, 200/201 |
| Gravação ilegível | `nao repete POST ilegivel`, 200/201, status e mensagem |
| Sucesso raiz nula | `rejeita JSON raiz nulo`, 200/201, envelope completo |
| Nulos internos e exceção 204 | `preserva JSON valido`, objeto/lista; DELETE/logout sem ler JSON |
| Conflito estruturado | `lanca ApiError com mensagem da API`, 409 com código/detalhes |
| Erro HTTP sem JSON | `preserva erro HTTP ... JSON ilegivel`, 401/500 |
| Erro HTTP raiz nula | `preserva erro HTTP ... JSON raiz nulo`, 400/401/403/409/500 |
| Bootstrap ilegível | `impede POSTs concorrentes ... ilegivel`, duas rejeições e tentativa explícita |
| Resposta perdida após envio | `nao repete POST ilegivel`, contagem, token e consulta posterior |
| Erro válido de sessão | `sinaliza expiracao sem repetir mutacao`, evento e nova confirmação |
| Bootstrap raiz nula | `impede POSTs concorrentes ... nulo`, uma consulta/zero POSTs e promessa liberada |
| Resposta nula após envio | `nao repete POST nulo`, 200/201, sem recuperação/retry e token preservado |

`openspec validate corrigir-respostas-nulas-e-revisar-entrega --strict --json`:
**1 change válida, zero issues**. `openspec validate --specs --strict --json`:
**11 specs válidas, zero issues**. Essas validações estruturais não substituem
a etapa posterior de verificação/sincronização/arquivamento do workflow.

### E2E real — tarefa 4.1

Comando: `python test-results/corrigir-respostas-nulas-e-revisar-entrega/e2e-isolado.py`.
O auxiliar temporário inicia uma instância nova do MySQL 8.0 instalado, em porta
local livre e datadir exclusivo ignorado; confere `@@datadir`/versão e gera uma
senha aleatória apenas em memória. Não lê `.env` nem reutiliza banco operacional.
Injeta DB_* e `RUN_MYSQL_E2E=1` somente no ambiente do processo e chama uma única
vez `python scripts/run_e2e.py`, o runner existente, sem alterar a suíte.

**3/3 testes Playwright aprovados em 56,7 s**, sem retry ou respostas simuladas:

- `entrega-academica.spec.js`: vinte funcionalidades, persistência e navegação;
  18,1 s.
- `plano-simulado.spec.js`: geração/conclusão do plano, finalização/correção de
  Simulado e recálculo persistidos; 21,1 s.
- `privacidade.spec.js`: documentos, cadastro/aceite, recusa, estudo real,
  autorização, eliminação e nova autorização; 15,5 s.

Runner confirmou remoção do schema; consulta independente ao information_schema
confirmou nenhum schema E2E remanescente. Instância MySQL exclusiva encerrada.
Log em `e2e.log`; relatório existente em `test-results/e2e.json`. Capturas somente
sintéticas, sem vídeo/trace/HAR/storage state. Aviso de cores do terminal foi
inofensivo; códigos de saída da suíte e do auxiliar: 0. O E2E complementa a
conferência das sete páginas e não comprova implantação ou CI publicado.

### Revisão incremental — tarefa 4.2

`python test-results/corrigir-respostas-nulas-e-revisar-entrega/review.py`:
SHA-256 de todos os arquivos do baseline comparados ao conteúdo final.
**Zero alterações fora do escopo**: somente API, seu teste, sete HTMLs, README
e tasks desta change; único arquivo novo versionável: este relatório.
Diff incremental salvo em `incremental.diff`, ignorado. Revisados hunks de API,
teste e README; HTMLs comprovados por DOM e comparação literal salvo indentação.
`git diff --check -- <dez arquivos>`: sem erros, usando a configuração local
de normalização de finais de linha. Forçar `core.autocrlf=false` durante uma
checagem anterior marcou CRLF como whitespace; não indicava espaços no conteúdo.

Preservados literalmente os demais arquivos preexistentes, incluindo mudanças
locais anteriores em backend, specs, documentação, SQL e HTMLs legais.
Nenhuma mudança de CSS, dependência, contrato de endpoint ou dado operacional.
Nenhuma credencial/sessão incorporada ao código ou relatório. Somente conteúdo
UTF-8; sem commit, push, merge ou sincronização/arquivamento nesta etapa de apply.

**Resultado: 9/9 tarefas implementadas e validadas.** Próxima etapa do workflow:
verificar a change, depois sincronizar o delta e arquivar.
