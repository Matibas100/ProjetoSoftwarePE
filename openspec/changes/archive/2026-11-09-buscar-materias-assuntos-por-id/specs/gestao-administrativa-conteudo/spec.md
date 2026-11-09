# Spec Delta

## ADDED Requirements

### Requirement: Edição do catálogo começa com consulta individual
Ao acionar Editar em ADM-CON-001 ou ADM-CON-002, a tela SHALL consultar o GET individual usando o ID da linha e preencher o formulário somente após sucesso válido. Dados da linha SHALL NOT substituir a leitura individual. O carregamento SHALL ser anunciado no bloco de edição, sem disparar escrita, perder filtros/página ou redesenhar a tela existente.

#### Scenario: Matéria mudou após a listagem
- **GIVEN** linha de Matéria carregada e registro alterado no servidor depois disso
- **WHEN** Administrador aciona Editar
- **THEN** ocorre GET do ID selecionado e o formulário mostra nome, descrição, Área e status da resposta atual, sem reutilizar os valores antigos da linha
- **AND** nenhuma escrita é enviada até confirmação explícita de Salvar

#### Scenario: Assunto foi transferido antes de editar
- **GIVEN** linha de Assunto com Matéria antiga e transferência confirmada no servidor
- **WHEN** Administrador aciona Editar
- **THEN** formulário e referência de origem usam `materia_id` do detalhe atual, com a Matéria corrente selecionada
- **AND** salvar sem mudar essa seleção não inicia uma transferência fictícia com base na linha antiga

#### Scenario: Vínculo atual indisponível para novos usos
- **GIVEN** Assunto cuja Matéria corrente está inativa ou arquivada
- **WHEN** o detalhe é carregado para edição
- **THEN** a Matéria corrente permanece identificável e selecionada; as outras opções de novo vínculo continuam limitadas às Matérias ativas
- **AND** o servidor continua validando as regras existentes no salvamento

### Requirement: Falha de detalhe preserva formulário e contexto
Erro 404, rede, 500, resposta inválida ou falha ao carregar opções necessárias SHALL impedir substituição do formulário e anunciar o problema no contexto de edição. Campos, ID anterior, alterações não salvas e filtros SHALL permanecer; a tela SHALL NOT usar dados antigos da linha como fallback nem anunciar sucesso. Repetir consulta SHALL exigir nova ação explícita.

#### Scenario: Registro excluído entre listagem e edição
- **GIVEN** uma linha ainda visível cujo registro foi excluído e um formulário anterior válido
- **WHEN** o GET individual retorna 404
- **THEN** aparece erro de registro não encontrado e o formulário anterior permanece associado ao seu ID, sem assumir o ID da linha excluída

#### Scenario: Rede ou resposta malformada
- **GIVEN** formulário preenchido e leitura individual em andamento
- **WHEN** o servidor está indisponível ou retorna resposta incompatível
- **THEN** a tela conserva o rascunho, libera os controles aplicáveis e permite selecionar Editar novamente, sem fallback nem retry automático

### Requirement: Leituras atrasadas respeitam a intenção mais recente
Resultado de detalhe SHALL ser aplicado somente à seleção vigente e à mesma identidade autorizada, sem alterações locais posteriores ao início da consulta. Selecionar outro registro, iniciar criação, cancelar, salvar ou editar campos SHALL invalidar leitura anterior. Enquanto a leitura vigente estiver pendente, Salvar SHALL permanecer bloqueado para evitar envio ao registro errado.

#### Scenario: Selecionar dois registros rapidamente
- **WHEN** consultas de A e B ficam pendentes e a resposta de A chega depois da de B
- **THEN** somente B pode preencher o editor e a conclusão de A não altera campos, mensagens ou estado de salvamento de B

#### Scenario: Digitar durante a leitura
- **GIVEN** formulário anterior preservado e detalhe solicitado
- **WHEN** Administrador modifica um campo antes da resposta
- **THEN** a leitura pendente é invalidada e a digitação não é sobrescrita; nova seleção explícita permite consultar o registro pretendido

#### Scenario: Nova criação ou cancelamento
- **WHEN** Administrador confirma iniciar novo cadastro ou cancelar enquanto um detalhe está pendente
- **THEN** o resultado anterior não preenche o formulário após essa ação e nenhuma mutação é enviada pela leitura

### Requirement: Consulta individual preserva descarte e recuperação de identidade
Antes de substituir formulário alterado, Editar SHALL manter a confirmação de descarte existente. Cancelar essa confirmação SHALL preservar os dados sem iniciar novo GET. Perda ou troca de identidade SHALL invalidar leituras pendentes e preservar o fluxo administrativo de recuperação, sem aplicar dados atrasados nem repetir escrita/consulta automaticamente.

#### Scenario: Manter rascunho em vez de editar outro registro
- **GIVEN** formulário com alterações não salvas
- **WHEN** Administrador seleciona outro item e escolhe continuar editando na confirmação
- **THEN** nenhum GET desse novo item é enviado e o rascunho original permanece

#### Scenario: Descarte autorizado mas consulta falha
- **GIVEN** Administrador confirmou troca de item com alterações não salvas
- **WHEN** a consulta individual falha antes de carregar o novo registro
- **THEN** os campos anteriores ainda estão disponíveis, sem marcar o rascunho como salvo ou substituí-lo parcialmente

#### Scenario: Sessão expira ou outra conta é detectada
- **WHEN** ocorre 401, bloqueio de identidade ou troca de conta durante a consulta
- **THEN** resposta tardia não preenche o editor; recuperação segue o fluxo existente e exige nova seleção explícita após liberação da mesma conta ou descarte/recarga para conta diferente
