# Consultas acadêmicas por procedures

Recorte da change `adequar-consultas-academicas-a-procedures`, regido pelo
[ADR-011](adr/ADR-011-interfaces-sql-de-leitura.md). São seis entradas HTTP existentes,
sete procedures e quatro views; não são funcionalidades adicionais às vinte da entrega.

## Interfaces e caminhos

| Entrada/tela | Controller/Service | Repository e procedure |
|---|---|---|
| `/api/admin/materias`; `admin/materias.html` | MateriaController / ListarMateriasAdminService | ConsultaMateriasMySQL → CatalogoRepository → `sp_materias_admin` |
| `/api/admin/assuntos`; `admin/assuntos.html` | AssuntoController / ListarAssuntosAdminService | ConsultaAssuntosMySQL → CatalogoRepository → `sp_assuntos_admin` |
| `/api/admin/questoes`; `admin/questoes.html` | QuestaoController / ListarQuestoesAdminService | QuestaoRepository → `sp_questoes_admin` |
| `/api/aluno/desempenho`; `aluno/desempenho.html` | DesempenhoController / ConsultarDesempenhoService | ConsultaMetricasMySQL → DesempenhoRepository → `sp_desempenho_resumo` |
| `/api/aluno/dashboard`; `aluno/inicio.html` | DesempenhoController / ConsultarDashboardAlunoService | diagnóstico acima + DesempenhoRepository → `sp_atividades_recentes` |
| `/api/admin/dashboard`; `admin/dashboard.html` | DesempenhoController / ConsultarDashboardAdminService | APIs públicas → CatalogoRepository/QuestaoRepository e SimuladoRepository → `sp_conteudo_contagens_dashboard`, `sp_simulados_contagens_dashboard` |

Todas as chamadas usam parâmetros vinculados, `READS SQL DATA` e
`SQL SECURITY INVOKER`, sem transação interna. Não há SQL em Service/Controller.
Os nomes de classes e o estado implementado são conferidos na validação da change.

## Contratos SQL

| Migration / procedure | Entradas IN, em ordem | Saídas úteis, em ordem |
|---|---|---|
| 011 / `sp_materias_admin` | busca VARCHAR(100), status VARCHAR(20), area_enem_id BIGINT UNSIGNED, pagina BIGINT UNSIGNED, por_pagina INT | Matéria/Área com aliases, assuntos/questoes DISTINCT; total |
| 011 / `sp_assuntos_admin` | busca VARCHAR(100), status VARCHAR(20), area_enem_id BIGINT UNSIGNED, materia_id BIGINT UNSIGNED, pagina BIGINT UNSIGNED, por_pagina INT | Assunto/Matéria/Área com aliases, questoes; total |
| 011 / `sp_questoes_admin` | busca VARCHAR(100), status VARCHAR(20), dificuldade VARCHAR(10), area_enem_id/materia_id/assunto_id BIGINT UNSIGNED, pagina BIGINT UNSIGNED, por_pagina INT | conteúdo e metadata Questão/Assunto/Matéria/Área com aliases; total |
| 011 / `sp_conteudo_contagens_dashboard` | nenhuma | matérias/assuntos ativos, Questões por estado |
| 012 / `sp_desempenho_resumo` | usuario_id INT, inicio/fim DATETIME(6) | geral; grupos por Matéria; grupos por Matéria/Assunto |
| 012 / `sp_atividades_recentes` | usuario_id INT, inicio/fim DATETIME(6) | até cinco atividades por instante/tipo/ID decrescentes |
| 012 / `sp_simulados_contagens_dashboard` | nenhuma | Simulados por estado e tentativas finalizadas |

Filtros opcionais usam NULL; busca vazia conserva ausência de filtro.
Matérias/Assuntos preservam LIKE; Questões escapa `%`, `_` e o escape `/`.
Total independe da página. Datas são serializadas como antes na aplicação.
Paginação positiva, limite até 100, IDs positivos, estados/dificuldades e intervalos
estruturais são validados também nas routines. Não se acrescentam limites HTTP.

## Views públicas de origem

| View / proprietário | Colunas e predicados |
|---|---|
| `vw_conteudo_classificacao_historica` / Conteúdo | questao_versao_id, materia_id/nome, assunto_id/nome; versões publicadas |
| `vw_praticas_fatos_desempenho` / Práticas | tipo, id, atividade_id, usuario_id, ocorrido_em, correta, materia_id/nome, assunto_id/nome; respondidas |
| `vw_simulados_fatos_desempenho` / Simulados | mesmas colunas de fatos; respostas não brancas em tentativas finalizadas e classificação pela view de Conteúdo |
| `vw_simulados_atividades` / Simulados | tipo, id, usuario_id, ocorrido_em, titulo; uma linha por tentativa finalizada, inclusive em branco |

São projeções históricas, sem filtros pelo estado corrente do catálogo. Métricas
unem fatos por UNION ALL; `[inicio, fim)` e microssegundos são preservados.
Rótulos seguem o fato mais recente por instante/tipo/ID. Percentuais, erros,
limiar de amostra e destinos permanecem nos Services. O Plano reutiliza o mesmo
diagnóstico na conexão/instante externos, com seus locks e consentimento atuais.

