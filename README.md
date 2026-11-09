# Plataforma ENEM

Projeto escolar de conclusão de curso para organizar matérias, assuntos e
questões do ENEM. As áreas administrativa e do Aluno usam HTML, CSS e
JavaScript, consumindo uma API Flask persistida em MySQL. Inclui conteúdo
versionado, práticas, simulados, desempenho e plano básico de estudos.

Os [Termos de Uso](frontend/legal/termo-de-uso-v2.html) e o
[Consentimento do plano](frontend/legal/termo-de-consentimento-plano-v1.html)
são documentos completos, públicos e imprimíveis. O cadastro exige aceite
explícito de uso; o plano depende de autorização opcional posterior em
`/aluno/privacidade.html`. Recusa ou revogação confirmada apaga os planos
próprios e suas conclusões; questões, práticas, simulados e desempenho continuam
disponíveis. Nova autorização permite começar outro plano, sem restaurar o antigo.

Esta extensão é uma demonstração acadêmica com dados sintéticos. O responsável
informado é Matheus Gabriel Oliveira Martins e o contato `.example` é fictício,
não operacional. Antes de dados reais, definir canal válido, política geral de
retenção/direitos e proteção/autorização de menores. Não há adequação jurídica
integral ou bônus garantido. Veja [fontes e limites](docs/legal/README.md) e
[operação de privacidade](docs/technical/operacao-privacidade.md).

## Gestão administrativa de Alunos

O menu **Usuários** abre `/admin/usuarios.html`: criar, buscar, consultar,
editar nome/e-mail, desativar/reativar e excluir contas de Aluno sem vínculos.
Criação administrativa usa senha inicial, sem sessão ou aceite em nome do titular.
Trocar e-mail ou desativar revoga sessões; reativar exige novo login.
Contas com aceites, sessões ou histórico recebem 409 no DELETE; desativação é
uma ação distinta. Administradores não são alvos deste recorte.

Instale a migration **017** antes das novas telas/rotas, após backup validado
em ambiente operacional. Veja [contratos, Services, routines e operação](docs/technical/gestao-administrativa-alunos.md).

## Tecnologias utilizadas

- Python 3.10 ou mais recente
- Flask e Flask-CORS
- Flask-SQLAlchemy com SQLAlchemy 2
- PyMySQL
- MySQL Server 8.0
- HTML5, CSS3 e JavaScript sem framework
- `unittest` e `coverage.py` para testes Python
- Vitest, jsdom e cobertura V8 para testes do frontend
- Playwright/Chromium para testes de navegador com API e MySQL reais

## Arquitetura

O fluxo obrigatório da aplicação é:

```text
Frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL
```

Controllers adaptam requisições e respostas HTTP. Cada Service representa um
caso de uso e concentra suas validações. As Models contêm o CRUD simples. O
Repository é reservado para consultas especializadas, contagens, impacto,
locks e a Stored Procedure existente.

Nove consultas recebem contratos por construtor, ligadas pela factory em uma
composição própria por aplicação. Models usam `ModeloBase`, `ModeloAtualizavel`
ou `CrudMixin` conforme a capacidade; versões/eventos não oferecem mutações
incompatíveis. Veja [SOLID e testes](docs/technical/aplicacao-solid.md),
[ADR-008](docs/technical/adr/ADR-008-contratos-e-capacidades-de-persistencia.md)
e [diagrama](docs/technical/diagrama-de-classes.md).

```text
Plataforma ENEM/
├── frontend/
│   ├── css/
│   ├── js/
│   └── index.html
└── backend/
    ├── app/                         pacote Python da aplicação Flask
    │   ├── modules/                 contas, conteudo, praticas, simulados,
    │   │                            desempenho, plano_estudos e tutor_ia
    │   │                            cada qual com rotas e camadas próprias
    │   ├── core/                    bases, relógio, paginação, validação e health
    │   ├── contracts/               Protocols e registros de leitura
    │   ├── composition.py           ligações por aplicação
    │   ├── models/                  registro das 21 Models e ponte das bases
    │   ├── extensions.py            db compartilhado e CORS
    │   └── routes.py                agregação dos sete Blueprints e health
    ├── database/
    │   ├── migrate.py                   runner oficial de migrations SQL
    │   ├── migration_types.py           tipos compartilhados de migration e erro
    │   ├── sql_scripts.py               leitura, validação e separação do SQL
    │   ├── legacy_schema.py             reconhecimento de schemas históricos
    │   ├── migrations/
    │   └── create_database.sql
    ├── tests/
    ├── requirements.txt
    └── run.py
```

