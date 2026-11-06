# ADR-008 — Contratos e capacidades de persistência

## Status e contexto

**Aceito**, em 06/11/2026, pela aplicação da change
[refatorar-backend-com-solid](../../../openspec/changes/archive/2026-11-06-refatorar-backend-com-solid/design.md).
Complementa os ADRs [002](ADR-002-estrategia-de-autenticacao.md),
[003](ADR-003-politica-de-exclusao-catalogo.md),
[005](ADR-005-versionamento-editorial.md) e
[006](ADR-006-fronteira-de-transacoes.md), sem reescrever decisões históricas.

Versões e eventos não podem cumprir uma promessa de CRUD completo. Consultas
estáticas acopladas à infraestrutura impedem substituir colaboradores sem
alterar o caso de uso. O produto e o banco devem permanecer compatíveis.

## Decisão

A persistência usa uma cadeia abstrata única:
`db.Model → ModeloBase → ModeloAtualizavel → CrudMixin`.
`ModeloBase` oferece salvar e consultas; `ModeloAtualizavel` acrescenta
atualizar; `CrudMixin` acrescenta deletar. Todas ficam em
`app.models.crud_mixin`, preservando o import legado. Não criam tabelas.
Salvar respeita os invariantes do objeto; não promete atualização irrestrita.
Os guards ORM permanecem necessários para atribuições diretas e exclusões.

QuestaoVersao, QuestaoEvento, SimuladoVersao, SimuladoVersaoItem e
SimuladoEvento usam ModeloBase. PlanoEstudo e PlanoEstudoItem usam
ModeloAtualizavel. As outras treze Models preservam CrudMixin.

CRUD simples continua Active Record. Retornos, campos permitidos, commit,
rollback e flush com `confirmar=False` mantêm o contrato anterior. A fronteira
transacional externa continua responsável por seu único commit/rollback.

O recorte aprovado de nove consultas recebe contratos pequenos por
construtor, com registros independentes do ORM. A factory faz a composição
por aplicação, sem capturar usuário, conexão ou resultado. Somente HTTP pode
recuperar a composição corrente; Services não resolvem dependências.
A implementação e suas evidências são registradas por tarefa na change.

## Alternativas e consequências

Rejeitados CRUD genérico em Repository, herança múltipla até `db.Model`,
métodos de mutação que sempre falham e container externo de injeção.
A ausência de métodos incompatíveis é mudança deliberada da API Python;
rotas, payloads, schema e procedure permanecem. Escritas e autenticação
continuam no recorte existente; não se declara inversão completa do backend.

## Verificação

[Testes de CRUD](../../../backend/tests/unit/test_models_repository_controllers.py)
e [capacidades](../../../backend/tests/unit/test_persistencia_capacidades.py)
verificam retornos, campos permitidos, falhas e mappers. Metadados são
comparados ao baseline da change; integrações verificam guards e atomicidade
com MySQL real. Ver [relatório](../../../openspec/changes/archive/2026-11-06-refatorar-backend-com-solid/validacao.md).


## Composição e leitura consistente

Composicao fica em app.extensions['servicos'], criada por app.composition.compor na factory.
Cada aplicação recebe instâncias próprias, sem conexão/identidade/resultado capturado.
Controllers acessam app.http_composition.servicos; Services recebem colaboradores obrigatórios.
Adaptadores MySQL não montam envelopes HTTP nem decidem disponibilidade de Simulados.

EscoposLeitura fornece somente contexto opaco e instante. O adaptador delega ContextoLeitura.usar,
reutilizando contexto externo sem encerrá-lo. O mesmo diagnóstico atende dashboard e seleção
do plano. Gerar/recalcular recebem seletor; a função gerar recebe-o explicitamente. Locks e
TransactionManager não mudam. Não são abstraídas outras dependências de escrita/autenticação.
Alternativas em memória são exclusivas de unitários; integrações/E2E continuam MySQL real.
