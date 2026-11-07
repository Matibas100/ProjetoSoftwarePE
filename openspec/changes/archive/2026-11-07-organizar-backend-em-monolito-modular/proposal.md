# Proposta — Organizar o backend em monólito modular

## Why

O backend já separa camadas, mas concentra os domínios em pastas globais e registra os endpoints em um único arquivo. O material do professor exige módulos internos com rotas e camadas próprias, preservando a simplicidade de uma aplicação Flask e um banco compartilhado.

## What Changes

- Organizar o código de negócio em seis módulos de `backend/app/modules/`: `contas`, `conteudo`, `praticas`, `simulados`, `desempenho` e `plano_estudos`, cada qual com suas rotas, Controllers, Services e persistência aplicável.
- Agrupar autenticação e privacidade em Contas, e catálogo e Questões em Conteúdo, conforme a coesão das regras e transações atuais. Não criar módulos futuros/vazios para reproduzir nomes de exemplo do material.
- Registrar os Blueprints dos módulos pela factory/agrupador, mantendo todas as URLs, métodos, respostas, permissões, cookies, CSRF e comandos de operação atuais.
- Estabelecer interfaces públicas pequenas entre módulos, aproveitando os contratos existentes. Remover acesso direto a Models/Repositories privados de outro módulo e o ciclo entre negativa de consentimento e eliminação do plano, preservando a única transação e os locks.
- Manter ORM e infraestrutura únicos; deslocar apenas bases/helpers realmente compartilhados para um núcleo neutro. Preservar a identidade dos 21 mapeamentos e a compatibilidade explícita das bases Active Record.
- Adaptar imports e alvos de patch dos testes/scripts para os caminhos canônicos, acrescentar verificações de fronteiras e manter as regressões funcionais existentes.
- Atualizar documentação operacional e de arquitetura, matriz/diagrama e conventions; registrar a decisão no ADR-010, sem alterar decisões históricas ou apresentar o roadmap inteiro como implementado.

### Fora de escopo

Novas funcionalidades, telas ou regras; mudança de contrato HTTP, schema, migrations, bootstrap, hashes legais, limites de autenticação ou políticas de privacidade; módulos futuros de redação/IA/mídias; microserviços, filas, eventos, container de injeção ou dependências novas; redesenho frontend/mobile; uso de dados reais, AWS, vídeo, slides, guia de estudo, commit, push ou merge.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma mudança de comportamento especificado. `skip_specs: true` declara uma refatoração arquitetural: as onze capabilities e os vinte casos continuam obrigatórios. A estrutura e os limites serão verificáveis no design/ADR/testes de arquitetura, sem inventar requisito funcional para movimentação interna de código.

## Impact

- Código de negócio atualmente em `backend/app/{controllers,services,models,repositories,domain}` e rotas/composição/factory; DTOs/Protocols de `app.contracts` permanecem uma fronteira explícita de leitura, sem ORM/SQL.
- Organização final em seis módulos, núcleo comum e compatibilidade mínima para `app.models`/`app.models.crud_mixin`. Não manter cópias paralelas das implementações nas pastas antigas.
- Imports dos testes backend e setup sintético de `scripts/run_e2e.py`; novas verificações de rotas, metadados, composição, dependências e transações entre módulos. Asserções de negócio existentes permanecem.
- Documentação atual em README, `docs/conventions/`, `docs/technical/`, mais apenas o contexto textual de `openspec/config.yaml` se precisar refletir a nova organização; sem alterar schema/rules/operations do workflow.
- Nomes internos de endpoints Flask poderão receber o namespace do módulo; URLs HTTP não mudam. O inventário anterior/posterior deverá distinguir essas duas identidades e verificar eventuais consumidores internos.
- Sem alteração de dados/deploy ou dependência de outra change ativa. A aplicação será migrada por etapas testadas; antes do apply, registrar baseline dos arquivos, rotas, Models, SQLs e regressão. Esta proposta cria somente planejamento.
