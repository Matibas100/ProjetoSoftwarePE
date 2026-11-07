# Operação de práticas e histórico

Código canônico: [`backend/app/modules/praticas/`](../../backend/app/modules/praticas/);
interfaces e transações no [mapa modular](organizacao-modular.md).

## Persistência e implantação

A migration 007 acrescenta somente `pratica_tentativas`, após a 006. Não gera
histórico fictício nem altera Questões, versões ou correções anteriores. O
bootstrap consolidado contém a mesma estrutura. IDs de usuário e versão e a
classificação histórica têm FKs `RESTRICT`. A chave UUID normalizada é única
por usuário; novas chaves permitem repetições reais da mesma Questão.

`em_andamento` exige resposta, correção e data nulas; `respondida` exige
alternativa A–E, correção booleana e data não anterior ao início. O banco
verifica esses invariantes e diferencia maiúsculas em alternativas/chaves.
Índice `(usuario_id, respondida_em, id)` atende histórico e leitura de fatos.

Antes da implantação: backup testado e inspeção de `python backend/database/migrate.py status`.
Execute `python backend/database/migrate.py up` somente no banco autorizado,
fora do startup. Confirme versão 007, integridade das FKs e preservação dos
registros existentes. Disponibilize API/telas apenas após o upgrade.
Os testes usam schemas descartáveis; não atualizam o banco operacional.
Não há downgrade destrutivo: restaure backup ou prepare migration compensatória
revisada preservando tentativas. DDL parcial exige inspeção/reconciliação pelo
runner; não reexecute SQL manualmente.

## Contratos HTTP

Todas as rotas exigem sessão de Aluno. Administrador recebe 403; anônimo 401.
GET/HEAD usam `no-store`; mutações exigem origem autorizada e CSRF. Dono vem
da sessão; IDs alheios e inexistentes retornam o mesmo 404.

| Operação | Entrada e saída |
| --- | --- |
| `GET /api/aluno/questoes` | `materia_id`, `assunto_id` positivos opcionais; `pagina=1`, `por_pagina=20` até 100. Ordem Questão crescente. Envelope `itens/pagina/por_pagina/total_itens/total_paginas`. DTO do Service de conteúdo sem gabarito/explicação. |
| `POST /api/aluno/praticas` | Somente `{questao_versao_id, chave_envio}` UUID. 201 `{id,estado,questao}`; replay da mesma chave/versão 200 com mesma tentativa, inclusive após retirada. Chave com outra versão 409. Versão ausente 404, retirada/superada 409. |
| `GET /api/aluno/praticas` | Somente respondidas próprias, filtro `assunto_id`, mesmo envelope/paginação. Ordem resposta/ID decrescente. Cada item tem ID, versão, resposta, correção, data UTC e classificação histórica. |
| `GET /api/aluno/praticas/<id>` | Questão segura enquanto em andamento. Após responder inclui `resposta_escolhida`, `correta`, `gabarito`, `explicacao` anulável, `respondida_em`, Matéria/Assunto históricos. |
| `POST /api/aluno/praticas/<id>/resposta` | Somente `{alternativa:"A"}` com A–E. 200 com detalhe persistido. Replay igual retorna o mesmo resultado; alternativa diferente 409. |

Entradas extras, filtros repetidos, paginação inválida e campos de correção ou
usuário fornecidos pelo cliente retornam 400. Falha interna retorna 500 sem
sucesso parcial. A UNIQUE resolve disputa de início; lock de tentativa
serializa correções. Models usam `confirmar=False` e `TransactionManager`
possui commit/rollback; Services e Controllers não executam SQL.

Exemplo: iniciar versão publicada com UUID novo retorna tentativa 42; enviar
`{"alternativa":"B"}` salva uma resposta incorreta se o gabarito da versão é A.
Repetir B retorna a mesma data/correção; enviar A depois retorna 409. Nova
tentativa com outra chave é independente. Nenhuma correção é calculada no navegador.

## Conteúdo histórico e fronteira de leitura

Início verifica elegibilidade pelo Service de conteúdo do item 2 e captura
Matéria/Assunto da versão. Uma tentativa iniciada pode terminar após retirada,
transferência ou nova publicação. Conteúdo e gabarito vêm da versão original;
nomes e IDs de classificação vêm do snapshot, sem reatribuição retroativa.

`ConsultarFatosPraticasService.executar(usuario_id, inicio, fim)` é contrato
interno de leitura para consumidor autorizado: intervalo UTC `[inicio,fim)`,
somente respondidas, ordem data/ID, campos `{id,usuario_id,questao_versao_id,
respondida_em,alternativa,correta,classificacao}`. Não há autorização de escrita
externa nem cópia de respostas de simulados. Replays não acrescentam fatos;
novas tentativas reais acrescentam. Retenção geral/OD-08 permanece aberta.

## Interface, sessão e privacidade

`/aluno/questoes.html` seleciona/inicia; `/aluno/questao.html?tentativa_id=42`
executa e mostra a correção persistida; `/aluno/historico.html` consulta o
histórico. O início mantém o destino de login e oferece os dois links.
Uma Questão por tentativa, sem sequência adaptativa, cronômetro, resumos,
tutor, recomendações ou dashboard. Referências ALU-QUE-001/002/003 preservadas
no recorte aprovado; arquivos oficiais permanecem congelados.

Seleção e chave pendente ficam apenas em memória, nunca em localStorage.
Falha de rede/sessão preserva alternativa e exige novo envio explícito.
Recuperação usa AuthUI; mudança de identidade limpa conteúdo e bloqueia o
contexto até recarga. Consultas verificam identidade antes e depois da resposta
e descartam respostas atrasadas. Gabarito só é renderizado após correção salva.
Labels nativos, foco visível, mensagens anunciadas e resultado textual permitem
uso por teclado sem depender de cor.
