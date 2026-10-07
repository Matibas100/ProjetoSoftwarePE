# Gestão administrativa — identidade e sessão

## ADDED Requirements

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

## MODIFIED Requirements

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
