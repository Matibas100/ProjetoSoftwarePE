# Design: contratos e capacidades de persistência com SOLID

## Context

Ver `proposal.md` para motivação. A referência é o estado local após `consolidar-entrega-academica`, arquivada em 06/11/2026, ainda com alterações legítimas sem commit. Esta change não pressupõe working tree limpo nem autorização para publicar.

Os exemplos fornecidos pelo professor enfatizam: motivos de mudança no SRP; extensão por comportamento intercambiável no OCP; preservação do contrato na herança no LSP; interfaces pequenas no ISP; contratos e injeção de dependências no DIP. Separar pastas ou usar uma interface apenas como anotação não comprova esses princípios.

Hoje as consultas são métodos estáticos que importam Repositories concretos. `CrudMixin(db.Model)` oferece salvar/atualizar/deletar/consultar a todas as entidades, incluindo snapshots e eventos que proíbem parte dessas operações. `ContextoLeitura` já protege snapshot e relógio compartilhados entre desempenho, dashboard e plano. A correção deve preservar essas garantias, não desmontá-las para simplificar a injeção.

## Goals / Non-Goals

**Goals:** demonstrar os cinco princípios com dependências realmente substituíveis e uma hierarquia de persistência coerente; manter API, modelos de domínio, desempenho das leituras em lote e vinte fluxos atuais.

**Non-Goals:** criar interfaces para todas as Models, injetar todos os Services de escrita/autenticação, trocar Active Record por Repository CRUD, substituir SQLAlchemy, criar um framework de DI ou declarar adesão absoluta a SOLID. Métodos internos dos Services selecionados e capacidades das Models podem mudar coordenadamente; a API pública e o banco não mudam.

## Decisions

### 1. Nove casos de uso de leitura como recorte fechado

| Domínio | Classes a converter para instâncias com dependências obrigatórias no construtor |
|---|---|
| Catálogo | `ListarMateriasAdminService`, `ListarAssuntosAdminService` |
| Questões | `BuscarQuestoesPorAssuntoService`, `ListarQuestoesAlunoService` |
| Simulados | `ListarSimuladosAlunoService`, `ListarHistoricoSimuladosService` |
| Desempenho | `ConsultarDesempenhoService`, `ConsultarDashboardAlunoService`, `ConsultarDashboardAdminService` |

Todas as chamadas dessas classes no repositório serão migradas: Controllers, testes e consumidores internos. `ConsultarTentativaSimuladoService`, consultas editoriais e as escritas mantêm sua lógica/contratos atuais, exceto ajustes necessários à nova hierarquia de Models.

`SelecionarPlanoService`, `GerarPlanoService`, `RecalcularPlanoService` e a função interna `gerar` receberão as dependências necessárias para reutilizar o diagnóstico convertido. Isso é adaptação da cadeia de composição, sem trocar a fórmula, a seleção, os locks ou a fronteira transacional do plano. Não importar o módulo de composição dentro de um Service para resolver dependências implicitamente.

Alternativa rejeitada: converter todos os Services numa única refatoração. O recorte atravessa os domínios discutidos e permite comprovação real sem reescrita do MVP.

### 2. Protocols pequenos e dados independentes do ORM

Adicionar `backend/app/contracts/` com arquivos Python por domínio e `typing.Protocol` da biblioteca padrão. Sem dependência adicional. Os Protocols serão definidos pelas necessidades dos consumidores e não herdarão de classes concretas de Repository. Não importar Flask, SQLAlchemy, PyMySQL ou Models nesses contratos.

Os dados de consulta serão registros explícitos (`TypedDict`/dataclasses com campos nomeados e tipos), coleções e escalares; não sessão, `Row`, entidade ORM, consulta SQL ou um contrato genérico cheio de `Any`. A transformação de representação ORM para registro é do adaptador técnico; validação de filtros, composição do envelope, elegibilidade e decisões de negócio permanecem no respectivo Service.

Contratos e semântica mínima:

