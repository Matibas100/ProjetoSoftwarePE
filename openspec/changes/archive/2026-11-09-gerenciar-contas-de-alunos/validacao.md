# Validação — gerenciar-contas-de-alunos

Data: **09/11/2026**. Schema OpenSpec: `spec-driven`.

## Resultado e limites

Implementados CRUD administrativo de Alunos, desativação/reativação, duas telas
e migration 017. MySQL real e Chromium comprovam criação sem vínculo/aceite,
DELETE permitido, DELETE bloqueado por FK, revogação de múltiplas sessões e
novo login após reativação/troca de e-mail. F01 encerrada **somente para Alunos**.
F02 e os vinte casos anteriores permanecem; E01–E03 seguem independentes.

Não há gestão de Administradores, escolha de perfil, reset/envio de senha,
exclusão geral/anonimização, auditoria completa ou aceite acadêmico presumido.
Não foi aplicada migration no banco operacional. Dados de teste são sintéticos,
em schemas aleatórios descartáveis, removidos pelas fixtures/runners.
Não houve chamada externa ao Gemini, commit, push ou merge.

## Execução

| Verificação | Resultado |
| --- | --- |
| Backend unitário | 202 testes passaram; inclui arquitetura, sete módulos, 21 mappers e factories independentes |
| Integração backend completa, ambos os opt-ins ativos | 215 testes executados; somente duas expectativas de quantidade pendente, ainda fixadas em 016, falharam em 28 subcenários |
| Rechecagem após atualização das expectativas para 017 | 13 testes passaram: os dois casos corrigidos, com todos os prefixos, e 11 integrações de gestão |
| Caso adicional de lock na revogação + unidades administrativas | 6 testes passaram; o erro direto do cursor retorna 409 e a desativação é revertida |
| Integrações distintas verificadas entre regressão e complementos | 219; inclui os 29 testes originais e todas as suítes de migrations habilitadas |
| Cobertura backend consolidada | Linhas **97,81%** (4862/4971), branches **92,72%** (1031/1112); gate aprovado |
| Frontend com cobertura | **302 testes**, 18 arquivos; linhas **99,38%** (2255/2269), branches **90,63%** (1721/1899); gate aprovado |
| Chromium/API/MySQL, suíte completa sem interceptação | **6 E2E passaram**, em 57,1 s; vinte casos originais, F02, plano/simulado, privacidade, Tutor desabilitado e gestão de Alunos |
| OpenSpec | `openspec validate gerenciar-contas-de-alunos --strict`: válido |

As duas falhas da primeira regressão eram as contagens de migrations restantes
nos testes de baseline/round-trip. A rechecagem executou todos os seus prefixos
com a expectativa corrigida (`17 - prefixo`), sem falhas. Não houve nova rodada
completa após essa correção de testes; os casos afetados foram reexecutados.
A cobertura reúne os processos unitário, integração e rechecagens; não confundir
cobertura agregada com ausência de falhas na primeira rodada.

Comandos principais, com opt-ins somente no ambiente do processo:

```powershell
$env:RUN_MYSQL_INTEGRATION = "1"
$env:RUN_MYSQL_MIGRATION_INTEGRATION = "1"
python backend/tests/run_backend_coverage.py

$env:PYTHONPATH = "backend"
python -m coverage run --parallel-mode -m unittest tests.test_migrations_integration.MigrationRunnerIntegrationTest.test_baseline_reconhece_todos_os_prefixos_sem_alterar_dados tests.test_schema_portavel_integration.SchemaPortavelIntegrationTest.test_round_trip_prefixos_baseline_upgrade_dados_e_contadores tests.test_gestao_alunos_integration -q
python -m coverage run --parallel-mode -m unittest tests.test_gestao_alunos_integration.GestaoAlunosIntegrationTest.test_lock_na_revogacao_participante_retorna_409_e_reverte_ativo tests.unit.test_gestao_alunos -q
python -m coverage combine
python -m coverage json
python scripts/validate_backend_coverage.py
npm run test:coverage
```

E2E usou `tmp/executar-gestao-e2e.py`, adaptador local do runner oficial
`scripts/run_e2e.py`: configuração carregada sem exibir valores, repassada ao
processo; `RUN_MYSQL_E2E=1`, seis arquivos Playwright, schema descartável.
O comando reproduzível oficial com configuração MySQL no ambiente é:

```powershell
$env:RUN_MYSQL_E2E = "1"
python scripts/run_e2e.py
```

Logs locais: `tmp/gestao-backend.log`, `tmp/gestao-backend-rechecagem.log`,
`tmp/gestao-frontend.log` e `tmp/gestao-e2e-completo.log`. Contêm resultados
sintéticos, sem configuração, cookies ou credenciais. Relatórios de cobertura
e `test-results/` são artefatos locais, não novos documentos oficiais congelados.

## Rastreabilidade

