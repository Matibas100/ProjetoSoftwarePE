# Tasks — Tornar portável a conferência estrutural do banco

## 1. Referência e reprodução isolada

- [x] 1.1 Registrar em `validacao.md` os hashes dos SQLs 000–010/bootstrap, nomes/reexportações atuais e o recorte das dez tabelas; executar o baseline dos testes do runner em MySQL descartável com opt-ins existentes e reproduzir a diferença de charset numa fixture sintética, comprovando metadados iguais sem operar no banco real do grupo.

## 2. Assinatura estrutural determinística

- [x] 2.1 Implementar no `legacy_schema.py` o helper de metadados/canonicalização definido no design, incluindo FKs internas/externas, CHECK/ENFORCED, expressões geradas, índices e defaults tipados; adicionar unitários em `backend/tests/unit/test_migrations.py` e verificar estabilidade de ordenação, independência de estatísticas/nome físico e sensibilidade às diferenças estruturais com `python backend/tests/run_unit.py`. Documentar os campos e limites no adendo ao ADR-001 no mesmo grupo.
- [x] 2.2 Derivar e revisar as dez assinaturas esperadas em schemas descartáveis criados pelas migrations oficiais; substituir o hash de DDL nos três detectores, mantendo nomes/importações, inventários e validações anteriores. Verificar os prefixos 008, 009 e 010 nas integrações de migrations de Simulados/Plano/Privacidade e registrar origem, versão e invariantes das referências no relatório, sem usar o banco encontrado como expectativa.

## 3. Restauração e proteção contra divergência

- [x] 3.1 Acrescentar testes de round-trip estrutural com MySQL real, reutilizando `migration_integration_support.py` e criando um teste `*_integration.py` descoberto pelo runner quando necessário; verificar restauração em segundo schema descartável, charset redundante, reconhecimento de 008–010, baseline sem histórico, dados sintéticos preservados, upgrade apenas das pendências e reexecução zero. Verificar também cópia com histórico válido, sem exigir `mysqldump`/Docker e com limpeza segura dos dois schemas mesmo após falha; documentar a reprodução no relatório.
- [x] 3.2 Acrescentar casos negativos por dimensão do design às integrações do runner, incluindo FKs externas, collation, defaults, índice/ordem/unicidade, expressão gerada e CHECK/ENFORCED; verificar recusa sem dados alterados nem versões presumidas, metadados insuficientes nos unitários e preservação dos testes existentes de checksum, lock, procedure, schema parcial/excedente e RUNNING/FAILED. Conforme ajuste aprovado, conferir corpo/parâmetros da procedure nos prefixos 008–010, reutilizando o contrato conhecido sem alterar o comportamento 000–007; testar corpo, nome, modo e tipo de parâmetro divergentes. Registrar os cenários efetivamente executados, sem contar skips como sucesso.
- [x] 3.3 Atualizar as seções de migrations do README e operação de Plano/Privacidade para explicar o reconhecimento por metadados, seus limites e a diferença entre assinatura estrutural, checksum SQL e hash legal; verificar links e comandos contra o runner, preservando o conteúdo da outra change e sem prometer compatibilidade universal ou hospedagem já realizada.

## 4. Regressão integrada e integridade

- [x] 4.1 Executar `python backend/tests/run_backend_coverage.py` com configuração de teste isolada, `RUN_MYSQL_INTEGRATION=1` e `RUN_MYSQL_MIGRATION_INTEGRATION=1` somente no processo; verificar integrações reais, cobertura mínima de 90% linhas/85% branches e ausência de arquivo executável sem cobertura. Depois dos checks direcionados, executar uma vez `npm run test:e2e` com `RUN_MYSQL_E2E=1` e MySQL fornecido por ambiente, comprovando os fluxos atuais com migrations oficiais. Registrar resultados, versões e limitações reais em `validacao.md`.
- [x] 4.2 Validar esta change em modo estrito e confrontar implementação com cada cenário do delta; conferir hashes dos SQLs/bootstrap inalterados, ausência de migration 011 e diff sem alteração de contrato HTTP, schema funcional, HTMLs legais, `.gitattributes`, dependências ou segredos. Confirmar que nenhum baseline/upgrade/restauração foi executado no banco operacional e que fixtures descartáveis foram limpas.

## Workflow follow-up

- Verificar a implementação com `openspec-verify-change`, sincronizar somente o delta `migrations-sql` e arquivar após a conclusão das verificações.
- Preferir aplicar após `alinhar-documentacao-de-entrega`; reler README antes de editar para preservar as seções já atualizadas.
- Commit, push, atualização do banco operacional e publicação AWS ficam fora desta change.
