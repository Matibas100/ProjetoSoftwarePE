# Catálogo acadêmico — acesso autenticado

## MODIFIED Requirements

### Requirement: Compatibilidade dos consumidores existentes
O sistema SHALL preservar as rotas de leitura existentes e os campos legados de Matéria e Assunto para consumidores autenticados. As leituras simples SHALL aceitar Aluno ou Administrador; consultas com `status=todos` e consultas administrativas SHALL exigir Administrador. Anônimo SHALL receber 401 e perfil insuficiente SHALL receber 403, sem retornar dados protegidos. Seletores destinados a novos vínculos SHALL obter apenas itens ativos, enquanto consultas administrativas SHALL poder incluir todos os estados. A introdução de autenticação SHALL NOT alterar payloads, ordenação, filtros, regras de negócio ou respostas de sucesso para o perfil autorizado.

#### Scenario: Leitura legada
- **GIVEN** consumidor existente autenticado com perfil autorizado
- **WHEN** consulta `/api/materias` ou `/api/assuntos`
- **THEN** os campos legados permanecem presentes e novos campos são aditivos

#### Scenario: Seletor de novo vínculo
- **GIVEN** formulário de usuário autenticado autorizado
- **WHEN** solicita opções para criar uma Questão ou um Assunto
- **THEN** itens inativos e arquivados não são oferecidos

#### Scenario: Leitura sem autenticação
- **GIVEN** consumidor sem sessão válida
- **WHEN** consulta Matérias ou Assuntos
- **THEN** recebe 401 e nenhum conteúdo do catálogo protegido é retornado

#### Scenario: Aluno tenta consultar todos os estados
- **GIVEN** sessão válida de Aluno
- **WHEN** consulta Matérias ou Assuntos com `status=todos` ou usa uma rota administrativa
- **THEN** recebe 403 sem dados administrativos

#### Scenario: Administrador consulta itens indisponíveis
- **GIVEN** sessão válida de Administrador
- **WHEN** consulta todos os estados ou a listagem administrativa
- **THEN** os contratos existentes continuam incluindo itens inativos e arquivados conforme os filtros
