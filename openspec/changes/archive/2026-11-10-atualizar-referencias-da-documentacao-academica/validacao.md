# Validação documental — referências da entrega acadêmica

Data da conferência: 10/11/2026 (America/Sao_Paulo).
Baseline: `bb9823de87f3be6ae4d0a0cb3484ff2725353d7e`.

## Escopo e ajuste autorizado

Foram atualizados somente os dois documentos previstos e os artefatos desta
change. O usuário autorizou corrigir a premissa de Models em arquivos separados:
`SimuladoTentativa`, `SimuladoResposta` e `SimuladoVersaoItem` permanecem em
`backend/app/modules/simulados/models/simulado.py`; `resultado` pertence a
`SimuladoTentativa`. `proposal.md`, `design.md` e `tasks.md` refletem esse fato. Não houve
movimentação de Models nem alteração de código, contratos, schema ou imagens.

O estado inicial de Git tinha esta change, `output/` e `tmp/` não rastreados,
sem alterações em arquivos rastreados. `output/` e `tmp/` não foram editados;
nenhum comando de limpeza foi executado. A descoberta Playwright regravou o
relatório preexistente `test-results/e2e.json`, conforme descrito ao final.
Em 10/11/2026, o usuário autorizou registrar essa ocorrência como exceção à
restrição da tarefa 3.1 sobre temporários e concluir a tarefa após as demais
checagens. Não existe cópia anterior; o relatório regenerado não é evidência
de execução dos E2E.

## Comandos e resultados

| Comando/conferência | Resultado |
| --- | --- |
| `openspec status --change atualizar-referencias-da-documentacao-academica --json` e `openspec instructions apply --change atualizar-referencias-da-documentacao-academica --json` | Schema `spec-driven`, planejamento suficiente, quatro tarefas; specs dispensadas por `skip_specs: true`. |
| `git status --short`, `git log -5 --oneline`, `git show` e `git ls-tree` no SHA de referência | Baseline confirmado; Models de Simulado já reunidas no mesmo arquivo. |
| `Get-Content -Raw -Encoding UTF8` e `rg -n` nas fontes, conventions e ADRs 006/008/010/011 | Proprietários, declarações, chamadores, transações e interfaces SQL conferidos por leitura. |
| `python -X utf8 -` com verificações em memória, usando apenas biblioteca padrão | Destinos relativos e âncoras conferidos; AST de 31 declarações em 21 arquivos, sem importar a aplicação. Chamadores, composição e herança também conferidos estaticamente. |
| Comparação documental com `git show HEAD:<arquivo>` | Três blocos Mermaid intactos (privacidade e os dois casos); todo o texto fora das tabelas dos fluxogramas preservado. As vinte linhas da matriz são idênticas ao baseline. |
| Leitura estática de `backend/app/routes.py` | Sete registros de Blueprint: Conteúdo, Práticas, Simulados, Desempenho, Contas, Plano de Estudos e Tutor IA. |
| `npm run test:e2e:list` | Exit 0: `Total: 6 tests in 6 files`. Somente descoberta, sem execução dos percursos; o reporter JSON configurado regravou `test-results/e2e.json`. |
| Leitura de `frontend/e2e/entrega-academica.spec.js` e dos outros cinco arquivos | Vinte passos numerados, IDs 1–20, no percurso acadêmico. O caso 15 continua após o 20; setups e auxiliares não foram contados como funcionalidades. |
| Consulta somente leitura ao GitHub, pelo conector, do commit e da execução 42736058343 | SHA correspondente, `status=completed` e `conclusion=success`; detalhes abaixo. |
| `git diff --check` | Exit 0, sem erros de whitespace. |
| `openspec validate --all --strict` | Exit 0: 20 itens aprovados, zero falhas (uma change e dezenove specs). |
| `git diff --name-only` e `git status --short` | Somente os dois documentos previstos entre os arquivos rastreados; alterações da change em `proposal.md`, `design.md`, `tasks.md` e neste relatório. `output/` e `tmp/` continuam preexistentes. Git não mostra o relatório ignorado regravado pela descoberta. |

As verificações Python foram executadas pela entrada padrão, sem criar scripts
permanentes ou instalar ferramentas. A conferência dos links extraiu destinos
Markdown, resolveu caminhos relativos ao documento e comparou as âncoras com
os títulos de seus destinos. A comparação com o baseline também confirmou
UTF-8 e CRLF da entrega e a preservação integral das seções a partir de
`Entrega externa`, incluindo auditorias e ressalvas históricas.

## Destinos corrigidos e símbolos

