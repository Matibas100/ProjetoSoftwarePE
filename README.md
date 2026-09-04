# Plataforma ENEM

Projeto escolar de conclusão de curso para organizar matérias, assuntos e
questões do ENEM. A aplicação possui uma interface administrativa em HTML, CSS
e JavaScript que consome uma API Flask persistida em MySQL.

## Tecnologias utilizadas

- Python 3.10 ou mais recente
- Flask e Flask-CORS
- Flask-SQLAlchemy com SQLAlchemy 2
- PyMySQL
- MySQL Server 8.0
- HTML5, CSS3 e JavaScript sem framework
- `unittest` e `coverage.py` para testes Python
- Vitest, jsdom e cobertura V8 para testes do frontend

## Arquitetura

O fluxo obrigatório da aplicação é:

```text
Frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL
```

Controllers adaptam requisições e respostas HTTP. Cada Service representa um
caso de uso e concentra suas validações. As Models contêm o CRUD simples. O
Repository é reservado para a consulta especializada que chama a Stored
Procedure.

```text
Plataforma ENEM/
├── frontend/
│   ├── css/
│   ├── js/
│   └── index.html
└── backend/
    ├── app/                         pacote Python da aplicação Flask
    │   ├── controllers/             camada Controller
    │   ├── models/                  camada Model e CRUD simples
    │   ├── repositories/            consultas especializadas
    │   ├── services/                casos de uso
    │   ├── extensions.py            db compartilhado e CORS
    │   └── routes.py                registro das rotas
    ├── database/
    │   ├── migrate.py                   runner oficial de migrations SQL
    │   ├── migrations/
    │   └── create_database.sql
    ├── tests/
    ├── requirements.txt
    └── run.py
```

As quatro camadas exigidas pela disciplina estão dentro de `backend/app`
porque `app` é o pacote importável usado pela application factory do Flask.
Esse nível adicional apenas delimita o código da aplicação; `controllers`,
`models`, `repositories` e `services` continuam separados e dentro de
`backend`, enquanto `database/create_database.sql` permanece no local exigido.

## Funcionalidades Implementadas

1. Cadastrar matéria
2. Listar matérias
3. Atualizar matéria
4. Excluir matéria
5. Cadastrar assunto
6. Listar assuntos
7. Atualizar assunto
8. Excluir assunto
9. Cadastrar questão
10. Buscar questões por assunto

## Componentes implementados

Models:

- `Materia`: campos da matéria, relacionamentos, serialização e CRUD simples.
- `Assunto`: campos do assunto, vínculo com Matéria, serialização e CRUD simples.
- `Questao`: alternativas, resposta, dificuldade, vínculo com Assunto,
  serialização e CRUD simples.

Services de negócio:

- `CriarMateriaService`, `ListarMateriasService`,
  `AtualizarMateriaService` e `DeletarMateriaService`.
- `CriarAssuntoService`, `ListarAssuntosService`,
  `AtualizarAssuntoService` e `DeletarAssuntoService`.
- `CriarQuestaoService` e `BuscarQuestoesPorAssuntoService`.

Repository:

- `QuestaoRepository`: encapsula exclusivamente o `CALL` da consulta de
  questões por assunto. O cadastro de Questão não utiliza Repository.

Stored Procedure:

- `sp_questoes_por_assunto`: recebe `assunto_id`, filtra as questões no MySQL
  e devolve o resultado ordenado por `id`.

## Rotas da API

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
`DATABASE_URL` completa. Não coloque credenciais reais no `.env.example`.

O `.env` está listado no `.gitignore` e não deve ser enviado ao repositório.

## Criação e atualização do banco MySQL

As migrations oficiais são arquivos SQL em `backend/database/migrations/`.
`migrate.py` controla ordem, checksum SHA-256, lock e histórico na tabela
`schema_migrations`, sem Alembic ou Flask-Migrate.

O schema configurado deve existir antes do runner. Para uma instalação nova,
crie-o vazio com `utf8mb4_unicode_ci`, configure o `.env` e execute:

```powershell
python backend/database/migrate.py status
python backend/database/migrate.py up
```

`up` aplica `000`, `001` e `002` em ordem. Chamá-lo novamente não reexecuta
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
python -m http.server 5500 --directory frontend
```

Abra `http://127.0.0.1:5500`. As origens autorizadas podem ser alteradas por
`CORS_ORIGINS` no `.env`.

## Testes automatizados

Os testes unitários Python bloqueiam o `.env`, usam uma URL fictícia apenas
para inicializar o Flask e não abrem conexão. As 29 integrações originais
continuam no MySQL 8 real, sem mocks ou SQLite. O frontend usa jsdom sem
converter os quatro scripts clássicos para ES Modules.

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

Os gates por stack são 90% de linhas e 85% de branches agregados, além de
reprovar qualquer arquivo executável zerado.

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

Resultado validado no Windows em 2 de setembro de 2026:

- backend: **54 testes unitários + 30 integrações**, 100% de linhas e 99,02%
  de branches;
- frontend: **21 testes**, 99,39% de linhas e 85,19% de branches;
- `make test-unit`, `make test-integration`, `make test-backend`,
  `make test-frontend`, `make test-coverage` e `make test` aprovados;
- gates de linhas, branches e arquivo executável zerado verificados com
  simulações que reprovaram `make test-coverage` como esperado.

As 30 integrações preservam as 29 originais (7 de Matéria, 10 de Assunto e 12
de Questão) e acrescentam a ordenação da Stored Procedure. Limitações: jsdom
não substitui um navegador real e a suíte de integração exige MySQL 8 preparado.
