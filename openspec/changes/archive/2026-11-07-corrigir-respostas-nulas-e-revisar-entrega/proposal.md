# Proposta — Corrigir respostas nulas e revisar a entrega

## Why

O cliente da API já trata JSON ilegível, mas uma resposta JSON `null` ainda causa `TypeError` ao acessar `csrf_token`, em vez do erro amigável esperado. O README mantém referências a vinte Models/migration 009 e os HTMLs administrativos contêm blocos compactados que dificultam a explicação do código à banca.

## What Changes

- Tratar o corpo JSON raiz `null`, fora de HTTP 204, como resposta inutilizável: erro `ApiError` amigável em sucesso HTTP e erro genérico com status preservado em falha HTTP.
- Preservar objetos/listas, HTTP 204, mensagens atuais, autenticação/CSRF, credenciais e ausência de repetição automática de gravações; cobrir respostas nulas no bootstrap CSRF e depois de uma mutação já enviada.
- Corrigir no README as referências atuais para 21 Models, migrations 000–010 e capacidades de persistência via `ModeloBase`, `ModeloAtualizavel` e `CrudMixin`, em coerência com as fontes existentes.
- Formatar somente os sete HTMLs de `frontend/admin/` com indentação e quebras de linha, preservando conteúdo, aparência, elementos, atributos, scripts e comportamento.

### Fora de escopo

Vídeo/áudio/legendas/roteiro, slides e guia de estudo; AWS, URL da API, infraestrutura e HTTPS; funcionalidades novas; validação geral de todos os tipos JSON ou de cada endpoint; alteração de backend, schema, migrations, documentos legais, CSS ou JavaScript além de `api.js` e seus testes. Sem nova biblioteca/formatter, commit, push, merge ou atualização do CI publicado.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `cliente-api-frontend`: explicitar o tratamento de JSON raiz `null` com o mesmo envelope de erro seguro das respostas inutilizáveis, preservando status HTTP, CSRF e a decisão explícita de nova tentativa. README e formatação HTML não criam requisitos funcionais.

## Impact

- `frontend/js/api.js` e `frontend/tests/api.test.js`; nenhuma mudança na API Flask nem no fluxo Controller → Service → Model/Repository → MySQL.
- `frontend/admin/assuntos.html`, `dashboard.html`, `materias.html`, `questao.html`, `questoes.html`, `simulado.html` e `simulados.html`: edição apenas de formatação.
- `README.md`: correções pontuais, preservando a lista oficial das vinte funcionalidades, evidências históricas e mudanças locais legítimas das changes anteriores.
- Sem dependência de outra change ativa. As duas changes anteriores estão arquivadas, mas suas alterações ainda presentes no working tree deverão ser preservadas; o baseline desta implementação é o conteúdo atual, não simplesmente `HEAD`.
- Verificação futura: testes direcionados do cliente, contratos/DOM administrativos, cobertura frontend nos gates atuais, comparação estrutural/visual dos HTMLs e regressão E2E existente com MySQL descartável. O planejamento não executa aplicação nem modifica essas fontes.
