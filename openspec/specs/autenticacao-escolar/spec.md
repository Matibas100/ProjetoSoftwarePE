# autenticacao-escolar Specification

## Purpose

Permitir que Alunos criem contas e acessem seu ambiente e que Administradores usem a gestão existente com identidade, sessão revogável e autorização real no servidor, dentro do escopo da entrega escolar.

## Requirements

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

### Requirement: Provisionamento local de Administrador
O sistema SHALL oferecer o comando local `python -m flask --app backend/run.py criar-administrador`, solicitando nome/e-mail e senha confirmada sem eco. O comando SHALL aplicar as mesmas validações e unicidade do cadastro, atribuir somente `administrador` e recusar e-mail existente sem alterar perfil ou senha. Migrations SHALL NOT criar contas ou senhas padrão.

#### Scenario: Primeira conta administrativa
- **GIVEN** schema atualizado e e-mail ainda não utilizado
- **WHEN** operador executa o comando e fornece dados válidos
- **THEN** uma conta Administrador é criada e pode fazer login pela mesma tela, sem senha/hash no output

#### Scenario: E-mail já pertence a Aluno
- **GIVEN** conta Aluno com o e-mail informado
- **WHEN** operador tenta criar Administrador com esse e-mail
- **THEN** o comando termina com erro de conflito e preserva a conta original

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

### Requirement: Ciclo de vida da sessão no servidor
O sistema SHALL manter sessões no servidor, consultar a identidade em `GET /api/auth/sessao` e revogar a atual em `POST /api/auth/logout`. A sessão autenticada SHALL expirar em 8 horas absolutas ou 30 minutos de inatividade, considerando o limite atingido como expirado; sessão anônima de CSRF SHALL durar 10 minutos e nunca conceder acesso. Sessões revogadas, expiradas, inexistentes ou de conta inativa SHALL gerar 401 `sessao_invalida` nas rotas protegidas. Cookie SHALL ser HttpOnly, SameSite=Lax, Path=/api, sem Domain e Secure em produção. Logout SHALL retornar 204 e remover o cookie; sem sessão válida SHALL ser idempotente. Sessões múltiplas SHALL ser independentes e SHALL poder ser revogadas individualmente ou por usuário no servidor.

#### Scenario: Consulta de identidade
- **GIVEN** sessão válida de conta ativa
- **WHEN** consulta `/api/auth/sessao`
- **THEN** recebe 200 com usuário público, CSRF e destino, sem expor identificador de sessão no JSON

#### Scenario: Expiração nos dois limites
- **GIVEN** sessão cuja duração absoluta alcançou 8 horas ou último acesso autorizado ocorreu há 30 minutos
- **WHEN** faz uma requisição protegida
- **THEN** recebe 401, cookie inválido é removido e nenhum caso de uso protegido é executado

#### Scenario: Logout em uma de duas sessões
- **GIVEN** usuário com duas sessões válidas em clientes distintos
- **WHEN** encerra uma delas com controles válidos
- **THEN** recebe 204, aquela sessão deixa de acessar a API e a outra permanece válida

#### Scenario: Sessão revogada não pode reaparecer
- **GIVEN** revogação concorrente com atualização de último acesso
- **WHEN** uma nova consulta é realizada após a revogação
- **THEN** a sessão continua revogada e retorna 401

#### Scenario: Revogação global
- **GIVEN** várias sessões de um usuário
- **WHEN** a operação de revogação por usuário é executada no servidor
- **THEN** todas deixam de autorizar acesso, sem afetar sessões de outro usuário

### Requirement: Proteção de origem e CSRF
O sistema SHALL oferecer `GET /api/auth/csrf` que devolve token vinculado à sessão válida ou cria sessão anônima. Cadastro, login e mutações autenticadas SHALL exigir `X-CSRF-Token` correto e `Origin` exatamente autorizado; origem ausente, `null` ou não permitida SHALL retornar 403 `origem_nao_permitida`, e CSRF ausente/incorreto SHALL retornar 403 `csrf_invalido`, sem executar negócio. Logout sem sessão válida SHALL exigir origem e dispensar CSRF. CORS SHALL permitir credenciais apenas para origens explícitas e SHALL NOT aceitar wildcard. O frontend SHALL enviar cookies por `credentials: include`, mantendo CSRF somente em memória. Respostas de autenticação SHALL usar `Cache-Control: no-store`.

#### Scenario: Bootstrap e mutação válida
- **GIVEN** navegador em origem permitida sem sessão
- **WHEN** obtém CSRF e envia cadastro/login com cookie e cabeçalho correspondentes
- **THEN** a operação é aceita pelos controles de segurança, sem que a sessão anônima conceda acesso administrativo

#### Scenario: CSRF de outra sessão
- **GIVEN** sessão válida
- **WHEN** envia mutação com CSRF de outro cliente ou anterior à rotação de login
- **THEN** recebe 403 e nenhum dado funcional é alterado

#### Scenario: Origem não autorizada
- **GIVEN** cookie e CSRF aparentemente válidos
- **WHEN** a mutação vem de origem não permitida, ausente ou `null`
- **THEN** recebe 403 e nenhum caso de uso é executado

#### Scenario: Preflight
- **GIVEN** origem explicitamente autorizada
- **WHEN** o navegador envia OPTIONS antes da requisição
- **THEN** recebe política CORS adequada a cookies/CSRF, sem exigir login e sem alterar dados funcionais

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

