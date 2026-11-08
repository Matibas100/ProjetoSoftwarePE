# Tarefas

## 1. Caracterização e proteção do estado atual

- [x] 1.1 Registrar em `validacao.md` o estado inicial, alterações externas e hashes das migrations 000–010, da procedure legada e dos contratos protegidos; conferir inventário C01–C06 e dependências. Verificar que a documentação da change `formalizar-modelagem-e-cobertura-crud` é preservada, sem incluir `.env`, credenciais ou dados pessoais reais nas evidências.
- [x] 1.2 Acrescentar caracterização MySQL com fixtures sintéticas para as seis rotas antes da substituição: campos/nulos/datas, buscas e filtros combinados, ordenação, totais, página vazia e grande, fatos históricos, amostras e autorização. Verificar as expectativas contra a implementação atual e registrar os comandos/resultados, sem manter consultas ORM alternativas no código de produção.

## 2. Infraestrutura participante e contratos SQL

- [x] 2.1 Implementar o helper neutro de cursor/resultados em `app/core/procedures_mysql.py` e a operação participante em `ContextoLeitura`, conforme design. Verificar com unitários parâmetros vinculados, conjunto útil vazio, múltiplos resultados, drenagem/close em erro e ausência de commit/rollback/close da conexão emprestada; documentar o contrato no módulo e validar com uma procedure sintética em MySQL real a sequência CALL → nova consulta na mesma conexão.
- [x] 2.2 Criar ADR-011 e iniciar `docs/technical/consultas-academicas-mysql.md` com o recorte, proprietários, assinaturas, views, segurança do invocador e fronteiras transacionais. Verificar coerência com ADRs 001/006/008/010 e manter o gate de arquitetura: nenhum CALL/driver/SQL em Controller ou Service, nenhum import privado cruzado e nenhuma Model nova.

## 3. Listagens administrativas e migration 011

- [x] 3.1 Criar `011_consultas_admin_procedures.sql` com as quatro routines previstas, pré-condições, preservação e compensação; acrescentar o mesmo bloco ao bootstrap e testes de instalação parcial até 011 em schema descartável. Verificar assinaturas, SQL estático, privilégios do invocador, resultados úteis, validações de SQL direto e manutenção dos hashes 000–010; atualizar no documento técnico o contrato de 011.
- [x] 3.2 Migrar `CatalogoRepository.listar_materias_admin` e `ConsultaMateriasMySQL` para `sp_materias_admin`, preservando o Protocol e o Service. Verificar caracterização e integrações de C01: filtros/LIKE, contagens DISTINCT, datas/nulos, página fora do intervalo e parâmetros acima de 2^31; documentar o caminho HTTP → procedure.
- [x] 3.3 Migrar `CatalogoRepository.listar_assuntos_admin` e `ConsultaAssuntosMySQL` para `sp_assuntos_admin`, preservando o Protocol e o Service. Verificar C02 com classificação/contagens, busca/ordenação normalizada, filtros e paginação, inclusive o campo `resumos: null` já acrescentado pelo Service; documentar o caminho correspondente.
- [x] 3.4 Migrar `QuestaoRepository.listar_admin` para `sp_questoes_admin` e ajustar apenas a serialização interna de `ListarQuestoesAdminService` para registros independentes do ORM. Verificar C03 com todas as combinações de filtros, busca literal de curingas/aspas/barras, classificação relacionada, revisão/versão, paginação e ausência de lazy loading; manter os contratos das telas de Questões e do banco de composição de Simulados e documentar o novo caminho.

## 4. Fatos históricos e migration 012

