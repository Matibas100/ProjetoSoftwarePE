# Validação: documentar fluxos acadêmicos

## Preflight — 06/11/2026

Change `documentar-fluxos-academicos`, schema `spec-driven`, estado inicial
`ready`, 0/9 tarefas concluídas; `specs` deliberadamente dispensadas por
`skip_specs: true`. Lidos proposal, design, tasks, AGENTS.md, as cinco
conventions, architecture-master-v1 e ADRs 002, 005, 006 e 008.

O working tree já continha alterações e arquivos não rastreados das entregas
acadêmica/SOLID, frontend/backend, testes, documentação e outras changes.
`git status --short` e hashes SHA-256 dos arquivos locais rastreados/não
ignorados foram capturados antes da primeira edição de produto em
`test-results/fluxos-academicos/baseline.json` (QA ignorado). Inclui `tmp/`,
histórico e os quatro binários oficiais; nenhum `.env` foi lido.

Escopo de produto/documentação: somente `docs/technical/fluxogramas-casos-de-uso.md`,
`README.md`, `docs/technical/entrega-academica.md`,
`docs/technical/operacao-desempenho.md`, `docs/technical/operacao-simulados.md`
e `frontend/aluno/desempenho.html`. Tasks e este relatório registram o workflow.
Sem reset, stash, commit, push, merge, mudança de backend, banco, contratos,
dependências, binários ou escrita no MySQL.

Conferidos os símbolos reais: `DesempenhoController.diagnostico`,
`servicos().desempenho`, `ConsultarDesempenhoService`, contratos/adaptadores,
`DesempenhoRepository.agregar`, projeções de Práticas/Simulados/Questões e
`ContextoLeitura`; `SimuladoController.finalizar`, `FinalizarSimuladoService`,
`propria`, `SimuladoRepository.propria/respostas`,
`ConsultarVersaoHistoricaService`, `QuestaoVersao`, `SimuladoResposta`,
`SimuladoTentativa` e `TransactionManager`. Também conferidos routes,
proteção HTTP, api.js, desempenho.js e aluno-simulados.js.

Ordem preservada: abrir escopo antes de validar período; replay antes de
comparar revisão; gravações Active Record com `confirmar=False`; commit
antes de devolver sucesso. Leitura não grava métricas, embora a infraestrutura
de autenticação possa renovar sessão. Nenhum conflito com o planejamento.

## Resultados executados

| Validação | Comando/procedimento | Resultado |
| --- | --- | --- |
| Regressão DOM após o ajuste final | `npm run test:unit -- frontend/tests/desempenho.test.js frontend/tests/navigation.test.js` | 2 arquivos, 27 testes aprovados; sem cobertura, 6,61 s |
| Renderização final SVG | `mmdc -p test-results/fluxos-academicos/puppeteer.json -i docs/technical/fluxogramas-casos-de-uso.md -o test-results/fluxos-academicos/fluxos.md -b white` | Dois blocos `flowchart` renderizados, sem erro de sintaxe |
| Renderização final PNG | Mesmo comando com `-o test-results/fluxos-academicos/fluxos.png --size 3600` | Dois PNGs: 1749×3600 e 1371×3600; inspecionados visualmente, inclusive recortes da finalização |
| Links relativos e âncoras | Checagem local com Python/pathlib/urllib nos cinco Markdown do escopo | 84 links válidos, nenhum destino/âncora ausente |
| Numeração oficial | Conferência das entradas do README e linhas da matriz | Vinte itens/linhas preservados; finalização identificada como caso adicional existente |
| Aviso HTML/DOM | JSDOM e comparação SHA-256 com baseline após reverter somente a frase em memória | Frase definida no design; restante do arquivo idêntico, três blocos, filtros, navegação e quatro scripts preservados |
| Preservação e escopo | Comparação SHA-256 dos 463 arquivos do baseline e inventário de novos arquivos | Exatamente seis arquivos de produto/documentação; tasks/relatório separados; zero alterações fora do escopo |
| Temporários e visuais oficiais | Mesma comparação | 65 arquivos de `tmp/`, quatro binários oficiais e histórico preservados |
| Whitespace do delta rastreado | `git diff --check -- README.md docs/technical/entrega-academica.md docs/technical/operacao-desempenho.md docs/technical/operacao-simulados.md frontend/aluno/desempenho.html` | Sem erros |

