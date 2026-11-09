# Validação da área do aluno

Data: 09/11/2026. Change: `padronizar-visual-da-area-do-aluno`.

## Escopo e estado inicial

- Dez páginas de `frontend/aluno/`, preservando textos, tags, IDs, demais atributos e ordem dos scripts. Comparação com `HEAD` por parser HTML confirmou alteração somente de classes.
- Base em `frontend/css/aluno.css`; harmonização delimitada em `desempenho.css`, `plano.css`, `tutor.css` e `privacidade.css`.
- Menu em `frontend/js/navigation.js`, sprite local `frontend/assets/aluno-icons.svg` e regressão de navegação nas duas áreas.
- Capturas anteriores: `tmp/area-aluno-visual/antes/<pagina>.html-1440.png`. Inventário: `antes/matriz.json`.
- Referências complementares consultadas em `output/imagegen/area-aluno-propostas/`. Nenhum artefato oficial de `docs/design/desktop-v1/` foi alterado.

## Comandos e resultados

| Verificação | Resultado |
| --- | --- |
| `npx vitest run frontend/tests/navigation.test.js frontend/tests/aluno-praticas.test.js frontend/tests/simulados.test.js frontend/tests/desempenho.test.js frontend/tests/aluno-plano.test.js frontend/tests/tutor.test.js frontend/tests/privacidade.test.js --coverage=false` | 7 arquivos, 132 testes aprovados |
| `npm run test:coverage` | 18 arquivos, 302 testes aprovados; 99,38% de linhas e 90,65% de branches; gates preservados |
| `python tmp/area-aluno-e2e.py` → `python scripts/run_e2e.py` | 6 testes E2E aprovados, incluindo os vinte casos da entrega; MySQL real descartável, removido pelo runner |
| `node tmp/area-aluno-visual.mjs antes` / `depois` | Dez capturas anteriores e quarenta posteriores, além das referências administrativas/pública |
| `node tmp/area-aluno-estados.mjs` | 19 estados × 4 resoluções: 76 inspeções aprovadas, com capturas adicionais de diálogos e reflow |
| `node tmp/area-aluno-teclado.mjs` | Dez páginas em desktop baixo e celular: oito links por Tab, foco visível, último destino alcançável e ativação com Enter |
| `node tmp/area-aluno-zoom.mjs` | Zoom real de 200% nas dez páginas, confirmado por `chrome.tabs.getZoom`; viewport efetiva de 720×450 a partir de 1440×900 |
| `openspec validate padronizar-visual-da-area-do-aluno --strict` | Change válida |
| `git diff --check` | Sem erros de whitespace |

O E2E recebeu `RUN_MYSQL_E2E=1` somente no subprocesso. Com autorização explícita do usuário, o preparador local carregou exclusivamente as chaves MySQL do `.env` em memória, sem exibir valores ou alterar o arquivo. O runner oficial criou seu próprio schema aleatório, aplicou migrations oficiais e confirmou a remoção ao terminar. Nenhuma conta ou banco de demonstração foi usado ou limpo. Gemini permaneceu desativado no E2E.

O aviso conhecido do JSDOM, `Not implemented: navigation to another Document`, não reprovou os testes; a navegação real também passou no Chromium.

## Matriz das dez páginas

Cada célula aprovada inclui captura, ausência de rolagem horizontal da página e preservação de blocos `hidden`. Tabelas mantêm rolagem no próprio contêiner.

| Página | 1440×900 | 1366×768 | 768×1024 | 390×844 | Zoom 200% |
| --- | --- | --- | --- | --- | --- |
| início | OK | OK | OK | OK | OK |
| questões | OK | OK | OK | OK | OK |
| questão | OK | OK | OK | OK | OK |
| histórico | OK | OK | OK | OK | OK |
| simulados | OK | OK | OK | OK | OK |
| simulado | OK | OK | OK | OK | OK |
| desempenho | OK | OK | OK | OK | OK |
| plano | OK | OK | OK | OK | OK |
| tutor | OK | OK | OK | OK | OK |
| privacidade | OK | OK | OK | OK | OK |

