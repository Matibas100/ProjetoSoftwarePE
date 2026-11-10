# Tarefas

## 1. Retirar o arquivo preservando o comportamento testado

- [x] 1.1 Registrar o estado local e hashes não sensíveis dos documentos, teste, runners, fontes e configurações antes de editar. Verificar os seis arquivos de escopo, o método que lê Makefile e as referências ativas, incluindo o guia operacional ainda não rastreado; preservar integralmente o trabalho legítimo das changes já arquivadas.
- [x] 1.2 Remover somente o Makefile da raiz e renomear o teste para `CliTest.test_baseline_e_reconcile`, retirando apenas a leitura/assertions do Makefile. Comparar com o original para confirmar que decorators, setup, mocks e verificações de baseline/reconcile continuam iguais e os demais testes permanecem intactos; executar `python backend/tests/run_unit.py`, sem MySQL ou novas fixtures de integração.

## 2. Documentar os comandos diretos

- [x] 2.1 Ajustar README, `docs/conventions/testes.md`, `docs/conventions/documentacao-e-nomenclatura.md` e `docs/technical/operacao-do-projeto.md` para retirar a indicação de GNU Make, as tabelas de aliases e a regra de tabulação de suas receitas. Verificar todos os usos da tabela do design contra os comandos existentes, preservando opt-ins, precondições, títulos/âncoras e histórico; conferir que não restam instruções ativas para executar Make fora dos artefatos da própria change e do histórico arquivado.

## 3. Conferência integrada

- [x] 3.1 Concluir `validacao.md` com resultados, comandos preservados, comparação do teste e limites. Conferir os hashes/diffs em relação ao estado local inicial, a preservação de CI/runners/dependências/produto e os links dos documentos alterados; executar `git diff --check` e `openspec validate --all --strict`. Confirmar ausência de edições fora do escopo, instalação, operações no banco, alterações em relatórios/backups ou publicação Git.

## Workflow follow-up

- Verificar antes de arquivar; não há specs a sincronizar (`skip_specs: true`).
- Arquivar após a verificação, preservando os artefatos históricos anteriores.
- Commit e push dependem de autorização explícita e não fazem parte do apply.