As quatro camadas exigidas pela disciplina estão dentro de `backend/app`
porque `app` é o pacote importável usado pela application factory do Flask.
As camadas `controllers`, `models`, `repositories` e `services` ficam dentro
do módulo proprietário em `backend/app/modules/`, conforme o
[mapa modular](docs/technical/organizacao-modular.md) e o
[ADR-010](docs/technical/adr/ADR-010-organizacao-modular-do-backend.md).
As mesmas 21 Models, vinte funcionalidades e URLs permanecem; o bootstrap
continua em `database/create_database.sql`. Módulos colaboram por APIs/contratos,
com SQL especializado nos Repositories e CRUD simples nas Models.

## Funcionalidades Implementadas

1. Cadastrar Matéria.
2. Listar Matérias.
3. Atualizar Matéria.
4. Excluir Matéria sem vínculos.
5. Cadastrar Assunto.
6. Listar Assuntos.
7. Atualizar Assunto.
8. Excluir Assunto sem vínculos.
9. Cadastrar Questão.
10. Buscar Questões por Assunto.
11. Cadastrar Aluno.
12. Fazer login.
13. Editar Questão.
14. Publicar Questão com snapshot imutável.
15. Arquivar Questão preservando histórico.
16. Iniciar prática de Questão publicada.
17. Responder prática com correção persistida.
18. Consultar histórico próprio de práticas.
19. Criar Simulado manual com composição fixa.
20. Consultar desempenho por Matéria/Assunto.

A [matriz de entrega](docs/technical/entrega-academica.md) liga cada número à
interface, API, camadas, persistência e evidência. O
[diagrama de classes](docs/technical/diagrama-de-classes.md) cobre as 21 Models.
A [modelagem de domínio atual](docs/technical/modelagem-de-dominio.md) explica
seus papéis e relações. A [matriz CRUD](docs/technical/matriz-crud.md) distingue
métodos de persistência, API e interface, com lacunas e restrições explícitas.
Esses documentos não comprovam entrega/aprovação acadêmica nem CRUD integral;
as evidências de execução permanecem limitadas aos relatórios referenciados.
Os [fluxogramas de casos de uso](docs/technical/fluxogramas-casos-de-uso.md)
detalham recuperação de dados (diagnóstico) e entrada (finalização de Simulado),
ambas já implementadas.
Automação, CI e documentação não são funcionalidades extras nessa contagem.

Também implementados: gestão administrativa filtrada/paginada, ciclo de vida
e transferência auditada do catálogo; logout e reautenticação; publicação,
execução, resposta e finalização de Simulados; dashboards; geração, recálculo
e conclusão manual do plano básico, acessível nas oito páginas do Aluno.

O acesso inicial é `/login`; o cadastro público cria somente Aluno.
Administrador é criado pelo comando local, sem senha padrão. Antes de iniciar
esta versão, aplique as migrations até `016` e configure `AUTH_SECRET_KEY`.
Veja [Operação da autenticação escolar](docs/technical/operacao-autenticacao-escolar.md)
para preparação, comandos, contratos, cookies/origens e recuperação.

As APIs de gestão exigem Administrador; leituras simples do catálogo exigem
login. Os payloads de sucesso existentes são preservados para o perfil
autorizado. `/index.html` continua disponível ao Administrador como MVP legado.

## Componentes implementados

As Models concretas, seus principais atributos, FKs, cardinalidades e herança
pelo caminho único `db.Model → ModeloBase → ModeloAtualizavel → CrudMixin`
estão no [diagrama](docs/technical/diagrama-de-classes.md). Cada Model usa a base
adequada às suas capacidades de persistência.
Desempenho é projeção de respostas concluídas, sem tabela de resultado inventada.

Services de negócio:

- `CriarMateriaService`, `ListarMateriasService`,
  `AtualizarMateriaService` e `DeletarMateriaService`.
- `CriarAssuntoService`, `ListarAssuntosService`,
  `AtualizarAssuntoService` e `DeletarAssuntoService`.
