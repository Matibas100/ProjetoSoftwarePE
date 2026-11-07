# Design: rejeitar resposta ilegível sem repetir gravações

## Context

Ver [proposal.md](proposal.md) e [spec do cliente](specs/cliente-api-frontend/spec.md). O cliente clássico compartilhado já separa falha de `fetch`, HTTP 204, erros de autenticação e leitura de JSON. O problema está no fallback da leitura: `resposta.json().catch(() => ({}))` também devolve `{}` em sucesso HTTP.

`frontend/tests/api.test.js` caracteriza explicitamente esse comportamento, portanto precisa ser atualizado por uma mudança de requisito. Fluxos como Plano e início de Prática/Simulado mantêm ações pendentes e chaves em memória para respostas incertas. Conservar o status HTTP real evita transformá-las em erro definitivo 400/404/409 que descartaria o contexto.

## Goals / Non-Goals

**Goals:** erro legível e estável para sucesso com JSON ilegível; preservar status, 204, JSON válido, erros da API e ausência de reenvio; limitar a implementação ao adaptador compartilhado.

**Non-Goals:** validar schemas ou valores JSON primitivos/null, alterar HEAD, timeout/retry, cookies/CSRF, rotas, scripts consumidores ou tratamento de domínio. Não classificar resposta ilegível como falha comprovada da transação no servidor.

## Decisions

### 1. Separar leitura do corpo de classificação HTTP

Manter `fetch` e seu erro de conexão com status 0 intactos. Manter retorno antecipado nulo para status 204, sem chamar `.json()`. Para os demais casos, usar `try/catch` delimitado somente à leitura do JSON, antes de processar campos de token/código. Não capturar no mesmo bloco erros de renderização ou dos consumidores.

| Resposta | Resultado do cliente |
| --- | --- |
| 2xx com objeto/lista JSON válidos | Caminho atual, mesmos dados e atualização de CSRF quando já aplicável |
| 204 | `null`, sem leitura do corpo |
| 2xx, exceto 204, com leitura JSON rejeitada | `ApiError`, status HTTP recebido, `details:null`, `code:"resposta_invalida"` |
| Erro HTTP com JSON válido | Mesmo tratamento atual: mensagem/detalhes/código/status da API, incluindo eventos existentes |
| Erro HTTP com leitura JSON rejeitada | `ApiError` com status recebido, mensagem genérica atual, código/detalhes nulos |
| `fetch` rejeitado | Erro de conexão atual, status 0 |

Mensagem fixa para sucesso ilegível: **`Resposta inválida do servidor. Confira os dados antes de tentar novamente.`** Não incluir HTML, texto do parser, URL com informações de conexão, token ou conteúdo da requisição. Mensagem de erro HTTP ilegível: **`Não foi possível concluir a operação.`**, já usada pelo fallback atual.

Usar uma pequena ramificação de erro na leitura, sem dependência ou classe adicional. Não transformar a melhoria em um validador universal de JSON: campos ausentes em JSON sintaticamente válido e tratamento de primitivos/null não mudam nesta change. Resposta JSON vazia válida `{}` continua sendo um objeto válido; corpo HTTP vazio que falha no parser recebe o novo erro.

### 2. Não inferir efeitos ou autenticação a partir do corpo ilegível

Só códigos recebidos em JSON válido podem acionar o mecanismo atual de `auth-required`. `resposta_invalida` não limpa identidade/token por conta própria, não emite evento de sessão e não aciona `recover`. Não repetir `fetch`, cancelar transação presumida, criar chave nova ou fazer refresh automático após POST.

Se o bootstrap GET `/auth/csrf` estiver ilegível, sua promise rejeita; as mutações dependentes não chegam a `fetch`. Preservar o compartilhamento da promise entre envios concorrentes e sua limpeza no `finally`, permitindo nova tentativa explícita. Não enviar header CSRF inventado nem manter uma promise rejeitada para sempre.

Após POST 200/201 ilegível, a persistência pode ter ocorrido: o cliente informa incerteza, preserva o status e devolve o controle. As telas continuam usando seus catches e políticas de consulta/ação pendente. Esta change não acrescenta reenvio nem altera os arquivos dessas telas.

