# Tasks — Organizar o backend em monólito modular

## 1. Baseline e núcleo compartilhado

- [x] 1.1 Registrar em `validacao.md` o estado atual, inventário arquivo → módulo, mapa completo de rotas/CLI, representação estrutural das 21 Models e hashes dos SQLs 000–010/bootstrap/HTMLs legais. Executar o baseline unitário e das integrações afetadas com configuração MySQL isolada/opt-ins existentes; verificar preservação do working tree, ausência de segredos e referência independente para comparação posterior.
- [x] 1.2 Extrair somente as bases, relógio, paginação e helpers neutros definidos no design para `app/core`, mantendo `extensions.py`/infraestrutura única e a ponte estática `app.models.crud_mixin`. Atualizar consumidores imediatos e os testes existentes de capacidades/validação; verificar identidade das bases/`db`, mensagens/normalização anteriores e unitários sem conexão MySQL ou `.env`.
- [x] 1.3 Criar o ADR-010 e iniciar `docs/technical/organizacao-modular.md` com os seis proprietários/interfaces e a transição; acrescentar em `backend/tests/unit/test_arquitetura_modular.py` as verificações de fronteira aplicáveis a cada módulo concluído e os invariantes de factory/metadata. Verificar que não se introduz ORM/container novo, que as exceções são estritas e que os testes não dependem de alterar comportamento para passar.

## 2. Conteúdo

- [x] 2.1 Mover catálogo e Questões para `modules/conteudo` conforme o inventário do design, preservando Models/capacidades, eventos, CRUD e Repositories especializados. Atualizar seus imports/patches e executar unitários e integrações reais de Matéria, Assunto, catálogo e versionamento, incluindo `CALL` no Repository; comparar os sete mapeamentos ao baseline e registrar propriedade/resultado no mapa e relatório.
- [x] 2.2 Criar Blueprint/rotas e API pública de Conteúdo, incluindo versões, elegibilidade, classificação histórica e contagens; remover seus registros equivalentes do arquivo central e adaptar consumidores por contrato/API, sem duplicar SQL nem exportar ORM/Repository. Verificar URLs/métodos/defaults equivalentes, ausência de duplicação de regras, fronteiras do módulo e regressão de consultas, permissões e locks; documentar as interfaces efetivas.

## 3. Práticas

- [x] 3.1 Mover Controller/Model/Repository/Services e rotas para `modules/praticas`, incluindo o catálogo de Questões do Aluno com a consulta de Conteúdo injetada. Publicar projeções de fatos/atividades sem acesso a persistência privada externa; adaptar imports/patches e verificar unitários, integrações reais, propriedade, replay, ausência de gabarito antecipado e correção histórica. Comparar mapa de rotas/Model e registrar entradas/saídas no mapa e relatório.

## 4. Simulados

- [x] 4.1 Mover gestão, execução, Models, consultas e rotas para `modules/simulados`; adaptar a dependência de Questões para a interface de Conteúdo e os helpers compartilhados para o núcleo. Verificar as sete Models sem duplicação, unitários e integrações reais de publicação/composição, início, resposta e finalização, preservando uma confirmação/rollback, revisões e histórico; documentar a propriedade e os resultados do grupo.
- [x] 4.2 Publicar as projeções/contagens de Simulados para Desempenho e conservar os contratos injetados de catálogo/histórico. Verificar regras de disponibilidade no Service, ausência de import privado de Conteúdo/Práticas, equivalência das rotas e resultados incluindo respostas em branco; registrar a API pública e testar as fronteiras do módulo.

## 5. Desempenho

- [x] 5.1 Mover diagnóstico/dashboards, consultas, Controller e rotas para `modules/desempenho`; trocar imports diretos de Repositories externos pelas projeções/APIs publicadas pelos donos. Verificar unitários, integrações MySQL, período UTC, classificação histórica, denominadores e snapshot consistente; manter o mesmo `DiagnosticoAluno` para o plano, sem Model/tabela nova, e atualizar mapa/relatório com as interfaces e evidências.

