# Tasks

Escopo exclusivo de testes. Preservar o site/banco da apresentação e todas as mudanças locais anteriores. Não desabilitar testes ou reduzir cobertura para obter resultado verde.

## 1. Corrigir a restauração literal

- [x] 1.1 Nas três restaurações identificadas em `test_contas_procedures_integration.py`, `test_plano_procedures_integration.py` e `test_gestao_alunos_integration.py`, enviar o DDL com `no_parameters=True` conforme design; acrescentar regressão MySQL descartável preservando `100% ENEM` e `%s` na routine. Verificar restauração, valores intactos, limpeza em `finally` e os três casos originais, sem mocks ou alteração de permissões globais.
- [x] 1.2 Registrar em `validacao.md` a causa comum dos dois runs, reprodução, arquivos corrigidos e resultado dos testes; verificar correspondência aos logs reais e distinguir causa inicial, falhas em cascata e resultado remoto ainda não confirmado, sem dados sensíveis.

## 2. Verificar isolamento e regressão

- [x] 2.1 Executar as suítes relacionadas de Contas, Plano e gestão de Alunos com MySQL real descartável, revisar diff/UTF-8/segredos e validar `openspec validate corrigir-restauracao-procedures-ci --strict`; verificar que testes seguintes continuam íntegros e não houve mudança em produção, migrations, schema, workflow ou arquivos legítimos de outras changes. Documentar os comandos/resultados e qualquer limitação de validação remota.

## Workflow follow-up

- Verificar e arquivar após aplicação; não há delta funcional para sincronizar (`skip_specs: true`).
- Commit/push só com autorização explícita. Depois de publicar, acompanhar uma nova execução do Actions; não alegar correção remota apenas pela reprodução/testes locais.
