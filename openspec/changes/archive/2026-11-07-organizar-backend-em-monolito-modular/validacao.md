# Validação — Organizar o backend em monólito modular

Baseline capturado em 07/11/2026 antes de alterar código de produção.
Estado inicial: somente esta change e `tmp/` não rastreados; arquivos rastreados sem alterações.
Referência independente: cópia dos arquivos rastreados e SHA-256 em `tmp/modular-baseline/files/`
e `tracked-hashes.json`; HEAD em `git-head.txt`. Nenhum `.env` foi lido/copiado pela captura.

[`baseline.json`](baseline.json) contém o mapa completo de 68 rotas (inclui static), métodos,
conversores, defaults, strict-slashes, redirecionamento, endpoint e função, dois comandos CLI,
as 21 Models (colunas/tipos/defaults/constraints/índices/relacionamentos/capacidades),
os seis guards ORM e 14 hashes protegidos (SQLs 000–010, bootstrap e dois HTMLs legais).
Busca inicial por `url_for`/`request.endpoint` em backend/scripts: nenhuma referência.
Configuração sintética para captura/unitários, com dotenv desabilitado e sem conexão.

MySQL 8.0.44 descartável: processo próprio em loopback:33381, dados em `tmp/modular-baseline/mysql-data`.
Credencial aleatória somente no temporário local, nunca no relatório. Runner temporário injeta
configuração/opt-ins apenas nos subprocessos e desabilita dotenv. Integrações criam/limpam
schemas com prefixos validados. Nenhuma operação usa o banco operacional.

## Baseline dos testes

- `python backend/tests/run_unit.py`: 166 testes, OK (5,134 s), log `tmp/modular-baseline/unit.log`.
- `python tmp/modular-baseline/run.py python backend/tests/run_integration.py`: 136 testes, OK (586,674 s), log `tmp/modular-baseline/integration.log`.

## Inventário arquivo → destino canônico

Prefixo comum: `backend/app/`. Núcleo e ponte das bases serão extraídos sem redefinição.

