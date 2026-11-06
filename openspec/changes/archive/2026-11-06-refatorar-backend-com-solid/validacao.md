# Validação: refatorar backend com SOLID

## Baseline em 06/11/2026

Preflight concluído: artefatos, AGENTS.md, cinco conventions, arquitetura mestre e ADRs
002, 003, 005 e 006. ADRs 001/004 consultados quanto a migrations e unicidade.
A consolidação acadêmica arquivada e suas melhorias locais sem commit são o baseline.
Nenhum reset, stash ou commit foi executado. Arquivo arquivado, tmp/, change vazia e
binários oficiais são preservados. baseline-sha256.json registra os hashes anteriores
à primeira edição, sem conteúdo de configuração sensível.

### Estado anterior

```text
 M .gitignore
 M Makefile
 M README.md
 M backend/app/auth_http.py
 M backend/app/controllers/area_enem_controller.py
 M backend/app/controllers/assunto_controller.py
 M backend/app/controllers/autenticacao_controller.py
 M backend/app/controllers/desempenho_controller.py
 M backend/app/controllers/materia_controller.py
 M backend/app/controllers/plano_estudo_controller.py
 M backend/app/controllers/pratica_controller.py
 M backend/app/controllers/questao_controller.py
 M backend/app/controllers/simulado_controller.py
 M backend/app/models/assunto.py
 M backend/app/repositories/catalogo_repository.py
 M backend/app/repositories/questao_repository.py
 M backend/app/repositories/simulado_repository.py
 M backend/app/services/consultar_simulado_service.py
 M backend/app/services/gestao_questao_service.py
 M backend/app/services/gestao_simulado_service.py
 M backend/app/services/listar_assuntos_service.py
 M backend/app/services/listar_questoes_aluno_service.py
 M backend/tests/test_catalogo_admin_integration.py
 M backend/tests/test_questoes_versionadas_integration.py
 M backend/tests/test_simulados_integration.py
 M backend/tests/unit/test_services.py
 M docs/conventions/testes.md
 M docs/technical/operacao-autenticacao-escolar.md
 M docs/technical/operacao-catalogo-academico.md
 M docs/technical/operacao-questoes.md
 M docs/technical/operacao-simulados.md
 M frontend/admin/assuntos.html
 M frontend/admin/dashboard.html
 M frontend/admin/materias.html
 M frontend/admin/questao.html
 M frontend/admin/questoes.html
 M frontend/admin/simulado.html
 M frontend/admin/simulados.html
 M frontend/aluno/desempenho.html
 M frontend/aluno/historico.html
 M frontend/aluno/inicio.html
 M frontend/aluno/plano.html
 M frontend/aluno/questao.html
 M frontend/aluno/questoes.html
 M frontend/aluno/simulado.html
 M frontend/aluno/simulados.html
 M frontend/css/auth.css
 M frontend/tests/admin-pages.test.js
 M frontend/tests/aluno-plano.test.js
 M frontend/tests/aluno-praticas.test.js
 M frontend/tests/auth.test.js
 M frontend/tests/coverage-validator.test.js
 M frontend/tests/desempenho.test.js
 M frontend/tests/simulados.test.js
 M openspec/specs/plano-estudos-basico/spec.md
 M package-lock.json
 M package.json
?? .github/
?? backend/app/http_response.py
?? backend/tests/unit/test_e2e_runner.py
?? backend/tests/unit/test_http_response.py
?? docs/technical/diagrama-de-classes.md
?? docs/technical/entrega-academica.md
?? frontend/e2e/
?? frontend/js/navigation.js
?? frontend/tests/navigation.test.js
?? openspec/changes/archive/2026-11-06-consolidar-entrega-academica/
?? openspec/changes/mover-join-assuntos-para-repository/
?? openspec/changes/refatorar-backend-com-solid/
?? playwright.config.js
?? scripts/run_e2e.py
?? tmp/
```

### Diffs preexistentes (adi??es/remo??es por arquivo versus HEAD)