| Contrato | Operações e dados necessários |
|---|---|
| `ConsultaMateriasAdmin` | `listar(filtros, pagina, limite)` retorna registros de Matéria, Área e contagens, mais total; sem montar envelope HTTP |
| `ConsultaAssuntosAdmin` | `listar(filtros, pagina, limite)` retorna registros de Assunto, Matéria, Área e contagem de Questões, mais total |
| `ConsultaQuestoesPorAssunto` | `buscar_por_assunto(assunto_id)` devolve o conteúdo administrativo legado da Stored Procedure na mesma ordem |
| `ConsultaQuestoesElegiveis` | `listar(filtros, pagina, limite)` devolve conteúdo publicado seguro sem gabarito/explicação, mais total |
| `ConsultaCatalogoSimulados` | listar publicados paginados, obter composições em lote e IDs de tentativas próprias em andamento; sem métodos de escrita ou cálculo de disponibilidade |
| `ConsultaHistoricoSimulados` | listar tentativas concluídas próprias com título e resultado histórico em lote, mais total |
| `ConsultaElegibilidadeVersoes` | `executar(ids)` devolve mapa de versões elegíveis pelo contrato de conteúdo já existente; o consumidor pode consultar as chaves sem decidir elegibilidade no SQL de outro domínio |
| `ConsultaMetricasDesempenho` | `agregar(contexto, usuario_id, inicio, fim)` devolve contagens gerais e grupos com classificação histórica |
| `ConsultaAtividadesAluno` | `atividades(contexto, usuario_id, inicio, fim)` devolve as últimas atividades pelo contrato atual |
| `ConsultaContagensAdmin` | `administrativo(contexto)` devolve somente as contagens globais atuais |
| `DiagnosticoAluno` | `executar(usuario_id, filtros=None, contexto=None, instante=None)` retorna o mesmo diagnóstico público/reutilizável atual |
| `EscoposLeitura` | `usar(contexto=None, instante=None)` fornece um context manager de leitura consistente com instante; não oferece SQL ao Service |

Para verificar existência de Assunto na busca legada, usar dependência pequena `Callable[[int], bool]`, ligada a `Assunto.buscar_por_id` na composição. Essa ligação não transfere CRUD para um Repository nem requer uma interface de CRUD para cada Model.

Implementações concretas de consulta/adaptadores ficam em `repositories/`, junto aos acessos especializados existentes. Podem delegar a métodos existentes e converter seus resultados, sem copiar SQL ou duplicar CRUD. `ConsultarVersoesElegiveisService` pode satisfazer estruturalmente o contrato de elegibilidade já fornecido por Questões; o consumidor não importa sua classe concreta. A existência de métodos extras numa implementação não os inclui no Protocol oferecido ao consumidor.

Alternativas rejeitadas: um único `Repository` com todos os métodos do sistema, Protocols que devolvem objetos SQLAlchemy e uma interface por getter. Os contratos acima representam capacidades de leitura, não réplicas de classes concretas.

### 3. Composição explícita na inicialização da aplicação

Adicionar `backend/app/composition.py` como ponto que conhece os Protocols, Services e implementações MySQL. A factory constrói uma composição por aplicação e a registra em `app.extensions`, por chave própria. As instâncias são sem estado de usuário, sem sessão/conexão aberta, sem resultado de consulta e sem cache privado; recebem somente colaboradores.

Controllers continuam classes por recurso, interpretam HTTP e usam os Services já compostos. Um acessor técnico pequeno pode recuperar a composição da aplicação corrente. Services recebem colaboradores no construtor, não consultam `current_app` nem importam composição, Models ou Repositories concretos no recorte de consultas. Os valores padrão dos construtores não instanciam silenciosamente uma implementação MySQL.

```text
Controller --> Service --> Protocol de consulta
                              ^
                              |
                     Repository/adaptador MySQL

Application factory --> compoe e fornece os colaboradores
```

Testes unitários instanciam o mesmo Service com alternativas em memória apenas para verificar contrato/regra; integrações usam composição real e MySQL real. Não criar uma fachada estática `executar` que monte o Repository concreto a cada chamada. Classes e imports públicos dos Services podem permanecer com os nomes atuais, mas a chamada passa a ser de instância e os consumidores internos serão atualizados.

Alternativas rejeitadas: container externo, singleton global e injeção por monkeypatch em produção. Tornariam o fluxo menos explícito ou arriscariam compartilhar identidade/conexão entre aplicações.

### 4. Snapshot e transações continuam pertencendo à mesma operação

A implementação padrão de `EscoposLeitura` delega a `ContextoLeitura.usar`. O Service recebe um contexto opaco, seu relógio e uma abstração para abrir/reusar o escopo. Só o Repository técnico conhece o mecanismo de executar consultas. Não ampliar o Protocol para aceitar SQL no Service.

Dashboard do Aluno abre um escopo e passa a mesma instância/instante ao diagnóstico e às atividades. O diagnóstico aceita contexto externo autorizado e não o fecha, confirma ou reverte. Geração/recálculo do plano continuam usando o contexto da transação já aberta pelo `PlanoEstudoRepository.contexto`, com mesmo relógio e isolamento REPEATABLE READ.

