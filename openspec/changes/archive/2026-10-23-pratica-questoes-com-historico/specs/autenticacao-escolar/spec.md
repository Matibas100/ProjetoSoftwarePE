# Delta — Autorização do ambiente Aluno

## MODIFIED Requirements

### Requirement: Autorização por perfil e recurso
O sistema SHALL autorizar operações no servidor, independentemente da tela. GET health SHALL continuar público. Leituras simples de Áreas, Matérias e Assuntos SHALL aceitar Aluno e Administrador; `status=todos`, consultas administrativas, prévias de impacto, todas as mutações do catálogo e consulta legada de Questões SHALL exigir Administrador. Rotas existentes sob `/api/aluno/` SHALL exigir perfil Aluno e SHALL limitar coleções e recursos pessoais ao usuário da sessão; Administrador SHALL receber 403 nessas rotas. Recurso pessoal inexistente ou de outro Aluno SHALL retornar o mesmo 404 sem exposição de conteúdo. Anônimo SHALL receber 401; perfil insuficiente SHALL receber 403 `acesso_negado`. HEAD SHALL herdar a política de GET; rotas/métodos inexistentes SHALL preservar 404/405. Gabarito da consulta legada SHALL NOT ser fornecido ao Aluno. Mutações permitidas ao Aluno SHALL manter os controles existentes de sessão, origem e CSRF.

#### Scenario: Aluno lê catálogo ativo
- **GIVEN** sessão de Aluno válida
- **WHEN** consulta Áreas, Matérias ou Assuntos sem `status=todos`
- **THEN** recebe as respostas existentes do catálogo disponível

#### Scenario: Aluno tenta gestão ou gabarito
- **GIVEN** sessão de Aluno válida
- **WHEN** consulta listagem administrativa, impacto, `status=todos`, Questões legadas ou tenta mutação administrativa do catálogo
- **THEN** recebe 403, sem gabarito nem alteração de dados

#### Scenario: Requisição anônima
- **GIVEN** cliente sem identidade autenticada
- **WHEN** chama qualquer rota existente protegida
- **THEN** recebe 401 antes das validações e efeitos do negócio

#### Scenario: Métodos auxiliares e inválidos
- **GIVEN** cliente anônimo
- **WHEN** usa HEAD em leitura protegida ou solicita rota/método não existente
- **THEN** HEAD aplica autenticação e rota/método inexistente mantém 404/405

#### Scenario: Ação própria de Aluno
- **GIVEN** sessão válida de Aluno e origem/CSRF válidos
- **WHEN** usa rota existente de `/api/aluno/` sobre seu próprio recurso
- **THEN** a regra da ação é avaliada para a identidade da sessão sem exigir perfil Administrador

#### Scenario: Recurso de outra conta ou perfil administrativo
- **GIVEN** Aluno consultando recurso alheio ou Administrador usando rota de Aluno
- **WHEN** solicita a operação
- **THEN** recebe respectivamente 404 ou 403 sem leitura/escrita de dados do estudante
