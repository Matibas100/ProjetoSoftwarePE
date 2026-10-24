# Operação do plano de estudos básico

## Escopo e seleção

Recorte de ALU-PLA-001: lista de até três Assuntos para prática. Sem agenda,
disponibilidade semanal, duração, prazo, notificações, IA ou reagendamento.
Referência visual: Protótipo Desktop V1, página 23; IDs e fluxo conferidos no
Inventário Mestre e no Handoff. Os binários oficiais permanecem congelados.

`SelecionarPlanoService` consome `ConsultarDesempenhoService`, inclusive seu
período padrão de 30 dias civis UTC (hoje e 29 anteriores), limiar de cinco
respostas, denominador e percentual. Não copia a fórmula do diagnóstico.
Práticas corrigidas e itens respondidos de simulados finalizados entram na
mesma base. Itens em branco e tentativas pendentes não entram.

Exigir catálogo ativo e versão publicada atual elegível. O vínculo atual
Assunto–Matéria deve coincidir com o grupo histórico e com a versão publicada;
transferência não reclassifica respostas antigas. A disponibilidade é consultada
novamente em cada leitura do plano.

Comparar frações exatas, sem arredondamento prévio: menor acerto, maior amostra,
menor ID do Assunto. Exemplo: 2/10 precede 1/5 pelo tamanho da amostra, ambos
precedem 4/10. Somente três candidatos; nunca completar vagas com amostra menor
que cinco. Um assunto com 100% pode aparecer como prioridade relativa, sem
afirmar dificuldade. O limiar é operacional e não comprova domínio pedagógico.

Cada item guarda snapshot dos IDs/rótulos, posição, acertos/total/percentual,
período, limiar e justificativa. Novas respostas atualizam o diagnóstico, mas
não alteram o plano. Só recálculo explicitamente confirmado cria nova geração.
Falha de diagnóstico retorna erro, nunca `sem_base_suficiente`.

## Schema e implantação

Migration `009_create_planos_estudo.sql`, após prefixo 008 completo; o snapshot
`create_database.sql` é equivalente à sequência. As duas tabelas iniciam vazias,
sem backfill ou planos fictícios:

| Tabela | Dados e garantias |
| --- | --- |
| `planos_estudo` | Usuário, geração, atual, período JSON, data UTC com microssegundos, UUID, operação e plano anterior. UNIQUE de usuário/geração e usuário/chave. Coluna gerada `usuario_atual` retorna usuário somente quando atual, garantindo no máximo um atual por conta. |
| `plano_estudo_itens` | Plano, classificação, posição 1–3, snapshot JSON, estado e data UTC. Posição e Assunto únicos por plano; conclusão exige data e pendência exige ausência de data. |

Todas as FKs usam `RESTRICT`, incluindo usuário, catálogo, plano e geração
anterior. Os eventos ORM impedem exclusão de histórico e alteração dos snapshots;
somente a desativação do plano e a primeira conclusão são mutáveis. Alterações
SQL administrativas diretas não fazem parte do contrato da aplicação.

Antes da implantação, fazer backup e ensaiar upgrade em cópia. Executar o runner
oficial `python backend/database/migrate.py up`, sem DDL no startup. Conferir
status/checksums, fingerprint 009, tabelas vazias na instalação e regressões.
O runner verifica estrutura inteira, incluindo generated, índices, checks e FKs.

DDL MySQL não possui rollback transacional geral. Reversão usa restauração do
backup ou migration compensatória revisada; suspender novas gravações antes.
Após uso real, preservar planos/itens/conclusões e suas referências. Não apagar
tabelas para retornar código antigo; preferir desabilitar o acesso à funcionalidade
até a compensação. Retenção e purge permanecem fora do escopo.

## Transação e concorrência

`TransactionManager` possui o único commit/rollback. Repository bloqueia o usuário
antes de procurar replay/plano atual. O diagnóstico participa da conexão existente
em `REPEATABLE READ`, com um instante fixado uma vez; não abre transação própria.
A seleção faz leitura final de elegibilidade com locks compartilhados sobre
conteúdo e catálogo. Models persistem com `confirmar=False`.