Evidências locais em `tmp/area-aluno-visual/`:

- `depois/<pagina>.html-<largura>.png` e `depois/matriz.json`: layout base.
- `estados/<pagina>-<estado>-<largura>.png` e `estados/matriz.json`: conteúdo renderizado pelos scripts existentes, com fixtures reutilizadas dos testes DOM.
- `depois/teclado-*.png` e `depois/teclado.json`: foco e acesso ao último item, também em desktop com 600 px de altura.
- `depois/zoom-real-*.png` e `depois/zoom.json`: ampliação nativa de 200%. Os estados com dados também foram inspecionados em 720×450 para reflow equivalente.
- `estados/*-confirmacao-*.png`: finalizar simulado, recalcular plano e revogar autorização.
- `visao-geral.png`: visão conjunta das dez páginas.

## Estados e acessibilidade

- Início com amostra pequena; desempenho com dados, vazio e erro, mantendo base, período UTC e denominadores.
- Questões disponíveis; histórico respondido; resolução e correção correta/incorreta com textos correspondentes, rádios desabilitados e ocultação da ação respondida.
- Simulados disponíveis; tentativa em andamento, resultado finalizado e correção; mapa, paginação, alternativas e confirmação preservados.
- Plano pendente/concluído e confirmação de recálculo; conclusão manual e seus metadados preservados.
- Tutor com resposta em quatro partes e indisponibilidade; avisos do provedor e rascunho preservados. A resposta visual usou fixture local, sem chamada externa.
- Privacidade autorizada/recusada, evidências SHA-256/UTC, ações explícitas e diálogo de eliminação. Autorizar/recusar mantêm o mesmo destaque; a confirmação destrutiva tem tratamento próprio.
- Nome extenso e enunciado sem espaços não encobriram ações nem excederam a página.
- Menor contraste calculado para texto visível não desabilitado nos estados: **5,50:1**, superior ao mínimo de 4,5:1.
- Nenhum botão habilitado ou link de ação/menu com altura inferior a 44 px nas 76 inspeções. Ícones decorativos não alteram nomes nem introduzem foco.
- Identidade, respostas tardias, confirmações, estados desabilitados e guardas de saída continuam cobertos pelas suítes existentes e pelo E2E.

## Isolamento e limites

As capturas de dashboard, matérias, assuntos, questões, simulados e usuários administrativos, além de login, ficaram **binariamente idênticas** às anteriores. O E2E também preservou seus percursos reais. O diff não altera backend, contratos, migrations, dependências, dados de produção nem design oficial.

As inspeções visuais isoladas usam documentos sem scripts de autenticação e fixtures sintéticas apenas em `tmp/`; não substituem o E2E com persistência real. Nenhuma fixture foi incorporada ao frontend de produção. A validação foi feita em Chromium; não afirma compatibilidade verificada com outros navegadores, leitores de tela ou dispositivos físicos.

Capturas e relatórios ficaram em `tmp/` e `test-results/`, sem traces, HAR, vídeo ou exportação de sessão autenticada. Não houve commit, push, sincronização de specs ou arquivamento nesta aplicação. O follow-up é verificar a change, sincronizar `interface-area-aluno` e então arquivar.

## Verificação e encerramento — 09/11/2026

Verificação posterior aprovada em completude, correção e coerência, sem achados críticos. O comando `python tmp/verificar-aluno-runner.py` repetiu os seis E2E oficiais e aprovou quarenta inspeções das dez páginas autenticadas com API/MySQL reais em schema descartável; o runner confirmou sua remoção. Evidências adicionais em `tmp/verificacao-aluno-real/matriz.json` e capturas da mesma pasta. As 76 inspeções de estados, vinte percursos de teclado e dez ampliações nativas a 200% também passaram. O diagnóstico de cache confirmou CSS/JavaScript atuais no servidor local; atualização sem cache é necessária em abas que conservaram estilos anteriores.

A spec `interface-area-aluno` foi sincronizada com sete requisitos e onze cenários, preservando o Purpose aprovado. Encerramento solicitado pelo usuário; commit e push continuam fora do escopo.
