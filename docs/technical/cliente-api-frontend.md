# Cliente da API no frontend

O adaptador compartilhado [`apiRequest`](../../frontend/js/api.js) interpreta
as respostas HTTP antes de entregá-las às telas. Os
[testes do cliente](../../frontend/tests/api.test.js) exercitam esse contrato.

| Resposta | Resultado |
| --- | --- |
| Sucesso com objeto/lista JSON válido | Retorna os mesmos dados; conserva a atualização de CSRF existente. |
| HTTP 204 | Retorna `null`, sem ler o corpo. |
| Sucesso, exceto 204, com JSON ilegível | Rejeita com `ApiError`, código `resposta_invalida`, detalhes nulos e status HTTP original. |
| Erro HTTP com JSON válido | Conserva mensagem, código, detalhes e status da API, incluindo os eventos de autenticação existentes. |
| Erro HTTP com JSON ilegível | Rejeita com `ApiError`, mensagem genérica, código/detalhes nulos e status original. |
| Falha de conexão (`fetch`) | Mantém o erro de conexão e status 0. |

`resposta_invalida` indica que a leitura do JSON falhou: por exemplo, o corpo
veio vazio, com HTML ou JSON malformado. Um objeto válido `{}` continua válido.
Não há validação adicional do schema dos payloads nem mudança no tratamento
de valores JSON primitivos ou `null`.

A mensagem é fixa: **Resposta inválida do servidor. Confira os dados antes de
tentar novamente.** O erro não expõe corpo recebido, detalhes do parser ou
informações da requisição. Erro HTTP ilegível mantém a mensagem
**Não foi possível concluir a operação.**

## Gravações e sessão

Um POST pode ter sido persistido mesmo que sua resposta esteja ilegível.
O status recebido, inclusive 200/201, permanece em `ApiError.status`;
`resposta_invalida` não comprova reversão da operação. Consulte os dados antes
de decidir repetir uma gravação. O cliente não faz reenvio automático.

Por exemplo: após um POST 201 ilegível, consulte a listagem para verificar se
o item foi criado antes de confirmar outro envio.

Somente códigos de autenticação recebidos em JSON válido mantêm a sinalização
existente de recuperação. Corpo ilegível não provoca evento `auth-required`,
chamada a `recover`, limpeza de identidade/token ou atualização de CSRF.

Se o GET de bootstrap `/auth/csrf` estiver ilegível, todas as mutações que
aguardam sua promise compartilhada recebem erro sem enviar seus POSTs. A
promise é limpa em `finally`, permitindo nova tentativa explícita com token
válido. Cookies e `credentials: include` permanecem conforme a
[operação de autenticação](operacao-autenticacao-escolar.md#api-cookies-e-origem).

Esses cenários de JSON ilegível são provocados nos testes unitários. Os E2E
existentes usam API e MySQL reais e verificam a regressão dos percursos válidos,
sem simular falha de parser. Este contrato transversal não acrescenta uma
funcionalidade à contagem acadêmica.
