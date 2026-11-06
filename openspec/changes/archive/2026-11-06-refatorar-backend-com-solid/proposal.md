# Proposta: refatorar o backend com SOLID

## Why

O checkpoint exige arquitetura com responsabilidades separadas e aplicação dos princípios SOLID. O projeto já possui camadas e vinte funcionalidades, mas os Services dependem de consultas concretas e entidades imutáveis herdam operações CRUD incompatíveis; corrigir essas fronteiras aproxima o código dos exemplos apresentados pelo professor sem alterar o produto.

## What Changes

- Aplicar DIP/OCP por contratos pequenos de consulta (`typing.Protocol`), dependências recebidas pelo construtor e composição explícita na application factory. O recorte compreende nove Services de leitura: duas consultas administrativas do catálogo; busca de Questões por Assunto e listagem elegível do Aluno; catálogo e histórico de Simulados; diagnóstico e os dois dashboards.
- Adaptar apenas os consumidores necessários desses Services, inclusive diagnóstico compartilhado com geração/recálculo do plano, sem refatorar todas as escritas ou autenticação.
- Aplicar LSP/ISP separando persistência básica, atualização e CRUD completo em bases abstratas com um único caminho para `db.Model`. Versões/eventos imutáveis deixam de oferecer atualização/exclusão; Plano e itens mantêm apenas suas alterações permitidas. Models convencionais continuam com CRUD Active Record.
- Preservar SRP: Services validam/coordenam o caso de uso, Repositories executam consultas especiais, Models persistem, Controllers adaptam HTTP e o módulo de composição liga implementações aos contratos.
- Acrescentar testes de substituição de dependências, capacidades de persistência e regressão real de versões, transações, consultas e vinte fluxos de navegador.
- Atualizar diagrama, matriz da entrega, README e documentação técnica com exemplos verificáveis dos cinco princípios e as limitações do recorte. Registrar ADR-008 sobre contratos e capacidades de persistência, compatível com ADRs 002, 003, 005 e 006.

### Fora de escopo

Novas funcionalidades, perfis, rotas, payloads ou estados; alteração de schema, migrations ou Stored Procedure; mover CRUD simples para Repository; interfaces para todas as classes; novo framework/container de DI; mudança visual; vídeo/roteiro; commit, push, merge ou envio da atividade. Não se promete eliminar todo acoplamento do backend nem atender SOLID apenas por nomenclatura.

## Capabilities

### New Capabilities

Nenhuma: refatoração interna e documentação, sem nova capacidade de produto.

### Modified Capabilities

Nenhuma: os requisitos observáveis de `catalogo-academico`, `questoes-versionadas`, `pratica-questoes`, `simulados-fixos`, `desempenho-real`, `plano-estudos-basico`, autenticação e gestão permanecem os mesmos. A metadata usa `skip_specs: true`; não serão criadas deltas artificiais de funcionalidade. Critérios técnicos, substituibilidade e compatibilidade interna ficam no design e nas tarefas.

## Impact

- Código: contratos novos em `backend/app/contracts/`, composição em `backend/app/composition.py`, application factory, nove Services de consulta explicitados no design, consumidores/Controllers correspondentes e Repositories/adaptadores especializados. Services não passam a executar SQL nem a acessar `db.session`.
- Persistência: novas bases abstratas e extração do `CrudMixin`; migração de `QuestaoVersao`, `QuestaoEvento`, `SimuladoVersao`, `SimuladoVersaoItem`, `SimuladoEvento`, `PlanoEstudo` e `PlanoEstudoItem` para as capacidades adequadas. A contagem de vinte Models concretas e seus metadados permanecem.
- Compatibilidade externa: preservar as vinte funcionalidades, dez casos originais, 29 integrações originais, sessão/CSRF, status/erros/payloads, ordenação/paginação, leitura em lote, elegibilidade, imutabilidade e transações. Sem DDL, backfill ou dependência adicional de produção.
- Compatibilidade interna: os nove Services passam de chamadas estáticas para instâncias compostas; todas as chamadas internas/testes afetados serão migrados. A ausência de `atualizar`/`deletar` nas Models imutáveis é intencional; os testes passam a verificar a capacidade correta e a preservação pelos guards ORM. Não manter fachadas estáticas que voltem a selecionar implementações concretas dentro dos Services.
- Documentação: `README.md`, `docs/technical/diagrama-de-classes.md`, `entrega-academica.md`, novo `aplicacao-solid.md`, ADR-008 e relatório de validação desta change. Arquitetura mestre e ADRs históricos serão referenciados; não haverá reescrita de decisões antigas nem cópia integral dos materiais do professor.
- Dependências: partir do estado local resultante de `consolidar-entrega-academica`, já arquivada, incluindo suas melhorias ainda não commitadas. Preservar esse trabalho, a change vazia preexistente, `tmp/` e os binários oficiais. Não limpar o working tree para iniciar a refatoração.
- Entrega do checkpoint: esta change prepara a evidência técnica; commit/push e envio do link permanecem etapas externas, dependentes da autorização/ação do usuário. Resultados históricos não serão apresentados como testes executados nesta change.
