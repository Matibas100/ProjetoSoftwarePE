# Design — Ajustes finais de robustez e leitura

## Context

Ver [proposta](proposal.md). `apiRequest` em `frontend/js/api.js` centraliza JSON, credenciais, CSRF e recuperação de sessão. A reprodução somente leitura confirmou HTTP 200 com JSON raiz `null` gerando `TypeError`; objetos e listas continuam válidos. A capability existente é `cliente-api-frontend`.

Os sete HTMLs administrativos usam scripts clássicos, seletores/atributos compartilhados e artefatos visuais já aprovados. O working tree contém mudanças legítimas das duas changes arquivadas; uma restauração de `HEAD` apagaria parte desse trabalho.

## Goals / Non-Goals

**Goals:** eliminar a exceção técnica para o caso reproduzido, tornar o código administrativo legível e alinhar as instruções atuais com Model/migrations existentes, em alterações pequenas e verificáveis.

**Non-Goals:** adicionar uma camada genérica de validação de payloads, reescrever o cliente ou instalar formatter. Não há alteração no fluxo Frontend → Route → Controller → Service → Model/Repository → MySQL, nas transações, na Stored Procedure ou nas permissões. Vídeo e implantação ficam fora deste trabalho.

## Decisions

### 1. Verificação específica de `null` antes de ler campos

Manter o retorno antecipado de HTTP 204. Após interpretar JSON e antes de acessar `csrf_token`, detectar estritamente `dados === null` e encaminhar ao mesmo tratamento seguro já usado para leitura inválida. Preferir reaproveitar o bloco existente sem criar classe, módulo ou abstração nova.

Não usar `dados || {}`: ocultaria a resposta incorreta. Não usar somente optional chaining: evitaria a exceção, mas ainda aceitaria `null` como sucesso de uma gravação. Não ampliar o guard para todos os valores falsy ou novos tipos JSON; números, strings e booleanos na raiz não serão redefinidos por esta change. Campos/itens nulos dentro de objetos/listas válidos continuam permitidos.

| Resposta | Resultado esperado |
| --- | --- |
| HTTP 204 | `null`, sem ler o corpo, inclusive exclusão/logout |
| HTTP 200/201 + JSON raiz `null` | `ApiError`, status original, código `resposta_invalida`, detalhes nulos, mensagem atual orientando conferir dados antes de tentar novamente |
| HTTP de erro + JSON raiz `null` | `ApiError`, status original, código/detalhes nulos, mensagem genérica atual; sem inferir expiração de sessão |
| Objeto/lista válidos | Mesmo retorno e comportamento atuais, inclusive campos/itens nulos |
| JSON ilegível ou erro estruturado | Tratamentos existentes preservados |

A correção não altera endpoint, URL, headers, cookie, backend ou contrato de envio. Deve ser possível explicá-la como uma checagem do conteúdo recebido antes de acessar seus campos.

### 2. Efeitos de autenticação e mutações preservados

Uma resposta nula não fornece token nem código de sessão confiável. Não limpar/substituir token válido, disparar `auth-required`, chamar recuperação de sessão, repetir gravação nem alegar rollback de uma ação já enviada.

Bootstrap CSRF nulo deve rejeitar todas as mutações que aguardam a promessa compartilhada, sem enviá-las. O `finally` existente continua liberando essa promessa para uma nova tentativa explícita. Erros estruturados reais de sessão continuam acionando o fluxo atual.

Em `frontend/tests/api.test.js`, acrescentar cenários parametrizados para sucesso 200/201, erro 400/401/403/409/500, objetos/listas com valores nulos internos, POST enviado com token válido e bootstrap concorrente. Verificar status/mensagem/tipo de erro, contagem de chamadas, eventos e conservação do token. Usar o Vitest/jsdom existente; mocks somente nestes testes unitários/DOM.

### 3. Formatação HTML com superfície fechada

Formatar apenas estes arquivos de `frontend/admin/`:

- `assuntos.html`
- `dashboard.html`
- `materias.html`
- `questao.html`
- `questoes.html`
- `simulado.html`
- `simulados.html`