## Operação e limites

Instalação/upgrade devem ocorrer explicitamente pelo runner oficial, com backup
e prefixo anterior válido: 010 → 011 → 012. Não há DML funcional, tabelas novas
ou migração automática no startup. O instalador precisa de CREATE ROUTINE,
CREATE VIEW e privilégios sobre os objetos referenciados; o invocador precisa
de EXECUTE e SELECT nas dependências. Nenhuma conta/host é fixado como DEFINER.

DDL MySQL não tem rollback transacional garantido. Falha mantém as proteções
RUNNING/FAILED/checksum e requer reconciliação. Compensação revisada: voltar
primeiro ao código anterior e restaurar backup ou remover recursos novos na
ordem inversa (procedures antes das views dependentes), preservando dados,
procedure legada e histórico. Não apagar checksums nem executar downgrade implícito.

Comandos de operação, após o backup e a revisão do ambiente de destino:

```powershell
python backend/database/migrate.py status
python backend/database/migrate.py up
python backend/database/migrate.py status
```

Restauração sem histórico usa `baseline --confirm` somente após o reconhecimento
do prefixo completo; falha usa `reconcile --help` para consultar o procedimento
oficial, após inspeção e compensação. Reexecutar `up` após sucesso aplica zero
migrations. Estes comandos não são executados automaticamente por esta change.

O reconhecimento valida primeiro as tabelas de 010 e compara assinaturas IN,
corpos, modo SQL e segurança das routines, além das definições, colunas/tipos e
dependências das views. As onze assinaturas em
`backend/database/sql_resources_reference.json` foram obtidas instalando somente
migrations oficiais num schema descartável. Só o qualificador do schema local
e a identidade física do DEFINER ficam fora da comparação. Literais, destinos
externos e SQL SECURITY são preservados; metadados insuficientes e recursos
parciais bloqueiam sem recuo para prefixo inferior.

As etapas 013–016 descritas abaixo cobrem o recorte especializado inventariado
dos seis módulos. A auditoria final distingue as projeções ainda disponíveis
dos caminhos efetivamente executados. CRUD básico
permanece Active Record. As etapas não prometem aceite do professor nem
representam envio acadêmico.

## Catálogo e Questões editoriais — migration 013

A migration 013 acrescenta quinze procedures de leitura sobre as mesmas 21
Models. O conjunto 011–013 contém **22 procedures novas e quatro views**, além
da procedure legada preservada. As quatro Áreas e seus IDs permanecem intactos.

| Métodos de Conteúdo / procedure | Entradas IN | Saída / ordem |
|---|---|---|
| AreaEnem.listar_ordenadas → CatalogoRepository.listar_areas_ordenadas / `sp_areas_enem_ordenadas` | nenhuma | Área completa; ordem/ID |
| Materia.listar_ativos → CatalogoRepository.listar_materias_ativas / `sp_materias_ativas` | nenhuma | Matéria completa; nome/ID |
| listar_assuntos_ativos / `sp_assuntos_ativos` | materia_id opcional | Assunto completo com Matéria ativa; nome_normalizado/ID |
| impacto_materia / `sp_impacto_materia` | materia_id | uma linha: assuntos, questoes, transferencias |
| impacto_assunto / `sp_impacto_assunto` | assunto_id | uma linha: questoes, transferencias |
| contar_assuntos_nao_arquivados / `sp_assuntos_nao_arquivados` | materia_id | uma linha: total |
| buscar_assunto_para_atualizacao / `sp_bloquear_assunto` | assunto_id | Assunto completo FOR UPDATE |
| buscar_materias_para_atualizacao / `sp_bloquear_materias` | ids_json JSON | Matérias completas por ID crescente FOR UPDATE |
| existe_assunto_equivalente / `sp_assunto_equivalente` | materia_id, nome_normalizado VARCHAR(150) utf8mb4_0900_ai_ci, ignorar_id opcional | uma linha: existe; inclui arquivados |
| QuestaoRepository.bloquear / `sp_bloquear_questao` | questao_id | Questão completa FOR UPDATE |
| versoes / `sp_versoes_questao` | questao_id | versões completas por numero crescente |
| versao_elegivel / `sp_questao_versao_elegivel` | versao_id, bloquear TINYINT 0/1 | versão elegível completa; FOR UPDATE quando solicitado |
| listar_elegiveis / `sp_questoes_elegiveis` | assunto_id opcional, materia_id opcional, pagina, limite INT | versões completas por questao_id; segundo conjunto: total |
| versoes_elegiveis / `sp_questoes_versoes_elegiveis` | ids_json JSON | versões elegíveis sem duplicação |
| versoes_historicas / `sp_questoes_versoes_historicas` | ids_json JSON | versões publicadas, usando a view histórica pública de Conteúdo |

