# Proposal

## Why

As execuções do GitHub Actions dos commits `6b37946` e `46493dc` falharam no mesmo ponto: restaurar DDL obtido por `SHOW CREATE PROCEDURE` com `exec_driver_sql(original)`. No CI, `DEFINER` contém o host `%`; o driver recebe parâmetros vazios e tenta interpolar esse caractere, produzindo `ValueError: unsupported format character` e falhas seguintes por procedures não restauradas.

## What Changes

- Enviar o DDL literal sem parâmetros nas três restaurações afetadas dos testes de Contas, Plano e gestão de Alunos.
- Acrescentar regressão MySQL descartável que preserve `%` no corpo da routine durante remoção/restauração, reproduzível também quando o usuário local não possui host `%`.
- Registrar causa, reprodução e validação, sem desabilitar testes, reduzir cobertura ou mascarar falhas reais.

Fora de escopo: código do site, banco operacional, migrations, schema, permissões MySQL, workflow YAML, novas funcionalidades e publicação sem autorização.

## Capabilities

### New Capabilities

Nenhuma. `skip_specs: true`: correção exclusiva de infraestrutura de testes, sem mudança em comportamento funcional contratado.

### Modified Capabilities

Nenhuma; specs de produto continuam iguais.

## Impact

- `backend/tests/test_contas_procedures_integration.py`, `test_plano_procedures_integration.py` e `test_gestao_alunos_integration.py`: correção de restauração DDL.
- Teste de regressão na infraestrutura/suíte de integração existente, com MySQL real e schema próprio descartável.
- Sem dependência nova, alteração das funcionalidades ou interrupção do ambiente da apresentação. Preservar todas as mudanças locais legítimas ainda sem commit.
- Evidências: [execução 42600955448](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42600955448) e [42462204592](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42462204592). Ambas falharam no backend; frontend/E2E foram pulados após essa falha.
