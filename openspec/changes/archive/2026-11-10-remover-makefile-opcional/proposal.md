# Proposta: remover o Makefile opcional

## Why

A equipe usa diretamente Python e npm; o Makefile apenas duplica esses comandos e adiciona uma ferramenta opcional para explicar. A retirada pode simplificar a raiz do projeto, desde que a documentação e o teste que exige esse arquivo sejam ajustados juntos.

## What Changes

- Remover somente o `Makefile` da raiz, sem substituir seus atalhos por novos scripts ou ferramentas.
- Retirar a dependência opcional de GNU Make do README e das conventions; apresentar os mesmos comandos diretos de testes e migrations nas tabelas existentes.
- Atualizar as referências de Make em `docs/technical/operacao-do-projeto.md`, preservando os comandos, precondições e limitações operacionais.
- Ajustar `CliTest.test_baseline_reconcile_e_atalhos_make`, em `backend/tests/unit/test_migrations.py`: manter as verificações de `baseline`/`reconcile`, remover somente a leitura/assertions do Makefile e renomear o método de acordo com o escopo restante.
- Validar os testes unitários existentes e documentar a preservação do produto e da CI.

### Fora do escopo

Alterar runners, CLI, migrations, SQL, banco, frontend/backend, contratos, dependências, GitHub Actions ou gates de cobertura; apagar testes de comportamento ou criar testes de ausência de arquivo; editar artefatos arquivados, preferências locais, relatórios e backups. Sem instalação, execução de migrations, limpeza, commit, push ou merge.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. `skip_specs: true` é aplicável: são retirados atalhos opcionais, mantendo todos os comandos e requisitos do sistema.

## Impact

- **Arquivos:** remover `Makefile`; ajustar `README.md`, `docs/conventions/testes.md`, `docs/conventions/documentacao-e-nomenclatura.md`, `docs/technical/operacao-do-projeto.md` e um método em `backend/tests/unit/test_migrations.py`.
- **Compatibilidade:** comandos `make ...` deixam de existir; os equivalentes Python/npm continuam os mesmos. Aplicação e workflow usam os comandos diretos, mas o teste unitário atual ainda lê o Makefile; esse vínculo será retirado explicitamente, preservando as verificações da CLI.
- **Estado local:** preservar integralmente as alterações legítimas das duas changes anteriores já arquivadas, incluindo o README simplificado e o guia operacional ainda não versionado. Não reconstruir esses documentos a partir do HEAD antigo.
- **Arquitetura/produto:** nenhuma mudança nas camadas, 21 Models, vinte funcionalidades, autorização ou persistência.
- **Validação:** comparação do teste antes/depois, conferência estática de comandos e referências, `python backend/tests/run_unit.py`, diff restrito e OpenSpec. Não é necessário abrir MySQL ou repetir frontend/E2E.
