# Design

## Context

Veja [proposal.md](proposal.md) para motivação e escopo. O código atual tem factory Flask, camadas globais, `TransactionManager`, migrations 000–004 e páginas estáticas servidas separadamente. A consulta legada de Questões devolve `resposta_correta`; ela não pode ser liberada ao Aluno. PUB-AUT-001/002 existem apenas no Desktop V1.

Este design aplica [ADR-001](../../../docs/technical/adr/ADR-001-estrategia-de-migrations.md), [ADR-002](../../../docs/technical/adr/ADR-002-estrategia-de-autenticacao.md) e [ADR-006](../../../docs/technical/adr/ADR-006-fronteira-de-transacoes.md). Os contratos abaixo são propostas desta change, sujeitos à revisão antes do apply; não são descritos como endpoints já existentes.

## Goals / Non-Goals

**Goals:** entregar cadastro, login e saída verificáveis no navegador e MySQL; proteger o catálogo e o MVP legado; introduzir identidade individual que as próximas changes possam usar.

**Non-Goals:** criar pastas de módulos, RBAC configurável, infraestrutura de identidade externa ou abstrações para clientes futuros. Recuperação, verificação de e-mail, onboarding e gestão web de conta são adiados, conforme a proposta.

## Decisions

### 1. Manter as camadas e reutilizar dependências

Fluxo: `Frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL`. Um `AutenticacaoController` adapta HTTP; Services separados coordenam cadastro, login, consulta de sessão, logout, reautenticação e provisionamento local. Um adaptador HTTP de autorização extrai cookie/cabeçalho e chama Services, sem executar SQL ou acessar `db.session`.

Models realizam CRUD. `AutenticacaoRepository` fica restrito a consulta de sessão com usuário, atualização condicionada/locks, revogação e contador concorrente de tentativas; não duplica CRUD. Services usam `TransactionManager` e Models participantes com `confirmar=False` onde a operação é composta. Manter hash de senha com `werkzeug.security` (scrypt, `scrypt:32768:8:1`), `secrets`/`hashlib`/`hmac` da biblioteca padrão; nenhuma nova dependência direta. JWT, sessão cookie-based padrão do Flask e Redis foram descartados por incompatibilidade com o ADR ou esforço desnecessário.

### 2. Identidade e criação de contas

- Perfis fixos: `aluno` e `administrador`, conferidos no servidor a cada requisição. Não criar tabelas de permissões.
- Cadastro: JSON estrito com `nome`, `email`, `senha`, `senha_confirmacao`; campos adicionais, especialmente `perfil`, são rejeitados com 400. A conta resultante sempre é Aluno ativo.
- Nome: string, trim, entre 2 e 100 caracteres. E-mail: string ASCII, trim e lowercase, até 254 caracteres; exatamente um `@`, partes não vazias, domínio com ponto, sem espaços, caracteres de controle ou pontos consecutivos. Esta normalização é única para cadastro, login e comando local; não remover pontos nem sufixos `+`.
- Senha: string de 8 a 128 caracteres, sem trim nem transformação; confirmação deve ser idêntica. Login aceita senha não vazia de até 128 caracteres para autenticar contas existentes. A confirmação existe no formulário e no contrato de cadastro.
- E-mail normalizado possui UNIQUE com collation binária, evitando que acentuação/collation ampla introduza equivalências não previstas. Cadastro duplicado recebe 409; a informação permite recuperar o fluxo por login, sem criar recuperação por e-mail nesta etapa.
- Cadastro bem-sucedido não autentica automaticamente: apresenta confirmação e encaminha ao login, transferindo somente o e-mail por `sessionStorage` e removendo-o ao consumir. Não transmitir senha nem e-mail em query string. Senhas e tokens de sessão nunca entram em storage. O usuário autenticado que tente cadastrar recebe 409, sem trocar sua conta.
- Criar Administrador via `python -m flask --app backend/run.py criar-administrador`, executado da raiz. Nome/e-mail são solicitados interativamente; senha e confirmação usam prompt oculto. E-mail existente gera conflito, sem promover ou sobrescrever conta. O comando chama Service, não SQL, e não imprime senha/hash. Nenhuma senha padrão nem seed de conta na migration.

### 3. Persistência mínima e tempos explícitos

A migration 005 cria somente três tabelas InnoDB, sem alterar tabelas funcionais atuais:

| Tabela | Campos e invariantes propostos |
| --- | --- |
| `usuarios` | `id INT` PK AUTO_INCREMENT; `nome VARCHAR(100)`; `email VARCHAR(254)` normalizado, collation binária e UNIQUE; `senha_hash VARCHAR(255)`; `perfil VARCHAR(20)` com CHECK para os dois valores; `ativo BOOLEAN` padrão true; `criado_em DATETIME(6)` UTC. Tudo NOT NULL. |
| `sessoes` | `id BIGINT` PK AUTO_INCREMENT; `usuario_id INT NULL` FK RESTRICT; `identificador_hash CHAR(64)` ASCII binário UNIQUE; `criada_em`, `ultimo_acesso_em`, `expira_em DATETIME(6)` NOT NULL; `reautenticada_em` e `revogada_em DATETIME(6) NULL`. Índices para usuário e expiração. `usuario_id NULL` representa sessão anônima de CSRF. |
| `auth_limites` | `chave_hash CHAR(64)` ASCII binário PK; `falhas SMALLINT UNSIGNED`; `janela_inicio DATETIME(6)` NOT NULL; `bloqueado_ate DATETIME(6) NULL`. Guarda contagem de falhas de senha sem armazenar e-mail/IP em claro. |

Gerar identificador com 32 bytes aleatórios e guardar apenas SHA-256 no banco. A sessão autenticada expira após 8 horas absolutas ou 30 minutos sem requisição autorizada; usar UTC e limites inclusivos (`agora >= limite` expira). Sessão anônima dura 10 minutos absolutos e não concede identidade. Login revoga a sessão usada anteriormente e cria nova sessão/CSRF atomicamente, evitando fixação. `reautenticada_em` começa no login e é renovada pela reautenticação; várias sessões independentes são permitidas. Logout revoga somente a sessão atual. Implementar revogação individual e por usuário no Repository para cumprir o ADR e reutilização futura; não há tela de outras sessões nesta entrega.

Requisições autorizadas atualizam `ultimo_acesso_em` somente se a sessão ainda não estiver expirada/revogada; nunca reativam uma sessão revogada em concorrência. O adaptador conclui a verificação antes de chamar o caso de uso. Cadastro e login possuem transações curtas; calcular hash/verificar senha fora de locks longos e revalidar estado relevante na transação de confirmação.

### 4. Cookie, origem e CSRF

- Cookie `enem_session`: HttpOnly, SameSite=Lax, Path=/api, sem Domain, Secure em produção; Max-Age limitado à expiração absoluta, 600 s anônimo/28800 s autenticado. Remover com os mesmos atributos. `AUTH_COOKIE_SECURE` padrão false para o desenvolvimento HTTP local; deve ser true no ambiente HTTPS de entrega. Não alterar `.env` existente.
- Usar `AUTH_SECRET_KEY` com 32 bytes aleatórios codificados em 64 caracteres hexadecimais, obrigatória e estável entre processos; falta/formato inválido recusa inicialização com erro sem valor sensível. Decodificar antes de usar HMAC. `.env.example` apenas documenta a variável vazia; geração/configuração local é etapa operacional, não instalação de serviço.
- `GET /api/auth/csrf` reaproveita sessão válida ou cria anônima e devolve `csrf_token`. Derivar o token como HMAC-SHA256 de identificador opaco + propósito CSRF com a chave de ambiente. A validação compara em tempo constante com o cookie recebido e com a sessão válida. A chave não sai do servidor; token CSRF fica apenas na memória do frontend, é diferente do segredo de autenticação e permanece estável entre abas da mesma sessão.
- Cadastro/login e toda mutação com sessão válida exigem `X-CSRF-Token`. Logout sem sessão válida é idempotente, limpa o cookie e devolve 204. Com sessão válida, exige CSRF antes de revogar.
- Toda mutação via API exige `Origin` exatamente presente em `CORS_ORIGINS`; origem ausente, `null` ou não permitida é 403. Clientes HTTP de teste enviam a origem da fixture, sem dispensar a política. Comando local não passa pela API.
- Flask-CORS com credenciais e lista explícita; recusar wildcard, origens com caminho ou mistura de HTTP/HTTPS/host que não respeite a configuração. `OPTIONS` não exige sessão/CSRF e continua sem executar negócio. Métodos/cabeçalhos CORS incluem Content-Type e X-CSRF-Token.
- Frontend usa `credentials: include`. Para desenvolvimento, `http://127.0.0.1:5500` chama `http://127.0.0.1:5000/api`; `http://localhost:5500` chama `http://localhost:5000/api`. Usar configuração via `window.ENEM_API_URL` opcional, com padrão derivado desses hosts; ambiente publicado documenta o valor HTTPS explícito. Origem e API devem usar o mesmo site para SameSite=Lax; configuração entre sites fica fora desta change.
- Todas as respostas de autenticação usam `Cache-Control: no-store`; sessão, senha, CSRF, corpo de login e hashes não são registrados em logs.

