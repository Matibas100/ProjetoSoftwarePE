# Operação do projeto

Este documento reúne os detalhes operacionais transferidos do [README](../../README.md).
Os contratos completos continuam nas operações de cada domínio; não é um novo
inventário de funcionalidades. Execute comandos somente no ambiente apropriado.
Credenciais ficam na configuração privada, nunca em SQL, argumentos ou documentação.

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
[matriz](entrega-academica.md). Contratos completos por domínio:
[Questões](operacao-questoes.md),
[Práticas](operacao-praticas.md),
[Simulados](operacao-simulados.md),
[Desempenho](operacao-desempenho.md) e
[Plano](operacao-plano-estudos.md).

O catálogo administrativo, suas migrations e a auditoria pré-upgrade estão
detalhados em [Operação do catálogo acadêmico](operacao-catalogo-academico.md).

No contrato legado, `QuestaoRepository` encapsula o `CALL sp_questoes_por_assunto`:
a procedure recebe `assunto_id`, filtra as Questões no MySQL e devolve o resultado
ordenado por `id`. O cadastro de Questão mantém CRUD na Model.

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
São verificações independentes. Consulte o [adendo ao ADR-001](adr/ADR-001-estrategia-de-migrations.md#22-adendo--assinatura-estrutural-portável-2026-11-07).

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

<a id="testes-e-atalhos-make"></a>

## Testes e comandos diretos

Execute os testes locais sob demanda, conforme os arquivos alterados. O push
não executa uma suíte local obrigatória; após o envio, o GitHub Actions executa
a validação automática descrita abaixo.

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

Os comandos diretos de testes e gates estão nas
[convenções de testes](../conventions/testes.md#comandos), conferidos contra os
runners Python e `package.json`. Os opt-ins devem ser informados explicitamente.

Os comandos de manutenção do banco exigem as mesmas precondições descritas acima:

| Finalidade | Comando direto |
| --- | --- |
| Consultar status | `python backend/database/migrate.py status` |
| Aplicar migrations | `python backend/database/migrate.py up` |
| Adotar banco existente | `python backend/database/migrate.py baseline --confirm` |
| Registrar reconciliação autorizada | `python backend/database/migrate.py reconcile 003 --confirm` |

No exemplo de reconciliação, `003` é a versão da migration reconciliada.

Os gates por stack são 90% de linhas e 85% de branches agregados, além de
reprovar qualquer arquivo executável zerado.

## Navegador e integração contínua

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
portas livres. A suíte contém **seis testes Playwright em seis arquivos**:
[entrega-academica.spec.js](../../frontend/e2e/entrega-academica.spec.js) preserva os vinte casos
numerados, navegação ao plano, cancelamento de descarte e capturas a 1440/390 px.
[plano-simulado.spec.js](../../frontend/e2e/plano-simulado.spec.js), com conta e conteúdo próprios,
verifica geração/conclusão manual do Plano, finalização/correção de Simulado e
recálculo confirmado, cancelamentos e persistência por recarga/GET real.
Confere 2/5 (40%) no plano inicial, 1/3 (33,33%) no resultado do Simulado e
3/7 (42,86%) no diagnóstico/novo plano; o branco não entra no diagnóstico.
Um replay HTTP auxiliar, identificado no teste e sem botão, verifica a geração
anterior preservada.
[privacidade.spec.js](../../frontend/e2e/privacidade.spec.js) cobre documentos públicos,
cadastro com aceite explícito, recusa mantendo estudo real, autorização do plano,
revogação com eliminação e nova autorização, incluindo outra aba aberta.
[catalogo-detalhe.spec.js](../../frontend/e2e/catalogo-detalhe.spec.js) verifica a
consulta atual de Matéria/Assunto durante a edição, inclusive outra aba.
[usuarios.spec.js](../../frontend/e2e/usuarios.spec.js) cobre gestão de Alunos, vínculos,
sessões e revisão 1440/390 px.
[tutor.spec.js](../../frontend/e2e/tutor.spec.js) cobre navegação, uso antigo, aceite 2.0
e 503 real com Tutor desabilitado; não consulta Gemini. Veja
[operação do Tutor](operacao-tutor-ia.md#evidências-e-demonstração).
A contagem atual foi obtida por leitura estática das declarações `test(...)`;
descoberta ou inventário não comprovam aprovação funcional.

`npm run test:e2e:list` apenas descobre os seis testes; não executa seus percursos
nem comprova aprovação. Nenhuma resposta é simulada. Esses passos adicionais não
alteram a contagem oficial de vinte funcionalidades. Processos/schema são
limpos em `finally`, mesmo após falha.
Relatórios e capturas sintéticas ficam em `test-results/`, sem traces, HAR ou
storage state. Veja [convenções de testes](../conventions/testes.md).

O [workflow GitHub Actions](../../.github/workflows/testes.yml) usa Python 3.12,
Node 22 e MySQL 8 descartável com health check; executa cobertura backend com
os dois opt-ins, cobertura frontend, testes do servidor público e Chromium.
Preserva gates de 90%/85%, permissões mínimas e timeout.

## Checkpoint publicado e CI

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

## Testes locais e clones antigos

O hook de `pre-push` foi aposentado. Os comandos de testes continuam disponíveis
sob demanda, e o GitHub Actions valida o código após o push. Acompanhe o resultado
da execução correspondente ao commit enviado; a validação pode falhar depois
que o GitHub já recebeu o código.

Se este clone usava o hook antigo, confira somente a configuração local:

```powershell
git config --local --get-all core.hooksPath
git config --show-origin --show-scope --get-all core.hooksPath
```

Somente se o valor local for `.githooks` (ou o caminho absoluto equivalente
à pasta deste projeto), e não houver outros hooks nessa pasta, remova a chave:

```powershell
git config --local --unset-all core.hooksPath
```

Se a chave local estiver ausente, não há nada a remover. Preserve valores que
apontem para outros diretórios e configurações globais. Confira novamente a
origem e o valor efetivo com o segundo comando; remover a chave local pode
revelar uma configuração global. Essa preferência não se propaga a outros clones.

### Visualização local no VS Code

Para reduzir o ruído no Explorer, crie ou mescle estas entradas em
`.vscode/settings.json`, preservando suas demais preferências e entradas de
`files.exclude`. O arquivo já é ignorado pelo Git; cada integrante pode adotar
essa visualização no próprio clone.

```json
{
  "files.exclude": {
    ".venv": true,
    "node_modules": true,
    "**/__pycache__": true,
    ".coverage": true,
    ".coverage.*": true,
    "coverage-backend.json": true,
    "coverage-frontend": true,
    "test-results": true
  }
}
```

Os arquivos continuam no disco e os testes continuam gerando seus relatórios.
Fontes, scripts e configurações do projeto permanecem visíveis. Para reverter,
remova somente essas entradas de `files.exclude` ou restaure seus valores
anteriores; preserve as demais preferências.

### Histórico de validação

O README de origem registrava validação no Windows em **7 de outubro de 2026**
com os números abaixo. São um relato herdado, preservado nesta transferência;
não são execução atual nem os resultados do
[relatório da consolidação de 06/11/2026](../../openspec/changes/archive/2026-11-06-consolidar-entrega-academica/validacao.md),
que registra outra execução (128 unitários + 114 integrações e 143 testes frontend).

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
Essa descrição de execução hospedada pertence ao relato anterior: o
[roteiro oficial atual](https://github.com/gleisonbt/RoteiroApresentacaoPS2026/blob/main/Roteiro_Apresentacao_Projeto_Rubrica.md)
admite demonstração com sistema em execução e separação frontend/API local;
hospedagem é bônus. Veja também a orientação atual no [README](../../README.md).
Testes não substituem a demonstração do grupo nem garantem pontuação; consultas
isoladas não têm contagem garantida entre as quatro ações. Vídeo, slides e
hospedagem ficam a cargo do grupo. Veja a
[distinção das entregas](entrega-academica.md#entrega-externa).
Commit, push e merge dependem sempre de autorização explícita para a operação.
Esta limpeza não autoriza novas operações Git.

## Consultas acadêmicas por procedures

As seis consultas administrativas e de desempenho usam sete procedures de
leitura e quatro views históricas, pelas migrations 011/012. Contratos HTTP,
CRUD nas Models, permissões e transações permanecem. Veja
[assinaturas, caminhos e operação](consultas-academicas-mysql.md)
e o [ADR-011](adr/ADR-011-interfaces-sql-de-leitura.md).
O Catálogo editorial acrescenta quinze procedures na migration 013 para seletores,
impactos, locks, versões e elegibilidade. Práticas/Simulados acrescentam dezesseis
na migration 014 para propriedade, composição, retomada, históricos e fatos.
Plano acrescenta seis na 015 para geração atual/replay, itens, elegibilidade e
eliminação participante após negativa. Contas acrescenta onze na 016 para
identidade, sessões, limites, limpeza e decisões correntes de privacidade:
são 55 procedures novas e quatro views no conjunto 011–016, além da legada.
As [correspondências e a auditoria dos seis módulos](consultas-academicas-mysql.md#contas-e-privacidade--migration-016)
distinguem executores, projeções de compatibilidade e CRUD básico.
Esse recorte histórico exige a 016 aplicada e validada; os testes usam schemas
descartáveis. A versão atual acrescenta a **017** para
[gestão administrativa de Alunos](gestao-administrativa-alunos.md).
Prepare o destino até a 017 antes de iniciar o código atual. O recorte 011–016
não representa adequação acadêmica integral nem comprova publicação.

