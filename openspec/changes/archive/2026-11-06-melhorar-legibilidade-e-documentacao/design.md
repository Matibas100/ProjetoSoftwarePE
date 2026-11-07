# Design: limpeza de legibilidade sem mudança funcional

## Context

Motivação em [proposal.md](proposal.md). A aplicação mantém camadas e testes validados, mas parte do frontend foi escrita em linhas muito extensas e a finalização de Simulado usa abreviações que dificultam a leitura. Os imports identificados são resíduos da centralização das respostas HTTP. README/matriz ainda afirmam que a primeira publicação/CI não ocorreu, embora o checkpoint `37b9b0c` já esteja publicado e aprovado.

A reorganização de migrations está aplicada/arquivada, mas ainda local. Ela deve ser preservada integralmente, inclusive seu texto novo no README. Esta change cobre uma revisão textual delimitada, não uma limpeza automática global nem uma correção de negócio.

## Goals / Non-Goals

**Goals:** facilitar leitura dos arquivos usados pelo grupo; manter a mesma aplicação e evidências; remover ruído sem introduzir abstrações/ferramentas; tornar a documentação atual verificável.

**Non-Goals:** unificar todos os estilos do repositório, alterar interface ou funcionamento, corrigir o tratamento de JSON, extrair validadores comuns, modificar políticas de autorização, prometer nota ou produzir material de estudo.

## Decisions

### 1. Lista fechada de 25 arquivos

| Grupo | Arquivos permitidos | Alteração |
| --- | --- | --- |
| HTML, oito | `frontend/aluno/inicio.html`, `questoes.html`, `questao.html`, `historico.html`, `simulados.html`, `simulado.html`, `desempenho.html`, `plano.html` | Somente indentação/quebras de linha seguras |
| CSS, cinco | `frontend/css/aluno.css`, `auth.css`, `desempenho.css`, `plano.css`, `simulados.css` | Somente apresentação do código, sem mudança de tokens significativos |
| Controllers, oito | `backend/app/controllers/assunto_controller.py`, `autenticacao_controller.py`, `desempenho_controller.py`, `materia_controller.py`, `plano_estudo_controller.py`, `pratica_controller.py`, `questao_controller.py`, `simulado_controller.py` | Somente imports listados na decisão 3 |
| Service, um | `backend/app/services/finalizar_simulado_service.py` | Nomes locais claros e formatação |
| Documentação, três | `README.md`, `docs/technical/entrega-academica.md`, `docs/conventions/testes.md` | Atualização dos trechos desatualizados |

Na primeira coluna de HTML/CSS, os nomes abreviados continuam na mesma pasta do primeiro caminho da linha. Nenhum JS, HTML administrativo, `styles.css`, arquivo de banco, runner, teste versionado, config ou dependência deve mudar. Artefatos e `validacao.md` desta change ficam separados do delta de produto.

### 2. Formatação que preserve semântica e aparência

Usar indentação de dois espaços em HTML/CSS, blocos CSS em várias linhas, uma declaração por linha e hierarquia legível nas páginas. Preservar ordem de regras/declarações, seletores, valores, especificidade, media queries, URLs, prioridades e comentários úteis. Não ordenar propriedades, converter unidades, remover repetições, normalizar strings, cores, seletores ou atalhos CSS.

No HTML, preservar elementos, atributos/valores, IDs/classes, rótulos, textos, links e ordem dos scripts. Não acrescentar/remover wrappers. Manter conteúdo literal de `pre`, `textarea`, scripts e estilos; manter espaços significativos entre elementos inline e dentro de conteúdo renderizado com `white-space:pre-wrap`. Quebrar linhas somente em fronteiras seguras de elementos de bloco; não executar um formatador global que transforme textos da interface. A formatação não autoriza alterar o DOM funcional ou o fluxo de teclado.

Não instalar Prettier, ESLint, Ruff ou ferramentas novas nesta change. Fazer edições delimitadas com as ferramentas existentes. Scripts pontuais de comparação/QA podem ficar em `test-results/legibilidade/`, ignorado; não criar framework de formatação no repositório.

Antes/depois, comparar representação dos elementos/atributos e textos significativos com o parser DOM existente (`jsdom`). Não aceitar uma normalização que simplesmente remova todos os espaços e esconda mudança visível. Conferir CSS com parser já disponível no ambiente de QA ou CSSOM do navegador, preservando sequência de regras, seletores e declarações; complementar com inspeção de strings/URLs/comentários e comparação textual. Não usar apenas substituição global de whitespace como prova.