| Arquivo atual | Destino |
| --- | --- |
| `auth_cli.py` | `modules/contas/auth_cli.py` |
| `auth_http.py` | `modules/contas/auth_http.py` |
| `controllers/area_enem_controller.py` | `modules/conteudo/controllers/area_enem_controller.py` |
| `controllers/assunto_controller.py` | `modules/conteudo/controllers/assunto_controller.py` |
| `controllers/autenticacao_controller.py` | `modules/contas/controllers/autenticacao_controller.py` |
| `controllers/desempenho_controller.py` | `modules/desempenho/controllers/desempenho_controller.py` |
| `controllers/health_controller.py` | `core/controllers/health_controller.py` |
| `controllers/materia_controller.py` | `modules/conteudo/controllers/materia_controller.py` |
| `controllers/plano_estudo_controller.py` | `modules/plano_estudos/controllers/plano_estudo_controller.py` |
| `controllers/pratica_controller.py` | `modules/praticas/controllers/pratica_controller.py` |
| `controllers/privacidade_controller.py` | `modules/contas/controllers/privacidade_controller.py` |
| `controllers/questao_controller.py` | `modules/conteudo/controllers/questao_controller.py` |
| `controllers/simulado_controller.py` | `modules/simulados/controllers/simulado_controller.py` |
| `domain/autenticacao.py` | `modules/contas/domain/autenticacao.py` |
| `domain/catalogo.py` | `modules/conteudo/domain/catalogo.py` |
| `domain/privacidade.py` | `modules/contas/domain/privacidade.py` |
| `models/area_enem.py` | `modules/conteudo/models/area_enem.py` |
| `models/assunto.py` | `modules/conteudo/models/assunto.py` |
| `models/assunto_transferencia.py` | `modules/conteudo/models/assunto_transferencia.py` |
| `models/auth_limite.py` | `modules/contas/models/auth_limite.py` |
| `models/crud_mixin.py` | `core/persistencia.py` |
| `models/materia.py` | `modules/conteudo/models/materia.py` |
| `models/plano_estudo.py` | `modules/plano_estudos/models/plano_estudo.py` |
| `models/pratica_tentativa.py` | `modules/praticas/models/pratica_tentativa.py` |
| `models/questao.py` | `modules/conteudo/models/questao.py` |
| `models/questao_evento.py` | `modules/conteudo/models/questao_evento.py` |
| `models/questao_versao.py` | `modules/conteudo/models/questao_versao.py` |
| `models/registro_privacidade.py` | `modules/contas/models/registro_privacidade.py` |
| `models/sessao.py` | `modules/contas/models/sessao.py` |
| `models/simulado.py` | `modules/simulados/models/simulado.py` |
| `models/usuario.py` | `modules/contas/models/usuario.py` |
| `repositories/autenticacao_repository.py` | `modules/contas/repositories/autenticacao_repository.py` |
| `repositories/catalogo_repository.py` | `modules/conteudo/repositories/catalogo_repository.py` |
| `repositories/consultas_catalogo.py` | `modules/conteudo/repositories/consultas_catalogo.py` |
| `repositories/consultas_desempenho.py` | `modules/desempenho/repositories/consultas_desempenho.py` |
| `repositories/consultas_questoes.py` | `modules/conteudo/repositories/consultas_questoes.py` |
| `repositories/consultas_simulados.py` | `modules/simulados/repositories/consultas_simulados.py` |
| `repositories/desempenho_repository.py` | `modules/desempenho/repositories/desempenho_repository.py` |
| `repositories/plano_estudo_repository.py` | `modules/plano_estudos/repositories/plano_estudo_repository.py` |
| `repositories/pratica_repository.py` | `modules/praticas/repositories/pratica_repository.py` |
| `repositories/privacidade_repository.py` | `modules/contas/repositories/privacidade_repository.py` |
| `repositories/questao_repository.py` | `modules/conteudo/repositories/questao_repository.py` |
| `repositories/simulado_repository.py` | `modules/simulados/repositories/simulado_repository.py` |
| `services/aceitar_termos_uso_service.py` | `modules/contas/services/aceitar_termos_uso_service.py` |
| `services/alterar_status_catalogo_service.py` | `modules/conteudo/services/alterar_status_catalogo_service.py` |
| `services/atualizar_assunto_service.py` | `modules/conteudo/services/atualizar_assunto_service.py` |
| `services/atualizar_materia_service.py` | `modules/conteudo/services/atualizar_materia_service.py` |
| `services/autenticacao_service.py` | `modules/contas/services/autenticacao_service.py` |
| `services/buscar_questoes_por_assunto_service.py` | `modules/conteudo/services/buscar_questoes_por_assunto_service.py` |
| `services/catalogo_validacao.py` | `modules/conteudo/services/catalogo_validacao.py` |
| `services/concluir_plano_item_service.py` | `modules/plano_estudos/services/concluir_plano_item_service.py` |
| `services/consentir_plano_service.py` | `modules/contas/services/consentir_plano_service.py` |
| `services/consultar_desempenho_service.py` | `modules/desempenho/services/consultar_desempenho_service.py` |
| `services/consultar_plano_service.py` | `modules/plano_estudos/services/consultar_plano_service.py` |
| `services/consultar_pratica_service.py` | `modules/praticas/services/consultar_pratica_service.py` |
| `services/consultar_privacidade_service.py` | `modules/contas/services/consultar_privacidade_service.py` |
| `services/consultar_simulado_service.py` | `modules/simulados/services/consultar_simulado_service.py` |
| `services/consultar_termos_service.py` | `modules/contas/services/consultar_termos_service.py` |
| `services/criar_assunto_service.py` | `modules/conteudo/services/criar_assunto_service.py` |
| `services/criar_materia_service.py` | `modules/conteudo/services/criar_materia_service.py` |
| `services/criar_questao_service.py` | `modules/conteudo/services/criar_questao_service.py` |
| `services/dashboard_service.py` | `modules/desempenho/services/dashboard_service.py` |
| `services/deletar_assunto_service.py` | `modules/conteudo/services/deletar_assunto_service.py` |
| `services/deletar_materia_service.py` | `modules/conteudo/services/deletar_materia_service.py` |
| `services/desempenho_validacao.py` | `modules/desempenho/services/desempenho_validacao.py` |
| `services/finalizar_simulado_service.py` | `modules/simulados/services/finalizar_simulado_service.py` |
| `services/gerar_plano_service.py` | `modules/plano_estudos/services/gerar_plano_service.py` |
| `services/gestao_questao_service.py` | `modules/conteudo/services/gestao_questao_service.py` |
| `services/gestao_simulado_service.py` | `modules/simulados/services/gestao_simulado_service.py` |
| `services/health_check_service.py` | `core/services/health_check_service.py` |
| `services/impacto_catalogo_service.py` | `modules/conteudo/services/impacto_catalogo_service.py` |
| `services/iniciar_pratica_service.py` | `modules/praticas/services/iniciar_pratica_service.py` |
| `services/iniciar_simulado_service.py` | `modules/simulados/services/iniciar_simulado_service.py` |
| `services/listar_areas_enem_service.py` | `modules/conteudo/services/listar_areas_enem_service.py` |
| `services/listar_assuntos_service.py` | `modules/conteudo/services/listar_assuntos_service.py` |
| `services/listar_catalogo_admin_service.py` | `modules/conteudo/services/listar_catalogo_admin_service.py` |
| `services/listar_historico_simulados_service.py` | `modules/simulados/services/listar_historico_simulados_service.py` |
| `services/listar_materias_service.py` | `modules/conteudo/services/listar_materias_service.py` |
| `services/listar_praticas_service.py` | `modules/praticas/services/listar_praticas_service.py` |
| `services/listar_questoes_aluno_service.py` | `modules/praticas/services/listar_questoes_aluno_service.py` |
| `services/listar_simulados_aluno_service.py` | `modules/simulados/services/listar_simulados_aluno_service.py` |
| `services/paginacao.py` | `core/paginacao.py` |
| `services/plano_validacao.py` | `modules/plano_estudos/services/plano_validacao.py` |
| `services/pratica_validacao.py` | `modules/praticas/services/pratica_validacao.py` |
| `services/privacidade_validacao.py` | `modules/contas/services/privacidade_validacao.py` |
| `services/recalcular_plano_service.py` | `modules/plano_estudos/services/recalcular_plano_service.py` |
| `services/recusar_consentimento_plano_service.py` | `modules/contas/services/recusar_consentimento_plano_service.py` |
| `services/responder_pratica_service.py` | `modules/praticas/services/responder_pratica_service.py` |
| `services/responder_simulado_service.py` | `modules/simulados/services/responder_simulado_service.py` |
| `services/revogar_consentimento_plano_service.py` | `modules/contas/services/revogar_consentimento_plano_service.py` |
| `services/selecionar_plano_service.py` | `modules/plano_estudos/services/selecionar_plano_service.py` |
| `services/simulado_validacao.py` | `modules/simulados/services/simulado_validacao.py` |
| `services/transferir_assunto_service.py` | `modules/conteudo/services/transferir_assunto_service.py` |
| `services/validar_permissao_plano_service.py` | `modules/contas/services/validar_permissao_plano_service.py` |


