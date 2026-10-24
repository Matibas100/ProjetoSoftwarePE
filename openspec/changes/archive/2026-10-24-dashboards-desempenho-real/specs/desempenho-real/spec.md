# Delta — Desempenho real

## Purpose

Apresentar desempenho e dashboards derivados de respostas reais, com origem, período e amostra explícitos, preservando privacidade e dados históricos.

## ADDED Requirements

### Requirement: Métricas derivadas de fatos concluídos
O diagnóstico SHALL considerar respostas de práticas corrigidas e itens respondidos de simulados finalizados uma vez por origem/registro. Tentativas em andamento e itens em branco SHALL NOT integrar o denominador de desempenho; repetições reais SHALL contar como respostas distintas. Total SHALL igualar acertos + erros; percentual SHALL ser `100 * acertos / total`, arredondado a duas casas; agregado SHALL usar totais, não média de percentuais. Resultado do simulado SHALL continuar usando todas as Questões em seu próprio denominador.

#### Scenario: Combinar origens sem dupla contagem
- **GIVEN** duas práticas respondidas e simulado finalizado com duas respostas e um branco
- **WHEN** consulta diagnóstico do período
- **THEN** desempenho contabiliza quatro respostas, separa contagens de origem e não duplica o simulado como prática

#### Scenario: Reenvio e repetição real
- **GIVEN** replay de uma resposta e nova tentativa real da mesma Questão
- **WHEN** consulta métricas
- **THEN** replay não acrescenta fato e a nova tentativa concluída acrescenta um fato

### Requirement: Período e classificação históricos explícitos
`GET /api/aluno/desempenho` e `/api/aluno/dashboard` SHALL aceitar `inicio`/`fim` juntos em datas ISO inclusivas, máximo 366 dias, início não posterior ao fim e fim não futuro em UTC. Padrão SHALL ser últimos 30 dias incluindo dia UTC atual. SHALL retornar período, timezone UTC, instante de cálculo, base e contagens por origem. Prática SHALL usar instante de resposta e simulado o de finalização. Matérias/Assuntos SHALL agrupar por IDs/classificação capturados na versão histórica, preservando referências após transferência/renomeação; rótulo de grupo SHALL vir do fato mais recente com desempate estável por origem/ID. Parâmetros extras ou inválidos SHALL retornar 400.

#### Scenario: Limites do período
- **GIVEN** fatos antes, dentro e depois das datas solicitadas
- **WHEN** consulta período válido
- **THEN** inclui somente fatos entre 00:00 UTC do início e 00:00 UTC do dia após o fim, informando a base temporal

#### Scenario: Taxonomia muda
- **GIVEN** respostas anteriores a transferência de Assunto ou renomeação de Matéria
- **WHEN** consulta desempenho histórico
- **THEN** contagens mantêm os grupos da classificação capturada, sem atribuição retroativa à nova Matéria

#### Scenario: Datas inválidas
- **GIVEN** cliente autenticado
- **WHEN** envia só uma data, fim futuro, intervalo invertido ou maior que 366 dias
- **THEN** recebe 400 sem consulta não limitada ou erro interno

### Requirement: Ausência de dados e amostra pequena
Cada métrica SHALL expor total, acertos, erros, percentual e estado da amostra. Zero respostas SHALL produzir percentual null e `sem_dados`; 1–4 SHALL produzir percentual e `amostra_pequena`; >=5 SHALL produzir `dados_disponiveis`. SHALL retornar limiar 5 e não apresentar significância estatística, tendência ou nota prevista. Assuntos sem resposta SHALL NOT aparecer como desempenho zero.

#### Scenario: Conta sem histórico
- **GIVEN** Aluno sem fatos no período
- **WHEN** abre diagnóstico/dashboard
- **THEN** vê contagens zero, percentual indisponível, estado sem dados e orientação para prática real

#### Scenario: Limite de amostra
- **GIVEN** grupos com quatro e cinco respostas
- **WHEN** consulta diagnóstico
- **THEN** primeiro é amostra pequena e segundo dados disponíveis, ambos com contagens reais

### Requirement: Dashboards privados e operacionais
Dashboard do Aluno SHALL mostrar diagnóstico próprio, até cinco últimas atividades próprias e links para fluxos existentes, usando ALU-DASH-001 e ALU-DES-001. Dashboard administrativo SHALL mostrar somente contagens reais globais de catálogo ativo, Questões/simulados por estado e tentativas finalizadas, usando ADM-DASH-001 e exigindo Administrador. APIs SHALL NOT aceitar usuário alvo do cliente nem expor histórico individual a Administrador. Sessão/perfil SHALL ser verificados no servidor, mantendo 401/403 e no-store.