### 5. Contratos HTTP novos

Perfil exposto usa os dois valores fixos. Objeto público `usuario`: `{id, nome, email, perfil}`. Erros mantêm `{erro}` e acrescentam `codigo` apenas nos endpoints de autenticação e novas falhas do guard; nunca incluir hash, identificador opaco ou informações internas.

| Método e rota | Entrada | Sucesso | Falhas específicas |
| --- | --- | --- | --- |
| GET `/api/auth/csrf` | Cookie opcional | 200 `{csrf_token}` e cookie anônimo se necessário | 500 neutro se indisponível |
| POST `/api/auth/cadastro` | Os quatro campos de cadastro + Origin/CSRF | 201 `{usuario}` sem sessão autenticada | 400 `dados_invalidos`; 409 `email_em_uso` ou `ja_autenticado`; 403 CSRF/origem |
| POST `/api/auth/login` | `{email, senha}` + Origin/CSRF | 200 `{usuario, csrf_token, destino}` e novo cookie | 400 validação; 401 `credenciais_invalidas`; 409 `ja_autenticado`; 429 limite |
| GET `/api/auth/sessao` | Cookie | 200 `{usuario, csrf_token, destino}` | 401 `sessao_invalida`, limpando cookie inválido/expirado |
| POST `/api/auth/logout` | Sem corpo; Origin, CSRF se sessão válida | 204, cookie removido | 403 CSRF/origem sem revogação |
| POST `/api/auth/reautenticar` | `{senha}` + cookie/Origin/CSRF | 200 `{csrf_token}` e janela sensível renovada | 400 validação; 401 sessão inválida ou senha incorreta (códigos distintos); 429 limite |

E-mail desconhecido, senha incorreta e conta inativa retornam a mesma mensagem `E-mail ou senha inválidos.` no login. Comparar senha com hash fictício quando não há conta para evitar caminho de execução sem hash. Reautenticação com senha incorreta usa `credenciais_invalidas` e preserva a sessão; frontend não interpreta esse 401 como expiração.

Limite básico: 5 falhas de login por e-mail normalizado em janela de 15 minutos bloqueiam senha para essa chave por 15 minutos. Reautenticação usa chave por usuário com propósito distinto. HMAC da chave lógica protege dados em `auth_limites`; aplicar também a e-mails inexistentes/inativos. Quinta falha e tentativas durante bloqueio retornam 429 com `Retry-After` em segundos. Credenciais válidas durante bloqueio não o contornam. Depois do prazo, contador reinicia; sucesso anterior ao bloqueio zera o contador. Atualização concorrente usa lock no Repository, sem Redis. A criação concorrente da chave deve ser tratada sem erro 500.

O código do 429 é `tentativas_excedidas`. Nos endpoints novos, campos adicionais em login/reautenticação e corpo JSON que não seja objeto recebem 400 `dados_invalidos`. Falha inesperada recebe 500 `erro_interno` com mensagem neutra.

### 6. Políticas das rotas atuais e compatibilidade

| Superfície existente | Política aprovada nesta proposta |
| --- | --- |
| GET `/api/health` | Público; corpo atual preservado. |
| GET `/api/areas-enem`, `/api/materias`, `/api/assuntos` | Aluno ou Administrador. Consultas `status=todos` de Matérias/Assuntos exigem Administrador, preservando leitura administrativa de itens indisponíveis. |
| GET `/api/admin/materias`, `/api/admin/assuntos`, prévias `impacto-exclusao` e `impacto-transferencia` | Administrador. |
| GET `/api/questoes/por-assunto` | Administrador; mantém gabarito/explicação do contrato legado. Aluno recebe 403, mesmo passando identificador válido. |
| POST `/api/materias`, `/api/assuntos`, `/api/questoes`; PUT `/api/materias/<id>`, `/api/assuntos/<id>` | Administrador + CSRF/origem. |
| DELETE de Matéria/Assunto; POST `inativar`, `arquivar`, `reativar`, `transferir` | Administrador + CSRF/origem + autenticação recente de até 15 minutos. |
| PUT Matéria com `status` ou `area_enem_id`; PUT Assunto com `materia_id` | Mesma exigência de autenticação recente, mesmo se o valor não mudar, evitando rota alternativa para ações sensíveis. |

