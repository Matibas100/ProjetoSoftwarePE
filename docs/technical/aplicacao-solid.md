# Aplicação de SOLID

O recorte e suas limitações estão no
[ADR-008](adr/ADR-008-contratos-e-capacidades-de-persistencia.md).
Refatoração interna não acrescenta funcionalidades às vinte já entregues.

## LSP e ISP: capacidades de persistência

`ModeloBase` oferece `salvar`, `listar_todos` e `buscar_por_id`;
`ModeloAtualizavel` acrescenta `atualizar`; `CrudMixin` acrescenta `deletar`.
São bases abstratas em uma cadeia única até `db.Model`. O import anterior de
`CrudMixin` permanece válido. Models convencionais preservam seu contrato.

As cinco versões/eventos de Questões e Simulados herdam de `ModeloBase`:
não anunciam operações incompatíveis com a imutabilidade. O guard ORM também
impede atribuição direta seguida de salvar/flush ou exclusão por sessão.
Isso evita apresentar um snapshot como substituto de uma entidade com CRUD
completo. `salvar` só persiste estado válido segundo os invariantes da Model.

`PlanoEstudo` e `PlanoEstudoItem` herdam de `ModeloAtualizavel`: só permitem
desativação do plano atual e conclusão do item nos campos/transições já
autorizados. Gerações e snapshots permanecem imutáveis, sem `deletar`.
Os testes de [plano](../../backend/tests/test_planos_integration.py) verificam
geração, recálculo, replay, snapshot, concorrência e falhas compostas.

Evidências: [capacidades](../../backend/tests/unit/test_persistencia_capacidades.py),
[CRUD convencional](../../backend/tests/unit/test_models_repository_controllers.py),
`test_snapshot_e_evento_append_only_inclusive_flush_orm` em
[Questões](../../backend/tests/test_questoes_versionadas_integration.py) e
`test_snapshots_e_eventos_sem_mutacoes_ou_exclusao` em
[Simulados](../../backend/tests/test_simulados_integration.py). As integrações
comprovam recusa e rollback com conteúdo/eventos preservados no MySQL real.


## Contratos de consulta

Os [contratos](../../backend/app/contracts/) usam Protocol e TypedDict, sem Flask,
SQLAlchemy, Models ou Repositories. Registros possuem campos nomeados; o adaptador
representa entidades. Services validam filtros, decidem elegibilidade e montam envelopes.

| Contrato | Assinatura e dados |
| --- | --- |
| ConsultaMateriasAdmin | listar(filtros,pagina,limite) → Matéria/Área/contagens + total |
| ConsultaAssuntosAdmin | listar(filtros,pagina,limite) → Assunto/Matéria/Área/contagem + total |
| ConsultaQuestoesPorAssunto | buscar_por_assunto(id) → conteúdo administrativo legado ordenado |
| ConsultaQuestoesElegiveis | listar(filtros,pagina,limite) → QuestaoSegura + total, sem gabarito/explicação |
| ConsultaElegibilidadeVersoes | executar(ids) → mapa de QuestaoSegura por versão elegível |
| ConsultaCatalogoSimulados | listar(pagina,limite), composicoes(ids), andamentos(usuario,ids) → catálogo e IDs em lote |
| ConsultaHistoricoSimulados | listar(usuario,pagina,limite) → título e resultado persistido + total |
| ConsultaMetricasDesempenho | agregar(contexto,usuario,inicio,fim) → contagens e grupos históricos |
| ConsultaAtividadesAluno | atividades(contexto,usuario,inicio,fim) → últimas atividades |
| ConsultaContagensAdmin | administrativo(contexto) → contagens globais |
| DiagnosticoAluno | executar(usuario,filtros=None,contexto=None,instante=None) → diagnóstico público |
| EscoposLeitura | usar(contexto=None,instante=None) → context manager com instante, sem SQL |

ContextoConsulta só expõe instante. Infraestrutura valida e reutiliza o contexto externo
sem encerrá-lo. A existência de Assunto usará Callable[[int], bool], ligada ao Active Record.
Não existe Repository CRUD genérico.

## Composição

A [factory](../../backend/app/__init__.py) registra uma composição própria em
app.extensions['servicos']. O [acessor HTTP](../../backend/app/http_composition.py) fica
nos Controllers. As ligações são acrescentadas por domínio convertido.
[Testes](../../backend/tests/unit/test_composition.py) verificam duas aplicações isoladas,
inicialização sem conexão e independência dos contratos.


