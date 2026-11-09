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
O sistema SHALL oferecer baseline explícito para reconhecer somente estados históricos conhecidos do MVP. O baseline SHALL validar o schema e a Stored Procedure antes de registrar as versões correspondentes e MUST NOT modificar tabelas funcionais nem dados existentes. Para os prefixos 008–010, o reconhecimento SHALL considerar a estrutura efetiva, sem recusar o caso conhecido de charset redundante na apresentação do DDL quando os metadados forem iguais.

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

#### Scenario: Adoção de cópia restaurada estruturalmente equivalente
- **GIVEN** uma cópia sem histórico correspondente ao prefixo 008, 009 ou 010, com estrutura e procedure válidas, cuja apresentação do DDL passou a explicitar um charset já efetivo
- **WHEN** o operador confirma o baseline e solicita atualização
- **THEN** somente o prefixo comprovado é registrado com os checksums oficiais, sem recriar tabelas ou alterar dados funcionais durante o baseline
- **AND** a atualização executa somente versões posteriores e uma segunda atualização sem pendências executa zero migrations

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

### Requirement: Reconhecimento independente da apresentação do DDL
O sistema SHALL reconhecer os prefixos 008–010 por estrutura conhecida e determinística. A apresentação implícita ou explícita de charset, o nome físico do schema e contadores estatísticos SHALL NOT causar divergência quando os metadados estruturais forem equivalentes. Referências esperadas MUST provir da estrutura oficial, nunca da aceitação automática do banco encontrado.

#### Scenario: Charset redundante após restauração
- **GIVEN** schemas MySQL 8 conhecidos com metadados estruturais iguais, um deles restaurado com `CHARACTER SET utf8mb4` explícito onde antes era implícito
- **WHEN** o reconhecimento estrutural é solicitado
- **THEN** ambos são reconhecidos como o mesmo prefixo histórico
- **AND** a igualdade de apresentação textual do DDL não é exigida

#### Scenario: Identidade física e estatísticas não são estrutura
- **GIVEN** dois schemas oficiais com nomes físicos, próximos valores AUTO_INCREMENT e estatísticas diferentes, mas estrutura igual
- **WHEN** seus estados históricos são reconhecidos
- **THEN** o prefixo reconhecido é igual em ambos
- **AND** os atributos estruturais de AUTO_INCREMENT das colunas continuam sendo verificados

#### Scenario: Histórico restaurado permanece íntegro
- **GIVEN** uma cópia estruturalmente equivalente com histórico válido e todas as versões oficiais já aplicadas
- **WHEN** o operador solicita atualização
- **THEN** os checksums existentes continuam sendo conferidos e nenhuma migration é reexecutada
- **AND** hashes de reconhecimento estrutural não substituem checksums dos arquivos SQL no histórico

### Requirement: Rejeição conservadora de divergência estrutural
O sistema SHALL rejeitar diferenças reais nas tabelas reconhecidas dos prefixos 008–010, incluindo colunas, defaults, charset/collation, índices, FKs, CHECKs e expressões geradas. Metadados insuficientes SHALL resultar em erro, sem aceitação permissiva. A conferência SHALL preservar dados e as proteções existentes de histórico, procedure, concorrência e falha.

#### Scenario: Alteração real em tabela protegida
- **GIVEN** uma cópia do prefixo conhecido com diferença de tabela esperada, engine/opções persistentes, coluna/ordem/tipo/nulabilidade/default, charset/collation, índice/ordem/unicidade/visibilidade, FK/destino/regras, expressão gerada ou CHECK/ENFORCED
- **WHEN** o operador solicita reconhecimento para baseline
- **THEN** o sistema recusa a estrutura divergente sem registrar versões presumidas ou modificar dados funcionais
- **AND** não obtém uma nova referência esperada a partir da cópia divergente

#### Scenario: Referência externa não equivale a referência interna
- **GIVEN** uma FK que aponta para outro schema, embora nomes de tabela e coluna coincidam com os esperados no próprio schema
- **WHEN** a estrutura é conferida
- **THEN** o sistema recusa a divergência de destino
- **AND** a portabilidade do nome físico do banco não elimina essa verificação

#### Scenario: Metadados obrigatórios indisponíveis
- **GIVEN** que não é possível obter algum metadado obrigatório para comprovar a estrutura conhecida
- **WHEN** o reconhecimento é solicitado
- **THEN** o sistema retorna erro operacional sem credenciais ou dados pessoais e não presume compatibilidade

