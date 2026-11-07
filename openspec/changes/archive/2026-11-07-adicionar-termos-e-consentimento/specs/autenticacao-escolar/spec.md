# Autenticação escolar — aceite de uso

## MODIFIED Requirements

### Requirement: Cadastro público exclusivo de Aluno
O sistema SHALL disponibilizar `/cadastro` como URL canônica, mantendo `/cadastro.html` por redirecionamento, e `POST /api/auth/cadastro` para criar Aluno ativo com nome, e-mail, senha, confirmação e `termos_uso:{versao,aceito:true}`. O aceite SHALL ser explícito, inicialmente desmarcado, referir-se ao Termo de Uso vigente e ser persistido atomicamente com a conta, sem autorizar o plano. Nome SHALL ter 2–100 caracteres após trim; e-mail SHALL ser normalizado por trim/lowercase, ASCII, até 254 caracteres, com exatamente um `@`, partes não vazias, domínio com ponto e sem espaços, controles ou pontos consecutivos. Senha SHALL ter 8–128 caracteres, sem transformação, e confirmação idêntica. Campos extras SHALL ser recusados com 400. O e-mail normalizado SHALL ser único, inclusive sob concorrência. Sucesso SHALL retornar 201 com `{usuario: {id, nome, email, perfil}}`, sem autenticar automaticamente; validação SHALL retornar 400, versão de uso desatualizada SHALL retornar 409 `termo_desatualizado` e duplicidade SHALL retornar 409.

#### Scenario: Cadastro válido
- **GIVEN** pessoa não autenticada com origem e CSRF válidos
- **WHEN** envia os quatro campos de identificação/credenciais válidos e o aceite explícito da versão vigente para e-mail ainda não registrado
- **THEN** uma única conta Aluno e sua evidência de aceite de uso são persistidas na mesma transação, recebe 201, a tela confirma o cadastro e encaminha a `/login` sem transmitir a senha; consentimento do plano continua ausente

#### Scenario: Tentativa de escolher Administrador
- **GIVEN** pessoa no cadastro público
- **WHEN** inclui `perfil: administrador` ou outro campo não permitido
- **THEN** recebe 400 e nenhuma conta é criada ou promovida

#### Scenario: Confirmação ou campos inválidos
- **GIVEN** pessoa no cadastro
- **WHEN** envia senha divergente da confirmação, nome curto, e-mail inválido ou senha fora dos limites
- **THEN** recebe 400, nenhum dado parcial é persistido e a tela preserva nome/e-mail com erro associado ao campo

#### Scenario: Duplicidade normalizada e concorrente
- **GIVEN** e-mail existente ou duas requisições concorrentes que diferem apenas por caixa/espaços externos
- **WHEN** o cadastro é executado
- **THEN** existe no máximo uma conta para o e-mail normalizado e a requisição conflitante recebe 409 previsível, sem deixar aceite órfão

#### Scenario: Cadastro estando autenticado
- **GIVEN** sessão de conta autenticada válida
- **WHEN** chama a API de cadastro com os controles de origem/CSRF válidos
- **THEN** recebe 409 `ja_autenticado`, sem criar ou substituir a conta da sessão

#### Scenario: Aceite ausente ou inválido
- **GIVEN** campos pessoais e credenciais válidos
- **WHEN** envia o corpo antigo sem `termos_uso`, objeto incompleto, campo extra, `aceito:false` ou valor diferente do booleano true
- **THEN** recebe 400 e nem conta nem aceite são persistidos

#### Scenario: Texto mudou durante o preenchimento
- **GIVEN** cadastro preenchido e versão apresentada que deixou de ser vigente
- **WHEN** solicita cadastro com aquela versão
- **THEN** recebe 409 `termo_desatualizado`, a tela obtém os metadados atuais, desmarca o aceite e exige nova confirmação sem reenviar cadastro automaticamente

#### Scenario: Falha ao gravar a evidência
- **GIVEN** cadastro válido com aceite vigente
- **WHEN** a persistência do aceite ou o commit falha
- **THEN** criação de usuário e aceite são revertidas juntas, não há sessão autenticada e não se anuncia sucesso

### Requirement: Autorização por perfil e recurso
O sistema SHALL autorizar operações no servidor, independentemente da tela. GET health e GET `/api/termos` SHALL continuar públicos. Leituras simples de Áreas, Matérias e Assuntos SHALL aceitar Aluno e Administrador; `status=todos`, consultas administrativas, prévias de impacto, todas as mutações do catálogo e consulta legada de Questões SHALL exigir Administrador. Rotas existentes sob `/api/aluno/` SHALL exigir perfil Aluno e SHALL limitar coleções e recursos pessoais ao usuário da sessão; Administrador SHALL receber 403 nessas rotas. Recurso pessoal inexistente ou de outro Aluno SHALL retornar o mesmo 404 sem exposição de conteúdo. Anônimo SHALL receber 401; perfil insuficiente SHALL receber 403 `acesso_negado`. HEAD SHALL herdar a política de GET; rotas/métodos inexistentes SHALL preservar 404/405. Gabarito da consulta legada SHALL NOT ser fornecido ao Aluno. Mutações permitidas ao Aluno SHALL manter os controles existentes de sessão, origem e CSRF. Políticas específicas do plano SHALL ser verificadas antes de consultar seu recurso; ausência de consentimento SHALL produzir 403 uniforme sem expor existência do item. Consulta de privacidade SHALL permitir ao próprio Aluno decidir mesmo sem aceite prévio, sem abrir gestão administrativa.

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
- **GIVEN** sessão válida de Aluno, origem/CSRF válidos e permissões específicas do caso atendidas
- **WHEN** usa rota existente de `/api/aluno/` sobre seu próprio recurso
- **THEN** a regra da ação é avaliada para a identidade da sessão sem exigir perfil Administrador

#### Scenario: Recurso de outra conta ou perfil administrativo
- **GIVEN** Aluno autorizado para o caso consultando recurso alheio ou Administrador usando rota de Aluno
- **WHEN** solicita a operação
- **THEN** recebe respectivamente 404 ou 403 sem leitura/escrita de dados do estudante

#### Scenario: Metadados de termos sem autenticação
- **GIVEN** cliente sem sessão
- **WHEN** consulta GET ou HEAD `/api/termos`
- **THEN** recebe 200 sem obter acesso a decisões individuais; POST nessa rota permanece 405 e caminho inexistente permanece 404

#### Scenario: Privacidade da conta ainda sem aceites
- **GIVEN** Aluno autenticado sem registro de privacidade
- **WHEN** consulta `/api/aluno/privacidade`
- **THEN** recebe apenas seu estado pendente e pode registrar uma escolha com origem/CSRF, sem bypass de sessão ou acesso a outra conta
