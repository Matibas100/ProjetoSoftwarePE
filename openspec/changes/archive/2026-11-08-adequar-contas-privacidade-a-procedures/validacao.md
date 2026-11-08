# Validação — Contas e Privacidade por procedures

## Preflight — 08/11/2026

**Estado da aplicação:** **12/12 tarefas concluídas**, após autorização do usuário (“faz o q achar melhor”). As seções de pausa abaixo preservam o histórico da descoberta; o ajuste de conjunto único já foi autorizado, planejado, implementado e validado. O fechamento autorizado é registrado ao final.

- Change local, schema `spec-driven`, inicialmente 0/12 tarefas. Aplicadas as quatro orientações do CLI: preflight somente leitura, escopo mínimo, pausa diante de conflito de design e conclusão somente após validação.
- Dependência 015 aplicada, verificada, sincronizada e arquivada em `archive/2026-11-08-adequar-plano-estudos-a-procedures/`. Conferidos tasks/relatório, spec principal `plano-estudos-mysql`, requisito da 015 em `migrations-sql`, definição da migration e reconhecimento/preflight existentes. A execução MySQL abaixo comprovou instalação e reconhecimento físico até 015 em schema descartável.
- Nenhum arquivo `016*` existia em `backend/database/migrations/`. A sequência anterior permanece 000–015; nenhuma migration foi criada nesta sessão.
- Estado inicial em `tmp/contas-status-inicial.txt`; hashes dos arquivos preexistentes em `tmp/contas-baseline.json`. Há alterações externas de 011–015, Repositories, Models de Conteúdo, infraestrutura, testes e documentação, além das changes/specs correspondentes. Preservadas integralmente.
- Lidos AGENTS, cinco conventions, architecture-master, ADRs 001/002/003/004/005/006/008/009/010/011 e todos os artefatos da change, incluindo inventário. Nenhuma mudança de contrato HTTP, Model de produção, schema, regra de negócio ou artefato visual nesta sessão.
- Conteúdo de `.env` e credenciais não foi exibido. Integrações usam o carregamento de configuração existente, dados sintéticos e schema descartável; sem DDL no banco de uso. Não foram executados commit, push, merge, sincronização ou arquivamento.

## Inventário de métodos e consumidores

| Fonte | Consumidor existente | Contrato a preservar |
|---|---|---|
| `Usuario.buscar_por_email` | `LoginService`; delegação futura ao Repository proprietário | Usuário gerenciado interno; comparação binária; normalização e senha no Service |
| `AutenticacaoRepository.consultar_sessao` | `ConsultarSessaoService` → preparação CSRF, autorização HTTP e sessão atual | LEFT JOIN, relação gerenciada inclusive anônima, `populate_existing`, validade no Service |
| `renovar_acesso` | `ConsultarSessaoService.renovar`, `ReautenticarService` | Booleano de correspondência, limites estritos, mesma transação |
| `revogar` | `CriarSessaoService`, `LogoutService` | Retorno atual `None`, atualização condicional, rotação atômica |
| `revogar_usuario` | Operação interna exercitada pela integração; sem rota própria | Contagem explícita de sessões do dono |
| `usuario_ativo_bloqueado` | `CriarSessaoService`, `ValidarSenhaService` | Usuário ativo gerenciado, leitura corrente FOR UPDATE |
| `limite_bloqueado` | `ValidarSenhaService` | Upsert e lock participantes; contador/janela/bloqueio no Service |
| `limpar` | `LimparAutenticacaoService` → CLI `limpar-autenticacao` | Contagens de sessões/limites, cortes originais e rollback externo |
| `PrivacidadeRepository.bloquear_usuario` | Services de decisão/consulta; API pública consumida por Plano | Lock exato inclusive identidade inativa; sem novo filtro |
| `ultimas` | Consulta, permissão do Plano e quatro Services de decisão | Última evidência uso e plano, nessa ordem, leitura corrente bloqueante |
| `por_chave` | Aceitar uso, consentir, recusar e revogar | Evidência própria gerenciada, replay corrente e append-only |

## Caracterização executada

Comando (opt-in somente no processo):