## Núcleo e decisão (1.2–1.3)
Bases/relógio/paginação/validação pura extraídos; ponte estática mantém identidade de classes e db. ADR-010 e mapa modular iniciados, gate progressivo de fronteiras/factory/metadata acrescentado. Unitários: 172 OK (unit-core-final.log). Comparação independente: 21 Models, seis guards, 68 rotas, dois comandos e 14 hashes idênticos. Nenhum ORM, container ou conexão foi introduzido.


## Conteúdo (2.1–2.2)
33 arquivos canônicos em modules/conteudo; sete Models e suas capacidades/guards preservados. Blueprint sem prefixo novo. API de versões, pares, classificação histórica e contagens descrita no mapa modular; consumidores não importam persistência privada. Unitários: 172 OK (unit-conteudo-final.log). Integrações reais: 45 OK, 38,777 s (integration-conteudo.log), incluindo os 29 originais e CALL/versionamento. Comparação estrutural completa idêntica, permitindo apenas namespace interno documentado.


## Práticas (3.1)
Nove arquivos movidos, incluindo catálogo de Questões do Aluno com ConsultaQuestoesElegiveis injetada. Uma Model canônica. API pública contém somente projeções próprias de desempenho/atividades. Unitários: 172 OK (unit-praticas.log); integrações: sete OK, 20,479 s (integration-praticas.log), preservando replay, propriedade, sigilo do gabarito e correção histórica. Rotas/metadata/guards/CLI/hashes equivalentes ao baseline.


