# Fluxogramas dos casos de uso acadêmicos

Dois casos já implementados exemplificam **recuperação de dados** (diagnóstico)
e **entrada de dados** (finalização de Simulado). Os fluxogramas acompanham as
decisões e o retorno à interface pelas camadas reais. Não acrescentam funções
à [matriz das vinte funcionalidades](entrega-academica.md).

## Recuperação: consultar diagnóstico de desempenho

O diagnóstico continua acessível após recusa/revogação do plano. A extensão
acadêmica de privacidade usa este fluxo próprio, sem alterar os vinte casos:

```mermaid
flowchart TD
  A[Aluno lê os dois documentos] --> B{Escolha explícita}
  B -->|Aceitar uso| U[Gravar evidência de uso]
  B -->|Autorizar plano| C[Exigir aceite de uso vigente]
  B -->|Recusar ou revogar| D{Confirmar eliminação?}
  D -->|Cancelar| E[Não enviar POST]
  D -->|Confirmar| F[Controller chama Service da decisão]
  U --> G[Transação com lock do usuário]
  C --> G
  F --> G
  G --> H{Chave já processada?}
  H -->|Sim e idêntica| I[Registro original e estado atual sem novos efeitos]
  H -->|Não| J[Validar versão, revisão e transição]
  J --> K[Salvar decisão; negativa elimina planos próprios]
  K --> L{Persistência concluída?}
  L -->|Não| M[Rollback integral e erro]
  L -->|Sim| N[Único commit e estado atual]
  N --> O[Plano exige dois aceites vigentes antes de dados ou replay]
```

Revisão/chave conflitante retorna 409; campos inválidos, 400. O servidor aplica
sessão, perfil, Origin/CSRF e no-store. Guard do plano precede diagnóstico,
snapshot e item. Eliminação é irreversível na aplicação, restrita ao plano próprio
e confirmada com a negativa. Ver [operação](operacao-privacidade.md).

**Objetivo:** apresentar respostas concluídas do próprio Aluno, agregadas por
Matéria/Assunto, com período e base explícitos. Perfil: Aluno autenticado;
ausência de respostas é um resultado válido.

**Tela/ação:** [desempenho.html](../../frontend/aluno/desempenho.html),
ALU-DES-001, no carregamento ou envio de `dash-filtros`.
**Requisição:** `GET /api/aluno/desempenho`, opcionalmente com
`?inicio=2026-10-01&fim=2026-10-23`. Sem corpo, CSRF ou usuário alvo enviado
pelo cliente; identidade vem da sessão. Sem filtros, inclui hoje e os 29 dias
anteriores em UTC.

```mermaid
%%{init: {"theme":"neutral","themeVariables":{"fontFamily":"Arial","fontSize":"16px"},"flowchart":{"wrappingWidth":280,"rankSpacing":35}}}%%
flowchart TB
    D0([Início: consultar desempenho]) --> D1["Frontend: conferir identidade<br/>e limpar blocos para carregamento"]
    D1 --> D2["Route GET /api/aluno/desempenho<br/>Proteção HTTP: sessão e perfil"]
    D2 --> D3{Acesso autorizado?}
    D3 -- Não --> D4["HTTP 401 ou 403<br/>Interromper antes do Controller"]
    D4 --> DE["Interface: tratar erro de acesso<br/>ou consulta; permitir nova ação"]
    D3 -- Sim --> D5["DesempenhoController.diagnostico<br/>Usuário da sessão e filtros"]
    D5 --> D6["Service via composição<br/>EscoposLeitura: abrir contexto MySQL"]
    D6 --> D7{Período válido?}
    D7 -- Não --> D8["Liberar escopo próprio<br/>Controller: HTTP 400"]
    D8 --> DE
    D7 -- Sim --> D9["ConsultaMetricasMySQL<br/>DesempenhoRepository.agregar"]
    D9 --> D10["Projeções de Práticas, Simulados<br/>e classificação histórica de Questões"]
    D10 --> D11["Models: mapeamentos das fontes<br/>Sem CRUD de métricas"]
    D11 --> D12[("MySQL: contagens e grupos<br/>Snapshot consistente somente leitura")]
    D12 --> D13{Consulta concluída?}
    D13 -- Não --> D14["Liberar escopo próprio<br/>HTTP 500 sem diagnóstico parcial"]
    D6 -. Falha de abertura .-> D14
    D14 --> DE
    D13 -- Sim --> D15["Retorno pelo Repository/adaptador<br/>Normalizar contagens para o Service"]
    D15 --> D16{Há respostas?}
    D16 -- Não --> D17["sem_dados; percentual null<br/>Contagens zero; listas vazias"]
    D16 -- Sim --> D18["Service: percentuais e amostra<br/>Montar diagnóstico por grupo"]
    D17 --> D19["Liberar escopo próprio<br/>Controller: JSON HTTP 200"]
    D18 --> D19
    D19 --> D20["Frontend: reconferir identidade<br/>e geração; exibir blocos válidos"]
    D20 --> DF([Fim da consulta])
    DE --> DF
```