IDs/página usam BIGINT UNSIGNED, preservando filtros acima de 2³¹. Arrays usam
JSON_TABLE com IDs distintos; vazios não inventam linhas. As routines validam
formato estrutural, sem repetir regras de negócio ou normalizar nomes no SQL.
Todas são READS SQL DATA / SQL SECURITY INVOKER, sem commit/rollback próprios.

Leituras que alimentam escrita usam `select(...).from_statement(CALL)` com
colunas completas/tipadas, entidades gerenciadas e `populate_existing` nos locks.
Resultados são fechados em finally e o driver drena conjuntos subsequentes.
A listagem de apresentação usa o helper de múltiplos resultados; o adaptador
retira gabarito/explicação por whitelist, preservando o contrato seguro do Aluno.

### Caminhos existentes e locks

| Entrada/tela | Controller → Service → acesso especializado |
|---|---|
| `/api/areas-enem`, `/api/materias`, `/api/assuntos`; seletores administrativos/Aluno | AreaEnemController/MateriaController/AssuntoController → Services de listagem → Models/delegações → CatalogoRepository → seletores |
| impactos de exclusão/status e transferência; `admin/materias.html`, `admin/assuntos.html` | MateriaController/AssuntoController → Services de impacto/exclusão/status/TransferirAssuntoService → CatalogoRepository → impacto/equivalência/locks |
| detalhe/publicação/arquivamento; `admin/questao.html` | QuestaoController → ConsultarQuestaoService/PublicarQuestaoService/ArquivarQuestaoService → QuestaoRepository → lock/versões/classificação |
| `/api/aluno/questoes`; `aluno/questoes.html` | PraticaController → ListarQuestoesAlunoService → adaptador público → QuestaoRepository → listagem elegível |
| início/correção de Práticas e composição/execução de Simulados | Services proprietários → APIs públicas de Conteúdo → elegibilidade/versões históricas; não há rota por procedure auxiliar |

Publicação mantém a ordem Questão → Assunto → Matéria corrente. Transferência
mantém Assunto → Matérias por ID crescente. Ambos revalidam após os locks na
mesma conexão/transação externa. Falha posterior reverte a operação inteira.
Histórico preserva versões publicadas antigas após nova publicação ou retirada;
elegibilidade exige somente os predicados anteriores de cada método. A igualdade
adicional usada por `pares_elegiveis_plano` é implementada na etapa 015 abaixo.

### Instalação e reconhecimento de 013

O upgrade oficial segue 012 → 013, sem DML funcional durante instalação ou
baseline. O bootstrap contém as mesmas definições. O prefixo 013 exige
seus contratos íntegros. O reconhecimento conserva as onze assinaturas
anteriores e acrescenta quinze geradas exclusivamente por instalação oficial
em schema descartável; ausência ou divergência de recurso bloqueia sem recuo.
Os prefixos anteriores continuam reconhecíveis com seus próprios recursos.

Privilégios, backup, comandos de status/up/baseline e proteções RUNNING/FAILED
seguem a seção operacional acima. Para compensar 013: voltar primeiro ao código
anterior e restaurar backup ou remover somente as quinze routines em migration
revisada; preservar views, versões, dados e recursos 000–012. Não há rollback DDL
automático, alteração de checksums antigos ou implantação por efeito colateral.

## Práticas e Simulados — migration 014

A 014 acrescenta dezesseis procedures específicas: o conjunto 011–014 tem
**38 procedures novas e quatro views**, além da legada intacta. Não há alteração
de tabelas, colunas, índices, FKs, 21 Models ou contratos HTTP. Todas as novas
rotinas são `READS SQL DATA` e `SQL SECURITY INVOKER`, com SQL estático e parâmetros
vinculados. Nenhuma grava resposta, corrige ou finaliza tentativa no banco.

