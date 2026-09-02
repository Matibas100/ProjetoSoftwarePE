# Workflow OpenSpec

## Quando usar

Use uma change para funcionalidade, correção, refatoração, alteração arquitetural, contrato HTTP, schema, migration ou comportamento observável.

## Fluxo

```text
explore
  -> propose
  -> apply
  -> verify
  -> sync-specs
  -> archive
```

1. **Explore:** investigar requisitos e o repositório sem implementar.
2. **Propose:** criar a change pelo CLI e produzir `proposal`, `design`, delta specs e `tasks` suficientes.
3. **Apply:** implementar apenas tarefas aprovadas, mantendo os artefatos coerentes.
4. **Verify:** comparar implementação, requisitos, cenários, design e testes.
5. **Sync:** atualizar specs principais quando necessário.
6. **Archive:** arquivar somente após tarefas concluídas e ausência de problema crítico.

## Regras

- Nunca crie `openspec/changes/<nome>` manualmente.
- Uma change não pode depender apenas da conversa para ser implementada.
- Proposal declara objetivo, escopo, fora de escopo, impacto e compatibilidade.
- Specs descrevem comportamento observável e cenários testáveis.
- Design registra decisões técnicas, riscos, migrations e integrações.
- Tasks indicam superfícies afetadas e validações necessárias.
- Descoberta que muda escopo ou decisão deve atualizar os artefatos antes de continuar.
- Correções pequenas continuam usando OpenSpec quando alterarem comportamento; tarefas puramente operacionais de Git não exigem change.
