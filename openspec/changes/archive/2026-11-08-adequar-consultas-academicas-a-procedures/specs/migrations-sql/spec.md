# Delta — Recursos de consulta acadêmica

## ADDED Requirements

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
