# Validação — Plano básico por desempenho

Data: 24/10/2026. Change `plano-basico-por-desempenho`, schema `spec-driven`.

## Evidências

| Requisito | Implementação e validação |
| --- | --- |
| Seleção determinística | `SelecionarPlanoService` chama o diagnóstico existente com contexto/relógio externos. Frações exatas, empate por total/ID, limite três, fronteira 4/5, 100%, período e snapshot cobertos por unitários e MySQL real. Integração gera prioridades 2/10, 1/5 e 4/10; exclui amostra 0/4 e mantém somente três. Nova resposta muda a ordenação apenas após recálculo. |
| Catálogo e disponibilidade | Consulta especializada em `QuestaoRepository` verifica publicação atual, catálogo ativo e vínculo histórico/atual. Transferência real exclui dificuldade antiga; publicação na nova classificação e novas práticas permitem nova base. Arquivamento retira prática sem apagar justificativa/conclusão. |
| Persistência e migrations | Migration 009, snapshot equivalente e Models com eventos de imutabilidade. Instalação vazia, upgrade de 008, reexecução, todos os baselines 000–009, fingerprint/drift, FKs RESTRICT, posição/Assunto/geração/chave únicos, um atual por usuário e histórico preservado validados no MySQL 8.0.44. |
| Geração e consulta | GET não grava. POST 201, replay 200, UUID/operação divergente 409, plano atual já existente 409 e ausência de candidatos sem plano vazio. Duas gerações concorrentes com mesma chave dão 201/200; chaves distintas dão 201/409. |
| Transação e diagnóstico | Mesmo contexto `REPEATABLE READ` e instante fixo; resposta confirmada em outra conexão durante agregação não entra no snapshot do plano. Falhas reais na última inclusão e na consulta de diagnóstico retornam 500, sem dados internos, sem plano parcial ou perda de conclusões. Sem fallback para ausência de base. |
| Propriedade e HTTP | Rotas privadas, sessão/perfil/CSRF/Origin/no-store; 400 para campos extras/UUID/ID/confirmação/filtros, 401 anônimo, 403 Administrador/CSRF/Origin e 404 idêntico para item ausente/alheio. Identidade vem da sessão. |
| Conclusão | Primeira conclusão salva UTC; replay mantém data. Diagnóstico/respostas não mudam. Model impede adulterar snapshot/data e excluir histórico, inclusive após expiração/releitura de atributos ORM. Item histórico dá 409. |
| Recálculo | Confirmação com ID atual, geração sequencial, replay antigo, chave divergente e prévia obsoleta; disputa com mesmo ID anterior dá 201/409. Falta de candidatos/falha preserva plano atual/conclusões; histórico anterior continua consultável pelo replay autorizado. |
| Interface | Lista em ALU-PLA-001, link no início, gerar/iniciar/concluir/recalcular, explicação e datas reais, disponibilidade e base insuficiente. Fluxo de Questões recebe/preseleciona Assunto e recusa filtro inválido/retirado sem ampliar silenciosamente a seleção. |
| Sessão e acessibilidade | DOM cobre falhas de rede/consulta, recuperação da mesma conta sem replay, UUID/corpo pendentes, bloqueio de outra ação incerta, troca de identidade e respostas/erros atrasados. Botão dedicado recupera geração/conclusão com resposta perdida mesmo após consulta ocultar o botão original. Diálogo por teclado, Escape/cancelar e foco devolvido; status anunciado. Sem storage acadêmico. |

Testes específicos: `backend/tests/unit/test_planos.py`,
`backend/tests/test_planos_integration.py`,
`backend/tests/test_planos_migration_integration.py`,
`frontend/tests/aluno-plano.test.js` e cenário contextual em
`frontend/tests/aluno-praticas.test.js`.

## Demonstração no navegador

Contexto de navegador isolado, frontend em 5500, API em 5000 e schema MySQL
descartável criado pelo suporte de integração. Conta exclusiva da fixture.
Três Assuntos com 1/5, 4/10 e 2/5 produziram plano nessa ordem; os dois com 40%
desempataram pela maior amostra. Tela inspecionada em 1440 px contra a página 23
do Protótipo Desktop V1: moldura, identidade, cartões, hierarquia e foco visível,
sem overflow horizontal, sobreposição ou texto cortado. Nenhum binário mudou.

