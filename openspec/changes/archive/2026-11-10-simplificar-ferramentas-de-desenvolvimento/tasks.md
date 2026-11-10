# Tarefas

## 1. Retirar o hook obrigatório

- [x] 1.1 Registrar o estado inicial das alterações locais, o valor/origem de `core.hooksPath`, a existência de hooks adicionais e de preferências do VS Code, além dos hashes não sensíveis de frontend/backend, banco, workflow, lockfile e configurações de testes. Verificar a lista de edição fechada da proposta e preservar alterações legítimas; não ler credenciais ou configuração Git completa.
- [x] 1.2 Remover somente `.githooks/pre-push`, `scripts/install-git-hooks.mjs`, o script `hooks:install` de `package.json` e sua regra exclusiva em `.gitattributes`; atualizar a preparação e a orientação de testes no README. Verificar JSON, igualdade das dependências/demais scripts/lockfile/workflow, preservação das regras SQL/legais e ausência de instruções ativas para instalar o hook. Executar uma vez `python backend/tests/run_unit.py` e `npm run test:unit`, mantendo os testes e gates existentes.
- [x] 1.3 Retirar `core.hooksPath` somente do escopo local deste clone e somente se corresponder à `.githooks` deste projeto, conforme o design; documentar no README como outros clones conferem e removem apenas a mesma configuração antiga. Verificar origem e valor efetivo após a operação, preservando configurações globais, caminhos e hooks alheios. Não executar push ou configurar diretório vazio de hooks para validar.

## 2. Facilitar a navegação no VS Code

- [x] 2.1 Criar ou mesclar as oito entradas de `files.exclude` em `.vscode/settings.json` local, preservando demais preferências; explicar brevemente no README como adotar e reverter essa visualização. Verificar o conteúdo resultante e `git check-ignore .vscode/settings.json`, confirmar que fontes/configurações continuam fora dos padrões de ocultação e que os diretórios/relatórios preexistentes permanecem no disco. Registrar separadamente qualquer efeito visual realmente observado no editor, sem alegar inspeção de UI que não tenha ocorrido.

## 3. Conferência integrada e fechamento

- [x] 3.1 Concluir `validacao.md` com os comandos, resultados unitários, estado do hook, preferência local, hashes preservados e limitações. Conferir o diff restrito aos cinco arquivos versionados previstos e aos artefatos da change, sem mudança em produto, banco, pipeline, dependências, relatórios ou backups; executar `git diff --check` e `openspec validate --all --strict`. Não executar integrações, Gemini, descoberta E2E, instalação de pacotes ou limpeza de temporários para esta mudança de ferramentas.

## Workflow follow-up

- Verificar antes de arquivar; não há specs a sincronizar (`skip_specs: true`).
- Arquivar somente depois da verificação. Commit e push exigem autorização explícita e ficam fora do apply.
- O resultado de CI de uma publicação anterior não comprova uma futura publicação desta change; a CI permanece habilitada com os mesmos testes e limites.