| Repository.método → procedure | Parâmetros IN na ordem | Resultado / predicado / ordem |
|---|---|---|
| Pratica.por_chave → `sp_pratica_por_chave` | usuario_id, chave, bloquear | tentativa completa do dono/chave; FOR UPDATE opcional |
| Pratica.propria → `sp_pratica_propria` | usuario_id, tentativa_id, bloquear | tentativa completa do dono/ID; FOR UPDATE opcional |
| Pratica.historico → `sp_praticas_historico` | usuario_id, assunto_id opcional, pagina, limite | somente respondidas do dono/Assunto; respondida_em/ID decrescentes; segundo conjunto total |
| Pratica.fatos → `sp_praticas_fatos` | usuario_id, inicio, fim | respondidas do dono em [início,fim); respondida_em/ID crescentes |
| Simulado.bloquear → `sp_bloquear_simulado` | simulado_id | Simulado completo FOR UPDATE |
| Simulado.itens → `sp_simulado_itens` | simulado_id opcional, versao_id opcional | rascunho se versão NULL, senão versão; posição crescente |
| Simulado.itens_em_lote → `sp_simulados_itens_lote` | simulado_ids_json opcional, versao_ids_json opcional | mesma precedência; identidade/posição crescentes; sem duplicação |
| Simulado.andamentos_em_lote → `sp_simulados_andamentos_lote` | usuario_id, versao_ids_json | tentativas em andamento do dono/versões |
| Simulado.titulos_em_lote → `sp_simulados_titulos_lote` | versao_ids_json | pares ID/título das versões |
| Simulado.listar → `sp_simulados_listar` | pagina, limite, estado opcional | Simulados por ID decrescente; segundo conjunto total |
| Simulado.propria → `sp_simulado_tentativa_propria` | usuario_id, tentativa_id, bloquear | tentativa do dono/ID; FOR UPDATE opcional |
| Simulado.por_chave → `sp_simulado_tentativa_por_chave` | usuario_id, chave | tentativa do dono/chave FOR UPDATE |
| Simulado.andamento → `sp_simulado_em_andamento` | usuario_id, versao_id | tentativa em andamento do dono/versão FOR UPDATE |
| Simulado.respostas → `sp_simulado_respostas` | tentativa_id, bloquear | par Resposta/Item completo com aliases r_/i_; posição crescente; FOR UPDATE opcional |
| Simulado.historico → `sp_simulados_historico` | usuario_id, pagina, limite | finalizadas do dono; finalizada_em/ID decrescentes; segundo conjunto total |
| Simulado.fatos → `sp_simulados_fatos` | usuario_id, inicio, fim | tripla Resposta/Item/Tentativa finalizada do dono; alternativa não nula, [início,fim); finalizada_em/Resposta.id crescentes |

Os prefixos Pratica/Simulado na tabela representam `PraticaRepository` e
`SimuladoRepository`. IDs/página são BIGINT UNSIGNED; limite INT (1–100), locks
TINYINT 0/1, chave CHAR(36) ascii_bin e datas DATETIME(6) UTC fornecidas pelo
chamador. Lotes usam JSON_TABLE e IN de IDs distintos, com validação estrutural;
vazios retornam vazio e os adaptadores mantêm o atalho anterior sem consulta.
Estado/filtros textuais são dados vinculados, sem critérios SQL interpolados.

Leituras ORM de entidade/par/tripla selecionam todas as colunas na ordem mapeada,
com aliases explícitos nos JOINs. Os locks usam `populate_existing`; respostas
mantêm essa opção mesmo sem lock, como antes. Flush preserva a visibilidade das
escritas pendentes. Results são fechados em finally, drenando os conjuntos
subsequentes pelo driver; não se cria outra sessão/conexão. Históricos/listagem
usam o helper participante de múltiplos resultados e registros tipados, com total
independente da página e bool/Decimal/datas preservados na serialização.

### Caminhos e limites de exposição

| Entrada / tela | Controller → Service → Repository / métodos |
|---|---|
| POST `/api/aluno/praticas`; `aluno/questoes.html` | PraticaController.iniciar → IniciarPraticaService → PraticaRepository.por_chave; elegibilidade pela API de Conteúdo |
| GET detalhe e POST resposta de prática; `aluno/questao.html` | PraticaController.detalhe/responder → ConsultarPraticaService/ResponderPraticaService → propria; correção no Service, salvar na Model |
| GET `/api/aluno/praticas`; `aluno/historico.html` | PraticaController.historico → ListarPraticasService → historico; ConsultarFatosPraticasService → fatos é auxiliar interno |
| `/api/admin/simulados`; `admin/simulados.html`, `admin/simulado.html` | SimuladoController → Services de listar/criar/editar/consultar/publicar/arquivar → listar/bloquear/itens/itens_em_lote; revisão/publicação/eventos nas mesmas transações |
| GET `/api/aluno/simulados`; `aluno/simulados.html` | SimuladoController.catalogo → ListarSimuladosAlunoService → ConsultaCatalogoSimuladosMySQL → listar/itens_em_lote/andamentos_em_lote |
| POST `/api/aluno/tentativas-simulado`; `aluno/simulado.html` | SimuladoController.iniciar → IniciarSimuladoService → por_chave/andamento; retomada preserva composição capturada |
| detalhe, PUT respostas, POST finalizar, GET resultado/correção; `aluno/simulado.html` | SimuladoController → ConsultarTentativaSimuladoService/ResponderSimuladoService/FinalizarSimuladoService → propria/respostas; correção/totais no Service, escrita nas Models |
| GET histórico; `aluno/simulados.html` | SimuladoController.historico → ListarHistoricoSimuladosService → ConsultaHistoricoSimuladosMySQL → historico/titulos_em_lote; ConsultarFatosSimuladosService → fatos é auxiliar interno |

Propriedade vem da sessão; ID alheio/ausente conserva 404 uniforme. Respostas e
itens internos podem conter correção, mas gabarito/explicação chegam ao HTTP
somente após a etapa permitida. Salvar/limpar exige revisão; finalizar mantém
ordem de lock tentativa → respostas por posição, calcula totais no Service e
confirma tudo uma vez. Falha após corrigir parte das respostas reverte tudo.
Replay e retomada mantêm versões; conteúdo retirado impede novo início conforme
as regras anteriores. A constraint de dono/versão/andamento continua intacta.
Históricos/fatos não incluem tentativas abertas; fatos de Simulado excluem
brancos e conservam classificação histórica pela API pública de Conteúdo.
Desempenho continua consumindo as quatro views de 012, sem cálculo duplicado;
as projeções Python de compatibilidade não são executadas pelos adaptadores.

