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
As telas SHALL detectar mudanças locais ainda não persistidas e SHALL solicitar confirmação antes de descartá-las por cancelar, trocar de item, navegar ou fechar a página.

#### Scenario: Saída com formulário alterado
- **GIVEN** um formulário modificado após o último salvamento
- **WHEN** o administrador tenta sair ou iniciar outra edição
- **THEN** a tela oferece continuar editando ou descartar mediante confirmação

#### Scenario: Saída sem alterações
- **WHEN** não há mudanças locais
- **THEN** a navegação ou o cancelamento ocorre sem confirmação desnecessária

### Requirement: Acessibilidade operacional
ADM-CON-001 e ADM-CON-002 SHALL possuir foco visível, navegação por teclado, labels persistentes, mensagens associadas aos campos, alvos de ação com pelo menos 44 px e estados compreensíveis sem depender apenas de cor.

#### Scenario: Uso por teclado
- **WHEN** a tela é operada sem apontador
- **THEN** filtros, tabela, menus, formulário e confirmações podem ser percorridos e acionados em ordem coerente

#### Scenario: Confirmação crítica
- **WHEN** um modal de exclusão, arquivamento ou transferência é aberto
- **THEN** o foco fica contido, o título e a consequência são anunciados e o foco retorna ao disparador ao fechar
