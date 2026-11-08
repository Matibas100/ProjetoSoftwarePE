# Práticas e Simulados — Interfaces MySQL

## Purpose

Definir consultas especializadas MySQL para práticas, composição e execução de simulados, preservando propriedade, versões, idempotência e persistência atômica dos resultados.

## ADDED Requirements

### Requirement: Interfaces especializadas por procedures
O recorte inventariado SHALL executar filtros, JOINs, ordenações e operações especializadas pelas procedures oficiais do domínio, com parâmetros vinculados e CALL somente no Repository. CRUD básico SHALL permanecer nas Models e regras de negócio nos Services. SQL dinâmico e fallback ORM para rotina indisponível SHALL NOT ser usados.

#### Scenario: Consulta ou operação especializada autorizada
- **GIVEN** banco atualizado e cliente autorizado para a funcionalidade existente
- **WHEN** executa um caso de uso do inventário
- **THEN** o acesso especializado usa a procedure correspondente e mantém status, campos, tipos, nulos, ordenação e efeitos atuais

#### Scenario: Entrada vinculada e lote vazio
- **GIVEN** filtros textuais com caracteres especiais e listas de IDs vazias, repetidas ou com itens ausentes
- **WHEN** o caso de uso consulta seus dados
- **THEN** entradas são dados, sem execução de SQL adicional; lotes preservam a semântica de conjunto, vazios e ordenação atual sem duplicar registros

### Requirement: Compatibilidade e autorização do domínio
As interfaces SQL SHALL preservar permissões, identidade do servidor e respostas de validação/ausência/conflito existentes. Consultas de apresentação SHALL manter paginação, total independente da página, datas e conteúdo permitido. Procedures auxiliares SHALL NOT criar novas rotas, permissões ou funcionalidades declaradas.

#### Scenario: Cliente não autorizado ou parâmetro inválido
- **GIVEN** cliente anônimo, perfil insuficiente ou entrada inválida
- **WHEN** solicita uma operação protegida
- **THEN** recebe o mesmo erro atual sem conteúdo protegido, mutação parcial ou detalhe SQL

#### Scenario: Página sem resultados
- **GIVEN** listagem paginada do recorte com filtros válidos
- **WHEN** solicita uma página sem linhas
- **THEN** recebe itens vazios e total real correspondente aos filtros, sem linha fictícia ou alteração do envelope

### Requirement: Participação transacional e falha integral
As procedures SHALL usar a conexão e transação do caso de uso, preservar locks, leituras correntes e identidade dos registros alteráveis e SHALL NOT iniciar, confirmar ou reverter transações. Resultados SHALL ser consumidos e cursores liberados sem encerrar conexão emprestada. Falha SHALL manter os erros seguros atuais, sem sucesso parcial.

#### Scenario: Falha depois da leitura bloqueante
- **GIVEN** operação composta que mantém locks e realiza uma escrita após ler pela procedure
- **WHEN** uma etapa posterior falha antes do commit
- **THEN** o rollback externo restaura todas as alterações e os objetos carregados não levam a gravação parcial ou estado obsoleto

#### Scenario: Reutilização após resultado vazio ou erro
- **GIVEN** chamadas sucessivas na mesma conexão, incluindo resultado útil vazio e falha de routine
- **WHEN** o caso termina e uma nova operação usa a infraestrutura
- **THEN** não há resultados pendentes, conexão inválida é descartada e a API não retorna dados artificiais nem expõe SQL, parâmetros sensíveis ou credenciais

### Requirement: Propriedade, replay e correção nas etapas atuais
As consultas SHALL limitar recursos pessoais ao dono da sessão e manter 404 uniforme para ausente/alheio. Replay e retomada SHALL preservar identidade e versões. Antes da conclusão permitida, conteúdo de correção SHALL NOT chegar ao HTTP/DOM, mesmo quando o Repository possui dados internos para o caso de uso.

#### Scenario: Retomada e conteúdo retirado
- **GIVEN** tentativa iniciada antes de arquivamento ou nova publicação de Questão/Simulado
- **WHEN** o dono retoma e outro cliente solicita novo início
- **THEN** a tentativa existente mantém a composição original e o novo início segue a indisponibilidade atual, sem substituição de Questões

#### Scenario: Consulta alheia ou correção antecipada
- **GIVEN** outra conta ou tentativa própria ainda em andamento
- **WHEN** consulta detalhe, resultado ou correção
- **THEN** recebe o mesmo 404/409 ou conteúdo seguro da etapa atual, sem gabarito antecipado ou leitura de outra conta

### Requirement: Respostas e finalização continuam atômicas
Leituras bloqueantes SHALL conservar a mesma ordem, revisão e identidade das entidades usadas na escrita pelas Models. Tentativa concluída SHALL permanecer imutável; concorrência SHALL NOT criar duas respostas definitivas, duas tentativas em andamento da mesma versão ou resultado parcial.

#### Scenario: Respostas concorrentes e finalização
- **GIVEN** duas requisições de salvar/finalizar a mesma tentativa com revisão corrente
- **WHEN** competem pelos locks
- **THEN** somente a operação compatível confirma e a obsoleta mantém o conflito atual, com totais e versão preservados

#### Scenario: Histórico, lotes e fatos do período
- **GIVEN** históricos de duas contas, composição com itens em ordem e fatos nos limites UTC
- **WHEN** lista páginas, lotes ou fatos internos
- **THEN** paginação/total, ordem de itens, distinção entre prática e Simulado e critérios de respondida/finalizada/não branca permanecem idênticos
