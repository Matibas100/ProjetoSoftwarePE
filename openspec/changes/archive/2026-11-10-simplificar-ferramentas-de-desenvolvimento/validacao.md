# Validação: simplificar as ferramentas de desenvolvimento

## Estado inicial — 10/11/2026

- Referência: `2a82c77b6978efdf32ecfc11deb25d529e576fc2`.
- `git status --short`: somente a change atual, `output/` e `tmp/` não rastreados; nenhum arquivo versionado modificado.
- `git config --local --get-all core.hooksPath`: `.githooks`.
- `git config --show-origin --show-scope --get-all core.hooksPath`: `local file:.git/config .githooks`; nenhuma outra origem efetiva retornada.
- `.githooks/` contém somente `pre-push`; `.git/hooks/` contém 14 arquivos `.sample`, sem hooks ativos adicionais.
- `.vscode/settings.json` ausente. `git check-ignore .vscode/settings.json` retorna esse caminho (exit 0).
- Presentes no disco: `.venv/`, `node_modules/`, `.coverage`, `coverage-backend.json`, `coverage-frontend/`, `test-results/`, `instance/`, `tmp/` e `output/`.
- Lista fechada de edição conferida: remover `.githooks/pre-push` e `scripts/install-git-hooks.mjs`; ajustar somente `package.json`, `.gitattributes` e `README.md`, além dos artefatos desta change. Configurações locais Git/VS Code não são versionadas.
- Preflight somente leitura: AGENTS.md, conventions, arquitetura mestre, ADR-010, proposta, design, tasks e superfícies afetadas. Nenhuma leitura de `.env` ou da configuração Git completa.

## Baseline de preservação

Hashes SHA-256 dos bytes locais, antes da primeira edição. Para conjuntos, o hash
agregado usa caminhos relativos ordenados e a representação
`caminho + NUL + sha256_do_arquivo + LF`, em UTF-8. Banco está incluído em backend.

| Conjunto | Arquivos | SHA-256 inicial |
| --- | ---: | --- |
| backend | 299 | `4e49b406da8e40eee2ea957901995ab226ac621df2c7cd60adbbaf1c65253a32` |
| frontend | 87 | `209f57fa5e39db411408297d5bcc2f32b1bf0ea844d847135e224a8eca9de42c` |
| banco | 26 | `7f94257d8ca570a111ccac78a9e70474a0dc6cd83b24fda1d89ac050979ee1ab` |
| workflow | 1 | `e7dffcef2bacf711eba7a73db73131b43c25bba501834069cb24312be460ad83` |
| configuracoes_testes | 4 | `6f313de9be84bc30de01121b8c3cabd730d665cc06de03dfedc661cf8824ad6e` |
| lockfile | 1 | `22ebb5c936cf78b65e1026c60c1401e4ed64db90adaa0f49da4c39b2d525c360` |
| relatorios | 643 | `d1c470611fbb82d4ca3a23bf416f0683f0964bec6367b2e09c7e02fb53c892dc` |

Os 727 arquivos versionados fora da lista de edição, excluindo nomes
`.env*`, têm hash agregado
`2d0ece5278281d503f1ccbfa5b42d295125ce959e8360cbe4463fb5117b9a14f`.
Inventário por caminho/tipo/tamanho/mtime dos 5050 itens em
`output/`, `tmp/` e `instance/`:
`c434cee666b33da294a55cbd905c30fe3555d79e8bacf65af84781f5f0ff5b17`. Nenhum conteúdo desses diretórios foi lido para esse inventário.

## Resultados

### Implementação e comandos

- Removidos somente `.githooks/pre-push` e `scripts/install-git-hooks.mjs`.
- `package.json` validado com `json.loads`: objeto idêntico ao `HEAD` após
  remover exclusivamente `scripts["hooks:install"]`; dependências e demais
  scripts iguais. Nenhuma instalação executada.
- `.gitattributes` conserva as regras de SQL e HTML legais; saiu somente
  `.githooks/* text eol=lf`. Hashes dos SQL/termos permanecem iguais.
- README atualizado: preparação sem instalador, testes locais sob demanda,
  CI após o envio, orientação restrita para clones antigos e adoção/reversão
  da preferência local. Comandos de testes e evidências históricas preservados.