- `CriarQuestaoService` e `BuscarQuestoesPorAssuntoService`.

Repository:

- `QuestaoRepository`: encapsula o `CALL` legado, leituras administrativas,
  elegibilidade/conteúdo histórico em lote, projeções e locks editoriais.
  O cadastro de Questão mantém CRUD na Model.
- `CatalogoRepository`: consultas administrativas, contagens, impacto e locks;
  não duplica CRUD nem controla commits.
- `AutenticacaoRepository`: consultas de sessão, revogação, locks e limpeza.
- `PraticaRepository`, `SimuladoRepository`, `DesempenhoRepository` e
  `PlanoEstudoRepository`: consultas especializadas dos respectivos módulos.

Stored Procedure:

- `sp_questoes_por_assunto`: recebe `assunto_id`, filtra as questões no MySQL
  e devolve o resultado ordenado por `id`.

## Consulta individual do catálogo

`GET /api/materias/{id}` e `GET /api/assuntos/{id}` exigem Administrador
autenticado e incluem registros ativos, inativos e arquivados. Aceitam HEAD,
usam `Cache-Control: no-store` e não exigem CSRF ou senha recente para leitura.
Query strings não mudam a permissão nem filtram o detalhe.

Exemplo de Matéria (200):

```json
{"id":12,"nome":"Matemática","descricao":null,"area_enem_id":4,"status":"inativa","criado_em":"2026-11-09T10:00:00","atualizado_em":"2026-11-09T10:00:00"}
```

Assunto retorna `id`, `nome`, `nome_normalizado`, `descricao`, `materia_id`,
`status`, `criado_em` e `atualizado_em`. Os objetos não incluem contagens ou
relações aninhadas; descrição nula continua `null` e datas seguem ISO 8601.
IDs zero/acima de 2147483647 retornam 400; ID válido ausente, 404; sem sessão,
401; Aluno, 403. Erros usam `erro`; falhas inesperadas retornam 500 genérico.
Texto/negativos mantêm o 404 do roteador.

Em `/admin/materias.html` e `/admin/assuntos.html`, **Editar** consulta o detalhe
antes de preencher. Assunto também atualiza as opções de Matéria, preservando a
Matéria corrente mesmo inativa/arquivada. Durante a leitura, Salvar fica bloqueado.
Falhas preservam rascunho, filtros e página; repetir exige clicar Editar novamente.
Digitação, outra seleção, Novo/Cancelar/Salvar ou perda/troca de identidade
invalidam respostas pendentes. O descarte continua confirmado pelo formulário;
a identidade é revalidada antes do preenchimento. A escrita ocorre só ao Salvar.

## Rotas legadas da API

As demais rotas e Services dos vinte casos estão na
[matriz](docs/technical/entrega-academica.md). Contratos completos por domínio:
[Questões](docs/technical/operacao-questoes.md),
[Práticas](docs/technical/operacao-praticas.md),
[Simulados](docs/technical/operacao-simulados.md),
[Desempenho](docs/technical/operacao-desempenho.md) e
[Plano](docs/technical/operacao-plano-estudos.md).

O catálogo administrativo, suas migrations e a auditoria pré-upgrade estão
detalhados em [Operação do catálogo acadêmico](docs/technical/operacao-catalogo-academico.md).

| Método | Rota | Finalidade |
| --- | --- | --- |
| `GET` | `/api/health` | Verificar se a API está em execução |
| `POST` | `/api/materias` | Cadastrar uma matéria |
| `GET` | `/api/materias` | Listar matérias |
| `PUT` | `/api/materias/<id>` | Atualizar uma matéria |
| `DELETE` | `/api/materias/<id>` | Excluir uma matéria |
| `POST` | `/api/assuntos` | Cadastrar um assunto |
| `GET` | `/api/assuntos` | Listar assuntos |
| `PUT` | `/api/assuntos/<id>` | Atualizar um assunto |
| `DELETE` | `/api/assuntos/<id>` | Excluir um assunto |
| `POST` | `/api/questoes` | Cadastrar uma questão |
| `GET` | `/api/questoes/por-assunto?assunto_id=<id>` | Buscar questões por assunto |

## Pré-requisitos