### Decisões e limites

- A proteção recusa sessão ausente/inválida com **401** e perfil inadequado com
  **403**. Falha interna ao verificar identidade produz **500**, também antes
  do Controller. O frontend usa as verificações de identidade existentes antes
  e depois da consulta; respostas de geração/conta antiga são descartadas.
- `ConsultarDesempenhoService` abre o escopo **antes** de validar filtros.
  `inicio` e `fim` devem vir juntos, sem campos extras/repetidos: datas
  `YYYY-MM-DD`, intervalo inclusivo de 1–366 dias, sem fim futuro UTC.
  Entradas inválidas geram **400** e liberam o contexto próprio, sem executar
  agregações acadêmicas. O intervalo de consulta é semiaberto em UTC.
- `EscoposLeitura` e `ConsultaMetricasDesempenho` são contratos; a composição
  fornece `EscoposLeituraMySQL` e `ConsultaMetricasMySQL`. Não são passos de
  gravação. `ContextoLeitura.usar` abre conexão dedicada em **REPEATABLE READ**,
  com snapshot consistente **READ ONLY** e um instante fixo. Na requisição
  mostrada, fechar o escopo libera a conexão em sucesso ou falha.
  Quando o diagnóstico é usado pelo Plano com contexto externo ativo, reutiliza
  snapshot/relógio e não fecha nem confirma/reverte a transação do consumidor.
- Práticas respondidas e respostas **não brancas** de Simulados finalizados
  compõem os fatos do usuário/período. `QuestaoVersao` fornece classificação
  histórica do Simulado; `PraticaTentativa` já guarda seu snapshot.
  Models são mapeamentos de origem: não existe Model/tabela de métrica gravada
  nem salvamento fictício no Repository. A proteção de autenticação pode
  renovar o registro de sessão, separadamente da leitura acadêmica.
- Sem respostas: **200**, `geral.estado_amostra="sem_dados"`,
  `percentual_acerto=null`, contagens zero e listas `materias`/`assuntos`
  vazias. Com 1–4: `amostra_pequena`; a partir de 5: `dados_disponiveis`.
  O limiar é operacional, sem garantia estatística ou domínio pedagógico.
  Percentual é `100 * acertos / total_respostas`, com duas casas.
- Falha de consulta/cálculo retorna **500**, libera o contexto próprio e não
  devolve blocos ou números parciais. A interface limpa dados anteriores e
  oferece tentar novamente; recuperar sessão não repete mutações.

### Rastreabilidade da recuperação

