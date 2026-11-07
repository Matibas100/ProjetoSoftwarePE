# Tasks — Alinhar a documentação da entrega

## 1. Referência e rastreabilidade

- [x] 1.1 Reler os dez arquivos delimitados no design, registrar revisão Git, os 31 avisos atuais e os títulos/cenários originais em `validacao.md`; verificar a correspondência do inventário com `openspec validate --specs --strict` e preservar uma referência verificável de cada bloco antes de editá-lo.

## 2. Reorganização editorial das specs

- [x] 2.1 Reorganizar os dez requisitos longos de `autenticacao-escolar/spec.md`, preservando seus títulos e cenários e transferindo cada detalhe para cenário adequado; completar o mapeamento por cláusula no relatório e verificar que a capability passa na validação estrita, sem perder permissões, CSRF, limites ou contratos HTTP.
- [x] 2.2 Reorganizar um requisito de `catalogo-academico/spec.md` e quatro de `gestao-administrativa-conteudo/spec.md`; verificar ambas as capabilities em modo estrito e comparar cada cláusula com o baseline, incluindo compatibilidade, descarte e acesso administrativo.
- [x] 2.3 Reorganizar quatro requisitos de `desempenho-real/spec.md` e cinco de `plano-estudos-basico/spec.md`; verificar ambas em modo estrito e rastrear fórmulas, períodos, privacidade, idempotência e histórico sem alterar suas regras.
- [x] 2.4 Reorganizar três requisitos de `questoes-versionadas/spec.md` e quatro de `simulados-fixos/spec.md`; verificar ambas em modo estrito e rastrear validações, snapshots, retomada, finalização e preservação histórica. Em cada arquivo, conferir que os demais requisitos ficaram intactos.

## 3. Entrega e evidências atuais

- [x] 3.1 Atualizar README e `docs/technical/entrega-academica.md` para os três arquivos E2E existentes, mantendo a matriz numerada 1–20; verificar com `npm run test:e2e:list` e conferir os links. Registrar publicação/CI pelo SHA e run indicados no design, sem atribuir aprovação a mudanças posteriores nem reescrever relatórios históricos.
- [x] 3.2 Ajustar somente o contexto textual de `openspec/config.yaml` para distinguir dez funcionalidades originais e vinte atuais; verificar parsing YAML com ferramentas já disponíveis e diff demonstrando que `schema`, `rules`, `operations` e guardrails não mudaram.

## 4. Verificação documental integrada

- [x] 4.1 Executar `openspec validate --specs --strict` sem erros/avisos e validar esta change em modo estrito; revisar o mapeamento completo das cláusulas, títulos/cenários preservados, links e IDs 1–20. Registrar comandos/resultados e confirmar pelo diff que só os dez arquivos permitidos e os artefatos desta change mudaram, sem código, SQL, HTML legal, segredos ou binários oficiais. Não executar a aplicação ou testes MySQL por esta edição documental.

## Workflow follow-up

- Verificar a implementação com `openspec-verify-change` antes do arquivamento.
- Não há delta funcional a sincronizar (`skip_specs: true`); arquivar somente após a verificação.
- Aplicar preferencialmente antes de `tornar-fingerprint-de-schema-portavel`. Commit e push não fazem parte desta autorização.
