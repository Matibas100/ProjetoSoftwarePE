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
As telas SHALL proteger alterações locais não salvas durante descarte, falha de autenticação e recuperação de identidade.

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

#### Scenario: Descarte e bloqueio sem perda de campos
- **GIVEN** formulário com mudanças ainda não persistidas
- **WHEN** ocorre intenção de descarte ou falha de segurança da mutação
- **THEN** As telas SHALL detectar mudanças locais ainda não persistidas e SHALL solicitar confirmação antes de descartá-las por cancelar, trocar de item, navegar, sair da conta ou fechar a página.
- **THEN** Expiração de sessão, CSRF inválido ou necessidade de reautenticação SHALL bloquear mutações sem apagar campos e contexto.

#### Scenario: Recuperação da identidade com contexto local
- **GIVEN** operação pendente e dados locais preservados
- **WHEN** a identidade é recuperada na mesma conta ou em outra
- **THEN** A recuperação da identidade SHALL ocorrer em diálogo no contexto; operação pendente SHALL exigir nova confirmação explícita, sem repetição automática.
- **THEN** Se a conta recuperada for diferente, mutações SHALL continuar bloqueadas até descarte e recarga, permitindo copiar os dados locais antes de sair.

### Requirement: Acessibilidade operacional
ADM-CON-001 e ADM-CON-002 SHALL possuir foco visível, navegação por teclado, labels persistentes, mensagens associadas aos campos, alvos de ação com pelo menos 44 px e estados compreensíveis sem depender apenas de cor.

#### Scenario: Uso por teclado
- **WHEN** a tela é operada sem apontador
- **THEN** filtros, tabela, menus, formulário e confirmações podem ser percorridos e acionados em ordem coerente

#### Scenario: Confirmação crítica
- **WHEN** um modal de exclusão, arquivamento ou transferência é aberto
- **THEN** o foco fica contido, o título e a consequência são anunciados e o foco retorna ao disparador ao fechar

### Requirement: Acesso administrativo autenticado
As telas de catálogo administrativo SHALL verificar a identidade e permitir a gestão somente ao Administrador.

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

#### Scenario: Identidade e moldura da gestão de catálogo
- **GIVEN** cliente abrindo ADM-CON-001 ou ADM-CON-002
- **WHEN** a tela resolve a sessão e prepara a gestão
- **THEN** ADM-CON-001 e ADM-CON-002 SHALL verificar identidade antes de carregar conteúdo e chamar APIs administrativas.
- **THEN** Somente Administrador SHALL utilizar a gestão; anônimo SHALL ir ao login e Aluno SHALL receber acesso negado com retorno ao seu início.
- **THEN** A moldura SHALL exibir nome real e ação `Sair`, mantendo composição, fluxos e funcionalidades existentes.

#### Scenario: Falha de sessão e encerramento administrativo
- **GIVEN** gestão administrativa consultando sessão ou processando logout
- **WHEN** recebe indisponibilidade ou resultado de revogação
- **THEN** Indisponibilidade da consulta de sessão SHALL mostrar erro/tentar novamente, sem conceder acesso.
- **THEN** Logout SHALL navegar ao login somente após revogação confirmada.

### Requirement: Gestão mínima utilizável de Questões
As telas administrativas SHALL oferecer gestão mínima de Questões com autorização, acessibilidade e preservação do contexto.

#### Scenario: Gerir Questão real
- **GIVEN** Administrador e catálogo ativo
- **WHEN** cadastra, edita, revisa/publica ou arquiva uma Questão
- **THEN** a tela chama APIs reais, reflete o estado confirmado e preserva contexto da listagem

#### Scenario: Falha ou saída durante edição
- **GIVEN** formulário alterado e ainda não salvo
- **WHEN** ocorre erro, sessão expirada ou tentativa de navegar/sair
- **THEN** dados são preservados, recuperação não repete escrita e descarte exige confirmação explícita

#### Scenario: Operação acessível e escopo limitado
- **GIVEN** usuário operando por teclado
- **WHEN** percorre filtros, formulário e confirmação de publicação/arquivamento
- **THEN** foco e consequências são compreensíveis e não há importação, IA ou upload funcional fora deste recorte

#### Scenario: Fluxos e referências oficiais da gestão de Questões
- **GIVEN** cliente abrindo listagem ou edição administrativa de Questão
- **WHEN** usa os fluxos implementados de gestão
- **THEN** As telas `/admin/questoes.html` e `/admin/questao.html` SHALL oferecer listagem, filtros, paginação, cadastro, edição de rascunho, revisão/publicação explícita e arquivamento com confirmação, usando referências ADM-QUE-001/002, moldura e ativos oficiais.

#### Scenario: Perfil e recuperação contextual de Questões
- **GIVEN** formulário ou filtros de Questões em uso
- **WHEN** consulta dados ou recupera uma falha de negócio, rede ou identidade
- **THEN** SHALL verificar perfil antes de consultar dados e preservar formulário/filtros em falha de negócio, rede ou sessão.
- **THEN** Recuperação/reautenticação SHALL ocorrer no contexto, sem repetição automática da mutação; troca de conta SHALL bloquear contexto antigo até descarte/recarga.

#### Scenario: Estados e acessibilidade da gestão de Questões
- **GIVEN** pessoa interagindo com a gestão de Questões
- **WHEN** navega ou aciona um recurso da tela
- **THEN** SHALL proteger alterações não salvas, manter labels, foco e teclado e diferenciar carregamento, vazio, filtros sem resultado, erro e sucesso.
- **THEN** Funções fora do recorte SHALL permanecer indisponíveis sem ação fictícia.

### Requirement: Gestão mínima utilizável de Simulados fixos
As telas administrativas SHALL oferecer gestão mínima de Simulados fixos com dados reais e confirmação contextual.

#### Scenario: Publicação de composição real
- **GIVEN** Administrador com rascunho válido
- **WHEN** revisa e confirma publicação pela tela
- **THEN** versão e composição retornadas pelo servidor são refletidas e a edição de publicado fica indisponível

#### Scenario: Falha e proteção da seleção
- **GIVEN** rascunho com Questões selecionadas e ainda não salvo
- **WHEN** falha gravação, expira sessão ou tenta sair
- **THEN** seleção é preservada, descarte exige confirmação e recuperação não repete mutação automaticamente

#### Scenario: Composição manual e referências da gestão de Simulados
- **GIVEN** Administrador usando a gestão de Simulados
- **WHEN** lista ou mantém a composição fixa
- **THEN** As telas administrativas de Simulados SHALL usar referências ADM-SIM-001/002 para listar, cadastrar composição manual ordenada, editar rascunho, revisar/publicar e arquivar, com dados reais e APIs protegidas.

#### Scenario: Preservação e confirmação da gestão de Simulados
- **GIVEN** formulário de Simulado com campos e seleção locais
- **WHEN** ocorre erro, expiração de sessão ou ação de publicação ou arquivamento
- **THEN** SHALL preservar campos, seleção, revisão e filtros diante de erro/sessão expirada, proteger alterações não salvas e exigir confirmação/reautenticação contextual em publicação/arquivamento.

#### Scenario: Estados acessíveis e limites da gestão de Simulados
- **GIVEN** pessoa interagindo com as telas administrativas de Simulados
- **WHEN** navega ou busca os recursos disponíveis
- **THEN** SHALL permitir teclado/foco e mostrar vazio, carregamento, falha e sucesso.
- **THEN** Geradores, importação, calendário, TRI e recursos fora do recorte SHALL permanecer indisponíveis.