#### Scenario: Proteções anteriores continuam bloqueantes
- **GIVEN** histórico com checksum divergente, execução RUNNING/FAILED, lock mantido por outro runner ou procedure incompatível
- **WHEN** a operação correspondente de migration ou baseline é solicitada
- **THEN** a operação continua bloqueada conforme as regras existentes, mesmo que as novas assinaturas estruturais sejam iguais

#### Scenario: Corpo e parâmetros da procedure nos prefixos 008–010
- **GIVEN** tabelas com assinaturas estruturais oficiais do prefixo 008, 009 ou 010 e procedure existente com corpo ou parâmetros divergentes do contrato conhecido
- **WHEN** o operador solicita baseline
- **THEN** a operação é recusada sem registrar versões presumidas nem modificar dados funcionais
- **AND** o comportamento dos validadores anteriores a 008 permanece preservado

### Requirement: Reconhecimento dos recursos SQL acadêmicos
O sistema SHALL reconhecer os prefixos 011/012 somente quando as tabelas e os recursos SQL oficiais correspondentes estiverem íntegros. Assinaturas de procedures, contratos de views e corpos SQL SHALL ser conferidos contra referências oficiais independentes do banco encontrado, preservando os validadores dos prefixos anteriores e a procedure legada.

#### Scenario: Instalação e upgrade preservam registros
- **GIVEN** schema vazio ou cópia válida do prefixo 010 com dados sintéticos
- **WHEN** o runner aplica a sequência oficial até 012
- **THEN** as sete procedures e quatro views ficam disponíveis, as tabelas e registros anteriores permanecem intactos e a segunda atualização executa zero migrations
- **AND** os arquivos e checksums das migrations 000–010 permanecem inalterados

#### Scenario: Bootstrap equivalente
- **GIVEN** schemas independentes instalados pelo bootstrap consolidado e pela sequência até 012
- **WHEN** os objetos oficiais são comparados
- **THEN** tabelas, constraints, procedure legada, sete procedures novas e quatro views apresentam os mesmos contratos e comportamento

#### Scenario: Adoção de novos prefixos completos
- **GIVEN** cópia sem histórico correspondente exatamente a 011 ou 012
- **WHEN** o operador confirma baseline
- **THEN** somente o prefixo comprovado é registrado com os checksums oficiais, sem recriar recursos ou alterar dados funcionais
- **AND** a atualização aplica somente as migrations posteriores ao prefixo reconhecido

#### Scenario: Recurso parcial ou divergente
- **GIVEN** recursos identificáveis de 011/012 com procedure ou view ausente, corpo alterado, assinatura divergente, dependência externa ao schema ou privilégio incompatível
- **WHEN** o reconhecimento para baseline é solicitado
- **THEN** a operação falha sem registrar prefixo presumido e sem recuar silenciosamente para 010/011 para esconder a divergência

#### Scenario: Portabilidade restrita e metadados insuficientes
- **GIVEN** restauração equivalente em outro schema MySQL 8, com identidade física do instalador diferente
- **WHEN** todos os metadados obrigatórios podem ser conferidos
- **THEN** nomes físicos locais e identidade do instalador não causam divergência, mas segurança do invocador, assinatura, colunas e dependências dos recursos continuam verificadas
- **AND** ausência de metadado obrigatório causa erro, sem aprovação por mera existência dos objetos

#### Scenario: Prefixos históricos e falhas continuam protegidos
- **GIVEN** prefixo válido entre 000 e 010 sem recursos das novas versões, ou histórico com drift/RUNNING/FAILED
- **WHEN** ocorre reconhecimento ou atualização
- **THEN** os estados antigos válidos continuam reconhecíveis e as proteções de checksum, lock, falha e procedure legada continuam bloqueantes quando aplicáveis

### Requirement: Reconhecimento e instalação do prefixo 013
O sistema SHALL instalar e reconhecer o prefixo 013 somente com o prefixo 012 íntegro e todas as procedures inventariadas com assinaturas, corpos e segurança oficiais. Bootstrap e sequência SHALL ser equivalentes. Baseline/instalação SHALL NOT executar os casos funcionais das routines ou alterar dados existentes.

#### Scenario: Instalação limpa e upgrade
- **GIVEN** schema vazio ou cópia válida de 012 com dados sintéticos
- **WHEN** a sequência oficial é aplicada até 013 e repetida
- **THEN** o banco contém as routines previstas, dados e objetos anteriores intactos, e a segunda atualização executa zero migrations