- Python 3.10 ou mais recente disponível no terminal.
- MySQL Server 8.0 em execução.
- Cliente de linha de comando `mysql` ou MySQL Workbench para executar os
  scripts SQL.
- Node `>=22.9.0` e npm `11.6.2` para os testes do frontend.
- GNU Make, opcional, para usar os atalhos do `Makefile`; confirme com
  `make --version`.

## Preparação do ambiente

No PowerShell, a partir da raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements-dev.txt
npm ci
npm run hooks:install
Copy-Item .env.example .env
```

Edite o `.env` criado e informe os valores locais de `DB_HOST`, `DB_PORT`,
`DB_NAME`, `DB_USER` e `DB_PASSWORD`. Também é possível configurar uma
`DATABASE_URL` completa. Configure também `AUTH_SECRET_KEY` conforme a
documentação operacional. Não coloque credenciais reais no `.env.example`.

O `.env` está listado no `.gitignore` e não deve ser enviado ao repositório.

## Criação e atualização do banco MySQL

As migrations oficiais são arquivos SQL em `backend/database/migrations/`.
`migrate.py` controla ordem, checksum SHA-256, lock e histórico na tabela
`schema_migrations`, sem Alembic ou Flask-Migrate.

`migration_types.py` reúne os tipos compartilhados e `sql_scripts.py` cuida
da leitura, validação, separação e execução das instruções SQL.
`legacy_schema.py` reconhece estruturas históricas para o baseline.
`migrate.py` continua sendo a entrada oficial e coordena configuração,
histórico, locks e comandos. Essa divisão separa responsabilidades da
infraestrutura, preservando os comandos abaixo.

O schema configurado deve existir antes do runner. Para uma instalação nova,
crie-o vazio com `utf8mb4_unicode_ci`, configure o `.env` e execute:

```powershell
python backend/database/migrate.py status
python backend/database/migrate.py up
```

`up` aplica `000` a `017` em ordem. Chamá-lo novamente não reexecuta
migrations aplicadas. `create_database.sql` permanece como snapshot consolidado
para compatibilidade; uma instalação feita por ele deve adotar o histórico como
um banco existente.

### Adoção de um banco MVP existente

Faça e valide um backup antes da adoção. Em seguida:

```powershell
python backend/database/migrate.py status
python backend/database/migrate.py baseline --confirm
python backend/database/migrate.py up
```

`baseline` compara tabelas, colunas, índices, constraints, foreign keys e
`sp_questoes_por_assunto` com os estados históricos conhecidos. Ele registra
somente o prefixo comprovado e não altera dados funcionais. Schema divergente é
recusado; não corrija o histórico manualmente para contornar essa proteção.

Nos prefixos `008`–`010`, as dez tabelas de Simulados, Plano e Privacidade são
reconhecidas por assinatura de metadados do MySQL, com referências derivadas das
migrations oficiais. Charset implícito ou explícito no DDL é aceito quando os
metadados são iguais. O nome físico do schema e contadores não interferem;
diferenças reais de charset/collation, defaults, índices, FKs, CHECK/ENFORCED e
expressões geradas continuam recusadas. Metadados obrigatórios indisponíveis
causam erro. Isso não garante compatibilidade universal entre versões.
Esses prefixos também conferem corpo e parâmetros da procedure conhecida.

A assinatura estrutural reconhece o schema; o checksum SQL protege os arquivos
aplicados em `schema_migrations`; o hash legal identifica o HTML aceito.
São verificações independentes. Consulte o [adendo ao ADR-001](docs/technical/adr/ADR-001-estrategia-de-migrations.md#22-adendo--assinatura-estrutural-portável-2026-11-07).

### Falhas e recuperação

DDL do MySQL pode confirmar mudanças antes do fim do arquivo. Por isso uma
migration `FAILED` ou `RUNNING` bloqueia todas as seguintes. Após inspecionar o
schema e restaurar o backup ou aplicar uma correção segura, autorize nova
tentativa explicitamente:

```powershell
python backend/database/migrate.py status
python backend/database/migrate.py reconcile 003 --confirm
python backend/database/migrate.py up
```

`reconcile` não desfaz SQL. Ele apenas registra que a reconciliação externa foi
feita. Nunca altere uma migration `APPLIED`; checksum, remoção ou renomeação do
arquivo bloqueiam o runner.

O usuário operacional deve ter acesso ao schema configurado, leitura de
`information_schema`, uso de `GET_LOCK`, DDL exigido pelas migrations e leitura/
escrita em `schema_migrations`. Prefira um usuário separado do usuário da API e
conceda apenas os privilégios necessários. Credenciais ficam somente no
ambiente e nunca nos scripts SQL ou argumentos do terminal.

## Executando o backend

Na raiz do projeto, com o ambiente virtual ativado:

```powershell
python backend\run.py
```

A API utiliza `http://127.0.0.1:5000` por padrão.

