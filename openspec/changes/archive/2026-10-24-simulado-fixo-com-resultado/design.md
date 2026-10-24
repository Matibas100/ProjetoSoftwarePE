# Design — Simulado fixo

## Context

Ver [proposal.md](proposal.md). Itens 2/3 entregam versões de Questões, contrato de correção e propriedade do Aluno. Simulado é domínio próprio: não criar práticas individuais para cada resposta, evitando duplicidade no desempenho. ADRs 001/002/003/005/006 se aplicam.

## Goals / Non-Goals

**Goals:** composição manual fixa e avaliação reproduzível, com persistência de progresso e conclusão atômica.

**Non-Goals:** geração automática, contador com prazo, TRI ou evento assíncrono. Um simulado publicado não é editado; nova composição neste MVP exige novo simulado lógico, preservando os anteriores.

## Decisions

### 1. Composição e schema

Criar `simulados` (ID, título 3–150 caracteres, estado rascunho/publicado/arquivado, revisão, autoria, datas, versão publicada), `simulado_rascunho_itens` (simulado, posição, `questao_id`, `questao_versao_id`), `simulado_versoes` (ID, simulado, número, revisão de origem, título/autor/data congelados), `simulado_versao_itens` (versão, posição, `questao_id`, `questao_versao_id`) e `simulado_eventos` (simulado, versão opcional, ator, ação, motivo, instante). Todos os vínculos `RESTRICT`; posições e `questao_id` únicos por composição, validando que cada versão pertence à identidade indicada. Limite explícito 1–180 Questões distintas por identidade lógica; versões diferentes da mesma Questão não podem coexistir na composição. Número da versão é único por simulado; revisão de origem identifica replay de publicação. Eventos registram cadastro/edição e revisão/aprovação/publicação/arquivamento com ator, sem credenciais.

Criar `simulado_tentativas` (ID, usuário, `simulado_versao_id`, estado em_andamento/finalizada, revisão, chave UUID de início, datas e totais/percentual anuláveis antes da conclusão) e `simulado_respostas` (tentativa, item de versão, alternativa anulável, correção anulável). Garantir uma resposta por item; todas as linhas são criadas com a tentativa. Usar marcador gerado anulável para `UNIQUE(usuario_id, simulado_versao_id, em_andamento_marcador)`: valor 1 em andamento e NULL após conclusão. Permitir novas tentativas após conclusão; chave de início única por usuário garante replay. Índices de usuário/data e FKs restritivas; posição, item e versão validados juntos.

### 2. Gestão administrativa

`GET/POST /api/admin/simulados`: listagem paginada envelope do catálogo (1/20, máximo 100, filtro status, ordem ID decrescente), criação `{titulo, questao_versao_ids: [ids ordenados]}` 201 com detalhe. `GET/PUT /api/admin/simulados/<id>`: detalhe ou edição de rascunho com `{titulo, questao_versao_ids, revisao}`. Detalhe `{id, titulo, estado, revisao, simulado_versao_id, itens: [{posicao, questao_versao_id}]}`.

`POST .../<id>/publicar` exige `{revisao, confirmar:true, motivo}` (3–500 caracteres), revisão explícita pelo Administrador, reautenticação de 15 minutos e todas as versões de Questão ainda publicadas/elegíveis. Criar versão e composição imutáveis com eventos revisão/aprovação/publicação em transação. Não substituir automaticamente versão superada. Publicação repetida da mesma revisão retorna versão atual sem duplicar.

`POST .../<id>/arquivar` exige o mesmo corpo e reautenticação; preserva tentativas e impede novos inícios. Repetição retorna estado atual. Edição de publicado/arquivado gera 409; sem DELETE ou reativação. Falta de Questões, duplicidade, título inválido ou >180 itens gera 400; indisponibilidade/versão superada/revisão conflitante gera 409; ausente 404.

### 3. Fluxo do Aluno

