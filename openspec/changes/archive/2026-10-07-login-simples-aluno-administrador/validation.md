# Evidências do apply

Validação concluída em 7 de outubro de 2026, no Windows, com Python da `.venv`,
MySQL 8 real e frontend estático. Escopo: cadastro público de Aluno, login dos
dois perfis, sessão, autorização e integração com a gestão existente.

## Regressão e gates

Comandos executados da raiz, com opt-ins exclusivamente no processo:

```powershell
$env:RUN_MYSQL_INTEGRATION = "1"
$env:RUN_MYSQL_MIGRATION_INTEGRATION = "1"
.venv\Scripts\python.exe backend/tests/run_backend_coverage.py
Remove-Item Env:RUN_MYSQL_MIGRATION_INTEGRATION
Remove-Item Env:RUN_MYSQL_INTEGRATION
npm run test:coverage
openspec validate login-simples-aluno-administrador --strict
git diff --check
```

| Validação | Resultado |
| --- | --- |
| Backend unitário | 106 testes aprovados |
| Backend/MySQL, incluindo migrations | 58 testes aprovados, sem skips |
| Cobertura backend | 95,54% linhas (1841/1927), 87,64% branches (461/526) |
| Frontend DOM/contratos | 48 testes aprovados |
| Cobertura frontend | 98,81% linhas (915/926), 85,55% branches (361/422) |
| Gates por stack | 90% linhas/85% branches aprovados; nenhum arquivo zerado |
| OpenSpec strict | Change válida |
| Whitespace do diff | Sem erros |

Os cenários originais de Matérias, Assuntos e Questões permanecem na suíte,
com asserts de negócio preservados. A preparação autentica Administrador pela
API real. Não há SQLite, mocks de integração ou bypass na aplicação. Mocks de
sessão/rede dos testes DOM e unitários não são usados pelo produto.

## Rastreabilidade dos cenários

| Requisitos/cenários | Implementação e evidência |
| --- | --- |
| Cadastro, validação, duplicidade normalizada/concorrente, perfil extra e conta já autenticada | `CadastrarAlunoService`/`CriarUsuarioService`; `test_validacao_duplicidade_e_perfil`, `test_concorrencia_cadastro_e_contador`; `auth.test.js` |
| Administrador local, confirmação e conflito sem promoção | `auth_cli.py`; `test_cli_conta_limpeza_e_revogacao`, `test_cli_duplicado_preserva_aluno_senha_e_catalogo`, unitário de erro neutro |
| Login, hash, identidade pública, rotação e rollback | `LoginService`/`CriarSessaoService`; `test_cadastro_login_cookie_identidade_logout`, `test_rotacao_reverte_nova_sessao_se_revogacao_falhar`; trigger de falha real somente no schema descartável |
| Expiração absoluta/inatividade, conta inativa, logout individual/global e concorrência com revogação | `ConsultarSessaoService`/Repository; testes de limites inclusivos unitários/MySQL, `test_cli_conta_limpeza_e_revogacao`, `test_revogacao_concorrente_nao_ressuscita_sessao` |
| Origin, CSRF de outra sessão, cookie, no-store e preflight | `auth_http.py`/Controller/factory; `test_csrf_origins_e_cookie_secure`, testes unitários de configuração; `api.test.js` e navegador entre portas |
| Matriz de autorização, gabarito, status=todos, HEAD e 404/405 | `test_autorizacao_todas_rotas_existentes` percorre as regras/métodos existentes; regressões administrativas autenticadas |
| Janela sensível, PUT alternativos, senha incorreta e nova confirmação | `AutorizarService`/`ReautenticarService`; `test_expiracao_absoluta_inatividade_e_reautenticacao`; DOM e navegador sem retry automático |
| Quinta falha, Retry-After, retomada, desconhecido/inativo e concorrência | `ValidarSenhaService`/locks MySQL; `test_limite_senha_inativa_e_retomada`, `test_concorrencia_cadastro_e_contador` |
| Tela de cadastro/login, prefill consumido, loading, erros e destinos fixos | `auth-page.js`, `auth.test.js`; fluxo real de Aluno e inspeção desktop/mobile |
| Guard, identidade, saída com edição, rede indisponível, expiração, troca de conta e CSRF | `auth-session.js`, guard dos três consumidores; `auth.test.js`, regressões DOM administrativas/legadas e navegador |
| Upgrade, snapshot, baseline, preservação e idempotência | `test_migrations_integration.py`: instalação 000–005, todos os prefixos, equivalência e rejeição de sete estados divergentes; migrations antigas intactas |
| Limpeza sem excluir contas/catálogo/sessão válida | `LimparAutenticacaoService`; testes CLI com contagens antes/depois e sessão válida preservada |

## Navegador real