## Simulados (4.1–4.2)
Doze arquivos movidos e sete Models canônicas, sem duplicação. Catálogo/histórico mantêm contratos injetados e regra de disponibilidade no Service. Questões acessadas pela API de Conteúdo, inclusive projeção de classificação histórica. API publica fatos, atividades e contagens. Unitários: 172 OK (unit-simulados.log); 13 integrações OK em 30,436 s (integration-simulados.log), cobrindo publicação, composição, início/resposta/finalização, branco, revisões e rollback. Comparação integral equivalente ao baseline.


## Desempenho (5.1)
Seis arquivos em modules/desempenho, sem Model/tabela nova. Agregação consulta somente APIs públicas de Conteúdo/Práticas/Simulados no mesmo snapshot. O mesmo DiagnosticoAluno continua no dashboard e seletor do plano. Unitários: 172 OK (unit-desempenho.log); 11 integrações OK em 23,368 s (integration-desempenho.log), incluindo UTC, classificação histórica, denominadores, transferência e snapshot concorrente. Comparação estrutural integral preservada.


## Contas/Plano e consolidação (6.1–6.3, 7.1)
21 arquivos de Contas e nove de Plano movidos, além do health em core. Quatro + duas Models, seis Blueprints e registro explícito das mesmas 21 classes. Pastas globais de negócio sem implementação; restam somente as duas pontes estáticas delimitadas. Factory/hooks/cache/CLI e seed E2E usam caminhos canônicos. Lock exato em Contas; eliminação própria e ordenada em Plano por participante sem commit, injetado em Recusar/Revogar. Acrescentada regressão MySQL de recusa com falha real de eliminação/retry e isolamento das duas instâncias por aplicação. Unitários: 172 OK (unit-contas-plano.log); 32 integrações OK em 55,969 s (integration-contas-plano.log), com falhas reais/rollback, concorrência geração-negativa, replay, conta alheia e respostas preservadas. Comparação de rotas/Models/guards/CLI/hashes integralmente equivalente; busca em backend/scripts sem referências funcionais aos caminhos removidos.


## Documentação (7.2)
ADR-010 e mapa modular concluídos; README, índice de ADRs, conventions de estrutura/arquitetura/testes, oito documentos operacionais, aplicação SOLID, matriz dos vinte casos e diagrama atualizados. Plano mestre recebe situação implementada preservando roadmap/histórico. YAML modifica apenas contexto: schema/rules/operations idênticos. Verificador local: 124 links válidos e 110 arquivos protegidos de SQL/frontend/specs/design/dependências idênticos. Não se alteraram ADRs históricos ou artefatos Desktop V1.


