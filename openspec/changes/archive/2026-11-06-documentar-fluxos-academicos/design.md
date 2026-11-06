# Design: fluxogramas de consulta e entrada de dados

## Context

Ver `proposal.md` para motivação e escopo. Os fluxos foram rastreados no código local após a change SOLID, sem alterar a implementação. A rubrica pede fluxogramas, não apenas um desenho genérico das pastas nem diagramas de sequência isolados. Os dois casos escolhidos já incluem consultas especializadas reais e permitem mostrar Repository sem contrariar CRUD Active Record.

Há um aviso incorreto na página de desempenho e duas referências operacionais atuais ao Plano indisponível. Agenda, redação, tutor, TRI e recomendações avançadas continuam fora do recorte; o Plano básico de prioridades existe. Documentação histórica e artefatos oficiais permanecem preservados.

## Goals / Non-Goals

**Goals:** entregar dois fluxogramas legíveis e rastreáveis ao código, incluindo decisões/retorno; tornar a informação atual sobre o Plano coerente na interface e nos documentos de operação.

**Non-Goals:** redesenhar os fluxos, mudar transações ou regras para facilitar o desenho, criar Repository de CRUD, acrescentar recursos, montar apresentação/vídeo ou executar publicação. Não recontar esses documentos como funcionalidades adicionais.

## Decisions

### 1. Um documento versionável com dois fluxogramas independentes

Criar `docs/technical/fluxogramas-casos-de-uso.md`, com introdução curta relacionando os dois exemplos aos critérios de recuperação/entrada da rubrica. Cada seção terá objetivo, perfil/pré-condições, tela/ação, método/rota, fluxograma Mermaid `flowchart`, explicação das decisões e tabela de rastreabilidade com links relativos para arquivos reais.

Usar início/fim, processos, decisões e setas direcionais rotuladas; organizar por camadas em subgraphs quando melhorar a leitura. Labels curtos; a tabela apresenta nomes completos dos símbolos e detalhes sem sobrecarregar o desenho. Usar UTF-8 e português brasileiro; as setas/sintaxe Mermaid e eventuais diagramas ASCII preservam caracteres ASCII. Incluir fluxo de retorno do banco até a interface, não terminar em MySQL.

O fonte Markdown/Mermaid é o artefato permanente. Renderizar ambos para inspeção visual com a ferramenta Mermaid já utilizada pelo projeto; saídas de QA ficam em `test-results/` ignorado, não em `docs/design/desktop-v1/`. Nenhuma dependência de produção será adicionada. Não criar diagramas de sequência no lugar dos fluxogramas exigidos.

Alternativa rejeitada: duas imagens sem fonte editável ou um único fluxo abstrato para os dois casos. Isso dificulta manutenção e não comprova as decisões reais de cada operação.

### 2. Recuperação: consultar o diagnóstico de desempenho

**Entrada:** `/aluno/desempenho.html`, carregamento inicial ou formulário `dash-filtros`, com período opcional. **Requisição principal:** `GET /api/aluno/desempenho`, sem usuário alvo enviado pelo cliente. O padrão é o período atual de trinta dias UTC.

Representar esta sequência observada:

1. Interface (`frontend/js/desempenho.js`) verifica o contexto de identidade, inicia carregamento e chama `apiRequest`; a rota está registrada em `backend/app/routes.py`.
2. Proteção da API verifica sessão e perfil Aluno. Anônimo/perfil inadequado interrompem com 401/403, antes do Controller. GET não exige CSRF. Verificações auxiliares de identidade podem ser resumidas num bloco, sem inventar uma rota de autenticação nova.
3. `DesempenhoController.diagnostico` lê filtros e usuário da sessão e chama a instância `servicos().desempenho` da composição.
4. `ConsultarDesempenhoService` usa `EscoposLeitura`; a implementação `EscoposLeituraMySQL` delega a `ContextoLeitura.usar`. O código abre o escopo antes de validar o período: não desenhar uma ordem diferente. Datas/filtros inválidos retornam 400 e liberam o escopo, sem executar agregações acadêmicas.
5. O Service chama `ConsultaMetricasDesempenho`; `ConsultaMetricasMySQL` delega a `DesempenhoRepository.agregar`, que usa projeções de `PraticaRepository`, `SimuladoRepository` e classificação histórica de `QuestaoRepository`.
6. Repositories usam os mapeamentos de `PraticaTentativa`, `SimuladoTentativa`, `SimuladoResposta`, `SimuladoVersaoItem` e `QuestaoVersao`. Consultas são executadas no MySQL pelo contexto consistente de leitura. Não existe Model/tabela de métrica persistida, nem chamada de salvar/deletar nessa recuperação; Models aparecem como mapeamentos das fontes, não como CRUD artificial entre Service e Repository.
7. MySQL devolve contagens/grupos; adaptador normaliza os registros; Service calcula percentual/estado da amostra e monta o diagnóstico. Escopo próprio é liberado; Controller retorna JSON 200; interface apresenta os blocos.

