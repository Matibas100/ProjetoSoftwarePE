## Why

A suíte atual protege os dez casos de uso do backend com 29 testes de integração, mas não mede cobertura e deixa sem validação automatizada o health check, partes da configuração, caminhos de erro e todo o JavaScript do frontend. A mudança cria uma base verificável de qualidade antes das próximas evoluções do MVP.

## What Changes

- Preservar os 29 testes de integração existentes e ampliar o backend com testes escritos em `unittest`, separando validações unitárias das integrações que exigem MySQL real.
- Cobrir as onze rotas atuais, os dez casos de uso do MVP, caminhos relevantes de sucesso, validação, conflito, rollback e erro inesperado.
- Adicionar testes do frontend com Vitest e ambiente DOM, cobrindo o cliente HTTP, formulários, listagens, mensagens, estados vazios e falhas de API.
- Incluir todos os módulos Python e JavaScript de produção na coleta de cobertura, com meta mínima por stack de 90% de linhas e 85% de branches, sem permitir módulo executável com cobertura nula.
- Criar comandos reproduzíveis para executar separadamente testes rápidos, integrações MySQL e a validação completa com cobertura.
- Atualizar a documentação de testes com dependências, comandos, resultados esperados e limitações.
- Não alterar contratos HTTP, regras de negócio, schema, migrations nem o comportamento visual do Desktop V1.

### Fora de escopo

- Substituir MySQL por SQLite ou mocks nos testes de integração.
- Implantar pipeline de CI, testes visuais por pixel ou uma suíte completa de navegador ponta a ponta.
- Refatorar amplamente a aplicação apenas para facilitar testes.

## Capabilities

### New Capabilities

Nenhuma. Esta change altera somente testes, ferramentas e documentação interna, sem criar comportamento observável do produto; por isso utiliza `skip_specs: true`.

### Modified Capabilities

Nenhuma.

## Impact

- **Backend:** `backend/tests/`, configuração de cobertura, dependências de desenvolvimento e documentação; execução de integração continua usando MySQL 8 real e dados temporários autocontidos.
- **Frontend:** nova configuração Node de desenvolvimento, Vitest com DOM simulado e testes para `frontend/js/` e o contrato estrutural de `frontend/index.html`.
- **Dependências:** ferramenta de cobertura Python e dependências JavaScript de teste, sem dependências novas em produção.
- **Compatibilidade:** as dez funcionalidades, onze rotas, respostas HTTP, banco atual e os 29 testes existentes permanecem compatíveis.
- **ADRs:** ADR-001 é respeitado porque não haverá migration; ADR-006 orienta os testes de commit e rollback sem mudar a fronteira transacional atual.
