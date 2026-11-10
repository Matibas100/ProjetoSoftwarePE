# Design: executar diretamente Python e npm

## Context

Ver [proposal.md](proposal.md). O Makefile tem apenas aliases para runners existentes. A aplicação e o workflow não o invocam, mas `CliTest.test_baseline_reconcile_e_atalhos_make` lê o arquivo e exige quatro targets; apagá-lo isoladamente quebraria a suíte unitária executada na CI.

As changes de ferramentas e README estão aplicadas/arquivadas, com mudanças locais ainda não publicadas e dois novos guias não rastreados. A fonte desta alteração deve ser a árvore local, preservando o README curto e esses guias.

## Goals / Non-Goals

**Objetivo:** remover a necessidade de GNU Make e manter todos os comandos, testes de comportamento e orientação de operação.

**Limites:** somente os seis arquivos enumerados na proposta e os artefatos desta change. Sem nova camada de atalhos, mudanças nos runners ou reescrita das changes anteriores.

## Decisions

### 1. Aposentar os aliases e preservar suas operações

Excluir somente o `Makefile` da raiz. Nos documentos, substituir tabelas de aliases por finalidade/comando direto, preservando a cobertura dos seguintes usos:

| Uso | Comando direto existente |
| --- | --- |
| Status do banco | `python backend/database/migrate.py status` |
| Aplicar migrations | `python backend/database/migrate.py up` |
| Adotar banco existente | `python backend/database/migrate.py baseline --confirm` |
| Registrar reconciliação autorizada | `python backend/database/migrate.py reconcile 003 --confirm` (003 é exemplo de versão) |
| Unitários | `python backend/tests/run_unit.py` e `npm run test:unit` |
| Integrações | `python backend/tests/run_integration.py` |
| Cobertura backend | `python backend/tests/run_backend_coverage.py` |
| Cobertura frontend | `npm run test:coverage` |
| Cobertura das duas pilhas | Executar os dois comandos de cobertura acima |
| Navegador | `python scripts/run_e2e.py` ou o equivalente existente `npm run test:e2e` |

Preservar os opt-ins de processo, uso de MySQL descartável, precondições e limites dos comandos; removê-los junto com a coluna Make seria perda de orientação. Não executar migrations ou testes de integração para conferir essa tabela.

Retirar apenas a indicação de GNU Make no README e em `docs/conventions/testes.md`, e a cláusula de tabulação de receitas Make em `docs/conventions/documentacao-e-nomenclatura.md`. No guia operacional, manter os comandos de banco e referências às conventions atualizadas. Preservar títulos/âncoras já referenciados e relatos históricos; não fazer substituições globais no arquivo de changes arquivadas.

Alternativa rejeitada: substituir Make por novos scripts Python/npm. Os runners já são as entradas diretas e suficientes.

### 2. Retirar a exigência de arquivo sem perder o teste da CLI

Em `backend/tests/unit/test_migrations.py`, renomear somente `test_baseline_reconcile_e_atalhos_make` para `test_baseline_e_reconcile`. Preservar decorators, setup, mocks, chamadas de `baseline`/`reconcile` e todas as assertions correspondentes. Remover somente a leitura de `Makefile` e o laço que confere `db-status`, `db-up`, `db-baseline` e `db-reconcile`.

Não excluir o método ou substituir suas verificações por mocks mais amplos, skip ou assertion genérica. Não criar teste que confira apenas a ausência do Makefile. Os demais testes do arquivo permanecem intactos.

### 3. Verificar a alteração com escopo proporcional

Registrar antes da edição os arquivos locais já modificados, hashes e conteúdo relevante do método de teste e documentos. Após a edição, conferir a diferença específica desta change e preservar todos os demais arquivos, inclusive as mudanças locais anteriores.

Executar uma vez `python backend/tests/run_unit.py`, que não abre MySQL nem lê `.env`. Comparar o teste alterado com o original, confirmar que comandos/opt-ins continuam documentados e pesquisar referências ativas a Make, incluindo o guia operacional não rastreado. Referências históricas em arquivos arquivados não são instruções ativas e permanecem preservadas.

Conferir links/âncoras dos documentos alterados, igualdade das fontes do produto, workflow, dependências e runners com o estado inicial, `git diff --check` e `openspec validate --all --strict`. Registrar comandos/resultados/limites em `validacao.md`. Não executar frontend/E2E, descoberta de testes, instalação ou publicação para esta retirada de aliases.

## Risks / Trade-offs

- **Apagar o arquivo quebrar testes:** ajustar junto apenas a dependência ao arquivo, mantendo o comportamento testado da CLI.
- **Orientação continuar citando ferramenta removida:** atualizar README, duas conventions e guia operacional, sem apagar comandos diretos.
- **Perder alterações locais anteriores:** comparar com o estado local capturado, sem reset/checkouts ou edição de artefatos arquivados.
- **Remoção dos aliases ser confundida com retirada dos testes:** manter todos os runners, limites, npm scripts e GitHub Actions.

## Migration Plan

Sem migration de banco ou mudança de implantação. Remover o arquivo, ajustar o teste e a documentação e validar. Para reverter, restaurar somente essas edições preservando o trabalho anterior. Não há specs a sincronizar (`skip_specs: true`); verificar antes de arquivar. Commit e push exigem autorização explícita.