```text
5	0	.gitignore
4	1	Makefile
89	30	README.md
3	2	backend/app/auth_http.py
3	10	backend/app/controllers/area_enem_controller.py
4	12	backend/app/controllers/assunto_controller.py
5	8	backend/app/controllers/autenticacao_controller.py
4	9	backend/app/controllers/desempenho_controller.py
4	12	backend/app/controllers/materia_controller.py
4	11	backend/app/controllers/plano_estudo_controller.py
4	11	backend/app/controllers/pratica_controller.py
5	9	backend/app/controllers/questao_controller.py
4	11	backend/app/controllers/simulado_controller.py
2	9	backend/app/models/assunto.py
11	0	backend/app/repositories/catalogo_repository.py
19	0	backend/app/repositories/questao_repository.py
29	0	backend/app/repositories/simulado_repository.py
21	14	backend/app/services/consultar_simulado_service.py
19	0	backend/app/services/gestao_questao_service.py
7	3	backend/app/services/gestao_simulado_service.py
2	1	backend/app/services/listar_assuntos_service.py
1	2	backend/app/services/listar_questoes_aluno_service.py
26	0	backend/tests/test_catalogo_admin_integration.py
9	0	backend/tests/test_questoes_versionadas_integration.py
65	0	backend/tests/test_simulados_integration.py
16	2	backend/tests/unit/test_services.py
24	0	docs/conventions/testes.md
10	0	docs/technical/operacao-autenticacao-escolar.md
6	0	docs/technical/operacao-catalogo-academico.md
11	0	docs/technical/operacao-questoes.md
11	0	docs/technical/operacao-simulados.md
2	17	frontend/admin/assuntos.html
2	17	frontend/admin/dashboard.html
2	17	frontend/admin/materias.html
2	17	frontend/admin/questao.html
2	17	frontend/admin/questoes.html
2	17	frontend/admin/simulado.html
2	17	frontend/admin/simulados.html
2	2	frontend/aluno/desempenho.html
2	2	frontend/aluno/historico.html
2	2	frontend/aluno/inicio.html
2	7	frontend/aluno/plano.html
2	2	frontend/aluno/questao.html
2	2	frontend/aluno/questoes.html
2	2	frontend/aluno/simulado.html
2	2	frontend/aluno/simulados.html
2	0	frontend/css/auth.css
1	0	frontend/tests/admin-pages.test.js
2	2	frontend/tests/aluno-plano.test.js
1	1	frontend/tests/aluno-praticas.test.js
1	1	frontend/tests/auth.test.js
1	1	frontend/tests/coverage-validator.test.js
1	1	frontend/tests/desempenho.test.js
5	0	frontend/tests/simulados.test.js
23	0	openspec/specs/plano-estudos-basico/spec.md
46	0	package-lock.json
4	1	package.json
```


## Caracterização inicial (tarefa 1.2)

- python backend/tests/run_unit.py: **128 testes aprovados**, sem banco (0,989 s).
- Preflight: **MySQL 8.0.44 disponível**, privilégio para criar schemas confirmado.
- RUN_MYSQL_INTEGRATION=1 e RUN_MYSQL_MIGRATION_INTEGRATION=1 somente no processo:
  python backend/tests/run_integration.py: **114 testes aprovados**, 246,513 s,
  incluindo 29 originais e migrations. Schemas descartáveis, sem SQLite/mocks.

As nove consultas iniciais eram estáticas. A suíte caracteriza filtros/paginação/contagens
administrativos; Questões por Assunto 400/404 e conteúdo seguro do Aluno; disponibilidade,
histórico e propriedade de Simulados; fórmula/UTC/amostra e snapshot compartilhado de
desempenho/dashboard/plano. Modelos inicialmente herdavam CRUD completo, com guards ORM
para snapshots/eventos/planos. O processo de integração iniciou antes da extração e
carregou os módulos originais. Estes resultados são o baseline, não a regressão final.

## Tarefa 2.1

Extraídas as três bases abstratas. **130 unitários aprovados** (0,821 s), incluindo falha de
flush sem rollback interno. DDL compilado MySQL e índices iguais ao baseline: 20 tabelas,
20 mappers, sem novas colunas/constraints/índices. Ciclos de FKs já existiam no baseline.
Diagrama e ADR-008 atualizados.

## Tarefas 2.2 e 2.3

Cinco snapshots/eventos migrados para ModeloBase; planos para ModeloAtualizavel.
Guardas ORM preservados. Primeiro teste focado de Questão apontou uma asserção antiga
não migrada; corrigida para ausência da capacidade e recusa de exclusão ORM.
Nova execução: **1 teste Questão aprovado** (4,603 s); teste de Simulado aprovado na
primeira execução (o outro dos dois focados). Suíte completa de plano: **9 aprovados**
(21,108 s), incluindo geração, recálculo, replays, concorrência, snapshot e rollback.
Unitários após a migração: **131 aprovados** (0,354 s).