### 3. Três arquivos e testes proporcionais

Alterações permitidas: `frontend/js/api.js`, `frontend/tests/api.test.js` e novo `docs/technical/cliente-api-frontend.md`, além dos artefatos/registro desta change. Nenhum README/CSS/HTML da limpeza em andamento é alterado.

No teste de API, substituir a caracterização antiga de sucesso `{}` por asserções dos comportamentos definidos; conservar os demais casos. Exercitar leitura rejeitada para HTTP 200 e 201, 204 sem acesso ao parser, erro 401/500 sem JSON, erro estruturado válido, objetos/listas válidos, fetch rejeitado e controles atuais de autenticação.

Casos adicionais importantes:

- Mutações com token previamente obtido e resposta inválida: exatamente um POST original, erro de status real/código novo, nenhum `auth-required`/`recover`, nenhum corpo/parser refletido na mensagem.
- Dois envios aguardando bootstrap ilegível: somente um GET de bootstrap compartilhado, nenhum POST, ambas as promises rejeitadas. Em nova ação explícita com resposta válida, obter token e enviar uma única vez.
- Após leitura inválida, uma consulta explícita válida continua funcionando. Não testar repetição automática inexistente nem alterar chaves dos fluxos de domínio.

Mocks ficam apenas nesses unitários/DOM. A suíte E2E real permanece sem interceptações: ela confirma que cadastro/login, 204, tokens, vinte casos e Plano/Simulado seguem funcionando com API/MySQL reais, não simula uma resposta malformada do backend. Não alegar que o E2E testou uma falha de proxy ou de parser que só os unitários provocaram.

Executar primeiro `npm run test:unit -- frontend/tests/api.test.js`, depois `npm run test:coverage` uma vez, mantendo gates e testes de sessão/páginas. Executar os dois E2E pelo runner oficial com `RUN_MYSQL_E2E=1` e configuração por ambiente apenas no processo, confirmando limpeza. Sem alteração backend, não repetir cobertura backend apenas por essa mudança de cliente.

O novo documento técnico deve explicar a tabela de respostas, significado de `resposta_invalida`, status real e consulta antes de repetir gravação, ligando para `api.js`/testes e para a operação de autenticação. Sem listar como funcionalidade acadêmica extra ou prometer que uma operação foi revertida.

### 4. Sequência e preservação

Aplicar somente depois de encerrada/verificada a limpeza existente, com baseline fresco capturado no início do apply em `test-results/json-invalido/`, ignorado. Não executar implementações simultâneas no mesmo diretório. Preservar todos os arquivos preexistentes e changes, incluindo o trabalho de migrations, `tmp/`, visuais oficiais e specs principais até o sync específico desta change.

Confirmar no fechamento inventário, testes, links, `git diff --check`, verificação OpenSpec e validação estrita; guardar resultados reais em `validacao.md`. Não abrir/expor `.env`, usar banco operacional, exportar sessão ou publicar logs/corpos sensíveis.

## Risks / Trade-offs

- **Status 2xx em erro parece incomum:** ele informa a resposta recebida e preserva a política atual de operação incerta; o identificador de erro é `resposta_invalida`, sem falsificar status 500 ou 0.
- **Regressão em logout/exclusão:** 204 permanece antes do parser e possui teste com leitura proibida.
- **Confusão entre erro de sessão e corpo ilegível:** não inferir código, token ou evento; JSON de erro válido conserva o fluxo anterior.
- **Tentativa duplicada de gravação:** proibir retry automático e testar contagem de requests, inclusive bootstrap concorrente; mensagem orienta consulta prévia.
- **Conflito com a limpeza ativa:** novos artefatos podem ser preparados agora; apply sequencial e escopo de três arquivos sem sobreposição com ela.

## Migration Plan

Nenhuma migration/alteração de backend ou deploy. Aplicar após a limpeza, validar o cliente e registrar evidências; depois sincronizar a nova capability `cliente-api-frontend` e arquivar. Rollback somente dos três arquivos desta change a partir do baseline, preservando deltas anteriores. Commit/push/merge e AWS não são automáticos. A extração de helpers vem depois, com sua própria validação.
