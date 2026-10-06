# Validação do catálogo acadêmico administrativo

Validação realizada em 6 de outubro de 2026, antes da sincronização e do arquivamento.

| Dimensão | Resultado |
| --- | --- |
| Completude | 36 tarefas concluídas; requisitos das duas capabilities representados na implementação e nos testes. |
| Correção | Testes unitários, integração MySQL, cobertura e fluxos reais no Chrome aprovados. |
| Coerência | Camadas, transações, migrations SQL e contratos seguem o design e os ADRs; MVP e artefatos oficiais preservados. |

## Banco e preservação

O erro HTTP 500 inicial decorria do banco local ainda no schema anterior ao catálogo. Foi criado um backup completo, restaurado em um schema MySQL descartável e validado antes do upgrade do banco original. O baseline reconheceu `002`; as migrations `003` e `004` foram aplicadas após auditoria sem pendências.

O banco original manteve IDs, campos legados, contagens e vínculos de Matéria, Assunto e Questão. As operações visuais de escrita utilizaram exclusivamente cópias MySQL descartáveis, sem mocks ou SQLite.

Backup local, ignorado pelo Git: `instance/backups/catalogo-20261006-094922/antes-catalogo.sql`. SHA-256: `57f0b5e2f94694fcbdeb680c617ab0e281c64900b9ed1827ec697a996f2226de`.

## Testes executados

| Validação | Resultado |
| --- | --- |
| `python backend/tests/run_unit.py` | 96 testes aprovados. |
| `python backend/tests/run_backend_coverage.py`, com ambos os opt-ins MySQL | 96 unitários e 46 integrações aprovados, incluindo a regressão original. |
| Cobertura backend | 94,58% de linhas; 85,81% de branches. |
| `npm run test:coverage` | 7 arquivos, 30 testes aprovados. |
| Cobertura frontend | 98,80% de linhas; 86,61% de branches, conforme relatório V8. |
| `openspec validate evoluir-catalogo-academico-administrativo --strict` | Change válida. |

Os limites agregados de 90% de linhas e 85% de branches foram atendidos nas duas stacks. Foram usados os comandos equivalentes aos alvos Make documentados.

## Comparação visual e comportamento

Referências: Protótipo Desktop FINAL, páginas 29 e 30; Handoff Mestre, navegação administrativa, componentes, modais e alertas; Inventário Mestre, ADM-CON-001/002; e `docs/design/desktop-v1/ERRATA.md`.

As telas foram inspecionadas no Chrome em **1440 × 1496 px**, com fontes locais carregadas. Foram ajustados logo oficial, tipografia Noto Sans, ícones, sidebar, header, hierarquia, proporção dos painéis, espaçamentos, contraste, foco e menus. Nenhum artefato congelado foi alterado.

Foram exercitados menus sem recorte ou rolagem horizontal, bloqueios de exclusão com contagens reais, duplicidade com valores preservados, filtros sem resultado, catálogo vazio, carregamento, falha de rede e recuperação. A transferência real exibiu origem/destino/impacto, preservou questões e só ocorreu após confirmação. Tab permaneceu dentro do modal; Escape cancelou sem transferir e devolveu foco ao disparador. O descarte também preservou os valores quando cancelado.

Diferenças contextuais previstas no design: dados e identidade locais; estados exibidos somente quando aplicáveis; contagens reais; Resumos como `—`; e seletor de Matéria com origem/destino explícitos na prévia. Alvos de 44 px podem aumentar a altura das linhas em relação à prancha ilustrativa.

Capturas em [validacao-visual](validacao-visual/): telas base, menu, erro preservado, confirmação de transferência, falha de rede e estados vazios. Foram obtidas pelo Chrome DevTools Protocol em uma instância de QA; as APIs de escrita apontavam para um backend com MySQL descartável.

## Auditoria e achados

Lighthouse 13.4.1, modo snapshot, desktop, nas duas telas: **Acessibilidade 100**, **Boas práticas 100** e **Agentic Browsing 100**. O rótulo acessível do menu foi corrigido mesmo quando o achado não reduzia a pontuação. Resumo dos relatórios em [lighthouse.json](validacao-visual/lighthouse.json).

- **CRÍTICO:** nenhum achado pendente.
- **SUGESTÃO:** adicionar meta description se estas páginas internas precisarem de indexação. SEO 80; única auditoria reprovada restante, sem impacto nos fluxos administrativos.

A verificação aprovou a sincronização e o arquivamento. Nenhum commit, push ou merge foi realizado.

## Encerramento

As specs principais `catalogo-academico` (8 requisitos) e `gestao-administrativa-conteudo` (6 requisitos) foram sincronizadas antes do archive. Seus requisitos e cenários foram comparados integralmente com os deltas; `openspec validate --specs --strict` aprovou as três specs principais, incluindo `migrations-sql` preservada.

A change foi arquivada pelo CLI em `openspec/changes/archive/2026-10-06-evoluir-catalogo-academico-administrativo/`. Foi usado `--skip-specs` somente porque a sincronização já havia sido realizada e validada. As cópias MySQL e a instância Chrome de QA foram encerradas; o backup foi mantido.