```powershell
$env:RUN_MYSQL_INTEGRATION='1'
$env:PYTHONPATH='backend'
python -m unittest tests.test_contas_procedures_integration -v
```

**2 testes aprovados**, 3,677 s; saída 0. Evidência local: `tmp/contas-caracterizacao.log`.

- Caracterizados e-mail/collation sem normalização SQL, entrada tratada como dado, resultado ausente, sessão anônima e usuário associado com identidade compartilhada, Boolean/DATETIME, mutação participante e rollback; HTTP 200 sem campos internos de senha/sessão.
- Procedure de ensaio com LEFT JOIN completo, aliases explícitos e FOR UPDATE, instalada somente no schema descartável. Mapeamento `from_statement` com `contains_eager`/`populate_existing` preservou Sessão/Usuário gerenciados, recarregou mudança confirmada em outra conexão e tratou resultado vazio/anônimo. Result fechado em `finally`, consulta seguinte reutilizou a conexão e rollback reverteu a mutação. Routine de ensaio removida em `finally` e schema removido pela fixture.
- Tarefa 1.2 permanece aberta: o ensaio seguinte encontrou incompatibilidade do contrato de dois conjuntos com o caminho ORM aprovado. Nenhum fallback, mapeador novo ou alteração de produção foi usado para contorná-la.

## Achado de design que interrompe a aplicação

O inventário define `sp_ultimas_decisoes_privacidade(usuario_id)` com **dois conjuntos**: uso e plano. O design/proposta preserva entidades ORM gerenciadas para métodos que alimentam escrita e proíbe um novo mapeador genérico ou hidratação manual/transiente. `ultimas` também alimenta revisão e validação nos Services que gravam novas decisões.

Ensaio real: `RUN_MYSQL_INTEGRATION=1; PYTHONPATH=backend; python tmp/contas-prova-multiplos.py`: **1 teste aprovado**, 3,180 s, saída 0 (`tmp/contas-multiplos-resultados.log`). A routine sintética fez as duas leituras sequenciais FOR UPDATE previstas:

1. `Session.execute(select(RegistroPrivacidade).from_statement(CALL...))` entregou somente `uso` como entidade gerenciada; o Result ORM não disponibilizou `nextset` público. Fechar o Result drenou o conjunto seguinte, permitindo reutilização da conexão.
2. O helper existente `executar_resultados` entregou ambos os conjuntos completos, porém como dicionários, sem identidade ORM.

Isso demonstra que o caminho usado pelo projeto não atende simultaneamente aos dois contratos aprovados. Não constitui prova de impossibilidade de outras APIs/implementações, que exigiriam decisão técnica adicional. A produção permanece no caminho anterior, completo e funcional; a migration 016 não foi iniciada.

### Ajuste proposto para decisão do usuário

Preferência: alterar somente o contrato de resultado de `sp_ultimas_decisoes_privacidade` para **um conjunto com até duas evidências completas**, em ordem uso → plano. A routine mantém duas leituras correntes bloqueantes sequenciais: captura colunas completas em variáveis locais (`SELECT ... INTO ... FOR UPDATE`), primeiro uso, depois plano; devolve os valores capturados em uma única projeção estática, omitindo tipos ausentes. O Repository usa `from_statement` e recompõe o dicionário atual `{'uso': entidade_ou_None, 'plano': entidade_ou_None}`. Não há nova leitura de snapshot, hidratação manual, Model transiente ou mudança de HTTP/Service/locks/transação.

Antes de implementar, atualizar de forma coerente design, inventário e tarefa 4.1, e caracterizar no MySQL tipos, conjuntos vazios/parciais/completos, identidade e atualização concorrente depois de snapshot antigo. Proposal/specs devem ser conferidas para manter o contrato coerente; os requisitos funcionais não precisam ser enfraquecidos. Esta proposta de ajuste **ainda não foi aplicada nem autorizada**.

Alternativa: permitir explicitamente um registro imutável de leitura para `ultimas`, mantendo dois conjuntos e o helper atual. Isso altera o contrato Python interno de retorno e exige registrar a exceção ao requisito de entidades gerenciadas; não foi adotado silenciosamente.

