# Operação da autenticação escolar

## Escopo e preparação

Esta entrega adiciona cadastro público de Aluno, login por e-mail/senha, sessão
individual e acesso administrativo. Mantém Flask, frontend estático e MySQL 8.
Não inclui recuperação/verificação de e-mail, onboarding ou dashboard. E-mail
é identificador não verificado; a interface não afirma que houve verificação.

Antes de ativar a aplicação atualizada, valide backup e histórico do banco.
As migrations antigas permanecem imutáveis. A `005` adiciona `usuarios`,
`sessoes` e `auth_limites`, sem contas padrão, sem modificar catálogo/procedure.
O snapshot consolidado representa o mesmo estado final. Use o runner oficial:

```powershell
python backend/database/migrate.py status
python backend/database/migrate.py up
```

Instalação pelo snapshot exige adoção pelo `baseline --confirm` já documentado
no README. O fingerprint reconhece os estados históricos e o estado 005,
recusando autenticação parcial ou colunas/índices/checks/FKs divergentes.
DDL MySQL pode confirmar parcialmente: falha exige inspeção e recuperação
conforme ADR-001, nunca alteração do arquivo aplicado. Não há downgrade
automático. Preserve contas novas em correção compensatória ou backup validado;
não reexponha gestão restaurando versão sem autorização.

Configure `AUTH_SECRET_KEY` com 32 bytes aleatórios em 64 caracteres hexadecimais.
A aplicação recusa chave ausente/formato inválido. Não use a chave fictícia dos
testes na aplicação. Para execução local, gere somente no processo, sem imprimir:

```powershell
$env:AUTH_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
python backend/run.py
```

Mantenha a mesma chave entre processos/reinícios para preservar CSRF e limites.
Para configuração persistente, o operador informa sua chave privada no ambiente
local. O agente preservou o `.env` existente; a aplicação mantém o carregamento
de configuração já usado pelo projeto. `.env.example` contém somente variável
vazia. Cookies usam `AUTH_COOKIE_SECURE=false` em HTTP
local e exigem `true` no ambiente de entrega HTTPS. Não existe infraestrutura
externa de autenticação.

## Contas e uso

Abra `http://127.0.0.1:5500/login.html`, com frontend servido pelo comando atual:

```powershell
python -m http.server 5500 --directory frontend
```

`Criar uma conta` abre `/cadastro.html`. Cadastro pede nome, e-mail, senha de
8–128 caracteres e confirmação; cria sempre Aluno e encaminha ao login, sem
login automático. Nome/e-mail permanecem após erro, senha não vai a logs/URL/storage.
E-mail é normalizado por trim/lowercase, único inclusive sob concorrência.
Apenas e-mail de cadastro é transferido por sessionStorage e removido ao entrar.

Crie Administrador pelo terminal, da raiz e no mesmo ambiente configurado:

```powershell
python -m flask --app backend/run.py criar-administrador
```

O comando pergunta nome, e-mail e senha confirmada sem eco. E-mail já registrado
gera conflito; não promove Aluno nem redefine senha. Não há senha padrão.

Após login, Aluno vai a `/aluno/inicio.html`, com saudação real e `Sair`.
Administrador vai a `/admin/materias.html` e pode acessar Assuntos e o MVP legado
em `/index.html`. O início do Aluno não é dashboard e não inventa indicadores.
Login/cadastro reproduzem a composição PUB-AUT-001/002; os binários oficiais
permanecem congelados. Diferenças escolares: senha mínima de 8 caracteres e
ausência de links sem destino real de recuperação/privacidade/ajuda/onboarding.

## API, cookies e origem

| Método/rota | Entrada | Sucesso |
| --- | --- | --- |
| GET `/api/auth/csrf` | Cookie opcional | 200 `{csrf_token}`, sessão anônima se necessário |
| POST `/api/auth/cadastro` | `{nome,email,senha,senha_confirmacao}` | 201 `{usuario}` |
| POST `/api/auth/login` | `{email,senha}` | 200 `{usuario,csrf_token,destino}` e cookie novo |
| GET `/api/auth/sessao` | Cookie | 200 `{usuario,csrf_token,destino}` |
| POST `/api/auth/logout` | Sem campos | 204 e cookie removido |
| POST `/api/auth/reautenticar` | `{senha}` | 200 `{csrf_token}` |

