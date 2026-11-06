# Operação de desempenho e dashboards

## Origem e denominadores

Leitura derivada, sem tabelas de métricas, migration ou escrita nos resultados.
`PraticaRepository.projecao_desempenho` fornece uma linha por prática respondida;
`SimuladoRepository.projecao_desempenho`, uma por resposta não branca de tentativa
finalizada. A classificação do simulado usa a projeção histórica pública de
Questões; nenhum consumidor consulta tabelas internas fora dessas fronteiras.

Cada projeção recebe usuário e intervalo obrigatórios e fornece
`{tipo,id,atividade_id,usuario_id,ocorrido_em,correta,materia_id,materia_nome,assunto_id,assunto_nome}`.
Identidade `(tipo,id)` é estável: replay não cria fatos; novas tentativas contam
novamente. `atividade_id` é a tentativa de destino. Práticas usam respondida_em;
simulados usam finalizada_em. Ambos os instantes são UTC. Os testes comparam
essas projeções aos contratos dos Services de origem por identidade, instante,
correção e classificação.

Desempenho: `total_respostas = acertos + erros`,
`percentual_acerto = round(100 * acertos / total_respostas, 2)`.
Agregados somam totais, sem média de percentuais. Exemplo: práticas 0/2 e
simulado 1/1 respondida resultam em 1/3 = 33,33%, não 50%. Já o resultado de um
simulado de três Questões com acerto/erro/branco divide por **três**: 33,33%.
As mesmas duas respostas contribuem 1/2 = 50% para desempenho. Esses exemplos
são exercitados com dados temporários no MySQL real.

Zero respostas retorna percentual null e `sem_dados`; 1–4, `amostra_pequena`;
cinco ou mais, `dados_disponiveis`. O limiar 5 é operacional para este MVP,
não significância estatística, domínio, tendência ou nota prevista. OD-17 geral
continua aberta. Grupos sem respostas não são fabricados com percentual zero.

Agrupamento preserva IDs históricos: Matéria por materia_id; Assunto pelo par
materia_id/assunto_id. Nome vem do fato mais recente no período, desempate por
tipo e ID decrescentes. Transferir/renomear/arquivar catálogo não reclassifica
respostas anteriores. Contagens por origem aparecem em `base` no diagnóstico
e em cada métrica; sua soma sempre equivale ao total de respostas respectivo.

## Período e snapshot

`inicio` e `fim`, juntos, em YYYY-MM-DD inclusivo: 1–366 dias, início ≤ fim e
fim ≤ dia UTC atual. Ausentes: últimos 30 dias incluindo hoje UTC. Converter
para intervalo semiaberto `[início 00:00, dia após fim 00:00)` UTC. Repetições,
filtros desconhecidos e entradas inválidas retornam 400 antes da agregação.

`ContextoLeitura` abre uma conexão dedicada, transação somente leitura em
REPEATABLE READ com snapshot consistente e relógio fixado uma vez. Todas as
consultas de uma resposta usam essa conexão; fechar o contexto próprio libera
a conexão inclusive em falha, sem commit na sessão de autenticação. Não usar
TransactionManager de escrita nem fallback para leituras independentes.

Contrato interno: `ConsultarDesempenhoService.executar(usuario_id, filtros,
contexto, instante)`. O usuário deve vir de consumidor autorizado. A
infraestrutura do [Plano básico já implementado](operacao-plano-estudos.md)
constrói `ContextoLeitura(conexao, instante)` sobre conexão com
transação/snapshot REPEATABLE READ já aberta e
passar esse contexto ativo ao Service. Relógio divergente, contexto encerrado,
isolamento incorreto ou ausência de transação produzem erro. Diagnóstico não
abre outra conexão nem confirma/reverte a transação recebida; falhas propagam
ao proprietário, que decide rollback. Nenhuma sessão ou SQL fica no Service.

## APIs

Sessão/perfil no servidor e Cache-Control no-store, inclusive em negação.
GET não exige CSRF. Nenhum endpoint aceita usuario_id alvo do cliente.

| Endpoint GET | Conteúdo |
| --- | --- |
| `/api/aluno/desempenho?inicio=2026-10-01&fim=2026-10-23` | periodo `{inicio,fim,timezone}`, calculado_em, limiar_amostra, base, geral, materias e assuntos |
| `/api/aluno/dashboard` | desempenho com o mesmo DTO e ultimas_atividades do mesmo período |
| `/api/admin/dashboard` | calculado_em, catalogo, questoes, simulados e tentativas_simulado_finalizadas; sem filtros |

Métrica: `{total_respostas,acertos,erros,percentual_acerto,estado_amostra,base}`;
linhas acrescentam IDs/nomes aplicáveis. Matérias por ID; Assuntos por
Matéria/Assunto. Conta vazia tem base `{pratica:0,simulado:0}`, geral com zero
contagens e percentual null, listas vazias.

Atividade: `{tipo,id,ocorrido_em,titulo,url}`; até cinco tentativas próprias,
instante/tipo/ID decrescentes, simulado antes de prática no empate. URLs:
`/aluno/questao.html?tentativa_id=<id>` e
`/aluno/simulado.html?tentativa_id=<id>`. Um simulado todo branco pode aparecer
uma vez como atividade, contribuindo zero respostas. Atividades não são a
quantidade de respostas. Destino continua validando propriedade.

Admin conta estados atuais globais: `catalogo:{materias_ativas,assuntos_ativos}`,
`questoes:{rascunhos,publicadas,arquivadas}`,
`simulados:{rascunhos,publicados,arquivados}` e total de tentativas finalizadas.
Não fornece aluno, e-mail, alternativas ou histórico individual. Publicado
não promete elegibilidade de todo o conteúdo.

Sem sessão: 401; perfil diferente: 403; filtros inválidos: 400. Falha em qualquer
consulta retorna 500 no envelope `{erro:...}` existente, sem sucesso parcial,
SQL, detalhes internos ou números substitutos.

## Interface e limites

Início `/aluno/inicio.html`, `/aluno/desempenho.html` e `/admin/dashboard.html`
usam APIs reais; destinos de login preservados. Cada bloco indica carregamento,
vazio, amostra pequena ou erro. Blocos do mesmo endpoint recarregam juntos.
Recarga/troca de período remove dados anteriores; respostas atrasadas de outra
geração/identidade não preenchem a tela. Troca de conta limpa dados privados;
recuperar sessão não repete mutações. Navegação continua acessível durante erro.
O [Plano básico de prioridades para prática](operacao-plano-estudos.md) está
disponível. Agenda, duração/reagendamento, redação, tutor, TRI, tendência e
recomendações avançadas permanecem indisponíveis, sem números fictícios.
Sem storage de respostas ou diagnóstico.

Consultas são limitadas por usuário/período e agregadas no MySQL com os índices
existentes. Materialização, índices novos ou cache persistente exigem outra
change. Reversão remove consumidores novos sem alterar fatos ou correções.


Composição SOLID: diagnóstico recebe ConsultaMetricasDesempenho e EscoposLeitura.
Dashboard do Aluno recebe DiagnosticoAluno, ConsultaAtividadesAluno e os mesmos escopos;
reutiliza contexto/relógio com até cinco atividades. Dashboard administrativo recebe apenas
ConsultaContagensAdmin e escopos, sem dados individuais. Factory fornece instâncias por
aplicação, sem usuário/conexão capturados. O contexto externo do plano não é encerrado
pelo diagnóstico; falhas preservam a fronteira de rollback do caso composto.
