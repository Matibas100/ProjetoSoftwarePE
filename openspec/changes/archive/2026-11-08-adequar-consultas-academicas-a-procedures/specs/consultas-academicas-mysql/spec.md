# Consultas acadêmicas MySQL

## Purpose

Definir interfaces SQL de leitura para listagens administrativas, diagnóstico e dashboards da Plataforma ENEM, com procedures especializadas, compatibilidade HTTP e participação transacional segura.

## ADDED Requirements

### Requirement: Leitura especializada pelas interfaces SQL oficiais
As seis consultas HTTP delimitadas nesta etapa SHALL executar sua seleção, filtros, ordenação e agregação por procedures oficiais chamadas exclusivamente na camada Repository. CRUD básico SHALL permanecer nas Models. Falha de procedure MUST NOT acionar consulta ORM substituta ou produzir sucesso parcial.

#### Scenario: Listagens administrativas e diagnóstico
- **GIVEN** banco atualizado e cliente autorizado
- **WHEN** consulta `/api/admin/materias`, `/api/admin/assuntos`, `/api/admin/questoes` ou `/api/aluno/desempenho`
- **THEN** a seleção especializada é executada pela procedure oficial correspondente, com os mesmos status e formatos HTTP existentes

#### Scenario: Dashboards por composição de consultas
- **GIVEN** cliente autorizado consultando o dashboard de seu perfil
- **WHEN** solicita `/api/aluno/dashboard` ou `/api/admin/dashboard`
- **THEN** todas as métricas, atividades ou contagens necessárias provêm das procedures oficiais, mantendo os contratos existentes

#### Scenario: Procedure indisponível
- **GIVEN** uma procedure obrigatória ausente ou com resultado incompatível
- **WHEN** uma consulta que depende dela é solicitada
- **THEN** a API retorna erro interno no formato existente, sem fallback, dados artificiais ou blocos parciais e sem expor SQL ou credenciais

### Requirement: Compatibilidade das listagens administrativas
Listagens administrativas SHALL preservar filtros, semântica de busca, ordenação estável, campos serializados, valores nulos, contagens e paginação atuais. O total SHALL ser independente da existência de linhas na página solicitada. Validação e envelope HTTP SHALL continuar na aplicação.

#### Scenario: Matérias e Assuntos filtrados
- **GIVEN** catálogo com múltiplas Áreas, estados e vínculos de Questões
- **WHEN** Administrador combina busca e filtros das listagens
- **THEN** recebe as mesmas linhas, objetos relacionados e contagens atuais, sem multiplicação indevida por JOIN, ordenadas por nome/ID para Matérias e nome normalizado/ID para Assuntos
- **AND** a semântica LIKE atual dessas duas buscas é preservada

#### Scenario: Busca literal de Questões
- **GIVEN** enunciados com porcentagem, sublinhado, aspas e caracteres acentuados
- **WHEN** Administrador usa esses caracteres na busca de Questões, combinada com filtros válidos
- **THEN** porcentagem e sublinhado são tratados como conteúdo literal, sem virarem curingas ou SQL executável, e a ordenação continua por ID decrescente

#### Scenario: Página sem linhas e dados anuláveis
- **GIVEN** registros compatíveis com filtros, descrições opcionais nulas e paginação além da última página
- **WHEN** a listagem é solicitada
- **THEN** retorna itens vazios com o total real, sem linha fictícia para transportar o total
- **AND** páginas existentes preservam os nulos e as datas serializadas como no contrato anterior

#### Scenario: Parâmetros HTTP inválidos
- **GIVEN** cliente autorizado
- **WHEN** envia paginação, status, IDs ou filtros temporais inválidos conforme a validação atual de cada endpoint
- **THEN** recebe o erro de validação existente, sem ampliar filtros aceitos ou expor detalhes SQL

### Requirement: Equivalência histórica das métricas e atividades
Diagnóstico e dashboards SHALL preservar as regras de `desempenho-real`: fatos concluídos, denominadores, grupos históricos, intervalo UTC e desempates estáveis. Mudança do mecanismo SQL SHALL NOT alterar percentuais, amostras, limites, destinos ou classificação das atividades.

#### Scenario: Mistura de origens e classificações históricas
- **GIVEN** práticas respondidas, repetição real, replay, Simulados abertos/finalizados e itens em branco, antes e depois de transferência de Assunto
- **WHEN** o usuário consulta o mesmo período e fatos anteriores à conversão
- **THEN** recebe os mesmos totais e bases por origem, sem contar replays, brancos ou tentativas abertas, preservando IDs históricos e o rótulo do fato mais recente com os mesmos desempates