## Regressão integrada (8.1)
Runner oficial de cobertura: python tmp/modular-baseline/run.py python backend/tests/run_backend_coverage.py — exit 0. Unitários: 172 OK (3,142 s); integrações reais com os dois opt-ins: 137 OK (405,295 s). Cobertura: 97,72% linhas (4034/4128), 91,68% branches (871/950); gates 90%/85% e ausência de arquivo executável sem cobertura aprovados pelo validador oficial. Log: tmp/modular-baseline/coverage-final.log; métricas em coverage-backend.json. Gate de arquitetura reforçado na revisão e unitários novamente aprovados: 172 (3,618 s), unit-review-final.log.
Servidor frontend: python -m unittest discover -s scripts/tests -p test_serve_frontend.py — sete testes OK (1,855 s), server-final.log.
E2E: python tmp/modular-baseline/run.py python scripts/run_e2e.py — única execução dos três percursos, três passaram (52,4 s), e2e-final.log e test-results/e2e.json. Runner removeu o schema/processos locais; configurações sem trace/vídeo/sessão exportada preservadas.
Opt-ins/credencial foram injetados somente nos subprocessos pelo runner temporário, com dotenv desabilitado. Após as suítes, consulta da instância própria confirmou zero schemas de aplicação remanescentes; porta/datadir exclusivos conferidos e SHUTDOWN executado. Dados/evidências temporários permanecem em tmp/modular-baseline para revisão, sem tocar no tmp anterior ou no banco operacional.


## Comparação e fechamento (8.2)
Baseline independente em [baseline.json](baseline.json); resultado e correspondência completa de endpoints em [comparacao.json](comparacao.json). As 21 representações de Models, seis guards, dois comandos CLI e 14 hashes são idênticos. As 68 rotas completas (67 da API e static) preservam URLs/métodos/conversores/defaults/strict-slashes/redirecionamentos/funções; somente namespaces internos recebem o módulo.
O inventário acima é o mapa final dos 94 movimentos. Revisão por AST: 80 corpos idênticos retirando imports/docstrings; 14 adaptações limitadas aos helpers extraídos, fronteiras públicas e participante transacional aprovado. Nos testes anteriores, corpos/asserções permanecem após normalizar imports/patches; as três diferenças adicionais são identidade das bases, isolamento da composição e nova falha real da recusa. APIs/fronteiras revisadas e gate completo aprovado; nenhum alias dinâmico, export ORM/Repository completo ou implementação global de negócio.
Validação OpenSpec estrita aprovada; skip_specs aceita zero deltas funcionais. git diff --check aprovado. Verificador documental: 124 links locais válidos, schema/rules/operations intactos e 110 arquivos de frontend/SQL/specs/Desktop V1/dependências idênticos ao baseline. Alterações legítimas iniciais e tmp anterior preservados, sem leitura/exposição de .env ou credenciais. Nenhuma operação no banco operacional, migration nova, alteração de schema/SQL publicado/HTML legal, dependência, frontend ou contrato HTTP. Sem pendência crítica de implementação identificada.
Limites e sequência: resultados locais contra MySQL 8.0.44 e dados sintéticos; nenhuma implantação/commit/push/merge. A verificação formal da change deve preceder o arquivamento. Esta refatoração usa skip_specs e não exige sincronização de delta funcional. Logs e referências temporárias são locais; capturas PowerShell preservam stderr de unittest e aviso de cor do Node, com códigos finais 0 dos runners.

## Verificação formal — 07/11/2026

Executada pela skill `openspec-verify-change`, após o apply: completude,
correção e coerência aprovadas, sem achados críticos ou avisos. Os 172 unitários
foram reexecutados e passaram (3,870 s; `tmp/modular-baseline/unit-verificacao.log`).
Conferidas as evidências das 137 integrações MySQL e três E2E, os gates de
cobertura (97,72% linhas / 91,68% branches), o baseline oficial, as fronteiras,
os 124 links locais e os 110 arquivos protegidos. Validação OpenSpec estrita
e `git diff --check` aprovados. Nenhum código ou artefato foi alterado durante
a verificação; este registro foi acrescentado na etapa de arquivamento.
Sem delta funcional para sincronizar (`skip_specs: true`).
