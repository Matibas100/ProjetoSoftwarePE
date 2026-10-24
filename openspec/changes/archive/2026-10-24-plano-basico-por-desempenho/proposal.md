# Proposta — 6. Plano básico por desempenho

## Why

O diagnóstico mostra dificuldades, mas o Aluno precisa de um próximo passo. Esta entrega gera uma lista persistida e explicável de até três Assuntos prioritários, ligados à prática de Questões.

## What Changes

- Gerar plano próprio usando o diagnóstico do item 5 e somente Assuntos com Questões publicadas disponíveis.
- Priorizar menor percentual de acerto com amostra suficiente e explicar a ordem com acertos, total e período.
- Persistir o plano e seus itens; iniciar prática contextual, marcar item concluído e recalcular mediante confirmação.
- Manter plano anterior e conclusões como histórico, sem mudança automática ao registrar uma resposta.
- Fora de escopo: agenda semanal, disponibilidade, duração sugerida, notificações, metas, reagendamento, IA, resumos e tutor. É um recorte básico de ALU-PLA-001, não a agenda completa do Desktop V1.

## Capabilities

### New Capabilities

- `plano-estudos-basico`: geração determinística, persistência, conclusão e recálculo explicado por desempenho.

### Modified Capabilities

Nenhuma. O plano consome o contrato de diagnóstico do item 5 e a prática do item 3 sem alterar essas capacidades.

## Impact

- Superfícies: Models de plano/itens, Services de gerar/consultar/concluir/recalcular, Repository especializado para consulta e elegibilidade, Controllers/rotas e frontend ALU-PLA-001 com link no dashboard.
- Contratos propostos: `/api/aluno/plano`, `/api/aluno/plano/gerar`, `/api/aluno/plano/recalcular` e `/api/aluno/plano/itens/<id>/concluir`.
- Dependências: item 5 (`dashboards-desempenho-real`) encerrado e contratos dos itens 2–4 disponíveis; localizar artefatos pelo nome inclusive após arquivamento e executar por último. Limiar e denominador são reaproveitados, sem fórmula paralela.
- Decisões propostas para o MVP: até três Assuntos, últimos 30 dias, mínimo de cinco respostas por Assunto, menor acerto primeiro; desempate por maior amostra e ID. Sem amostra suficiente, orientar prática para diagnóstico sem inventar prioridade.
- Banco: migration aditiva com planos e itens, FKs `RESTRICT`, snapshot da justificativa e histórico preservado. ADRs 001, 002, 003, 005 e 006.
- Compatibilidade: autenticação, dashboard, histórico e resultados permanecem preservados; sem mudanças nos binários oficiais, framework ou integrações externas.
