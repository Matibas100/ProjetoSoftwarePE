# Validação da formatação

Data: 09/11/2026. Change: `padronizar-formatacao-do-codigo`, schema `spec-driven`.
Baseline: `663891af9f6b0cbe7c1df0b7841e104ae7f2cbf1` (igual ao HEAD no início).

## Escopo e preservação

O inventário fechado selecionou 359 arquivos. Não havia diferença local de conteúdo
nesses arquivos em relação ao baseline; diferenças de checkout LF/CRLF foram
consideradas sem normalizar o repositório. Foram ajustados 241 arquivos e mantidos
118 byte a byte. Somente a convenção ganhou texto; os demais ajustes são de formatação.

O snapshot privado, fontes e manifestos SHA-256 estão em `tmp/formatacao-codigo/`.
Nenhum `.env`, arquivo de credenciais, senha ou estado autenticado foi lido ou
copiado para esse snapshot. Os 362 arquivos protegidos não sensíveis mantêm seus
hashes: SQL, termos legais, referências SQL, demais assets, dependências/locks,
fixtures não executáveis, CI, skills, documentação oficial, specs e histórico.
Os arquivos e diretórios locais preexistentes em `tmp/` e `output/` foram preservados.

| Grupo | Ajustados | Intactos |
| --- | ---: | ---: |
| Aplicação Python e entrada | 106 | 87 |
| Ferramentas Python de banco | 4 | 1 |
| Testes e runners Python | 61 | 10 |
| JavaScript de produção | 18 | 1 |
| HTML | 9 | 13 |
| CSS e sprites | 12 | 1 |
| Testes JavaScript/E2E e configurações | 26 | 2 |
| Scripts | 4 | 2 |
| Convenção | 1 | 0 |
| Makefile | 0 | 1 |

## Comparação estrutural

- **Python:** 273 fontes comparados com `ast.parse(type_comments=True)`, sem
  posições; somente posições de `TypeIgnore` normalizadas. Ordem, nomes,
  operações, literais, comentários e diretivas preservados. Tokens de f-strings,
  strings e comentários comparados integralmente; parênteses de imports,
  vírgulas de apresentação e separadores de instruções não substituem o gate AST.
- **JavaScript:** 49 fontes (`.js`/`.mjs`) comparados por `@babel/parser`.
  AST sem metadados de posição, todos os tokens brutos e comentários iguais;
  diretivas, regexes, templates, declarações, callbacks e ordem preservados.
- **CSS:** 11 fontes comparados por árvore PostCSS ordenada (seletores,
  propriedades, valores, prioridades, parâmetros e comentários) e por árvore
  css-tree serializada; sem ordenação de regras/propriedades.
- **HTML:** 22 documentos comparados com parse5, em ordem, incluindo atributos,
  textos e conteúdo sensível. Apenas whitespace entre blocos sem texto foi
  normalizado na comparação; espaços inline e conteúdo de `pre`, `textarea`,
  `option`, scripts e estilos foram preservados.
- **SVG:** os dois sprites próprios mantêm todas as tags/atributos em ordem,
  byte a byte; somente whitespace entre elementos foi ajustado.
- **Makefile:** permaneceu byte a byte, com receitas/tabulações e atalhos
  conferidos contra `docs/conventions/testes.md`.

Ferramentas auxiliares temporárias usam bibliotecas já disponíveis: biblioteca
padrão Python, Babel, parse5, PostCSS, css-tree e Playwright. Nenhuma instalação,
dependência, configuração ou gate de CI foi acrescentado ao projeto. Os auxiliares
ficam fora do código de produção, em `tmp/formatacao-codigo/`.

## Testes por etapa

Os logs e resultados JSON ficam no mesmo diretório temporário. Todas as execuções
usaram UTF-8, `PYTHON_DOTENV_DISABLED=1`, `PYTHONPATH=backend`, chave Gemini vazia
e Tutor externo desabilitado. Não houve chamada real ao Gemini.

