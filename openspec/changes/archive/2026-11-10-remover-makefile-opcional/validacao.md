# Validação: remover Makefile opcional

Data: 10/11/2026. Comparação com a árvore local imediatamente anterior ao apply, não com o HEAD.

## Estado inicial

Foram registrados em memória os SHA-256 de 4183 arquivos existentes (fontes, testes, runners, configurações, documentação, artefatos arquivados, output e tmp), sem ler arquivos .env. Os seis arquivos do escopo também tiveram seus bytes originais preservados em memória para comparação. Nenhum backup foi criado no disco.

Alterações locais preexistentes:

```text
 M .gitattributes
 D .githooks/pre-push
 M README.md
 M package.json
 D scripts/install-git-hooks.mjs
?? docs/technical/operacao-do-projeto.md
?? docs/technical/operacao-tutor-ia.md
?? openspec/changes/archive/2026-11-10-simplificar-ferramentas-de-desenvolvimento/
?? openspec/changes/archive/2026-11-10-simplificar-readme-do-projeto/
?? openspec/changes/remover-makefile-opcional/
?? output/
?? tmp/
```

Hashes iniciais dos arquivos do escopo:

| Arquivo | SHA-256 inicial |
| --- | --- |
| `Makefile` | `237b7e5d977744bb753ecb04897307a459b4d86dbf1e7b2f8da890d35aeafa94` |
| `README.md` | `b41c1637e915d55f2ee51ae7c4acc248efe157a8008991ddadbfb87e476b11c5` |
| `docs/conventions/testes.md` | `9d6ba4789604b4cfb4b08f5917326a6254bdd684110b8c225ec6af9fb89674a1` |
| `docs/conventions/documentacao-e-nomenclatura.md` | `80cac77765d8dbd793be2ea348c738571e7baf726bfe8bed10767d24b6770c33` |
| `docs/technical/operacao-do-projeto.md` | `834941b511b532d638b3173a2238c92dd0f016a6a0298b68314c8ebba8493fe0` |
| `backend/tests/unit/test_migrations.py` | `36f1995fddc0d844f0eca10a17fcc1592aeaed9d36cac171efe13382e70031e6` |

## Resultados

| Verificação | Resultado |
| --- | --- |
| `python backend/tests/run_unit.py` | 202 testes aprovados; uma execução, código de saída 0 |
| Comparação integral de `test_migrations.py` com os bytes locais iniciais | Somente renomeação para `CliTest.test_baseline_e_reconcile` e retirada das quatro linhas de leitura/laço/assertion de Makefile, incluindo a linha vazia; decorators, setup, mocks, chamadas e assertions de baseline/reconcile e os demais testes idênticos |
| Pesquisa estática por `makefile` e `\bmake\b` com `rg -n -i --hidden`, excluindo Git, dependências, temporários e histórico | Nenhuma instrução ativa de executar Make fora dos artefatos desta change; ocorrências restantes são âncora de compatibilidade, pacote transitivo `make-dir` e texto em inglês das skills |
| Links dos quatro documentos alterados | 81 links locais válidos, incluindo os fragmentos Markdown |
| Âncoras do guia operacional | As 13 âncoras anteriores continuam válidas; título atualizado para “Testes e comandos diretos”, mantendo `testes-e-atalhos-make` como id explícito |
| `git diff --check` | Código de saída 0, sem erros de whitespace; avisos de conversão futura LF/CRLF em arquivos locais, sem conversão realizada |
| `openspec validate --all --strict` | 20 itens aprovados, zero falhas; `skip_specs: true` aceito |

## Comandos preservados

Conferência estática contra o Makefile original, os runners existentes, o parser de `backend/database/migrate.py` e os scripts atuais de `package.json`, sem executar operações no banco:

| Uso | Entrada direta documentada |
| --- | --- |
| Status do banco | `python backend/database/migrate.py status` |
| Aplicar migrations | `python backend/database/migrate.py up` |
| Adotar banco existente | `python backend/database/migrate.py baseline --confirm` |
| Registrar reconciliação autorizada | `python backend/database/migrate.py reconcile 003 --confirm` (`003` é exemplo) |
| Unitários Python/frontend | `python backend/tests/run_unit.py` e `npm run test:unit` |
| Integrações | `python backend/tests/run_integration.py` |
| Cobertura backend | `python backend/tests/run_backend_coverage.py` |
| Cobertura frontend | `npm run test:coverage` |
| Cobertura das duas pilhas (antigos `test` e `test-coverage`) | Executar os dois comandos de cobertura acima |
| Navegador | `python scripts/run_e2e.py` ou `npm run test:e2e` |

Foram conferidas 11 entradas diretas únicas. Os opt-ins `RUN_MYSQL_INTEGRATION`, `RUN_MYSQL_MIGRATION_INTEGRATION` e `RUN_MYSQL_E2E` mantêm as mesmas ocorrências nos quatro documentos. Permanecem as precondições de backup/inspeção, confirmação, MySQL 8 descartável, configuração por ambiente no E2E, ausência de mocks/SQLite nas integrações e gates de 90%/85%.

## Preservação do estado local

A comparação de SHA-256 com a captura inicial confirmou igualdade em 4.176 arquivos fora dos seis arquivos do escopo e de `tasks.md` desta change. Isso inclui fontes do produto, migrations/SQL/CLI, testes restantes, runners, dependências/lockfile, workflow CI, `.gitattributes`, guias e changes arquivadas preexistentes, relatórios e backups em `output/` e `tmp/`. As remoções preexistentes de hooks continuam preservadas.

SHA-256 agregado dos caminhos e hashes preservados: `77de5c0e0872cc61afb5cfd6e3f0a47023a9689ffa3fd28c7f6aee4dc450b904` (pares ordenados por caminho, cada registro no formato `caminho + NUL + hash + LF`).

As únicas diferenças em arquivos existentes são os seis arquivos previstos e o checklist desta change. O único arquivo novo é `validacao.md` desta change. Os diffs foram comparados com o estado local inicial, incluindo o README já simplificado e o guia operacional ainda não rastreado. UTF-8 e finais de linha dos arquivos existentes foram preservados.

| Arquivo | SHA-256 final |
| --- | --- |
| `docs/technical/operacao-do-projeto.md` | `af77e1e13593bbc2d5336c8a7d21c56cf1b59ed712562ee6eae738ba56296f55` |
| `Makefile` | Removido |
| `README.md` | `5bb316f6db14a9d56d3963f8b487aca9e991567421c14415d35fb5f043f46515` |
| `backend/tests/unit/test_migrations.py` | `bd39a6839ce13395e4e5ada010851924d3a73a12f95ea4e8a501a59a8734a1de` |
| `docs/conventions/documentacao-e-nomenclatura.md` | `43eec5f7bab402c42fe23a04a3014904abd1b49378e4ea252552fc61efaf7a8d` |
| `docs/conventions/testes.md` | `b6a6ba0ad56456967c3cb7fc1560bfed3470cba3419bd18f96a47db3913e510a` |

## Limites e próximos passos

Não houve instalação, operação no banco, integração MySQL, cobertura, frontend, E2E ou descoberta Playwright. Não foi medida cobertura nesta execução e não se declara aprovação atual de CI ou publicação. A execução unitária usa o runner que bloqueia `.env`, desabilita Tutor e não abre MySQL. Nenhuma nova fixture de integração ou teste de ausência de arquivo foi criado. Não houve edição de relatórios/backups preexistentes, preferências locais, commit, push ou merge.

Apply concluído; a verificação formal do workflow e o arquivamento continuam como próximos passos. Não há delta specs para sincronizar (`skip_specs: true`).