## 6. Contas e Plano, com transação preservada

- [x] 6.1 Mover autenticação/privacidade para `modules/contas` e o plano para `modules/plano_estudos`, com Models, Controllers, Services e rotas próprios. Deslocar o lock exato de usuário para Contas e expor a permissão do plano sem dependência de seus Models; verificar unitários, metadata 4+2 Models, mapa HTTP e proteções de perfil/origem/CSRF/cookie/versão antes de qualquer dado privado. Documentar propriedade e interfaces nos mesmos artefatos do grupo.
- [x] 6.2 Mover a eliminação especializada para o Repository/Service participante de Plano e injetá-la por construtor nas duas negativas de consentimento, pela composição. Acrescentar a regressão necessária e verificar em MySQL real o único commit/rollback, falha real de eliminação, lock de usuário comum, concorrência com geração, replay que não reaplica decisão e preservação de outra conta/respostas; confirmar ausência de imports cíclicos, commit interno e endpoint novo. Registrar a realocação que complementa o ADR-009.
- [x] 6.3 Adaptar hooks HTTP/cache, CLI e `PrivacidadeController` para os colaboradores de Contas e suas duas instâncias injetadas; verificar criação/cadastro com aceite atômico, login/logout/reauth, comandos existentes, recusa/revogação e nova autorização. Testar duas aplicações sem vazamento de estado/conexão/usuário na composição; atualizar mapa/relatório e preservar integralmente os contratos de consentimento/hash/documentos.

## 7. Consolidação da estrutura e documentação atual

- [x] 7.1 Consolidar os seis Blueprints na factory/agregador e o registro canônico das 21 Models; atualizar todos os consumidores internos, imports/alvos de patch de testes e o setup sintético de `scripts/run_e2e.py`. Remover implementações/passagens transitórias das pastas globais, mantendo somente as pontes delimitadas; verificar gate completo de arquitetura, duas factories independentes, mappers únicos, mapa HTTP/CLI equivalente e nenhuma referência funcional a caminhos removidos.
- [x] 7.2 Concluir o mapa modular/ADR-010 e atualizar README, índice de ADRs, conventions de estrutura/arquitetura, documentação operacional com paths, aplicação SOLID, matriz e diagrama. Acrescentar situação implementada ao plano mestre sem reescrever o roadmap/histórico; verificar links, mesmas 21 Models/vinte funcionalidades, responsabilidades por módulo e contexto YAML com `schema`/`rules`/`operations` preservados. Conferir que specs funcionais e artefatos Desktop V1 não mudaram.

## 8. Regressão integrada e fechamento

- [x] 8.1 Executar `python backend/tests/run_backend_coverage.py` com MySQL isolado e `RUN_MYSQL_INTEGRATION=1`/`RUN_MYSQL_MIGRATION_INTEGRATION=1` somente no processo; verificar regressão original/ampliada, gates 90% linhas/85% branches e nenhum arquivo executável sem cobertura. Executar testes existentes do servidor frontend e uma vez os três E2E pelo runner oficial com `RUN_MYSQL_E2E=1` e ambiente isolado; registrar comandos/resultados/limpeza reais, sem mocks de integração, vídeo, trace ou sessão exportada.
- [x] 8.2 Comparar rotas/Models/CLI, hashes protegidos e comportamentos ao baseline; executar validação OpenSpec estrita e `git diff --check`, revisar fronteiras/exports e o diff completo preservando alterações legítimas. Confirmar zero mudança de schema/SQL/frontend/HTML legal/dependência, nenhuma operação no banco operacional e ausência de pendência crítica; concluir `validacao.md` com o mapa final dos movimentos, limitações e evidências verificáveis.

## Workflow follow-up

- Verificar a implementação pelo workflow antes do arquivamento; esta change usa `skip_specs: true` e não possui delta funcional para sincronizar.
- Arquivar somente após todos os grupos concluídos e ausência de achados críticos.
- Commit, push, AWS, vídeo, slides e guia de estudo dependem de instruções posteriores; não são tarefas desta change.
