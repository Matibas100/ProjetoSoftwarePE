# Design — Desempenho real

## Context

Ver [proposal.md](proposal.md). Após itens 3/4, existem fatos persistidos de prática e simulado. Arquitetura Mestre exige período/base explícitos e que ausência de dados não seja tratada como zero. OD-17 permanece aberta para o produto definitivo; cinco respostas é uma decisão proposta apenas para este MVP.

## Goals / Non-Goals

**Goals:** leitura verificável de origem, sem alterar resultados; mesmo diagnóstico para tela e plano.

**Non-Goals:** criar tabelas de métricas, filas, cache persistente, migração de framework ou acesso administrativo ao histórico individual.

## Decisions

### 1. Fonte e contrato entre módulos

Os Services de origem dos itens 3/4 continuam oferecendo seus contratos de fatos concluídos. Para agregação no MySQL, os mesmos módulos oferecem projeções de leitura especializadas por seus Repositories, com semântica equivalente: prática respondida e item respondido de simulado finalizado, com ID de origem, usuário, instante, correção e IDs/rótulos de classificação histórica. `DesempenhoRepository` compõe essas projeções, sem acessar tabelas internas por fora desse contrato nem carregar todos os fatos no Service. Esta change acrescenta o contrato de projeção, sem substituir os contratos dos Services predecessores; a tarefa 1.1 verifica equivalência com suas versões finais antes do apply.

Cada projeção fornece `{tipo, id, atividade_id, usuario_id, ocorrido_em, correta, materia_id, materia_nome, assunto_id, assunto_nome}`. `tipo` é `pratica` ou `simulado`; `id` identifica a tentativa de prática ou o registro de resposta do simulado, respectivamente; `atividade_id` identifica a tentativa que será aberta. `ocorrido_em` é resposta/finalização em UTC, `correta` é booleano não nulo e classificação vem do snapshot histórico. Usuário e intervalo são obrigatórios nas consultas; nenhuma projeção autoriza escrita. Os Services e projeções devem concordar sobre inclusão, correção e classificação dos mesmos fatos.

Usar `UNION ALL` entre tipos de origem com chave `(tipo, id)`; uma resposta de simulado não gera prática. Repetições reais de Questão e novas tentativas contam novamente; replay de requisição não conta novamente. Branco não integra desempenho por Matéria/Assunto porque não houve resposta, mas permanece no resultado do simulado com seu denominador próprio. Correção de simulado usa finalização como instante; prática usa instante da resposta.

Classificação e nomes vêm do snapshot usado na tentativa, não de JOIN que reatribui histórico após transferir/renomear Assunto. Agrupar por `(materia_id, assunto_id)` e, para Matéria, por `materia_id`; rótulo de grupo = do fato mais recente no período, desempate por tipo/ID. Preservar agrupamento de conteúdo arquivado no histórico; elegibilidade atual é outro contrato.

### 2. Fórmulas, períodos e amostra

`total_respostas = acertos + erros`; `percentual_acerto = round(100 * acertos / total_respostas, 2)`. Calcular agregados pelos totais, nunca pela média de percentuais. Zero respostas -> percentual null, estado `sem_dados`; 1–4 -> `amostra_pequena` com contagens/percentual; >=5 -> `dados_disponiveis`. Não chamar esse limiar de significância estatística. Linhas de assuntos/matérias sem resposta não aparecem como 0%; a UI explica ausência.

Parâmetros opcionais `inicio`/`fim` em `YYYY-MM-DD`, fornecidos juntos, datas inclusivas, `inicio <= fim`, máximo 366 dias e fim não posterior ao dia UTC atual. Converter a `[00:00 inicio, 00:00 do dia após fim)` UTC. Padrão últimos 30 dias incluindo o dia UTC atual. Retornar início/fim/UTC e instante de cálculo; essa base também é usada no plano. Strings/datas/filtros extras inválidos -> 400. Datas para leitura no frontend podem ser localizadas, mantendo legenda do período UTC.

### 3. Contratos HTTP e interno

`GET /api/aluno/desempenho?inicio=...&fim=...` retorna `{periodo: {inicio, fim, timezone}, calculado_em, limiar_amostra:5, base:{pratica, simulado}, geral, materias:[...], assuntos:[...]}`. `base` contém quantidades de respostas por origem, inclusive zero, cuja soma é `geral.total_respostas`. Cada métrica tem IDs/rótulos aplicáveis, `total_respostas`, `acertos`, `erros`, `percentual_acerto`, `estado_amostra` e `base` com as mesmas contagens por origem. Linhas de Matéria acrescentam `materia_id`/`materia_nome`; linhas de Assunto acrescentam também `assunto_id`/`assunto_nome`. Ordenar Matérias por ID e Assuntos por Matéria/Assunto para resposta determinística.

