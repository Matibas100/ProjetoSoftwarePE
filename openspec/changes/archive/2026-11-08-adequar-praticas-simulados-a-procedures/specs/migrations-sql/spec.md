# Delta — Prefixo 014

## ADDED Requirements

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