| Etapa | Comando | Resultado |
| --- | --- | --- |
| Aplicação | `python backend/tests/run_unit.py` | 202 testes passaram |
| Ferramentas de banco | `python -m unittest discover -s backend/tests -p '*migration*integration.py'` | 48 integrações passaram em MySQL real |
| JavaScript público | Vitest: API, autenticação, navegação, app, assuntos e questões | 86 testes passaram |
| JavaScript Aluno | Vitest: práticas, plano, simulados, desempenho, privacidade e tutor | 112 testes passaram |
| JavaScript Administração | Vitest: páginas, questões, usuários e detalhe do catálogo | 99 testes passaram |
| Contratos HTML | Vitest: contrato HTML e áreas afetadas | 112 testes passaram |
| Testes Python formatados | `python backend/tests/run_unit.py` | 202 testes passaram |
| Testes JavaScript formatados | `npm run test:unit` | 302 testes em 18 arquivos passaram |
| Descoberta E2E | `npm run test:e2e:list` | Mesmos 6 casos nos mesmos 6 arquivos; só posições mudaram |
| Scripts Python | `python -m unittest discover -s scripts/tests` | 7 testes passaram |

O MySQL 8.0.44 foi iniciado com o executável já instalado, `--no-defaults`, datadir
novo em `tmp/formatacao-codigo/mysql-data` e porta local livre. Cada execução gerou
usuário/senha efêmeros somente em memória e nas variáveis do processo filho.
Os runners oficiais criam/removem seus schemas API/migration/E2E descartáveis;
nenhuma conexão foi feita ao serviço MySQL da demonstração. Os opt-ins
`RUN_MYSQL_INTEGRATION=1`, `RUN_MYSQL_MIGRATION_INTEGRATION=1` e
`RUN_MYSQL_E2E=1` existiram somente nos processos de validação.

As tentativas iniciais do comando direto de migrations identificaram ausência de
`PYTHONPATH` e a exigência de senha não vazia pelo parser de configuração. O
ambiente auxiliar foi corrigido e o comando foi executado integralmente com êxito;
nenhum contrato, teste ou configuração da aplicação precisou mudar.

## Regressão final

- **Backend:** `python backend/tests/run_backend_coverage.py`; saída 0; 648.76 s.
- **Frontend:** `npm.cmd run test:coverage`; saída 0; 20.93 s.
- **E2E real:** `npm.cmd run test:e2e`; saída 0; 73.7 s.

Gates originais preservados: pelo menos 90% de linhas e 85% de branches em cada
stack; nenhuma assertion, fixture, cenário, filtro ou threshold foi alterado.

Frontend: **99,16% de linhas; 90,65% de branches**, 302 testes aprovados.

Backend: **97.81% de linhas (4870/4979); 92.79% de branches (1030/1110)**, conforme o validador oficial de produção.

A suíte final aprovou **202 testes unitários e 220 integrações MySQL (422 testes backend)**, incluindo os 29 casos originais. O E2E aprovou os seis cenários completos.

Após os testes, foi confirmada a ausência de schemas descartáveis restantes e o MySQL temporário foi encerrado.

## Comparação visual

Comparadas **60 combinações de página/estado/largura**, com 60 idênticas. Cada comparação confronta PNG integral, texto renderizado e geometria/visibilidade
de todos os elementos em Chromium, em 1440 e 390 px. Capturas e inventário ficam
em `tmp/formatacao-codigo/visual/` e `visual.json`.

Foram incluídas as 22 páginas elegíveis e as três páginas legais que consomem CSS
formatado, além de estados de resposta de Questão, resultado/correção de Simulado,
resposta do Tutor e modal administrativo. Menus de ações foram conferidos abertos.
Formulários, navegação e componentes existentes foram inspecionados nas capturas.
Algumas páginas administrativas já excedem a largura de 390 px; essa largura
mínima/rolagem horizontal permanece igual ao baseline. Não foi feita correção
responsiva fora do escopo de formatação.

Fixtures sintéticas foram derivadas dos testes existentes e aplicadas igualmente
antes/depois; sem login real, cookie, token ou exportação de sessão. Esses ensaios
comprovam aparência; os fluxos persistidos são comprovados pelo E2E oficial em
MySQL real, incluindo os vinte casos da entrega. Sem HAR, traces ou vídeo.

## Exceções deliberadas de apresentação

- Literais SQL, mensagens, URLs, regexes e templates permanecem intactos e podem
  exceder aproximadamente 100 caracteres. Imports extensos com um único símbolo
  permanecem em uma linha quando não há ganho de leitura.