A skill `openspec-apply-change`, passo 6, determina: “Implementation reveals a design issue → suggest updating artifacts” e “surface the added scope and ask”. A aplicação está pausada nessa decisão, com 1/12 tarefas concluídas. Não foram executados os gates completos/cobertura/E2E, pois a implementação não ocorreu.

## Revisão da pausa

- `openspec validate adequar-contas-privacidade-a-procedures --strict`: aprovado.
- `git diff --check`: saída 0; somente avisos preexistentes de normalização LF/CRLF em dois arquivos externos ao recorte.
- Comparação SHA-256 contra o snapshot inicial: somente `tasks.md` mudou entre arquivos preexistentes. Acrescentados este relatório e os dois testes de caracterização; ensaio/logs permanecem em `tmp/`. Produção, SQLs anteriores, visuais, textos legais e alterações externas preservados. Os dois arquivos novos estão em UTF-8 válido.
- CLI confirma **1/12 tarefas concluídas**, mantendo `state: ready`; a pausa decorre do guardrail de design da skill, não de estado bloqueado do CLI. A implementação só deve continuar após a decisão sobre o ajuste descrito acima.

## Retomada autorizada e implementação — 08/11/2026

- O usuário autorizou escolher a melhor solução e continuar. Aplicada a opção de um conjunto ORM. Pela skill `openspec-update-change`, revisados design, inventário, tarefa 4.1 e cenário adicional da spec de Contas; proposal e delta de migrations continuam coerentes, sem precisar de alteração. `openspec validate ... --strict` aprovado. Retomada a skill `openspec-apply-change`, sem nova confirmação para o ajuste já autorizado.
- `RUN_MYSQL_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_contas_procedures_integration -v`: **3 testes aprovados antes da conversão**, 4,358 s, saída 0 (`tmp/contas-caracterizacao-016.log`). Incluída prova da routine definitiva: um conjunto ORM vazio/parcial/completo, ordem uso/plano, tipos DATETIME(6)/inteiros, identidade persistente e decisão corrente confirmada depois de snapshot antigo. Tarefa 1.2 concluída.
- Implementadas onze procedures estáticas na 016: seis READS SQL DATA e cinco MODIFIES SQL DATA, todas SQL SECURITY INVOKER. Bootstrap acrescenta exatamente os bytes da nova migration; seus bytes anteriores são preservados. As 48 referências anteriores foram recomputadas/conferidas e mantidas; onze novas vieram somente das migrations oficiais em schema descartável, removido em `finally`. Nenhuma rotina funcional foi chamada durante instalação/baseline.
- Repositories de Contas usam CALLs fixos e vinculados, mesma sessão/conexão, flush e fechamento em `finally`/helper existente. `Usuario.buscar_por_email` apenas delega ao proprietário. Sessão completa usa `contains_eager`/`populate_existing`, inclusive relação anônima. Renovações sincronizam somente último acesso; revogações expiram somente o atributo de revogação dos alvos. Demais campos pendentes são preservados. Limpeza expira somente sessões/limites carregados; evidências/contas permanecem.
- Senha, hash fictício, HMAC, normalização, relógio, regras temporais, limites, CSRF/origens/cookies, replay/revisão e versões legais continuam nos mesmos Services. Controllers/rotas/CLI, composição, guards, contratos públicos e demais Models não foram alterados. O participante de eliminação da 015 continua na única transação da negativa.

### Regressões específicas