### Instalação e reconhecimento de 014

Requer 013 íntegro, MySQL 8 com JSON_TABLE e privilégios de CREATE ROUTINE,
EXECUTE e SELECT dos recursos lidos. Segue backup/status/up/baseline e o fluxo
RUNNING/FAILED/reconciliação já documentados. Código que chama 014 só deve ser
disponibilizado após atualização/verificação do destino. Startup não instala DDL.

Antes de iniciar 014, o runner exige o prefixo físico 013 validado pelo detector
existente, sob seu lock e depois das proteções de histórico/checksum/falha. Isso
confere tabelas, procedure legada e recursos SQL oficiais anteriores; falha de
metadados também bloqueia. A recusa ocorre antes de RUNNING/DDL de 014, preserva
dados/histórico/objetos e libera o lock. Reparar a dependência permite nova
tentativa; objetos parciais de 014 exigem a compensação já documentada.

Bootstrap e migration contêm as mesmas definições, sem DML funcional. O prefixo
014 exige seus contratos íntegros. São 42 referências SQL oficiais, dezesseis novas
geradas por instalação em schema descartável; as 26 anteriores permanecem iguais.
Recursos ausentes, metadados insuficientes ou corpo/assinatura/segurança divergentes
bloqueiam o baseline, sem recuo silencioso. Prefixos anteriores e checksums 000–013
continuam protegidos. Compensação: retornar primeiro ao código anterior e depois
restaurar backup ou remover somente as dezesseis routines por migration revisada,
preservando versões, dados, views e histórico. Não existe rollback DDL automático.

## Plano de Estudos — migration 015

A 015 acrescenta seis interfaces: o conjunto 011–015 contém **44 procedures novas
e quatro views**, além da legada preservada. Cinco são `READS SQL DATA`; a eliminação
participante é `MODIFIES SQL DATA`. Todas têm SQL estático, parâmetros vinculados,
`SQL SECURITY INVOKER` e nenhuma instrução de controle de transação, DDL em runtime,
SQL dinâmico ou desativação de FKs. Não há mudança em tabelas, Models ou HTTP.

| Proprietário / Repository.método → procedure | IN na ordem | Resultado / locks |
|---|---|---|
| Plano / PlanoEstudo.atual → `sp_plano_atual` | usuario_id BIGINT UNSIGNED, bloquear TINYINT | Plano atual completo; FOR UPDATE opcional |
| Plano / PlanoEstudo.por_chave → `sp_plano_por_chave` | usuario_id BIGINT UNSIGNED, chave CHAR(36) ascii_bin | Plano próprio/chave completo FOR UPDATE |
| Plano / PlanoEstudo.itens → `sp_plano_itens` | plano_id BIGINT UNSIGNED | Itens completos por posição FOR UPDATE |
| Plano / PlanoEstudo.item_proprio → `sp_plano_item_proprio` | usuario_id BIGINT UNSIGNED, item_id BIGINT UNSIGNED | JOIN Item/Plano completos, aliases i_/p_, FOR UPDATE |
| Conteúdo / Questao.pares_elegiveis_plano → `sp_pares_elegiveis_plano` | assunto_ids JSON, bloquear TINYINT | pares Assunto/Matéria; FOR SHARE opcional, vínculo atual igual ao snapshot publicado |
| Plano / PlanoEstudo.eliminar_planos_proprios → `sp_eliminar_planos_proprios` | usuario_id BIGINT UNSIGNED | uma linha planos_eliminados/itens_eliminados, zero sem ocorrências |

PlanoEstudo/Questao na tabela representam os respectivos Repositories. O dono
vem da sessão autorizada, não do cliente. Flags aceitam somente 0/1; IDs positivos
incluem valores acima de 2^31. JSON_TABLE reproduz IN, sem duplicar pares no set
Python; array vazio mantém vazio/atalho sem consulta. Resultados ausentes mantêm
None/404/409. Conteúdo mantém status/pointer publicado e igualdade
`Assunto.materia_id = QuestaoVersao.materia_id`, sem reclassificar fatos históricos.

O mapeamento textual ORM seleciona todas as colunas e tipos JSON/Boolean/DATETIME(6).
JOIN tem aliases explícitos e ordem Item/Plano. Leituras bloqueantes usam
populate_existing; flush mantém escritas pendentes visíveis. Results fecham em
finally; o helper existente drena resultados da elegibilidade/eliminação e não
fecha a conexão emprestada. Falha de rotina não aciona consulta alternativa.

### Caminhos autorizados e transação

