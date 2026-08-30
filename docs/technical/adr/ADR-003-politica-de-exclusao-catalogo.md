# ADR-003 — Política de exclusão do catálogo acadêmico

## 1. Status

**ACEITO**

## 2. Data da decisão

2026-08-29

## 3. Contexto

Hoje, `Materia → Assunto` usa `ON DELETE CASCADE` e relacionamento `delete-orphan`; `Assunto → Questao` usa `ON DELETE RESTRICT`. O Design aprovado exige bloqueio de exclusão vinculada, ausência de cascata silenciosa e preservação do conteúdo já utilizado em tentativas e históricos. Resumos e outras referências futuras ainda não existem no schema.

## 4. Problema

Definir quando Matéria e Assunto podem ser excluídos fisicamente, arquivados ou ter vínculos transferidos, sem apagar conteúdo dependente ou reescrever histórico.

## 5. Restrições do projeto e da disciplina

- MySQL deve garantir integridade por FKs coerentes.
- CRUD simples permanece na Model; avaliação de impacto pode usar Repository.
- Services aplicam a política e retornam conflito compreensível.
- Nenhuma tentativa, versão publicada ou histórico pode mudar retroativamente.
- O contrato atual deve evoluir com compatibilidade planejada.

## 6. Opções analisadas

- **A — Manter cascade.**
- **B — Bloquear exclusão quando houver qualquer vínculo.**
- **C — Arquivamento/soft delete.**
- **D — Transferência explícita antes da exclusão.**
- **E — Combinação de bloqueio, arquivamento e transferência.**

## 7. Vantagens de cada opção

- **A:** operação simples e limpeza automática de árvore não utilizada.
- **B:** máxima previsibilidade e proteção por FK.
- **C:** preserva identidade, referências e possibilidade de reativação.
- **D:** permite reorganizar taxonomia sem perder conteúdo.
- **E:** oferece regra segura para históricos e uma saída operacional para reorganização.

## 8. Desvantagens de cada opção

- **A:** apaga silenciosamente e contradiz o Design; o cascade pode alcançar dados inesperados.
- **B:** gera bloqueios permanentes mesmo para itens obsoletos.
- **C:** exige filtros por status, política de nomes e proibição de uso novo.
- **D:** transferência é caso de uso complexo, com validações e auditoria.
- **E:** possui mais estados e precisa de mensagens/ações administrativas claras.

## 9. Riscos

Cascade existente apagar Assuntos; ORM e FK discordarem; item arquivado continuar selecionável; transferência misturar taxonomias; exclusão física de item já referenciado; contagens de impacto incompletas; concorrência entre validação e exclusão.

## 10. Impacto no MVP atual

A regra atual de Matéria não satisfaz a política proposta, embora o Service já espere poder retornar conflito. Assunto com Questões já é protegido por `RESTRICT`. Nenhuma alteração é feita agora; eventual correção exigirá migration e testes de regressão.

## 11. Impacto nas 60 telas

Impacto direto em ADM-CON-001 e ADM-CON-002: confirmação, contagem de vínculos, bloqueio, arquivamento e transferência. Impacto indireto em filtros/selects, Questões, Resumos, Simulados, Práticas e históricos que referenciam a taxonomia.

## 12. Impacto no MySQL

Se aprovado, FKs do catálogo devem tender a `RESTRICT` para vínculos preserváveis. Matéria/Assunto poderão ganhar estado de arquivamento. Novas entidades que usam catálogo devem referenciar identidade estável ou versão apropriada. Não se propõe SQL nesta etapa.

## 13. Impacto na API

O `DELETE` atual deve continuar retornando 204 apenas quando a exclusão física for permitida e 409 quando houver vínculo. Arquivamento, consulta de impacto e transferência serão casos de uso separados com contratos ainda a definir; não devem ser escondidos em `DELETE`.

## 14. Impacto nos testes

Cobrir cada combinação de vínculo, cascata inexistente, arquivamento, reativação, transferência, conflito concorrente, seleção apenas de ativos e preservação de tentativa/histórico. Manter os 17 testes atuais de Matéria/Assunto como regressão, ajustando apenas após contrato aprovado.

## 15. Impacto em segurança

Ações destrutivas exigem permissão, confirmação, motivo e auditoria; transferência/arquivamento não pode permitir elevação de acesso nem inferir conteúdo restrito por contagens detalhadas.

## 16. Recomendação técnica

Fica aceita a **opção E**, com as seguintes regras:

- substituir futuramente o `ON DELETE CASCADE` de Matéria para Assunto;
- usar `RESTRICT` em vínculos históricos;
- tratar arquivamento como ciclo de vida, não como exclusão física disfarçada;
- exigir transferência explícita, confirmada, transacional e auditada;
- permitir exclusão física somente para registro sem vínculo e sem uso histórico;
- impedir exclusão de Matéria com Assuntos;
- impedir exclusão de Assunto com Questões, Resumos ou histórico;
- impedir novos vínculos com registros arquivados, preservando consultas históricas.

Política aceita por cenário:

- **Matéria sem vínculos:** exclusão física permitida se nunca utilizada; caso contrário, arquivar.
- **Matéria com Assuntos:** exclusão bloqueada; transferir/arquivar os Assuntos antes.
- **Assunto sem conteúdo:** exclusão física permitida se nunca utilizado; caso contrário, arquivar.
- **Assunto com Questões ou Resumos:** exclusão bloqueada; arquivamento ou transferência explícita.
- **Registro usado em tentativa/histórico:** nunca excluir fisicamente nem reatribuir retroativamente; preservar identidade/versionamento.

## 17. Consequências da recomendação

O cascade silencioso deverá ser removido por migration futura. Listagens precisarão distinguir ativos/arquivados, e impacto/transferência exigirão consultas especializadas. Haverá mais segurança e rastreabilidade, ao custo de regras adicionais.

## 18. Estratégia de adoção gradual

1. Auditar dados e FKs reais.
2. Aprovar semântica de “utilizado”.
3. Introduzir arquivamento sem remover contratos atuais.
4. Filtrar itens arquivados de novos usos.
5. Trocar cascade por restrição em migration testada.
6. Criar impacto e transferência como casos de uso separados.
7. Validar históricos e regressão.

## 19. Critérios de aceite

- Nenhuma exclusão vinculada produz cascade silencioso.
- Tentativas e históricos mantêm a referência original.
- 409 informa o tipo de impedimento sem vazar dados.
- Arquivado não entra em novo conteúdo, mas permanece consultável onde necessário.
- Transferência é explícita, atômica e auditada.
- Exclusão física só ocorre sem vínculos e sem uso histórico.

## 20. Pontos que dependem do professor ou da equipe

Permanecem para definição operacional da equipe: critérios verificáveis de “já utilizado”; prazo de retenção; experiência de arquivamento e transferência; visibilidade de itens arquivados; política específica para conteúdo oficial; e plano seguro da migration que substituirá o `CASCADE`.

## 21. Decisão final

**ACEITO.**