- `RUN_MYSQL_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_contas_procedures_integration tests.test_autenticacao_integration tests.test_privacidade_integration tests.test_planos_integration -v`: **35 testes aprovados**, 42,399 s, saída 0 (`tmp/contas-conversao.log`). Inclui cinco falhas/429/Retry-After, senha correta durante bloqueio, login/reautenticação independentes, primeira tentativa concorrente, sessões independentes, revogação concorrente, rotação com falha real e rollback; privacidade/replay/revisões/negativas/snapshot antigo e participante da 015.
- Suíte específica ampliada `tests.test_contas_procedures_integration`: **8 testes aprovados**, 5,810 s, saída 0 (`tmp/contas-procedures.log`). Além da caracterização, comprova igualdades exatas de 8h/30min, margem de 1µs, renovação com timestamp inalterado, contagens próprias, sincronização seletiva e rollback. Limite gerenciado conserva contador/janela e criação não é confirmada antecipadamente. Lock de identidade inativa bloqueia UPDATE real em outra conexão (1205), sem adicionar filtro de ativo; replay é isolado por dono.
- Limpeza cobre expiração/revogação/inatividade e todas as igualdades dos cortes, anonimato, bloqueio nulo/igual/vigente, outra conta válida, evidências antigas e contagens correspondentes ao número real de remoções. Trigger MySQL no segundo DELETE provoca falha e rollback externo restaura o primeiro DELETE; nenhuma conta/evidência é removida. Durante desenvolvimento, ajustado o teste para esperar a exceção nativa PyMySQL do helper DBAPI, antes da execução aprovada.
- Ausência de cada uma das onze routines falha sem fallback: respostas HTTP 500 seguras nos caminhos existentes, CLI com saída não zero e erro interno propagado na revogação global. Não há senha, e-mail sintético, hashes ou nomes/SQL de routines nas respostas de erro. Logger HTTP existente registra somente contexto constante e nome da classe da exceção, sem mensagem/traceback/parâmetros; preservado. Conexão e sessão são reutilizáveis após restauração da definição.

### Instalação e reconhecimento

- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_contas_procedures_migrations_integration tests.test_plano_procedures_migrations_integration -v`: **10 testes aprovados**, 94,655 s, saída 0 (`tmp/contas-migrations.log`). São cinco testes novos de 016 e cinco regressões do recorte 015, que continua fixado até 015; o teste de bootstrap desse recorte desconsidera somente as novas definições de 016 para preservar a comparação histórica.
- Comprovados instalação vazia, equivalência integral bootstrap/sequência, upgrade 015→016 com sessão/limite/evidência/plano/item sintéticos intactos, baseline/restauração, segunda aplicação zero, assinaturas/corpos/segurança e ausência de cada routine. IDs acima de 2^31, parâmetros estruturais inválidos, vazio útil com nove colunas e conjunto terminal drenado também cobertos.
- Sob lock do runner, drift de tabela/legada/015 e indícios parciais/completos de 016 são rejeitados **antes de RUNNING/DDL**: dados, histórico e objetos permanecem; lock liberado e reparação permite upgrade. Preservadas proteções anteriores de checksum/RUNNING/FAILED/metadados indisponíveis. Reconhecimento exige 59 referências oficiais; preflight exige 016. Regressões gerais de migrations/restauração/privacidade acrescentam 016 sem remover prefixos antigos.
- `PYTHONPATH=backend; python backend/tests/run_unit.py`: **183 unitários aprovados**, 2,648 s, saída 0 (`tmp/contas-unit.log`), incluindo arquitetura, composição, metadata, capacidades/guards e infraestrutura SQL. Gates não alterados.

### Auditoria e documentação

- Conferidos todos os métodos executores dos oito Repositories proprietários nos seis módulos contra os cinco inventários. A extração AST das chamadas e comparação dos nomes comprova correspondência integral com os inventários (mais a legada); classificação/consumidores conferidos na fonte. Evidência local: `tmp/contas-auditoria.json`; ver [tabela técnica](../../../../docs/technical/consultas-academicas-mysql.md#auditoria-dos-seis-módulos).
- Conteúdo: seletores/admin/impactos/contagens/equivalência/locks/versões/elegibilidade e pares de Plano têm CALL correspondente; Práticas: propriedade/replay/histórico/fatos; Simulados: gestão/composição/lotes/listas/tentativas/andamento/respostas/histórico/fatos; Desempenho: agregação/atividades/contagens por APIs; Plano: atual/replay/itens/propriedade/eliminação; Contas: onze interfaces e delegação da Model. Nenhum executor especializado de produção fora do inventário encontrado.
- Cinco projeções Select permanecem para compatibilidade (`projecao_desempenho`/`projecao_atividades` de Práticas e Simulados e classificação histórica de Conteúdo). Rastreado o único executor: regressão de equivalência de `test_desempenho_integration`; produção usa procedures/views de 012. `bloquear_classificacao` compõe locks e busca básica por PK; `administrativo` compõe APIs; contexto empresta conexão/instante; adaptadores apenas delegam. CRUD/relacionamentos básicos/refresh por PK e flush não foram confundidos com consultas especializadas.
- README, documento SQL técnico, matrizes acadêmica/CRUD e adendo ao ADR-011 atualizados com contratos, caminhos Controller/Service/Repository/tela, CLI/auxiliares, privilégios, pré-condições e compensação. Nenhuma funcionalidade renumerada; F01/F02/E01–E03 permanecem abertas, sem promessa de aceite acadêmico. Links locais e vinte IDs conferidos por `python tmp/contas-revisar.py`.
- Revisão até aqui: `openspec validate adequar-contas-privacidade-a-procedures --strict`, `git diff --check` e auditoria de escopo/hashes/UTF-8/links aprovados. Snapshot comprova alterações somente nos arquivos permitidos desta change; migrations 000–015, fontes externos, serviços/contratos/frontend/legais/visuais preservados. A execução completa de cobertura/MySQL/frontend/E2E está em andamento; tarefas 6.1/6.2 continuam abertas até os resultados finais.

### Frontend e navegador

- `npm run test:coverage`: **15 arquivos / 182 testes aprovados**, 44,99 s, saída 0. Linhas **99,26% (1879/1893)**; branches **87,98% (1325/1506)**; gate de arquivo executável sem cobertura preservado (`tmp/contas-frontend-completo.log`).
- `scripts.run_e2e.executar_suite(settings, ambiente)` com `RUN_MYSQL_E2E=1`: **3 E2Es aprovados**, 57,0 s, saída 0 (`tmp/contas-e2e-completo.log`). Configuração existente usada somente em memória/ambiente, sem imprimir credenciais. Cobertos os vinte casos originais, sessão/navegação, geração/conclusão/recálculo de Plano, Simulado e decisões/eliminação/nova autorização de privacidade com persistência MySQL real. Runner confirmou remoção do schema e encerrou os processos locais em `finally`.

## Resultado final da aplicação

- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; python backend/tests/run_backend_coverage.py`: **183 unitários e 197 integrações MySQL aprovados**, sem integrações puladas, saída 0. Unitários em 11,016 s; integrações em **640,048 s** (`tmp/contas-backend-completo.log`). Incluídas as 29 integrações originais, os treze testes novos da 016, suíte ampliada, arquitetura, metadata/guards, concorrência/rollback e todos os prefixos antigos.
- Cobertura backend: **97,60% de linhas (4357/4464)** e **92,14% de branches (914/992)**; gate de arquivo executável sem cobertura aprovado. Frontend: **182 testes**, **99,26% / 87,98%**; navegador: **3 E2Es** com MySQL real. Nenhum gate reduzido e nenhuma integração substituída por SQLite/mocks.
- `openspec validate adequar-contas-privacidade-a-procedures --strict`, `git diff --check` e revisão final de escopo/hashes/segredos/links/UTF-8: aprovados. As dezesseis migrations anteriores, procedure legada, conteúdo anterior do bootstrap, fontes/alterações externas fora do recorte, Services/Controllers/rotas/contratos, frontend/legais e visuais permanecem preservados. CALLs novos somente nos Repositories. As definições não controlam transação, não usam SQL dinâmico nem relógio paralelo.
- **12/12 tarefas concluídas**, schema `spec-driven`: onze procedures, migration/bootstrap 016, dois Repositories de Contas e delegação de e-mail da Model, reconhecimento/preflight, testes MySQL e documentação/auditoria implementados. O ajuste aprovado preserva duas leituras correntes ordenadas e entrega um conjunto ORM gerenciado.
- Banco de uso não migrado: aplicar e validar a **016 antes de disponibilizar o novo código** nesse ambiente. Todas as escritas/DDL dos ensaios ficaram em schemas descartáveis limpos pelas fixtures/runners. Sem commit, push, merge ou deploy.
- Próximas etapas: verificar formalmente a implementação, sincronizar os dois deltas e arquivar sem achados críticos. Esta aplicação não executou sincronização ou arquivamento.