| Operação | Contrato proposto |
| --- | --- |
| `GET /api/aluno/simulados` | Envelope paginado, ordem ID decrescente; itens `{id, simulado_versao_id, titulo, total_questoes, disponivel, tentativa_em_andamento_id}`; somente publicados; sem gabaritos |
| `POST /api/aluno/tentativas-simulado` | `{simulado_versao_id, chave_envio}` -> 201 com tentativa; mesma chave/dados retorna 200; tentativa já em andamento da mesma versão retorna 200 com ela; chave divergente 409 |
| `GET /api/aluno/tentativas-simulado` | Histórico finalizado paginado, finalização/ID decrescentes; resumo de resultado |
| `GET /api/aluno/tentativas-simulado/<id>` | `{id, estado, revisao, simulado_versao_id, titulo, itens: [{item_id, posicao, questao: <DTO seguro>, alternativa}]}`; finalizada acrescenta resultado |
| `PUT .../<id>/respostas/<item_id>` | `{alternativa: A..E ou null, revisao}` -> 200 com alternativa e nova revisão; sem feedback; só em andamento |
| `POST .../<id>/finalizar` | `{revisao, confirmar:true}` -> 200 com resultado persistido; se já finalizada, retornar o mesmo resultado, sem recontar |
| `GET .../<id>/resultado` e `GET .../<id>/correcao` | Só finalizada (senão 409); resultado `{total, respondidas, acertos, erros, em_branco, percentual_acerto, finalizada_em}`; correção por item com versão, escolhida, gabarito, explicação e classificação congelados |

Novos inícios exigem simulado publicado e todas as versões componentes elegíveis. Se qualquer questão foi arquivada/superada ou catálogo inativado, mostrar indisponibilidade e retornar 409 ao iniciar; não trocar composição. Tentativa iniciada pode continuar/finalizar na composição capturada, inclusive após arquivamento. Administrador recebe 403 nas rotas de Aluno; propriedade por sessão e 404 uniforme para recurso alheio. Mutações usam CSRF/Origin, respostas no-store, campos extras recusados.

### 4. Resultado e transação

Acerto = alternativa igual ao gabarito da versão; erro = respondida diferente; em branco = null. `total = acertos + erros + em_branco`; `percentual_acerto = 100 * acertos / total`, duas casas decimais, sem TRI. Nenhum gabarito/explicação é enviado antes de finalizar, inclusive para respostas já salvas.

Preservar camadas; Services usam `TransactionManager`, Models CRUD participante e Repositories para filtros/elegibilidade/locks. Lock da tentativa mais revisão impede salvar e finalizar com base desatualizada: salvar/finalizar obsoletos em andamento retornam 409. Finalização lê todas as respostas, corrige e persiste totais/data/estado em um commit; falha reverte tudo. Após finalizada, nenhuma resposta/resultado muda.

Service de simulados oferece fatos de itens **respondidos** de tentativas finalizadas ao desempenho com IDs, usuário, finalização, correção e classificação da versão. Não emitir fatos de rascunho/em andamento ou práticas duplicadas. Registro final pode conter branco, mas branco não é fato respondido.

### 5. Telas

Usar `/admin/simulados.html` e `/admin/simulado.html` para ADM-SIM-001/002; `/aluno/simulados.html`, `/aluno/simulado.html?tentativa_id=<id>`, resultado/correção no contexto ALU-SIM-003/004. Apenas composição manual e progresso; cronômetro/geradores futuros ficam indisponíveis. Confirmar finalização informando quantidade em branco. Preservar respostas no servidor e localmente em erro, pedir reenvio explícito após recuperação de sessão, testar teclado/foco e moldura Desktop V1 sem alterar os binários.

## Risks / Trade-offs

- Banco de conteúdo muda após publicação -> verificar elegibilidade no início, preservar composição em tentativas já iniciadas.
- Finalização concorrente -> lock/revisão e replay do resultado final; não corrigir no navegador.
- Não haverá prazo de tentativa -> decisão do MVP; eventual cronômetro precisa de nova change.

## Migration Plan

Após encerramento dos itens 2/3, próxima migration consecutiva (esperada 008) cria tabelas vazias e snapshot equivalente. Sem simulado ou resultado artificial no bootstrap. Testar zero/upgrade/reexecução, constraints geradas e rollback composto com MySQL real, mantendo 29 testes e suítes de autenticação/catálogo/prática. Backup/compensação são a reversão; não apagar histórico concluído. Reler contratos predecessores no preflight e atualizar planejamento antes de divergências.
