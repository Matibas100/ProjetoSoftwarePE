# Validação — Dashboards e desempenho real

Data: 24/10/2026. Change: `dashboards-desempenho-real`, schema `spec-driven`.

## Evidências por requisito

| Requisito | Implementação e evidência |
| --- | --- |
| Fatos concluídos | Projeções públicas dos Repositories de práticas/simulados e classificação histórica de Questões. Integração compara identidade de resposta/atividade, usuário, instante, correção e classificação com os Services predecessores; replay, repetições reais, branco e em andamento exercitados. |
| Fórmula e amostra | Agregação MySQL por totais, cálculo único de percentual e DTO comum. Zero/null, amostra 4/5, média ponderada e contagens por origem conferidos contra fixture real. |
| Período e histórico | Padrão 30 dias, máximo 366, limites UTC semiabertos, validação estrita e relógio fixo. Grupos por IDs, ordem determinística e rótulo recente; transferência real com nova publicação preserva fatos anteriores e separa o mesmo Assunto nas Matérias históricas. |
| Snapshot e consumo interno | ContextoLeitura próprio somente leitura, REPEATABLE READ e snapshot consistente. Resposta confirmada em outra conexão durante consulta não entra nos agregados/atividades. Contexto externo mantém relógio e transação, inclusive em falha de diagnóstico; rollback pertence ao chamador. Escrita no contexto próprio é recusada pelo MySQL; falha libera conexão. |
| APIs privadas | Três GETs com sessão/perfil e no-store; sem usuário alvo. Atividades próprias, período igual ao diagnóstico, até cinco por tentativa, ordem/desempate e simulado totalmente branco. 400/401/403, vazio, erro 500 sem payload parcial e isolamento A/B exercitados. |
| Contagens administrativas | Contratos públicos de contagem por módulo, estados atuais, vazio e inserção concorrente durante leitura, sem informações individuais. Catálogo/Questões/simulados/finalizadas usam a mesma visão consistente. |
| Interface | Início, desempenho e dashboard administrativo com APIs reais. DOM cobre base/período, amostras, tabelas, links, ausência de percentual fictício, recarga conjunta, remoção dos valores anteriores, sessão/identidade e descarte de respostas/erros atrasados. |

Testes específicos: `backend/tests/test_desempenho_integration.py`,
`backend/tests/unit/test_desempenho.py` e `frontend/tests/desempenho.test.js`.
Os runners existentes mantêm autenticação, catálogo, Questões, práticas,
simulados e os 29 cenários originais como regressão. Sem SQLite ou mocks nas
integrações. Falhas controladas usam eventos de execução sobre MySQL real.

## Demonstração e inspeção visual

Navegador isolado e schema MySQL descartável. Duas práticas (A/B) e um simulado
finalizado (A/B/branco) produziram quatro respostas, dois acertos, dois erros,
base `{pratica:2,simulado:2}`, 50% e amostra pequena no início do Aluno.
Uma nova prática respondida corretamente atualizou, após recarga, geral,
Matéria e Assunto para cinco respostas, três acertos, dois erros, 60% e dados
disponíveis. A comparação do resultado persistido do simulado antes/depois
retornou igualdade integral; nenhuma correção foi recalculada.

Tela de desempenho apresentou a mesma base. Período explícito sem respostas
retornou listas vazias e percentual indisponível. Rede offline retirou valores
anteriores e colocou todos os blocos em erro com nova tentativa, mantendo
navegação. Retorno aos últimos 30 dias por Enter recuperou os dados juntos.
O dashboard administrativo mostrou contagens reais de catálogo, três Questões
publicadas, um simulado publicado e uma tentativa finalizada, sem alunos.

Início, desempenho e administração inspecionados em 1440 px contra
ALU-DASH-001, ALU-DES-001 e ADM-DASH-001 (páginas 9, 22 e 28 do Protótipo),
com moldura, ativos e hierarquia existentes, foco visível e sem overflow
horizontal ou sobreposição. Tabelas possuem região com foco para rolagem.
Horário de cálculo e período exibidos explicitamente em UTC. Nenhum binário
oficial foi alterado; plano, redação, tutor e recomendações continuam
indisponíveis, sem dados fictícios.

## Operação

Sem nova tabela, índice ou migration nesta change. Última migration continua
sendo a 008 de simulados. Nenhum upgrade no banco operacional; implantação de
simulados continua sujeita ao guia `operacao-simulados.md`. Reversão dos
dashboards retira consumidores sem alterar fatos. Destinos de login preservados.
Sem commit, push ou merge; alterações locais legítimas anteriores preservadas.

## Validações e fechamento

| Comando | Resultado final |
| --- | --- |
| `python backend/tests/run_backend_coverage.py` | 115 unitários e 101 integrações MySQL aprovados, sem skips; linhas 96,91% (3170/3271), branches 90,39% (743/822). |
| `npm run test:coverage` | 110 testes em 12 arquivos aprovados; linhas 99,15% (1631/1645), branches 87,64% (1071/1222), conforme validador agregado. |
| `openspec validate dashboards-desempenho-real --strict` | Aprovado. |
| `openspec validate --specs` | Oito capacidades aprovadas, sem erros; somente sugestões informativas sobre extensão de requisitos. |
| `git diff --check` | Sem erros de whitespace. |

Os dois stacks superam linhas ≥90% e branches ≥85%, sem arquivo executável
zerado. Opt-ins MySQL ficaram somente nos processos. Vitest foi executado
com autorização fora do sandbox devido ao bloqueio de subprocessos EPERM.
As fixtures de transferência obtêm a prévia de impacto, usam o contrato vigente
do catálogo e exigem sucesso da operação; a regressão final exercita a
transferência efetiva, a nova publicação e os grupos históricos distintos.

## Verificação

| Dimensão | Resultado |
| --- | --- |
| Completude | 10/10 tarefas e os cinco requisitos do delta representados. |
| Correção | Fórmulas, períodos, classificação histórica, amostra, isolamento, consistência transacional, erros e interface conferidos com as evidências acima. |
| Coerência | Camadas existentes, contratos públicos entre módulos, conexão/snapshot no contexto de infraestrutura e ausência de novo schema preservados. |

Nenhum achado CRÍTICO ou AVISO pendente. Capacidade `desempenho-real` apta
à sincronização integral e arquivamento; nenhuma condição especificada foi
reduzida ou substituída por dados fictícios.

Os cinco requisitos foram sincronizados integralmente em
`openspec/specs/desempenho-real/spec.md`, com Purpose preservado e sem cabeçalhos
de operação de delta. Comparação dos blocos confirmou igualdade antes do
arquivamento. Servidores e abas de demonstração encerrados; schema descartável
e arquivos temporários de autenticação removidos.