Como `auth.css` também afeta login e administração, executar os testes DOM existentes e verificar essas telas mesmo sem editar seus HTML. Durante o E2E real, conferir capturas já produzidas e complementar inspeção de desempenho, resolução/resultado de Simulado e login em 1440/390 px. Para capturas complementares, pode-se usar comando de QA temporário pelo `executar_suite` do runner, aproveitando schema/contextos sintéticos; não mudar runner/testes versionados ou usar banco operacional. Registrar quais telas foram efetivamente inspecionadas. Se a formatação alterar layout/texto, corrigir a formatação, não ajustar os estilos ou expectativas.

### 3. Remoção mínima de imports sem uso

Inventário confirmado na exploração, a revalidar no apply:

| Controller | Nomes a remover |
| --- | --- |
| Assunto | `jsonify`, `resposta_json_dinamica` |
| Autenticação | `ConsultarSessaoService` |
| Desempenho | `jsonify`, `resposta_json_dinamica` |
| Matéria | `jsonify`, `resposta_json_dinamica` |
| Plano de Estudo | `jsonify`, `resposta_json` |
| Prática | `jsonify`, `resposta_json` |
| Questão | `resposta_json_dinamica` |
| Simulado | `jsonify`, `resposta_json` |

A análise de AST encontrou 14 nomes sem uso local. Conferir também imports/patches externos antes da remoção: um nome oferecido deliberadamente como reexportação não é descartável só porque não aparece como `Name` no módulo. Se um item tiver consumidor legítimo, preservá-lo e registrar a exceção; não alterar consumidores para justificar a limpeza. Nenhuma função/classe/decorator/corpo do Controller muda, e não se remove o helper que ele efetivamente executa.

Verificar por AST que o delta dos Controllers contém somente remoções dessa lista e executar os unitários existentes de HTTP/Controllers. Não aplicar remoção automática de imports nos módulos de migrations, que possuem reexportações deliberadas.

### 4. Finalização com nomes claros e mesma execução

No `FinalizarSimuladoService`, substituir somente variáveis locais abreviadas: `t` por `tentativa`, `r` por `resposta`, `i` por `item` e `q` por `versao_historica`. Manter alias/imports e todos os nomes públicos, parâmetros, atributos de Models e chaves de payload. O nome local `valor` pode ficar `revisao_recebida`. Separar operações com ponto e vírgula em linhas próprias e quebrar expressões longas com parênteses, sem extrair novas funções/classes ou mudar a fórmula.

Preservar a sequência exata: corpo/revisão/confirmação; iniciar `TransactionManager`; obter tentativa própria com lock; replay antes da revisão; conferir revisão; respostas com lock; tratar branco; buscar gabarito histórico; corrigir e salvar resposta sem commit; atribuir totais/percentual/estado/instante/revisão; salvar tentativa sem commit; montar resultado; commit único externo antes do sucesso. O denominador continua sendo todas as Questões, com `Decimal` e `ROUND_HALF_UP`. Não acrescentar evento, SQL, validação ou novo tratamento de erro.

Comparar AST antes/depois com mapeamento explícito somente desses nomes locais e ignorando coordenadas de origem. O restante, inclusive a ordem das atribuições/chamadas/decisões, deve ser idêntico. A comparação é QA temporário, não teste permanente que espelha a implementação. Usar os testes existentes para cenários reais de replay, revisão obsoleta, branco, rollback, propriedade e correção persistida.

### 5. Documentação atual com referência verificável

