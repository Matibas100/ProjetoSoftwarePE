# gestao-administrativa-conteudo Specification

## Purpose

Definir o comportamento utilizável e visualmente aderente das telas administrativas de Matérias e Assuntos aprovadas no Desktop V1, integradas ao catálogo acadêmico real.

## Requirements

### Requirement: Estrutura administrativa do Desktop V1
As telas ADM-CON-001 e ADM-CON-002 SHALL reproduzir a composição, hierarquia, identidade visual e navegação administrativa aprovadas para 1440 px, usando os ativos oficiais e sem criar funcionalidades de produto fora do escopo.

#### Scenario: Abertura de Gestão de Matérias
- **WHEN** o administrador abre ADM-CON-001
- **THEN** a tela apresenta cabeçalho, navegação administrativa, título, ação `Nova matéria`, filtros, tabela, paginação e área contextual de criação ou edição conforme a referência aprovada

#### Scenario: Abertura de Gestão de Assuntos
- **WHEN** o administrador abre ADM-CON-002
- **THEN** a tela apresenta cabeçalho, navegação administrativa, título, ação `Novo assunto`, filtros, tabela e área contextual de criação, edição ou transferência conforme a referência aprovada

#### Scenario: Elemento fora do escopo
- **WHEN** a moldura visual exibe item de navegação pertencente a módulo não implementado
- **THEN** o item não executa funcionalidade fictícia nem inicia implementação do módulo externo

### Requirement: Gestão utilizável de Matérias
ADM-CON-001 SHALL permitir buscar, filtrar, paginar, criar, visualizar, editar, ativar, inativar, arquivar, reativar e excluir Matérias conforme as regras do catálogo.

#### Scenario: Criação de Matéria
- **WHEN** o administrador aciona `Nova matéria`, informa nome, Área, descrição e status válidos e salva
- **THEN** a Matéria é criada, a tabela é atualizada no contexto atual e uma confirmação de sucesso é exibida

#### Scenario: Filtros de Matérias
- **WHEN** busca e status são alterados
- **THEN** a tabela apresenta os resultados correspondentes e `Limpar filtros` restaura o estado inicial

#### Scenario: Exclusão bloqueada de Matéria
- **WHEN** o administrador tenta excluir uma Matéria com Assuntos
- **THEN** a tela mostra a quantidade de Assuntos e Questões afetadas, não remove dados e oferece orientação para tratar os vínculos

#### Scenario: Arquivamento bloqueado por Assuntos disponíveis
- **WHEN** o arquivamento de uma Matéria não satisfaz as regras de dependência
- **THEN** a tela preserva o contexto e explica quais vínculos devem ser tratados

### Requirement: Gestão utilizável de Assuntos
ADM-CON-002 SHALL permitir buscar, filtrar, paginar, criar, editar, ativar, inativar, arquivar, reativar, excluir e transferir Assuntos conforme as regras do catálogo.

#### Scenario: Filtros dependentes
- **WHEN** o administrador escolhe uma Área
- **THEN** o filtro de Matéria oferece somente Matérias compatíveis e a listagem combina busca, Área, Matéria e status

#### Scenario: Nome duplicado
- **WHEN** criação, edição, reativação ou transferência encontra nome equivalente na Matéria
- **THEN** a tela exibe o erro junto ao campo relevante, mantém os valores informados e permite correção

#### Scenario: Transferência com impacto
- **WHEN** o administrador escolhe outra Matéria para um Assunto
- **THEN** a tela exibe origem, destino e quantidade de Questões impactadas antes de habilitar a confirmação explícita

#### Scenario: Exclusão bloqueada de Assunto
- **WHEN** o administrador tenta excluir um Assunto com Questões
- **THEN** a tela informa o bloqueio e mantém o Assunto e a lista inalterados

#### Scenario: Resumos fora do escopo funcional
- **WHEN** ADM-CON-002 exibe a coluna de Resumos prevista no Desktop V1
- **THEN** a tela usa marcador textual de indisponibilidade em vez de inventar uma contagem enquanto o módulo de Resumos não existir

### Requirement: Estados de carregamento, vazio, erro e sucesso
As duas telas SHALL tratar operações por bloco e SHALL preservar dados válidos e contexto diante de falhas.

#### Scenario: Carregamento de tabela
- **WHEN** uma consulta está em andamento
- **THEN** somente o bloco dependente apresenta estado de carregamento e a navegação permanece disponível

#### Scenario: Catálogo vazio
- **WHEN** não existe item cadastrado
- **THEN** a tela apresenta estado vazio com chamada para a ação de criação correspondente

#### Scenario: Filtros sem resultado
- **WHEN** existem itens mas nenhum corresponde aos filtros
- **THEN** a tela diferencia esse estado do catálogo vazio e oferece limpar os filtros

#### Scenario: Falha ao salvar
- **WHEN** uma criação ou edição falha
- **THEN** os campos permanecem preenchidos, o erro aparece próximo ao contexto afetado e a ação pode ser repetida

