# questoes-versionadas Specification

## Purpose

Permitir gestão básica de Questões por Administrador e preservar versões publicadas para correções, tentativas e históricos estáveis.

## Requirements

### Requirement: Listagem e detalhe administrativos de Questões
O sistema SHALL oferecer listagem filtrada e detalhe de Questões exclusivamente à Administração.

#### Scenario: Filtros combinados
- **GIVEN** Administrador e Questões de diferentes classificações e estados
- **WHEN** aplica filtros válidos à listagem
- **THEN** recebe somente os itens correspondentes na ordem e paginação estabelecidas, ou página vazia com metadados coerentes

#### Scenario: Filtro ou recurso inválido
- **GIVEN** Administrador autenticado
- **WHEN** fornece paginação/filtro inválido ou consulta ID inexistente
- **THEN** recebe respectivamente 400 ou 404 sem erro interno ou alteração de dados

#### Scenario: Consulta não autorizada
- **GIVEN** cliente anônimo ou Aluno
- **WHEN** consulta listagem ou detalhe administrativo
- **THEN** recebe respectivamente 401 ou 403, sem dados de Questão ou gabarito

#### Scenario: Filtros e paginação administrativos de Questões
- **GIVEN** cliente usando a listagem administrativa de Questões
- **WHEN** o servidor valida filtros e compõe a página
- **THEN** O sistema SHALL oferecer `GET /api/admin/questoes` com filtros combináveis de busca por enunciado, Área, Matéria, Assunto, dificuldade e status, ordenado por ID decrescente.
- **THEN** SHALL usar envelope `itens`, `pagina`, `por_pagina`, `total_itens`, `total_paginas`, padrão 1/20 e máximo 100 itens por página.
- **THEN** Busca SHALL ter até 100 caracteres; IDs SHALL ser inteiros positivos; status SHALL aceitar rascunho/publicada/arquivada e dificuldade facil/media/dificil.

#### Scenario: Detalhe e autorização administrativos de Questões
- **GIVEN** cliente consultando listagem ou detalhe de Questões
- **WHEN** o servidor verifica perfil e retorna o conteúdo permitido
- **THEN** `GET /api/questoes/<id>` SHALL retornar conteúdo administrativo, status, revisão e versões.
- **THEN** Todas essas operações SHALL exigir Administrador e SHALL NOT fornecer gabarito ao Aluno.

### Requirement: Cadastro e edição de rascunho compatíveis
O sistema SHALL preservar o cadastro legado e editar rascunhos de Questões com validação e controle de revisão.

#### Scenario: Cadastro válido sem publicação
- **GIVEN** Administrador com sessão, origem e CSRF válidos e catálogo ativo
- **WHEN** cadastra conteúdo válido
- **THEN** recebe o payload legado 201 e a Questão fica em rascunho, indisponível para novos usos do Aluno

#### Scenario: Edição de Questão publicada
- **GIVEN** Questão publicada e revisão atual
- **WHEN** o Administrador salva alteração válida no rascunho
- **THEN** conteúdo administrativo e revisão são atualizados e a versão publicada anterior permanece intacta até publicação explícita

#### Scenario: Edição conflitante ou inválida
- **GIVEN** rascunho aberto por um Administrador
- **WHEN** envia revisão obsoleta ou conteúdo inválido
- **THEN** recebe 409 ou 400, respectivamente, sem alteração parcial

#### Scenario: Contrato de criação e atualização do rascunho
- **GIVEN** Administrador cadastrando ou editando Questão
- **WHEN** envia conteúdo à API de Questões
- **THEN** O sistema SHALL manter `POST /api/questoes` com validações, campos e sucesso 201 existentes, criando rascunho não publicado.
- **THEN** `PUT /api/questoes/<id>` SHALL editar somente campos de conteúdo/classificação com `revisao` obrigatória, permitir alterações parciais válidas e recusar campos desconhecidos com 400.
- **THEN** Enunciado e cinco alternativas SHALL ser textos não vazios; gabarito SHALL ser A–E, dificuldade facil/media/dificil, explicação texto ou null e Assunto/Matéria SHALL estar ativos.

#### Scenario: Revisão e versão publicada após edição
- **GIVEN** Questão com revisão corrente ou obsoleta, publicada ou arquivada
- **WHEN** o servidor avalia a edição do rascunho
- **THEN** Edição SHALL incrementar revisão sem alterar versão publicada; revisão obsoleta ou Questão arquivada SHALL retornar 409.

