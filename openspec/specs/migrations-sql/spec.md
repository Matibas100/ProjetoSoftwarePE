# migrations-sql Specification

## Purpose

Garantir evolução reproduzível, auditável e segura do schema MySQL da Plataforma ENEM por migrations versionadas em SQL puro, sem reexecutar mudanças nem perder dados existentes.

## Requirements

### Requirement: Descoberta e ordem determinística
O sistema SHALL reconhecer somente migrations cujo nome siga a convenção numérica oficial, SHALL rejeitar versões duplicadas ou lacunas na sequência e SHALL executar migrations pendentes em ordem crescente.

#### Scenario: Execução ordenada de migrations pendentes
- **GIVEN** um diretório com migrations válidas e consecutivas
- **WHEN** o operador solicita a atualização do banco
- **THEN** o sistema executa cada versão pendente uma única vez, da menor para a maior

#### Scenario: Histórico ou diretório inválido
- **GIVEN** versões duplicadas, ausentes, malformadas ou inseridas antes da última versão aplicada
- **WHEN** o sistema valida o conjunto de migrations
- **THEN** a execução é recusada antes de aplicar qualquer migration pendente

### Requirement: Histórico persistente e checksum
O sistema SHALL controlar migrations na tabela `schema_migrations`, registrando versão, arquivo, checksum SHA-256, estado e datas relevantes. O sistema MUST interromper a operação quando uma migration aplicada tiver sido alterada, removida ou associada a outro arquivo.

#### Scenario: Migration aplicada permanece íntegra
- **GIVEN** uma migration registrada como aplicada e com checksum correspondente ao arquivo atual
- **WHEN** o histórico é conferido
- **THEN** a migration é reconhecida como válida e não é reexecutada

#### Scenario: Drift no histórico
- **GIVEN** uma migration aplicada cujo arquivo foi alterado, removido ou renomeado
- **WHEN** o histórico é conferido
- **THEN** o sistema bloqueia novas execuções e identifica a versão inconsistente sem expor credenciais

#### Scenario: Execução repetida sem pendências
- **GIVEN** todas as migrations válidas registradas como aplicadas
- **WHEN** o operador solicita novamente a atualização
- **THEN** nenhuma instrução daquelas migrations é executada e o banco permanece inalterado

### Requirement: Controle de concorrência
O sistema SHALL obter um lock consultivo exclusivo do MySQL, específico para o schema selecionado, antes de consultar ou alterar o histórico e SHALL liberá-lo ao encerrar a operação.

#### Scenario: Outro runner mantém o lock
- **GIVEN** uma execução de migrations já ativa para o mesmo schema
- **WHEN** outro processo tenta iniciar uma operação de migration
- **THEN** o segundo processo não executa SQL de migration e termina com erro operacional claro

#### Scenario: Encerramento do runner
- **GIVEN** um runner que obteve o lock do schema
- **WHEN** sua operação termina com sucesso ou erro
- **THEN** o lock é liberado explicitamente ou pelo encerramento da conexão proprietária

### Requirement: Aplicação e tratamento seguro de falhas
O sistema SHALL registrar o início antes de executar uma migration e SHALL registrar `APPLIED` somente depois de todas as suas instruções terminarem com sucesso. Falhas ou interrupções SHALL deixar estado bloqueante, e versões posteriores MUST NOT ser executadas até reconciliação operacional explícita.

#### Scenario: Migration concluída
- **GIVEN** uma migration pendente válida
- **WHEN** todas as suas instruções são executadas com sucesso
- **THEN** o histórico registra a versão como `APPLIED` com seu checksum e instante de conclusão

#### Scenario: Instrução SQL falha
- **GIVEN** uma migration em execução
- **WHEN** uma instrução retorna erro
- **THEN** o sistema interrompe a migration, registra `FAILED` quando a conexão permitir e não inicia versões posteriores

#### Scenario: Processo interrompido
- **GIVEN** uma migration registrada como `RUNNING`
- **WHEN** uma nova operação encontra esse estado persistente
- **THEN** o sistema considera a execução inconclusiva e bloqueia avanço ou reexecução automática

