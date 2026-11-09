# Validação — restauração literal de procedures

Data: 09/11/2026. Escopo exclusivo de testes, com MySQL 8.0.44 real e schemas
descartáveis criados pelo suporte existente. SQLAlchemy local: 2.0.51.

## Evidência remota e causa

Foram consultados os jobs pela API do GitHub e os logs reais com:

```powershell
gh run view 42462204592 --repo Matibas100/ProjetoSoftwarePE --log-failed
gh run view 42600955448 --repo Matibas100/ProjetoSoftwarePE --log-failed
```

| Execução | Commit | Resultado observado nas integrações |
| --- | --- | --- |
| [42462204592](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42462204592) | `6b37946` | 197 testes; 1 falha e 19 erros |
| [42600955448](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42600955448) | `46493dc` | 200 testes; 1 falha e 19 erros |

Em ambos, 16 erros ocorrem nos subtestes de ausência de procedures de Contas
e Plano: o `finally` chega a `exec_driver_sql(original)` e o PyMySQL tenta
interpolar o DDL com parâmetros vazios. O traceback termina em
`ValueError: unsupported format character` no índice 24. O `%` no host do
`DEFINER` explica esse ponto de falha, conforme a reprodução do driver.

As falhas seguintes são compatíveis com a restauração interrompida: três testes
de Plano geram `KeyError: 'plano'` ao receber resposta de erro e a consulta final
de sessão de Contas recebe HTTP 500 em vez de 200. Os logs não demonstram falha
independente nesses quatro casos; a ausência das routines explica a cascata.
Gestão de Alunos contém a mesma chamada vulnerável, corrigida preventivamente;
ela não aparece como origem de falha nesses dois runs.

Os jobs falharam na etapa de backend/MySQL. Frontend e Chromium foram pulados;
isso não constitui resultado de testes dessas etapas.

## Correção e regressão

- `backend/tests/test_contas_procedures_integration.py` e
  `test_plano_procedures_integration.py`: restauração com
  `execution_options={"no_parameters": True}`, preservando o `finally`.
- `backend/tests/test_gestao_alunos_integration.py`: mesma correção, preservando
  todo o conteúdo local anterior.
- `backend/tests/test_restauracao_procedures_integration.py`: cria procedure
  temporária, lê o DDL, remove/restaura e compara o texto completo. Confere
  `100% ENEM` e `%s` retornados antes e depois de erro real de argumentos no
  `CALL`, além de consulta posterior na mesma conexão. Remove a procedure em
  `finally` e verifica sua ausência; a fixture remove o schema.

Reprodução complementar no driver, sem executar SQL: um cursor PyMySQL com
`defer_connect=True` recebeu DDL sintético com host `%`. `mogrify(ddl, {})`
gerou `ValueError`; `mogrify(ddl)` preservou exatamente o texto. Nenhuma conta
ou permissão MySQL foi criada ou alterada.

A regressão real também foi executada com a chamada de restauração antiga,
substituída somente no código compilado em memória. Falhou nessa chamada com
`TypeError: must be real number, not dict`: nesse DDL local, o primeiro `%`
problemático está em `100% ENEM`, em vez do host do definer. É a mesma tentativa
indevida de interpolação. Com a opção aplicada, passou. Não houve alteração
do arquivo para essa reprodução; a fixture executou a limpeza após o erro.

## Comandos e resultados locais

Opt-ins definidos somente no processo; Tutor externo desativado:

```powershell
$env:PYTHONPATH = 'backend'
$env:RUN_MYSQL_INTEGRATION = '1'
$env:RUN_MYSQL_MIGRATION_INTEGRATION = '1'
$env:GEMINI_API_KEY = ''
$env:TUTOR_IA_ENABLED = 'false'
```

Primeiro foram executados os três métodos originais de ausência de routines,
seguidos do módulo de regressão:

```powershell
python -m unittest -v tests.test_contas_procedures_integration.ContasProceduresIntegrationTest.test_routines_indisponiveis_falham_sem_fallback_ou_detalhes_sensiveis tests.test_plano_procedures_integration.PlanoProceduresIntegrationTest.test_falta_de_routine_erro_http_seguro_sem_fallback_e_guard_precede_derivados tests.test_gestao_alunos_integration.GestaoAlunosIntegrationTest.test_routine_ausente_e_erro_sanitizado tests.test_restauracao_procedures_integration
```

Resultado: **4 testes passaram**, em 13,814 s, sem skips.

Em seguida, regressão relacionada, incluindo migrations em schemas próprios:

```powershell
python -m unittest -v tests.test_autenticacao_integration tests.test_privacidade_integration tests.test_planos_integration tests.test_contas_procedures_integration tests.test_plano_procedures_integration tests.test_gestao_alunos_integration tests.test_contas_procedures_migrations_integration tests.test_plano_procedures_migrations_integration tests.test_gestao_alunos_migrations_integration tests.test_restauracao_procedures_integration
```

Resultado: **76 testes passaram**, em 135,384 s, sem falhas, erros ou skips.
Os três casos de Plano que falharam em cascata no CI passaram, assim como a
consulta de sessão após as restaurações de Contas e toda a suíte de Alunos.

## Isolamento e limites

A comparação SHA-256 com o preflight preserva os arquivos locais anteriores
fora das três restaurações e dos artefatos desta change. Não houve edição em
produção, migrations, schema de instalação, workflow, frontend ou specs de
produto; SQL das integrações ficou restrito aos schemas descartáveis.
Não foram usados mocks ou SQLite. Nenhum segredo ou conteúdo de `.env` foi
incluído neste relatório.

Validações finais:

- `git diff --check` nos dois testes já rastreados alterados: passou.
- Inspeção dos seis arquivos do escopo: UTF-8 válido sem BOM, sem caracteres de
  substituição, espaços finais ou padrões de credenciais; diff revisado.
- Snapshot de 712 arquivos não temporários antes da edição: somente os três
  testes existentes e `tasks.md` mudaram. As duas adições são o teste de
  regressão e este relatório; os demais arquivos mantiveram seus hashes.
- `openspec validate corrigir-restauracao-procedures-ci --strict`: passou;
  o CLI aceitou zero deltas conforme `skip_specs: true`.

Não houve commit, push ou nova execução do Actions. O resultado remoto da
correção continua **não confirmado**; requer publicação autorizada e novo run.
Não há delta funcional para sincronizar (`skip_specs: true`). Verificação
formal e arquivamento permanecem etapas posteriores do workflow.
