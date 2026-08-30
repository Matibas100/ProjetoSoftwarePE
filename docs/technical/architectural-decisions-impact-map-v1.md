# Mapa de impacto — Pacote de Decisões Arquiteturais 1

## Leitura do mapa

As entidades, migrations e APIs abaixo são conceitos de impacto, não itens aprovados para implementação. “Futura” significa que contrato, nome e estrutura ainda serão definidos após decisão formal.

## Status consolidado

| ADR | Status | Data da decisão |
|---|---|---|
| ADR-001 | **Aceito condicionalmente** — aguarda confirmação do professor | 2026-08-29 |
| ADR-002 | **Aceito** | 2026-08-29 |
| ADR-003 | **Aceito** | 2026-08-29 |
| ADR-004 | **Aceito** | 2026-08-29 |
| ADR-005 | **Aceito** | 2026-08-29 |
| ADR-006 | **Aceito** | 2026-08-29 |
| ADR-007 | **Aceito** | 2026-08-29 |

## Ordem de adoção

1. Migrations.
2. Fronteira de transações.
3. Exclusão e arquivamento.
4. Unicidade do catálogo.
5. Versionamento editorial.
6. Autenticação e sessões.
7. Mídias e armazenamento.

## Matriz consolidada

| ADR | Módulos afetados | Telas afetadas | Entidades futuras | Migrations futuras | APIs futuras | Testes necessários | Risco para o MVP | Acompanhamento pendente |
|---|---|---|---|---|---|---|---|---|
| ADR-001 | Todos os 15 módulos; núcleo de config/extensões | Todas indiretamente | Controle de revision e todas as entidades futuras | Baseline, schema relacional e SQL procedural versionado | Nenhuma rota específica; coordena disponibilidade de contratos | banco vazio, upgrade do MVP, downgrade/irreversibilidade, procedure e 29 regressões | Divergência entre `create_database.sql`, metadata e banco aplicado | **Professor:** confirmar Flask-Migrate/Alembic |
| ADR-002 | autenticacao, usuarios, autorizacao, auditoria; todos os protegidos | PUB-AUT-001–005, ALU-PER-001, ADM-USU-001/002, ADM-SEG-001 e demais telas autenticadas | usuário, credencial, sessão, token opaco, revogação, evento de segurança | Criação/backfill seguro das entidades e índices de expiração | login, logout, sessão, recuperação, revogação e reautenticação — contratos a definir | cookie, CSRF, CORS, expiração, revogação, perfis, XSS e enumeração | Bloqueio indevido ou quebra do frontend/29 testes se aplicado sem transição | Equipe: parâmetros operacionais e biblioteca |
| ADR-003 | catalogo_academico, questoes, resumos, praticas, simulados, auditoria | ADM-CON-001/002 e todos os selects/históricos dependentes | status de catálogo, referência/impacto e eventual registro de transferência | Remoção futura do cascade, introdução de arquivamento e FKs restritivas | impacto, arquivamento e transferência — contratos a definir; DELETE legado preservado | todos os cenários de vínculo, histórico, concorrência, 409 e regressão | Cascade atual pode apagar Assuntos; mudança precipitada pode quebrar limpeza/testes | Equipe: contratos e definição operacional de uso histórico |
| ADR-004 | catalogo_academico, importacoes, questoes, resumos, desempenho | ADM-CON-002; filtros e importações com Assunto | valor normalizado e identidade estável | saneamento, backfill e constraint composta | conflito em POST/PUT/importação sem URL nova definida | caixa, acento, espaços, Unicode, mudança de Matéria, arquivado e concorrência | Dados existentes podem colidir; collation pode divergir da regra | Equipe: relatório e resolução manual das colisões |
| ADR-005 | questoes, simulados, resumos, redacao, revisao_editorial, praticas, desempenho, auditoria | ALU-QUE-002/003, ALU-SIM-002–004, ALU-RES-002, ALU-RED-002–004; telas ADM editoriais | entidades lógicas e versões de Questão, Simulado, Resumo, Tema e Correção | tabelas de versão, backfill da Questão atual, FKs históricas | gestão/publicação/histórico; adaptadores para contratos legados | imutabilidade, concorrência, publicação, tentativa histórica, autoria, procedure e 29 regressões | Backfill ou troca de IDs pode quebrar procedure/API e dados atuais | Equipe: modelagem detalhada e plano de backfill |
| ADR-006 | Todos os módulos de escrita; núcleo transacional | Onboarding, práticas, simulados, redação, importações, revisão, permissões e auditoria | Unit of Work é infraestrutura; possível outbox/checkpoint depende de decisão futura própria | Ajustes só após contrato; nenhuma migration automática decorre do ADR | respostas atômicas, idempotência e jobs futuros — contratos a definir | rollback total, commit simples, locks, retry, idempotência e falha externa | Alterar `CrudMixin` sem compatibilidade quebraria os 29 testes | Equipe: contrato da abstração, sem biblioteca adicional definida |
| ADR-007 | questoes, resumos, redacao, importacoes, auditoria; núcleo de arquivos | ALU-QUE-002/003, ALU-RES-002, ALU-RED-002/003; ADM-QUE-002–009, ADM-RES-002/003, ADM-TEM-002–005 | arquivo/mídia, metadata, vínculo versionado, upload/checkpoint | metadata, vínculos e backfill apenas quando houver dados | upload/download/vínculo/arquivamento — contratos a definir | formato, MIME, tamanho, malware, hash, autorização, expiração e órfãos | Caminho local ou objeto mutável pode quebrar deploy e histórico | Equipe: provedor, limites e operação |

## Dependências entre decisões

```text
ADR-001 migrations
  ├── ADR-002 autenticação
  ├── ADR-003 exclusão ──> ADR-004 unicidade
  └── ADR-005 versões ──> ADR-006 transações
                         └─> ADR-007 mídias versionadas
```

- ADR-003 e ADR-005 convergem na regra de preservação de conteúdo já utilizado.
- ADR-004 depende da definição de arquivamento do ADR-003.
- ADR-005 precisa da atomicidade do ADR-006 para publicação e referências históricas.
- ADR-007 vincula a mídia à versão do conteúdo quando ela integra o material versionado.
- ADR-001 governa a aplicação futura de todas as mudanças, inclusive SQL específico do MySQL.

## Compatibilidade obrigatória

- `POST/GET/PUT/DELETE /api/materias` e `/api/assuntos` permanecem até evolução aprovada.
- `POST /api/questoes` e `GET /api/questoes/por-assunto` permanecem compatíveis durante backfill/versionamento.
- `sp_questoes_por_assunto` continua chamada exclusivamente pelo `QuestaoRepository`.
- Models existentes, `CrudMixin`, banco e 29 testes não são alterados por este pacote.
- Nenhuma migration listada neste mapa está criada ou autorizada.