A composição injeta o mesmo `ConsultarDesempenhoService` como `DiagnosticoAluno` no dashboard e na seleção do plano. Instâncias dos Services de plano recebem o seletor; a função interna `gerar` recebe esse seletor explicitamente, sem fallback a classe concreta. Os demais colaboradores de escrita do plano ficam no recorte existente, sem promessa de inversão completa dessas operações.

`TransactionManager` mantém o único commit/rollback do caso composto, e `confirmar=False` mantém flush sem commit das Models. Todos os CALLs ficam nos Repositories, sem mudança na procedure. Consultas em lote continuam em lote e os locks de escrita não migram para GETs.

Alternativa rejeitada: cada Repository abrir seu snapshot. Isso permitiria diagnóstico e atividades divergentes e quebraria o consumo pelo plano.

### 5. Uma cadeia de herança, três capacidades de persistência

Extrair a implementação atual, preservando seu comportamento, para esta hierarquia abstrata:

```text
db.Model
   ^
   |
ModeloBase             salvar, listar_todos, buscar_por_id
   ^
   |
ModeloAtualizavel      acrescenta atualizar
   ^
   |
CrudMixin              acrescenta deletar
```

Todas as bases usam `__abstract__ = True`; cada Model concreta herda de apenas uma delas. O nome/import de `CrudMixin` permanece compatível para Models convencionais. `salvar` persiste estado válido respeitando os invariantes da entidade; não promete alterar qualquer entidade indiscriminadamente. Manter retorno, rollback, `confirmar=True/False`, flush e commit do comportamento atual.

Distribuição fechada das vinte Models:

| Base | Models |
|---|---|
| `ModeloBase` | `QuestaoVersao`, `QuestaoEvento`, `SimuladoVersao`, `SimuladoVersaoItem`, `SimuladoEvento` |
| `ModeloAtualizavel` | `PlanoEstudo`, `PlanoEstudoItem` |
| `CrudMixin` | `AreaEnem`, `Materia`, `Assunto`, `AssuntoTransferencia`, `Questao`, `Usuario`, `Sessao`, `AuthLimite`, `PraticaTentativa`, `Simulado`, `SimuladoRascunhoItem`, `SimuladoTentativa`, `SimuladoResposta` |

Os cinco snapshots/eventos não terão métodos públicos `atualizar` ou `deletar`. Planos/itens não terão `deletar`; `atualizar` continua limitado aos campos e transições válidos já existentes. Não remover as proteções ORM `before_update`/`before_delete`, incluindo os guards de planos, nem liberar alteração por atribuição direta seguida de `salvar`/flush. O catálogo fixo e outros estados continuam limitados por seus casos de uso; esta change não inventa novas restrições de domínio para as treze Models convencionais.

Os testes que hoje chamam atualização/exclusão em imutáveis esperando `ConflitoError` serão adaptados: verificar ausência da capacidade e, separadamente, tentar mutação/exclusão via ORM e confirmar recusa, rollback e histórico intacto. Não manter os métodos incompatíveis apenas para preservar um teste interno. Os 29 testes originais e os comportamentos HTTP mantêm suas expectativas.

Essa é uma mudança interna deliberada de contrato Python; consumidores externos da API não a observam. Nenhuma coluna, tabela, FK, índice, constraint, relacionamento de domínio ou nome de entidade muda. Validar metadados/mappers com vinte tabelas de domínio e comparar com schema real das migrations 000–009; não usar `create_all` ou DDL automático para adaptar o banco à refatoração.

Alternativas rejeitadas: retirar os guards de imutabilidade, oferecer métodos que sempre falham no contrato de CRUD e usar herança múltipla por dois caminhos de `db.Model`.

### 6. Evidência de SOLID em código e documentação

- SRP: Controllers adaptam transporte; Services validam/coordenam um caso; Repositories consultam; Models persistem; composição configura. Validar motivos de mudança, sem impor uma classe por método auxiliar.
- OCP/DIP: executar um Service selecionado com duas implementações do mesmo contrato e trocar a implementação pela composição sem editar sua lógica. Um Protocol somente anotado, mas ignorado por chamada à classe concreta, reprova a verificação.
- ISP: contratos expõem somente as leituras necessárias; capacidades de persistência não obrigam entidades imutáveis a oferecer mutações.
- LSP: Models convencionais mantêm o contrato de CRUD; implementações válidas de consulta mantêm resultados/erros combinados; entidades imutáveis não se apresentam como CRUD completo.

Registrar a decisão em `docs/technical/adr/ADR-008-contratos-e-capacidades-de-persistencia.md`, após aprovação desta change, sem editar o conteúdo histórico dos ADRs aceitos. Atualizar o índice e as referências normativas necessárias para apontar a nova hierarquia, preservando CRUD nas Models e um único caminho até `db.Model`.