| Entrada / tela | Controller → Service → Repository / métodos |
|---|---|
| GET `/api/aluno/plano`; `aluno/plano.html` | PlanoEstudoController.consultar → ConsultarPlanoService → atual/itens; DTO consulta pares pela API de Conteúdo |
| POST `/api/aluno/plano/gerar` e `/recalcular`; mesma tela | PlanoEstudoController.gerar/recalcular → GerarPlanoService/RecalcularPlanoService → por_chave/atual/contexto/itens; SelecionarPlanoService → diagnóstico + API de Conteúdo → QuestaoRepository.pares_elegiveis_plano |
| POST `/api/aluno/plano/itens/<id>/concluir`; mesma tela | PlanoEstudoController.concluir → ConcluirPlanoItemService → item_proprio; estado/data gravados pela Model, pares pela API de Conteúdo |
| POST `/api/aluno/privacidade/consentimento-plano/recusar` ou `/revogar`; `aluno/privacidade.html` | PrivacidadeController → RecusarConsentimentoPlanoService/RevogarConsentimentoPlanoService → EliminarPlanosPropriosService injetado → PlanoEstudoRepository.eliminar_planos_proprios |

Consulta/geração/recálculo/conclusão mantêm lock de identidade de Contas, depois
dois aceites vigentes e só então replay/plano/item/diagnóstico. O mesmo contexto
e instante externo alimentam o diagnóstico. Taxa exata, desempate, limiar,
três prioridades e justificativas continuam no Service. Models preservam CRUD
individual e guards de snapshot/conclusão/geração histórica. Não há lock de
identidade duplicado, nova rota, tela, funcionalidade ou Controller auxiliar.

O participante de negativa não revalida consentimento nem confirma transação.
A procedure percorre gerações decrescentes FOR UPDATE, remove itens antes de
cada geração e repete o dono no DELETE, com RESTRICT ativo. Somente contagens
internas retornam; o contrato participante externo permanece sem retorno.
Depois do DML, o Repository expira seletivamente derivados carregados afetados
(inclusive item sem Plano carregado, cujo dono é identificado por busca básica
da Model por PK). Preserva decisão pendente e outras contas. Rollback externo
restaura evidência e derivados, inclusive falha real após remover itens; replay
antigo após nova autorização não elimina o plano novo. Respostas e hashes legais
permanecem preservados.

### Instalação e reconhecimento de 015

Pré-condição física exata 014 íntegro, conferida pelo detector existente sob o
lock do runner e após proteções de histórico/checksum/falha, antes de RUNNING/DDL
de 015. Indício parcial ou completo de 015 sem histórico também bloqueia esse
upgrade. Metadados insuficientes, tabela/legada/dependência divergente bloqueiam
sem alterar dados/histórico/objetos nem ocultar o erro por recuo de prefixo.

Bootstrap e migration publicam as mesmas seis definições, sem executar casos
funcionais no baseline/instalação. O prefixo 015 exige 48
referências SQL oficiais, seis derivadas em schema descartável e 42 anteriores
inalteradas. Prefixos antigos e checksums 000–014 permanecem reconhecíveis.
Ensaios cobrem instalação vazia, upgrade com dados, restauração/baseline,
reexecução zero e corpo/assinatura/segurança/ausência incompatíveis.

Instalador exige CREATE ROUTINE e privilégios do runner; invocador exige EXECUTE
e SELECT nas tabelas, além de DELETE nas duas tabelas derivadas para eliminação.
Usar status/up/baseline, backup e reconciliação RUNNING/FAILED conforme operação
acima. Disponibilizar código somente após a 015 validada no destino. Compensação:
retornar primeiro ao código anterior e restaurar backup ou remover somente essas
seis routines por migration revisada; preservar dados, versões, views, histórico
e checksums. Sem rollback DDL automático ou DDL no banco de uso pelos testes.
Contas é coberta pela etapa 016 abaixo. As vinte funcionalidades acadêmicas conservam IDs
e significado; esta cobertura não constitui promessa de aprovação acadêmica.

## Contas e Privacidade — migration 016

A migration acrescenta onze interfaces sobre as mesmas tabelas e 21 Models,
sem nova funcionalidade, permissão, tela, coluna ou política. O conjunto 011–016
tem 55 procedures novas e quatro views; a procedure legada permanece intacta.
Contagem de recursos não substitui a auditoria de seus consumidores.

### Métodos, contratos e caminhos existentes

Todos os IDs de entrada são BIGINT UNSIGNED; instantes usam DATETIME(6) e o
relógio da aplicação. E-mail é VARCHAR(254)/utf8mb4_bin; hashes são CHAR(64)/ascii_bin
e chave de replay é CHAR(36)/ascii_bin. SQL estático, parâmetros vinculados,
SQL SECURITY INVOKER e a mesma conexão/transação do chamador em todas as routines.

