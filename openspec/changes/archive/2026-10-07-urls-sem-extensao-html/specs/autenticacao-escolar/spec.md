# Delta de autenticação escolar

## ADDED Requirements

### Requirement: URLs canônicas das páginas públicas de autenticação
O servidor local do frontend SHALL responder a GET `/login` e GET `/cadastro` com 200 e conteúdo HTML das respectivas telas, mantendo essas URLs no navegador e permitindo entrada direta e recarga. HEAD SHALL apresentar o mesmo status e cabeçalhos de GET, sem corpo. GET e HEAD de `/login.html` e `/login/` SHALL retornar 302 com `Location: /login`; `/cadastro.html` e `/cadastro/` SHALL retornar 302 com `Location: /cadastro`. Havendo query string, ela SHALL ser preservada no Location, sem ser interpretada como destino de navegação. Os redirecionamentos SHALL usar somente caminhos locais fixos e SHALL NOT criar ciclos ou aceitar destino externo. CSS, JavaScript, imagens, fontes, `/`, `/index.html`, `/aluno/inicio.html`, `/admin/materias.html` e `/admin/assuntos.html` SHALL continuar acessíveis com seus comportamentos existentes. Caminhos inexistentes SHALL retornar 404, sem fallback para login ou cadastro. O servidor do frontend SHALL NOT executar ou encaminhar operações `/api` nem disponibilizar arquivos fora do diretório público do frontend.

#### Scenario: Entrada direta e recarga
- **GIVEN** servidor local do frontend em execução
- **WHEN** pessoa abre `/login` ou `/cadastro` e recarrega a página
- **THEN** cada GET retorna 200 com a tela correspondente e a URL permanece sem `.html`

#### Scenario: Endereços antigos continuam utilizáveis
- **GIVEN** link para `/login.html` ou `/cadastro.html`
- **WHEN** cliente solicita o endereço com GET ou HEAD
- **THEN** recebe 302 para `/login` ou `/cadastro`, respectivamente, e o destino responde 200 sem ciclo de redirecionamento

#### Scenario: Barra final e parâmetros
- **GIVEN** endereço `/cadastro/?origem=local` ou `/login.html?origem=local`
- **WHEN** cliente faz GET
- **THEN** recebe 302 para `/cadastro?origem=local` ou `/login?origem=local`, respectivamente, e os recursos da página continuam carregando após o redirecionamento

#### Scenario: Destino externo não controla o redirecionamento
- **GIVEN** endereço antigo contendo `?next=https://example.com`
- **WHEN** cliente solicita esse endereço
- **THEN** Location aponta à URL canônica local com a mesma query string e não encaminha o navegador a `example.com`

#### Scenario: Consulta sem corpo
- **GIVEN** servidor local do frontend em execução
- **WHEN** cliente usa HEAD nas URLs canônicas e nos aliases
- **THEN** recebe o status e os cabeçalhos correspondentes a GET, inclusive Location nos aliases, sem corpo de resposta

#### Scenario: Recursos e páginas existentes
- **GIVEN** login ou cadastro aberto pela URL canônica
- **WHEN** navegador carrega estilos, scripts, logo e fontes, ou solicita as páginas existentes de Aluno, administração e MVP
- **THEN** os arquivos continuam acessíveis e as verificações de sessão/perfil existentes permanecem responsáveis pela navegação protegida

#### Scenario: Caminho inexistente e API no servidor de páginas
- **GIVEN** servidor do frontend separado da API
- **WHEN** cliente solicita `/pagina-inexistente`, `/login/inexistente` ou `/api/auth/login` no servidor do frontend
- **THEN** recebe 404 sem página de autenticação como fallback nem execução de negócio na API

#### Scenario: Diretório público delimitado
- **GIVEN** servidor do frontend em execução
- **WHEN** cliente solicita um arquivo da raiz do projeto fora de `frontend`, inclusive por caminho com tentativa de subir diretórios
- **THEN** o arquivo externo não é entregue e, não existindo recurso público correspondente, a resposta é 404

## MODIFIED Requirements

### Requirement: Cadastro público exclusivo de Aluno
O sistema SHALL disponibilizar `/cadastro` como URL canônica, mantendo `/cadastro.html` por redirecionamento, e `POST /api/auth/cadastro` para criar Aluno ativo com nome, e-mail, senha e confirmação. Nome SHALL ter 2–100 caracteres após trim; e-mail SHALL ser normalizado por trim/lowercase, ASCII, até 254 caracteres, com exatamente um `@`, partes não vazias, domínio com ponto e sem espaços, controles ou pontos consecutivos. Senha SHALL ter 8–128 caracteres, sem transformação, e confirmação idêntica. Campos extras SHALL ser recusados com 400. O e-mail normalizado SHALL ser único, inclusive sob concorrência. Sucesso SHALL retornar 201 com `{usuario: {id, nome, email, perfil}}`, sem autenticar automaticamente; validação SHALL retornar 400 e duplicidade SHALL retornar 409.