Nos fluxogramas havia **24 ocorrências de links locais inexistentes**, relativas
a 19 caminhos distintos. Todos foram corrigidos. Na tabela abaixo, caminhos
antigos e atuais são relativos a `backend/app/`.

| Caminho antigo | Destino atual |
| --- | --- |
| `auth_http.py` | `modules/contas/auth_http.py` |
| `services/autenticacao_service.py` | `modules/contas/services/autenticacao_service.py` |
| `controllers/desempenho_controller.py` | `modules/desempenho/controllers/desempenho_controller.py` |
| `services/consultar_desempenho_service.py` | `modules/desempenho/services/consultar_desempenho_service.py` |
| `services/desempenho_validacao.py` | `modules/desempenho/services/desempenho_validacao.py` |
| `repositories/consultas_desempenho.py` | `modules/desempenho/repositories/consultas_desempenho.py` |
| `repositories/desempenho_repository.py` | `modules/desempenho/repositories/desempenho_repository.py` |
| `repositories/pratica_repository.py` | `modules/praticas/repositories/pratica_repository.py` |
| `repositories/simulado_repository.py` | `modules/simulados/repositories/simulado_repository.py` |
| `repositories/questao_repository.py` | `modules/conteudo/repositories/questao_repository.py` |
| `models/pratica_tentativa.py` | `modules/praticas/models/pratica_tentativa.py` |
| `models/simulado.py` | `modules/simulados/models/simulado.py` |
| `models/questao_versao.py` | `modules/conteudo/models/questao_versao.py` |
| `controllers/simulado_controller.py` | `modules/simulados/controllers/simulado_controller.py` |
| `services/finalizar_simulado_service.py` | `modules/simulados/services/finalizar_simulado_service.py` |
| `services/pratica_validacao.py` (anunciava `corpo`) | `core/validacao.py` |
| `services/simulado_validacao.py` | `modules/simulados/services/simulado_validacao.py` |
| `services/consultar_simulado_service.py` | `modules/simulados/services/consultar_simulado_service.py` |
| `services/gestao_questao_service.py` | `modules/conteudo/services/gestao_questao_service.py` |

Conferências adicionais das tabelas:

- GET de diagnóstico e POST de finalização estão nos `routes.py` de Desempenho
  e Simulados; `app/routes.py` agrega os Blueprints. A factory aplica `/api`
  e registra `proteger_api`, que chama `AutorizarService`/`ValidarCsrfService`.
- `DesempenhoController.diagnostico` usa `servicos().desempenho.executar`.
  `compor` injeta `ConsultaMetricasMySQL` e `EscoposLeituraMySQL` em
  `ConsultarDesempenhoService`; este chama `periodo`, `metrica`, o escopo e a
  consulta. O adaptador chama `DesempenhoRepository.agregar`, que executa
  `CALL sp_desempenho_resumo` por `ContextoLeitura.executar_resultados`.
- A procedure usa `vw_praticas_fatos_desempenho` e
  `vw_simulados_fatos_desempenho`; esta referencia
  `vw_conteudo_classificacao_historica`. Bootstrap e migration 012 foram lidos.
  Não existe `DesempenhoRepository.fatos`. As projeções ORM de Práticas,
  Simulados e Conteúdo têm declarações e consumidores de equivalência; não
  foram apresentadas como consulta de produção.
- `SimuladoController.finalizar` chama `FinalizarSimuladoService.executar`.
  Este usa `corpo` de `core/validacao.py`, `revisao`/`conferir_revisao` de
  Simulados, `propria` do Service de consulta e `Repo.respostas`.
  O helper `propria` chama `SimuladoRepository.propria`.
- A finalização chama `ConsultarVersaoHistoricaService.executar`, que usa
  `QuestaoVersao.buscar_por_id`, além de `resposta.salvar(confirmar=False)`,
  `tentativa.salvar(confirmar=False)` e `tentativa.resultado()`.
  `ModeloBase.salvar` é implementado em `core/persistencia.py`, herdado pela
  cadeia de `CrudMixin`; `models/crud_mixin.py` somente reexporta as bases.
  `TransactionManager.executar` mantém a fronteira existente.
- As Models de origem permanecem nos respectivos módulos. No diagnóstico,
  representam as tabelas de origem; o retorno de produção são registros SQL,
  sem hidratação dessas Models.

Resultado final dos links locais: **59 ocorrências válidas nos fluxogramas**
e **32 na entrega**, total de **91**, com **9 âncoras** válidas. As novas
âncoras `views-públicas-de-origem` e `adendo--tutor-pontual-09112026` existem
nos títulos de destino. As sete âncoras preexistentes também foram conferidas.