Aplicar indentação consistente de dois espaços e separar blocos/controles para leitura. Não impor quebra arbitrária que altere texto. Preservar elementos e ordem, IDs, classes, atributos `data-*`, ARIA, URLs, estado `hidden`, tipos/names/valores dos campos e ordem dos scripts. Manter o conteúdo de `textarea`, `pre`, `script` e `style` e os espaços significativos entre elementos inline. Não trocar aspas/textos nem remover notas de recursos indisponíveis.

Não alterar CSS, JavaScript administrativo, artefatos em `docs/design/desktop-v1/` ou HTMLs legais. Formatar arquivo por arquivo e conferir o resultado antes do próximo.

Antes da edição, conservar cópia temporária dos sete HTMLs atuais em diretório ignorado de validação. Comparar DOM antes/depois com o jsdom já disponível: estrutura, atributos, controles e conteúdo significativo idênticos; ignorar somente whitespace de indentação sem efeito no conteúdo. Não adicionar snapshots permanentes ou testes que apenas espelhem a formatação. Os testes atuais de contrato/DOM e a conferência visual complementam a comparação.

### 4. README com referências coerentes

Corrigir pontualmente as duas instruções que param em 009 para 010/000–010; alinhar o total atual de Models para 21 e o trecho de herança ao caminho único via `ModeloBase`, `ModeloAtualizavel` e `CrudMixin`, como já descrito no diagrama/ADR-008. A lista de vinte funcionalidades e a contagem de Models têm significados diferentes e não devem ser confundidas.

Conferir contra `backend/database/migrations/`, `backend/app/models/`, diagrama e ADRs, sem executar migrations. Não editar o diagrama ou reescrever os registros históricos para atualizar contagens da época. Preservar as seções recém-atualizadas de CI, migrations e entrega; não atribuir aprovação do CI publicado às alterações locais.

### 5. Validação proporcional e isolamento

Executar primeiro `npm run test:unit -- frontend/tests/api.test.js` após a correção; os testes de novos cenários devem demonstrar a falha anterior e passar com o ajuste. Após cada HTML formatado, comparar DOM e executar os contratos/DOM relacionados já existentes; ao final, `npm run test:coverage` deve manter ao menos 90% de linhas/85% de branches e nenhum arquivo executável sem cobertura.

Conferir as sete páginas em navegador a 1440 e 390 px, com o mesmo conteúdo sintético antes/depois, confirmando leitura, navegação, foco/formulários/modais e ausência de mudança visual causada pela formatação. Usar a infraestrutura local/fixtures existentes; nenhum login real, edição do banco operacional ou mock em integração. Não gravar outro vídeo nesta change.

Executar uma vez o E2E existente com `RUN_MYSQL_E2E=1` no processo, MySQL descartável e configuração por ambiente. Ele complementa a inspeção; não se presume que os três testes cobrem visualmente todas as sete páginas. Registrar comandos, resultados e limitações reais no `validacao.md` desta change, sem credenciais nem sessão exportada. Não executar cobertura backend por mudanças apenas no cliente/HTML/README.

## Risks / Trade-offs

- [Tratar `null` como ausência legítima] → Distinguir HTTP 204 antes da leitura e testar a exceção explicitamente.
- [Nova tentativa duplicar uma gravação] → Preservar a ausência de retry e testar número de envios/token após resposta nula.
- [Quebras de linha mudarem texto/controles/layout] → Preservar conteúdo sensível a whitespace, comparação DOM e conferência visual com baseline atual.
- [Sobrescrever alterações anteriores ainda locais] → Reler fontes, registrar baseline do working tree e aplicar somente hunks desta change, sem reset/checkout amplo.
- [Escopo crescer para implantação ou redesenho] → Whitelist de dez arquivos principais: API, teste, sete HTMLs e README; desvios exigem planejamento próprio.

## Migration Plan

Não há migration, deploy nem alteração de dados. Aplicar primeiro o ajuste da API com seus testes, depois a formatação dos HTMLs e as correções do README. Ao reverter, remover somente os hunks desta change, preservando as mudanças legítimas anteriores. Após a implementação, verificar, sincronizar o delta de `cliente-api-frontend` e arquivar pelo workflow; commit/push e vídeo permanecem para instruções posteriores.
