# Plataforma ENEM

Projeto escolar para alunos que estudam para o ENEM e para a equipe que organiza
Matérias, Assuntos e Questões. O frontend HTML/CSS/JavaScript consome uma API Flask
com MySQL. O recorte entregue inclui conteúdo versionado, práticas, simulados,
desempenho, plano básico de estudos e Tutor IA opcional.

## Recursos principais

Além dos cadastros, a plataforma permite:

- Publicar Questões com snapshot imutável e arquivá-las preservando o histórico.
- Responder práticas com correção persistida e consultar o próprio histórico.
- Publicar e executar Simulados de composição fixa, finalizar tentativas e receber correção.
- Gerar e recalcular um plano básico a partir do diagnóstico, com conclusão manual
  de itens. Depende de autorização e amostra suficiente; não é gerado por IA.
- Enviar uma dúvida de revisão ao Gemini e receber explicação, exemplo, pergunta
  de compreensão e exercício curto, quando o Tutor opcional estiver habilitado.

Há também catálogo administrativo com filtros/paginação, ciclo de vida e
transferência auditada; logout, reautenticação e dashboards. Recursos adicionais,
automação, CI e documentação não ampliam a lista oficial abaixo.

<a id="gestão-administrativa-de-alunos"></a>

A **gestão administrativa de Alunos**, em `/admin/usuarios.html`, permite criar,
buscar, consultar, editar, desativar/reativar e excluir contas sem vínculos.
Troca de e-mail/desativação revoga sessões; reativação exige novo login.
Exclusão vinculada retorna 409; desativação é distinta. Administradores não são alvos.
Criação usa senha inicial, sem sessão ou aceite em nome do titular.
Veja [contratos e operação](docs/technical/gestao-administrativa-alunos.md).

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

