# ADR-006 — Fronteira de transações

## 1. Status

**ACEITO**

## 2. Data da decisão

2026-08-29

## 3. Contexto

O `CrudMixin` atual executa `commit` e `rollback` em `salvar()`, `atualizar()` e `deletar()`. Isso atende ao CRUD simples do MVP. Casos futuros combinam usuário+perfil, prática+itens, simulado+composição, redação+versão, importação+itens e publicação+auditoria, que precisam concluir ou falhar como unidade.

## 4. Problema

Preservar o Active Record exigido pela disciplina e os métodos CRUD, permitindo transações atômicas de múltiplas Models sem acesso direto a `db.session` em Controllers ou SQL em Services.

## 5. Restrições do projeto e da disciplina

- CRUD simples permanece na Model.
- Services coordenam um caso de uso por classe.
- Controllers nunca acessam `db.session`.
- Services não executam SQL.
- Repository executa apenas acesso especializado e procedures, não CRUD repetido.
- O `CrudMixin` não será alterado nesta tarefa.

## 6. Opções analisadas

- **A — Cada Model confirma sua operação.**
- **B — Service controla diretamente a transação.**
- **C — Unit of Work explícita.**
- **D — Modelo híbrido Active Record + fronteira transacional.**

## 7. Vantagens de cada opção

- **A:** simples, igual ao MVP e fácil de apresentar.
- **B:** fronteira do caso de uso fica visível e atômica.
- **C:** abstrai sessão, commit/rollback e facilita testes de casos compostos.
- **D:** preserva CRUD simples atual e adiciona atomicidade somente onde necessária.

## 8. Desvantagens de cada opção

- **A:** commits intermediários deixam estado parcial.
- **B:** acesso direto à sessão no Service viola o padrão adotado e mistura infraestrutura.
- **C:** pode parecer camada excessiva e conflitar com métodos que confirmam internamente.
- **D:** exige dois modos claramente documentados para evitar commit acidental dentro de transação composta.

## 9. Riscos

Commit interno quebrar atomicidade; rollback duplicado; sessão em estado inválido após IntegrityError; Repository confirmar sem autorização; transação longa em upload/LLM; evento de auditoria gravado fora da operação; testes passarem no fluxo simples e falharem no composto.

## 10. Impacto no MVP atual

Os métodos atuais permanecem inicialmente para os dez casos de uso já validados. A evolução deverá introduzir compatibilidade, não remover abruptamente `salvar()`, `atualizar()` e `deletar()` nem alterar respostas.

## 11. Impacto nas 60 telas

Toda tela de escrita é afetada indiretamente. Casos críticos: onboarding, prática, composição/finalização de Simulado, Redação, importações, revisão/publicação, permissões, exclusão/transferência e auditoria. Telas somente leitura não abrem transações de escrita.

## 12. Impacto no MySQL

Operações compostas usarão uma única transação InnoDB, com escopo curto. Locks, isolation, retry e idempotência precisarão ser definidos por caso de uso. Chamadas externas não devem manter transação aberta; persistem intenção/checkpoint antes e resultado depois em transações separadas.

## 13. Impacto na API

Falha composta não poderá retornar sucesso parcial. Erros devem preservar contratos atuais e acrescentar correlação/idempotência quando necessário. Uploads e processamentos longos tendem a contratos assíncronos futuros, ainda não definidos.

## 14. Impacto nos testes

Testar rollback completo após falha na última etapa, commits simples, IntegrityError, concorrência, retry, idempotência e auditoria atômica/outbox quando aplicável. Os 29 testes atuais permanecem regressão obrigatória.

## 15. Impacto em segurança

Atomicidade evita concessão parcial de permissão e publicação sem auditoria. Transações devem ser curtas para reduzir negação de serviço por locks. Dados sensíveis não entram em logs de rollback ou exceções.

## 16. Recomendação técnica

Fica aceita a **opção D — Active Record com fronteira transacional**, sob estas regras:

- CRUD permanece nas Models;
- o Service define a fronteira do caso de uso e utiliza uma abstração `TransactionManager`/`UnitOfWork`;
- o Service não acessa `db.session` e não executa SQL;
- a infraestrutura realiza `begin`, `commit` e `rollback`;
- Models adicionam, alteram, removem e executam `flush` quando necessário;
- Models não encerram uma transação externa;
- novos módulos adotam a fronteira transacional desde o início;
- o MVP será migrado gradualmente, preservando os 29 testes como regressão;
- savepoints serão usados apenas em lotes cujo processamento parcial seja intencional e documentado;
- nenhuma biblioteca adicional de Unit of Work é selecionada nesta decisão.

Repository participa da mesma unidade quando necessário, sem commit autônomo e sem repetir CRUD simples.

## 17. Consequências da recomendação

O `CrudMixin` precisará futuramente distinguir operação autônoma de operação participante sem duplicar métodos nas Models. A equipe deverá proibir commits escondidos em casos compostos e documentar quem possui a transação.

## 18. Estratégia de adoção gradual

1. Confirmar interpretação do Active Record com o professor.
2. Definir contrato da fronteira transacional sem SQL no Service.
3. Criar testes de caracterização do `CrudMixin` atual.
4. Adaptar um caso composto piloto.
5. Manter CRUD legado em modo autônomo.
6. Migrar casos compostos módulo a módulo.
7. Definir idempotência e integração de eventos/auditoria.

## 19. Critérios de aceite

- CRUD simples continua disponível nas Models.
- Controller e Service não acessam `db.session` nem SQL.
- Caso composto confirma uma vez ou reverte tudo.
- Repository não confirma de forma independente.
- Integração externa não segura transação aberta.
- Falhas concorrentes e retries são testados.
- Os 29 testes permanecem aprovados.

## 20. Pontos que dependem do professor ou da equipe

Permanecem para definição operacional da equipe: contrato da abstração `TransactionManager`/`UnitOfWork`; assinatura futura compatível dos métodos Active Record; isolation/retry; estratégia de eventos/auditoria; e tratamento de operações assíncronas. Nenhuma biblioteca adicional de Unit of Work foi selecionada.

## 21. Decisão final

**ACEITO.**