- Busca direcionada (`rg -n 'hooks:install|install-git-hooks|pre-push|githooks'`
  no README, manifestos, scripts, conventions e CI): nenhum comando ativo para
  instalar o hook permanece. Menções históricas nos arquivos arquivados não
  foram alteradas.

| Comando executado uma vez | Resultado |
| --- | --- |
| `python backend/tests/run_unit.py` | Exit 0; 202 testes, `OK` |
| `npm run test:unit` | Exit 0; 18 arquivos e 302 testes aprovados, cobertura desabilitada pelo comando existente |

O Vitest emitiu `Not implemented: navigation to another Document`, sem falha.
Mensagens sanitizadas de erro nos testes Python pertencem aos cenários negativos;
a suíte terminou com `OK`. Não houve alteração de testes ou gates.

### Configuração Git local

Antes de desconfigurar, um script de conferência normalizou o único valor local
para a pasta `.githooks` deste projeto e confirmou que, após remover `pre-push`,
não restavam hooks nessa pasta. Executado:

```powershell
git config --local --unset-all core.hooksPath
git config --local --get-all core.hooksPath
git config --show-origin --show-scope --get-all core.hooksPath
```

O primeiro comando terminou com exit 0. As duas consultas posteriores terminaram
com exit 1 e saída vazia, comportamento esperado para chave ausente. Não há valor
efetivo herdado neste clone. Nenhuma configuração global foi modificada; os 14
arquivos `.sample` de `.git/hooks/` mantêm os hashes iniciais. Não houve push nem
configuração de diretório vazio para contornar hooks.

### Preferência local do VS Code

Criado `.vscode/settings.json` com as oito entradas exatas do design, todas
`true`; não havia preferências preexistentes. JSON e igualdade do objeto foram
conferidos, assim como `git check-ignore .vscode/settings.json` (exit 0).
O arquivo permanece ignorado e não integra o diff versionado.

Os padrões não abrangem fontes, testes-fonte, scripts, `.github/`, `.coveragerc`,
manifestos, `instance/`, `tmp/` ou `output/`. Os diretórios/relatórios preexistentes
continuam no disco. **Não houve inspeção da UI do VS Code**; foi verificada a
configuração, sem alegar que o efeito visual foi observado.

### Preservação e limites

Repetida a coleta de hashes após os testes e as edições: todos os sete conjuntos
da tabela inicial mantêm seus hashes e contagens. Os 727 arquivos versionados
protegidos mantêm o hash agregado inicial. Os 643 relatórios mantêm bytes e
caminhos. O inventário dos 5050 itens de `output/`, `tmp/` e `instance/` permanece
igual, incluindo tamanhos/mtime de arquivos; nenhum backup foi removido ou movido.
Bibliotecas e caches preexistentes não foram limpos.

Não executados: integrações/MySQL, Gemini real, cobertura completa, descoberta
E2E, navegador, instalação de pacotes, limpeza de temporários, commit, push ou
merge. As suítes unitárias usam seus mecanismos controlados existentes e não
comprovam integrações ou a CI de uma publicação futura. O workflow e os limites
de 90% de linhas/85% de branches permanecem idênticos.

### Conferências finais

- `git diff --name-status` e comparação programática: exatamente os cinco
  arquivos previstos, com três modificações e duas remoções. Não há arquivo
  versionado alterado fora dessa lista. `output/` e `tmp/` continuam não
  rastreados, como no início; não foram incluídos na change.
- Comparação binária de `.gitattributes` com o `HEAD` menos a linha aposentada:
  igualdade exata das regras restantes. Comparação estrutural de `package.json`
  repetida com sucesso.
- `git diff --check`: exit 0, sem erros de whitespace. Git emitiu apenas avisos
  de futura conversão LF/CRLF em `.gitattributes` e `package.json`; regras SQL e
  legais e hashes dos arquivos protegidos estão preservados.
- `openspec validate --all --strict`: exit 0, **20 itens aprovados, 0 falhas**
  (19 specs e esta change). Informação esperada de `skip_specs: true`: nenhum
  delta de comportamento e nenhuma sincronização de specs necessária.

As cinco tarefas de apply foram implementadas e conferidas. A change permanece
ativa para a etapa de verificação antes do arquivamento; não foi arquivada
automaticamente.

