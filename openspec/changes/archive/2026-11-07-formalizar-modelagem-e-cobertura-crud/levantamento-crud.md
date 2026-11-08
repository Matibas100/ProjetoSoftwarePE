# Levantamento atual — domínio e CRUD

## Escopo e evidência

Levantamento de 07/11/2026, durante o planejamento desta change. O grupo informou não ter entregue modelagem de domínio anterior. A classificação abaixo organiza o sistema implementado e não representa escopo acadêmico anteriormente aprovado.

Fontes: `backend/app/modules/`, bases em `backend/app/core/persistencia.py`, Blueprints, Controllers/Services, HTML/JavaScript, `docs/technical/diagrama-de-classes.md`, matriz acadêmica e ADRs 003/008/009/010. Os métodos e o mapa de rotas foram inspecionados com factory/configuração sintética, `.env` desabilitado e conexão SQLAlchemy bloqueada; nenhum banco foi acessado. Isso confirma estrutura/exposição, não uma nova execução de todos os fluxos de navegador.

Há 21 Models concretas: 13 herdam CRUD completo de `CrudMixin`, duas usam `ModeloAtualizavel` e seis usam `ModeloBase`. Todas herdam indiretamente de `db.Model`. Métodos disponíveis não significam automaticamente rotas, permissão ou interface correspondente.

## Entidades principais propostas para organizar a análise

Esta seleção de seis entidades centrais é editorial e precisa ser confrontada com a expectativa do professor; não redefine o domínio nem exclui as outras quinze Models da documentação.

| Model | Criar | Ler | Atualizar | Excluir | Situação real de ponta a ponta |
| --- | --- | --- | --- | --- | --- |
| `Materia` | Cadastro administrativo | Listas simples/administrativas | Edição pela interface | DELETE condicionado à ausência de vínculos | Quatro operações convencionais presentes; não há GET individual dedicado em `/api/materias/<id>`. `buscar_por_id` existe na Model e é usado internamente. |
| `Assunto` | Cadastro administrativo | Listas/filtros administrativos | Edição e transferência controlada | DELETE condicionado à ausência de vínculos | Quatro operações convencionais presentes; não há GET individual dedicado em `/api/assuntos/<id>`. Não confundir prévia de impacto com consulta geral por ID. |
| `Usuario` | Cadastro público de Aluno; Administrador por CLI | Consulta da própria identidade na sessão | Sem gestão por interface/API | Sem exclusão de conta por interface/API | Cadastro/login não constituem gestão CRUD completa. `campos_atualizaveis` permite atualmente `ativo`/`senha_hash`, não edição genérica de nome/e-mail/perfil. |
| `Questao` | Rascunho administrativo | Listagem, detalhe e busca por Assunto | Edição controlada/publicação versionada | Arquivamento por POST; sem DELETE | Gestão editorial implementada, sem exclusão física exposta. Arquivar não equivale à operação DELETE exigida literalmente. |
| `Simulado` | Composição manual | Listagem e detalhe | Edição de rascunho/publicação | Arquivamento por POST; sem DELETE | Ciclo editorial implementado, sem CRUD irrestrito. Resultados e versões permanecem históricos. |
| `PlanoEstudo` | Geração por desempenho e consentimento | Consulta própria do plano atual | Recálculo cria geração; conclusão atua em item | Negativa confirmada elimina derivados próprios | Operações específicas, não CRUD administrativo manual; a eliminação é efeito da decisão de privacidade e não uma tela de DELETE de plano. |

### Rotas e telas dos seis recursos

Todos os caminhos de API abaixo incluem `/api`.

| Recurso | Principais rotas atuais | Interface |
| --- | --- | --- |
| Matéria | `POST/GET /api/materias`, `PUT/DELETE /api/materias/<id>`, `GET /api/admin/materias`; ciclo de status e impacto | `/index.html`, `/admin/materias.html` |
| Assunto | `POST/GET /api/assuntos`, `PUT/DELETE /api/assuntos/<id>`, `GET /api/admin/assuntos`; transferência, status e impacto | `/index.html`, `/admin/assuntos.html` |
| Usuário | `POST /api/auth/cadastro`, `POST /api/auth/login`, `GET /api/auth/sessao`; logout/reautenticação | `/cadastro`, `/login`; identidade nas páginas autenticadas. Gestão de Usuários está indisponível no menu. |
| Questão | `POST /api/questoes`, `GET /api/admin/questoes`, `GET/PUT /api/questoes/<id>`, `POST .../publicar`, `POST .../arquivar`, `GET /api/questoes/por-assunto` | `/index.html`, `/admin/questoes.html`, `/admin/questao.html` |
| Simulado | `POST/GET /api/admin/simulados`, `GET/PUT /api/admin/simulados/<id>`, `POST .../publicar`, `POST .../arquivar` | `/admin/simulados.html`, `/admin/simulado.html` |
| Plano | `GET /api/aluno/plano`, `POST .../gerar`, `POST .../recalcular`, `POST .../itens/<id>/concluir`; negativa em `/api/aluno/privacidade/consentimento-plano/{recusar,revogar}` | `/aluno/plano.html`, `/aluno/privacidade.html` |