Usuário público contém somente `id`, `nome`, `email` e `perfil`. Hash/identificador
opaco nunca saem na resposta. Erros usam `{erro,codigo}`: 400 `dados_invalidos`,
401 `credenciais_invalidas`/`sessao_invalida`, 403 `acesso_negado`,
`csrf_invalido`, `origem_nao_permitida`, `reautenticacao_necessaria`, 409
`email_em_uso`/`ja_autenticado`, 429 `tentativas_excedidas` com Retry-After e
500 `erro_interno` neutro. Os erros de negócio das APIs legadas mantêm o contrato.

Todas as mutações exigem Origin explícita permitida e `X-CSRF-Token`, inclusive
cadastro/login. Primeiro obtenha CSRF, mantendo o cookie `enem_session`.
Logout sem sessão válida é idempotente e dispensa CSRF, mantendo Origin.
Token CSRF fica em memória; o identificador de autenticação é HttpOnly,
SameSite=Lax, Path=/api, sem Domain e Secure em HTTPS. Sessão anônima dura 10
minutos; autenticada dura 8 horas absolutas ou 30 minutos de inatividade.
Cookie renovado pelo bootstrap respeita o tempo absoluto restante.
Logout revoga apenas a sessão atual; revogação global existe na camada do servidor.

Configure `CORS_ORIGINS` com origens exatas, sem wildcard/caminho. Frontend e API
devem usar o mesmo host/site: `127.0.0.1:5500` com `127.0.0.1:5000`, ou
`localhost:5500` com `localhost:5000`. Não misture os dois hosts. O cliente usa
`credentials: include`; implantação pode definir `window.ENEM_API_URL` antes
de `api.js`. Implantação cross-site não faz parte desta change.
Respostas de identidade são no-store; o HTML estático não é a fronteira de
segurança: a API verifica identidade/perfil em todas as operações protegidas.

## Compatibilidade e ações sensíveis

**Mudança de contrato anônimo:** health continua público; Áreas, Matérias e
Assuntos exigem login. `status=todos`, gestão, impacto e todas as mutações
exigem Administrador. Questões legadas contêm gabarito e exigem Administrador.
Aluno recebe 403 ao tentar esses recursos, mesmo por requisição direta.
URLs, campos e respostas de sucesso para o perfil autorizado são preservados.
HEAD segue GET; OPTIONS é preflight; 404/405 permanecem intactos.

Exclusão, ações de status, transferência e PUT alternativos com status/Área
de Matéria ou Matéria do Assunto exigem senha confirmada há menos de 15 minutos.
Login inicia essa janela. Vencida a janela, a gestão solicita senha no contexto,
mantendo campos e filtros; sessão expirada solicita novo login no diálogo.
Senha incorreta de reautenticação não encerra a sessão. Conta diferente exige
copiar/descartar dados e recarregar antes de novas mutações. Nenhum POST/PUT/DELETE
é repetido automaticamente após recuperar sessão/CSRF; confirme novamente a ação.
Logout com alterações não salvas permite continuar editando ou descartar;
falha de rede não navega como se tivesse saído.

Cinco falhas de senha em 15 minutos bloqueiam a identidade por 15 minutos,
inclusive conta inexistente/inativa. Reautenticação tem contador separado.
Mesmo senha correta não contorna bloqueio vigente. Após o prazo, contador
reinicia; sucesso anterior ao bloqueio zera falhas. É limite básico escolar,
sem promessa de proteção avançada.

## Limpeza e testes

```powershell
python -m flask --app backend/run.py limpar-autenticacao
```

Remove somente sessões expiradas/revogadas há mais de 24 horas e limites cuja
janela/bloqueio terminaram há mais de 24 horas. Preserva usuários, sessões
válidas e todo catálogo/histórico. Não existe scheduler nem exclusão de conta.

Os testes originais mantêm cenários/asserts, autenticando Administrador real
na preparação compartilhada. Nenhum bypass existe na aplicação. Integrações
usam MySQL 8 e schemas descartáveis; mocks ficam exclusivamente nos unitários.

```powershell
python backend/tests/run_unit.py
$env:RUN_MYSQL_INTEGRATION = "1"
$env:RUN_MYSQL_MIGRATION_INTEGRATION = "1"
python backend/tests/run_backend_coverage.py
Remove-Item Env:RUN_MYSQL_MIGRATION_INTEGRATION
Remove-Item Env:RUN_MYSQL_INTEGRATION
npm run test:coverage
```

Os gates permanecem 90% de linhas e 85% de branches por stack. Evidências do
apply ficam na change; não confundir validação de planejamento com testes ou
verificação da implementação.