## Executando o frontend

Em outro terminal:

```powershell
python scripts/serve_frontend.py
```

Abra `http://127.0.0.1:5500/login`. O servidor usa somente a biblioteca padrão
do Python, escuta em `127.0.0.1` e serve a raiz pública `frontend`.
Para outra porta, use `python scripts/serve_frontend.py --port 5501` e autorize
a origem `http://127.0.0.1:5501` em `CORS_ORIGINS` na configuração local da API.

## Testes automatizados

Os testes unitários Python bloqueiam o `.env`, usam uma URL fictícia apenas
para inicializar o Flask e não abrem conexão. As integrações usam schemas MySQL
8 descartáveis, sem mocks ou SQLite. O frontend usa jsdom.

```powershell
python backend/tests/run_unit.py
npm run test:unit
npm run test:coverage
```

Para autorizar integrações, informe o opt-in somente no processo:

```powershell
$env:RUN_MYSQL_INTEGRATION = "1"
python backend/tests/run_integration.py
Remove-Item Env:RUN_MYSQL_INTEGRATION
```

O preflight valida conexão, tabelas e `sp_questoes_por_assunto`. Os runners
nunca exibem valores de configuração sensível.

As integrações destrutivas do runner criam e removem somente schemas com nome
aleatório rigidamente validado e exigem um segundo opt-in no mesmo processo:

```powershell
$env:RUN_MYSQL_INTEGRATION = "1"
$env:RUN_MYSQL_MIGRATION_INTEGRATION = "1"
python backend/tests/run_integration.py
Remove-Item Env:RUN_MYSQL_MIGRATION_INTEGRATION
Remove-Item Env:RUN_MYSQL_INTEGRATION
```

O usuário de teste precisa poder criar e remover esses schemas descartáveis.

Com GNU Make disponível, os atalhos são:

| Alvo | Equivalente direto |
| --- | --- |
| `make db-status` | `python backend/database/migrate.py status` |
| `make db-up` | `python backend/database/migrate.py up` |
| `make db-baseline` | baseline confirmado do schema existente |
| `make db-reconcile VERSION=003` | reconciliação confirmada da versão informada |
| `make test-unit` | `python backend/tests/run_unit.py` e `npm run test:unit` |
| `make test-integration` | `python backend/tests/run_integration.py` |
| `make test-backend` | `python backend/tests/run_backend_coverage.py` |
| `make test-frontend` | `npm run test:coverage` |
| `make test-coverage` | runner backend e cobertura frontend |
| `make test` | igual a `make test-coverage` |
| `make test-e2e` | `python scripts/run_e2e.py` |

Os gates por stack são 90% de linhas e 85% de branches agregados, além de
reprovar qualquer arquivo executável zerado.

### Navegador e integração contínua

Com configuração MySQL fornecida **por ambiente** (o runner E2E não lê `.env`)
e permissão de criar/remover schemas descartáveis:

```powershell
npx playwright install chromium
npm run test:e2e:list
$env:RUN_MYSQL_E2E = "1"
npm run test:e2e
Remove-Item Env:RUN_MYSQL_E2E
```

