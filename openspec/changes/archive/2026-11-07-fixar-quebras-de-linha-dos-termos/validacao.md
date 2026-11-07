# Validação — 07/11/2026

Correção solicitada pelo usuário após a revisão: manter os bytes publicados dos termos em qualquer checkout. Change `spec-driven`, com `skip_specs: true`, sem mudança de requisito funcional.

## Evidências

- `.gitattributes` recebeu somente `frontend/legal/*.html text eol=lf`; regras de hooks e SQL preservadas.
- `git check-attr text eol -- frontend/legal/termo-de-uso-v1.html frontend/legal/termo-de-consentimento-plano-v1.html`: ambos `text: set`, `eol: lf`.
- SHA-256 dos dois HTML conferido antes e depois; nenhum documento ou metadado foi reescrito.
- Repositório temporário, sem remote e sem commits, com `core.autocrlf=true`: arquivos adicionados apenas ao índice temporário e recriados por `git checkout-index --all --force`. Ambos os hashes permaneceram iguais aos publicados; diretório limpo ao concluir.
- `tests.unit.test_privacidade.DocumentosPrivacidadeTest`: 2/2 aprovados, sem banco nem leitura de `.env`.
- `openspec validate fixar-quebras-de-linha-dos-termos --strict`: aprovado, sem deltas aplicáveis.
- `git diff --check -- .gitattributes`: aprovado.

A suíte completa da aplicação já passou na revisão imediatamente anterior (160 unitários, 129 integrações MySQL, 169 frontend, 7 servidor, 3 E2E). Não foi repetida por esta alteração exclusiva de atributos de Git.

Sem commit, push, renormalização global ou alteração da configuração Git do usuário. A operação autorizada de backup/implantação da migration 010 é separada desta correção de checkout e terá registro local sem credenciais em `test-results/atualizacao-local-010/`.

## Verificação OpenSpec

| Dimensão | Resultado |
| --- | --- |
| Completude | 2/2 tarefas concluídas, sem requisito funcional alterado |
| Correção | Atributos LF, checkout Windows simulado, ambos os hashes e 2 unitários aprovados |
| Coerência | Uma linha de configuração; textos, metadados, aplicação e regras anteriores preservados |

Sem achados críticos ou avisos específicos desta correção. Pronta para arquivar. Sincronização não aplicável: `skip_specs: true`, sem delta specs. Os avisos de tamanho das specs gerais permanecem fora desta correção.
