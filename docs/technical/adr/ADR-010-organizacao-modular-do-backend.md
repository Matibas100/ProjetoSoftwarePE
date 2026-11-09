# ADR-010 — Organização modular do backend

**Aceito**, em 07/11/2026, pela change
[`organizar-backend-em-monolito-modular`](../../../openspec/changes/archive/2026-11-07-organizar-backend-em-monolito-modular/design.md).
Complementa os ADRs 002, 006, 008 e 009.

## Decisão

Organizar o recorte entregue em seis módulos de `backend/app/modules/`:
Contas, Conteúdo, Práticas, Simulados, Desempenho e Plano de Estudos.
Cada proprietário contém suas rotas, Controllers, Services, Models e
Repositories aplicáveis. Desempenho é projeção, sem tabela própria.
O fluxo `Route → Controller → Service → Model/Repository → MySQL` permanece.

Blueprints próprios são agregados em `app.routes.api_blueprint`, sob `/api`
uma única vez. URLs, métodos, payloads, autorização, hooks, CLI e contratos
legais permanecem. Apenas endpoints internos ganham namespace do módulo.

Módulos colaboram por `api.py` com `__all__` explícito ou por Protocols/DTOs
de `app.contracts`. APIs expõem operações, DTOs e projeções de leitura
delimitadas; nunca Models, instâncias ORM ou Repositories completos.
Imports privados cruzados são proibidos, inclusive dentro de funções.
A composição explícita por aplicação liga implementações e contratos.
O registro de Models é a outra exceção estrita para importar proprietários.

`extensions.py` conserva um único SQLAlchemy/CORS. Configuração, transações,
contexto de leitura, exceções e adaptação HTTP continuam compartilhados.
`core` contém somente persistência abstrata, relógio UTC, paginação,
primitivas puras de validação e o health check de infraestrutura.
Não se introduz ORM, sessão, container, tabela ou dependência nova.

As bases do ADR-008 passam a `app.core.persistencia`.
`app.models.crud_mixin` reexporta estaticamente as mesmas três classes e `db`.
`app.models` registra/reexporta as 21 classes canônicas (4+7+1+7+0+2).
Nenhuma tabela possui duas classes. As pastas globais de negócio são retiradas
ao concluir a transição; não há aliases dinâmicos ou cópia em `legacy`.

## Adendo ao ADR-009

O lock exato da linha de usuário pertence a Contas, sem filtro novo de ativo.
A eliminação especializada dos planos próprios passa de Privacidade para o
Repository de Plano. Um Service participante de Plano delega a operação,
sem commit ou TransactionManager próprios e sem revalidar consentimento.

Recusar/Revogar recebem esse comportamento por construtor. Contas não importa
Plano; a composição liga os participantes e a Controller usa suas instâncias.
Preserva-se a ordem lock → replay/revisão/versão → negativa → eliminação →
resposta, sob uma única confirmação/rollback. Replay não reaplica a eliminação.
Geração e consulta continuam validando permissão após o mesmo lock, antes de
replay, snapshot, diagnóstico ou item. Não existe endpoint novo de eliminação.

## Consequências e verificação

Seis módulos refletem a coesão das transações entregues. A divisão mais
granular do plano mestre continua como roadmap. Rejeitados módulo por entidade,
acesso cruzado à persistência e API pública usada para exportar Repository.

Movimentos preservam o baseline de HTTP/CLI, metadata, guards e hashes SQL/legais.
Testes de arquitetura protegem camadas, fronteiras e factories independentes;
integrações MySQL verificam histórico, locks, replay e rollback real.
O [mapa modular](../organizacao-modular.md) registra as interfaces e a transição.

## Adendo — Tutor pontual (09/11/2026)

A change `adicionar-tutor-revisao-com-gemini` acrescenta o sétimo proprietário,
`tutor_ia`, sem Model/Repository: sua consulta externa não cria entidade ou CRUD.
Controller adapta HTTP; `GerarTutoriaService` valida e coordena a permissão pública
`ValidarPermissaoTutoriaService` de Contas, o limite local e `GeminiService` pelo
contrato textual `GeradorTutoria`. A leitura transacional de Contas termina antes
da rede. Configuração, cliente e limite são próprios de cada aplicação; inicializar
não consulta Gemini. Os 21 mappers e as fronteiras existentes permanecem.