### Requirement: Publicação explícita com versão imutável
O sistema SHALL publicar explicitamente versões imutáveis de Questões, preservando versões anteriores.

#### Scenario: Publicação revisada
- **GIVEN** rascunho válido e confirmação autorizada
- **WHEN** Administrador publica a revisão atual
- **THEN** snapshot, decisão e ponteiro publicado são persistidos atomicamente e a versão fica elegível para novos usos

#### Scenario: Nova versão ou replay
- **GIVEN** Questão já publicada
- **WHEN** publica nova revisão válida ou repete a publicação da mesma revisão
- **THEN** nova revisão cria versão distinta preservando a anterior; replay retorna versão existente sem novo evento

#### Scenario: Falha composta ou sessão vencida
- **GIVEN** publicação em andamento
- **WHEN** falha uma gravação ou faltam sessão/CSRF/reautenticação válidos
- **THEN** não ocorre publicação parcial nem exposição de segredos e a operação protegida recebe erro correspondente

#### Scenario: Controles e snapshot da publicação de Questão
- **GIVEN** Administrador solicitando publicação de uma revisão
- **WHEN** o servidor verifica controles e valida conteúdo e catálogo
- **THEN** `POST /api/questoes/<id>/publicar` SHALL exigir Administrador, reautenticação nos últimos 15 minutos, origem/CSRF, revisão atual, `confirmar:true` e motivo de 3–500 caracteres após trim.
- **THEN** SHALL validar conteúdo e catálogo, registrar revisão/aprovação/publicação com ator e motivo e disponibilizar snapshot imutável com número único, conteúdo completo, gabarito e classificação.

#### Scenario: Preservação e replay da publicação de Questão
- **GIVEN** Questão já publicada ou arquivada
- **WHEN** é solicitada outra publicação
- **THEN** Nova publicação SHALL preservar versões anteriores; revisão já publicada SHALL retornar a mesma versão sem duplicação.
- **THEN** Arquivada SHALL rejeitar publicação com 409.

### Requirement: Arquivamento sem perda de conteúdo
`POST /api/questoes/<id>/arquivar` SHALL exigir as mesmas confirmações, revisão, motivo e controles de sessão da publicação. SHALL registrar ator/motivo e marcar a identidade arquivada atomicamente, impedindo novos usos sem excluir Questão, versões ou referências. Replay de arquivamento concluído SHALL retornar estado atual sem duplicar eventos. Esta capacidade SHALL NOT oferecer exclusão física ou reativação.

#### Scenario: Retirada de uso
- **GIVEN** Questão com versão publicada referenciada
- **WHEN** Administrador confirma arquivamento válido
- **THEN** novos usos ficam indisponíveis e referências existentes podem continuar lendo a versão original

#### Scenario: Arquivamento repetido
- **GIVEN** Questão já arquivada
- **WHEN** repete a ação autorizada
- **THEN** recebe estado arquivado e nenhum conteúdo/evento é duplicado ou removido

### Requirement: Elegibilidade e preservação do legado
Novos usos SHALL obter somente versão igual ao ponteiro publicado de identidade não arquivada com Assunto/Matéria referenciados ativos. Conteúdo, gabarito e classificação histórica SHALL ser preservados por versão. Migration SHALL manter IDs e dados legados e SHALL NOT publicar automaticamente o backfill. `GET /api/questoes/por-assunto` e `sp_questoes_por_assunto` SHALL manter campos, ordenação e consulta administrativa existentes, incluindo conteúdo indisponível para novos usos.

#### Scenario: Backfill do banco existente
- **GIVEN** banco com Questões anteriores à gestão versionada
- **WHEN** upgrade é aplicado pelo runner
- **THEN** IDs e conteúdo permanecem, origem legada é registrada sem autoria inventada e nenhuma Questão é publicada automaticamente

#### Scenario: Consulta administrativa legada
- **GIVEN** Administrador autorizado e Questões no Assunto solicitado
- **WHEN** usa a busca legada após edição ou arquivamento
- **THEN** recebe os campos/ordenação anteriores sem substituir o contrato por DTO do Aluno

#### Scenario: Catálogo indisponível
- **GIVEN** versão publicada cujo Assunto ou Matéria foi inativado/arquivado
- **WHEN** um consumidor solicita elegibilidade para novo uso
- **THEN** a versão não é oferecida, mantendo consultas históricas intactas