Mermaid CLI **12.2.0** já estava no cache local. Sua primeira chamada não
encontrou o Chrome esperado pelo Puppeteer; a configuração de QA passou a
apontar para o Chromium já instalado pelo Playwright. Não houve instalação ou
alteração de dependências. A opção antiga `-w` não existe nessa versão; o
comando final usa `--size`. Uma tentativa de substituição via pipe PowerShell
foi recusada por assert antes de editar o HTML por causa da codificação;
reexecutada com escapes Unicode, seguida da regressão final acima.

Inspeção visual: labels legíveis sem sobreposição/corte, início/fim,
decisões/setas direcionais, retorno à interface e Repository nos dois casos.
Saídas em `test-results/fluxos-academicos/`, ignoradas pelo Git, incluindo
`baseline.json`, `checagens.json`, `dom.json`, SVGs/PNGs e recortes de inspeção.
Os fontes permanentes são os dois Mermaid no documento técnico.

Revisão contra código e specs atuais de `desempenho-real`, `simulados-fixos`
e operação do Plano: 401/403; escopo antes do período/400; 500 sem payload
parcial; 200 `sem_dados`/percentual null; snapshot/limiar/renovação de sessão;
cancelar sem POST; corpo estrito/400; propriedade/404; replay antes da revisão;
revisão/409; branco sem correção; gabarito histórico; Models com flush e
commit único antes do sucesso; rollback na operação/commit; sem auditoria ou
reautenticação fictícias. Os avisos atuais distinguem Plano básico disponível
de agenda, TRI, geradores e recomendações avançadas indisponíveis.

Integrações MySQL e cobertura completa **não se aplicam**: nenhuma lógica,
contrato, schema, migration, procedure ou regra de persistência foi alterada.
Não foi executado backend nem comando que escrevesse no banco operacional.
Nenhuma evidência histórica foi apresentada como nova execução desta change.

## Verificação OpenSpec

Aplicada a skill `.agents/skills/openspec-verify-change/SKILL.md`, em modo
somente leitura durante a revisão. `openspec status` e `instructions apply`
confirmaram os três artefatos de contexto e o escopo local; contexto e
orientações foram considerados, sem conflito. A revisão começou com 8/9
tasks marcadas: a única restante era a própria consolidação/verificação 5.2,
encerrada pelo apply depois da revisão, sem mudança adicional de produto.

| Dimensão | Resultado e evidência |
| --- | --- |
| Completude | Os nove itens cobertos: preflight; [dois fluxos e rastreabilidade](../../../../docs/technical/fluxogramas-casos-de-uso.md); renderização; aviso/duas operações; README/matriz; validação consolidada. Nenhum delta funcional de spec requerido. |
| Correção | Caminhos confrontados com código/specs; replay antes da revisão e commit antes do 200; 27 testes DOM aprovados, 84 links válidos e HTML restrito à frase prevista. Evidências locais nas tabelas acima. |
| Coerência | Arquitetura/ADRs preservados, sem CRUD artificial em Repository, escrita de métricas, reautenticação ou evento fictício. Seis arquivos de produto/documentação, trabalho anterior e quatro binários preservados por SHA-256. |

`openspec validate documentar-fluxos-academicos --strict`: **aprovado**.
O CLI confirmou que `skip_specs` aceita zero deltas porque a change não
altera comportamento no nível de especificação.

**Achados:** zero críticos, zero avisos e nenhuma sugestão bloqueante.
**Resultado final:** 9/9 tarefas concluídas; arquivada em 06/11/2026 em
`openspec/changes/archive/2026-11-06-documentar-fluxos-academicos/`.
Sincronização de specs **não aplicável**, pois não existem deltas.
Antes da movimentação, a validação estrita foi novamente aprovada. O conteúdo
de todos os arquivos, incluindo `.openspec.yaml`, foi conferido por SHA-256
após a movimentação; este relatório recebeu apenas o registro de arquivamento
e o ajuste do link relativo para a nova profundidade.
Sem commit, push, merge ou envio externo.