Decisões principais do desenho: acesso autorizado? período válido? consulta concluída? há respostas? Sem dados é sucesso 200 com `sem_dados`, percentual null e listas vazias, não 404 nem 0% inventado. Amostra de 1–4 e limiar 5 podem ser explicados em nota ao fluxo sem multiplicar excessivamente nós. Falha de consulta resulta em 500 sem payload parcial e erro/tentar novamente na tela.

Explicar a distinção entre leitura acadêmica e infraestrutura: o diagnóstico não grava resultados de aprendizagem, mas a proteção de sessão pode renovar seu registro. Não afirmar que todo GET é absolutamente isento de escrita em qualquer tabela. Composição/Protocol são ligações técnicas, não novos passos de persistência.

Alternativa rejeitada: consultar somente uma lista cadastral. O diagnóstico mostra recuperação com agregação real, período, regras e camadas, sem ser confundido com uma tela CRUD isolada.

### 3. Entrada: finalizar uma tentativa de Simulado

**Entrada:** `/aluno/simulado.html?tentativa_id=<id>`, botão `sim-finalizar` e confirmação. **Requisição:** `POST /api/aluno/tentativas-simulado/<id>/finalizar`, corpo `{revisao, confirmar:true}`. Identidade é obtida da sessão.

Representar esta sequência observada:

1. `frontend/js/aluno-simulados.js` impede finalizar com alternativa local não salva; a confirmação informa a quantidade de brancos. Cancelar volta à tentativa sem POST. Confirmar chama `apiRequest` com revisão corrente e token CSRF.
2. A rota e a proteção HTTP verificam sessão/perfil, origem e CSRF. Recusa 401/403 não inicia o caso de uso. Não inventar exigência de reautenticação recente para finalizar: ela não pertence a esse contrato.
3. `SimuladoController.finalizar` interpreta o JSON e chama `FinalizarSimuladoService.executar`. O Service valida estrutura, revisão positiva e confirmação explícita; dados inválidos retornam 400 antes da transação acadêmica.
4. `TransactionManager.executar` delimita a operação. A função `propria` usa `SimuladoRepository.propria` com lock e filtro do usuário. Tentativa ausente/alheia produz o mesmo 404, com rollback do caso composto.
5. Se a tentativa já está finalizada, retornar seu resultado persistido, sem recalcular. Essa decisão ocorre **antes** de comparar a revisão recebida com a revisão da tentativa. A transação libera locks ao terminar; replay não recria nem altera o resultado.
6. Em andamento, conferir revisão atual; divergência retorna 409 com rollback. `SimuladoRepository.respostas(..., bloquear=True)` obtém respostas/itens; `ConsultarVersaoHistoricaService` fornece o gabarito da versão usada por meio da Model `QuestaoVersao`.
7. Para cada resposta, distinguir branco de alternativa respondida. O Service calcula correção, acertos, erros, brancos, total e percentual sobre **todas** as Questões. `SimuladoResposta.salvar(confirmar=False)` grava as correções respondidas; `SimuladoTentativa.salvar(confirmar=False)` grava totais/estado/revisão/data.
8. `TransactionManager` executa commit único. Somente depois de sucesso, Controller retorna JSON 200 e a interface mostra o resultado salvo. Qualquer falha na operação ou no commit executa rollback, sem resultado acadêmico parcial. A tela permite nova ação explícita, sem replay automático de escrita.

O fluxograma distingue decisão no frontend, controle de acesso, validação de entrada, consulta/lock no Repository, regras no Service, persistência nas Models e commit na infraestrutura. Não desenhar Repository salvando o CRUD nem Service executando SQL. Não acrescentar evento de auditoria de finalização ou gravação em `SimuladoEvento`, pois essa operação não os produz.

Alternativa rejeitada: cadastro simples como exemplo de entrada. Finalização é uma ação não CRUD e já percorre as duas formas corretas de persistência: consulta especializada/lock e gravação Active Record.

### 4. Correção textual e coerência operacional

No aviso de `frontend/aluno/desempenho.html`, preservar as frases sobre ausência de respostas, repetições e limiar operacional. Substituir somente a frase final por: `Redação, tutor e recomendações avançadas ainda estão indisponíveis.` Não inserir nova ação/link, mudar menu, CSS, IDs ou scripts. O link existente ao Plano permanece no menu compartilhado.