O runner usa migrations oficiais, operador sintético e API/frontend locais em
portas livres. A suíte contém **quatro testes Playwright**:
[entrega-academica.spec.js](frontend/e2e/entrega-academica.spec.js) preserva os vinte casos
numerados, navegação ao plano, cancelamento de descarte e capturas a 1440/390 px.
[plano-simulado.spec.js](frontend/e2e/plano-simulado.spec.js), com conta e conteúdo próprios,
verifica geração/conclusão manual do Plano, finalização/correção de Simulado e
recálculo confirmado, cancelamentos e persistência por recarga/GET real.
Confere 2/5 (40%) no plano inicial, 1/3 (33,33%) no resultado do Simulado e
3/7 (42,86%) no diagnóstico/novo plano; o branco não entra no diagnóstico.
Um replay HTTP auxiliar, identificado no teste e sem botão, verifica a geração
anterior preservada.
[privacidade.spec.js](frontend/e2e/privacidade.spec.js) cobre documentos públicos,
cadastro com aceite explícito, recusa mantendo estudo real, autorização do plano,
revogação com eliminação e nova autorização, incluindo outra aba aberta.
`npm run test:e2e:list` apenas descobre os quatro testes; não executa seus percursos
nem comprova aprovação. Nenhuma resposta é simulada. Esses passos adicionais não
alteram a contagem oficial de vinte funcionalidades. Processos/schema são
limpos em `finally`, mesmo após falha.
Relatórios e capturas sintéticas ficam em `test-results/`, sem traces, HAR ou
storage state. Veja [convenções de testes](docs/conventions/testes.md).

O [workflow GitHub Actions](.github/workflows/testes.yml) usa Python 3.12,
Node 22 e MySQL 8 descartável com health check; executa cobertura backend com
os dois opt-ins, cobertura frontend, testes do servidor público e Chromium.
Preserva gates de 90%/85%, permissões mínimas e timeout.

### Checkpoint publicado e CI