## Tarefas 3.1, 3.2, 4.1 e 4.2

Criados contratos por domínio, registros nomeados e contexto opaco sem infraestrutura.
Composição por aplicação registrada pela factory, sem conexão/identidade capturada;
acesso corrente restrito a HTTP. Convertidas duas consultas de catálogo e Controllers.
Dois adaptadores unitários intercambiáveis exercitam filtros, página, ordenação e vazio;
a substituição explícita numa aplicação preserva a outra.

- python backend/tests/run_unit.py: **135 aprovados** (0,889 s).
- Integração focada tests.test_catalogo_admin_integration com opt-in: **7 aprovados**
  (5,017 s), MySQL real. Cobrem autorização, filtros, paginação, contagens, campos e CRUD.
- Contratos independentes conferidos por AST; nenhum import Flask/ORM/Model/Repository.
- Documentados contratos, composição e exemplos DIP/OCP; diagrama recebe ligações reais.


## Tarefas 5.1 e 5.2

Convertidas consultas de Questões para dependências obrigatórias, com adaptadores de registros
seguros e existência ligada ao Active Record na composição; migrados Controllers/consumidores.
Integração focada: tests.test_materias_integration, test_assuntos_integration,
test_questoes_integration, test_questoes_versionadas_integration e test_praticas_integration:
**45 aprovados** (32,331 s), incluindo as 29 originais, filtros, status, 400/404, ausência de
correção antecipada, elegibilidade e versões. CALL e procedimento preservados.


## Tarefas 6.1, 6.2, 7.1, 7.2 e 7.3

Convertidos catálogo/histórico de Simulados com registros e lotes, diagnóstico e dois
dashboards por contratos; plano recebe diagnóstico/seletor compostos. O mesmo diagnóstico
é compartilhado, sem resolver composição no Service ou fechar contexto externo.

- tests.test_simulados_integration: **13 aprovados** (24,819 s), incluindo privacidade,
  disponibilidade, histórico, correção/detalhe e quantidade constante de SELECTs.
- tests.test_desempenho_integration + tests.test_planos_integration: **20 aprovados**
  (43,034 s), incluindo snapshots, relógio, contexto externo, rollback e concorrência.
- python backend/tests/run_unit.py: **142 aprovados** (0,692 s), incluindo alternativas
  de métricas, simulado disponível/retirado/vazio, histórico, composição e análise estrutural.
- Corrigida expectativa de novo teste unitário: filtro opcional materia_id é None;
  isso preserva a normalização anterior. Não houve alteração de contrato para satisfazê-lo.
- Documentados SRP/DIP/ISP, formatos, ligações, escopo do plano e limites das escritas.


## Tarefas 8.1, 8.2 e 9.1

README, matriz dos vinte casos, documentação SOLID, ADR-008/índice e referências normativas
atualizados. Nenhuma reescrita dos ADRs históricos. Os dez blocos Mermaid foram renderizados
em PNG e inspecionados: bases, quatro visões de domínio e cinco visões da aplicação.
Comando mmdc via CLI em cache, com -i docs/technical/diagrama-de-classes.md,
-o test-results/solid/diagrama.md -e png -b white -p test-results/solid/puppeteer.json.
A primeira tentativa exigiu criar a pasta de saída; a seguinte não achou o browser padrão
do Puppeteer. Configurado o Chromium já instalado pelo Playwright, sem nova dependência.
Renderização final: **10/10 diagramas**, sem cortes/sobreposições de texto. Imagens locais
em test-results/solid/. Links relativos da documentação revisada: válidos.

Análise estrutural (test_composition.py) verifica as nove classes: construtores obrigatórios,
imports sem infraestrutura e ausência de current_app/db. Inspeção dos Controllers confirma
uso do acessor HTTP, sem SQL/sessão; busca de CALL/SELECT nas nove consultas não encontrou
SQL. Alternativas de catálogo/métricas exercitam comportamento, paginação e substituição.
Composição compartilha diagnóstico/escopos na mesma aplicação e isola duas factories.