Em `operacao-desempenho.md` e `operacao-simulados.md`, retirar a indicação global de Plano indisponível e apontar por link relativo para `operacao-plano-estudos.md`. Explicar que existe o Plano básico de prioridades para prática; agenda, duração/reagendamento, geradores, TRI e integrações avançadas continuam limitados conforme o documento próprio. Corrigir a referência a "futuro plano" no contrato de leitura do documento de desempenho para refletir o consumidor já existente, sem mudar o contrato técnico descrito.

Não executar substituição indiscriminada por todo o repositório: arquivos de histórico e avisos específicos de indisponibilidade de conteúdo devem permanecer. `frontend/aluno/inicio.html` informa agenda indisponível corretamente e não será alterado.

Alternativa rejeitada: remover todos os avisos de limites. Isso passaria a sugerir disponibilidade de recursos ainda não implementados.

### 5. Descoberta e rastreabilidade dos artefatos

README receberá um link para os fluxogramas junto das referências de arquitetura/diagrama; `entrega-academica.md` receberá uma seção curta relacionando recuperação e entrada aos dois fluxos. Preservar as vinte entradas, a distinção de casos adicionais e os registros históricos de validação.

Usar links relativos reais para HTML/JS, routes, proteção HTTP, Controllers, Services, contratos/adaptadores, Repositories, Models e infraestrutura necessária. Não duplicar integralmente a matriz acadêmica ou as specs. Não copiar o DOCX da rubrica para o repositório nem apontar para o caminho de Downloads do usuário.

As specs principais não mudam: esta é documentação do comportamento existente e correção de texto conforme a interface honesta já especificada. `skip_specs: true` é deliberado, sem novo requisito funcional. ADRs são referências, sem criação de decisão arquitetural nova.

### 6. Validação proporcional ao escopo

- Comparar cada nó/ramificação com os símbolos e ordem de chamadas efetivos, incluindo replay antes do conflito de revisão e commit antes do sucesso.
- Renderizar e inspecionar visualmente os dois Mermaid; verificar labels legíveis, setas, decisões, erros e retorno à tela. Artefatos de QA não serão versionados como entregáveis.
- Conferir links do documento, README e matriz; confirmar presença dos dois fluxogramas independentes e Repository em ambos, sem inventar CRUD em consultas.
- Verificar o aviso final por leitura/DOM e executar os testes existentes de desempenho/navegação: `npm run test:unit -- frontend/tests/desempenho.test.js frontend/tests/navigation.test.js`. Não criar testes que apenas repitam a string literal de um ajuste de texto.
- Conferir diff limitado aos seis arquivos do escopo: novo documento, README, matriz, duas operações e HTML do desempenho. Preservar todas as outras alterações locais anteriores; registrar comandos/resultados em `validacao.md` da change.

Não executar integrações MySQL, migrations ou suíte completa de cobertura como obrigação desta change sem lógica alterada. Se o apply descobrir necessidade de mudar comportamento, interromper e atualizar o planejamento, sem ampliar silenciosamente o escopo. Os fluxogramas não substituirão as evidências de execução já registradas nas changes anteriores.

## Risks / Trade-offs

- Desenho simplificado demais pode omitir Repository, retorno ou decisão → fluxos separados por caso, tabela de rastreabilidade e revisão contra código/specs.
- Representar toda a infraestrutura pode tornar o desenho ilegível → resumir autenticação/composição em blocos e manter detalhes em notas e links, sem mudar a ordem de negócio.
- Confundir Model com etapa obrigatória de CRUD na consulta → representar mapeamentos de origem e o Repository executor, sem gravar métricas fictícias.
- Correção do aviso pode sugerir agenda/IA disponíveis → mencionar apenas Plano básico e preservar os limites atuais nos documentos.
- Working tree contém mudanças legítimas anteriores → registrar preflight e conferir somente o delta desta change, sem reset/stash/commit.

## Migration Plan

1. Após autorização de apply, registrar o estado preexistente e criar os dois fluxogramas com suas fontes verificadas.
2. Corrigir aviso/referências operacionais e adicionar links de descoberta.
3. Renderizar, conferir caminhos/links e executar regressão DOM pertinente; registrar a verificação.
4. Registrar sync não aplicável e arquivar somente com tarefas concluídas e sem achados críticos.

Não há mudança de banco, API ou dependência de produção. Reversão consiste em remover apenas os acréscimos deste escopo e restaurar os trechos anteriores, preservando o trabalho já existente. Publicação e apresentação continuam fora desta etapa.
