# Design — Preservação dos bytes publicados

## Context

Ver [proposal.md](proposal.md). O hash de documento identifica bytes publicados, não texto normalizado. Os HTML atuais estão em LF e os metadados conferem; o Git local usa `core.autocrlf=true` e não tinha atributo específico para esses arquivos.

## Goals / Non-Goals

Preservar a evidência de integridade em checkouts Windows e Linux. Não mudar texto, hash, versão, API, testes ou configuração global do usuário. Não há migration nesta correção de configuração.

## Decisions

Acrescentar uma regra restrita `frontend/legal/*.html text eol=lf`, mantendo as duas regras existentes. Atributo explícito prevalece sobre autocrlf; não executar renormalização global nem stage no repositório principal. Rejeitar a alternativa de normalizar o texto antes do hash, pois mudaria a identidade já publicada.

Verificar os atributos e simular checkout num repositório temporário sem commit, com autocrlf ativo. A cópia deve produzir os mesmos bytes/hashes. Executar os dois unitários existentes de documentos, sem banco. Guardar somente resultados, sem credenciais, em `validacao.md`.

## Risks / Trade-offs

Padrão amplo pode afetar arquivos alheios → limitar ao diretório legal e à extensão HTML. Alterar arquivo já publicado invalidaria hash → comparar os dois hashes antes/depois sem reescrever documentos. O repositório temporário não tem remote nem commits e deve ser limpo sem atingir o workspace.