A [matriz dos vinte casos](docs/technical/entrega-academica.md#rastreabilidade-dos-vinte-casos)
liga cada item à tela, API, camadas, persistência e evidência. O MVP original
de dez funcionalidades permanece nesse conjunto. A lista não comprova aprovação
acadêmica nem CRUD integral: veja as restrições na
[matriz CRUD](docs/technical/matriz-crud.md), incluindo Models auxiliares,
exclusão sem vínculos e arquivamento com histórico.

## Tecnologias utilizadas

- **Backend:** Python 3.10+, Flask, Flask-CORS, Flask-SQLAlchemy/SQLAlchemy 2,
  PyMySQL e python-dotenv; Requests na integração opcional com Gemini.
- **Persistência:** MySQL Server 8.0 e migrations SQL com runner próprio,
  sem Alembic ou Flask-Migrate.
- **Frontend:** HTML5, CSS3 e JavaScript sem framework.
- **Testes:** unittest/coverage.py, Vitest/jsdom/cobertura V8 e Playwright/Chromium.

## Arquitetura

```text
Frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL
```

Controllers adaptam HTTP; cada Service concentra um caso de uso e suas validações.
Models mantêm CRUD simples; Repositories encapsulam consultas especializadas,
contagens, impacto, locks e todo `CALL`. Controllers/Services não executam SQL.

O backend usa application factory e sete módulos em `backend/app/modules/`:
`contas`, `conteudo`, `praticas`, `simulados`, `desempenho`, `plano_estudos` e
`tutor_ia`. As camadas ficam no módulo proprietário; colaboração ocorre por APIs
e contratos públicos. `core` contém bases/helpers neutros; composição e registro
ORM são exceções estritas às fronteiras. As 21 Models continuam preservadas;
Desempenho é projeção, sem tabela própria.

<a id="componentes-implementados"></a>

Veja o [mapa modular e seus componentes](docs/technical/organizacao-modular.md),
[modelagem de domínio](docs/technical/modelagem-de-dominio.md),
[diagrama das 21 Models](docs/technical/diagrama-de-classes.md) e
[SOLID](docs/technical/aplicacao-solid.md). As bases
`ModeloBase → ModeloAtualizavel → CrudMixin` oferecem capacidades compatíveis,
num caminho único desde `db.Model`; nove consultas recebem contratos por construtor,
ligados pela composição por aplicação.
As decisões estão nos [ADRs](docs/technical/adr/README.md), em especial
[008](docs/technical/adr/ADR-008-contratos-e-capacidades-de-persistencia.md),
[010](docs/technical/adr/ADR-010-organizacao-modular-do-backend.md) e
[011](docs/technical/adr/ADR-011-interfaces-sql-de-leitura.md).
A [arquitetura mestre](docs/technical/architecture-master-v1.md) distingue o recorte
implementado do roadmap.

<a id="consultas-acadêmicas-por-procedures"></a>

As [consultas acadêmicas MySQL](docs/technical/consultas-academicas-mysql.md)
documentam procedures/views e a auditoria dos módulos.
A [evolução histórica 011–016](docs/technical/operacao-do-projeto.md#consultas-acadêmicas-por-procedures)
é distinta da versão atual, que exige **017** para gestão de Alunos.

## Pré-requisitos

- Python 3.10+ e MySQL Server 8.0 em execução.
- Cliente `mysql` ou MySQL Workbench para criar o schema.
- Para testes do frontend: Node `>=22.9.0` e npm `11.6.2`.

## Preparação do ambiente

No PowerShell, a partir da raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
if (-not (Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
```

Configure privadamente `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` e `DB_PASSWORD`,
ou uma `DATABASE_URL` completa. Preserve um `.env` existente; ele é ignorado
pelo Git e não deve ser enviado ao repositório.
Configure `AUTH_SECRET_KEY` com 32 bytes aleatórios em 64 caracteres hexadecimais,
mantendo a mesma chave entre processos/reinícios.
Veja [configuração e geração segura](docs/technical/operacao-autenticacao-escolar.md#escopo-e-preparação).
Não use segredos reais no `.env.example`.

### Criação e atualização do banco MySQL

Para uma instalação nova, crie um schema **vazio** no MySQL/Workbench com o mesmo
nome de `DB_NAME` (ou da URL). Exemplo, se o nome escolhido for `plataforma_enem`:

```sql
CREATE DATABASE plataforma_enem CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Depois de configurar o ambiente, aplique as migrations oficiais:

```powershell
python backend/database/migrate.py status
python backend/database/migrate.py up
```

O schema deve existir antes do runner; `up` aplica `000`–`017` em ordem e não
reexecuta migrations aplicadas. Valide o histórico até **017** antes de iniciar
esta versão. Em ambiente operacional, faça e valide backup antes da atualização.

<a id="adoção-de-um-banco-mvp-existente"></a>
<a id="falhas-e-recuperação"></a>

Para banco existente ou instalação pelo snapshot `create_database.sql`, siga a
[adoção por baseline](docs/technical/operacao-do-projeto.md#adoção-de-um-banco-mvp-existente).
Falhas de DDL exigem inspeção e
[recuperação explícita](docs/technical/operacao-do-projeto.md#falhas-e-recuperação).
Detalhes do runner, privilégios, checksums e assinaturas estão na
[operação do banco](docs/technical/operacao-do-projeto.md#criação-e-atualização-do-banco-mysql).

## Executando o backend

Na raiz, com o ambiente virtual ativado e a configuração pronta:

```powershell
python backend\run.py
```

A API usa `http://127.0.0.1:5000` por padrão.

## Executando o frontend

Em outro terminal, na raiz:

```powershell
python scripts/serve_frontend.py
```

Abra **http://127.0.0.1:5500/login**. O servidor usa a biblioteca padrão do Python,
escuta em `127.0.0.1` e serve apenas `frontend/`.
Outra porta: `python scripts/serve_frontend.py --port 5501`; autorize a origem
`http://127.0.0.1:5501` em `CORS_ORIGINS` na configuração da API.

O cadastro em `/cadastro` cria somente Aluno, com aceite explícito de uso.
Administrador é criado pela
[CLI local documentada](docs/technical/operacao-autenticacao-escolar.md#contas-e-uso),
sem senha padrão. Gestão exige Administrador; leituras simples do catálogo exigem
login. `/index.html` permanece como MVP legado para Administrador.
Contratos de sucesso continuam disponíveis ao perfil autorizado.

## Testes automatizados

Os testes locais são executados sob demanda. Para preparar as ferramentas:

```powershell
python -m pip install -r backend\requirements-dev.txt
npm ci
```

Comandos básicos:

```powershell
python backend/tests/run_unit.py
npm run test:unit
npm run test:coverage
```

Os 29 testes de integração originais continuam na suíte ampliada. Integrações
exigem MySQL 8 real, schemas descartáveis e opt-ins somente no processo,
sem SQLite ou mocks. Unitários Python bloqueiam `.env` e não conectam ao banco;
os testes DOM usam jsdom. Gates por stack: 90% de linhas e 85% de branches,
sem arquivo executável zerado. Consulte [comandos e regras](docs/conventions/testes.md)
e [opt-ins de migrations e testes](docs/technical/operacao-do-projeto.md#testes-e-atalhos-make).

### Navegador e integração contínua

Há **seis testes E2E em seis arquivos**, verificados por leitura estática:
vinte casos, Plano/Simulado, Privacidade, Tutor desabilitado, detalhe do catálogo
e gestão de Alunos. Inventário/descoberta não comprova execução ou aprovação.
Preparação do Chromium, ambiente MySQL, limites e escopo de cada teste estão na
[operação E2E](docs/technical/operacao-do-projeto.md#navegador-e-integração-contínua).

O [GitHub Actions](.github/workflows/testes.yml) roda após push e em pull requests,
com Python 3.12, Node 22, MySQL 8 descartável, cobertura e Chromium.
O hook `pre-push` foi aposentado; push não exige suíte local obrigatória.
Acompanhe a execução correspondente ao SHA enviado.

### Checkpoint publicado e CI

O checkpoint `6f40f1303560cad908fbdd752fd0aaa4dd285b3b`, de 07/11/2026, tem
[registro de publicação e CI aprovado](docs/technical/operacao-do-projeto.md#checkpoint-publicado-e-ci).
Essa evidência cobre somente aquele SHA; não valida alterações locais posteriores,
hospedagem AWS ou apresentação acadêmica.

<a id="histórico-de-validação"></a>

Os [resultados históricos](docs/technical/operacao-do-projeto.md#histórico-de-validação)
mantêm datas, contagens e limites das evidências anteriores.

<a id="testes-locais-e-clones-antigos"></a>
<a id="visualização-local-no-vs-code"></a>

Veja [clones antigos e configuração local de hooks](docs/technical/operacao-do-projeto.md#testes-locais-e-clones-antigos)
e [preferências do Explorer no VS Code](docs/technical/operacao-do-projeto.md#visualização-local-no-vs-code).
São preferências de cada clone, preservando outras configurações e arquivos no disco.

## Tutor IA: revisão pontual com Gemini

Em `/aluno/tutor.html`, selecione Matéria/Assunto ativos e envie uma dúvida
sintética de 10–2000 caracteres. Exige Aluno autenticado e uso 2.0 aceito;
recusa/revogação do plano não bloqueia o Tutor. Atualizar uso não apaga planos
nem altera decisões; o plano continua exigindo uso vigente.
Por padrão, Tutor desabilitado: o restante da plataforma funciona sem chave.

<a id="contrato-http"></a>
<a id="camadas-limites-e-dados"></a>
<a id="evidências-e-demonstração"></a>

Veja [configuração opcional](docs/technical/operacao-tutor-ia.md#configuração-opcional),
[contrato HTTP](docs/technical/operacao-tutor-ia.md#contrato-http),
[limites e dados](docs/technical/operacao-tutor-ia.md#camadas-limites-e-dados) e
[evidências controladas e prova real de 09/11/2026](docs/technical/operacao-tutor-ia.md#evidências-e-demonstração).
Ativar pode consumir quota/custo; chave somente no backend, sem dados pessoais.
Não há conversa persistente nem novo CRUD. A prova anterior não garante acesso,
quota ou qualidade de respostas em outro ambiente.

## Documentação

<a id="consulta-individual-do-catálogo"></a>
<a id="rotas-legadas-da-api"></a>

| Assunto | Fonte |
| --- | --- |
| Casos, telas, camadas e evidências | [Matriz da entrega](docs/technical/entrega-academica.md) |
| Classes, atributos e relações | [Diagrama](docs/technical/diagrama-de-classes.md) e [modelagem](docs/technical/modelagem-de-dominio.md) |
| Fluxos de recuperação e entrada | [Diagnóstico e finalização de Simulado](docs/technical/fluxogramas-casos-de-uso.md) |
| CRUD e suas restrições | [Matriz CRUD](docs/technical/matriz-crud.md) |
| Contas e gestão de Alunos | [Autenticação](docs/technical/operacao-autenticacao-escolar.md) e [Alunos](docs/technical/gestao-administrativa-alunos.md) |
| Catálogo, detalhe e rotas legadas | [Catálogo](docs/technical/operacao-catalogo-academico.md), [consulta individual](docs/technical/operacao-do-projeto.md#consulta-individual-do-catálogo) e [rotas](docs/technical/operacao-do-projeto.md#rotas-legadas-da-api) |
| Contratos de estudo | [Questões](docs/technical/operacao-questoes.md), [Práticas](docs/technical/operacao-praticas.md), [Simulados](docs/technical/operacao-simulados.md), [Desempenho](docs/technical/operacao-desempenho.md) e [Plano](docs/technical/operacao-plano-estudos.md) |
| Banco, ferramentas e evidências | [Operação do projeto](docs/technical/operacao-do-projeto.md) |
| Tutor | [Operação do Tutor IA](docs/technical/operacao-tutor-ia.md) |
| Regras do projeto | [Conventions](docs/conventions/estrutura-do-projeto.md) e [workflow OpenSpec](docs/conventions/workflow-openspec.md) |

## Entrega acadêmica e limites

O [roteiro oficial](https://github.com/gleisonbt/RoteiroApresentacaoPS2026/blob/main/Roteiro_Apresentacao_Projeto_Rubrica.md)
prevê até sete minutos: cinco casos com telas e demonstração de pelo menos quatro
ações principais **não CRUD** em até dois minutos. A separação frontend/API pode
ser demonstrada localmente; hospedagem é bônus. Isso não dispensa automaticamente
o vídeo obrigatório de até cinco minutos da atividade anterior. Veja a
[distinção das entregas](docs/technical/entrega-academica.md#entrega-externa).
Slides, vídeo, hospedagem e demonstração ficam a cargo do grupo; consultas isoladas,
testes, documentação e CI não garantem aceite docente, pontuação ou hospedagem.
Não se presume aplicação do cronograma de 2025 à turma de 2026.

Os [Termos de Uso](frontend/legal/termo-de-uso-v2.html) e o
[Consentimento do plano](frontend/legal/termo-de-consentimento-plano-v1.html) são
completos, públicos e imprimíveis. O plano depende de autorização opcional posterior
em `/aluno/privacidade.html`; recusa/revogação confirmada elimina planos próprios
e conclusões, preservando questões, práticas, simulados e desempenho.
Nova autorização inicia outro plano sem restaurar o anterior.

Demonstração acadêmica com dados sintéticos. O responsável informado é Matheus
Gabriel Oliveira Martins; o contato `.example` é fictício e não operacional.
Antes de dados reais, definir canal válido, retenção/direitos e proteção/autorização
de menores. Não há adequação jurídica integral nem bônus garantido.
Veja [fontes e limites legais](docs/legal/README.md) e
[operação de privacidade](docs/technical/operacao-privacidade.md).
