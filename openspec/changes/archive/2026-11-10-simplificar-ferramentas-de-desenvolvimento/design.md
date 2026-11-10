# Design: ferramentas mais simples, produto preservado

## Context

Ver [proposal.md](proposal.md). O clone atual usa `core.hooksPath=.githooks` em `.git/config`, com um único hook versionado, `pre-push`. O instalador é acionado por `hooks:install` e aparece em duas instruções do README. `.vscode/` já é ignorada pelo Git e não há `settings.json` local no momento da proposta.

O design distingue configurações versionadas do projeto de preferências locais; essa distinção evita substituir hooks pessoais ou publicar preferências do editor de um integrante.

## Goals / Non-Goals

**Objetivos:** encerrar a instalação do hook aposentado, simplificar o push e reduzir o ruído no Explorer. Manter disponíveis todos os testes e configurações necessárias à instalação e execução.

**Limites:** nenhuma mudança em frontend/backend, SQL, dados, bibliotecas instaladas, testes, regras de cobertura ou workflow do GitHub. Não limpar diretórios nem acrescentar automação substituta.

## Decisions

### 1. Retirar somente a automação local duplicada

Excluir apenas `.githooks/pre-push` e `scripts/install-git-hooks.mjs`. Não fazer exclusão recursiva de diretórios nem remover hooks adicionais que possam aparecer depois desta proposta.

Em `package.json`, remover somente `scripts["hooks:install"]`. Dependências e demais scripts permanecem idênticos; não executar instalação nem regenerar `package-lock.json`. Em `.gitattributes`, retirar somente a linha exclusiva de `.githooks`; conservar byte a byte as regras de SQL e HTML legais.

O workflow `.github/workflows/testes.yml`, os validadores, os gates de 90% de linhas/85% de branches e as configurações de Playwright/Vitest/cobertura permanecem iguais. Não desativar CI ou alterar testes para compensar a retirada do hook. A diferença operacional é explícita: o GitHub recebe o push antes de executar sua validação; testes locais continuam disponíveis sob demanda.

Alternativas rejeitadas: apagar as bibliotecas/relatórios para reduzir a árvore ou substituir o hook por outro instalador. A primeira perde recursos/evidências; a segunda mantém a manutenção que se pretende simplificar.

### 2. Desconfigurar o hook somente neste clone

Consultar apenas `git config --local --get-all core.hooksPath` e a origem efetiva dessa chave, sem imprimir a configuração Git inteira. Retirar a chave local somente quando ela apontar para `.githooks` deste projeto, seja caminho relativo, seja equivalente absoluto normalizado.

Se a chave estiver ausente, não fazer alteração. Se apontar para outro diretório, preservar esse valor e registrar que a configuração não pertence ao hook aposentado. Nunca alterar configuração global, usar um diretório vazio de hooks como bypass ou executar push para testar a mudança. Se aparecerem hooks adicionais que dependam da mesma configuração, preservá-los e resolver o novo conflito antes de desconfigurar.

O README deve orientar outros clones que instalaram o hook a conferir o valor local e removê-lo somente nesse caso. Um novo clone já não terá instalação de hook na preparação.

### 3. Ocultar arquivos gerados somente no Explorer local

Criar `.vscode/settings.json` com `files.exclude`, sem mudar `.gitignore` ou versionar esse arquivo. Se surgir configuração preexistente no apply, mesclar somente as oito entradas abaixo, preservando outras chaves e comentários; não reescrever todas as preferências.

```json
{
  "files.exclude": {
    ".venv": true,
    "node_modules": true,
    "**/__pycache__": true,
    ".coverage": true,
    ".coverage.*": true,
    "coverage-backend.json": true,
    "coverage-frontend": true,
    "test-results": true
  }
}
```

Isso afeta somente a exibição no editor. Não excluir ou mover esses arquivos nem alterar sua geração. Não ocultar `backend/`, `frontend/`, testes-fonte, scripts, `.github/`, `.coveragerc`, manifestos, `instance/`, `tmp/` ou `output/`.

Explicar brevemente no README como os demais integrantes podem adotar a preferência local e como revertê-la. Não criar arquivo modelo, extensão ou script extra. A verificação deve distinguir configuração conferida de efeito visual efetivamente observado no VS Code.

### 4. Validar pela superfície realmente alterada

Antes de editar, registrar o estado local relevante e hashes não sensíveis do produto, workflow, lockfile e configurações de testes. Depois, comparar o diff com a lista fechada da proposta, validar o JSON e confirmar que scripts/dependências só diferem pela retirada de `hooks:install`.

Executar uma vez os testes unitários existentes: `python backend/tests/run_unit.py` e `npm run test:unit`. Não criar testes novos de exclusão de arquivos. Integrações/E2E não precisam ser repetidos nesta change de ferramentas; a CI continua com seus mesmos passos. Não executar `test:e2e:list`, que pode regenerar o relatório local.

Conferir a chave Git, ausência do hook e instalador aposentados, preservação de hooks alheios, `git check-ignore .vscode/settings.json`, configuração do Explorer, `git diff --check` e `openspec validate --all --strict`. Não publicar para obter evidência de CI sem autorização de push. Registrar resultados e limitações reais em `validacao.md`.

## Risks / Trade-offs

- **Falha de teste conhecida apenas após envio:** testes locais permanecem manuais; GitHub Actions preserva a validação completa após o push.
- **Clones antigos mantêm a chave local:** orientar a desinstalação restrita no README; não prometer que alterações de `.git/config` se propagam pelo Git.
- **Preferência do editor substituir personalizações:** mesclar somente `files.exclude`; preservar outras configurações e manter o arquivo ignorado.
- **Ocultar ser confundido com apagar:** registrar que os arquivos continuam no disco, podem ser exibidos novamente e não foram removidos da instalação.

## Migration Plan

Não há migration de banco. Retirar hook/instalador e referências; atualizar a chave local e as preferências do Explorer; verificar e documentar. Para reverter, restaurar somente essas edições e os valores locais anteriores, sem reset geral ou limpeza. Specs não exigem sincronização (`skip_specs: true`); verificar antes de arquivar. Commit e push continuam dependendo de autorização explícita.
