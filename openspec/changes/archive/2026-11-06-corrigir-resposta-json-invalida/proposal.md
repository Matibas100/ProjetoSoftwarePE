# Proposta: corrigir resposta JSON inválida

## Why

O cliente `apiRequest` transforma falha de leitura JSON em `{}` e pode indicar sucesso apesar de uma resposta ilegível. Isso esconde o erro original e, após uma gravação, pode induzir repetição indevida de uma ação cujo resultado ainda precisa ser consultado.

## What Changes

- Recusar sucesso HTTP com corpo JSON ilegível usando `ApiError` e mensagem clara, mantendo o status HTTP real e sem apresentar o corpo recebido.
- Preservar HTTP 204, JSON válido de objetos/listas e erros HTTP com mensagem da API; erro HTTP sem JSON continua produzindo erro genérico com seu status original.
- Garantir que leitura inválida não dispara nova mutação nem recuperação de autenticação sem um código válido recebido da API; bootstrap CSRF ilegível deve impedir o envio da mutação dependente.
- Atualizar os testes do cliente e a documentação técnica específica desse comportamento, sem modificar páginas, backend ou tratamento de JSON dentro dos casos de uso.

### Fora de escopo

Validação do schema de todos os payloads, mudança de tratamento de valores JSON primitivos/null, timeouts, retries, nova biblioteca HTTP, endpoints, autenticação, banco, migrations, layout, AWS e extração de helpers. Não fazer commit/push/merge. Não implementar nem alterar a change de legibilidade que está em execução.

## Capabilities

### New Capabilities

- `cliente-api-frontend`: interpretação previsível de respostas da API pelo cliente compartilhado, preservando respostas válidas, erros HTTP e a ausência de repetição automática de gravações.

### Modified Capabilities

Nenhuma. Os requisitos de origem/CSRF/sessão de `autenticacao-escolar` continuam intactos; a interpretação comum de resposta ilegível não possui capability própria hoje. A nova spec é do cliente HTTP, não uma nova funcionalidade acadêmica para a contagem das vinte.

## Impact

- Produto: somente `frontend/js/api.js`. Testes: `frontend/tests/api.test.js`. Documentação: novo `docs/technical/cliente-api-frontend.md`.
- Todos os scripts que já usam `apiRequest` recebem o erro por seu tratamento existente; seus arquivos não mudam. `ApiError.status` conserva 200/201 em sucesso ilegível, permitindo que fluxos com ação incerta mantenham suas chaves/contexto em vez de assumirem falha definitiva.
- Nenhuma mudança em rotas Flask, Controllers, Services, Models/Repositories, SQL, schema, contratos válidos ou dependências. Preservar arquitetura mestre, ADR-002 e fronteiras transacionais.
- Validar casos de leitura/sucesso ilegível, erro HTTP ilegível, 204, token CSRF, concorrência no bootstrap, ausência de reenvio e recuperação explícita; executar cobertura frontend e os dois E2E existentes com API/MySQL reais.
- Ordem operacional: concluir/verificar `melhorar-legibilidade-e-documentacao` antes do apply desta change; depois aplicar `centralizar-helpers-de-paginacao`. O planejamento pode ocorrer agora, mas implementações não devem disputar o mesmo working tree ou evidências de teste.