| Repository / método → procedure | Parâmetros IN, em ordem | Retorno e consumidor |
|---|---|---|
| Autenticação.buscar_por_email → `sp_usuario_por_email` | email | Usuário completo gerenciado interno; `Usuario.buscar_por_email` delega → LoginService, sem normalização SQL |
| consultar_sessao → `sp_consultar_sessao` | identificador_hash | LEFT JOIN completo Sessão/Usuário, aliases explícitos e relação gerenciada; ConsultarSessaoService/CSRF/hooks HTTP |
| renovar_acesso → `sp_renovar_acesso_sessao` | sessao_id, agora | Uma linha `correspondencias` (0/1); ConsultarSessaoService.renovar e ReautenticarService mantêm booleano |
| revogar → `sp_revogar_sessao` | sessao_id, agora | Uma linha `afetadas`; CriarSessaoService/LogoutService preservam retorno Python `None` e rotação atômica |
| revogar_usuario → `sp_revogar_sessoes_usuario` | usuario_id, agora | Uma linha `afetadas`; operação interna retorna contagem, sem endpoint de gestão novo |
| usuario_ativo_bloqueado → `sp_usuario_ativo_bloqueado` | usuario_id | Usuário ativo completo FOR UPDATE; ValidarSenhaService/CriarSessaoService |
| limite_bloqueado → `sp_preparar_limite_autenticacao` | chave_hash, agora | Upsert idempotente e AuthLimite completo FOR UPDATE; ValidarSenhaService, sem reset no SQL |
| limpar → `sp_limpar_autenticacao` | agora | Uma linha `sessoes`/`limites`; LimparAutenticacaoService → CLI `limpar-autenticacao`, sem rota/tela própria |
| Privacidade.bloquear_usuario → `sp_bloquear_identidade_privacidade` | usuario_id | Somente ID FOR UPDATE, inclusive conta inativa; Services de privacidade e API pública consumida por Plano |
| ultimas → `sp_ultimas_decisoes_privacidade` | usuario_id | Um conjunto com até duas evidências completas, uso → plano; dicionário Python de entidades gerenciadas/None → consulta, revisão e permissão |
| por_chave → `sp_decisao_privacidade_por_chave` | usuario_id, chave | Evidência própria completa FOR UPDATE → replay nos quatro Services de decisão |

[Blueprint Contas](../../backend/app/modules/contas/routes.py) →
[AutenticacaoController](../../backend/app/modules/contas/controllers/autenticacao_controller.py)
→ [Services de autenticação](../../backend/app/modules/contas/services/autenticacao_service.py)
→ [AutenticacaoRepository](../../backend/app/modules/contas/repositories/autenticacao_repository.py).
As entradas `/api/auth/{csrf,cadastro,login,sessao,logout,reautenticar}` permanecem;
[cadastro](../../frontend/cadastro.html), [login](../../frontend/login.html) e
[auth-session.js](../../frontend/js/auth-session.js) usam os mesmos contratos.
Cadastro e escrita individual de conta/sessão/limite permanecem Active Record.

[PrivacidadeController](../../backend/app/modules/contas/controllers/privacidade_controller.py)
→ Services de consultar/aceitar uso/consentir/recusar/revogar →
[PrivacidadeRepository](../../backend/app/modules/contas/repositories/privacidade_repository.py).
`/api/aluno/privacidade` e as decisões da [tela](../../frontend/aluno/privacidade.html)
mantêm revisão/UUID/versões legais no Service. `/api/termos` continua público e
não consulta banco. A composição injeta o participante da 015; não há import
privado de Plano em Contas nem nova transação na eliminação.

### Atualidade, identidade e política preservadas

Leituras completas usam `from_statement`, fechamento em `finally` e
`populate_existing` nos mesmos locks/consultas de sessão. O LEFT JOIN também
recarrega o Usuário e preserva a sessão anônima; validade/ativo continuam no
Service. Senha, hash fictício, HMAC, normalização e mensagens neutras ficam na
aplicação; valores sensíveis não entram em respostas, documentação ou logs.

Últimas decisões fazem duas capturas completas `SELECT ... INTO ... FOR UPDATE`,
primeiro uso, depois plano, por ID desc. A projeção final usa somente variáveis
locais e omite tipos ausentes, sem reler snapshot. Um único conjunto permite
mapear as evidências gerenciadas, com seus guards append-only. Esse ajuste
interno foi caracterizado e autorizado antes da conversão; não altera HTTP.

Renovação mantém `expira_em > agora`, acesso `> agora−30min` e não revogada.
A leitura corrente bloqueante conta correspondências, inclusive timestamp
inalterado; não se usa rowcount do CALL. Atualiza-se somente `ultimo_acesso_em`
na entidade carregada. Revogações expiram somente `revogada_em` dos alvos,
conservando os demais atributos e o instante de revogação anterior em reenvio.
Autoflush precede CALL; rollback externo expira/restaura as entidades. Nenhuma
routine inicia, confirma ou reverte transação. Origens/CSRF/cookies permanecem.

