# Matriz de cobertura CRUD

Inspeção estrutural em **07/11/2026** do sistema implementado. Complementa a
[modelagem atual](modelagem-de-dominio.md), o [diagrama](diagrama-de-classes.md)
e a [matriz das vinte funcionalidades](entrega-academica.md). Não certifica CRUD
integral de todas as Models nem dispensa acadêmica das restrições.

As listagens administrativas de Matéria, Assunto e Questão, o diagnóstico e os
dashboards usam as sete procedures e quatro views descritas em
[consultas acadêmicas MySQL](consultas-academicas-mysql.md). A alteração é de
leitura especializada: preserva as capacidades CRUD, Models e lacunas desta
matriz. A migration 013 acrescenta quinze procedures de seletores, impactos,
locks, versões e elegibilidade editorial, preservando as operações públicas.
A migration 014 acrescenta dezesseis procedures de Práticas/Simulados para
propriedade/replay, composição, andamento, respostas, páginas e fatos. Os métodos
que alimentam mutações conservam entidades gerenciadas; páginas usam registros
de apresentação. O [mapeamento SQL](consultas-academicas-mysql.md#práticas-e-simulados--migration-014)
liga os dezesseis métodos às cadeias de Práticas, composição e execução abaixo.
A migration 015 acrescenta seis interfaces de Plano: atual/replay/itens próprios,
pares elegíveis no proprietário Conteúdo e eliminação participante na negativa.
O [mapeamento de Plano](consultas-academicas-mysql.md#plano-de-estudos--migration-015)
detalha as cadeias existentes. Contas permanece na etapa 016; não há nova funcionalidade CRUD.

## Como ler as evidências

O inventário único abaixo contém **21 Models**, divididas em seis recursos
centrais para análise e outras quinze Models. Essa seleção é editorial e não
define quais entidades o professor aceitará como principais.

As três colunas de evidência são independentes: método na Model, operação
exposta por API/caso de uso e ação disponível na interface. Métodos herdados,
CLI, arquivamento e recálculo não preenchem operações públicas ausentes.

As [bases canônicas](../../backend/app/core/persistencia.py) têm estas capacidades:

| Sigla | Base direta | Métodos disponíveis |
| --- | --- | --- |
| C | `CrudMixin` (13 Models) | `salvar`, `listar_todos`, `buscar_por_id`, `atualizar`, `deletar`. |
| U | `ModeloAtualizavel` (2 Models) | Os anteriores, exceto `deletar`. |
| B | `ModeloBase` (6 Models) | `salvar`, `listar_todos`, `buscar_por_id`; sem `atualizar`/`deletar`. |

`salvar` respeita invariantes; `atualizar` só aceita `campos_atualizaveis`.
Guards ORM/FKs continuam aplicáveis. Base C não significa permissão para alterar
qualquer campo ou excluir dados históricos. Algumas Models não declaram
`campos_atualizaveis`: seus fluxos atribuem atributos e usam `salvar`, sem contrato
de atualização genérica. As rotas abreviam parâmetros como
`<id>`; os Blueprints usam os nomes/conversores reais, por exemplo
`<int:materia_id>`. Todos os caminhos HTTP incluem `/api`.

## Inventário: seis recursos centrais

| Model / fonte canônica | Persistência | API / caso de uso | Interface | Restrição ou lacuna |
| --- | --- | --- | --- | --- |
| [Materia](../../backend/app/modules/conteudo/models/materia.py) | C; nome, descrição, área e status atualizáveis. | Criar, listar, consultar por ID, editar, DELETE condicionado; lista administrativa/status/impacto. [Cadeia M](#materia). | `/index.html` e `/admin/materias.html`: cadastro, listagem, edição e exclusão confirmada; Editar administrativo consulta detalhe atual. | GET individual exclusivo de Administrador, incluindo inativos/arquivados. Vínculos bloqueiam DELETE (409); status/arquivamento são operações distintas. |
| [Assunto](../../backend/app/modules/conteudo/models/assunto.py) | C; nome/normalização, descrição, Matéria e status atualizáveis. | Criar, listar, consultar por ID, editar, DELETE condicionado; transferência/status/impacto. [Cadeia A](#assunto). | `/index.html` e `/admin/assuntos.html`: quatro operações e transferência administrativa; Editar consulta detalhe e vínculo atuais. | GET individual exclusivo de Administrador, incluindo inativos/arquivados; prévia de impacto continua distinta. Questões/histórico impedem DELETE. |
| [Usuario](../../backend/app/modules/contas/models/usuario.py) | C; nome, e-mail, ativo e hash atualizáveis conforme caso de uso. | Cadastro público/CLI preservados; `UsuarioController` → sete Services administrativos para criar/listar/detalhar/editar/desativar/reativar/excluir Alunos. [Cadeia U](#contas). | `/admin/usuarios.html` e `/admin/usuario.html`: CRUD administrativo de Aluno e status confirmado. | Perfil imutável; Administrador não é alvo. DELETE só sem vínculos; sessão mesmo revogada, aceite, autoria e histórico impedem exclusão. Desativação é ação distinta. |
| [Questao](../../backend/app/modules/conteudo/models/questao.py) | C; conteúdo/classificação atualizáveis conforme caso de uso. | Criar rascunho, listar/detalhar/buscar, editar, publicar e arquivar. [Cadeia Q](#questoes). | `/index.html`, `/admin/questoes.html` e `/admin/questao.html`: busca/cadastro e gestão editorial. | Arquivar é POST, sem DELETE físico exposto. Publicação preserva snapshot e eventos. |
| [Simulado](../../backend/app/modules/simulados/models/simulado.py) | C; sem `campos_atualizaveis` declarado; Services alteram atributos e salvam sob regras. | Compor, listar/detalhar, editar rascunho, publicar e arquivar. [Cadeia S](#simulados). | `/admin/simulados.html` e `/admin/simulado.html`: composição e ciclo editorial. | Sem DELETE físico exposto; versão e tentativas sobrevivem ao arquivamento. |
| [PlanoEstudo](../../backend/app/modules/plano_estudos/models/plano_estudo.py) | U; somente `atual` atualizável, com guard de geração histórica. | Gerar, consultar próprio e recalcular; negativa elimina derivados próprios. [Cadeia P](#plano). | `/aluno/plano.html` e `/aluno/privacidade.html`: geração/consulta/recálculo e decisão de consentimento. | Recálculo cria geração, não PUT genérico. Não há DELETE manual de plano; eliminação é efeito especializado da privacidade. |

## Inventário: outras quinze Models

As referências às cadeias identificam o Controller/Service responsável pelo
recurso pai. Itens, fatos e infraestrutura não ganham Controllers fictícios.

| Model / fonte canônica | Persistência | API / caso de uso responsável | Interface | Limite |
| --- | --- | --- | --- | --- |
| [AreaEnem](../../backend/app/modules/conteudo/models/area_enem.py) | C; campos atualizáveis vazios. | `GET /api/areas-enem`, `AreaEnemController` → `ListarAreasEnemService`. [Catálogo](#catalogo-auxiliar). | Seletores de área nas telas administrativas. | Referência fixa; sem criação/edição/DELETE públicos. |
| [AssuntoTransferencia](../../backend/app/modules/conteudo/models/assunto_transferencia.py) | C; campos atualizáveis vazios. | Criada por `AssuntoController.transferir` → `TransferirAssuntoService`; origem/destino e contagem histórica. [A](#assunto). | Transferir em `/admin/assuntos.html`; impacto informa vínculos. | Sem CRUD isolado nem tela de edição do histórico. |
| [QuestaoVersao](../../backend/app/modules/conteudo/models/questao_versao.py) | B; guards impedem alteração/exclusão. | `QuestaoController.publicar` → `PublicarQuestaoService`; leitura histórica/elegível pelos consumidores. [Q](#questoes). | Publicação no editor; conteúdo usado em práticas/Simulados e correções. | Snapshot imutável, sem CRUD genérico. |
| [QuestaoEvento](../../backend/app/modules/conteudo/models/questao_evento.py) | B; guards impedem alteração/exclusão. | `CriarQuestaoService`, `EditarQuestaoService`, `PublicarQuestaoService`, `ArquivarQuestaoService`, via `QuestaoController`. [Q](#questoes). | Criado pelas ações editoriais; sem tela CRUD de eventos. | Fatos preservados, sem atualizar/DELETE. |
| [Sessao](../../backend/app/modules/contas/models/sessao.py) | C; acesso, reautenticação e revogação atualizáveis. | `AutenticacaoController` → `PrepararCsrfService`/`CriarSessaoService`, `ConsultarSessaoService`, `LoginService`, `LogoutService`, `ReautenticarService`; limpeza interna/CLI. [U](#contas). | Login, logout e confirmação de reautenticação; identidade da própria sessão. | Consulta de sessão não é listagem administrativa de sessões ou Usuários; revogar não é DELETE público. |
| [AuthLimite](../../backend/app/modules/contas/models/auth_limite.py) | C; falhas/janela/bloqueio atualizáveis. | `AutenticacaoController.login/reautenticar` → `ValidarSenhaService` e `AutenticacaoRepository`; limpeza por `LimparAutenticacaoService`. [U](#contas). | Mensagens de autenticação; sem gestão do contador. | Infraestrutura por hash, sem FK de Usuário nem CRUD HTTP próprio. |
| [RegistroPrivacidade](../../backend/app/modules/contas/models/registro_privacidade.py) | B; guards impedem alteração/exclusão. | Cadastro e decisões de uso/plano; consulta própria por `PrivacidadeController`/Services. [Privacidade](#privacidade). | Aceite em `/cadastro`; evidências/escolhas em `/aluno/privacidade.html`. | Append-only, sem atualizar/DELETE; negativa do plano preserva evidências. |
| [PraticaTentativa](../../backend/app/modules/praticas/models/pratica_tentativa.py) | C; sem `campos_atualizaveis` declarado; responder atribui/salva sob regra. | `PraticaController` → iniciar, consultar/listar e responder. [Práticas](#praticas). | `/aluno/questoes.html`, `/aluno/questao.html`, `/aluno/historico.html`. | Resposta definitiva com replay da mesma alternativa; sem edição arbitrária ou DELETE público. |
| [SimuladoRascunhoItem](../../backend/app/modules/simulados/models/simulado.py) | C; sem `campos_atualizaveis` declarado. | `SimuladoController.criar/editar` → `CriarSimuladoService`/`EditarSimuladoService`; substitui itens ao editar composição. [S](#simulados). | Adicionar, ordenar e remover na composição do rascunho. | Sem recurso HTTP independente; remoção interna de item não é DELETE de Simulado. |
| [SimuladoVersao](../../backend/app/modules/simulados/models/simulado.py) | B; guards impedem alteração/exclusão. | `SimuladoController.publicar` → `PublicarSimuladoService`; detalhe/catálogo/execução leem versão. [S](#simulados). | Publicação e execução do Simulado. | Snapshot imutável, sem CRUD próprio. |
| [SimuladoVersaoItem](../../backend/app/modules/simulados/models/simulado.py) | B; guards impedem alteração/exclusão. | `PublicarSimuladoService` cria; Services de consulta, início e correção usam composição fixa. [S](#simulados). | Questões ordenadas na execução/correção. | Não reordena/altera versão publicada; sem CRUD próprio. |
| [SimuladoEvento](../../backend/app/modules/simulados/models/simulado.py) | B; guards impedem alteração/exclusão. | `SimuladoController` → Services de criar/editar/publicar/arquivar. [S](#simulados). | Registrado pelas ações editoriais; sem tela CRUD de eventos. | Fatos preservados, sem atualizar/DELETE. |
| [SimuladoTentativa](../../backend/app/modules/simulados/models/simulado.py) | C; sem `campos_atualizaveis` declarado; fluxo atribui/salva. | `SimuladoController` → iniciar/retomar, histórico, detalhe/resultado/correção e finalizar. [Execução S](#execucao-de-simulados). | `/aluno/simulados.html` (catálogo/histórico) e `/aluno/simulado.html` (execução/resultado). | Finalização consolida resultado; sem DELETE público ou reescrita de concluída. |
| [SimuladoResposta](../../backend/app/modules/simulados/models/simulado.py) | C; sem `campos_atualizaveis` declarado; fluxo atribui/salva. | `IniciarSimuladoService` cria por item; `ResponderSimuladoService` grava/limpa; `FinalizarSimuladoService` corrige. [Execução S](#execucao-de-simulados). | Selecionar/limpar alternativa durante tentativa; consultar correção após finalizar. | PUT especializado durante tentativa; sem CRUD genérico/DELETE de respostas. |
| [PlanoEstudoItem](../../backend/app/modules/plano_estudos/models/plano_estudo.py) | U; `estado`/`concluido_em` atualizáveis sob guards. | Geração/recálculo cria; `PlanoEstudoController.concluir` → `ConcluirPlanoItemService`; negativa elimina com plano. [P](#plano). | Consultar/concluir manualmente em `/aluno/plano.html`. | Sem edição livre de snapshot, desfazer conclusão ou DELETE manual; exceção de privacidade especializada. |

## Rotas, camadas e ações verificáveis

As telas apontam para os arquivos HTML e seus scripts. A inspeção confirma a
existência do percurso no código, sem declarar nova execução de navegador.
Leituras/escritas usam as permissões atuais de Aluno/Administrador; expor método
na Model não concede acesso HTTP.

<a id="materia"></a>

### Matéria

[Blueprint Conteúdo](../../backend/app/modules/conteudo/routes.py) →
[MateriaController](../../backend/app/modules/conteudo/controllers/materia_controller.py):

- `POST /api/materias` → [CriarMateriaService](../../backend/app/modules/conteudo/services/criar_materia_service.py).
- `GET /api/materias` → [ListarMateriasService](../../backend/app/modules/conteudo/services/listar_materias_service.py).
- `GET /api/materias/<id>` → `MateriaController.buscar_por_id` → [BuscarMateriaPorIdService](../../backend/app/modules/conteudo/services/buscar_materia_por_id_service.py) → `Materia.buscar_por_id`/`to_dict` → MySQL. Editar administrativo usa o detalhe antes de preencher, sem escrita automática.
- `PUT /api/materias/<id>` → [AtualizarMateriaService](../../backend/app/modules/conteudo/services/atualizar_materia_service.py).
- `DELETE /api/materias/<id>` → [DeletarMateriaService](../../backend/app/modules/conteudo/services/deletar_materia_service.py).
- `GET /api/admin/materias` → `ListarMateriasAdminService` em
  [listar_catalogo_admin_service.py](../../backend/app/modules/conteudo/services/listar_catalogo_admin_service.py).
- `GET /api/materias/<id>/impacto-exclusao` → `ImpactoMateriaService` em
  [impacto_catalogo_service.py](../../backend/app/modules/conteudo/services/impacto_catalogo_service.py).
- `POST /api/materias/<id>/{inativar,arquivar,reativar}` → `AlterarStatusMateriaService`
  em [alterar_status_catalogo_service.py](../../backend/app/modules/conteudo/services/alterar_status_catalogo_service.py).

CRUD simples permanece na Model; [CatalogoRepository](../../backend/app/modules/conteudo/repositories/catalogo_repository.py)
faz impacto/consultas/locks. DELETE verifica Assuntos e transferências; FKs
protegem vínculos restantes, com conflito 409. Interface:
[MVP](../../frontend/index.html)/[app.js](../../frontend/js/app.js) e
[Admin](../../frontend/admin/materias.html)/[admin-materias.js](../../frontend/js/admin-materias.js).

<a id="assunto"></a>

### Assunto

Mesmo [Blueprint](../../backend/app/modules/conteudo/routes.py) →
[AssuntoController](../../backend/app/modules/conteudo/controllers/assunto_controller.py):

- `POST/GET /api/assuntos` → [CriarAssuntoService](../../backend/app/modules/conteudo/services/criar_assunto_service.py)/[ListarAssuntosService](../../backend/app/modules/conteudo/services/listar_assuntos_service.py).
- `GET /api/assuntos/<id>` → `AssuntoController.buscar_por_id` → [BuscarAssuntoPorIdService](../../backend/app/modules/conteudo/services/buscar_assunto_por_id_service.py) → `Assunto.buscar_por_id`/`to_dict` → MySQL. Editar administrativo atualiza opções e origem com o vínculo do detalhe; Salvar comum usa PUT, sem transferência indevida.
- `PUT/DELETE /api/assuntos/<id>` → [AtualizarAssuntoService](../../backend/app/modules/conteudo/services/atualizar_assunto_service.py)/[DeletarAssuntoService](../../backend/app/modules/conteudo/services/deletar_assunto_service.py).
- `GET /api/admin/assuntos` → `ListarAssuntosAdminService` em
  [listar_catalogo_admin_service.py](../../backend/app/modules/conteudo/services/listar_catalogo_admin_service.py).
- `GET /api/assuntos/<id>/impacto-exclusao` → `ImpactoAssuntoService` em
  [impacto_catalogo_service.py](../../backend/app/modules/conteudo/services/impacto_catalogo_service.py).
- `GET /api/assuntos/<id>/impacto-transferencia` e `POST /api/assuntos/<id>/transferir`
  → [TransferirAssuntoService](../../backend/app/modules/conteudo/services/transferir_assunto_service.py).
- `POST /api/assuntos/<id>/{inativar,arquivar,reativar}` → `AlterarStatusAssuntoService`
  em [alterar_status_catalogo_service.py](../../backend/app/modules/conteudo/services/alterar_status_catalogo_service.py).

A Model faz CRUD simples; [CatalogoRepository](../../backend/app/modules/conteudo/repositories/catalogo_repository.py)
confere unicidade, impacto e locks. DELETE verifica Questões/transferências;
referências históricas adicionais seguem protegidas por FK e conflito 409.
[MVP](../../frontend/index.html)/[assuntos.js](../../frontend/js/assuntos.js) e
[Admin](../../frontend/admin/assuntos.html)/[admin-assuntos.js](../../frontend/js/admin-assuntos.js)
implementam as ações, incluindo transferência auditada na Administração.

<a id="catalogo-auxiliar"></a>

### Catálogo auxiliar

`GET /api/areas-enem` no [Blueprint Conteúdo](../../backend/app/modules/conteudo/routes.py)
→ [AreaEnemController](../../backend/app/modules/conteudo/controllers/area_enem_controller.py)
→ [ListarAreasEnemService](../../backend/app/modules/conteudo/services/listar_areas_enem_service.py)
→ Model → CatalogoRepository → `sp_areas_enem_ordenadas`. Seletores administrativos consomem a lista fixa. Transferências são
criadas pelo fluxo de Assunto acima, sem CRUD de histórico independente.

<a id="contas"></a>

### Contas, sessões e limites

[Blueprint Contas](../../backend/app/modules/contas/routes.py) →
[AutenticacaoController](../../backend/app/modules/contas/controllers/autenticacao_controller.py)
→ classes de [autenticacao_service.py](../../backend/app/modules/contas/services/autenticacao_service.py):
`POST /api/auth/cadastro` (`CadastrarAlunoService`), `POST /api/auth/login`
(`LoginService`), `GET /api/auth/sessao` (`ConsultarSessaoService`),
`GET /api/auth/csrf` (`PrepararCsrfService`), `POST /api/auth/logout`
(`LogoutService`) e `POST /api/auth/reautenticar` (`ReautenticarService`).
`CriarSessaoService` e `ValidarSenhaService` apoiam os fluxos;
[AutenticacaoRepository](../../backend/app/modules/contas/repositories/autenticacao_repository.py)
faz consultas, locks, revogação, limitação e limpeza. `CriarUsuarioService` e
`LimparAutenticacaoService` também são usados pela [CLI](../../backend/app/modules/contas/auth_cli.py).

O acesso especializado usa as oito routines de autenticação da 016,
incluindo `Usuario.buscar_por_email` → Repository → `sp_usuario_por_email`.
Sessão completa usa `sp_consultar_sessao` com LEFT JOIN gerenciado; renovação,
revogações, upsert bloqueante do limite e limpeza participam da transação externa.
Senha/política temporal/limitação ficam nos Services; CRUD individual permanece
nas Models. [Contratos e consumidores](consultas-academicas-mysql.md#contas-e-privacidade--migration-016).

[Cadastro](../../frontend/cadastro.html), [login](../../frontend/login.html),
[auth-page.js](../../frontend/js/auth-page.js) e
[auth-session.js](../../frontend/js/auth-session.js) cobrem autenticação.
O [menu](../../frontend/js/navigation.js) habilita Usuários para Administradores.
`UsuarioController` chama `CriarAlunoAdminService`, `ListarAlunosAdminService`,
`BuscarAlunoAdminService`, `AtualizarAlunoAdminService`, `DesativarAlunoService`,
`ReativarAlunoService` e `ExcluirAlunoAdminService`. CRUD usa a Model;
listagem/lock usam `UsuarioRepository` e as duas routines da 017. Revogação
reutiliza a 016, na mesma transação. [Contratos e limites](gestao-administrativa-alunos.md).

<a id="questoes"></a>

### Questões, versões e eventos

[Blueprint Conteúdo](../../backend/app/modules/conteudo/routes.py) →
[QuestaoController](../../backend/app/modules/conteudo/controllers/questao_controller.py)
→ [CriarQuestaoService](../../backend/app/modules/conteudo/services/criar_questao_service.py)
(`POST /api/questoes`),
[BuscarQuestoesPorAssuntoService](../../backend/app/modules/conteudo/services/buscar_questoes_por_assunto_service.py)
(`GET /api/questoes/por-assunto`) e classes de
[gestao_questao_service.py](../../backend/app/modules/conteudo/services/gestao_questao_service.py):
`ListarQuestoesAdminService` (`GET /api/admin/questoes`), `ConsultarQuestaoService`
(`GET /api/questoes/<id>`), `EditarQuestaoService` (`PUT` no mesmo caminho),
`PublicarQuestaoService` e `ArquivarQuestaoService`
(`POST /api/questoes/<id>/publicar` e `/arquivar`).

[QuestaoRepository](../../backend/app/modules/conteudo/repositories/questao_repository.py)
encapsula consultas/locks e o `CALL sp_questoes_por_assunto`; versões históricas
e elegíveis são fornecidas pelas APIs/contratos do módulo, sem cruzar ORM privado.
[MVP](../../frontend/index.html)/[questoes.js](../../frontend/js/questoes.js) e
[listagem](../../frontend/admin/questoes.html)/[editor](../../frontend/admin/questao.html)
com [admin-questoes.js](../../frontend/js/admin-questoes.js) executam busca e ciclo
editorial. Arquivar preserva snapshots/eventos e tentativas; não há rota DELETE.

<a id="praticas"></a>

### Práticas

[Blueprint Práticas](../../backend/app/modules/praticas/routes.py) →
[PraticaController](../../backend/app/modules/praticas/controllers/pratica_controller.py)
→ [ListarQuestoesAlunoService](../../backend/app/modules/praticas/services/listar_questoes_aluno_service.py)
(`GET /api/aluno/questoes`), [IniciarPraticaService](../../backend/app/modules/praticas/services/iniciar_pratica_service.py)
(`POST /api/aluno/praticas`), [ListarPraticasService](../../backend/app/modules/praticas/services/listar_praticas_service.py)
(`GET /api/aluno/praticas`), [ConsultarPraticaService](../../backend/app/modules/praticas/services/consultar_pratica_service.py)
(`GET /api/aluno/praticas/<id>`) e [ResponderPraticaService](../../backend/app/modules/praticas/services/responder_pratica_service.py)
(`POST /api/aluno/praticas/<id>/resposta`).
[PraticaRepository](../../backend/app/modules/praticas/repositories/pratica_repository.py)
consulta/bloqueia tentativas próprias; a fronteira de Conteúdo fornece versões.

[Questões](../../frontend/aluno/questoes.html), [tentativa](../../frontend/aluno/questao.html)
e [histórico de práticas](../../frontend/aluno/historico.html), com
[aluno-praticas.js](../../frontend/js/aluno-praticas.js), oferecem estudo/correção.
Uma resposta concluída não admite alternativa diferente; não existe DELETE público.

<a id="simulados"></a>

### Simulados: composição editorial

[Blueprint Simulados](../../backend/app/modules/simulados/routes.py) →
[SimuladoController](../../backend/app/modules/simulados/controllers/simulado_controller.py)
→ classes de [gestao_simulado_service.py](../../backend/app/modules/simulados/services/gestao_simulado_service.py):
`ListarSimuladosAdminService`/`CriarSimuladoService` (`GET/POST /api/admin/simulados`),
`ConsultarSimuladoAdminService`/`EditarSimuladoService`
(`GET/PUT /api/admin/simulados/<id>`), `PublicarSimuladoService`/`ArquivarSimuladoService`
(`POST /api/admin/simulados/<id>/publicar` e `/arquivar`).
[SimuladoRepository](../../backend/app/modules/simulados/repositories/simulado_repository.py)
consulta/bloqueia agregado e itens; a fronteira de Conteúdo valida versões.

[Lista](../../frontend/admin/simulados.html), [editor](../../frontend/admin/simulado.html)
e [admin-simulados.js](../../frontend/js/admin-simulados.js) permitem compor/editar
rascunho, publicar e arquivar. Editar substitui itens de rascunho; publicar cria
versão/itens imutáveis e evento. Arquivar mantém histórico, sem DELETE público.

<a id="execucao-de-simulados"></a>

### Execução de Simulados

Mesmo Blueprint/Controller → [ListarSimuladosAlunoService](../../backend/app/modules/simulados/services/listar_simulados_aluno_service.py)
(`GET /api/aluno/simulados`), [IniciarSimuladoService](../../backend/app/modules/simulados/services/iniciar_simulado_service.py)
(`POST /api/aluno/tentativas-simulado`), [ListarHistoricoSimuladosService](../../backend/app/modules/simulados/services/listar_historico_simulados_service.py)
(`GET /api/aluno/tentativas-simulado`), [ConsultarTentativaSimuladoService](../../backend/app/modules/simulados/services/consultar_simulado_service.py)
(`GET /api/aluno/tentativas-simulado/<id>`, também `/resultado` e `/correcao`),
[ResponderSimuladoService](../../backend/app/modules/simulados/services/responder_simulado_service.py)
(`PUT /api/aluno/tentativas-simulado/<id>/respostas/<item_id>`) e
[FinalizarSimuladoService](../../backend/app/modules/simulados/services/finalizar_simulado_service.py)
(`POST /api/aluno/tentativas-simulado/<id>/finalizar`). Usam o Repository do módulo
para propriedade/locks/leituras e as Models para escritas do fluxo.

[Catálogo/histórico](../../frontend/aluno/simulados.html) e [execução](../../frontend/aluno/simulado.html), com
[aluno-simulados.js](../../frontend/js/aluno-simulados.js), permitem iniciar/retomar,
responder/limpar, finalizar e consultar resultado/correção. Não há DELETE público.

<a id="plano"></a>

### Plano e itens

[Blueprint Plano](../../backend/app/modules/plano_estudos/routes.py) →
[PlanoEstudoController](../../backend/app/modules/plano_estudos/controllers/plano_estudo_controller.py)
→ [ConsultarPlanoService](../../backend/app/modules/plano_estudos/services/consultar_plano_service.py)
(`GET /api/aluno/plano`), [GerarPlanoService](../../backend/app/modules/plano_estudos/services/gerar_plano_service.py)
(`POST /api/aluno/plano/gerar`), [RecalcularPlanoService](../../backend/app/modules/plano_estudos/services/recalcular_plano_service.py)
(`POST /api/aluno/plano/recalcular`) e [ConcluirPlanoItemService](../../backend/app/modules/plano_estudos/services/concluir_plano_item_service.py)
(`POST /api/aluno/plano/itens/<id>/concluir`).
[PlanoEstudoRepository](../../backend/app/modules/plano_estudos/repositories/plano_estudo_repository.py)
consulta/bloqueia gerações/itens próprios por `sp_plano_atual`, `sp_plano_por_chave`,
`sp_plano_itens` e `sp_plano_item_proprio`, com entidades gerenciadas.
Seleção usa o diagnóstico de Desempenho e a API pública de Conteúdo →
`QuestaoRepository.pares_elegiveis_plano` → `sp_pares_elegiveis_plano`.
[Tela](../../frontend/aluno/plano.html)/[aluno-plano.js](../../frontend/js/aluno-plano.js)
oferece gerar, consultar, recalcular com confirmação e concluir manualmente.

Recálculo conserva gerações durante uso autorizado. A eliminação após negativa
é especializada: [EliminarPlanosPropriosService](../../backend/app/modules/plano_estudos/services/eliminar_planos_proprios_service.py)
delega ao Repository, como participante injetado em Contas pela
[composição](../../backend/app/composition.py), sem commit próprio ou endpoint
de DELETE manual. Itens e gerações são eliminados em ordem compatível com RESTRICT,
na mesma transação da decisão, por `sp_eliminar_planos_proprios`, preservando
guards normais. A rotina devolve contagens internas; o Repository mantém o
contrato participante sem retorno público e expira somente derivados carregados afetados.

<a id="privacidade"></a>

### Privacidade e evidências

[Blueprint Contas](../../backend/app/modules/contas/routes.py) →
[PrivacidadeController](../../backend/app/modules/contas/controllers/privacidade_controller.py)
→ [ConsultarTermosService](../../backend/app/modules/contas/services/consultar_termos_service.py)
(`GET /api/termos`), [ConsultarPrivacidadeService](../../backend/app/modules/contas/services/consultar_privacidade_service.py)
(`GET /api/aluno/privacidade`), [AceitarTermosUsoService](../../backend/app/modules/contas/services/aceitar_termos_uso_service.py)
(`POST /api/aluno/privacidade/termos-uso`) e
[ConsentirPlanoService](../../backend/app/modules/contas/services/consentir_plano_service.py),
[RecusarConsentimentoPlanoService](../../backend/app/modules/contas/services/recusar_consentimento_plano_service.py),
[RevogarConsentimentoPlanoService](../../backend/app/modules/contas/services/revogar_consentimento_plano_service.py)
(`POST /api/aluno/privacidade/consentimento-plano/{aceitar,recusar,revogar}`).
[PrivacidadeRepository](../../backend/app/modules/contas/repositories/privacidade_repository.py)
consulta decisões/replays e coordena lock de Usuário; a eliminação pertence ao
participante de Plano. A [tela](../../frontend/aluno/privacidade.html) e
[aluno-privacidade.js](../../frontend/js/aluno-privacidade.js) exibem decisões e
confirmações; cadastro grava o aceite de uso junto à conta.

Lock exato, últimas decisões e replay usam `sp_bloquear_identidade_privacidade`,
`sp_ultimas_decisoes_privacidade` e `sp_decisao_privacidade_por_chave` (016).
Últimas decisões capturam uso e depois plano sob lock e retornam um conjunto
de entidades gerenciadas; as evidências continuam append-only, gravadas na Model.

Recusa/revogação elimina somente planos/itens/conclusões próprios; mantém
respostas, Simulados, diagnóstico, outra conta e evidências. Nova autorização
inicia novo histórico de plano. Ver [ADRs 009](adr/ADR-009-consentimento-e-eliminacao-do-plano.md)
e [010](adr/ADR-010-organizacao-modular-do-backend.md).

## Pendências, limites e continuidade

A [auditoria dos seis módulos](consultas-academicas-mysql.md#auditoria-dos-seis-módulos)
confrontou os executores com os inventários 011–016 e a procedure legada.
Filtros/JOINs/ordenações/operações especializadas executados em produção usam
as routines proprietárias. Cinco projeções ORM permanecem como construção
compatível, com execução somente na regressão de equivalência de desempenho;
produção consome as views/procedures. CRUD básico permanece nas Models.
Essa cobertura técnica não resolve F01/F02/E01–E03 nem certifica aceite acadêmico.

| ID | Evidência e situação nesta entrega | Continuidade |
| --- | --- | --- |
| D01 | Formalização atual publicada na [modelagem](modelagem-de-dominio.md), no [diagrama](diagrama-de-classes.md) e nesta matriz; lacuna documental resolvida. Não há comprovação de modelagem anterior entregue. | Grupo decide e realiza envio/demonstração; aprovação acadêmica não é presumida. |
| F01 | Resolvida em 09/11/2026 somente para gestão administrativa de Alunos: CRUD condicionado, desativação/reativação e efeitos atômicos nas sessões. | [Validação](../../openspec/changes/archive/2026-11-09-gerenciar-contas-de-alunos/validacao.md): MySQL e Chromium reais. Não abrange Administradores, promoção de perfil, exclusão geral ou auditoria completa; E01–E03 permanecem independentes. |
| F02 | Resolvida em 09/11/2026: GET individual de Matéria/Assunto exclusivo de Administrador e consumido por Editar nas duas telas. Integração MySQL e Chromium com segunda aba comprovam os valores e o vínculo atuais. | Evidências e limites na [validação da busca por ID](../../openspec/changes/archive/2026-11-09-buscar-materias-assuntos-por-id/validacao.md). Não resolve F01/E01–E03 nem altera os vinte casos. |
| E01 | Arquivamento de Questão/Simulado usa POST e preserva histórico; não implementa DELETE físico. Evidência nas cadeias Q/S e [ADR-003](adr/ADR-003-politica-de-exclusao-catalogo.md). | Confirmar critério acadêmico do ciclo editorial; sem apagar versões/eventos ou prometer novo DELETE nesta change. |
| E02 | Quinze Models auxiliares representam itens, fatos, referência fixa, execução e infraestrutura; seus casos são coordenados pelos recursos responsáveis acima. | Apresentar classificação ao professor; justificativa técnica não significa dispensa acadêmica de CRUD. |
| E03 | Seis Models B não têm atualizar/deletar; duas U não têm deletar. Guardam fatos/snapshots/gerações conforme [ADR-008](adr/ADR-008-contratos-e-capacidades-de-persistencia.md) e ADRs 009/010. | Explicar capacidades e a exceção especializada do plano; não acrescentar métodos incompatíveis para aparentar CRUD integral. Aceitação acadêmica pendente. |

### Vínculo protegido de aceite e Usuário

O cadastro público grava a conta e seu aceite de uso na mesma transação.
`RegistroPrivacidade.usuario_id` usa `ON DELETE RESTRICT` e a evidência tem guard
contra exclusão. Sessões e fatos também podem referenciar a conta. Portanto,
uma futura gestão não pode prometer excluir qualquer conta pública apenas
quando estiver “sem práticas”: o próprio aceite já cria vínculo protegido.
Desativação, arquivamento e exclusão física são operações diferentes. Esta
documentação não define retenção nova, alteração de FK ou remoção de evidências;
essas decisões precisam de proposta própria.

## Alcance da validação

A [validação desta change](../../openspec/changes/archive/2026-11-07-formalizar-modelagem-e-cobertura-crud/validacao.md)
registra inspeção de mappers, métodos, FKs, rotas, camadas, telas e links, com
configuração sintética, `.env` desabilitado e conexão bloqueada. Isso confirma
estrutura/exposição; não comprova persistência por nova integração ou execução
E2E. Os [relatórios históricos](entrega-academica.md#evidências-e-reprodução)
continuam limitados às execuções/revisões neles registradas. As vinte
funcionalidades mantêm IDs; esta documentação não adiciona uma funcionalidade,
não implementa F01/F02 e não certifica cumprimento integral da exigência CRUD.

### Validação adicional — consulta por ID (09/11/2026)

O [relatório adicional](../../openspec/changes/archive/2026-11-09-buscar-materias-assuntos-por-id/validacao.md)
comprova F02 com GET/HEAD protegido, integração MySQL e edição administrativa
em Chromium. A segunda aba altera Matéria e transfere Assunto antes de Editar
na primeira; o formulário recebe o detalhe atual e salva somente após ação
explícita. O vínculo corrente também é preservado com Matéria inativa criada
depois da abertura da tela. Essa evidência acrescenta a prova ausente na inspeção
histórica acima, sem reescrevê-la. F01 e E01–E03 permanecem independentes.