Frontend em `127.0.0.1:5500` e API em `127.0.0.1:5000`, usando somente schema
de QA com prefixo validado `plataforma_enem_api_test_`. Contas/conteúdo usados
na inspeção eram temporários; nenhum dado do schema funcional foi alterado.

- Cadastro retornou ao login com apenas e-mail preenchido e senha vazia.
  Login de Aluno exibiu seu nome real; logout retornou ao login.
- Aluno recebeu 403 na API administrativa e acesso negado nas telas de
  Matérias, Assuntos e `/index.html`, sem revelar conteúdo protegido.
- Administrador entrou em Matérias, criou conteúdo temporário e acessou
  Assuntos/MVP legado com identidade real e API online.
- Reautenticação exigida por janela vencida abriu diálogo com foco na senha.
  Senha incorreta manteve sessão/edição; senha correta fechou diálogo sem
  executar novamente a ação. A matéria continuou ativa.
- Inatividade forçada somente na sessão de QA gerou 401 antes do PUT.
  Login contextual recuperou a mesma conta e preservou a edição, sem repetir PUT.
- Sessão vencida ao abrir outra tela redirecionou ao login.
- Requests reais entre portas usaram cookies/CSRF/preflight; cookie HttpOnly
  não apareceu em `document.cookie`. Flags completas/Secure foram também
  verificadas por integração HTTP real no MySQL.
- Login/cadastro foram comparados visualmente com páginas 0/1 do protótipo
  oficial em 1440 px. Em 390 px, os formulários ficaram dentro da viewport,
  com largura aproximada de 342 px e sem rolagem horizontal; Tab produziu foco
  visível. Ativos de logo/fonte são locais.

A captura de uma aba móvel travou na ferramenta. A inspeção foi concluída em
outra aba isolada a 390 px. A captura auxiliar headless do Windows recortava
a viewport e foi descartada; não foi usada como evidência de responsividade.

## Preservação e operação

Diff revisado: não modifica migrations 000–004, binários oficiais, `.env`,
dependências ou infraestrutura. Acrescenta migration 005 e snapshot equivalente.
Sem commit/push/merge. A diferença de senha mínima 8 versus 15 no protótipo
está documentada no design aprovado, sem alteração do material oficial.

O operador ainda deve configurar chave privada, aplicar 005 no banco funcional
e criar seu Administrador conforme `docs/technical/operacao-autenticacao-escolar.md`.
O apply não provisionou conta real nem migrou o banco funcional.

## Correções e nova verificação

Em 7 de outubro de 2026, o usuário autorizou corrigir os dois avisos reproduzidos
durante `openspec-verify-change`:

- Cadastro: nome é validado após trim (2–100 caracteres), com erro associado,
  `aria-invalid` e foco no campo. Teste cobre espaços, nome curto após trim,
  excesso de tamanho e correção válida, preservando e-mail e contrato HTTP.
- MVP legado: ao abrir edição de Matéria/Assunto, o formulário carregado passa
  a ser a referência de comparação para logout. Testes distinguem abertura sem
  mudanças, edição real, reversão e cancelamento; dados alterados continuam
  sinalizados como não salvos.

Foi executado novamente `npm run test:coverage`: 48 testes passaram e os gates
permaneceram aprovados. Backend e banco não foram alterados por essas correções;
seus resultados acima são da execução completa anterior, mantida como evidência.

| Dimensão da nova verificação | Resultado |
| --- | --- |
| Completude | 29/29 tarefas concluídas; requisitos da change representados |
| Correção | Dois avisos corrigidos com regressões; gates aprovados |
| Coerência | Mesmos contratos, camadas, schema e escopo escolar |

Não restam críticos nem os dois avisos reproduzidos nesta revisão. A change
está pronta para sincronização e arquivamento, seguindo essa ordem.
Sync/archive não foram executados nesta correção.

## Sincronização e arquivamento

Em 7 de outubro de 2026, após solicitação do usuário, os três deltas foram
sincronizados nas specs principais: 11 requisitos de autenticação adicionados,
compatibilidade do catálogo atualizada e acesso administrativo/proteção de
formulários incorporados. Antes do arquivamento, a comparação dos 14 requisitos
dos deltas confirmou correspondência integral com as specs principais.

Validações de encerramento: `openspec validate login-simples-aluno-administrador
--strict` aprovou a change; `openspec validate --specs` aprovou as quatro specs,
sem falhas. Todos os artefatos estavam concluídos, com 29/29 tarefas e sem
achados críticos pendentes. Os testes de implementação não foram repetidos
nesta etapa documental; os resultados registrados acima continuam como evidência.

A change foi arquivada em
`openspec/changes/archive/2026-10-07-login-simples-aluno-administrador/`,
preservando os artefatos e `.openspec.yaml`. Nenhum commit, push ou merge foi feito.