- As cláusulas JavaScript sem bloco permanecem sem adicionar chaves: isso
  preserva exatamente a AST. Declarações com múltiplas variáveis mantêm um único
  nó de declaração; somente a disposição pode mudar.
- Em HTML, conteúdo misto com elementos inline permanece compacto quando inserir
  quebras poderia criar espaços visíveis. Scripts externos mantêm suas tags
  reconhecíveis pelos consumidores atuais.
- Espaçamento de valores/propriedades customizadas CSS, comentários e conteúdo
  sensível não foi normalizado. Nenhum valor, seletor, prioridade ou desenho mudou.
- `Makefile`, `playwright.config.js`, `vitest.config.js`, `scripts/serve_frontend.py`
  e `scripts/install-git-hooks.mjs` já estavam organizados e permaneceram intactos.

## Revisão e workflow

Diff revisado por grupos, com equivalência estrutural e hashes protegidos sem
divergência. Nenhum arquivo versionado excluído/renomeado, mudança funcional,
dependência nova, alteração de dados operacionais ou segredo acrescentado.
`git diff --check` e `openspec validate padronizar-formatacao-do-codigo --strict`
passaram. A validação OpenSpec aceita zero deltas conforme `skip_specs: true`.

## Verificação final e correção dos avisos

Os dois avisos da verificação foram corrigidos em 09/11/2026:

- O relatório passou a usar a última síntese de cobertura do processo, que é a
  produção real: 97,81% de linhas e 92,79% de branches. As sínteses anteriores de
  100% e 0% pertencem às fixtures dos testes do validador.
- Os quatro blocos foram realinhados em `admin-assuntos.js`, `aluno-praticas.js`,
  `entrega-academica.spec.js` e `plano-simulado.spec.js`. Somente a indentação de
  oito linhas mudou; AST, tokens, comentários e literais continuam equivalentes.

A rechecagem confirmou zero blocos de controle JavaScript desalinhados nos 49
fontes elegíveis. Os 91 testes das três suítes afetadas passaram com
`npm run test:unit -- frontend/tests/admin-pages.test.js frontend/tests/admin-catalogo-detalhe.test.js frontend/tests/aluno-praticas.test.js`.
`npm run test:e2e:list` continuou descobrindo os mesmos seis cenários.

As comparações de Python, JavaScript, HTML, CSS e SVG e os 362 hashes protegidos
foram reconferidos; `git diff --check` e a validação OpenSpec estrita passaram.
A regressão completa do apply permanece como evidência: os ajustes posteriores
foram somente de indentação e documentação, comprovados por AST/tokens e pelos
testes dirigidos. Os logs adicionais estão em `tmp/formatacao-codigo/revisao-*.log`.

Verificação concluída: completude, correção e coerência atendidas, sem achados
pendentes. Não há specs a sincronizar (`skip_specs: true`). Arquivamento pelo CLI,
sem commit, push ou merge.

## Arquivos elegíveis mantidos byte a byte