Controllers por recurso e Services por caso de uso existem para os fluxos listados; não há Controller independente para cada item de composição ou registro técnico, pois são coordenados pelo recurso pai. A matriz final deverá ligar os casos às classes/fontes existentes, sem inventar uma Controller por tabela.

## Demais quinze Models

| Model | Papel | Operações expostas ou coordenadas pelo recurso |
| --- | --- | --- |
| `AreaEnem` | Referência fixa | GET das quatro áreas; sem telas/rotas públicas de criação, edição ou exclusão. Possui métodos herdados, mas o catálogo é fixo. |
| `PraticaTentativa` | Execução de prática | Iniciar, consultar/listar próprias e responder com correção; não há DELETE nem edição arbitrária de resposta concluída. |
| `SimuladoTentativa` | Execução de Simulado | Iniciar/retomar, consultar histórico/resultado/correção e finalizar; sem DELETE público. |
| `SimuladoRascunhoItem` | Item do agregado Simulado | Adição/ordenação/remoção dentro da edição da composição; sem recurso CRUD isolado. |
| `SimuladoResposta` | Resposta de tentativa | Criada no início; gravada/limpa durante tentativa; corrigida na finalização. Sem CRUD genérico de respostas. |
| `PlanoEstudoItem` | Item do agregado Plano | Criado na geração, consultado/concluído pelo dono e eliminado somente junto aos planos na negativa confirmada. |
| `AssuntoTransferencia` | Registro de transferência | Criado pelo caso de uso de transferência; sem edição/exclusão expostas. Herda CRUD, o que não constitui permissão irrestrita na API. |
| `QuestaoVersao` | Snapshot editorial | Criado na publicação e consultado para uso/histórico; base sem atualizar/deletar e guards ORM de imutabilidade. |
| `QuestaoEvento` | Evidência editorial | Criado pelas ações editoriais; sem atualizar/deletar na base e com guards. |
| `SimuladoVersao` | Snapshot da composição | Criado na publicação e consultado; sem atualização/exclusão na base e com guards. |
| `SimuladoVersaoItem` | Item de snapshot publicado | Criado junto da versão e consultado; sem atualização/exclusão na base e com guards. |
| `SimuladoEvento` | Evidência editorial | Criado pelas ações editoriais; sem atualizar/deletar na base e com guards. |
| `RegistroPrivacidade` | Evidência de decisão | Aceitar/recusar/revogar produz novo registro; consulta de situação/evidências próprias. Base sem atualizar/deletar e com guards. |
| `Sessao` | Infraestrutura de identidade | Preparação/rotação, consulta própria, renovação, reautenticação, revogação e limpeza por CLI; sem CRUD administrativo manual. |
| `AuthLimite` | Infraestrutura de limitação | Criado/atualizado nas tentativas e limpo operacionalmente; sem tela de manutenção de limites internos. |

## Pendências reais e continuidade proposta

| ID | Achado | Próximo passo, sem implementação nesta change |
| --- | --- | --- |
| D01 | Não há modelagem anterior entregue para comparar | Formalizar o domínio atual e identificar sua data/estado, mantendo a entrega acadêmica como responsabilidade do grupo. |
| F01 | Gestão completa de Usuários ausente | Se incluída no escopo acadêmico, propor change funcional específica. Definir acesso de Administrador/dono, campos, listagem/detalhe, reautenticação, alteração de identidade e efeitos sobre sessões antes de implementar. |
| F02 | GET individual dedicado de Matéria/Assunto ausente | Propor complemento se o caso de uso buscar por ID precisar ser demonstrado isoladamente, preservando listagens/edições atuais. O método de Model já existe. |
| E01 | Arquivamento de Questão/Simulado difere de DELETE físico | Registrar a diferença; confirmar o critério de avaliação do ciclo editorial. Não declarar exclusão implementada nem remover versões/eventos para fabricar um DELETE. |
| E02 | Algumas Models são itens, fatos, referências fixas ou infraestrutura | Explicitar a classificação e os casos de uso que as controlam. A justificativa técnica não comprova dispensa concedida pelo professor. |
| E03 | Seis Models não oferecem atualizar/deletar e duas não oferecem deletar | Documentar as capacidades do ADR-008 e a exceção participante do plano. Não acrescentar métodos incompatíveis só para aparentar CRUD completo. |

### Restrição relevante de Usuário

O cadastro público grava a conta e um `RegistroPrivacidade` de aceite na mesma transação. Esse registro aponta para `usuarios` com `ON DELETE RESTRICT` e é protegido contra exclusão; sessões e fatos também referenciam a conta. Portanto, não é correto prometer um DELETE de conta pública apenas com a condição “sem práticas”: o aceite já cria um vínculo.

Uma proposta futura deve resolver essa política explicitamente. Desativação de conta, arquivamento e exclusão física são operações distintas; não substituir uma pela outra nem apagar evidências silenciosamente. Não há autorização para alterar retenção, privacidade ou FKs neste levantamento.

## Conclusão delimitada

A arquitetura e os dois CRUDs convencionais estão presentes. A leitura literal de CRUD para toda Model principal não pode ser certificada com base apenas na lista das vinte funcionalidades ou nos métodos herdados. A formalização documental torna as diferenças verificáveis, mas não implementa F01/F02 nem equivale a uma aprovação de E01/E02/E03 pelo professor.
