# Entrega acadêmica

Esta matriz usa a numeração oficial das vinte
[Funcionalidades Implementadas](../../README.md#funcionalidades-implementadas).
Não conta CI, testes, documentação ou melhorias internas como novos casos de uso.
O [diagrama](diagrama-de-classes.md) descreve as 21 Models concretas, incluindo
a evidência de privacidade da extensão acadêmica.

A [modelagem de domínio atual](modelagem-de-dominio.md) explica os seis módulos
do recorte original e os papéis dessas Models. A organização atual acrescenta
`tutor_ia` como sétimo módulo, sem Model, tabela ou Repository próprios, conforme
o [adendo do ADR-010](adr/ADR-010-organizacao-modular-do-backend.md#adendo--tutor-pontual-09112026).
As 21 Models permanecem; a [matriz CRUD](matriz-crud.md) separa persistência,
API/caso de uso e interface, incluindo lacunas e restrições. A formalização de
07/11/2026 não comprova modelagem entregue anteriormente, nova execução dos
fluxos ou aprovação docente. Os vinte IDs abaixo permanecem; sua cobertura não
certifica CRUD integral de cada entidade. Na organização modular atual, a
eliminação dos derivados do plano é executada pelo participante de Plano
injetado nas negativas de Contas, conforme o
[adendo do ADR-010](adr/ADR-010-organizacao-modular-do-backend.md#adendo-ao-adr-009).

## Rastreabilidade dos vinte casos

UI consome os sete Blueprints proprietários (`contas`, `conteudo`, `praticas`,
`simulados`, `desempenho`, `plano_estudos` e `tutor_ia`), agregados por
[routes.py](../../backend/app/routes.py), que delegam a
Controllers e Services. `AR` abaixo significa CRUD Active Record da Model,
sem duplicação no Repository. O teste de navegador é
[entrega-academica.spec.js](../../frontend/e2e/entrega-academica.spec.js),
com um `test.step` numerado para cada caso; setup adicional é identificado.
Mutações verificam status real; persistência usa recarga ou leitura independente.

| ID | Módulo proprietário | Tela/ação | Método e rota | Controller → Service | Model / Repository → tabelas | Teste e evidência |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `conteudo` | `/index.html`: cadastrar Matéria | `POST /api/materias` | `MateriaController.cadastrar` → `CriarMateriaService` | `Materia` AR; `AreaEnem` → `materias`, `areas_enem` | E2E 01: 201 e cartão após recarga |
| 2 | `conteudo` | `/index.html`: atualizar lista | `GET /api/materias` | `MateriaController.listar` → `ListarMateriasService` | `Materia` AR → `materias` | E2E 02: lista real contém ID criado |
| 3 | `conteudo` | `/index.html`: editar Matéria | `PUT /api/materias/<id>` | `MateriaController.atualizar` → `AtualizarMateriaService` | `Materia` AR; `CatalogoRepository` para impacto → `materias`, vínculos do catálogo | E2E 03: 200 e nome alterado após recarga |
| 4 | `conteudo` | `/index.html`: excluir Matéria livre | `DELETE /api/materias/<id>` | `MateriaController.deletar` → `DeletarMateriaService` | `Materia` AR; `CatalogoRepository` para impacto → `materias`, `assuntos`, `questoes`, `assunto_transferencias` | E2E 04: confirmação, 204 e ausência após recarga |
| 5 | `conteudo` | `/index.html`: cadastrar Assunto | `POST /api/assuntos` | `AssuntoController.cadastrar` → `CriarAssuntoService` | `Assunto` AR; `Materia`; `CatalogoRepository` para unicidade → `assuntos`, `materias` | E2E 05: 201 e cartão após recarga |
| 6 | `conteudo` | `/index.html`: atualizar Assuntos | `GET /api/assuntos` | `AssuntoController.listar` → `ListarAssuntosService` | `CatalogoRepository.listar_assuntos_ativos`; `Assunto` → `assuntos`, `materias` | E2E 06: lista contém ID; integração cobre filtros/status/ordem |
| 7 | `conteudo` | `/index.html`: editar Assunto | `PUT /api/assuntos/<id>` | `AssuntoController.atualizar` → `AtualizarAssuntoService` | `Assunto` AR; `Materia`; `CatalogoRepository` → `assuntos`, `materias` | E2E 07: 200 e nome alterado após recarga |
| 8 | `conteudo` | `/index.html`: excluir Assunto livre | `DELETE /api/assuntos/<id>` | `AssuntoController.deletar` → `DeletarAssuntoService` | `Assunto` AR; `CatalogoRepository` para impacto → `assuntos`, `questoes`, `assunto_transferencias` | E2E 08: confirmação, 204 e ausência após recarga |
| 9 | `conteudo` | `/index.html`: cadastrar Questão | `POST /api/questoes` | `QuestaoController.cadastrar` → `CriarQuestaoService` | `Questao` AR; `QuestaoEvento`; `Assunto`, `Materia` → `questoes`, `questao_eventos`, catálogo | E2E 09: 201; conteúdo recuperado no caso 10 |
| 10 | `conteudo` | `/index.html`: buscar por Assunto | `GET /api/questoes/por-assunto?assunto_id=<id>` | `QuestaoController.buscar_por_assunto` → `BuscarQuestoesPorAssuntoService` | `ConsultaQuestoesPorAssuntoMySQL` → `QuestaoRepository.buscar_por_assunto` → `CALL sp_questoes_por_assunto`, `questoes` | E2E 10: busca após recarga exibe conteúdo persistido |
| 11 | `contas` | `/cadastro`: criar conta com aceite de uso | `POST /api/auth/cadastro` | `AutenticacaoController.cadastro` → `CadastrarAlunoService` | `Usuario` e `RegistroPrivacidade` AR → `usuarios`, `registros_privacidade`, uma transação | E2E 11: checkbox explícito, 201, redirecionamento; perfil Aluno comprovado no login |
| 12 | `contas` | `/login`: entrar | `POST /api/auth/login`; `GET /api/auth/sessao` | `AutenticacaoController.login` → `LoginService` | `Usuario`, `Sessao`, `AuthLimite`; `AutenticacaoRepository` → `usuarios`, `sessoes`, `auth_limites` | E2E 12: 200, sessão consultada independentemente e usuário após recarga |
| 13 | `conteudo` | `/admin/questao.html?id=<id>`: salvar edição | `PUT /api/questoes/<id>` | `QuestaoController.editar` → `EditarQuestaoService` | `Questao`, `QuestaoEvento` AR; `QuestaoRepository` → `questoes`, `questao_eventos`, `questao_versoes` | E2E 13: 200 e campo atualizado após recarga |
| 14 | `conteudo` | Mesma tela: revisar/publicar | `POST /api/questoes/<id>/publicar` | `QuestaoController.publicar` → `PublicarQuestaoService` | `Questao`, `QuestaoVersao`, `QuestaoEvento`; `QuestaoRepository` → conteúdo e snapshots | E2E 14: motivo/confirmação, 200 e estado publicado após recarga |
| 15 | `conteudo` | Mesma tela: arquivar | `POST /api/questoes/<id>/arquivar` | `QuestaoController.arquivar` → `ArquivarQuestaoService` | `Questao`, `QuestaoEvento`; `QuestaoRepository` → `questoes`, `questao_eventos` | E2E 15: 200, estado arquivado após recarga e correção histórica preservada |
| 16 | `praticas` | `/aluno/questoes.html`: iniciar | `GET /api/aluno/questoes`; `POST /api/aluno/praticas` | `PraticaController.questoes/iniciar` → `ListarQuestoesAlunoService`, `IniciarPraticaService` | `PraticaTentativa`; `PraticaRepository`; `ConsultaQuestoesElegiveisMySQL`/`QuestaoRepository` → `pratica_tentativas`, `questao_versoes` e catálogo | E2E 16: 201; GET independente e recarga; nenhum gabarito/explicação antecipado |
| 17 | `praticas` | `/aluno/questao.html?tentativa_id=<id>`: responder | `POST /api/aluno/praticas/<id>/resposta` | `PraticaController.responder` → `ResponderPraticaService` | `PraticaTentativa`; `PraticaRepository`; conteúdo histórico de Questões → `pratica_tentativas`, `questao_versoes` | E2E 17: 200 e correção visível após recarga |
| 18 | `praticas` | `/aluno/historico.html`: consultar | `GET /api/aluno/praticas`; `GET /api/aluno/praticas/<id>` | `PraticaController.historico/detalhe` → `ListarPraticasService`, `ConsultarPraticaService` | `PraticaRepository`; `PraticaTentativa`; conteúdo histórico → `pratica_tentativas`, `questao_versoes` | E2E 18: classificação, resposta e link da tentativa persistidos |
| 19 | `simulados` | `/admin/simulado.html`: compor/salvar | `POST /api/admin/simulados`; `GET /api/admin/simulados/<id>` | `SimuladoController.criar/admin_detalhe` → `CriarSimuladoService`, `ConsultarSimuladoAdminService` | `Simulado`, `SimuladoRascunhoItem`, `SimuladoEvento`; `SimuladoRepository`; fronteira de Questões → `simulados`, `simulado_rascunho_itens`, `simulado_eventos`, `questao_versoes` | E2E 19: 201, título/composição após recarga |
| 20 | `desempenho` | `/aluno/desempenho.html`: consultar | `GET /api/aluno/desempenho` | `DesempenhoController.diagnostico` → `ConsultarDesempenhoService` | `ConsultaMetricasMySQL`/`DesempenhoRepository`, projeções de Práticas/Simulados/Questões → `pratica_tentativas`, `simulado_tentativas`, `simulado_respostas`, `simulado_versao_itens`, `questao_versoes` | E2E 20: Matéria/Assunto próprios e percentual após recarga |

O caso 15 é executado após práticas e criação/publicação do Simulado: arquivar
antes impediria os novos usos corretamente. A classificação mostrada no
histórico é o snapshot da tentativa, sem exigir enunciado nesse DTO de lista.

## Fluxogramas de recuperação e entrada de dados

Os [dois fluxogramas](fluxogramas-casos-de-uso.md) detalham decisões,
camadas, Repository, Models, MySQL e retorno à interface:

- **Recuperação:** consultar diagnóstico de desempenho, caso 20,
  `GET /api/aluno/desempenho`, sem gravar métricas.
- **Entrada:** finalizar tentativa própria de Simulado,
  `POST /api/aluno/tentativas-simulado/<id>/finalizar`, com confirmação,
  correção histórica e persistência atômica. É um caso adicional já
  implementado de execução/resultado; o caso 19 continua sendo criar a
  composição fixa, e a lista oficial permanece com vinte funcionalidades.

Os fluxogramas acrescentam documentação e rastreabilidade, sem substituir as
evidências de execução abaixo ou contar como funcionalidades novas.

## Evidências e reprodução

- [Relatório local](../../openspec/changes/archive/2026-11-06-consolidar-entrega-academica/validacao.md):
  comandos, versões, resultados históricos e limitações da consolidação.
- [Relatório SOLID](../../openspec/changes/archive/2026-11-06-refatorar-backend-com-solid/validacao.md):
  refatoração, preservação do baseline e regressão executada naquela change.
- A suíte atual contém **seis testes Playwright em seis arquivos**: os vinte
  casos numerados continuam passos de um único teste
  em [entrega-academica.spec.js](../../frontend/e2e/entrega-academica.spec.js);
  [plano-simulado.spec.js](../../frontend/e2e/plano-simulado.spec.js) usa conta/conteúdo próprios
  para gerar/concluir Plano, finalizar/corrigir Simulado e confirmar recálculo.
  Verifica 2/5 (40%) no plano inicial, resultado 1/3 (33,33%) e diagnóstico/novo
  plano 3/7 (42,86%), excluindo o branco do diagnóstico, além de cancelamentos
  sem POST e persistência. O replay HTTP de histórico é auxiliar técnico sem
  botão, separado das ações pela interface. Não acrescenta funcionalidades à
  matriz. Estado de execução e limites no
  [relatório do percurso](../../openspec/changes/archive/2026-11-06-validar-fluxos-de-plano-e-simulado/validacao.md).
  [privacidade.spec.js](../../frontend/e2e/privacidade.spec.js) cobre documentos
  públicos, cadastro com aceite explícito, recusa mantendo práticas/Simulados,
  autorização/geração/conclusão do plano, revogação com eliminação e nova
  autorização, incluindo plano aberto em outra aba. Esses percursos adicionais
  não alteram os IDs 1–20 da matriz.
  [tutor.spec.js](../../frontend/e2e/tutor.spec.js) cobre navegação, uso antigo,
  novo aceite e indisponibilidade com o Tutor desabilitado, sem chamar Gemini
  nem comprovar geração de resposta pela IA.
  [catalogo-detalhe.spec.js](../../frontend/e2e/catalogo-detalhe.spec.js) confere
  a leitura atual de Matéria/Assunto ao editar após mudanças em outra aba,
  sem escrita automática nem transferência indevida.
  [usuarios.spec.js](../../frontend/e2e/usuarios.spec.js) cobre gestão de Alunos:
  CRUD permitido, exclusão bloqueada por vínculos, revogação de sessões,
  reativação e troca de e-mail, com revisão em 1440/390 px. Os seis testes, seus
  setups e as ferramentas de validação não ampliam a lista oficial de vinte casos.
- `npm run test:e2e:list` somente descobre os seis testes, sem executar seus
  percursos nem comprovar aprovação; `RUN_MYSQL_E2E=1 npm run test:e2e`
  em shell POSIX ou o exemplo PowerShell do [README](../../README.md) a executa.
- `test-results/e2e.json` registra os testes e seus passos, incluindo os vinte
  numerados do primeiro; capturas sintéticas em
  `test-results/browser/` mostram Plano/Admin a 1440 e 390 px. São artefatos
  locais ignorados pelo Git, reproduzidos a cada execução, sem sessão exportada.
- Testes adicionais cobrem exclusões vinculadas 409, ausência de correção
  antecipada, link do plano nas oito páginas, foco/Enter e cancelamento de
  descarte com alternativa preservada. A suíte DOM mantém regressões de
  expiração, troca de conta e recuperação; integrações usam MySQL real.
- As 29 integrações originais permanecem, complementadas pelas suítes de
  autenticação, catálogo, versões, Práticas, Simulados, desempenho e plano.
- O checkpoint publicado
  [`6f40f1303560cad908fbdd752fd0aaa4dd285b3b`](https://github.com/Matibas100/ProjetoSoftwarePE/commit/6f40f1303560cad908fbdd752fd0aaa4dd285b3b)
  teve CI concluído com sucesso na
  [execução 42337772001](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42337772001),
  em 7 de novembro de 2026. Esse resultado se limita àquele SHA; alterações
  posteriores, incluindo este alinhamento documental local, não herdam a aprovação.
  Os relatórios históricos mantêm seus resultados originais. Essa publicação
  de código não comprova hospedagem na AWS ou demonstração acadêmica do grupo.
- O checkpoint publicado mais recente
  [`bb9823de87f3be6ae4d0a0cb3484ff2725353d7e`](https://github.com/Matibas100/ProjetoSoftwarePE/commit/bb9823de87f3be6ae4d0a0cb3484ff2725353d7e)
  teve CI concluído com sucesso na
  [execução 42736058343](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42736058343),
  em 9 de novembro de 2026, às 22:36:40 (America/Sao_Paulo;
  10/11/2026 às 01:36:40 UTC). A execução corresponde a esse SHA e antecede esta
  correção documental. A revisão dos links e contagens nesta change é uma
  checagem documental local, sem nova execução da suíte da aplicação e sem
  herdar a aprovação do CI. As evidências históricas e os limites de entrega
  externa e aceite docente permanecem.

## Entrega externa

As exigências recebidas pertencem a atividades distintas:

| Fonte | Demonstração e escopo informado |
| --- | --- |
| Atividade anterior | Pelo menos vinte funcionalidades completas; vídeo obrigatório de até cinco minutos, demonstrando os casos e a arquitetura, além dos demais itens do enunciado. |
| Rubrica final recebida | Pelo menos quatro funcionalidades principais não CRUD; demonstração de até dois minutos, por vídeo ou execução hospedada. Não exige mostrar todas as vinte. Slides continuam exigidos. |

Não se presume que a rubrica final substitui ou dispensa a entrega anterior.
O cronograma de 2025 não é atribuído à turma de 2026. Consultas/listagens
isoladas não têm contagem garantida entre as quatro funcionalidades principais.
A evidência automatizada comprova somente o que for executado; não substitui
a demonstração do grupo nem garante nota. Vídeo, slides, roteiro, hospedagem e
envio não são produzidos por esta change e continuam sob responsabilidade do grupo.
O [registro de publicação e CI no README](../../README.md#checkpoint-publicado-e-ci)
identifica o checkpoint aprovado e distingue as alterações posteriores ainda
locais. Commit, push e merge dependem de autorização explícita para a operação;
esta limpeza não autoriza novas operações Git. O fechamento técnico local
depende dos testes e da verificação registrados no relatório.


## Composição e persistência após SOLID

As vinte entradas mantêm as mesmas rotas e comportamentos. Os casos 10, 16 e 20 agora
consomem consultas por contratos, compostas na factory. As outras seis consultas do
recorte apoiam catálogo administrativo, histórico/catálogo de Simulados e dashboards;
não contam como funcionalidades novas. Ver [aplicação SOLID](aplicacao-solid.md).

O recorte SOLID conservou vinte Models. A extensão de privacidade acrescenta
`RegistroPrivacidade` em ModeloBase: são agora 21 Models, seis em ModeloBase,
PlanoEstudo/PlanoEstudoItem em ModeloAtualizavel e treze em CrudMixin.
A migration 010 acrescenta a tabela de evidências; migrations anteriores e
procedure permanecem intactas.

Gerar/recalcular plano recebem o seletor que usa o mesmo DiagnosticoAluno do dashboard.
É adaptação necessária da composição: as dependências concretas de escrita do plano,
seus locks, replays e TransactionManager permanecem. O plano continua fora da contagem
dos vinte percursos de referência; sua regressão adicional é preservada.

## Extensão acadêmica de termos e consentimento

Os dois documentos completos estão em [docs/legal](../legal/README.md), com
fontes HTML públicas, versão, data e impressão. Foram adaptados dos modelos do
professor e descrevem apenas o sistema implementado, sem CPF/testemunhas,
assinatura, IA ou certificação ISO presumidas.

`PrivacidadeController` encaminha metadados/consulta aos Services respectivos
e quatro ações fixas a `AceitarTermosUsoService`, `ConsentirPlanoService`,
`RecusarConsentimentoPlanoService` e `RevogarConsentimentoPlanoService`.
`RegistroPrivacidade` grava a evidência; `PrivacidadeRepository` lê decisões
correntes/replays e elimina derivados próprios somente na negativa confirmada.
Os quatro casos de plano validam os dois aceites vigentes no servidor. Consulte
[contratos e efeitos](operacao-privacidade.md), [diagrama](diagrama-de-classes.md)
e [fluxogramas](fluxogramas-casos-de-uso.md).

`/aluno/privacidade.html` mostra evidências e escolhas; início/plano e navegação
oferecem acesso. Recusa/revogação mantém práticas, simulados e diagnóstico;
elimina somente planos próprios, sem restaurá-los na autorização posterior.
O [E2E de privacidade](../../frontend/e2e/privacidade.spec.js) cobre esse percurso;
a lista original de vinte casos é mantida.

Responsável informado: Matheus Gabriel Oliveira Martins. Contato
`contato@plataformaenem.example` fictício e não operacional. Entrega demonstrativa
com dados sintéticos; contato válido, retenção geral/direitos e proteção de menores
dependem de outra change antes de dados reais. Os termos não garantem bônus ou
adequação jurídica integral. Esta change não publica, hospeda ou envia a entrega.

## Consultas acadêmicas por procedures

O caso 20 mantém a mesma funcionalidade e passa a executar a agregação por
`DesempenhoRepository` → `sp_desempenho_resumo`, com duas views de fatos
históricos. As três listas administrativas e os dois dashboards também usam
as procedures de seus proprietários. Os caminhos Controller → Service →
Repository → procedure, parâmetros, telas e quatro views estão no
[documento SQL técnico](consultas-academicas-mysql.md).

As vinte entradas acima conservam IDs, rotas e significado. Procedures auxiliares
não contam como novas funcionalidades. As etapas 013–016 e a auditoria abaixo
delimitam a cobertura especializada; este recorte não comprova aceite acadêmico.

O Catálogo editorial da migration 013 acrescenta quinze procedures auxiliares
para seletores, impactos, transferência, locks e versões/elegibilidade de Questões.
As cadeias dos casos 3–10 e 13–19 continuam nas mesmas rotas/Services, com as
consultas especializadas correspondentes no Repository. Históricos e gabaritos
mantêm suas regras anteriores; as vinte funcionalidades não foram renumeradas.

A migration 014 cobre dezesseis consultas auxiliares de Práticas/Simulados.
Nos casos 16–18, `PraticaRepository` usa propriedade/replay/histórico por
procedures e preserva a resposta definitiva na Model. No caso 19, composição,
lotes e lock de gestão passam por `SimuladoRepository`; cadastro de itens e
eventos continua nas Models. Início/retomada, salvar/limpar e finalização/correção
usam as mesmas rotas e Services da execução complementar de Simulados.
As [dezesseis correspondências e caminhos ponta a ponta](consultas-academicas-mysql.md#práticas-e-simulados--migration-014)
incluem fatos internos e histórico, sem Controller/tela por consulta auxiliar.
O caso 20 continua consumindo as views históricas de 012.

A migration 015 cobre seis interfaces complementares de Plano. Na mesma
`aluno/plano.html`, `PlanoEstudoController` → Services de consultar/gerar/recalcular/
concluir → `PlanoEstudoRepository` usa atual/replay/itens/item próprio por procedures;
seleção usa a elegibilidade pela API de Conteúdo. `aluno/privacidade.html` →
`PrivacidadeController` → Services de recusa/revogação → participante de Plano
usa `sp_eliminar_planos_proprios` na transação da negativa, sem DELETE público.
Os [contratos e caminhos](consultas-academicas-mysql.md#plano-de-estudos--migration-015)
preservam prioridade no Service, autorização anterior aos derivados e escrita
individual nas Models. Contas é coberta pela etapa 016 abaixo. Os vinte IDs e
critérios acadêmicos permanecem, sem funcionalidade extra por contar routines.

A migration 016 cobre onze interfaces de Contas: no caso 12, login e sessão
seguem AutenticacaoController → LoginService/ConsultarSessaoService →
AutenticacaoRepository → procedures de identidade, sessão e limite. O caso 11
mantém cadastro/aceite na Model e uma transação; logout/reautenticação e CLI
continuam auxiliares. Privacidade mantém a mesma tela/Controller e Services:
lock exato → replay/últimas decisões correntes por procedures → evidência na
Model → participante da 015 nas negativas. Os [onze contratos e caminhos](consultas-academicas-mysql.md#contas-e-privacidade--migration-016)
preservam permissões, senha no Service, cookies/CSRF, regras temporais e rollback.

A [auditoria final por fonte e consumidor](consultas-academicas-mysql.md#auditoria-dos-seis-módulos)
confere os seis módulos e distingue CRUD, projeções de compatibilidade e SQL
efetivamente executado. As projeções antigas são executadas somente na regressão
de equivalência; as rotas de produção usam interfaces SQL proprietárias.
F01/F02 e demais critérios da [matriz CRUD](matriz-crud.md) permanecem próprios;
não há nova funcionalidade, envio ou promessa de aprovação acadêmica.