```text
Makefile
backend/app/__init__.py
backend/app/config.py
backend/app/contexto_leitura.py
backend/app/contracts/__init__.py
backend/app/core/__init__.py
backend/app/core/controllers/__init__.py
backend/app/core/controllers/health_controller.py
backend/app/core/paginacao.py
backend/app/core/persistencia.py
backend/app/core/relogio.py
backend/app/core/services/__init__.py
backend/app/core/services/health_check_service.py
backend/app/exceptions.py
backend/app/extensions.py
backend/app/http_composition.py
backend/app/models/crud_mixin.py
backend/app/modules/__init__.py
backend/app/modules/contas/__init__.py
backend/app/modules/contas/api.py
backend/app/modules/contas/controllers/__init__.py
backend/app/modules/contas/domain/__init__.py
backend/app/modules/contas/models/__init__.py
backend/app/modules/contas/models/auth_limite.py
backend/app/modules/contas/models/usuario.py
backend/app/modules/contas/repositories/__init__.py
backend/app/modules/contas/services/__init__.py
backend/app/modules/contas/services/buscar_aluno_admin_service.py
backend/app/modules/contas/services/consultar_privacidade_service.py
backend/app/modules/contas/services/criar_aluno_admin_service.py
backend/app/modules/conteudo/__init__.py
backend/app/modules/conteudo/controllers/__init__.py
backend/app/modules/conteudo/domain/__init__.py
backend/app/modules/conteudo/domain/catalogo.py
backend/app/modules/conteudo/models/__init__.py
backend/app/modules/conteudo/repositories/__init__.py
backend/app/modules/conteudo/services/__init__.py
backend/app/modules/conteudo/services/atualizar_materia_service.py
backend/app/modules/conteudo/services/buscar_assunto_por_id_service.py
backend/app/modules/conteudo/services/buscar_materia_por_id_service.py
backend/app/modules/conteudo/services/buscar_questoes_por_assunto_service.py
backend/app/modules/conteudo/services/catalogo_validacao.py
backend/app/modules/conteudo/services/criar_materia_service.py
backend/app/modules/conteudo/services/deletar_assunto_service.py
backend/app/modules/conteudo/services/deletar_materia_service.py
backend/app/modules/conteudo/services/impacto_catalogo_service.py
backend/app/modules/conteudo/services/listar_areas_enem_service.py
backend/app/modules/conteudo/services/listar_assuntos_service.py
backend/app/modules/conteudo/services/listar_materias_service.py
backend/app/modules/desempenho/__init__.py
backend/app/modules/desempenho/api.py
backend/app/modules/desempenho/controllers/__init__.py
backend/app/modules/desempenho/repositories/__init__.py
backend/app/modules/desempenho/services/__init__.py
backend/app/modules/plano_estudos/__init__.py
backend/app/modules/plano_estudos/api.py
backend/app/modules/plano_estudos/controllers/__init__.py
backend/app/modules/plano_estudos/models/__init__.py
backend/app/modules/plano_estudos/repositories/__init__.py
backend/app/modules/plano_estudos/services/__init__.py
backend/app/modules/plano_estudos/services/concluir_plano_item_service.py
backend/app/modules/plano_estudos/services/eliminar_planos_proprios_service.py
backend/app/modules/plano_estudos/services/plano_validacao.py
backend/app/modules/plano_estudos/services/recalcular_plano_service.py
backend/app/modules/praticas/__init__.py
backend/app/modules/praticas/api.py
backend/app/modules/praticas/controllers/__init__.py
backend/app/modules/praticas/models/__init__.py
backend/app/modules/praticas/repositories/__init__.py
backend/app/modules/praticas/services/__init__.py
backend/app/modules/praticas/services/listar_questoes_aluno_service.py
backend/app/modules/praticas/services/pratica_validacao.py
backend/app/modules/simulados/__init__.py
backend/app/modules/simulados/api.py
backend/app/modules/simulados/controllers/__init__.py
backend/app/modules/simulados/models/__init__.py
backend/app/modules/simulados/repositories/__init__.py
backend/app/modules/simulados/services/__init__.py
backend/app/modules/simulados/services/listar_historico_simulados_service.py
backend/app/modules/tutor_ia/__init__.py
backend/app/modules/tutor_ia/api.py
backend/app/modules/tutor_ia/controllers/__init__.py
backend/app/modules/tutor_ia/domain/__init__.py
backend/app/modules/tutor_ia/routes.py
backend/app/modules/tutor_ia/services/__init__.py
backend/app/routes.py
backend/app/transaction_manager.py
backend/database/migration_types.py
backend/run.py
backend/tests/__init__.py
backend/tests/fixtures/coverage_project/backend/app/module.py
backend/tests/fixtures/coverage_project/backend/run.py
backend/tests/fixtures/statements/docstring_only.py
backend/tests/fixtures/statements/import_only.py
backend/tests/run_backend_coverage.py
backend/tests/sql_observer.py
backend/tests/test_assuntos_integration.py
backend/tests/unit/__init__.py
backend/tests/unit/test_coverage_validator.py
frontend/admin/assuntos.html
frontend/admin/dashboard.html
frontend/admin/materias.html
frontend/admin/questao.html
frontend/admin/questoes.html
frontend/admin/simulado.html
frontend/admin/simulados.html
frontend/aluno/desempenho.html
frontend/aluno/historico.html
frontend/aluno/inicio.html
frontend/aluno/questoes.html
frontend/aluno/simulado.html
frontend/aluno/simulados.html
frontend/css/styles.css
frontend/js/navigation.js
playwright.config.js
scripts/install-git-hooks.mjs
scripts/serve_frontend.py
vitest.config.js
```