#### Scenario: Bootstrap e baseline do prefixo completo
- **GIVEN** schemas criados pelo bootstrap e pela sequência até 013, sem histórico em uma das cópias restauradas
- **WHEN** são comparados os objetos e confirmado baseline da cópia completa
- **THEN** os contratos SQL são equivalentes e somente o prefixo comprovado é registrado, sem recriar tabelas, criar decisões/contas ou eliminar dados

#### Scenario: Procedure parcial ou incompatível
- **GIVEN** indícios de 013 com recurso ausente, corpo/assinatura/segurança alterados ou metadados insuficientes
- **WHEN** o reconhecimento é solicitado
- **THEN** a operação falha sem presumir versão, usar o banco encontrado como referência ou recuar a prefixo inferior para ocultar a divergência

#### Scenario: Histórico e recursos anteriores preservados
- **GIVEN** prefixo anterior válido, ou histórico com checksum divergente/RUNNING/FAILED
- **WHEN** o runner executa reconhecimento ou atualização
- **THEN** prefixos anteriores válidos continuam reconhecíveis e os bloqueios existentes de falha, lock, checksum e procedure legada permanecem

### Requirement: Reconhecimento e instalação do prefixo 014
O sistema SHALL instalar e reconhecer o prefixo 014 somente com o prefixo 013 íntegro e todas as procedures inventariadas com assinaturas, corpos e segurança oficiais. Bootstrap e sequência SHALL ser equivalentes. Baseline/instalação SHALL NOT executar os casos funcionais das routines ou alterar dados existentes.

#### Scenario: Instalação limpa e upgrade
- **GIVEN** schema vazio ou cópia válida de 013 com dados sintéticos
- **WHEN** a sequência oficial é aplicada até 014 e repetida
- **THEN** o banco contém as routines previstas, dados e objetos anteriores intactos, e a segunda atualização executa zero migrations

#### Scenario: Bootstrap e baseline do prefixo completo
- **GIVEN** schemas criados pelo bootstrap e pela sequência até 014, sem histórico em uma das cópias restauradas
- **WHEN** são comparados os objetos e confirmado baseline da cópia completa
- **THEN** os contratos SQL são equivalentes e somente o prefixo comprovado é registrado, sem recriar tabelas, criar decisões/contas ou eliminar dados

#### Scenario: Upgrade bloqueado por dependência física divergente
- **GIVEN** histórico íntegro até 013 e tabela, procedure legada ou recurso SQL anterior ausente/divergente
- **WHEN** o runner tenta aplicar 014
- **THEN** valida o prefixo físico sob seu lock e recusa o upgrade antes de registrar ou executar 014, preservando dados, objetos e histórico encontrados

#### Scenario: Procedure parcial ou incompatível
- **GIVEN** indícios de 014 com recurso ausente, corpo/assinatura/segurança alterados ou metadados insuficientes
- **WHEN** o reconhecimento é solicitado
- **THEN** a operação falha sem presumir versão, usar o banco encontrado como referência ou recuar a prefixo inferior para ocultar a divergência

#### Scenario: Histórico e recursos anteriores preservados
- **GIVEN** prefixo anterior válido, ou histórico com checksum divergente/RUNNING/FAILED
- **WHEN** o runner executa reconhecimento ou atualização
- **THEN** prefixos anteriores válidos continuam reconhecíveis e os bloqueios existentes de falha, lock, checksum e procedure legada permanecem

### Requirement: Reconhecimento e instalação do prefixo 015
O sistema SHALL instalar e reconhecer o prefixo 015 somente com o prefixo 014 íntegro e todas as procedures inventariadas com assinaturas, corpos e segurança oficiais. Bootstrap e sequência SHALL ser equivalentes. Baseline/instalação SHALL NOT executar os casos funcionais das routines ou alterar dados existentes.

#### Scenario: Instalação limpa e upgrade
- **GIVEN** schema vazio ou cópia válida de 014 com dados sintéticos
- **WHEN** a sequência oficial é aplicada até 015 e repetida
- **THEN** o banco contém as routines previstas, dados e objetos anteriores intactos, e a segunda atualização executa zero migrations

#### Scenario: Bootstrap e baseline do prefixo completo
- **GIVEN** schemas criados pelo bootstrap e pela sequência até 015, sem histórico em uma das cópias restauradas
- **WHEN** são comparados os objetos e confirmado baseline da cópia completa
- **THEN** os contratos SQL são equivalentes e somente o prefixo comprovado é registrado, sem recriar tabelas, criar decisões/contas ou eliminar dados

