# Validação — Simulado fixo com resultado

Data: 24/10/2026. Change: `simulado-fixo-com-resultado`, schema `spec-driven`.

## Evidências por requisito

| Requisito | Implementação e evidência |
| --- | --- |
| Composição revisada | Services administrativos, Controller e rotas; título, ordem, paginação, limite 1–180, repetição de identidade, versões inelegíveis, revisão obsoleta, publicação/arquivamento idempotentes e eventos atômicos exercitados no MySQL. |
| Persistência | Migration 008 e bootstrap equivalentes, sete Models, FKs RESTRICT, posições/Questões únicas, UUID por dono e marcador gerado de tentativa em andamento. Integrações verificam instalação limpa, upgrade 007, reexecução, baseline, drift e constraints reais. |
| Tentativa própria | Catálogo sem gabarito, início/retomada com concorrência e replay; conteúdo superado/retirado impede novos usos e preserva tentativa existente. |
| Respostas e conclusão | Salvar/alterar/limpar com revisão e lock da tentativa. Finalização corrige e persiste tudo em um commit, inclusive brancos. Falha controlada da última gravação reverte correções e totais; salvar versus finalizar concorrentes não sobrescrevem revisão. |
| Histórico e fatos | Resultado/correção próprios, 404 uniforme, 409 antes de concluir, estabilidade após transferência/arquivamento e novo login. Contrato interno exclui brancos/em andamento e mantém usuário, resposta, atividade, instante e classificação histórica, sem criar práticas. |
| Autorização | Matriz HTTP de todas as rotas, 401/403, CSRF/Origin, reautenticação, HEAD e no-store inclusive em negação. Regressão dos 29 cenários originais e autenticação/catálogo/Questões/práticas preservada. |
| Interface | Gestão, composição ordenada, catálogo/histórico, execução, resultado e correção. DOM cobre seleção, falha, contexto, chave estável, recarga, descarte de dados atrasados, troca de conta, proteção de alterações e confirmação sem replay automático. Sessão administrativa também é conferida ao retornar à aba. |

## Demonstração real e visual

Navegador isolado, API/servidor locais e schema MySQL descartável. No Admin,
cadastrei uma composição de três Questões, salvei o rascunho e publiquei com
motivo e confirmação por Tab/Enter. O catálogo do Aluno mostrou essa versão.
Iniciei uma tentativa e salvei B na primeira Questão e A na segunda, deixando
a terceira em branco. A segunda resposta foi salva por Space/Tab/Enter.
Confirmação informou um branco e a finalização por teclado retornou:

```json
{"total":3,"respondidas":2,"acertos":1,"erros":1,"em_branco":1,"percentual_acerto":33.33}
```

Recarregar preservou os mesmos totais e instante. Correção mostrou B versus
gabarito A, explicação indisponível explícita, radios desabilitados e mapa com
incorreta/correta/branco. Conteúdo e correção vêm da API, não do navegador.

Gestão, editor, catálogo, execução, resultado e correção inspecionados contra
as referências ADM-SIM-001/002 e ALU-SIM-001/002/003/004 em viewport de 1440 px.
Sem overflow horizontal, cortes ou sobreposição no viewport. O recorte manual
não ativa cronômetro, geradores, TRI ou recomendações futuras. Fonte oficial
Desktop V1 preservada. O bloqueio inicial do DevTools foi resolvido na nova
tentativa; o fluxo final foi inspecionado por esse conector.

## Comandos e resultados

| Comando | Resultado final |
| --- | --- |
| `python backend/tests/run_backend_coverage.py` | 112 unitários e 90 integrações MySQL aprovados, sem skips; linhas 96,73% (2954/3054), branches 89,97% (700/778). |
| `npm run test:coverage` | 99 testes em 11 arquivos aprovados; linhas 99,10% (1546/1560), branches 87,04% (1001/1150). |
| Regressão dirigida de autorização | 12 integrações MySQL aprovadas após reforço de no-store. |
| `openspec validate simulado-fixo-com-resultado --strict` | Aprovado. |
| `openspec validate --specs` | Sete capacidades aprovadas, sem erros; somente sugestões informativas sobre extensão de requisitos. |
| `git diff --check` | Sem erros de whitespace. |

Não se usou SQLite nem mocks em integrações; dados são criados/limpos em
schemas descartáveis, opt-ins somente no processo. O Vitest exigiu execução
autorizada fora do sandbox devido a `spawn EPERM`. A falha inicial do teste
adicional de CHECK era a classe de exceção esperada pela fixture; o MySQL
efetivamente recusou a posição inválida. A fixture foi corrigida e a execução
completa final passou. Os números acima correspondem às execuções finais.

## Verificação e sincronização

| Dimensão | Resultado |
| --- | --- |
| Completude | 13/13 tarefas e sete requisitos dos dois deltas representados. |
| Correção | Cenários funcionais, concorrência, rollback, privacidade e recuperação exercitados com as evidências acima. |
| Coerência | Services/Controllers sem SQL ou db.session, CRUD participante nas Models, consultas/locks nos Repositories, TransactionManager e ADRs 001/002/003/005/006 preservados. |

Nenhum achado CRÍTICO ou AVISO pendente. Capacidade `simulados-fixos` criada e
requisito de gestão mínima de Simulados acrescentado à capacidade administrativa,
preservando todos os requisitos anteriores. Comparação integral dos blocos
confirmou correspondência dos dois deltas antes do arquivamento.

## Operação e compatibilidade

Nenhum upgrade no banco operacional. Implantação requer backup e migration
008 pelo runner, conforme `docs/technical/operacao-simulados.md`. Destinos de
login preservados. Nenhum commit, push ou merge; alterações locais anteriores
preservadas. O fingerprint de DDL MySQL 8 tem o limite de representação
documentado no guia operacional e recusa drift em vez de adotá-lo cegamente.