- [x] 4.1 Criar `012_desempenho_procedures.sql` e o bloco equivalente no bootstrap com quatro views e três routines, na ordem do inventário; documentar pré-condições e compensação. Verificar em MySQL real que views reproduzem os fatos atuais após transferência/renomeação/arquivamento, Simulados em branco viram apenas atividades e nenhuma tabela, registro, FK ou Model foi alterada; completar os contratos de origem no ADR/documento técnico.
- [x] 4.2 Migrar `DesempenhoRepository.agregar` e seu adaptador para `sp_desempenho_resumo`, mantendo o Service de diagnóstico e o contrato usado pelo Plano. Verificar C04 contra caracterização com duas identidades, origens distintas, replay/repetição, brancos, limites UTC, microssegundos, grupos históricos, desempates e amostras 0/4/5; documentar os três resultados úteis e os cálculos que continuam no Service.
- [x] 4.3 Migrar `DesempenhoRepository.atividades` para `sp_atividades_recentes` e as funções de contagem de Conteúdo/Simulados para as routines dos proprietários, preservando APIs públicas e a composição administrativa. Verificar C05/C06 com cinco atividades ordenadas, Simulado em branco, contagens zero/reais, formatos, autorização, no-store e falha integral de qualquer procedure; documentar quais chamadas cada dashboard utiliza.
- [x] 4.4 Acrescentar regressões MySQL de concorrência e participação: nova resposta entre blocos não entra no snapshot corrente; diagnóstico na geração/recalculo do Plano usa conexão/instante externos e não confirma uma escrita antes de falha posterior. Verificar rollback real e reaproveitamento da conexão/pool após chamadas múltiplas e erros, incluindo conjunto útil vazio; registrar evidências e limitações reais em `validacao.md`.

## 5. Reconhecimento, instalação e operação

- [x] 5.1 Acrescentar reconhecimento conservador dos recursos SQL de 011/012 em infraestrutura pequena e integrar ao detector existente, distinguindo views de base tables. Verificar unitários e integrações de assinatura/corpo/segurança/dependências/colunas, recursos incompletos ou alterados, metadados insuficientes e schema externo, sem aceitar prefixo inferior para esconder divergência; documentar os critérios novos sem relaxar 000–010.
- [x] 5.2 Atualizar testes de migrations/portabilidade e o preflight de integração para o conjunto atual, preservando expectativas históricas explícitas. Verificar instalação vazia, upgrade 010 → 011 → 012 com dados, baseline exato de 011/012, restauração equivalente, equivalência bootstrap/migrations e segunda atualização sem pendências; manter bloqueios de drift, RUNNING/FAILED e concorrência e registrar os comandos seguros de upgrade/recuperação.

## 6. Integração e fechamento do recorte

- [x] 6.1 Integrar o documento técnico ao README e à matriz acadêmica, atualizando referências da matriz CRUD quando disponível. Verificar links, rotas reais, sete procedures/quatro views e a lista de vinte funcionalidades sem renumeração ou acréscimo artificial; declarar as consultas especializadas ainda pendentes e não afirmar adequação integral, envio acadêmico ou aprovação do professor.
- [x] 6.2 Executar os gates existentes de arquitetura, unitários, integrações MySQL afetadas e completas (incluindo as 29 originais), cobertura backend/frontend e E2E de regressão conforme conventions. Verificar os contratos das seis telas/rotas e os fluxos existentes de Plano/Simulados/privacidade; registrar comandos/resultados reais no `validacao.md`, sem baixar limites de cobertura, substituir integrações por mocks/SQLite ou declarar sucesso se MySQL estiver indisponível.
- [x] 6.3 Executar `openspec validate adequar-consultas-academicas-a-procedures --strict`, `git diff --check` e revisão final de escopo, dados/segredos, hashes e artefatos congelados. Verificar que apenas superfícies previstas foram alteradas, mudanças externas foram preservadas, migrations antigas/procedure legada permanecem e nenhuma migration foi aplicada ao banco de uso como efeito colateral.

## Continuidade do workflow

- Verificar implementação contra os artefatos, sincronizar os dois deltas e arquivar pela skill correspondente somente após conclusão e ausência de achados críticos.
- Retomar o inventário de consultas restantes em próximas explorações/changes; este recorte não fecha toda a exigência de acesso especializado.
- Commit, push, deploy AWS e envio acadêmico ficam fora desta change e dependem de instrução própria.
