# Tarefas

## 1. Preflight e caracterização

- [x] 1.1 Conferir `adequar-consultas-academicas-a-procedures` aplicada/verificada/sincronizada e prefixo 012; registrar no `validacao.md` estado inicial, alterações externas, hashes dos SQLs anteriores e inventário de métodos/consumidores. Verificar ausência de colisão da migration 013, exposição de segredos e mudança não planejada de contrato; conflito exige atualizar artefatos antes de aplicar.
- [x] 1.2 Acrescentar caracterização com fixtures MySQL sintéticas dos resultados atuais e provar mapeamento textual ORM de CALL (inclusive JOIN quando aplicável), leitura corrente e mutação/rollback na mesma sessão. Verificar tipos, identidade gerenciada, resultados vazios, fechamento/drenagem e código HTTP sem fallback; registrar comandos/resultados, sem SQLite/mocks nas integrações.

## 2. Seletores, impacto e transferência

- [x] 2.1 Iniciar `013_catalogo_editorial_procedures.sql` com seletores de Áreas/Matérias/Assuntos e migrar os Repositories/delegações das Models inventariados. Verificar por MySQL os quatro IDs de Área, estados ativos/todos por perfil, filtros e ordenação atuais; atualizar a seção de Catálogo do documento SQL técnico com entradas/saídas.
- [x] 2.2 Migrar impacto de Matéria/Assunto, contagem de não arquivados e equivalência de nome para suas routines, preservando validações no Service. Verificar contagens com múltiplos vínculos, conflito normalizado/arquivado, ignorar o próprio ID, bloqueio RESTRICT e erros de exclusão/status; documentar as respectivas procedures e rotas existentes.
- [x] 2.3 Acrescentar as routines de locks de Assunto/Matérias e adaptar transferência/bloqueio de classificação sem alterar a ordem atual. Verificar em duas conexões a leitura corrente e a concorrência com transferência/publicação, com rollback após falha e sem identity map obsoleto; documentar a ordem de aquisição preservada.

## 3. Versões e elegibilidade editorial

- [x] 3.1 Migrar lock de Questão e histórico de versões para as routines do inventário, preservando entidades gerenciadas e guards. Verificar publicação/replay/arquivamento com revisão, motivo e imutabilidade atuais e ausência de commit interno; documentar os caminhos administrativos.
- [x] 3.2 Migrar elegibilidade individual, listagem e lotes de versões elegíveis/históricas, ajustando somente serialização dos adaptadores de leitura quando necessário. Verificar paginação vazia/total, JSON de IDs vazio/repetido, filtros, versões antigas após retirada e ausência de gabarito no Aluno/DOM; documentar a distinção entre disponibilidade e histórico e manter pares de Plano reservados à 015.

## 4. Instalação e integração documental

- [x] 4.1 Concluir `013_catalogo_editorial_procedures.sql` e bootstrap equivalente e integrar reconhecimento/preflight até 013, com assinaturas/corpos/segurança oficiais. Verificar instalação vazia, upgrade 012 → 013 com dados, baseline/restauração, recursos ausentes/alterados, idempotência e preservação de prefixos/checksums anteriores; documentar pré-condições, privilégios e compensação.
- [x] 4.2 Atualizar README, documento SQL técnico e matrizes acadêmica/CRUD com o recorte real e caminhos ponta a ponta. Verificar links, correspondência método/procedure/Controller/Service/tela, vinte funcionalidades sem renumeração e pendências das próximas etapas sem promessa de aprovação acadêmica.

## 5. Verificação integrada

- [x] 5.1 Executar regressões afetadas (`test_catalogo_admin_integration.py`, `test_materias_integration.py`, `test_assuntos_integration.py`, `test_questoes_versionadas_integration.py` e início de Práticas/Simulados/Plano.), as 29 integrações originais e suíte ampliada MySQL, gates de arquitetura, cobertura existente e E2E conforme conventions. Verificar contratos/metadata/guards/rollback e registrar comandos e resultados reais em `validacao.md`; não reduzir gates, substituir banco por mocks ou declarar sucesso se MySQL estiver indisponível.
- [x] 5.2 Executar `openspec validate adequar-catalogo-editorial-a-procedures --strict`, `git diff --check` e revisão de escopo/segredos/hashes. Verificar preservação de alterações externas, migrations antigas, procedure legada, visuais e dados, sem DDL no banco de uso por efeito colateral.

## Continuidade do workflow

- Verificar a implementação, sincronizar os dois deltas e arquivar somente sem tarefas pendentes ou achados críticos.
- Aplicar a próxima etapa apenas depois da dependência concluída; não executar as changes em paralelo.
- Commit, push, AWS, uso real e envio ao Classroom dependem de instrução própria.