O link da primeira prioridade abriu Questões com `assunto_id=2` selecionado e
somente uma Questão elegível. A tentativa 21 foi iniciada/resolvida pelo fluxo
real; resposta A recebeu correção correta persistida. Voltando ao plano, seu
snapshot continuou em 1/5, provando ausência de recálculo automático.

Conclusão manual marcou o item da geração 1. Escape no diálogo cancelou e
devolveu foco para Recalcular; Enter/Tab/Enter confirmou nova geração. Geração
2 apresentou 2/6, 4/10 e 2/5, todos pendentes. Consulta MySQL confirmou geração
1 histórica, seu item ainda concluído e data original preservada; somente a
geração 2 permaneceu atual. Rede offline durante consulta manteve os três itens
visíveis e informou erro. Nova consulta explícita após reconexão recuperou o
plano, sem mutação automática.

## Comandos e resultados

Opt-ins MySQL definidos somente no processo, removidos ao terminar. Runners
criaram/limparam seus schemas e dados temporários. Sem SQLite ou mocks nas
integrações; falhas injetadas por eventos SQLAlchemy sobre MySQL real.

| Comando | Resultado |
| --- | --- |
| `python backend/tests/run_unit.py` | 118 testes aprovados; runner desabilita dotenv e usa configuração unitária sem MySQL. |
| `npm run test:unit -- frontend/tests/aluno-plano.test.js frontend/tests/aluno-praticas.test.js` | 31 testes focados aprovados. |
| `python backend/tests/run_backend_coverage.py` com `RUN_MYSQL_INTEGRATION=1` e `RUN_MYSQL_MIGRATION_INTEGRATION=1` | 118 unitários e 112 integrações aprovados, incluindo 29 cenários originais, regressões anteriores, migrations e equivalência do bootstrap. Linhas 97,11% (3431/3533), branches 90,91% (800/880). |
| `python -m coverage run --append backend/tests/run_unit.py`, `python -m coverage json`, `python scripts/validate_backend_coverage.py` | Ajuste final de singular/plural da justificativa validado; mesma cobertura agregada aprovada. |
| `npm run test:coverage` | 127 testes em 13 arquivos aprovados. Linhas 99,19% (1724/1738), branches 87,90% (1170/1331). Novo script com 100% das linhas e 90% dos branches. |
| `openspec validate plano-basico-por-desempenho --strict` | Change válida. |
| `git diff --check` | Sem erros de whitespace. Avisos de conversão LF/CRLF do checkout, sem mudança de política. |

O Vitest precisou executar subprocessos fora do sandbox após `spawn EPERM`;
execução autorizada pelo mecanismo de aprovação. O ambiente jsdom também emite
aviso conhecido de navegação entre documentos; testes aprovados, navegação real
conferida separadamente no navegador. A exportação de screenshot pelo DevTools
não aceitou o caminho local; inspeção realizada diretamente pela imagem retornada.

## Verificação e fechamento

| Dimensão | Resultado |
| --- | --- |
| Completude | Todos os cinco requisitos e cenários representados; implementação, operação, regressão e demonstração concluídas. |
| Correção | Seleção, transações, replay, privacidade, sessão e histórico validados pelos testes e demonstração acima. |
| Coerência | Camadas/ADRs preservados, CRUD nas Models, diagnóstico único, escopo sem agenda/IA; sem alterações nos contratos predecessores. |

Sem achados críticos ou avisos de comportamento pendentes. Sincronização cria
somente a capability `plano-estudos-basico`, com cinco requisitos; nenhuma outra
spec precisa mudar. Fechamento segue verify → sync → archive da tarefa 5.2.

`openspec validate --specs --strict` confirma a sincronização de todas as specs.
O conteúdo dos cinco requisitos/cenários foi comparado integralmente com o delta;
Purpose preservado na nova spec principal, sem cabeçalhos de operação delta.

Arquivo realizado pelo CLI com `openspec archive plano-basico-por-desempenho
--yes --skip-specs --json`, após sync manual já validado. Destino:
`openspec/changes/archive/2026-10-24-plano-basico-por-desempenho`.
Conferência final: 13/13 tarefas, metadados preservados e igualdade integral dos
cinco requisitos/cenários com a spec principal. Ambiente de demonstração encerrado,
schema descartável removido e credenciais temporárias apagadas.

Migration validada em schemas descartáveis; aplicar no banco da aplicação é
etapa operacional de implantação, descrita no documento de operação. Nenhuma
gravação de demonstração foi feita nesse banco. Sem commit, push ou merge.