#### Scenario: Cadastro válido
- **GIVEN** pessoa não autenticada com origem e CSRF válidos
- **WHEN** envia os quatro campos válidos para e-mail ainda não registrado
- **THEN** uma única conta Aluno é persistida, recebe 201, a tela confirma o cadastro e encaminha a `/login` sem transmitir a senha

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
- **THEN** existe no máximo uma conta para o e-mail normalizado e a requisição conflitante recebe 409 previsível

#### Scenario: Cadastro estando autenticado
- **GIVEN** sessão de conta autenticada válida
- **WHEN** chama a API de cadastro com os controles de origem/CSRF válidos
- **THEN** recebe 409 `ja_autenticado`, sem criar ou substituir a conta da sessão

### Requirement: Login por credenciais com rotação de sessão
O sistema SHALL oferecer `/login` como URL canônica, mantendo `/login.html` por redirecionamento, e `POST /api/auth/login` com `{email, senha}`. Credenciais válidas SHALL retornar 200 com usuário público, `csrf_token` e `destino`, revogando a sessão anterior e estabelecendo nova sessão. E-mail desconhecido, senha incorreta ou conta inativa SHALL produzir 401 `credenciais_invalidas` com a mesma mensagem `E-mail ou senha inválidos.`; entrada malformada SHALL produzir 400. Login de usuário já autenticado SHALL retornar 409 `ja_autenticado`. Senhas SHALL ser persistidas somente por hash adequado e SHALL NOT aparecer em URL, storage ou logs.

#### Scenario: Login de Aluno ou Administrador
- **GIVEN** conta ativa e controles de origem/CSRF válidos
- **WHEN** usuário informa credenciais corretas
- **THEN** recebe novo cookie HttpOnly com identificador opaco, perfil correto e destino fixo do perfil; o identificador anterior deixa de autorizar requisições

#### Scenario: Credenciais recusadas sem identificação da causa
- **GIVEN** e-mail desconhecido, senha incorreta ou conta inativa
- **WHEN** solicita login dentro do limite de tentativas
- **THEN** recebe a mesma resposta neutra 401 e nenhuma sessão autenticada é criada

#### Scenario: Persistência e saída sem segredos
- **GIVEN** cadastro, comando local e login executados
- **WHEN** são inspecionados dados persistidos, respostas e logs
- **THEN** não existe senha em claro nem identificador opaco da sessão persistido em claro; usuário público não contém hash, sessão ou campos internos

### Requirement: Navegação autenticada e telas utilizáveis
Login e cadastro SHALL usar identidade visual e estados de PUB-AUT-001/002 com acessibilidade por teclado, labels, foco visível, loading, erro e sucesso. Os links entre essas telas SHALL usar `/login` e `/cadastro`; após cadastro concluído, logout confirmado ou identificação de sessão inválida no bootstrap de página protegida, o frontend SHALL encaminhar a `/login`. Aluno SHALL entrar em `/aluno/inicio.html` com nome real e saída; Administrador SHALL entrar em `/admin/materias.html`. Destinos SHALL ser fixos e SHALL NOT aceitar redirect externo. Início de Aluno SHALL NOT exibir métricas fictícias ou gestão. `/index.html` e telas administrativas SHALL verificar sessão antes de carregar gestão. Sessão válida nas telas de login/cadastro SHALL encaminhar ao destino do perfil. Saída SHALL navegar somente depois de logout confirmado; falha de rede SHALL mostrar erro sem fingir sucesso. Recuperação/onboarding não implementados SHALL NOT aparecer como links ativos.

#### Scenario: Fluxo escolar de Aluno
- **GIVEN** pessoa com cadastro recém-concluído
- **WHEN** faz login e depois aciona Sair
- **THEN** vê seu nome no início, encerra a sessão e retorna a `/login`; recarregar a área protegida exige nova autenticação

#### Scenario: Entrada direta em gestão
- **GIVEN** anônimo ou Aluno abrindo `/index.html`, Matérias ou Assuntos
- **WHEN** a página resolve sua identidade
- **THEN** anônimo vai a `/login` e Aluno vê acesso negado com retorno ao seu início, sem chamadas administrativas

#### Scenario: Formulário com erro ou duplo clique
- **GIVEN** login/cadastro em andamento ou falha de validação/rede
- **WHEN** pessoa tenta enviar novamente ou corrige o formulário
- **THEN** envio em andamento não duplica operação e erro mantém nome/e-mail e permite nova tentativa

#### Scenario: Acesso por teclado e tamanhos de tela
- **GIVEN** login/cadastro em navegador real
- **WHEN** operados por teclado a 1440 px e visualizados a 390 px
- **THEN** apresentam foco e erros compreensíveis, composição oficial no desktop e nenhuma rolagem horizontal causada pelo formulário

#### Scenario: Alternância entre formulários
- **GIVEN** pessoa não autenticada em `/login` ou `/cadastro`
- **WHEN** aciona Criar uma conta ou Entrar
- **THEN** navega a `/cadastro` ou `/login`, respectivamente, sem `.html`

#### Scenario: Sessão válida nas páginas públicas
- **GIVEN** Aluno ou Administrador com sessão válida
- **WHEN** abre `/login` ou `/cadastro`
- **THEN** segue para `/aluno/inicio.html` ou `/admin/materias.html`, respectivamente, preservando os destinos dos perfis