Calcular candidatos antes de desativar anterior. Desativação, criação do plano e
inclusão de todos os itens confirmam juntas. Falha até na última inclusão reverte
tudo. Recálculos concorrentes com o mesmo ID anterior: um confirma, outro recebe
409. Mesma chave/operação/dados: primeiro 201, replay 200. Chave com outro tipo ou
outro plano anterior: 409. Geração concorrente com chaves distintas: um 201 e um
409. UNIQUEs também protegem as invariantes no MySQL.

## Contratos HTTP

Todas as rotas exigem Aluno. Identidade vem da sessão, sem usuário alvo no cliente.
Anônimo recebe 401, Administrador 403, recurso ausente/alheio o mesmo 404. Toda
resposta é `no-store`; mutações exigem Origin autorizado e CSRF. Corpo estrito,
UUID canônico e inteiros positivos; campos extras/filtros retornam 400.

| Rota | Entrada e resposta |
| --- | --- |
| `GET /api/aluno/plano` | Sem filtros; 200 `{estado:"sem_plano",plano:null}` ou `{estado:"disponivel",plano:{id,geracao,atual,periodo,gerado_em,itens}}`. Nunca gera plano. |
| `POST /api/aluno/plano/gerar` | `{chave_envio}`; 201 com plano, replay 200; plano já existente 409. Sem candidatos: 200 `{estado:"sem_base_suficiente",plano:null}`, sem gravação. |
| `POST /api/aluno/plano/recalcular` | `{chave_envio,plano_atual_id,confirmar:true}`; 201 com nova geração, replay 200; prévia/chave divergente 409. Sem candidatos: 200 `sem_base_suficiente` com plano anterior preservado no payload e banco. |
| `POST /api/aluno/plano/itens/<id>/concluir` | `{confirmar:true}`; 200 com item próprio do plano atual. Replay conserva estado/data. Item histórico retorna 409, inclusive já concluído. |

Item contém `{id,posicao,assunto_id,materia_id,snapshot,estado,concluido_em,
disponivel_para_pratica}`. Snapshot contém classificação histórica, métricas,
período, limiar, posição e justificativa. Replay de chave antiga devolve aquela
geração com `atual:false`; a tela consulta o atual antes de exibi-lo.

Conclusão é decisão manual sobre estudo, não domínio de um Assunto nem submissão
de resposta. Não altera desempenho, práticas ou simulados. Conteúdo retirado
mantém item e explicação, com prática indisponível; a conclusão manual continua
permitida. Somente itens da geração atual podem mudar.

## Interface e sessão

Dashboard liga a `/aluno/plano.html`. A lista oferece gerar, consultar, iniciar
prática, marcar conclusão e recalcular mediante diálogo que explica substituição
e preservação do histórico. Escape/cancelar devolvem foco; mensagens anunciadas
e foco após envio permitem uso por teclado. Datas são reais, em UTC.

`Iniciar prática` abre `/aluno/questoes.html?assunto_id=<id>`, preselecionando o
Assunto no fluxo real existente. Assunto inválido/retirado não amplia a seleção
silenciosamente. O aluno pode escolher outro filtro explicitamente.

Plano, UUID e ação pendente ficam somente em memória. Em falha de rede/sessão,
preservar plano/contexto para a mesma conta; recuperação exige novo clique e não
reenvia mutação. Repetir ação incerta reutiliza a chave/corpo, impedindo escolher
outra mutação até resolver. Erros definitivos 400/404/409 liberam a ação pendente.
O botão Tentar ação pendente continua disponível mesmo se uma consulta já mostrar
a geração/conclusão salva e ocultar o botão original. A repetição usa a mesma
operação/chave/corpo, sem duplicar dados.
Troca de identidade remove plano, chave e diálogo; respostas atrasadas são
descartadas por geração/identidade. Não há cache em storage de dados acadêmicos.

## Validação

Evidências e comandos da entrega ficam em
[validação da change](../../openspec/changes/archive/2026-10-24-plano-basico-por-desempenho/validacao.md).
