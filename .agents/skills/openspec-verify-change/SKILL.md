---
name: openspec-verify-change
description: Verifica se a implementação corresponde aos artefatos de uma change OpenSpec antes da sincronização ou do arquivamento.
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires OpenSpec CLI 1.11 or newer.
metadata:
  version: "1.0-platform-enem"
---

# Verificar change OpenSpec

Use esta skill quando o usuário pedir validação de uma implementação antes de sincronizar ou arquivar a change.

## Fluxo

1. Selecione a change informada. Se estiver ambígua, use `openspec list --json` e peça a escolha.
2. Execute `openspec status --change "<nome>" --json`.
3. Execute `openspec instructions apply --change "<nome>" --json` e leia todos os `contextFiles` retornados.
4. Leia `AGENTS.md` e as conventions acionadas pelo escopo.
5. Verifique três dimensões:
   - **Completude:** todas as tasks concluídas e todos os requisitos representados.
   - **Correção:** implementação e testes atendem aos requisitos e cenários.
   - **Coerência:** implementação segue o design, os ADRs e a arquitetura do projeto.
6. Confirme que não houve ampliação de escopo, exposição de segredo ou alteração incompatível de contrato/schema.
7. Quando o escopo exigir execução de testes, use `docs/conventions/testes.md`; não substitua MySQL por mocks ou SQLite.
8. Não altere código, tasks ou artefatos durante a verificação sem nova autorização.

## Relatório

Apresente:

| Dimensão | Resultado |
|---|---|
| Completude | tarefas e requisitos cobertos |
| Correção | cenários e testes validados |
| Coerência | aderência ao design e conventions |

Classifique achados como:

- **CRÍTICO:** impede archive.
- **AVISO:** deve ser avaliado antes do archive.
- **SUGESTÃO:** melhoria não bloqueante.

Cada achado deve citar evidência concreta e ação recomendada. Sem críticos, informe objetivamente se a change está pronta para sync/archive.