Atividades SHALL usar o mesmo período UTC do diagnóstico e expor `{tipo, id, ocorrido_em, titulo, url}`, com uma linha por tentativa de prática respondida ou simulado finalizado, inclusive simulado totalmente em branco. SHALL ordenar por instante, tipo (`simulado` antes de `pratica`) e ID decrescentes e limitar o resultado a cinco linhas. Lista vazia SHALL ser `[]`. URLs SHALL apontar para `/aluno/questao.html?tentativa_id=<id>` ou `/aluno/simulado.html?tentativa_id=<id>` conforme a origem, mantendo autorização no destino. Quantidade de atividades SHALL NOT ser apresentada como quantidade de respostas.

#### Scenario: Dashboard do Aluno
- **GIVEN** Alunos A e B com históricos distintos
- **WHEN** A abre `/api/aluno/dashboard`
- **THEN** recebe somente diagnóstico/atividades de A sem dados de B

#### Scenario: Atividades no período com desempate
- **GIVEN** práticas e simulados próprios dentro e fora do período, com mais de cinco atividades e instantes empatados
- **WHEN** consulta dashboard com período explícito
- **THEN** recebe só as cinco primeiras atividades do período pela ordem de instante, tipo e ID decrescentes, com os campos e destinos definidos

#### Scenario: Simulado sem respostas
- **GIVEN** simulado próprio finalizado no período com todos os itens em branco
- **WHEN** consulta dashboard
- **THEN** simulado pode aparecer uma vez nas últimas atividades, mas não acrescenta resposta ao diagnóstico

#### Scenario: Contagens administrativas
- **GIVEN** Administrador e dados reais cadastrados
- **WHEN** consulta `/api/admin/dashboard`
- **THEN** recebe contagens coerentes sem nomes, e-mails, alternativas ou histórico individual dos estudantes

### Requirement: Contrato reutilizável e interface honesta
O diagnóstico SHALL disponibilizar ao plano a mesma base, período, limiar e fórmula da tela, sem fórmula paralela. As telas SHALL preservar destinos de login existentes, diferenciar vazio/amostra pequena/loading/erro por bloco e permitir nova tentativa de consulta. Recursos não implementados SHALL permanecer indisponíveis sem números fictícios. Métricas de uma resposta SHALL ser calculadas sobre visão consistente da mesma base de origem.

Projeções dos Repositories de origem SHALL preservar a semântica dos fatos oferecidos pelos Services de práticas/simulados, sem acesso externo de escrita. Diagnóstico e cada linha de métrica SHALL expor `base:{pratica, simulado}` como quantidades de respostas cuja soma iguala o total respectivo. Consultas de um endpoint SHALL compartilhar snapshot consistente; consumidor interno autorizado SHALL poder fornecer o contexto e relógio da transação externa, sem que o diagnóstico os substitua ou encerre.

Endpoints SHALL retornar payload completo ou erro, sem sucesso parcial. Falha de consulta interna SHALL retornar HTTP 500 no formato de erro existente; blocos da mesma requisição SHALL mostrar erro juntos e permitir recarga da requisição inteira. Navegação SHALL continuar disponível. Recarga/troca de período SHALL retirar dados anteriores dos blocos; resposta atrasada de período ou identidade anterior SHALL NOT preencher a tela.

#### Scenario: Plano consulta diagnóstico
- **GIVEN** mesmo usuário, período e fatos de origem
- **WHEN** tela e consumidor interno autorizado consultam diagnóstico
- **THEN** recebem as mesmas contagens, classificações e estados de amostra

#### Scenario: Diagnóstico participa da geração de plano
- **GIVEN** consumidor interno autorizado com contexto transacional e instante UTC fixados
- **WHEN** consulta diagnóstico e depois sua operação externa falha
- **THEN** diagnóstico usa a mesma visão e relógio sem confirmar ou reverter a transação externa, cuja decisão de rollback continua no consumidor

#### Scenario: Nova resposta durante a consulta
- **GIVEN** consulta de dashboard em andamento e uma nova resposta confirmada depois da abertura de seu snapshot
- **WHEN** compõe diagnóstico e atividades
- **THEN** nenhum bloco inclui a nova resposta naquela requisição, mantendo contagens e atividades coerentes com o snapshot

#### Scenario: Consulta de bloco falha
- **GIVEN** dashboard consultando diagnóstico e atividades
- **WHEN** qualquer consulta necessária falha
- **THEN** endpoint retorna 500 sem payload parcial, blocos da requisição mostram erro e permitem recarga conjunta, mantendo navegação disponível e sem valores artificiais

#### Scenario: Resposta atrasada após mudança de contexto
- **GIVEN** consulta pendente e mudança de período ou identidade antes da resposta
- **WHEN** a resposta anterior chega
- **THEN** não preenche os blocos do novo contexto nem restaura dados da identidade anterior
