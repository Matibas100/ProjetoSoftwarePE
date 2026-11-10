# Proposta: atualizar referências da documentação acadêmica

## Why

Os fluxogramas mantêm 24 links para caminhos anteriores à modularização, e a documentação de entrega descreve contagens antigas de Blueprints e testes. Corrigir essas referências facilita conferir e explicar o código já validado, sem introduzir trabalho funcional antes da apresentação.

## What Changes

- Corrigir links e referências de símbolos nas tabelas de rastreabilidade de `docs/technical/fluxogramas-casos-de-uso.md`, apontando para os módulos e fontes canônicas atuais.
- Ajustar referências próximas que ficaram incorretas após as mudanças de persistência: validação compartilhada, Models de Simulado preservadas no arquivo atual, registros de rotas e consulta de desempenho por procedure, distinguindo as projeções ORM mantidas somente para regressão.
- Atualizar o retrato atual em `docs/technical/entrega-academica.md`: sete Blueprints e seis testes E2E em seis arquivos, preservando os vinte casos numerados e seus significados.
- Acrescentar a referência de validação já publicada do commit `bb9823de87f3be6ae4d0a0cb3484ff2725353d7e`, separando-a dos resultados históricos e da futura validação desta correção documental.
- Conferir links, símbolos e contagens por leitura do código e registrar a checagem em `validacao.md` da change.

### Fora do escopo

Alterar código, testes, configuração, arquitetura, contratos, schema, SQL, imagens ou artefatos oficiais; acrescentar CRUD/exclusões; revisar a política de arquivamento; declarar aceite do professor, hospedagem ou entrega de vídeo. Não editar relatórios arquivados nem remover ressalvas acadêmicas existentes. Não acrescentar ferramenta ou gate de CI.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. `skip_specs: true` é aplicável porque apenas referências documentais são atualizadas; as dezenove specs mantêm seus requisitos.

## Impact

- **Arquivos de aplicação:** nenhum. O baseline de referência é `bb9823de87f3be6ae4d0a0cb3484ff2725353d7e`.
- **Documentação:** somente os dois documentos indicados e os artefatos desta change; sem reescrever o conjunto de documentação técnica.
- **Fluxos descritos:** diagnóstico de desempenho e finalização de Simulado, com os mesmos Services, autorização, transações, resultados e rotas existentes.
- **Arquitetura:** preservar Frontend → Route → Controller → Service → Model/Repository → MySQL e os ADRs 006, 008, 010 e 011. Tutor permanece o sétimo módulo, sem Model própria.
- **Validação:** checagem documental e OpenSpec; não repetir testes da aplicação nem abrir o banco ou chamar Gemini para corrigir links. Não ler credenciais, limpar temporários ou realizar commit/push automaticamente.