### Requirement: Reautenticação de ações sensíveis
O sistema SHALL exigir autenticação de senha nos últimos 15 minutos para excluir, inativar, arquivar, reativar ou transferir catálogo e para PUT Matéria contendo `status`/`area_enem_id` ou PUT Assunto contendo `materia_id`. Janela vencida SHALL retornar 403 `reautenticacao_necessaria`, sem mudança parcial. `POST /api/auth/reautenticar` SHALL confirmar a senha do usuário atual e renovar a janela; senha incorreta SHALL retornar 401 `credenciais_invalidas` preservando a sessão, e sessão inválida SHALL retornar 401 `sessao_invalida`. A tela SHALL preservar contexto e exigir nova confirmação da ação, sem repetir mutação automaticamente.

#### Scenario: Ação sensível com janela vencida
- **GIVEN** Administrador autenticado há mais de 15 minutos
- **WHEN** confirma exclusão, status sensível ou transferência
- **THEN** recebe necessidade de reautenticação, nenhum dado muda e o formulário/contexto permanece disponível

#### Scenario: Recuperar a janela sensível
- **GIVEN** sessão válida e diálogo de reautenticação
- **WHEN** Administrador confirma senha correta e depois confirma novamente a operação
- **THEN** a janela é renovada e a operação segue as regras existentes de confirmação/impacto

#### Scenario: Caminho alternativo por PUT
- **GIVEN** Administrador com janela vencida
- **WHEN** envia PUT de Matéria com status/Área ou PUT de Assunto com Matéria, mesmo repetindo o valor atual
- **THEN** recebe 403 de reautenticação antes de alterar o catálogo

#### Scenario: Senha incorreta no diálogo
- **GIVEN** sessão válida
- **WHEN** senha da reautenticação está incorreta
- **THEN** permanece autenticado, recebe erro no diálogo e seus campos continuam preservados

### Requirement: Limite básico de tentativas de senha
O sistema SHALL limitar login a 5 falhas por e-mail normalizado em janela de 15 minutos e reautenticação a 5 falhas por usuário em janela independente. A quinta falha SHALL iniciar bloqueio de 15 minutos e retornar 429 com Retry-After; tentativas durante bloqueio SHALL manter 429 inclusive com senha correta. E-mails desconhecidos/inativos SHALL seguir a mesma regra. Após o bloqueio o contador SHALL reiniciar; sucesso anterior ao bloqueio SHALL zerar falhas. Atualizações concorrentes SHALL NOT perder contagem ou produzir erro interno por colisão da chave.

#### Scenario: Quinta falha e bloqueio
- **GIVEN** quatro falhas na janela para uma identidade
- **WHEN** ocorre outra falha e depois uma tentativa com senha correta
- **THEN** ambas recebem 429 enquanto durar o bloqueio, sem criar sessão

#### Scenario: Retomada e contagem concorrente
- **GIVEN** bloqueio terminado ou tentativas simultâneas para a mesma identidade
- **WHEN** novas tentativas são processadas
- **THEN** bloqueio expirado reinicia a janela e falhas simultâneas são contabilizadas corretamente sem 500

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

### Requirement: Evolução compatível do banco e do MVP
O sistema SHALL adicionar autenticação por migration versionada e snapshot equivalente, preservando dados, identificadores, procedure e regras existentes. Não SHALL modificar migrations aplicadas. Operações de cadastro/login SHALL ser atômicas e falhas SHALL NOT deixar conta parcial ou sessão autenticada parcial. Instalação nova, upgrade de 004, baseline do snapshot completo e idempotência SHALL ser verificáveis no MySQL real. Os 29 cenários originais e a suíte ampliada SHALL continuar validando comportamento com autenticação real, sem bypass de produção.

#### Scenario: Upgrade sem perda
- **GIVEN** banco válido em 004 com Matérias, Assuntos e Questões
- **WHEN** a migration de autenticação é aplicada e executada novamente pelo runner
- **THEN** conteúdo e procedure permanecem preservados, tabelas novas existem e segunda execução não reaplica DDL

#### Scenario: Falha de login composto
- **GIVEN** sessão anônima válida
- **WHEN** a confirmação transacional da nova sessão falha
- **THEN** não existe sessão autenticada parcial e o cliente recebe erro neutro sem segredo

#### Scenario: Snapshot e regressão
- **GIVEN** instalação pelo snapshot ou execução dos testes legados autenticados
- **WHEN** baseline e regressão são realizados em MySQL descartável
- **THEN** snapshot é reconhecido integralmente, os cenários originais mantêm respostas de negócio e políticas não são desligadas

### Requirement: Limpeza operacional restrita da autenticação
O sistema SHALL oferecer comando local `python -m flask --app backend/run.py limpar-autenticacao` que remove somente sessões expiradas/revogadas há mais de 24 horas e limites cuja janela e bloqueio terminaram há mais de 24 horas. O comando SHALL NOT excluir contas, sessões ainda válidas, catálogo ou histórico funcional, nem exibir segredos.

#### Scenario: Limpeza de registros antigos
- **GIVEN** registros antigos, sessões válidas e conteúdo funcional no mesmo banco
- **WHEN** operador executa a limpeza
- **THEN** apenas registros de autenticação elegíveis são removidos e a saída contém contagens sem segredos

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
