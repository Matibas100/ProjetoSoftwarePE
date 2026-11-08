# Tarefas

## 1. Preflight e caracterização

- [x] 1.1 Conferir `adequar-catalogo-editorial-a-procedures` aplicada/verificada/sincronizada e prefixo 013; registrar no `validacao.md` estado inicial, alterações externas, hashes dos SQLs anteriores e inventário de métodos/consumidores. Verificar ausência de colisão da migration 014, exposição de segredos e mudança não planejada de contrato; conflito exige atualizar artefatos antes de aplicar.
- [x] 1.2 Acrescentar caracterização com fixtures MySQL sintéticas dos resultados atuais e provar mapeamento textual ORM de CALL (inclusive JOIN quando aplicável), leitura corrente e mutação/rollback na mesma sessão. Verificar tipos, identidade gerenciada, resultados vazios, fechamento/drenagem e código HTTP sem fallback; registrar comandos/resultados, sem SQLite/mocks nas integrações.

## 2. Práticas próprias

- [x] 2.1 Iniciar `014_praticas_simulados_procedures.sql` e migrar propriedade/replay bloqueante de Práticas para as duas routines do inventário. Verificar duas contas, chave repetida/conflitante, ID alheio, identidade ORM e corrida responder/replay com rollback; documentar predicados e locks no documento SQL técnico.
- [x] 2.2 Migrar histórico e fatos de Práticas, ajustando somente adaptadores/serialização de apresentação. Verificar filtro por Assunto, totais/página vazia, ordem resposta/ID, limites UTC, exclusão de tentativas abertas e classificação/versão históricas; documentar saídas de página/fatos e preservar o diagnóstico da primeira etapa.

## 3. Composição e execução de Simulados

- [x] 3.1 Migrar lock de Simulado, itens individuais/em lote, títulos e listagem para as routines previstas. Verificar rascunho versus versão, ordem de composição, lotes vazios/repetidos, estado/paginação/total, revisão/publicação e rollback dos eventos; documentar os caminhos de gestão e catálogo sem alterar seus contratos.
- [x] 3.2 Migrar propriedade, chave e andamento individual/em lote para as routines previstas, mantendo dono, locks e constraints. Verificar concorrência de início, uma tentativa em andamento por dono/versão, replay, conteúdo retirado e 404 alheio sem gabarito; documentar retomada e limites de leitura.
- [x] 3.3 Migrar pares Resposta/Item bloqueantes, histórico e fatos de Simulados, mantendo entidades gerenciadas nas mutações e dados seguros na apresentação. Verificar salvar/limpar/finalizar com revisão e branco, corrida salvar/finalizar, falha real após correção parcial, replay finalizado, paginação e classificação após retirada/transferência; documentar as etapas de exposição de correção.

## 4. Instalação e integração documental

- [x] 4.1 Concluir `014_praticas_simulados_procedures.sql` e bootstrap equivalente e integrar reconhecimento/preflight até 014, com assinaturas/corpos/segurança oficiais. Verificar instalação vazia, upgrade 013 → 014 com dados, baseline/restauração, recursos ausentes/alterados, idempotência e preservação de prefixos/checksums anteriores; documentar pré-condições, privilégios e compensação. Validar fisicamente 013 sob o lock do runner, antes de qualquer DDL/registro de 014; recurso ausente ou divergente deve bloquear sem alterar dados/histórico.
- [x] 4.2 Atualizar README, documento SQL técnico e matrizes acadêmica/CRUD com o recorte real e caminhos ponta a ponta. Verificar links, correspondência método/procedure/Controller/Service/tela, vinte funcionalidades sem renumeração e pendências das próximas etapas sem promessa de aprovação acadêmica.

## 5. Verificação integrada

- [x] 5.1 Executar regressões afetadas (`test_praticas_integration.py`, `test_simulados_integration.py`, testes de migrations correspondentes, `test_desempenho_integration.py` e E2E de Práticas/Simulados.), as 29 integrações originais e suíte ampliada MySQL, gates de arquitetura, cobertura existente e E2E conforme conventions. Verificar contratos/metadata/guards/rollback e registrar comandos e resultados reais em `validacao.md`; não reduzir gates, substituir banco por mocks ou declarar sucesso se MySQL estiver indisponível.
- [x] 5.2 Executar `openspec validate adequar-praticas-simulados-a-procedures --strict`, `git diff --check` e revisão de escopo/segredos/hashes. Verificar preservação de alterações externas, migrations antigas, procedure legada, visuais e dados, sem DDL no banco de uso por efeito colateral.

## Continuidade do workflow

- Verificar a implementação, sincronizar os dois deltas e arquivar somente sem tarefas pendentes ou achados críticos.
- Aplicar a próxima etapa apenas depois da dependência concluída; não executar as changes em paralelo.
- Commit, push, AWS, uso real e envio ao Classroom dependem de instrução própria.
