# Proposta — Fixar quebras de linha dos termos

## Why

Os dois termos publicados têm SHA-256 de seus bytes exatos. Sem regra de EOL, `core.autocrlf=true` pode converter os HTML para CRLF em um checkout Windows, divergindo dos hashes publicados mesmo sem alterar o texto.

## What Changes

- Acrescentar `frontend/legal/*.html text eol=lf` em `.gitattributes`.
- Verificar os atributos efetivos e um checkout descartável com `core.autocrlf=true`, preservando os dois hashes atuais.
- Registrar a validação sem criar novos testes de aplicação nem modificar HTML, metadados ou contratos.

Fora de escopo: textos legais, migrations, código de aplicação, avisos documentais de tamanho no OpenSpec, commit e push. O usuário autorizou a correção concreta após a revisão em 07/11/2026. A aplicação local da migration 010 é uma operação separada, já aprovada na change de termos, com autorização operacional nesta conversa.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. A regra de Git garante os bytes já contratados em `termos-e-consentimento`, sem mudar comportamento de produto. `skip_specs: true` por correção de configuração de checkout.

## Impact

Somente `.gitattributes` e os artefatos desta change. Sem dependências, schema ou alteração de arquitetura. Preservar as regras anteriores de hooks/SQL e todas as mudanças locais legítimas. Os testes de aplicação completos passaram na revisão anterior; esta correção exige apenas atributos, checkout descartável e os dois unitários de documentos já existentes.
