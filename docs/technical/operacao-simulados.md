# Operação de simulados fixos

## Fronteiras de leitura em lote

Listagens obtêm composições por conjunto de IDs da página; a administrativa
separa rascunhos de snapshots publicados. O catálogo do Aluno consulta em lote
a elegibilidade no Service de Questões e as próprias tentativas em andamento,
sem locks de início. Qualquer versão retirada torna a composição indisponível.
Detalhes/correções e fatos históricos usam conteúdo publicado em lote após
autorizar o consumidor; histórico busca os títulos por conjunto. A quantidade
de SELECTs dessas leituras independe da composição e do tamanho da página.
Início, resposta, publicação e finalização mantêm contratos e locks existentes.

## Persistência e implantação

A migration `008_create_simulados.sql` exige o prefixo 007 completo e cria
sete tabelas vazias. Não cria composição, tentativa ou resultado artificial.
O snapshot `create_database.sql` representa a mesma estrutura. Execute primeiro
backup e ensaio em cópia; use somente `python backend/database/migrate.py up`
na implantação autorizada. Startup Flask não executa DDL. A reversão usa backup
ou migration compensatória revisada, preservando tentativas concluídas.

`simulados` guarda rascunho/estado/revisão; `simulado_rascunho_itens` guarda
ordem editável. Publicação cria `simulado_versoes` e `simulado_versao_itens`
imutáveis e eventos de revisão, aprovação e publicação em `simulado_eventos`.
Uma composição contém 1–180 identidades de Questões distintas. Services usam
a fronteira de conteúdo de Questões, com locks de elegibilidade nas escritas;
não substituem versões retiradas ou superadas. Nova composição após publicação
exige outro simulado lógico neste MVP.

`simulado_tentativas` pertence ao Aluno autenticado. UNIQUE por usuário/chave
UUID normalizada protege início idempotente. Marcador gerado 1 em andamento,
NULL após conclusão, limita a uma tentativa em andamento por usuário/versão.
`simulado_respostas` possui uma linha por item, criada no início. Todas as FKs
são RESTRICT. Locks da tentativa e revisão serializam salvar/finalizar;
TransactionManager confirma uma vez ou reverte integralmente. Nenhuma chamada
externa ocorre dentro dessa transação.

O fingerprint 008 compara o DDL MySQL 8 completo por tabela, retirando apenas
o contador AUTO_INCREMENT variável. Alterações de coluna, FK, check, índice ou
expressão gerada bloqueiam baseline. Uma mudança de representação do DDL em
outra versão do servidor exige inspeção antes de adoção, nunca aceite cego.

## Contratos administrativos

Somente Administrador; sessão e no-store em todas as respostas. Mutações exigem
Origin/CSRF. Publicar/arquivar exigem reautenticação nos últimos 15 minutos.

| Método e rota | Corpo ou filtros | Retorno |
| --- | --- | --- |
| GET `/api/admin/simulados` | pagina, por_pagina, status | envelope paginado, ID decrescente |
| POST `/api/admin/simulados` | titulo, questao_versao_ids ordenados | detalhe, 201 |
| GET `/api/admin/simulados/<id>` | — | detalhe |
| PUT `/api/admin/simulados/<id>` | titulo, questao_versao_ids, revisao | detalhe de rascunho |
| POST `.../<id>/publicar` | revisao, confirmar:true, motivo | detalhe com versão publicada |
| POST `.../<id>/arquivar` | revisao, confirmar:true, motivo | detalhe arquivado |

Título: 3–150 caracteres; motivo: 3–500. Paginação padrão 1/20, máximo 100.
Detalhe: `{id,titulo,estado,revisao,simulado_versao_id,itens:[{posicao,questao_versao_id}]}`.
Edição obsoleta/publicada/arquivada: 409. Estrutura inválida/repetições: 400.
Versão inexistente: 404; existente mas inelegível: 409. Publicar novamente a
mesma revisão retorna a versão existente; arquivar novamente preserva estado.
Sem DELETE/reativação. Eventos não contêm credenciais.

