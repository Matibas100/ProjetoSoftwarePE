# ADR-004 — Unicidade de Assunto

## 1. Status

**ACEITO**

## 2. Data da decisão

2026-08-29

## 3. Contexto

`assuntos` possui nome e `materia_id`, mas não possui constraint de unicidade. A collation atual é `utf8mb4_unicode_ci`, que tende a ignorar diferenças de caixa e acento em comparações, porém não resolve espaços repetidos, normalização Unicode, equivalências pedagógicas ou importações. O Design prevê conflito compreensível e taxonomia controlada.

## 4. Problema

Evitar dois Assuntos ativos equivalentes dentro da mesma Matéria sem impedir nomes iguais em Matérias diferentes nem destruir histórico arquivado.

## 5. Restrições do projeto e da disciplina

- Validação de negócio ocorre no Service e integridade concorrente no MySQL.
- CRUD simples continua na Model.
- Importações devem sinalizar conflito, não criar duplicidade silenciosa.
- Alteração de nome ou Matéria deve respeitar a mesma regra.
- A política de arquivamento depende do ADR-003.

## 6. Opções analisadas

- **A — Nome livre:** duplicidade permitida.
- **B — `UNIQUE(materia_id, nome)`:** unicidade conforme collation do banco.
- **C — Nome normalizado único por Matéria:** chave composta com valor canônico definido.
- **D — Código interno único e nome livre:** identidade técnica independente do rótulo.

## 7. Vantagens de cada opção

- **A:** máxima flexibilidade e zero migration inicial.
- **B:** simples, garantida pelo banco e suficiente para caixa/acentos conforme collation.
- **C:** trata espaços e Unicode de modo previsível e oferece mensagem coerente em API/importação.
- **D:** facilita integrações e renomeações sem tornar nome identidade.

## 8. Desvantagens de cada opção

- **A:** degrada filtros, importações, métricas e seleção pedagógica.
- **B:** comportamento depende da collation e não captura todos os equivalentes; mudança de collation altera semântica.
- **C:** exige algoritmo versionado e saneamento; normalização agressiva pode unir conceitos distintos.
- **D:** não impede dois Assuntos ativos iguais e transfere a ambiguidade ao usuário.

## 9. Riscos

Dados atuais conflitantes; corrida entre validação e insert; acentos tratados de forma inesperada; arquivado impedir nova criação; alteração de Matéria colidir; imports com grafias divergentes; código interno exposto como regra pedagógica.

## 10. Impacto no MVP atual

Os endpoints e `to_dict()` podem permanecer compatíveis. Services passariam futuramente a detectar conflito e o banco garantiria a condição. Antes da constraint, é obrigatório auditar e resolver duplicidades existentes sem descarte automático.

## 11. Impacto nas 60 telas

Impacto direto em ADM-CON-002 e nos cadastros/importações que selecionam ou criam Assuntos. Impacto indireto em filtros e métricas de ALU-ONB-003, ALU-QUE-001, Questões, Simulados, Resumos e desempenho.

## 12. Impacto no MySQL

Se aprovada a opção C, o schema provavelmente armazenará um valor normalizado controlado e uma constraint composta com `materia_id`. A implementação exata para itens arquivados depende do ADR-003 e das limitações de índices condicionais no MySQL.

## 13. Impacto na API

POST/PUT devem retornar 409 para conflito, com mensagem indicando a Matéria sem revelar dados indevidos. Alterar `materia_id` também valida unicidade no destino. O contrato atual pode manter os mesmos campos de resposta.

## 14. Impacto nos testes

Casos de caixa, espaços externos/internos, acento, Unicode, mesma Matéria, Matérias diferentes, concorrência, mudança de Matéria, arquivamento/reativação e importação. Os testes atuais continuam como regressão.

## 15. Impacto em segurança

Normalização precisa limitar tamanho antes e depois, evitar caracteres invisíveis abusivos e não depender de SQL construído dinamicamente. Mensagens de conflito devem obedecer autorização.

## 16. Recomendação técnica

Fica aceita a **opção C**, mantendo identificador interno estável e a seguinte estrutura conceitual para `assuntos`:

- `nome`, preservando a forma original apresentada ao usuário;
- `nome_normalizado`, derivado de regra única do domínio;
- `UNIQUE(materia_id, nome_normalizado)`.

A normalização aplicará `trim`, colapso de espaços internos, normalização Unicode, comparação sem diferença de caixa e equivalência entre variações apenas de acento.

Regras complementares:

- a duplicidade permanece bloqueada quando o Assunto equivalente estiver arquivado;
- deve ser oferecida reativação do registro arquivado em vez de criar duplicata;
- troca de Matéria valida conflito no destino;
- migration futura produz relatório de duplicidades antes da constraint;
- nenhum registro será mesclado automaticamente.

## 17. Consequências da recomendação

O algoritmo de normalização vira contrato de domínio e deve ser igual em criação, atualização e importação. A constraint trata concorrência; o Service oferece erro legível. Mudanças futuras no algoritmo exigirão análise de dados e migration.

## 18. Estratégia de adoção gradual

1. Definir equivalência e collation com equipe pedagógica.
2. Auditar nomes atuais e gerar relatório de colisões.
3. Resolver colisões manualmente.
4. Preencher valor normalizado em etapas.
5. Criar constraint após validação.
6. Ativar conflito nos Services/importações.
7. Testar movimentação entre Matérias e arquivamento.

## 19. Critérios de aceite

- Equivalências aprovadas são documentadas e determinísticas.
- Matérias diferentes aceitam o mesmo nome.
- A mesma Matéria não aceita dois Assuntos equivalentes, mesmo quando o registro anterior está arquivado.
- POST/PUT/importação apresentam 409 previsível.
- Nenhum dado existente é descartado automaticamente.
- Mudança de Matéria e reativação obedecem a mesma constraint.

## 20. Pontos que dependem do professor ou da equipe

Permanecem para definição operacional da equipe: tratamento de pontuação e caracteres especiais; algoritmo/collation compatível com a equivalência aceita; eventual código interno adicional; resolução manual das colisões existentes; e mensagem final ao usuário.

## 21. Decisão final

**ACEITO.**