No README, substituir as afirmações atuais de CI ainda não executado/nenhum push autorizado por um registro datado e ligado ao checkpoint [37b9b0c](https://github.com/Matibas100/ProjetoSoftwarePE/commit/37b9b0ccf0bb4640527628b7f719c14ec987e0fe) e à [execução aprovada](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42315102152). Esse resultado pertence àquele SHA, não valida automaticamente a reorganização local de migrations ou esta limpeza. Conferir via consulta somente leitura ao GitHub antes de afirmar estado remoto novo.

Evitar substituir uma informação obsoleta por outra que também envelheça sem contexto: registrar o checkpoint comprovado, indicar que alterações posteriores seguem o estado Git/Actions e manter a regra permanente de operações Git dependerem de autorização explícita. Esta change não possui autorização de commit/push/merge. Não sobrescrever a documentação de migrations ainda não commitada.

Na matriz, apontar para esse registro do README, reduzindo duplicação de estado. Preservar evidências históricas, links dos relatórios anteriores, as vinte linhas e a distinção entre atividade anterior (vídeo até cinco minutos) e rubrica final (quatro funcionalidades principais não CRUD, até dois minutos).

Na convenção de testes, substituir a descrição limitada a quatro scripts clássicos por uma descrição das suítes DOM/contrato atuais de API, autenticação, navegação e áreas Aluno/Admin. Manter os 29 casos como referência histórica e os gates/opt-ins; não inventar uma nova contagem de testes sem execução nem reescrever relatórios de changes arquivadas.

### 6. Evidência proporcional, preservação e regressão

No preflight do apply, guardar baseline dos arquivos não sensíveis, AST, representações de markup/CSS e cópias dos arquivos afetados em `test-results/legibilidade/`. Registrar alterações preexistentes, em particular migrations e README. Não incluir `.env`, credenciais ou conteúdo de `tmp/` nos artefatos. Conferir hashes dos demais arquivos rastreados e dos novos módulos de migrations locais para garantir preservação.

Validação incremental por grupo: comparação estrutural e regressão DOM para frontend; AST e unitários de Controllers/Simulado para Python; links/conteúdo para documentação. Não escrever testes novos para espelhar espaços, strings de README ou nomes locais.

Antes de concluir, executar uma vez cada validação integrada:

1. `python backend/tests/run_backend_coverage.py` com os opt-ins de integração e migrations apenas no processo, MySQL real e gates 90%/85% intactos. Inclui o Service sensível alterado e os Controllers; schemas de teste devem ser limpos. Não declarar que testes históricos substituem essa execução.
2. `npm run test:coverage`, preservando testes/thresholds e verificando que HTML/CSS continuam aceitos e todos os scripts executáveis permanecem cobertos.
3. `npm run test:e2e` pelo runner oficial, com `RUN_MYSQL_E2E=1` e configuração somente no processo. Conferir os dois testes, cancelamentos, foco, resultados e capturas; limpeza de schema/processos em sucesso ou falha. Complementar QA visual com o mecanismo temporário descrito na decisão 2, sem repetir a suíte inteira apenas para screenshots.
4. Links, lista/matriz de vinte funcionalidades, `git diff --check`, inventário/AST/hashes e `openspec validate melhorar-legibilidade-e-documentacao --strict`. Revisar com a skill de verificação e registrar comandos, resultados e telas efetivamente inspecionadas em `validacao.md`.

Não executar operações contra o banco operacional. Usar configuração já disponível pelos mecanismos autorizados, sem abrir/expor `.env`, exportar sessões ou persistir segredos. Indisponibilidade de infraestrutura impede afirmar aprovação; não recorrer a SQLite/mocks em integração. Qualquer necessidade de alterar comportamento, layout ou expectativas dos testes exige reavaliar a proposta antes de seguir.

## Risks / Trade-offs

- **Whitespace muda texto/fluxo inline:** formatar somente fronteiras seguras, preservar conteúdo literal e comparar textos significativos/DOM, além de inspeção visual.
- **CSS equivalente em aparência inicial, mas diferente na cascata:** preservar ordem/tokens, regras responsivas e prioridades; comparar estrutura e conferir 1440/390 px.
- **Nome aparentemente sem uso é reexportado:** pesquisar consumidores/patches e preservar exceções justificadas; não ampliar remoção a outros módulos.
- **Renomeação modifica a finalização:** AST com mapeamento de nomes locais e regressões de sucesso/replay/rollback existentes; manter exatamente a ordem transacional.
- **Estado documental confunde CI antigo e código local:** associar resultado ao SHA/execução verificável, sem declarar aprovação remota do que não foi enviado.
- **Limpeza cresce sem benefício:** lista fechada de arquivos, sem ferramentas novas, extração de helpers ou reforma global de JS/Services.

## Migration Plan

Nenhuma migration, mudança de procedure, contrato ou deploy. Aplicar a limpeza em grupos verificáveis, mantendo a reorganização de migrations e outros arquivos preexistentes intactos. Para desfazer este delta, restaurar somente os trechos/arquivos deste baseline, sem reset/stash ou reversão de alterações legítimas posteriores.

Após verificação sem achados críticos, registrar sync não aplicável (`skip_specs: true`) e arquivar pela skill apropriada. A correção de JSON inválido permanece como próximo trabalho funcional independente, sem implementação nesta change. Publicação/AWS e guia de estudo continuam fora do escopo.