#### Scenario: Reconciliação de falha
- **GIVEN** uma migration em estado `FAILED` ou `RUNNING`
- **WHEN** o operador consulta o procedimento de recuperação
- **THEN** o sistema informa a versão afetada e exige verificação do schema, backup ou correção compensatória antes de permitir nova tentativa

### Requirement: Suporte a SQL procedural do MySQL
O sistema SHALL executar Stored Procedures e demais instruções SQL compatíveis com o contrato de migrations, incluindo arquivos que usem `DELIMITER`, sem enviar essa diretiva de cliente ao servidor.

#### Scenario: Migration cria Stored Procedure
- **GIVEN** uma migration válida que define delimitador e contém uma Stored Procedure com instruções internas separadas por ponto e vírgula
- **WHEN** a migration é aplicada
- **THEN** a definição completa é enviada como uma única instrução apropriada e a procedure fica disponível no MySQL

#### Scenario: Procedure existente após adoção
- **GIVEN** um banco MVP que contém `sp_questoes_por_assunto`
- **WHEN** o histórico oficial é adotado
- **THEN** a procedure é preservada e continua retornando questões ordenadas por `id`

### Requirement: Adoção segura do banco existente
O sistema SHALL oferecer baseline explícito para reconhecer somente estados históricos conhecidos do MVP. O baseline SHALL validar o schema e a Stored Procedure antes de registrar as versões correspondentes e MUST NOT modificar tabelas funcionais nem dados existentes.

#### Scenario: Banco MVP no estado consolidado
- **GIVEN** as tabelas, constraints, índices e Stored Procedure correspondentes ao estado após as migrations legadas `001` e `002`
- **WHEN** o operador confirma a adoção do baseline
- **THEN** o sistema registra as versões históricas com os checksums atuais sem executar novamente seus DDLs

#### Scenario: Banco MVP em estado histórico intermediário
- **GIVEN** um schema que corresponde exatamente a um prefixo histórico conhecido
- **WHEN** o operador confirma a adoção do baseline e solicita atualização
- **THEN** somente o prefixo comprovado é registrado e as versões posteriores são aplicadas normalmente

#### Scenario: Schema desconhecido ou divergente
- **GIVEN** um banco não vazio que não corresponde a nenhum estado histórico aceito
- **WHEN** o operador solicita o baseline
- **THEN** a adoção é recusada sem modificar dados nem registrar versões presumidas

### Requirement: Instalação limpa e equivalência do schema
O sistema SHALL permitir que um schema MySQL vazio alcance o estado consolidado exclusivamente pela sequência oficial. O resultado SHALL ser estruturalmente equivalente ao bootstrap `create_database.sql` para os objetos do MVP.

#### Scenario: Aplicação em schema vazio
- **GIVEN** um schema MySQL 8 existente, vazio e selecionado explicitamente
- **WHEN** todas as migrations oficiais são aplicadas
- **THEN** `materias`, `assuntos`, `questoes`, suas constraints e `sp_questoes_por_assunto` correspondem ao estado consolidado esperado

#### Scenario: Bootstrap e migrations divergem
- **GIVEN** schemas independentes criados pelo bootstrap e pela sequência de migrations
- **WHEN** suas estruturas oficiais são comparadas
- **THEN** a validação falha se houver divergência em tabelas, colunas, índices, constraints ou Stored Procedure do MVP

### Requirement: Configuração segura e compatibilidade
O sistema SHALL reutilizar a configuração MySQL por ambiente, SHALL operar apenas no schema explicitamente selecionado e MUST NOT registrar ou exibir senhas, URLs com credenciais ou conteúdo sensível. A adoção da infraestrutura SHALL preservar os contratos HTTP, as 10 funcionalidades e toda a regressão automatizada atual.

#### Scenario: Configuração incompleta
- **GIVEN** variáveis obrigatórias do MySQL ausentes ou inválidas
- **WHEN** uma operação de migration é solicitada
- **THEN** o sistema encerra antes da conexão com uma mensagem que cita somente os nomes das configurações ausentes

#### Scenario: Regressão do MVP
- **GIVEN** o schema atualizado pela infraestrutura oficial
- **WHEN** a suíte automatizada atual é executada
- **THEN** as 29 integrações originais, os testes adicionais e os contratos existentes permanecem aprovados