#### Scenario: Amostra vazia e limites temporais
- **GIVEN** intervalo UTC sem fatos e registros exatamente nos limites inicial e final
- **WHEN** o diagnóstico é consultado
- **THEN** o limite inicial é inclusivo e o final exclusivo; ausência de fatos produz contagens zero, percentual nulo e estado sem dados, mantendo os estados atuais para amostras de quatro e cinco respostas

#### Scenario: Atividades distintas de respostas
- **GIVEN** mais de cinco atividades próprias, empates de instante e um Simulado finalizado inteiramente em branco
- **WHEN** o dashboard consulta o período
- **THEN** recebe no máximo cinco atividades por instante/tipo/ID decrescentes; o Simulado em branco pode aparecer uma vez e não acrescenta resposta às métricas

### Requirement: Autorização e minimização preservadas
As consultas SHALL usar a identidade autorizada no servidor e preservar permissões, respostas 401/403 e política no-store atuais. Interfaces SQL compartilhadas SHALL expor apenas os campos de leitura delimitados, sem credenciais, dados de sessão, contato de estudantes ou capacidade de escrita.

#### Scenario: Outra identidade solicitada
- **GIVEN** Alunos A e B com históricos distintos
- **WHEN** A consulta desempenho ou dashboard e tenta fornecer identificador de B
- **THEN** B não é consultado e o servidor mantém a rejeição de parâmetros indevidos e os dados próprios de A

#### Scenario: Dashboard administrativo
- **GIVEN** Administrador autorizado e um Aluno tentando acessar a mesma rota
- **WHEN** consultam o dashboard administrativo
- **THEN** somente o Administrador recebe contagens globais, sem dados pessoais ou histórico individual; o Aluno recebe a recusa atual

### Requirement: Snapshot e transação participantes
Cada diagnóstico/dashboard SHALL compartilhar a mesma conexão, snapshot consistente e instante em todas as consultas. Consumo interno pelo Plano SHALL respeitar o contexto autorizado recebido, sem abrir outra conexão, confirmar, reverter ou encerrar a transação externa. Procedures de leitura SHALL NOT efetuar escrita ou controle transacional.

#### Scenario: Nova resposta confirmada por outra conexão
- **GIVEN** dashboard iniciado e nova resposta confirmada depois da abertura do snapshot
- **WHEN** o dashboard termina de consultar métricas e atividades
- **THEN** nenhum bloco daquela resposta incorpora o novo fato e uma consulta posterior pode incorporá-lo

#### Scenario: Plano reverte após diagnóstico
- **GIVEN** geração/recalculo de Plano autorizado com contexto e relógio externos
- **WHEN** o diagnóstico termina e a operação externa falha depois de uma escrita participante
- **THEN** o diagnóstico não confirma nenhuma escrita e o rollback externo restaura o estado integral, mantendo conexão e instante até o encerramento pelo proprietário

### Requirement: Contratos SQL e resultados completos
As sete procedures e quatro views do inventário SHALL constituir interfaces de leitura explícitas e versionadas, com parâmetros vinculados e privilégios do invocador. Todos os resultados de cada chamada SHALL ser consumidos e o cursor liberado antes de outra operação, inclusive em erro, sem encerrar a conexão emprestada.

#### Scenario: Sequência de chamadas na mesma conexão
- **GIVEN** procedure com múltiplos resultados, inclusive conjunto de linhas vazio e resultado terminal do protocolo
- **WHEN** a aplicação chama outra procedure e depois executa uma operação na mesma conexão
- **THEN** todos os conjuntos úteis são retornados na ordem contratada e a conexão continua utilizável, sem resultados pendentes ou confirmação autônoma

#### Scenario: Fronteira de leitura entre proprietários
- **GIVEN** métricas reunindo fatos de Práticas e Simulados
- **WHEN** as procedures leem os contratos SQL públicos
- **THEN** recebem somente as colunas e predicados históricos publicados pelos proprietários, sem acesso genérico a persistência privada ou escrita cruzada

#### Scenario: Entrada vinculada e limite de consulta
- **GIVEN** parâmetros com aspas ou conteúdo semelhante a SQL e limites inválidos em chamada SQL direta
- **WHEN** a procedure é invocada
- **THEN** texto permanece dado, nenhum SQL adicional é executado e parâmetros estruturais inválidos são recusados sem leitura irrestrita