Ordem do guard: identificar rota/método real (não transformar 404/405 em rotas válidas), sessão -> perfil -> Origin/CSRF para mutações -> janela sensível -> negócio. Anônimo: 401 `sessao_invalida`; usuário sem perfil: 403 `acesso_negado`; CSRF: 403 `csrf_invalido`; origem: 403 `origem_nao_permitida`; janela sensível vencida: 403 `reautenticacao_necessaria`. Regras e erros do negócio autorizado continuam como antes. `HEAD` herda a política de GET; `OPTIONS` é tratado como preflight.

Preservar as 10 funcionalidades, a procedure e todas as respostas de sucesso. Os 29 testes originais conservam cenários e asserts de negócio; preparação compartilhada passa a criar Administrador temporário, obter CSRF e executar login real. Um cliente de teste autenticado acrescenta Origin/CSRF às mutações e mantém cookies. Não há flag de desligamento de auth, nem mocks/SQLite nas integrações. Testes novos usam cliente anônimo e Aluno separadamente; unitários focados em Controllers podem mockar o Service de identidade, sem conexão.

### 7. Telas e comportamento de navegação

- Login e cadastro adotam composição oficial PUB-AUT-001/002 a partir do protótipo/handoff/inventário, logo e fontes locais, sem alterar os binários congelados. Cadastro com nome, e-mail, senha, confirmação e botão `Criar minha conta`; login com e-mail, senha, botão `Entrar` e link de cadastro. Labels, foco visível, erros associados, anúncios de estado e operação por teclado são obrigatórios.
- Não renderizar link ativo de recuperação, onboarding, perfil avançado ou funções ausentes. O repositório não contém termos/política de privacidade de produto: este recorte não adiciona checkbox de aceite nem links para documentos inexistentes. Se a referência completa os exibir, a omissão é uma diferença explícita desta change. A confirmação de senha é validação desta change, preservando a identidade visual.
- Cadastro válido exibe confirmação e vai ao login; nome/e-mail permanecem no formulário quando há erro; senha nunca vai a query string/log/storage. Durante envio, impedir duplo clique; indisponibilidade de rede não produz sucesso fictício. Link `Já tenho conta` funciona.
- Destino fixo de Aluno: `/aluno/inicio.html`, com saudação pelo nome retornado da API, identificação do ambiente e `Sair`. É página mínima de acesso, sem atribuir a ela ALU-DASH-001 ou inventar indicadores. Destino fixo de Administrador: `/admin/materias.html`. Não há parâmetro `next` arbitrário nem redirect externo.
- Login/cadastro com sessão autenticada encaminham ao destino fixo do perfil. Aluno na página administrativa ou `/index.html` recebe tela simples de acesso negado e link ao início, sem executar chamadas de gestão. Anônimo nessas páginas vai ao login antes de carregar conteúdo/consultas. A factory não promete sigilo do HTML estático; a API é a fronteira de segurança.
- Integrar nome real e `Sair` às páginas administrativas e ao MVP legado sem remover seu conteúdo/fluxos. O começo protegido permanece oculto até resolver a sessão; erro de rede mostra mensagem/tentar novamente, não acesso concedido.
- Expiração durante formulário administrativo não apaga dados válidos: bloquear mutações e abrir diálogo de autenticação no próprio contexto. Reautenticação sensível usa somente senha; sessão expirada usa login por e-mail/senha. Se login retornar conta diferente da anterior, manter dados apenas visíveis para copiar/descartar e exigir recarga antes de habilitar mutações; nunca salvar formulário de um usuário como outro sem revisão.
- Depois de recuperar a identidade original, reabilitar a ação; usuário a confirma novamente. Não repetir POST/PUT/DELETE automaticamente após 401, CSRF inválido ou reautenticação. Falha de senha/rede mantém diálogo e dados. Logout com alterações locais usa a confirmação de descarte já existente; só navega após 204. Logout sem alterações segue direto.
- `apiRequest` continua retornando JSON/null e `ApiError`. Obtém CSRF uma vez, compartilha promessa de bootstrap e guarda token apenas em memória; recebe token novo após login. Token inválido por troca de sessão em outra aba exige atualizar identidade/CSRF e nova ação explícita, sem repetir mutação. Eventos de storage só podem sinalizar mudança, sem transmitir segredos; não são necessários nesta entrega.

### 8. Validação e preservação de estado