## SHA-256 das migrations anteriores

| Arquivo | SHA-256 inicial |
|---|---|
| `011_consultas_admin_procedures.sql` | `2fc6aace67b5e6121d44d3e1840baaa00582332f6bdd3a8bffd37e655fe5e665` |
| `012_desempenho_procedures.sql` | `0fb8b07c76e5428bef37a06daefc206cdc55a115257d81e263064cbcb34734b8` |
| `013_catalogo_editorial_procedures.sql` | `8db9ea8917cb621d68ce9679828fc1a3f5dcd9364b51ca3dfd0a702e2bc1d2dd` |
| `014_praticas_simulados_procedures.sql` | `fb63b6c3ba688157dd9e48cecb1ab89a31408c0b0020d9c754e0b31359d951a9` |
| `015_plano_estudos_procedures.sql` | `48e11fdbfa5260cd2d0c1b479ad4f137354ad2c1f03cc163252246b32692de70` |
| `000_create_mvp_schema.sql` | `1e51d54b93a4d8125961a17e283e2933fa3fe1f0b8b385b6d50ede1bcdf868a8` |
| `001_restrict_delete_assuntos.sql` | `329594db44e2ee7f6a71b4c8a871cc5efb1dd849642ed4397b49a3ae7dca0b5d` |
| `002_create_sp_questoes_por_assunto.sql` | `7d19427eaed0f6e63ec4116aee0aa56cf07a2e12b6e559c2a09f5409414abd38` |
| `003_prepare_catalogo_academico.sql` | `dd27f63de40fd06585c4a3cbd33a9f164574ae983b3eeb3cffb8ff91a8decbd4` |
| `004_restrict_catalogo_academico.sql` | `de6bedc463391556498fe641cb61fe74a59717b421c59e0dfcb1d6ff71a804d8` |
| `005_create_autenticacao_escolar.sql` | `a650da20e8785b4de919e0324928844a282f63b76bacce0f752fdb55332fb8c2` |
| `006_create_questoes_versionadas.sql` | `97160b8fb019d8dc59e7f83452808b5fefd9a1944f20850d6336880822e2b36c` |
| `007_create_pratica_tentativas.sql` | `2ca7fc6c974dfa2e0011d72bc532a00a0e4cca8d9ab0055cdd9c4b93f58c3161` |
| `008_create_simulados.sql` | `b21286bbfcb77ba6bad04c1eda72d7fbc71b39dc825c847238cce1b73d71fe36` |
| `009_create_planos_estudo.sql` | `22763b2c463d65995f79a93aaa34a6ff3a760f591d94cfb19822be646126a624` |
| `010_create_registros_privacidade.sql` | `d91e31207a77afc6077c7dc7002b08fa7f2180f6df2dbe43a920d2107915d2dc` |

## Verificação para fechamento — 08/11/2026

Usuário autorizou verificar, sincronizar e arquivar após a aplicação. Usadas as skills locais `openspec-verify-change`, `openspec-sync-specs` e `openspec-archive-change`, no mesmo escopo local retornado pelo CLI. Lidos artefatos, inventário, AGENTS/conventions e confrontados SQL, Repositories, Services, reconhecimento/preflight, documentação e testes. Considerados contexto e as duas orientações de archive: tarefas completas/sem críticos e sync comprovado antes de arquivar. Nenhum conflito com as instruções do usuário.

| Dimensão | Resultado |
|---|---|
| Completude | 12/12 tarefas; seis requisitos de Contas e um de migrations, com dezesseis cenários, representados por implementação e testes |
| Correção | 183 unitários, 197 integrações MySQL (29 originais incluídas), 182 testes frontend e 3 E2Es aprovados; coberturas backend 97,60%/92,14% e frontend 99,26%/87,98%; gates preservados |
| Coerência | Onze CALLs especializados em Repositories; identidade ORM, locks correntes uso→plano, transação externa, validação no Service e participante restrito da 015 preservados; sem tabela/contrato HTTP novo |