`GET /api/aluno/dashboard` usa os mesmos parâmetros e retorna `{desempenho: <mesmo diagnóstico>, ultimas_atividades:[até 5 resumos próprios]}`. Cada resumo contém `{tipo, id, ocorrido_em, titulo, url}`: `id` é a tentativa de prática ou simulado; instante e filtro seguem o mesmo período UTC do diagnóstico. Ordenar por instante decrescente, tipo decrescente (`simulado` antes de `pratica`) e ID decrescente. Prática aparece uma vez por tentativa respondida, com título derivado dos nomes históricos de Matéria/Assunto e URL `/aluno/questao.html?tentativa_id=<id>`; simulado aparece uma vez por tentativa finalizada, inclusive quando todas as questões estão em branco, com título da versão e URL `/aluno/simulado.html?tentativa_id=<id>`. O simulado não é desdobrado em atividades por resposta. Ausência de atividades retorna `[]`; quantidade de atividades não é quantidade de respostas. Os detalhes de destino continuam sujeitos à autorização por proprietário.

Service de diagnóstico recebe `usuario_id` da sessão HTTP ou de outro Service autorizado, período e retorna esse mesmo DTO. Item 6 chama esse Service, sem copiar fórmulas nem fazer HTTP interno. O consumidor interno pode fornecer um contexto opaco de leitura e um instante UTC fixado pelo caso de uso; Service não manipula conexão ou sessão e não encerra a transação recebida.

`GET /api/admin/dashboard` retorna `{calculado_em, catalogo:{materias_ativas, assuntos_ativos}, questoes:{rascunhos, publicadas, arquivadas}, simulados:{rascunhos, publicados, arquivados}, tentativas_simulado_finalizadas}` com contagens globais atuais; apenas Administrador. Não recebe usuário alvo/período e não expõe respostas, e-mail ou comparação individual. Estado publicado do cadastro não promete elegibilidade de todo conteúdo.

### 4. Camadas, consistência e interface

Controllers interpretam filtros, Services validam/compõem e Repositories executam agregações MySQL; nenhuma escrita, SQL ou `db.session` em Service/Controller. A infraestrutura fornece `ContextoLeitura`: em GET, após autorização, abre conexão dedicada com transação InnoDB somente leitura em `REPEATABLE READ` e snapshot consistente, usada por todas as projeções, agregados e atividades/contagens daquela resposta. Fixa o relógio uma vez para período padrão, validação de futuro e `calculado_em`; encerra apenas o contexto próprio ao terminar, inclusive em falha, sem confirmar a sessão usada pela autenticação. Não usar `TransactionManager` de escrita para calcular o dashboard.

Quando o item 6 fornecer contexto da transação de geração, o diagnóstico participa da conexão/snapshot existente em `REPEATABLE READ`, sem abrir outra conexão/transação ou executar commit/rollback. A infraestrutura do caso de uso externo possui a transação, fixa o relógio e verifica o isolamento antes das leituras; inconsistência de contexto produz erro, nunca fallback para leitura independente. Falha de diagnóstico propaga ao consumidor, que decide o rollback de sua operação. Diferentes requests têm `calculado_em` próprios. Sem procedure nova; preservar CALL existente no Repository.

Os endpoints entregam respostas completas: falha em qualquer consulta necessária retorna erro HTTP 500 no formato de erro existente, sem payload parcial de sucesso nem números substitutos. Na UI, cada bloco visual distingue loading, vazio, amostra pequena e erro, mas os blocos alimentados pelo mesmo endpoint mudam juntos; recarregar repete a requisição inteira. Navegação e recursos independentes continuam acessíveis. Em recarga ou troca de período, retirar os dados anteriores dos blocos antes da consulta; respostas atrasadas de período/identidade anteriores não podem preencher a tela. Não há endpoints extras por bloco neste recorte.

Rotas de Aluno seguem perfil/propriedade do item 3; Admin separado, CSRF não exigido em GET mas sessão/no-store sempre. Nenhuma consulta aceita `usuario_id` fornecido pelo cliente. Preservar destinos de login: `/aluno/inicio.html` passa a renderizar ALU-DASH-001 e `/aluno/desempenho.html` usa ALU-DES-001. Criar `/admin/dashboard.html` com link na moldura, sem alterar destino administrativo de login. Blocos futuros de plano/redação/tutor indisponíveis, não preenchidos com mocks. Loading/erro por bloco, tentativa de recarga, teclado e legibilidade conforme Desktop V1.

## Risks / Trade-offs

- Repetição melhora acerto sem medir domínio amplo -> mostrar número de respostas e base; sem alegações estatísticas.
- Simulado exibe percentual diferente do agregado quando há brancos -> legendas explícitas: resultado divide por todas as Questões, desempenho divide por respondidas.
- Consulta pode crescer -> período limitado, índices existentes e agregação no MySQL; materialização requer change futura.

## Migration Plan

Sem migration: usar schema final dos itens 3/4, validar contratos de origem no preflight e não acrescentar índice/tabela silenciosamente. Disponibilizar API/telas após ambos encerrados. Reversão remove consumidores novos sem tocar fatos; preservar `/aluno/inicio.html` e sessão. Testar métricas com dados temporários no MySQL real, ausência de dados, limites de datas/amostra, isolamento e transferências de catálogo. Não executar suítes da aplicação durante esta fase documental.
