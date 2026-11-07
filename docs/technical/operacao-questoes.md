# Operação de Questões versionadas

Código canônico: [`backend/app/modules/conteudo/`](../../backend/app/modules/conteudo/);
interfaces e transações no [mapa modular](organizacao-modular.md).

## Fronteiras de leitura em lote

`ListarQuestoesAlunoService` serializa diretamente as versões da consulta
elegível paginada, sem consultar novamente cada item e sem gabarito/explicação.
`ConsultarVersoesElegiveisService` fornece um mapa somente das versões ainda
disponíveis; `ConsultarVersoesHistoricasService` exige que todas as versões
pedidas sejam snapshots publicados, preservando versões superadas/retiradas.
O consumidor interno autoriza propriedade e conclusão antes de pedir correção.
Repositories executam as consultas por conjunto. Os contratos unitários e os
locks das operações de escrita permanecem preservados.

## Persistência e upgrade

Aplica-se a [gestao-basica-questoes](../../openspec/changes/archive/2026-10-07-gestao-basica-questoes/design.md), com ADRs 001–006. `questoes` preserva seus IDs e campos legados como rascunho administrativo; `questao_versoes` e `questao_eventos` são append-only. Nova Questão tem status `rascunho`, revisão 1 e nenhuma versão publicada. Publicar cria snapshot e três eventos (revisão, aprovação, publicação) na mesma transação do ponteiro. Editar incrementa revisão sem substituir o snapshot publicado; arquivar conserva o ponteiro e o histórico. Não há DELETE, reativação ou publicação automática.

A migration `006` exige schema completo até `005`, catálogo referenciado íntegro e usuários/sessões existentes. Antes de upgrade operacional, faça backup e confira o histórico com `python backend/database/migrate.py status`; confira dados e referências em cópia descartável. Execute `python backend/database/migrate.py up` apenas no banco autorizado, fora do startup Flask. Não copie credenciais ou configuração para relatórios. O runner registra execução/checksum e bloqueia falha parcial de DDL até reconciliação explícita; não reexecute o arquivo SQL isoladamente.

Backfill preserva conteúdo/IDs e cria versão inicial de origem `legado`, estado `rascunho`, autor nulo e evento de cadastro com motivo de migration. Data do snapshot/evento é o instante UTC do backfill, não data original inventada; `questoes.criado_em` permanece nulo para legado. Não preenche o ponteiro nem libera conteúdo para Aluno. Pós-upgrade: versão 006 aplicada, mesmos IDs/conteúdo, backfill completo, todas as FKs restritivas e procedure inalterada. Reexecução do runner não acrescenta snapshots/eventos. Instalação limpa e `create_database.sql` devem produzir estrutura equivalente.

Não há downgrade automático: reversão usa backup ou migration compensatória revisada, preservando versões já utilizadas. Disponibilize as telas/APIs novas somente após upgrade; durante esta implementação migrations são ensaiadas em schemas temporários de teste, sem upgrade do banco operacional.

## Contratos administrativos

Todas as rotas abaixo exigem Administrador. Mutações exigem cookie de sessão, origem autorizada e CSRF; publicar/arquivar exigem reautenticação nos últimos 15 minutos. GET/HEAD não exigem CSRF. Respostas autenticadas usam `Cache-Control: no-store`.

| Operação | Contrato |
| --- | --- |
| `POST /api/questoes` | Conteúdo legado completo; 201 com os mesmos campos legados. Cria rascunho/evento com operador da sessão. |
| `GET /api/questoes/por-assunto?assunto_id=...` | Procedure legada, campos/ordem originais; mantém consulta administrativa inclusive sobre arquivadas. |
| `GET /api/admin/questoes` | Envelope `itens/pagina/por_pagina/total_itens/total_paginas`; 1/20, máximo 100; ordem ID decrescente. Filtros combináveis: `busca` até 100 caracteres, IDs positivos de Área/Matéria/Assunto, `dificuldade` facil/media/dificil e `status` rascunho/publicada/arquivada; sem status inclui todos. Classificação é catálogo atual. |
| `GET /api/questoes/<id>` | `{questao: <campos legados>, status, revisao, versao_publicada_id, versoes:[{id,numero,estado}]}`. |
| `PUT /api/questoes/<id>` | Conteúdo parcial mais `revisao` inteira positiva; rejeita campos desconhecidos e alteração vazia. 200 com detalhe; não publica. |
| `POST /api/questoes/<id>/publicar` | `{revisao, confirmar:true, motivo}`; motivo após trim tem 3–500 caracteres. 200 com detalhe; replay da revisão publicada não cria versão/eventos. |
| `POST /api/questoes/<id>/arquivar` | Mesmo corpo/controles de publicação; 200 com detalhe. Replay de arquivamento autorizado conserva estado sem outro evento. |

Exemplo: cadastrar retorna ID 42; editar com revisão 1 retorna revisão 2; publicar `{revisao:2, confirmar:true, motivo:"Conteúdo revisado"}` cria versão imutável. Editar novamente modifica somente rascunho/revisão; consumidores históricos continuam lendo a versão anterior.

Erros: 400 entrada inválida, 404 ausente, 409 revisão/estado conflitante, 401 sessão inválida e 403 perfil/CSRF/origem/reautenticação insuficientes. Falhas internas não retornam sucesso parcial. Lock da Questão serializa edição/numeração/publicação; catálogo relevante é bloqueado e verificado dentro da publicação. Models participam com `confirmar=False`; `TransactionManager` possui commit/rollback. Services/Controllers não executam SQL nem acessam `db.session`.

## Fronteira para práticas e simulados

`ConsultarVersaoElegivelService` resolve versão publicada atual de identidade não arquivada, com Assunto/Matéria referenciados ativos; retorna DTO sem gabarito/explicação. Versão inexistente retorna 404; retirada/superada retorna 409, sem troca silenciosa. `ConsultarVersaoHistoricaService` preserva versão publicada por ID mesmo após retirada/nova publicação; seu consumidor interno verifica propriedade e fase da tentativa antes de pedir correção. DTO com `correcao=True` inclui gabarito/explicação e nunca é exposto antes da conclusão. Não há endpoint público de versões/correções nesta entrega.

## Interface e validação

`/admin/questoes.html` oferece filtros, paginação e entrada de cadastro; `/admin/questao.html?id=<id>` permite detalhe/edição/revisão/publicação/arquivamento. Formulário e filtros permanecem em falhas; recuperação/reautenticação é contextual e exige novo envio explícito. Troca de identidade bloqueia contexto até descarte/recarga. Alterações não salvas exigem confirmação para navegar/sair; mensagens e confirmações são acessíveis por teclado. Importação, IA, upload e fila multiperfil ficam indisponíveis. Binários oficiais Desktop V1 permanecem congelados.

Integrações criam/limpam schemas temporários MySQL reais. Opt-in somente no processo: `RUN_MYSQL_INTEGRATION=1` e, para migrations, `RUN_MYSQL_MIGRATION_INTEGRATION=1`; nunca persista no `.env`. Execute os runners e gates das [conventions de testes](../conventions/testes.md). Resultados reais ficam no relatório de validação da change.


Consultas SOLID: BuscarQuestoesPorAssuntoService recebe a consulta e Callable de existência
ligado a Assunto.buscar_por_id pela composição; CALL permanece exclusivamente no Repository.
ListarQuestoesAlunoService recebe ConsultaQuestoesElegiveis; o adaptador representa conteúdo
seguro em lote antes de devolver registros ao Service. Sem gabarito/explicação ou ORM na fronteira.
