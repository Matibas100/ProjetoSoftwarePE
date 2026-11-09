# Spec Delta

## ADDED Requirements

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
