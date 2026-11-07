# Tarefas

## 1. Correção e verificação

- [x] 1.1 Acrescentar somente `frontend/legal/*.html text eol=lf` em `.gitattributes`, preservando as regras anteriores e os HTML; verificar `git check-attr` e os hashes publicados, registrando o resultado em `validacao.md`.
- [x] 1.2 Validar um checkout descartável com `core.autocrlf=true` e executar os dois unitários de documentos existentes; conferir hashes idênticos, diff restrito e `openspec validate fixar-quebras-de-linha-dos-termos --strict`, sem banco, commit ou push, registrando evidências em `validacao.md`.

## Workflow follow-up

- Verificar a correção com a skill OpenSpec. Não há delta para sincronizar (`skip_specs: true`).
- Arquivar somente com tarefas concluídas e sem achado crítico; commit e push permanecem fora do escopo autorizado.