## Contratos do Aluno

Administrador recebe 403; anônimo 401. Usuário vem da sessão, nunca do corpo.
IDs alheios/inexistentes retornam o mesmo 404. Campos/filtros extras são 400.

| Método e rota | Entrada | Retorno |
| --- | --- | --- |
| GET `/api/aluno/simulados` | pagina, por_pagina | publicados com disponibilidade e tentativa em andamento |
| POST `/api/aluno/tentativas-simulado` | simulado_versao_id, chave_envio UUID | tentativa 201, replay/retomada 200 |
| GET `/api/aluno/tentativas-simulado` | pagina, por_pagina | histórico finalizado, finalização/ID decrescentes |
| GET `.../<id>` | — | tentativa própria, itens seguros, alternativas salvas, revisão |
| PUT `.../<id>/respostas/<item_id>` | alternativa A–E ou null, revisao | item_id, alternativa, nova revisão |
| POST `.../<id>/finalizar` | revisao, confirmar:true | resultado imutável |
| GET `.../<id>/resultado` | — | resultado, ou 409 se em andamento |
| GET `.../<id>/correcao` | — | detalhe com gabaritos/explicações, ou 409 se em andamento |

Não há prazo nem cronômetro obrigatório. Questão/simulado retirados impedem
novo início; tentativas já iniciadas continuam respondíveis. Respostas salvas
podem mudar ou ser limpas antes de finalizar. Nenhum acerto, gabarito ou
explicação é enviado antecipadamente. Revisão obsoleta gera 409; recarregar e
confirmar novamente, sem replay automático.

Resultado: `{total,respondidas,acertos,erros,em_branco,percentual_acerto,finalizada_em}`.
O denominador inclui **todas as Questões**: três itens, um acerto, um erro e um
branco produzem 33,33%. Replay de finalização devolve o mesmo resultado sem
recontagem. Correção mantém conteúdo e classificação da versão usada, mesmo
após publicação, renomeação, transferência ou arquivamento.

`ConsultarFatosSimuladosService.executar(usuario_id,inicio,fim)` é contrato
interno autorizado, com intervalo UTC semiaberto pela finalização. Fornece
ID da resposta, atividade_id da tentativa, usuário, versão de Questão,
finalizada_em, alternativa, correta e classificação histórica. Exclui brancos
e tentativas em andamento. Não cria práticas; desempenho usa somente respostas
efetivas, com denominador diferente do resultado deste simulado.

## Interface e recuperação

Gestão em `/admin/simulados.html` e `/admin/simulado.html`; catálogo/histórico
em `/aluno/simulados.html`; execução, resultado e correção no contexto de
`/aluno/simulado.html?tentativa_id=<id>`. Destinos de login preservados.
Composição ordenada é revisada antes da confirmação de publicação. Finalização
informa quantos itens estão em branco. Rascunho/alternativa local permanecem
em erro de rede ou sessão; recuperar autenticação exige reenvio explícito.
Troca de conta limpa dados privados; respostas atrasadas são descartadas.
Não guardar respostas, credenciais ou correção em storage.
O [Plano básico de prioridades para prática](operacao-plano-estudos.md) está
disponível; não inclui agenda, duração ou reagendamento. Geradores,
importação oficial, cronômetro, TRI e recomendações avançadas estão indisponíveis.


Consultas compostas: ListarSimuladosAlunoService recebe ConsultaCatalogoSimulados e
ConsultaElegibilidadeVersoes. O adaptador devolve registros e IDs em lote; disponibilidade
continua decidida no Service. ListarHistoricoSimuladosService recebe histórico próprio com
título/resultado já representados em lote. Datas e resultados persistidos mantêm o formato.
As classes ficam em módulos próprios; consultar_simulado_service reexporta os nomes para
compatibilidade de imports, sem fachada estática ou seleção de implementação.
Detalhe/correção, locks de escrita e demais Services permanecem no recorte anterior.