Limite usa upsert e lock sem sobrescrever contador/janela. Cinco falhas,
janela/bloqueio de 15min, Retry-After e chaves independentes login/reautenticação
permanecem no Service. Limpeza: corte=agora−24h; sessões com expiração/revogação
`< corte` ou autenticadas com acesso `< corte−30min`; limites com janela
`< corte−15min` e bloqueio nulo ou `< corte`. Igualdades são preservadas.
Contagens vêm de variáveis de cada DELETE; sessões/limites carregados são
expirados após sucesso. Usuários e evidências não são removidos nem expirados.
Falha no segundo DELETE exige rollback do chamador e restaura o primeiro.

### Instalação e reconhecimento de 016

Pré-condição: 015 físico íntegro, conferido sob o lock do runner antes de
RUNNING/DDL da 016. Recursos parciais/completos de 016 fora do histórico,
dependências/tabelas/legada divergentes e metadados insuficientes bloqueiam;
não há recuo para esconder drift. Bootstrap e sequência definem as mesmas onze
routines sem executar casos funcionais ou alterar dados. Preflight exige 016;
são 59 referências oficiais, preservando as 48 anteriores e SQLs 000–015.

Seis leituras são READS SQL DATA; renovação, duas revogações, preparação do
limite e limpeza são MODIFIES SQL DATA. Instalador exige CREATE ROUTINE e
privilégios do runner; invocador exige EXECUTE/SELECT e UPDATE em sessões,
INSERT/UPDATE em limites e DELETE nas duas tabelas para os comandos respectivos.
Aplicar e verificar antes de disponibilizar código dependente. Operação/backup/
status/up/baseline/reconciliação seguem as seções anteriores. Compensação:
primeiro retornar o código, depois restaurar/compensar somente novas routines
por procedimento revisado, preservando dados, evidências e histórico/checksums.
Sem downgrade automático ou DDL no banco de uso por efeito colateral dos testes.

### Auditoria dos seis módulos

Confrontados todos os executores e seus consumidores com os inventários das
cinco etapas. O levantamento por fonte não encontrou consulta especializada
de produção fora dos contratos abaixo; CRUD básico/relacionamentos e construção
de projeções são classificados separadamente.

| Módulo / fonte | Execução especializada e consumidores conferidos |
|---|---|
| Conteúdo / CatalogoRepository | Seletores ativos/ordenados, listas administrativas, impactos, contagem de não arquivados, equivalência e locks: 011/013; Services de catálogo/admin e delegações das Models |
| Conteúdo / QuestaoRepository | Legada por assunto; dashboard/admin: 011; versões, publicação/locks, elegibilidade individual/lotes/histórico: 013; pares de Plano: 015; Services próprios e APIs públicas para Práticas/Simulados/Plano |
| Práticas / PraticaRepository | Propriedade/replay/histórico/fatos: 014; iniciar/consultar/responder/listar e API de fatos; dashboard usa view da 012 |
| Simulados / SimuladoRepository | Gestão/itens/lotes/títulos/lista/tentativas/replay/andamento/respostas/histórico/fatos: 014; dashboard: 012; Services de gestão/execução e API pública |
| Desempenho / DesempenhoRepository | Agregação/atividades por 012 e contagens por APIs/011/012; Services de diagnóstico/dashboards e seleção do Plano |
| Plano / PlanoEstudoRepository | Atual/replay/itens/item próprio/eliminação: 015; consultar/gerar/recalcular/concluir e participante de negativas; contexto apenas empresta conexão/instante |
| Contas / dois Repositories | Onze correspondências da 016 acima; Usuario.buscar_por_email é delegação, não novo CRUD em Repository |

`PraticaRepository.projecao_desempenho/projecao_atividades`,
`SimuladoRepository.projecao_desempenho/projecao_atividades` e
`QuestaoRepository.projecao_classificacao_historica` constroem Selects, sem
executá-los. As APIs preservam essas projeções de compatibilidade; o único
executor encontrado é a regressão de equivalência em
`test_desempenho_integration.test_projecoes_equivalentes_replay_repeticoes_e_origens`.
Produção usa `sp_desempenho_resumo`/`sp_atividades_recentes` e as quatro views
publicadas. Não há fallback ORM nessas rotas. A projeção de classificação é
consumida somente pela construção da projeção de Simulados.

`bloquear_classificacao` compõe locks da 013 e busca básica de Área por PK;
`administrativo` agrega APIs públicas; adaptadores `consultas_*` delegam aos
Repositories. `buscar_por_id`, listagem básica e escritas individuais herdadas
continuam nas Models. Expiração/refresh por PK e flush não são consultas
especializadas alternativas. Não foi necessário ampliar produto ou remover
APIs para completar a auditoria. F01/F02 e critérios acadêmicos da matriz CRUD
permanecem pendentes de decisões próprias; os vinte IDs conservam significado.

## Gestão administrativa de Alunos — migration 017

Duas routines adicionais e revogação participante da 016 são descritas em
[gestão administrativa de Alunos](gestao-administrativa-alunos.md#interfaces-sql-e-instalação).
Listagem usa snapshot próprio e contrato sem ORM; mutações bloqueiam Usuario
corrente, incluindo inativos, e mantêm CRUD na Model. Nenhuma FK, tabela,
routine anterior ou política de evidências é alterada.