Evidências por requisito: `autenticacao_repository.py`/`usuario.py` e os testes de caracterização/indisponibilidade cobrem interfaces vinculadas, e-mail/collation e erro seguro; testes originais de autenticação e oito específicos da 016 cobrem permissões, CSRF, limites, revogação, upsert/contagem e rollback. `privacidade_repository.py` e as duas capturas completas da 016 conservam leituras correntes e mapeamento gerenciado; regressões de Privacidade/Plano cobrem replay, concorrência após snapshot, negativa e participante. `migrate.run_up` verifica 015 físico sob lock antes de RUNNING/DDL; `sql_resources` exige todas as 59 referências oficiais e os cinco testes novos de migrations comprovam instalação/upgrade/baseline/restauração, drift e segurança. A auditoria dos seis módulos rastreia executores e projeções até consumidores reais.

Conferidos os logs completos da execução recém-concluída nesta conversa e timestamps dos fontes: nenhum código ou teste foi alterado depois da coleta completa. Não há motivo para repetir a suíte de aplicação durante este fechamento documental. Reexecutados `openspec validate adequar-contas-privacidade-a-procedures --strict`, `git diff --check` e auditoria de escopo/hashes/UTF-8/links/vinte IDs: aprovados. Snapshot adicional em `tmp/contas-fechamento-snapshot.json` protege os arquivos preexistentes nesta etapa.

**Sem achados CRÍTICOS ou AVISOS bloqueantes. Pronta para sync/archive.** A verificação não alterou código, tasks ou decisões de planejamento. O banco de uso continua sem DDL, e disponibilizar o código continua exigindo aplicar/validar a 016. Operações Git e deploy permanecem fora do fechamento.

## Sincronização das specs — 08/11/2026

- Criada a spec principal `contas-privacidade-mysql` com os seis requisitos, seus doze cenários e Purpose original. Acrescentado a `migrations-sql` o requisito da 016 com quatro cenários, preservando byte a byte todo seu conteúdo anterior, inclusive Purpose e requisitos históricos.
- Regras atuais de specs obtidas uma única vez pelo CLI antes da primeira escrita. Aplicadas ao conteúdo/formato das specs principais, sem copiar instruções em texto e sem alterar roots, caminhos ou workflow. Mantidos requisitos observáveis, validações/erros/permissões/compatibilidade e keywords normativas.
- Comparação integral dos dois deltas contra as specs principais: **sete requisitos e dezesseis cenários idênticos**, nenhuma operação pendente ou cabeçalho de operação delta na spec principal. A sincronização é idempotente: novo assessment não encontra nada para aplicar.
- `openspec validate --specs`: **16 specs aprovadas**, nenhuma falha. `openspec validate adequar-contas-privacidade-a-procedures --strict` e `git diff --check`: aprovados. Snapshot confirmou preservação de implementação, testes, tasks, planejamento e demais alterações externas.
- Usuário já autorizou as três etapas do fechamento. Todas as tasks e artefatos completos, sem críticos, ambos os deltas sincronizados e alvo de arquivo inexistente. Arquivamento pelo CLI usará `--skip-specs` apenas para evitar reaplicar os deltas já sincronizados/comparados; não suprime validação. Sem nova alteração de código, banco ou operação Git.

## Arquivamento — 08/11/2026

- `openspec archive adequar-contas-privacidade-a-procedures --skip-specs --yes --json`: saída 0; arquivada em `openspec/changes/archive/2026-11-08-adequar-contas-privacidade-a-procedures/`. O flag evitou reaplicar as specs já sincronizadas e comparadas; nenhuma validação foi suprimida.
- Origem/destino absolutos conferidos dentro do projeto, alvo inexistente antes do movimento. `.openspec.yaml` e todos os artefatos preservados. Snapshot confirmou identidade dos arquivos movidos e ausência da pasta ativa, além de implementação/testes e alterações externas intactos. Ajustado somente o link relativo do relatório para a profundidade do arquivo.
- Workflow concluído: aplicada, verificada, sincronizada e arquivada, **12/12 tarefas**, sem achado crítico. Specs principais conferidas contra os deltas arquivados. Banco de uso, commit/push/merge e deploy permanecem fora deste fechamento.