## Retrato da suíte e evidência publicada

A descoberta listou um teste em cada arquivo: `entrega-academica.spec.js`,
`plano-simulado.spec.js`, `privacidade.spec.js`, `tutor.spec.js`,
`catalogo-detalhe.spec.js` e `usuarios.spec.js`. A entrega agora distingue os
seis módulos do recorte original do sétimo proprietário, Tutor IA, que não
acrescenta Model ou Repository. As 21 Models e os vinte IDs permanecem.

O [commit publicado](https://github.com/Matibas100/ProjetoSoftwarePE/commit/bb9823de87f3be6ae4d0a0cb3484ff2725353d7e)
e os metadados da [execução 42736058343](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42736058343)
foram consultados em modo somente leitura. `head_sha` e `head_commit.id`
correspondem a `bb9823de87f3be6ae4d0a0cb3484ff2725353d7e`, em `main`, evento
`push`, tentativa 1; workflow `Testes da Plataforma ENEM`, concluído com sucesso.
`updated_at=2026-11-10T01:36:40Z` corresponde a 09/11/2026 às 22:36:40 em
America/Sao_Paulo. Os dois novos links externos apontam para os recursos
confirmados pelo GitHub.

O checkpoint anterior `6f40f1303560cad908fbdd752fd0aaa4dd285b3b`, sua execução
42337772001 e data de 07/11/2026 foram mantidos, assim como os relatórios antigos.
A evidência de CI antecede esta revisão e não a valida retroativamente.

## Limites

Esta revisão comprova referências, contagens e correspondência documental.
Não executou testes unitários, integrações, E2E ou novas rotinas da aplicação;
não abriu MySQL, leu credenciais, chamou Gemini ou outros serviços de execução
do produto. A leitura de metadados publicados do GitHub serviu exclusivamente
à conferência de CI prevista na tarefa 2.2; não disparou workflow ou publicação.

O teste de Tutor cobre indisponibilidade sem Gemini, não uma resposta real de IA.
Descoberta de testes e AST não comprovam aprovação funcional. Permanecem os
limites de CRUD, exclusão física/arquivamento, Models auxiliares, auditoria SQL,
aceite docente, AWS, vídeo, slides e demonstração do grupo. Nenhum commit,
push, merge, sincronização ou arquivamento foi realizado nesta aplicação.

## Ocorrência autorizada na tarefa 3.1

O `playwright.config.js` já configura o reporter JSON com saída em
`test-results/e2e.json`. A execução obrigatória de `npm run test:e2e:list`
também escreve esse relatório: a conferência de metadados identificou o arquivo
preexistente (criado em 06/11/2026), atualizado em 10/11/2026 às 03:09:38 UTC,
no momento da descoberta. Não foi guardada cópia anterior à execução; não se
tentou reconstruir ou substituir uma evidência histórica por conteúdo presumido.

Em 10/11/2026, o usuário autorizou expressamente registrar a sobrescrita,
a inexistência de cópia anterior e a conclusão da tarefa 3.1 após as demais
checagens. Essa autorização aceita somente o efeito já ocorrido; não autoriza
novas alterações em `test-results/`. O relatório regenerado representa apenas
descoberta de testes e não deve ser apresentado como evidência de execução
ou aprovação dos E2E. A evidência funcional publicada permanece limitada ao
CI e SHA identificados acima.

## Rechecagem e conclusão da tarefa 3.1 — 10/11/2026

Após a autorização, as conferências locais foram somente de leitura. A descoberta
não foi repetida e o relatório `test-results/e2e.json` não foi alterado novamente.
Foi corrigida também a expressão residual "Models separadas" na proposta,
alinhando-a à premissa já corrigida no design e nas tarefas, sem alterar Models.

- Verificação em memória pela biblioteca padrão Python, sem importar a aplicação:
  **91 links locais e 9 âncoras válidos**, sem destinos inexistentes.
- Comparação com `HEAD`: os três blocos Mermaid e as vinte linhas numeradas
  da matriz permanecem idênticos; somente os dois documentos previstos mudaram
  entre os arquivos rastreados.
- `git diff --check`: saída 0, sem erros de whitespace.
- `openspec validate --all --strict`: **20 itens aprovados, zero falhas**,
  correspondentes à change e às dezenove specs.

As quatro tarefas estão concluídas, com a exceção de relatório explicitamente
autorizada e registrada. A próxima etapa é verificar a implementação; não há
delta specs a sincronizar. O arquivamento deve seguir essa verificação.