## DIP e OCP: catálogo

ListarMateriasAdminService recebe ConsultaMateriasAdmin; ListarAssuntosAdminService
recebe ConsultaAssuntosAdmin. Nenhum escolhe implementação. ConsultaMateriasMySQL e
ConsultaAssuntosMySQL delegam consultas especializadas e representam os registros,
sem duplicar CRUD. Services continuam validando filtros e montando paginação.

Em [test_substituicao_catalogo.py](../../backend/tests/unit/test_substituicao_catalogo.py),
CatalogoEmLista e CatalogoIndexado produzem os mesmos resultados ao combinar filtros,
paginar e consultar resultado vazio. O mesmo código dos Services funciona com ambos.
Outro teste troca somente a ligação da aplicação e consulta o Controller sem MySQL;
a segunda aplicação mantém seu colaborador. A integração de catálogo valida a semântica
com os adaptadores MySQL, inclusive contagens, datas/nulos e autorização 401/403.


## ISP: conteúdo seguro de Questões

ConsultaQuestoesElegiveis só oferece listar e devolve QuestaoSegura, sem gabarito/explicação.
ListarQuestoesAlunoService não recebe capacidade de publicar ou editar. A transformação
conteudo() ocorre no adaptador MySQL, mantendo SELECTs constantes. O teste unitário
[test_consultas_compostas.py](../../backend/tests/unit/test_consultas_compostas.py) verifica
filtros/envelope e colaboração; Práticas/Questões versionadas verificam elegibilidade,
retirada, superação e privacidade com MySQL. Busca por Assunto recebe apenas consulta
administrativa e Callable de existência, sem interface genérica de CRUD.


## SRP: diagnóstico e infraestrutura

ConsultarDesempenhoService valida a identidade, período UTC, fórmula ponderada e amostra.
ConsultaMetricasMySQL representa contagens e delega agregações ao DesempenhoRepository,
que reúne projeções históricas. Mudar SQL altera o Repository/adaptador; mudar a regra de
amostra altera o caso de uso; mudar HTTP altera o Controller. O teste de métricas
intercambiáveis usa fatos ou contagens pré-calculadas para obter o mesmo diagnóstico.
Não basta separar pastas: o Service executa os colaboradores recebidos e não escolhe MySQL.

## Desempenho, dashboards e plano

ConsultarDesempenhoService satisfaz DiagnosticoAluno. A composição fornece a mesma
instância ao dashboard do Aluno e ao SelecionarPlanoService. EscoposLeituraMySQL delega
ContextoLeitura.usar; só a infraestrutura conhece a conexão/SQL. Dashboard abre um escopo
e compartilha contexto/instante com diagnóstico e atividades. Contagens administrativas
não recebem identidade de Aluno. Falha propaga sem payload parcial.

SelecionarPlanoService recebe diagnóstico; GerarPlanoService e RecalcularPlanoService
recebem o mesmo seletor; gerar recebe-o explicitamente. As outras dependências de escrita,
locks e TransactionManager continuam concretas no recorte existente. O plano fornece seu
contexto transacional autorizado, sem commit/rollback/fechamento pelo diagnóstico.
A seleção continua comparando frações exatas, com histórico e replay preservados.

Evidências: [consultas compostas](../../backend/tests/unit/test_consultas_compostas.py),
[composição e análise estrutural](../../backend/tests/unit/test_composition.py),
[desempenho MySQL](../../backend/tests/test_desempenho_integration.py) e
[plano MySQL](../../backend/tests/test_planos_integration.py). Cobrem troca de métricas,
contexto opaco, fórmula 1/3 = 33,33%, relógio compartilhado, falha completa, snapshot e
concorrência real. Simulados têm testes de disponibilidade por lote, histórico próprio,
resultado persistido, retirada posterior e SELECTs constantes.

## Limites

O recorte tem nove consultas, não todos os Services. Escritas, autenticação, detalhes e
correção de tentativas preservam suas dependências anteriores. Não se introduziu interface
por getter, Repository CRUD genérico, framework de DI, nova funcionalidade ou nova tabela.
As bases representam capacidades e não tornam qualquer mutação válida: invariantes e
fronteiras transacionais continuam obrigatórios. SOLID aqui é evidência localizada,
não uma declaração de desacoplamento completo do backend.