Comparação final de DDL MySQL/índices versus baseline: **20 Models/tabelas compatíveis**.
Manifesto identificou 41 arquivos anteriores alterados nesta aplicação (lista em
diff-baseline.json), além dos contratos, composição, adaptadores, testes e documentos novos.
Hashes preservados: database/migrations/procedure, frontend, Desktop V1, specs principais,
change vazia, tmp/ e change acadêmica arquivada. Diferenças preexistentes versus HEAD estão
registradas separadamente no início; não são atribuídas à refatoração SOLID.


## Tarefa 9.2: regressão completa em 06/11/2026

| Execução | Resultado |
| --- | --- |
| RUN_MYSQL_INTEGRATION=1 RUN_MYSQL_MIGRATION_INTEGRATION=1 python backend/tests/run_backend_coverage.py (opt-ins só no processo) | **142 unitários + 115 integrações aprovados**, integrações 253,591 s; 29 originais e migrations incluídas |
| Gate backend | **97,48% linhas (3591/3684), 91,33% branches (811/888)**; nenhum arquivo executável zerado |
| npm run test:coverage | **99,21% linhas (1750/1764), 88,19% branches (1202/1363)**; gate aprovado sem arquivo executável zerado |
| python -m unittest discover -s scripts/tests -v | **7 aprovados** (1,798 s) |
| RUN_MYSQL_E2E=1 python scripts/run_e2e.py | **1 teste Playwright aprovado com vinte percursos**, 19,7 s; API/MySQL reais, schema removido |

Runner E2E recebeu configuração no ambiente do processo pelo loader normal, sem exibição
ou persistência de credenciais. Chromium real; sem mocks, SQLite, HAR, traces ou sessão
exportada. Relatório test-results/e2e.json e capturas sintéticas locais. Gates exigidos
90% de linhas/85% branches atendidos nas duas stacks. CI remoto segue pendente de push.


## Tarefa 9.3: verificação OpenSpec

Aplicada a skill openspec-verify-change para refatorar-backend-com-solid; status e
instruções apply consultados, proposta/design/tasks comparados com código e evidências.
Não há delta funcional (skip_specs: true). Os sete critérios técnicos do design estão
representados na implementação e nos testes executados.

| Dimensão | Resultado |
| --- | --- |
| Completude | Nove consultas convertidas, consumidores/plano migrados, três capacidades de persistência e documentação entregues; 21/21 tarefas concluídas ao registrar esta verificação |
| Correção | 142 unitários, 115 integrações MySQL, 143 testes frontend, 7 do servidor e vinte percursos Playwright aprovados; gates 90%/85% atendidos |
| Coerência | Contratos pequenos sem infraestrutura; composição por aplicação; CRUD convencional preservado; snapshot/imutabilidade/transações mantidos; banco/procedure/frontend oficial preservados |

**CRÍTICO: nenhum. AVISO bloqueante: nenhum.** A verificação apontou somente linha em
branco adicional no EOF de crud_mixin.py; removida, sem mudança executável. git diff --check
passou depois da correção. openspec validate refatorar-backend-com-solid --strict:
**válida**, com informação esperada sobre skip_specs e ausência de deltas.

O relatório registra resultados desta sessão, separados dos históricos da consolidação.
Logs brutos movidos para test-results/solid/ (ignorados); os resumos permanentes ficam aqui.
Lista de arquivos anteriores alterados em diff-baseline.json; novos arquivos de implementação
em arquivos-novos.json; hashes iniciais e DDL em baseline-sha256.json/baseline-metadados.json.
Alterações de código são somente as capacidades, nove consultas, composição e consumidores
necessários. Alterações legítimas anteriores foram preservadas, sem reset/stash/commit.

## Fechamento local e próximos passos

- Sincronização de specs: **não aplicável**, skip_specs: true, nenhum delta funcional;
  specs principais preservadas por hash.
- Change arquivada em 06/11/2026 por openspec-archive-change, via CLI
  `openspec archive refatorar-backend-com-solid --yes --json`, em
  `openspec/changes/archive/2026-11-06-refatorar-backend-com-solid/`.
  Artefatos completos, 21/21 tarefas concluídas, sem deltas a sincronizar.
  Links externos da documentação atualizados para o destino arquivado.
- Commit, push, merge, execução remota de CI e envio da atividade não foram realizados.
  Publicação depende de autorização explícita; vídeo e envio do link são do usuário.
- Credenciais não foram registradas, exibidas ou persistidas em artefatos. Arquivos .env
  não foram inspecionados; o loader normal configurou os processos de teste sem imprimir valores.
