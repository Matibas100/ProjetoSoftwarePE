# Spec Delta — Reconhecimento estrutural do schema

## MODIFIED Requirements

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

## ADDED Requirements

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
