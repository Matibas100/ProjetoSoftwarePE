# Tarefas

## 1. Baseline e padrão de leitura

- [x] 1.1 Enumerar os arquivos elegíveis do baseline `663891af9f6b0cbe7c1df0b7841e104ae7f2cbf1` conforme a tabela do design; guardar lista, fontes e hashes em `tmp/`, preservando alterações locais posteriores. Verificar que o conjunto exclui SQL, termos, dependências, históricos, relatórios e arquivos sensíveis; não ler nem copiar credenciais.
- [x] 1.2 Acrescentar o padrão breve de indentação, espaçamento e quebras seguras à convenção existente `docs/conventions/documentacao-e-nomenclatura.md`. Verificar coerência com o design, sem nova ferramenta, dependência, configuração ou obrigação de reduzir linhas.

## 2. Python da aplicação

- [x] 2.1 Formatar somente os arquivos que precisem de ajuste em `backend/app/**/*.py` e `backend/run.py`, em lotes pequenos por módulo; separar instruções compactadas e organizar blocos, preservando nomes, imports e execução. Verificar AST antes/depois, comentários e literais de cada lote, e rodar os testes unitários existentes correspondentes; registrar resultados em `validacao.md`.

## 3. Ferramentas Python do banco

- [x] 3.1 Formatar somente o Python elegível em `backend/database/`, preservando integralmente strings SQL, metadados, assinaturas e operações. Verificar equivalência de AST/literais e hashes dos SQL/referências; executar os testes existentes das ferramentas, incluindo integrações de migrations no MySQL descartável com opt-in de processo, sem usar o banco da demonstração; registrar resultados.

## 4. JavaScript da interface

- [x] 4.1 Formatar os JavaScripts de produção elegíveis em `frontend/`, por área pública, Aluno e Administração, preservando ordem, declarações, callbacks, diretivas e comentários. Verificar AST antes/depois em cada lote e executar os testes Vitest existentes da área afetada; registrar resultados sem alterar assertions para aceitar diferenças funcionais.

## 5. HTML, CSS e sprites

- [x] 5.1 Formatar HTML elegível fora de `frontend/legal/`, preservando atributos, textos, espaços significativos, scripts e campos. Verificar DOM ordenado, textos e regiões sensíveis antes/depois, além dos testes de contrato HTML existentes; registrar páginas ajustadas e exceções.
- [x] 5.2 Formatar CSS elegível e os dois sprites próprios indicados no design, sem ordenar propriedades, alterar valores, seletores ou desenhos. Verificar árvores ordenadas do CSS e elementos/atributos dos SVG; conferir as páginas afetadas em 1440 e 390 px, incluindo menus, formulários e estados de resposta/resultado. Registrar a comparação visual sem traces, HAR ou estado autenticado.

## 6. Testes, scripts e configurações existentes

- [x] 6.1 Formatar os testes Python elegíveis, sem mudar cenários, fixtures, assertions ou thresholds. Verificar AST, comentários e literais antes/depois e executar `python backend/tests/run_unit.py`; registrar resultados. Não criar testes que apenas espelhem a disposição de espaços.
- [x] 6.2 Formatar os testes JavaScript/E2E, scripts `.mjs`, `playwright.config.js` e `vitest.config.js` elegíveis, mantendo cenários, valores, comandos e filtros. Verificar AST, diretivas e comentários; executar `npm run test:unit` e `npm run test:e2e:list`, confirmando a descoberta dos mesmos casos; registrar resultados.
- [x] 6.3 Formatar scripts Python elegíveis e, somente se necessário, o espaçamento do `Makefile`. Verificar equivalência de AST e dos comandos/receitas, incluindo tabulações obrigatórias; rodar os testes existentes dos scripts afetados e conferir os atalhos contra os comandos documentados. Registrar arquivos já legíveis que permaneceram intactos.

## 7. Regressão integrada e fechamento das evidências

- [x] 7.1 Executar `python backend/tests/run_backend_coverage.py` com os opt-ins `RUN_MYSQL_INTEGRATION=1` e `RUN_MYSQL_MIGRATION_INTEGRATION=1` somente no processo, `npm run test:coverage` e `npm run test:e2e` com `RUN_MYSQL_E2E=1`. Verificar MySQL real com dados/schemas de teste, os casos existentes e os gates de cobertura inalterados; não invocar Gemini real para comprovar formatação. Registrar comandos, resultados e limitações reais, sem declarar sucesso de uma etapa não executada.
- [x] 7.2 Revisar o diff completo, confirmar equivalência dos fontes alterados e hashes dos arquivos protegidos não sensíveis, e concluir `validacao.md` com evidências de todos os grupos. Verificar ausência de mudanças funcionais, exclusões, dependências novas, segredos ou alterações em dados/artefatos protegidos; executar `git diff --check` e `openspec validate padronizar-formatacao-do-codigo --strict`.

## Workflow follow-up

- Verificar a implementação pelo workflow OpenSpec antes de arquivar.
- Não sincronizar specs nesta change de formatação (`skip_specs: true`).
- Arquivar após a verificação; commit e push somente com autorização explícita.
- Tratar sugestões de simplificação da análise como discussão futura, fora destas tarefas.