| Requisito / tasks | Implementação e evidência |
| --- | --- |
| Procedures, snapshot e lock corrente; 1.1–1.3 | `017_gestao_alunos_procedures.sql`, `sql_resources.py`, `UsuarioRepository`, `ConsultaAlunosAdmin` e composição; 4 integrações de migration e teste de snapshot/identity map corrente |
| Gestão exclusiva/autorização; 2.5 | `UsuarioController`, rotas e `auth_http`: autenticação antes do corpo, Administrador como alvo recebe 404, Origin/CSRF/reauth, HEAD/OPTIONS, no-store, limite local 16 KiB e 413 |
| Criação e DTO mínimos; 2.1 | `CriarAlunoAdminService`, `ListarAlunosAdminService`, `BuscarAlunoAdminService`, validações/DTO separados; hash scrypt, perfil fixo, sem sessão/aceite, máscara e duplicidade normalizada |
| Identificação/sessões e atomicidade; 2.2 | `AtualizarAlunoAdminService`, e-mail esperado nos dois locks de autenticação; concorrência por endereço único, login antigo nos dois intervalos e trigger real de falha na revogação |
| Desativar/reativar; 2.3 | Services separados; múltiplas sessões, reenvio, login de inativo, planos/decisões/autoria preservados, falha intermediária e timeout na revogação com rollback |
| Exclusão por FK; 2.4 | `Usuario.deletar(confirmar=False)` sob lock; sem vínculos → 204; aceite, sessão revogada, plano/autoria → 409; referência concorrente não produz órfão |
| Falhas seguras | Unidades distinguem 1062 da chave esperada, 1451, 1205/1213; integração real cobre 1205 no lock do usuário e no cursor da revogação, routines ausentes e mensagens sanitizadas |
| Telas; 3.1–3.3 | HTML/CSS/JS próprios, navegação, 14 testes DOM: guard, campos exatos, senha limpa, POST→detalhe/PUT, cancelamento, falhas, reauth sem replay, conta diferente, XSS como texto e consultas obsoletas |
| Compatibilidade e prova; 4.1–4.3 | E2E completo, matriz CRUD, modelagem, mapa modular/telas, README, gates de arquitetura/cobertura e inspeção de preservação |

Não há SQL/`db.session` em Controller/Service, import privado de outro módulo,
Repository genérico de CRUD, fallback ORM especializado ou transação nas routines.
`TransactionManager` mantém a confirmação/rollback única; Models participam
com `confirmar=False`. Revogação reutiliza `sp_revogar_sessoes_usuario` da 016.

## Migration e preservação

A 017 foi instalada e reconhecida em schemas descartáveis. Foram verificados:
instalação limpa, upgrade 016 com dados, bootstrap equivalente, restauração,
baseline completo, reexecução zero, busca literal/paginação/total, parâmetros
inválidos, routines parciais e drift de corpo/assinatura/segurança, dependência
anterior inválida e gates existentes de checksum, lock e histórico FAILED/RUNNING.

Comparação com o conteúdo versionado confirma preservação dos checksums SQL
000–016, das 59 referências SQL anteriores, dos três HTMLs legais e dos quatro
binários oficiais do Desktop V1. A referência recebeu somente duas entradas;
nenhuma tabela/FK, mapper ou módulo foi acrescentado. Alterações locais anteriores
da busca por ID foram preservadas.

## Revisão visual e técnica

Comparadas as páginas 58–59 do protótipo oficial com as telas reais em 1440 e
390 px. Shell, ativos, cores e hierarquia seguem o padrão existente. A adaptação
móvel mantém navegação horizontal, saída acessível e rolagem apenas interna da
tabela; as checagens de `scrollWidth <= innerWidth` passaram nas duas telas.
Diálogos usam foco inicial seguro, Tab contido, Escape/cancelamento e retorno
de foco. Confirmação de troca de e-mail foi exercitada por teclado no Chromium.

Capturas estão em
`test-results/browser/usuarios-Gestão-de-Alunos--b1137--sessões-e-revisão-1440-390/`:
`usuarios-lista-1440.png`, `usuarios-lista-390.png`, `usuario-detalhe-1440.png`
e `usuario-detalhe-390.png`. Sem trace, HAR, vídeo ou storage state autenticado.

Diferenças do protótipo: somente Alunos; sem filtros/perfis avançados, métricas,
estudos de terceiros, auditoria, recuperação ou exportação fictícios. Exclusão
é condicionada e desativação é distinta. Limites descritos no
[contrato operacional](../../../../docs/technical/gestao-administrativa-alunos.md).

Inspeção de escopo, UTF-8, links relativos, sintaxe Python, diff e fronteiras
não encontrou pendência crítica. Sincronização das três capabilities e
arquivamento permanecem como próximos passos do workflow.

| Dimensão | Resultado |
| --- | --- |
| Completude | 14/14 tasks; requisitos rastreados aos casos administrativos, SQL, interface e testes |
| Correção | Cenários MySQL/DOM/Chromium e rechecagens aprovados; gates de cobertura satisfeitos |
| Coerência | CRUD na Model, CALL no Repository, transação única, sete módulos/21 mappers e limites aprovados preservados |

Sem achado crítico ou pendência de implementação para sincronizar/arquivar.

## Encerramento do workflow

Em 09/11/2026, as três capabilities foram sincronizadas com as specs principais:
dois requisitos em `contas-privacidade-mysql`, oito na nova spec
`gestao-administrativa-alunos` e um em `migrations-sql`. Os deltas foram
comparados integralmente após o merge, sem duplicatas ou operações pendentes.
`openspec validate --specs --strict`: **18 aprovadas, zero falhas**.

A change foi arquivada pelo CLI em
`openspec/changes/archive/2026-11-09-gerenciar-contas-de-alunos/`, com 14/14 tasks.
O comando usou `--skip-specs` porque a sincronização já estava concluída e
conferida. O CLI emitiu apenas a recomendação não bloqueante de dividir changes
com mais de dez deltas; o escopo aprovado foi mantido. Links foram atualizados.
Nenhum banco operacional, commit, push ou merge integra esse encerramento.