#### Scenario: Procedure parcial ou incompatível
- **GIVEN** indícios de 015 com recurso ausente, corpo/assinatura/segurança alterados ou metadados insuficientes
- **WHEN** o reconhecimento é solicitado
- **THEN** a operação falha sem presumir versão, usar o banco encontrado como referência ou recuar a prefixo inferior para ocultar a divergência

#### Scenario: Histórico e recursos anteriores preservados
- **GIVEN** prefixo anterior válido, ou histórico com checksum divergente/RUNNING/FAILED
- **WHEN** o runner executa reconhecimento ou atualização
- **THEN** prefixos anteriores válidos continuam reconhecíveis e os bloqueios existentes de falha, lock, checksum e procedure legada permanecem


### Requirement: Reconhecimento e instalação do prefixo 016
O sistema SHALL instalar e reconhecer o prefixo 016 somente com o prefixo 015 íntegro e todas as procedures inventariadas com assinaturas, corpos e segurança oficiais. Bootstrap e sequência SHALL ser equivalentes. Baseline/instalação SHALL NOT executar os casos funcionais das routines ou alterar dados existentes.

#### Scenario: Instalação limpa e upgrade
- **GIVEN** schema vazio ou cópia válida de 015 com dados sintéticos
- **WHEN** a sequência oficial é aplicada até 016 e repetida
- **THEN** o banco contém as routines previstas, dados e objetos anteriores intactos, e a segunda atualização executa zero migrations

#### Scenario: Bootstrap e baseline do prefixo completo
- **GIVEN** schemas criados pelo bootstrap e pela sequência até 016, sem histórico em uma das cópias restauradas
- **WHEN** são comparados os objetos e confirmado baseline da cópia completa
- **THEN** os contratos SQL são equivalentes e somente o prefixo comprovado é registrado, sem recriar tabelas, criar decisões/contas ou eliminar dados

#### Scenario: Procedure parcial ou incompatível
- **GIVEN** indícios de 016 com recurso ausente, corpo/assinatura/segurança alterados ou metadados insuficientes
- **WHEN** o reconhecimento é solicitado
- **THEN** a operação falha sem presumir versão, usar o banco encontrado como referência ou recuar a prefixo inferior para ocultar a divergência

#### Scenario: Histórico e recursos anteriores preservados
- **GIVEN** prefixo anterior válido, ou histórico com checksum divergente/RUNNING/FAILED
- **WHEN** o runner executa reconhecimento ou atualização
- **THEN** prefixos anteriores válidos continuam reconhecíveis e os bloqueios existentes de falha, lock, checksum e procedure legada permanecem

### Requirement: Reconhecimento e instalação do prefixo 017
O sistema SHALL instalar/reconhecer 017 somente sobre 016 íntegro e com `sp_alunos_admin` e `sp_usuario_gestao_bloqueado` nos contratos oficiais. Bootstrap e sequência SHALL ser equivalentes. Assinaturas SHALL vir de referência oficial independente do banco encontrado. A instalação SHALL preservar tabelas, dados, evidências, FKs, procedures anteriores e checksums 000–016, sem criar contas ou aceites.

#### Scenario: Instalação limpa e upgrade preservam dados
- **GIVEN** schema vazio ou cópia válida de 016 com usuários, sessões, respostas e decisões sintéticas
- **WHEN** a sequência oficial é aplicada até 017 e repetida
- **THEN** as duas routines novas estão disponíveis, dados e objetos anteriores permanecem intactos e a segunda atualização executa zero migrations

#### Scenario: Snapshot e baseline equivalentes
- **GIVEN** schemas independentes criados pelo bootstrap e sequência até 017, com uma cópia equivalente sem histórico
- **WHEN** objetos são comparados e baseline da cópia é solicitado
- **THEN** contratos equivalem e somente o prefixo completo comprovado é registrado, sem executar a gestão de usuários ou fabricar evidências

#### Scenario: Prefixo parcial ou dependência divergente
- **GIVEN** 016 divergente, somente uma das routines de 017, assinatura/corpo/segurança alterados ou metadados insuficientes
- **WHEN** o runner tenta atualizar ou reconhecer o prefixo
- **THEN** recusa o estado sem presumir assinatura, registrar sucesso parcial ou recuar para esconder a divergência; preflight físico bloqueia upgrade sobre dependência inválida

#### Scenario: Proteções e prefixos antigos continuam válidos
- **WHEN** runner encontra prefixo anterior íntegro ou histórico com checksum inválido/RUNNING/FAILED
- **THEN** mantém reconhecimento dos prefixos válidos e bloqueios existentes de histórico, lock, falha e procedure legada, sem aceitar o banco encontrado como fonte da referência