Em 7 de novembro de 2026, o checkpoint
[`6f40f1303560cad908fbdd752fd0aaa4dd285b3b`](https://github.com/Matibas100/ProjetoSoftwarePE/commit/6f40f1303560cad908fbdd752fd0aaa4dd285b3b)
foi publicado na branch `main` e a
[execução 42337772001](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42337772001)
concluiu com sucesso para esse mesmo SHA. A evidência inclui a extensão de
privacidade e a preservação dos bytes dos termos no Windows. A aprovação se
refere somente àquela revisão; alterações posteriores, incluindo este alinhamento
documental local, dependem de sua própria validação e publicação.
Os relatórios arquivados preservam suas execuções originais. Publicação do código
e CI aprovado não comprovam hospedagem na AWS nem demonstração acadêmica do grupo.

## Validação antes do push

O comando `npm run hooks:install` configura o hook versionado de `pre-push`
para este clone do repositório. Antes de cada push, ele executa a suíte completa
do backend, incluindo as integrações no MySQL real, e depois a suíte completa
do frontend. O hook usa o Python da `.venv` quando disponível e informa
`RUN_MYSQL_INTEGRATION=1` somente ao processo do runner de backend.

Qualquer falha de teste, cobertura, dependência ou acesso ao MySQL interrompe o
push. Por isso, mantenha o ambiente preparado e o MySQL 8 em execução. Para
reinstalar o hook neste clone, execute novamente:

```powershell
npm run hooks:install
```

Registro histórico de validação no Windows em 7 de outubro de 2026 (não é a
execução atual; veja [relatório da consolidação](openspec/changes/archive/2026-11-06-consolidar-entrega-academica/validacao.md)):

- backend: **106 testes unitários + 58 integrações**, 95,54% de linhas e
  87,64% de branches;
- frontend: **48 testes**, 98,81% de linhas e 85,55% de branches;
- migrations `000` a `005`, APIs legadas, Stored Procedure, autenticação e APIs
  administrativas aprovadas no MySQL real;
- cadastro/login inspecionados em navegador a 1440/390 px; fluxos dos dois
  perfis e recuperação de sessão verificados em schema descartável.

Limitações: integrações e E2E exigem MySQL 8; Chromium complementa a suíte DOM.
Não há redesign mobile nesta consolidação. O projeto usa migrations SQL puro,
sem Alembic ou Flask-Migrate. A atividade anterior exige pelo menos vinte
funcionalidades completas e vídeo obrigatório de até cinco minutos. A rubrica
final recebida exige pelo menos quatro funcionalidades principais não CRUD,
demonstração de até dois minutos por vídeo ou execução hospedada e slides;
não exige demonstrar todas as vinte. Não se presume dispensa ou substituição
da entrega anterior, nem aplicação do cronograma de 2025 à turma de 2026.
Testes não substituem a demonstração do grupo nem garantem pontuação; consultas
isoladas não têm contagem garantida entre as quatro ações. Vídeo, slides e
hospedagem ficam a cargo do grupo. Veja a
[distinção das entregas](docs/technical/entrega-academica.md#entrega-externa).
Commit, push e merge dependem sempre de autorização explícita para a operação.
Esta limpeza não autoriza novas operações Git.

## Consultas acadêmicas por procedures

As seis consultas administrativas e de desempenho usam sete procedures de
leitura e quatro views históricas, pelas migrations 011/012. Contratos HTTP,
CRUD nas Models, permissões e transações permanecem. Veja
[assinaturas, caminhos e operação](docs/technical/consultas-academicas-mysql.md)
e o [ADR-011](docs/technical/adr/ADR-011-interfaces-sql-de-leitura.md).
O Catálogo editorial acrescenta quinze procedures na migration 013 para seletores,
impactos, locks, versões e elegibilidade. Práticas/Simulados acrescentam dezesseis
na migration 014 para propriedade, composição, retomada, históricos e fatos.
Plano acrescenta seis na 015 para geração atual/replay, itens, elegibilidade e
eliminação participante após negativa. Contas acrescenta onze na 016 para
identidade, sessões, limites, limpeza e decisões correntes de privacidade:
são 55 procedures novas e quatro views no conjunto 011–016, além da legada.
As [correspondências e a auditoria dos seis módulos](docs/technical/consultas-academicas-mysql.md#contas-e-privacidade--migration-016)
distinguem executores, projeções de compatibilidade e CRUD básico. Disponibilizar
o código somente após aplicar e validar a 016 no destino; os testes usam schemas
descartáveis. Este recorte não representa adequação acadêmica integral nem publicação.


## Tutor IA: revisão pontual com Gemini

Abra `/aluno/tutor.html` pela navegação do Aluno. Selecione Matéria/Assunto ativos,
escreva uma dúvida de 10–2000 caracteres e confirme **Enviar dúvida ao Gemini**.
Uso 2.0 precisa estar aceito na [privacidade](frontend/aluno/privacidade.html).
Plano recusado/revogado não bloqueia a tutoria. Atualizar uso não altera decisões
nem apaga planos; o plano exige uso vigente pela sua regra anterior.
[Uso 1.0](frontend/legal/termo-de-uso-v1.html) e consentimento do plano 1.0 permanecem
consultáveis, com bytes/hashes/evidências preservados.

Por padrão, o Tutor está desabilitado e a plataforma funciona sem chave. Instale
`backend/requirements.txt` (`requests==2.34.2`). O responsável configura somente
no ambiente do backend, antes de iniciar uma aplicação local:

```text
TUTOR_IA_ENABLED=true
GEMINI_API_KEY=<chave local; nunca no frontend ou no Git>
GEMINI_MODEL=gemini-3.6-flash
```

`.env.example` contém apenas placeholders. Não coloque chave em URL, logs, ativos,
testes ou capturas. As suítes comuns mantêm Tutor desabilitado e não recebem chave
real; transporte controlado existe somente nos testes unitários. Ativar pode
consumir quota/custo, inclusive se o navegador cancelar a espera.

### Contrato HTTP

`POST /api/tutoria`, JSON com **exatamente quatro strings**:

```json
{
  "disciplina": "Física",
  "nivel": "ensino_medio",
  "assunto": "Eletricidade",
  "duvida": "Qual é a diferença entre corrente elétrica e tensão?"
}
```

Disciplina: 1–100 caracteres; assunto: 1–150; dúvida: 10–2000, após trim.
Nível fixo `ensino_medio`, corpo até 16384 bytes. Somente Aluno com sessão válida,
Origin permitido, CSRF e uso vigente; autorização HTTP precede leitura do corpo.
Sucesso: 200 `{disciplina, assunto, resposta}`. `resposta` tem até 12000 caracteres,
com títulos únicos, ordenados e em linhas próprias:

1. `1. Explicação simples`
2. `2. Exemplo`
3. `3. Verifique sua compreensão`
4. `4. Exercício curto`

Cada seção tem conteúdo; a instrução pede exercício sem gabarito e português
compatível com ENEM. A prova real inclui conferência pedagógica do conteúdo, sem garantir a qualidade de respostas futuras.

| HTTP | Código / situação |
| --- | --- |
| 400 | `dados_invalidos`: corpo/campos inválidos, antes de qualquer consumo externo |
| 401/403 | Falhas existentes de sessão/perfil/Origin/CSRF |
| 409 | `termos_uso_pendentes`: aceitar uso na privacidade |
| 413 | `corpo_muito_grande`: limite exclusivo desta rota |
| 429 | `limite_tutoria`: limite local, com `Retry-After` em segundos |
| 503 | `tutor_indisponivel`: desabilitado, chave ou modelo ausentes |
| 502 | `tutor_timeout`, `tutor_provedor_indisponivel` ou `tutor_resposta_invalida` |
| 500 | `erro_interno`: erro sanitizado |

Erros usam `{erro,codigo}`, sem corpo/headers do provedor. Todas as respostas são
`no-store`. Não há resposta de estudo substituta nem repetição automática.

### Camadas, limites e dados

`Tela → Route → TutoriaController → GerarTutoriaService → GeminiService → Gemini`.
A Controller adapta HTTP e captura somente o ID primitivo. O caso de uso valida,
chama a permissão pública de Contas (uso vigente) e encerra sua leitura transacional
antes da rede, verifica configuração, reserva o limite e libera em `finally`.
`GeminiService` encapsula REST HTTPS fixo, chave no cabeçalho `x-goog-api-key`,
`store=false`, prompt estável, quatro campos como dados e até 4096 tokens de saída.
Extrai só texto final da última etapa `model_output` em `steps`, sem pensamentos
ou dependência da conveniência SDK `output_text`.

Timeouts Requests: conexão 5 s, leitura 30 s, que não representam prazo global;
corpo externo limitado a 1 MiB e resposta sempre fechada. Interface espera até
45 s e cancela localmente quando possível, sem garantir cancelamento no Gemini.
Limite atômico por aplicação/processo: quatro tentativas externas/60 s por conta,
uma em andamento por conta, duas globais e até 1024 contas em memória. Falhas
externas contam; reinício zera contadores e workers não compartilham limites.
Isso não é proteção distribuída de orçamento para produção.

Não há histórico, ferramentas, desempenho automático, persistência de conversa,
Model, Repository, tabela ou novo CRUD. Perguntas/respostas não entram em banco,
logs ou armazenamento do navegador. `store=false` não garante retenção operacional
zero pelo provedor; não envie dados pessoais. A demonstração usa dados sintéticos,
com contato fictício e proteção/autorização de menores ainda pendentes.

### Evidências e demonstração

[tutor.spec.js](frontend/e2e/tutor.spec.js) acrescenta E2E com MySQL descartável:
uso antigo, aceite 2.0, navegação, aviso e 503 real com Tutor desabilitado, sem
interceptação do Gemini. Os vinte casos anteriores seguem nos outros E2E.
Python/DOM controlados verificam timeout, formato, sanitização, concorrência e
ciclo de identidade; não comprovam acesso real ao provedor.

Para a aula: com ambiente local preparado, use a tela autenticada e uma dúvida
sintética. Confira as quatro partes, pertinência ao ENEM e ausência de gabarito.
Uma requisição autenticada com objeto vazio demonstra 400 antes do provedor;
o timeout é comprovado em unidade, sem alegar falha real observada no Gemini.
Registre somente data/modelo/status/checklist, sem dúvida/resposta, chave ou sessão.
A [validação desta change](openspec/changes/archive/2026-11-09-adicionar-tutor-revisao-com-gemini/validacao.md)
distingue esses testes da prova real. Em 09/11/2026, uma dúvida sintética enviada
pela interface retornou **HTTP 200**, com as quatro partes e exercício sem gabarito
conferidos. Cadastro/aceite/login/catálogo e envio usaram Chromium com MySQL
descartável, sem interceptação do Gemini; a entrada inválida retornou 400.
O modelo foi `gemini-3.6-flash`. Timeout permanece comprovado somente em unidade.
Também houve falhas externas/formato recusado em execuções manuais, tratadas como
502 sem retry automático. O relatório guarda apenas metadata/checklist, sem
payloads, chave ou captura de sessão. Sem chave/acesso/quota em outro ambiente,
a prova real precisa ser repetida nele.
O fluxo atende à consulta de LLM com Controller/Services e não aumenta a contagem
de CRUD ou substitui vídeo, slides ou entrega acadêmica anterior.