| Camada | Símbolos e fonte |
| --- | --- |
| Interface e HTTP cliente | `load`, `renderAluno`, `apiRequest`: [desempenho.js](../../frontend/js/desempenho.js), [api.js](../../frontend/js/api.js) e [auth-session.js](../../frontend/js/auth-session.js) |
| Route e acesso | Registro GET em [rotas de Desempenho](../../backend/app/modules/desempenho/routes.py), agregado por [routes.py](../../backend/app/routes.py); prefixo `/api` e hook em [factory](../../backend/app/__init__.py); `proteger_api` em [auth_http.py](../../backend/app/modules/contas/auth_http.py); `AutorizarService`/renovação em [autenticacao_service.py](../../backend/app/modules/contas/services/autenticacao_service.py) |
| Controller e resposta | `DesempenhoController.diagnostico`: [controller](../../backend/app/modules/desempenho/controllers/desempenho_controller.py); envelopes/erros em [http_response.py](../../backend/app/http_response.py) |
| Composição e contratos | `servicos().desempenho`: [http_composition.py](../../backend/app/http_composition.py), `compor`: [composition.py](../../backend/app/composition.py); `EscoposLeitura`, `ConsultaMetricasDesempenho`: [contratos](../../backend/app/contracts/desempenho.py) |
| Regras | `ConsultarDesempenhoService.executar`, `metrica`: [service](../../backend/app/modules/desempenho/services/consultar_desempenho_service.py); `periodo`: [validação](../../backend/app/modules/desempenho/services/desempenho_validacao.py) |
| Adaptadores e agregação | `EscoposLeituraMySQL`, `ConsultaMetricasMySQL.agregar`: [adaptadores](../../backend/app/modules/desempenho/repositories/consultas_desempenho.py); `DesempenhoRepository.agregar` executa `CALL sp_desempenho_resumo`: [repository](../../backend/app/modules/desempenho/repositories/desempenho_repository.py) |
| Interfaces SQL históricas | Produção agrega `vw_praticas_fatos_desempenho` e `vw_simulados_fatos_desempenho`, com classificação por `vw_conteudo_classificacao_historica`: [views públicas de origem](consultas-academicas-mysql.md#views-públicas-de-origem). As projeções ORM `projecao_desempenho` de [Práticas](../../backend/app/modules/praticas/repositories/pratica_repository.py) e [Simulados](../../backend/app/modules/simulados/repositories/simulado_repository.py), e `projecao_classificacao_historica` de [Conteúdo](../../backend/app/modules/conteudo/repositories/questao_repository.py), permanecem somente para regressão de equivalência. |
| Models de origem | `PraticaTentativa`: [model](../../backend/app/modules/praticas/models/pratica_tentativa.py); `SimuladoTentativa`, `SimuladoResposta`, `SimuladoVersaoItem`: [mesmo arquivo de Models de Simulado](../../backend/app/modules/simulados/models/simulado.py); `QuestaoVersao`: [model](../../backend/app/modules/conteudo/models/questao_versao.py). São mapeamentos das tabelas de origem; a consulta de produção retorna registros SQL, sem hidratar essas Models. |
| Infraestrutura / MySQL | `ContextoLeitura.usar/executar_resultados`: [contexto_leitura.py](../../backend/app/contexto_leitura.py); conexão SQLAlchemy em [extensions.py](../../backend/app/extensions.py) |

Contrato completo: [operação de desempenho](operacao-desempenho.md).

## Entrada: finalizar tentativa de Simulado

**Objetivo:** tornar definitivas as respostas já salvas e persistir correções e
resultado da tentativa própria. Perfil: Aluno autenticado, com tentativa em
andamento; replay de uma finalização concluída devolve o resultado persistido.

**Tela/ação:** [simulado.html](../../frontend/aluno/simulado.html), em
`/aluno/simulado.html?tentativa_id=<id>`, botão `sim-finalizar` e diálogo de
confirmação. A interface informa quantos itens estão em branco; cancelar
retorna à tentativa sem enviar requisição.
**Requisição:** `POST /api/aluno/tentativas-simulado/<id>/finalizar`, corpo
`{"revisao":3,"confirmar":true}` (revisão corrente), cookie de sessão e
`X-CSRF-Token`. O usuário vem da sessão, sem campo de identidade no corpo.

```mermaid
%%{init: {"theme":"neutral","themeVariables":{"fontFamily":"Arial","fontSize":"16px"},"flowchart":{"wrappingWidth":280,"rankSpacing":35}}}%%
flowchart TB
    S0([Início: clicar Finalizar]) --> S1{Alternativa local salva?}
    S1 -- Não --> S2(["Pedir salvamento; sem POST<br/>Fim: manter tentativa"])
    S1 -- Sim --> S3["Interface: informar brancos<br/>e abrir confirmação"]
    S3 --> S4{Confirmar?}
    S4 -- Não --> S5(["Cancelar; fechar e devolver foco<br/>Fim: sem POST"])
    S4 -- Sim --> S6["apiRequest: POST finalizar<br/>Revisão, confirmação e CSRF"]
    S6 --> S7["Route e proteção HTTP<br/>Sessão, perfil, origem e CSRF"]
    S7 --> S8{Acesso autorizado?}
    S8 -- Não --> S9(["HTTP 401/403: erro na interface<br/>Fim: sem iniciar caso de uso"])
    S8 -- Sim --> S10["SimuladoController.finalizar<br/>Interpretar JSON e chamar Service"]
    S10 --> S11{Entrada válida?}
    S11 -- Não --> S12(["HTTP 400: erro na interface<br/>Fim: sem transação acadêmica"])
    S11 -- Sim --> S13["FinalizarSimuladoService<br/>TransactionManager: iniciar operação"]
    S13 --> S14["SimuladoRepository.propria<br/>MySQL: filtrar usuário e obter lock"]
    S14 --> S15{Tentativa própria existe?}
    S15 -- Não: 404 --> SR["TransactionManager: rollback<br/>Controller: erro, sem resultado parcial"]
    S15 -- Sim --> S16{Já finalizada?}
    S16 -- Sim: replay --> S17["Obter resultado persistido<br/>Sem recalcular ou salvar"]
    S16 -- Não --> S18{Revisão confere?}
    S18 -- Não: 409 --> SR
    S18 -- Sim --> S19["SimuladoRepository.respostas<br/>MySQL: respostas e itens com locks"]
    S19 --> S20{Há próximo item?}
    S20 -- Sim --> S21{Alternativa em branco?}
    S21 -- Sim --> S22["Service: contar branco<br/>Sem corrigir ou salvar resposta"]
    S22 --> S20
    S21 -- Não --> S23["ConsultarVersaoHistoricaService<br/>QuestaoVersao: ler gabarito no MySQL"]
    S23 --> S24["Service: comparar alternativa<br/>e contar acerto ou erro"]
    S24 --> S25["Model SimuladoResposta.salvar<br/>confirmar=False; flush no MySQL"]
    S25 --> S20
    S20 -- Não --> S26["Service: totais e percentual<br/>Estado, data e nova revisão"]
    S26 --> S27["Model SimuladoTentativa.salvar<br/>confirmar=False; flush no MySQL"]
    S27 --> S28[("MySQL: commit único<br/>TransactionManager")]
    S17 --> S28
    S28 --> S29{Commit concluído?}
    S29 -- Não: 500 --> SR
    S13 -. Exceção na operação .-> SR
    S29 -- Sim --> S30["Controller: JSON HTTP 200<br/>Resultado persistido; locks liberados"]
    S30 --> S31["Frontend: reconferir identidade<br/>Exibir resultado e mover foco"]
    SR --> SE["Interface: mostrar erro e preservar<br/>contexto da conta; nova ação explícita"]
    SE --> SEF([Fim: aguardar nova ação])
    S31 --> SF([Fim: resultado exibido])
```

### Decisões e atomicidade

- `confirmFinish` bloqueia alternativa local não salva; cancelar não envia
  POST. `finish` verifica identidade e envia revisão corrente/`confirmar:true`.
  `apiRequest` inclui credenciais e CSRF; o servidor exige sessão/perfil Aluno
  (**401/403**), origem permitida e CSRF (**403**). Falha interna nessa proteção
  produz **500**. Finalizar não exige reautenticação recente nem motivo.
- O Controller passa JSON ao `FinalizarSimuladoService`. Estrutura estrita,
  revisão inteira positiva e confirmação exatamente `true` são validadas
  **antes** da transação acadêmica; falha é **400**. O POST usa respostas já
  persistidas: não envia alternativas ou gabaritos no corpo da finalização.
- `TransactionManager.executar` inicia/participa da transação e só devolve o
  resultado após commit. `propria` consulta pelo par usuário/tentativa com
  `FOR UPDATE`; tentativa inexistente ou de outro usuário gera o mesmo **404**
  e rollback. Consultas/locks ficam no `SimuladoRepository`, sem CRUD duplicado.
- **Replay vem antes da comparação de revisão.** Com corpo válido e tentativa
  já finalizada, `t.resultado()` retorna os totais salvos sem recalcular,
  gravar correções ou incrementar revisão; commit encerra a transação/libera
  locks antes do **200**, mesmo com revisão recebida antiga. Em andamento,
  revisão divergente gera **409**, com rollback e necessidade de recarregar.
- `respostas(..., bloquear=True)` consulta pares `SimuladoResposta` e
  `SimuladoVersaoItem` ordenados, com locks. Para alternativa não branca,
  `ConsultarVersaoHistoricaService` lê `QuestaoVersao.buscar_por_id` e seu
  gabarito histórico; não usa o rascunho atual nem recalcula histórico antigo.
  Versão publicada ausente produz **404** e rollback pelo mesmo tratamento
  transacional. Arquivamento da Questão lógica não troca a versão utilizada.
- Branco incrementa `em_branco`, sem leitura de gabarito ou salvamento daquela
  resposta. Respondida calcula `correta` e chama
  `SimuladoResposta.salvar(confirmar=False)`. Ao concluir o laço, o Service
  atribui totais, percentual, `finalizada_em`, estado e revisão incrementada;
  `SimuladoTentativa.salvar(confirmar=False)` faz o flush final.
  O resultado é montado dentro da operação e só sai após o commit.
- **Denominador: todas as Questões.** Um acerto, um erro e um branco dão total
  3, respondidas 2 e 33,33%. Já o diagnóstico acima usa somente as duas
  respostas efetivas, portanto 50%. `TransactionManager` confirma uma única
  vez; exceção na operação ou no commit reverte o caso inteiro. Erros de
  domínio mantêm **404/409**; falha interna é **500**, sem resultado parcial.
- Não há evento de finalização gravado em `SimuladoEvento`. As gravações
  acadêmicas deste caso pertencem às Models de resposta/tentativa; o Service
  não executa SQL. Composição/Protocol do diagnóstico não foram estendidos
  artificialmente às escritas de Simulado, preservadas após a refatoração.
- Sucesso reconfere identidade/geração, atualiza estado/resultado na tela e
  move foco para o título. Erro de rede/sessão mantém contexto para a mesma
  conta e exige nova ação explícita; não há replay automático de escrita.
  Troca de conta limpa dados privados e descarta respostas atrasadas.

### Rastreabilidade da entrada

| Camada | Símbolos e fonte |
| --- | --- |
| Interface | `confirmFinish`, `finish`, `render`: [aluno-simulados.js](../../frontend/js/aluno-simulados.js); confirmação/resultado em [simulado.html](../../frontend/aluno/simulado.html) |
| Cliente e proteção HTTP | `apiRequest`: [api.js](../../frontend/js/api.js); identidade em [auth-session.js](../../frontend/js/auth-session.js); `proteger_api`: [auth_http.py](../../backend/app/modules/contas/auth_http.py); autorização/CSRF em [autenticacao_service.py](../../backend/app/modules/contas/services/autenticacao_service.py) |
| Route / Controller | POST em [rotas de Simulados](../../backend/app/modules/simulados/routes.py), agregadas por [routes.py](../../backend/app/routes.py); `SimuladoController.finalizar`: [controller](../../backend/app/modules/simulados/controllers/simulado_controller.py); envelopes em [http_response.py](../../backend/app/http_response.py) |
| Regras e validação | `FinalizarSimuladoService.executar`: [service](../../backend/app/modules/simulados/services/finalizar_simulado_service.py); `corpo`: [validação compartilhada](../../backend/app/core/validacao.py); `revisao`, `conferir_revisao`: [simulado_validacao.py](../../backend/app/modules/simulados/services/simulado_validacao.py) |
| Propriedade e locks | `propria`: [consultar_simulado_service.py](../../backend/app/modules/simulados/services/consultar_simulado_service.py); `SimuladoRepository.propria/respostas`: [repository](../../backend/app/modules/simulados/repositories/simulado_repository.py) |
| Versão histórica | `ConsultarVersaoHistoricaService`: [gestao_questao_service.py](../../backend/app/modules/conteudo/services/gestao_questao_service.py); `QuestaoVersao`: [model](../../backend/app/modules/conteudo/models/questao_versao.py) |
| Persistência Active Record | `SimuladoResposta`, `SimuladoTentativa`, `SimuladoVersaoItem` e `SimuladoTentativa.resultado`: [mesmo simulado.py](../../backend/app/modules/simulados/models/simulado.py); `salvar(confirmar=False)` herdado de `ModeloBase`: [implementação canônica](../../backend/app/core/persistencia.py); [crud_mixin.py](../../backend/app/models/crud_mixin.py) apenas reexporta as bases. |
| Transação / MySQL | `TransactionManager.executar`: [transaction_manager.py](../../backend/app/transaction_manager.py); sessão SQLAlchemy em [extensions.py](../../backend/app/extensions.py) |

Contrato completo: [operação de Simulados](operacao-simulados.md).
Decisões comuns: [arquitetura mestre](architecture-master-v1.md),
[sessões](adr/ADR-002-estrategia-de-autenticacao.md),
[versões](adr/ADR-005-versionamento-editorial.md),
[transações](adr/ADR-006-fronteira-de-transacoes.md) e
[contratos/capacidades](adr/ADR-008-contratos-e-capacidades-de-persistencia.md).