Criar `docs/technical/aplicacao-solid.md` com um exemplo real por princípio, classes/arquivos e testes que o comprovam, além dos limites do recorte. Referenciar os materiais de Gleison Brito/Brio fornecidos pelo usuário por título e conceito; não copiar os PDFs para o repositório nem usar caminhos locais de Downloads como dependência da documentação.

O diagrama de domínio atual mantém as vinte entidades e recebe a herança correta. Uma visão separada de aplicação mostra os Protocols, implementações, Services e composição, sem apresentar DTO como nova entidade persistida. README e matriz acadêmica mantêm as vinte funcionalidades e apontam para os exemplos SOLID; refatorações não contam como funcionalidade adicional. Não produzir roteiro nem vídeo.

### 7. Critérios de aceite e validação

1. Nenhum dos nove Services importa uma Model/Repository concreto, usa `current_app`, executa SQL ou resolve seu próprio colaborador de consulta. Contratos não importam infraestrutura. Controllers não acessam o banco.
2. Composição liga as implementações padrão, permite alternativas nos testes e não captura identidade, conexão ou estado de requisição; duas aplicações isolam suas composições.
3. Cada capacidade oferece somente seus métodos; invariantes de versões/eventos/planos resistem a bypass pelo ORM; mutáveis preservam o CRUD e a atomicidade.
4. Metadados do domínio permanecem compatíveis com MySQL 8 e migrations atuais; consultas mantêm filtros, limites, ordenação, privacidade, disponibilidade e quantidade de SELECTs constante por lote.
5. Desempenho/dashboard/plano compartilham base/relógio/snapshot, incluindo rollback externo, atualização concorrente e falha sem resultado parcial.
6. Suítes completas de backend e frontend mantêm gates de 90% de linhas e 85% de branches, sem arquivo executável zerado. As 29 integrações originais e os vinte percursos Playwright aprovam com API/MySQL reais.
7. Diagrama renderiza; links e matriz correspondem aos símbolos finais; relatório distingue execução atual, evidência histórica e publicação externa pendente.

Testes de contrato e substituição em memória são unitários. Integrações continuam exclusivamente MySQL 8 real, com schemas descartáveis e opt-ins de processo, sem SQLite nem mocks de banco. Não gerar evidências com credenciais, `.env`, cookies ou sessão exportada. Não instalar ferramentas/dependências novas de produção para demonstrar DIP.

## Risks / Trade-offs

- Extração da base pode alterar mapeamento ou commit → manter uma cadeia abstrata, caracterizar CRUD, comparar metadados e testar flush/rollback MySQL antes de converter consumidores.
- Converter estáticos afeta testes e planos → inventariar todas as chamadas e migrar em conjunto pela composição, preservando contratos HTTP e contexto transacional externo.
- DTO/adaptador pode alterar representação de datas/campos → caracterizar payloads e manter exatamente os envelopes/valores anteriores; não adicionar conversão de timezone ou arredondamento.
- Injeção pode virar service locator dentro do negócio → acesso à composição restrito à factory/HTTP; construtores obrigatórios e teste estrutural focado nas nove classes.
- Introduzir contratos em excesso → escopo fechado de nove consultas e três adaptações de plano, com métodos definidos pelo consumidor; sem refatoração geral de autenticação/escritas.
- Estado local contém outra entrega não commitada → registrar baseline por diff/arquivos no preflight do apply e preservar integralmente, sem reset, stash ou commit automático.
- MySQL/browser indisponível → registrar limitação e não marcar regressão como aprovada nem trocar por mocks.

## Migration Plan

1. Após revisão/autorização de apply, caracterizar o estado local, capturar a lista de mudanças preexistentes e executar a regressão focada.
2. Extrair bases de persistência e migrar snapshots/planos, verificando metadados, CRUD e proteções reais.
3. Introduzir contratos e composição e converter as consultas por domínio com seus testes; adaptar consumo por dashboard/plano.
4. Atualizar ADR, diagrama e documentação; executar testes completos, gates, E2E e verificação da change.
5. Registrar sync de specs como não aplicável por `skip_specs: true` e arquivar somente com tarefas concluídas e sem achados críticos.

Implantação não exige migration, backfill nem ação no banco operacional. A reversão é dos arquivos desta refatoração, preservando o trabalho anterior. Commit/push, conferência remota e envio do link do checkpoint são etapas separadas; não executá-las sem autorização. A entrega técnica não será chamada de entrega acadêmica enviada enquanto essas etapas externas estiverem pendentes.
