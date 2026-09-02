# Instruções para agentes

## Contexto

Este é um projeto existente da Plataforma ENEM. Preserve o MVP validado, as decisões em `docs/technical/` e os artefatos oficiais em `docs/design/desktop-v1/`.

## OpenSpec

Toda evolução funcional, correção, refatoração, alteração de contrato, schema ou arquitetura deve seguir:

```text
explorar -> propor -> aplicar -> verificar -> sincronizar -> arquivar
```

- Use as Skills OpenSpec em `.agents/skills/` como interface do workflow.
- Não implemente antes de existir uma change com artefatos suficientes.
- Não crie diretórios em `openspec/changes/` manualmente; use o CLI.
- Changes usam nomes em `kebab-case` e artefatos em português brasileiro.
- O bootstrap atual é a única exceção: ele instala o próprio workflow.

## Conventions obrigatórias

Leia conforme o escopo:

- [Estrutura do projeto](docs/conventions/estrutura-do-projeto.md)
- [Arquitetura da aplicação](docs/conventions/arquitetura-da-aplicacao.md)
- [Testes](docs/conventions/testes.md)
- [Workflow OpenSpec](docs/conventions/workflow-openspec.md)
- [Documentação e nomenclatura](docs/conventions/documentacao-e-nomenclatura.md)

## Guardrails

- Não exponha `.env`, senhas ou credenciais.
- Não use SQLite ou mocks nos testes de integração existentes.
- Não altere contratos, banco, migrations ou artefatos visuais fora de change aprovada.
- Não faça commit, push ou merge sem autorização explícita.
- Faça mudanças pequenas e preserve alterações legítimas já existentes.