#### Scenario: Operação concluída
- **WHEN** uma mutação é confirmada pelo backend
- **THEN** a tela anuncia sucesso sem obstruir o conteúdo, mantém filtros aplicados e atualiza somente os dados necessários

### Requirement: Proteção de alterações não salvas
As telas SHALL detectar mudanças locais ainda não persistidas e SHALL solicitar confirmação antes de descartá-las por cancelar, trocar de item, navegar, sair da conta ou fechar a página. Expiração de sessão, CSRF inválido ou necessidade de reautenticação SHALL bloquear mutações sem apagar campos e contexto. A recuperação da identidade SHALL ocorrer em diálogo no contexto; operação pendente SHALL exigir nova confirmação explícita, sem repetição automática. Se a conta recuperada for diferente, mutações SHALL continuar bloqueadas até descarte e recarga, permitindo copiar os dados locais antes de sair.

#### Scenario: Saída com formulário alterado
- **GIVEN** um formulário modificado após o último salvamento
- **WHEN** o administrador tenta sair ou iniciar outra edição
- **THEN** a tela oferece continuar editando ou descartar mediante confirmação

#### Scenario: Saída sem alterações
- **GIVEN** formulário sem mudanças locais
- **WHEN** há navegação ou cancelamento
- **THEN** a operação ocorre sem confirmação desnecessária

#### Scenario: Logout com formulário alterado
- **GIVEN** formulário ainda não salvo
- **WHEN** o administrador aciona Sair
- **THEN** a tela oferece continuar editando ou descartar; cancelar preserva sessão/dados e confirmar só navega após logout bem-sucedido

#### Scenario: Sessão expira durante edição
- **GIVEN** formulário preenchido e sessão expirada
- **WHEN** uma operação protegida recebe 401 `sessao_invalida`
- **THEN** a tela mantém campos/filtros, bloqueia mutações e permite novo login no contexto, sem guardar senha em storage

#### Scenario: Reautenticação sensível e nova confirmação
- **GIVEN** operação sensível bloqueada por janela de autenticação vencida
- **WHEN** o Administrador confirma sua senha no diálogo
- **THEN** mantém contexto e pode confirmar novamente a ação; nenhuma mutação é repetida automaticamente

#### Scenario: Outra conta após recuperar login
- **GIVEN** formulário local do Administrador anterior
- **WHEN** o diálogo autentica conta diferente
- **THEN** mutações permanecem bloqueadas, dados continuam disponíveis para copiar/descartar e a gestão exige recarga

#### Scenario: Falha de senha ou conexão
- **GIVEN** diálogo de recuperação/reautenticação aberto
- **WHEN** senha está incorreta ou serviço falha
- **THEN** o erro aparece no diálogo e campos/contexto originais são preservados

### Requirement: Acessibilidade operacional
ADM-CON-001 e ADM-CON-002 SHALL possuir foco visível, navegação por teclado, labels persistentes, mensagens associadas aos campos, alvos de ação com pelo menos 44 px e estados compreensíveis sem depender apenas de cor.

#### Scenario: Uso por teclado
- **WHEN** a tela é operada sem apontador
- **THEN** filtros, tabela, menus, formulário e confirmações podem ser percorridos e acionados em ordem coerente

#### Scenario: Confirmação crítica
- **WHEN** um modal de exclusão, arquivamento ou transferência é aberto
- **THEN** o foco fica contido, o título e a consequência são anunciados e o foco retorna ao disparador ao fechar

### Requirement: Acesso administrativo autenticado
ADM-CON-001 e ADM-CON-002 SHALL verificar identidade antes de carregar conteúdo e chamar APIs administrativas. Somente Administrador SHALL utilizar a gestão; anônimo SHALL ir ao login e Aluno SHALL receber acesso negado com retorno ao seu início. A moldura SHALL exibir nome real e ação `Sair`, mantendo composição, fluxos e funcionalidades existentes. Indisponibilidade da consulta de sessão SHALL mostrar erro/tentar novamente, sem conceder acesso. Logout SHALL navegar ao login somente após revogação confirmada.

#### Scenario: Administrador abre a gestão
- **GIVEN** sessão válida de Administrador
- **WHEN** abre Matérias ou Assuntos
- **THEN** vê seu nome, ação de saída e a gestão funcional integrada às APIs protegidas

#### Scenario: Acesso direto sem perfil
- **GIVEN** visitante anônimo ou sessão de Aluno
- **WHEN** abre Matérias ou Assuntos diretamente
- **THEN** não são disparadas consultas administrativas; anônimo vai ao login e Aluno vê acesso negado

#### Scenario: Serviço indisponível durante a verificação
- **GIVEN** a gestão ainda não foi carregada
- **WHEN** a consulta da sessão falha por rede
- **THEN** a página informa falha e permite tentar novamente sem renderizar gestão como autorizada

#### Scenario: Saída confirmada
- **GIVEN** Administrador sem alterações locais
- **WHEN** aciona Sair e a API confirma logout
- **THEN** retorna ao login e o cookie anterior deixa de autorizar gestão
