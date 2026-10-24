# Validação — Prática de Questões com histórico

Data: 23/10/2026. Change: `pratica-questoes-com-historico`; schema: `spec-driven`.

## Verificação OpenSpec

| Dimensão | Resultado |
| --- | --- |
| Completude | 13/13 tarefas concluídas; requisitos dos dois deltas implementados, verificados e sincronizados; change arquivada. |
| Correção | Seleção segura, início/correção idempotentes, histórico, autorização, concorrência e rollback exercitados no MySQL real; interface exercitada por DOM e navegador. |
| Coerência | Camadas existentes, Services de conteúdo do item 2, TransactionManager, ADRs 001/002/003/005/006 e recorte ALU-QUE-001/002/003 preservados. |

Nenhum achado CRÍTICO ou AVISO pendente. A implementação está apta ao fechamento.

## Evidências por requisito

| Requisito | Implementação e evidência |
| --- | --- |
| Seleção segura | `ListarQuestoesAlunoService`, projeção elegível no Repository de Questões, Controller e rota; testes de filtros, paginação, ordenação, catálogo inativo, vazio, 400/401/403 e ausência de gabarito/explicação. |
| Tentativa vinculada à versão | Migration/Model de tentativas e `IniciarPraticaService`; UUID normalizado, UNIQUE por dono, replay após retirada, chave divergente, versão superada, repetição real e duas requisições concorrentes. |
| Correção persistida | `ResponderPraticaService`, lock por dono e TransactionManager; A–E, entrada extra/inválida, acerto/erro, explicação nula, replay, conflito e falha de flush real com rollback. |
| Histórico estável | Services de detalhe/histórico/fatos e Repository; coleção/detalhe de A/B, ordenação/paginação/filtro, ausência de em andamento, limites temporais e snapshot após nova publicação/transferência/renomeação/arquivamento. |
| Autorização | Middleware `/api/aluno/*` separado de administração; matriz de todas as rotas, gabarito legado bloqueado, HEAD/404/405, CSRF/Origin e no-store; regressão completa de autenticação. |
| Interface recuperável | Seleção, resolução/correção, histórico e links no início; testes DOM de falha, reload, alternativa preservada, chave estável, recuperação sem replay automático, identidade antes/depois de consultas e ao voltar de outra aba, respostas atrasadas, limpeza e ausência de storage. |
| Schema e operação | Upgrade 006→007, instalação limpa, reexecução, fingerprint/baseline de todos os prefixos, checks/UNIQUE/FKs RESTRICT e equivalência integral de colunas/bootstrap; documento operacional com implantação, backup/compensação e contratos. |

Testes específicos: `backend/tests/test_praticas_integration.py`,
`test_praticas_migration_integration.py`, `unit/test_praticas.py` e
`frontend/tests/aluno-praticas.test.js`. As suites existentes de autenticação,
migrations e registro de rotas foram atualizadas para os novos contratos;
os 29 cenários originais permanecem preservados.

## Comandos e resultados finais

| Comando | Resultado |
| --- | --- |
| `python backend/tests/run_unit.py` | 109 testes aprovados, sem carregar `.env` ou conectar ao banco. |
| `python backend/tests/run_backend_coverage.py` | 109 unitários e 77 integrações aprovados, sem skips; linhas 96,25% (2437/2532), branches 88,77% (593/668). |
| `npm run test:coverage` | 81 testes em 10 arquivos aprovados; linhas 98,97% (1249/1262), branches 87,37% (664/760), conforme validador agregado. |
| `openspec validate pratica-questoes-com-historico --strict` | Aprovado. |
| `openspec validate --specs` | Seis capacidades aprovadas, sem erros; somente sugestões informativas sobre extensão de requisitos. |
| `git diff --check` | Sem erros de whitespace. |

Ambas as camadas superam linhas ≥90% e branches ≥85%; nenhum arquivo
executável ficou sem cobertura. As integrações usam MySQL 8 real e os opt-ins
`RUN_MYSQL_INTEGRATION=1` e `RUN_MYSQL_MIGRATION_INTEGRATION=1` somente no
processo. Não foi usado SQLite nem substituição de integrações por mocks.
As falhas controladas de gravação usam eventos do ORM sobre o MySQL real.

O Vitest inicialmente encontrou `spawn EPERM` no sandbox; as execuções finais
foram autorizadas e realizadas fora dele. Falhas intermediárias em fixtures
de teste foram corrigidas; os números acima correspondem às execuções finais.

## Demonstração e inspeção visual

Navegador isolado, API/servidor locais e schema descartável. Seleção iniciou
tentativa real; execução ofereceu cinco radios sem correção antecipada.
Seleção por Space e envio por Tab/Enter salvaram resposta incorreta B contra
gabarito A, com foco em `pratica-feedback` e explicação explicitamente
indisponível. Logout retornou 204; novo login 200; detalhe retornou exatamente
o mesmo JSON de correção e histórico apresentou a tentativa uma única vez.
O isolamento de outra conta foi demonstrado nos testes HTTP/MySQL.

Seleção, execução, resultado e histórico inspecionados com largura interna
de 1440 px, sem overflow horizontal, contra as páginas 10–13 do Protótipo e
fluxo de Questões do Handoff. Moldura, filtros, cartões, alternativas, foco e
mensagens seguem o recorte individual aprovado, sem sequência, recomendações,
cronômetro ou números fictícios. Links de entrada no início foram conferidos
no DOM e navegador. Artefatos visuais oficiais não foram alterados.

## Limites operacionais

Nenhum upgrade foi executado no banco operacional. Antes de disponibilizar
as telas, aplicar a migration 007 pelo runner após backup e verificações de
`docs/technical/operacao-praticas.md`. Os servidores de demonstração e o schema
temporário são encerrados/removidos ao terminar a validação. Sem commit, push
ou merge; alterações locais anteriores preservadas.

## Sincronização

Capacidade `pratica-questoes` criada com os cinco requisitos do delta.
Requisito de autorização de `autenticacao-escolar` atualizado com os dois
cenários novos, preservando todos os cenários existentes, Purpose e demais
requisitos. Comparação dos blocos confirmou correspondência integral com os
dois deltas antes do arquivamento; nenhuma operação de delta permaneceu nas
specs principais.

Arquivada pelo CLI em `2026-10-23-pratica-questoes-com-historico`, com
`--skip-specs` somente porque o merge e sua verificação já estavam concluídos.
Servidores encerrados e schema descartável removido com sucesso.
