# Tarefas: centralizar helpers de paginação

## 1. Preflight sequencial

- [x] 1.1 Confirmar conclusão/verificação de legibilidade e JSON, sem outro apply concorrente; ler proposta/design, AGENTS.md, conventions e contratos atuais. Inventariar consumidores/patches dos dois helpers privados, registrar corpos AST e baseline não sensível em `test-results/paginacao/`, com contexto em `validacao.md`. Conferir escopo de onze arquivos e preservar deltas anteriores, migrations, frontend, specs, demais changes, `tmp/` e visuais oficiais; não abrir/expor `.env` ou escrever no banco operacional.

## 2. Funções neutras com comportamento preservado

- [x] 2.1 Criar `backend/app/services/paginacao.py` com `inteiro_filtro` e `envelope_paginado`, extraídos dos corpos atuais sem endurecer validações ou mudar defaults/mensagens/cálculo. Criar `backend/tests/unit/test_paginacao.py` para ausência/vazio, conversões, limites/erros, total zero/exato/parcial, página sem itens e preservação da lista; executar o unitário e comparar AST dos corpos normalizando apenas os nomes das funções, sem dependências de Flask/banco ou classe genérica.

## 3. Consumidores e documentação

- [x] 3.1 Migrar catálogo e os sete módulos consumidores listados no design para imports/chamadas diretos do módulo neutro; remover definições antigas/import de ceil sem uso, sem wrappers ou cópias. Verificar busca sem imports de `_envelope`/`_inteiro_filtro` entre esses casos de uso, executar unitários existentes de catálogo/Questões/Práticas/Simulados/composição e conferir defaults, campos, filtros estritos/repetidos e mensagens preservados. Nenhuma validação específica, contrato de Service, SQL ou fluxo transacional deve mudar.
- [x] 3.2 Acrescentar explicação curta em `docs/conventions/arquitetura-da-aplicacao.md` sobre os helpers de paginação e a responsabilidade dos Services. Conferir link/caminho, ausência de classe/framework novo e consistência com CRUD nas Models e consultas especiais nos Repositories; manter README e documentos das outras changes intactos.

## 4. Verificação integrada

- [x] 4.1 Executar cobertura backend com unitários e integrações/migrations no MySQL real pelos runners oficiais, opt-ins apenas no processo e gates 90%/85% intactos. Conferir regressão de filtros/paginações, HTTP/propriedade e persistência, incluindo o arquivo novo sem cobertura zerada; registrar resultados atuais sem mocks/SQLite em integração ou alteração de testes antigos para acomodar regressão.
- [x] 4.2 Executar os dois E2E pelo runner oficial com API/MySQL reais e schema descartável, sem mudar frontend/testes/runner; confirmar os vinte casos e Plano/Simulado, limpeza do schema/processos e preservação do restante. Registrar comandos/resultados reais e limitações em `validacao.md`; não repetir cobertura DOM exclusivamente por esse delta sem frontend alterado.
- [x] 4.3 Aplicar `openspec-verify-change`, executar `openspec validate centralizar-helpers-de-paginacao --strict` e conferir AST/imports, links, whitespace e hashes. Consolidar os onze arquivos mais artefatos, preservação das diferenças de validação por recurso e ausência de mudanças nas outras changes. Resolver achados críticos antes de fechar; necessidade de alterar comportamento exige revisão de escopo.

## Workflow follow-up

- Sync não aplicável: `skip_specs: true`, nenhuma mudança funcional.
- Arquivar pela skill apropriada somente após tarefas concluídas e verificação sem achados críticos.
- Commit/push/merge, AWS, apresentação, vídeo e guia de estudo ficam fora desta change.
