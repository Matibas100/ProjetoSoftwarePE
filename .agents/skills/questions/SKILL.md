---
name: questions
description: Identifica dúvidas e decisões pendentes no contexto atual, apresenta primeiro uma lista numerada para aprovação e depois conduz a resolução de uma pendência por vez, com explicação breve, investigação somente leitura quando necessária, recomendação e confirmação do usuário. Use somente quando o usuário invocar explicitamente `/questions` ou `$questions`, pedir este fluxo nominalmente ou solicitar que dúvidas sejam levantadas e resolvidas uma por vez antes de continuar.
---

# Questions

Conduzir um ciclo temporário de esclarecimento. Não avançar na implementação da tarefa principal enquanto o ciclo estiver ativo, mas permitir investigação somente leitura necessária para resolver a pendência atual.

## Fluxo

1. Analisar o contexto atual e identificar somente dúvidas materiais que dependam de decisão ou confirmação do usuário.
2. Apresentar todas as dúvidas em uma lista numerada, com títulos curtos. Não iniciar a primeira pendência nessa resposta.
3. Pedir autorização para começar e aguardar a resposta do usuário.
4. Após autorização, apresentar somente uma pendência por vez:
   - usar o título `Pendência DD/DD — <assunto>`, com posição atual e total de
     pendências em dois dígitos, por exemplo `Pendência 03/08 — Idempotência`;
   - explicar brevemente o problema e seu impacto;
   - sempre que ajudar, usar um exemplo curto e concreto — como payload,
     cenário, tabela ou código — no lugar de uma explicação textual longa;
   - dar uma recomendação objetiva com motivo curto, quando houver base suficiente;
   - fazer uma única pergunta focada e aguardar.
5. Interpretar `sim`, `y`, `ok` ou equivalente como confirmação somente quando responderem diretamente à pendência atual.
6. Se a resposta não resolver a pendência, permanecer nela e pedir apenas o esclarecimento necessário.
7. Quando a pendência for resolvida, registrar mentalmente a decisão, reavaliar as restantes e só então apresentar a próxima.
8. Incorporar novas dúvidas materiais descobertas durante o ciclo, preservando
   o fluxo de uma por vez e atualizando o total exibido em `DD/DD`.
9. Depois da última pendência, apresentar resumo curto das decisões consolidadas.
10. Encerrar o efeito da skill após o resumo. Não manter este modo em turnos posteriores sem nova invocação.

## Regras

- Não mostrar antecipadamente detalhes da próxima pendência.
- Não repetir a lista completa durante o ciclo, salvo pedido do usuário.
- Manter a posição da pendência atual baseada na lista consolidada e usar zero à
  esquerda até 99 itens; se o total mudar, atualizar o denominador nas respostas
  seguintes.
- Não forçar exemplo quando ele não melhorar o entendimento.
- Não transformar recomendações em decisões já tomadas.
- Permitir leituras, buscas, consultas e outros comandos comprovadamente somente leitura quando forem necessários para explicar ou resolver a pendência atual.
- Evitar edições, comandos de escrita, integrações mutáveis e outras ações com efeito colateral durante o ciclo.
- Quando uma ação de escrita for necessária para resolver a pendência, explicar brevemente seu escopo e pedir autorização explícita ao usuário antes de executá-la.
- Se o usuário autorizar a escrita, executar somente o escopo autorizado, seguindo o fluxo normal, as instruções do projeto e os controles de segurança aplicáveis; depois retornar à pendência atual.
- Se não houver dúvidas materiais, informar isso brevemente e encerrar a skill sem pedir autorização.
- Se o usuário cancelar ou mudar de assunto, encerrar o ciclo e seguir a nova solicitação.
