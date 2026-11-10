# Proposta: simplificar as ferramentas de desenvolvimento

## Why

A equipe encontra bibliotecas e relatórios misturados aos arquivos que precisa estudar. O hook local também repete a suíte completa antes de cada push, embora a mesma validação já exista no GitHub Actions; simplificar esse fluxo reduz a dificuldade de uso sem alterar o produto.

## What Changes

- Remover `.githooks/pre-push` e `scripts/install-git-hooks.mjs`, aposentando apenas a automação local obrigatória de push.
- Retirar `hooks:install` de `package.json` e a regra exclusiva de `.githooks` em `.gitattributes`; preservar dependências, lockfile e regras de SQL/termos legais.
- Desconfigurar neste clone somente o `core.hooksPath` local que aponta para `.githooks`. Não modificar configuração global nem hooks de outros projetos.
- Atualizar o README: preparação sem instalação de hook, testes locais sob demanda e validação automática no GitHub após o envio. Preservar comandos e evidências históricas.
- Criar ou mesclar `.vscode/settings.json` local e ignorado pelo Git, ocultando no Explorer somente bibliotecas, caches Python e relatórios gerados. Preservar os arquivos no disco e as demais preferências do usuário.

### Fora do escopo

Código do frontend/backend, banco, migrations, procedures, segurança, arquitetura, telas e funcionalidades; modificar testes, thresholds ou `.github/workflows/testes.yml`; excluir bibliotecas, relatórios, backups, `instance/`, `tmp/` ou `output/`; introduzir dependências ou scripts novos; editar arquivos arquivados. Commit, push e merge não fazem parte desta autorização.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. A change usa `skip_specs: true`: ferramentas locais e documentação mudam, sem alterar requisitos das dezenove specs do sistema.

## Impact

- **Referência:** commit `2a82c77b6978efdf32ecfc11deb25d529e576fc2`.
- **Arquivos versionados:** dois removidos (`pre-push` e instalador) e três ajustados (`package.json`, `.gitattributes` e `README.md`), além dos artefatos desta change.
- **Estado local:** uma chave de configuração Git, quando corresponder ao hook aposentado, e preferências do Explorer em `.vscode/settings.json`; essas configurações não acompanham o clone de outro integrante.
- **Compatibilidade:** `npm run hooks:install` deixa de existir. Comandos de testes e instalação das dependências permanecem; o push deixa de aguardar a suíte local e o GitHub informa o resultado após receber o código.
- **Produto:** Frontend → Route → Controller → Service → Model/Repository → MySQL, vinte casos acadêmicos, 21 Models e contratos HTTP/SQL permanecem iguais. Nenhum dado é alterado.
- **Validação:** diff restrito, proteção dos arquivos do produto/CI/lockfile, configuração Git e VS Code, testes unitários existentes e validação OpenSpec. Sem executar MySQL, Gemini ou descoberta E2E para uma mudança de ferramentas.