Cobrir cadastro/duplicidade concorrente, autenticação e rotação, sessão expirada/revogada, isolamento de usuários, duas sessões e logout individual, revogação global, CSRF/origens, limite concorrente, todas as políticas de rotas, caminhos alternativos de ações sensíveis e regressão original. Relógio controlável em unitários; integrações usam datas preparadas diretamente no schema descartável, sem sleeps longos. Nenhum caminho de produção ignora segurança para testes.

DOM cobre os formulários, rede/erro, redirect por perfil, integração com API e preservação administrativa. Navegador real valida cookie/CORS/CSRF entre as portas 5500/5000, cadastro -> login -> início -> logout, Administrador -> catálogo e reautenticação. Comparação visual com PUB-AUT-001/002 a 1440 px, além de ausência de overflow a 390 px. Manter gates atuais de 90% linhas/85% branches por stack, sem ajustar limites para aprovar código.

## Risks / Trade-offs

- [Sessão SameSite com hosts diferentes] -> usar o mesmo host/site para frontend e API, configurar credenciais/origens e provar no navegador; cross-site não integra o escopo.
- [Auth altera os contratos anônimos] -> mudança BREAKING explícita, adaptação coordenada dos três consumidores atuais e fixtures reais, sem fallback inseguro.
- [Conta criada sem verificação] -> recorte escolar explícito; e-mail é identificador não verificado, sem afirmar verificação nem disparar e-mail.
- [Bloqueio por e-mail permite indisponibilidade dirigida] -> bloqueio curto e mensagem neutra; limite é básico, sem prometer defesa distribuída/avançada.
- [Linhas antigas de sessão/limites] -> índices e limpeza explícita por comando local `limpar-autenticacao`: remover somente sessões expiradas/revogadas e limites cuja janela e bloqueio terminaram há mais de 24 horas; não adicionar scheduler. Para sessão autenticada, expiração efetiva é o menor instante entre `expira_em` e `ultimo_acesso_em + 30 minutos`; para anônima, `expira_em`. Revogação considera `revogada_em`. Janela de limite termina em `janela_inicio + 15 minutos` e bloqueio NULL não impede limpeza. Nunca remover usuário ou catálogo.
- [Perda de formulário após expiração] -> diálogo no contexto, proibição de retry automático e preservação em memória; não guardar conteúdo/credenciais em storage.
- [Escopo visual escolar difere do produto completo] -> registrar diferenças acima; fonte oficial permanece congelada, sem prometer implementar as 60 telas.

## Migration Plan

1. No apply, preparar `005_create_autenticacao_escolar.sql`, snapshot equivalente e Models; nenhuma migration antiga muda. Pré-condição: histórico 000–004 consistente, backup validado e tabela/constraint nova sem colisões.
2. Estender minimamente o fingerprint/baseline em `backend/database/migrate.py` para reconhecer o estado 005 consolidado completo, sem aceitar subset de colunas/índices/constraints nem relaxar validação dos prefixos históricos. Baseline de snapshot novo reconhece 000–005; estado parcial é recusado.
3. Testar instalação vazia, upgrade a partir de 004, preservação de catálogo/procedure, idempotência, baseline dos estados anteriores e equivalência do snapshot em MySQL descartável. Usuários existentes não existem neste schema, portanto não há backfill de credenciais.
4. Configurar chave/origens/cookie, executar runner oficial e provisionar Administrador pelo comando; usuário comum nasce pelo cadastro público. Não gravar segredos em migration, argumentos, logs ou controle de versão.
5. Ativar aplicação e frontend da mesma versão; verificar os dois fluxos de ponta a ponta e regressão. Nunca implantar frontend novo com backend sem migration/políticas.
6. Falha antes da ativação: seguir o runner e reconciliar/restaurar o backup conforme ADR-001. Não há downgrade automático. Depois de contas reais, preservar novas tabelas/dados; corrigir por migration compensatória ou backup validado. Não reexpor as APIs administrativas restaurando uma versão sem autorização. Documentar recuperação no README e `docs/technical/operacao-autenticacao-escolar.md` durante o apply.

Não há pergunta bloqueante pendente: os valores de duração e políticas apresentados são decisões propostas para revisão nesta change. Hospedagem definitiva não é necessária para validar o recorte local e terá planejamento próprio se solicitada.

Preflight visual: o protótipo PUB-AUT-002 indica 15 caracteres; o recorte escolar aprovado nesta change usa 8–128, conforme a spec. A tela informará 8, sem alterar os binários oficiais.
