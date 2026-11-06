# Design: validação de Plano e Simulado pelo navegador

## Context

Motivação e limites em [proposal.md](proposal.md). O E2E atual contém um teste com vinte passos numerados e regressões adicionais. Ele termina com capturas de um Aluno sem Plano; inserir uma geração no meio alteraria essas premissas. As specs principais de Plano, Simulados e Desempenho já definem todos os comportamentos a verificar.

`scripts/run_e2e.py` prepara schema MySQL isolado, aplica migrations oficiais, cria somente o operador e inicia API/frontend separados. A configuração Playwright descobre `frontend/e2e/**/*.spec.js`, usa um worker e desabilita traces/vídeo. A CI já executa esse runner. Não é necessário mudar infraestrutura, API ou aplicação.

Este design resolve previamente a massa de dados, a observação independente de persistência e os limites de cada evidência. O roteiro abaixo é de teste automatizado, não material de apresentação.

## Goals / Non-Goals

**Goals:** comprovar ações reais na interface com resultados verificáveis; manter o teste adicional independente dos vinte casos; tornar contagens e fórmulas explícitas; reutilizar infraestrutura sem novas abstrações de produção.

**Non-Goals:** provar novamente todos os casos de concorrência, falha de commit e privacidade já cobertos em integração; simular respostas da API; alterar regras para facilitar o teste; obter garantia de nota ou definir implantação AWS.

## Decisions

### 1. Um arquivo e um teste adicional independente

Criar `frontend/e2e/plano-simulado.spec.js` com um único `test` e passos descritivos. Preservar integralmente `entrega-academica.spec.js`, seus vinte números e as capturas de ausência de plano. Manter `playwright.config.js`, CI, runner, pacotes e lockfile.

O novo arquivo deve passar sozinho via runner e junto ao teste anterior, em qualquer ordem. Usar guard equivalente ao existente para `RUN_MYSQL_E2E`, formato do schema e URLs E2E. Criar nomes e e-mail próprios com sufixo aleatório; não reutilizar a conta `E2E_STUDENT_EMAIL` como cadastro, nem depender de IDs/ordem criados por outro teste. Senha sintética pode vir do ambiente E2E, sem registro no relatório. Separar contextos autenticados de Administrador e Aluno e fechá-los em `finally`.

Pequenos helpers privados para login, ação seguida de resposta e consulta são suficientes. Duplicação curta nesses helpers é preferível, neste recorte, a extrair um framework compartilhado e alterar a suíte validada. Nenhuma classe genérica, page object ou camada nova é necessária.

### 2. Preparação pelo fluxo público existente

Administrador entra pela tela com credenciais sintéticas fornecidas pelo runner. Pela interface cria uma Matéria, um Assunto e três Questões distintas com gabarito A; publica as Questões e cria/publica um Simulado na ordem dessas três versões. Identificar conteúdo pelo sufixo próprio e usar filtros/paginação reais se necessário, sem assumir posição global do catálogo.

Aluno é cadastrado e autenticado pela interface. `addInitScript` pode configurar apenas `window.ENEM_API_URL`, como no teste existente. Não injetar sessão, plano, respostas, relógio, permissões ou resultados. As mutações principais e o setup acadêmico passam por cliques/formulários; somente o operador inicial continua sendo preparado pelo runner.

Login administrativo recente atende à publicação; não desativar reautenticação ou CSRF. Se surgir expiração, usar a recuperação real em vez de mudar configurações de produção.

### 3. Massa pequena e expectativas explícitas

Todas as respostas pertencem ao mesmo Assunto ativo, com versões elegíveis. A sequência escolhida permite conferir os cálculos sem fixtures grandes:

| Etapa | Fatos persistidos do Aluno | Resultado esperado |
| --- | --- | --- |
| Quatro práticas concluídas | Duas respostas A e duas B | Quatro respostas, 50%; gerar Plano retorna 200 `sem_base_suficiente`, sem Plano salvo |
| Quinta prática, resposta B | Duas corretas e três erradas | Cinco respostas, 40%; gerar Plano retorna 201, geração 1, um item com snapshot 2/5 |
| Concluir manualmente o item | Mesmas cinco respostas | Estado/data de conclusão persistidos; diagnóstico continua 2/5 |
| Salvar Simulado sem finalizar | Primeiro item A, segundo B, terceiro em branco | Tentativa em andamento; diagnóstico continua 2/5 e correção não é antecipada |
| Finalizar Simulado | Um acerto, um erro e um branco | Resultado total 3, respondidas 2, acertos 1, erros 1, branco 1, percentual 33,33% |
| Consultar diagnóstico | Cinco práticas e duas respostas do Simulado | Sete respostas, três acertos e quatro erros, 42,86%; base `{pratica:5,simulado:2}` |
| Consultar Plano sem recalcular | Mesmo Plano da geração 1 | Snapshot continua 2/5 e item concluído, embora o diagnóstico já seja 3/7 |
| Confirmar recálculo | Nova geração a partir dos sete fatos | 201, geração 2 com ID diferente, item pendente e snapshot 3/7 = 42,86%; geração 1 preservada |

Cada prática deve ser uma tentativa real iniciada/respondida pela interface. Repetir a mesma Questão em tentativas distintas conta, conforme a spec; reenviar a mesma resposta não forma a amostra. Não arredondar percentuais esperados a inteiros nem confundir as três Questões do resultado com as duas respostas que entram no diagnóstico.

### 4. Observar a interface e depois confirmar persistência

Antes de cada mutação, registrar `waitForResponse` filtrando método e caminho, acionar a tela e conferir status/payload. Em endpoints que redirecionam após sucesso, evitar ler o corpo no instante da navegação: obter o ID pela URL e confirmar por GET autenticado. Usar locators e esperas de estado; não usar sleeps fixos, `force`, aumentar timeouts/retries ou chamar funções internas da aplicação para executar os casos.

- **Plano:** `plano-gerar`, lista, metadados e status devem refletir os estados reais. Após a geração, recarregar e comparar ID, geração, item e snapshot com GET `/api/aluno/plano`. Concluir pelo botão do item e confirmar estado/data após recarga; comparar somente campos acadêmicos do diagnóstico, sem exigir igualdade de `calculado_em`.
- **Simulado:** salvar cada alternativa pelo formulário, recarregar e confirmar escolhas; manter terceiro item em branco. Conferir ausência de gabarito no detalhe em andamento. Abrir confirmação, conferir um branco, cancelar e verificar que nenhum POST de finalização ocorreu e o estado permanece em andamento. Reabrir/confirmar, verificar 200, totais, foco no resultado e permanência após recarga/GET. Acessar correção pela tela e conferir gabaritos/resultado dos itens e bloqueio de edição.
- **Recálculo:** consultar Plano após a finalização e demonstrar snapshot antigo preservado. Abrir/cancelar diálogo sem POST e sem troca do Plano; depois confirmar e verificar nova geração/novos números após recarga. Eventuais contadores de requests são apenas observação, nunca interceptação/mocking.

Para observar os planos anteriores, a API pública não oferece uma rota de histórico. Usar **uma verificação auxiliar explícita de replay**, separada do percurso de usuário: capturar o corpo original da geração 1, e, após a geração 2, reenviá-lo uma vez pelo `apiRequest` HTTP real com o mesmo usuário/CSRF. Não invocar `PlanoUI.mutate` ou alterar estado JS. O contrato retorna 200 com geração 1, `atual:false`, snapshot e conclusão originais; um GET posterior deve continuar retornando geração 2. Esse POST técnico reutiliza a chave da ação original, não prepara massa nem gera outra ação avaliada. Identificá-lo no passo como verificação de histórico/replay, sem anunciar que foi feito por botão. Sem SQL direto ou endpoint de teste.

Capturar apenas os campos necessários para assertivas. Nunca anexar cookies, tokens, corpo de login/cadastro, senha, estado autenticado, HAR ou traces. Os dois contextos devem permanecer isolados; não guardar tokens em arquivos.

### 5. Documentação das atividades e evidências

Editar somente os trechos relacionados de README e `docs/technical/entrega-academica.md`, com link relativo para o novo teste. Preservar matriz/numeração dos vinte casos e links existentes. Distinguir:

- **Atividade anterior:** pelo menos vinte funcionalidades completas, demonstração em vídeo obrigatória com limite informado de cinco minutos e demais itens do enunciado já compartilhado.
- **Rubrica final recebida:** demonstração de até dois minutos por vídeo ou execução hospedada, pelo menos quatro funcionalidades principais não CRUD; não exige mostrar todas as vinte. Slides continuam exigidos nessa rubrica, mas sua criação não entra nesta change.

Não declarar que um documento substitui ou dispensa o outro, nem impor prazo/cronograma do regulamento de 2025 à turma de 2026. A rubrica é a fonte do critério final; não prometer que consultas/listagens isoladas contam como uma das quatro funções. O teste evidencia funcionamento e não substitui a demonstração do grupo.

Atualizar a descrição do E2E para distinguir **dois testes Playwright** de **vinte casos numerados no primeiro**, com percurso adicional no segundo. Não transformar passos auxiliares em novas funcionalidades ou alterar nomes históricos dos relatórios anteriores. Não copiar os materiais externos do professor para o repositório.

### 6. Execução e registro proporcionais

No apply, registrar baseline dos arquivos locais em `test-results/plano-simulado/`, ignorado, antes de editar os três arquivos previstos. Relatar as mudanças preexistentes sem confundi-las com o delta desta change. Preservar `tmp/`, specs, arquivos anteriores, demais changes e visuais oficiais.

1. `npm run test:e2e:list`: conferir descoberta dos dois testes, sem apresentá-la como prova de execução.
2. Executar **a suíte E2E inteira** pelo runner oficial: `RUN_MYSQL_E2E=1` somente no processo e configuração MySQL no ambiente. No PowerShell, definir/remover o opt-in com `try/finally`. Não ler `.env` ou imprimir configuração. Aproveitar configuração já fornecida pelo ambiente; ausência de acesso impede declarar aprovação.
3. Para investigar falha isolada, usar o próprio `executar_suite` do runner com comando Playwright filtrado para `frontend/e2e/plano-simulado.spec.js`, mantendo o schema descartável e todas as proteções. Nunca chamar o Playwright contra banco operacional ou contornar guard.
4. Verificar resultado dos dois testes, UI/payloads, remoção do schema e encerramento dos processos. Usar relatórios locais para inspeção, sem publicar detalhes sensíveis.
5. Conferir links/numeração, `git diff --check` no escopo, hashes de preservação e `openspec validate validar-fluxos-de-plano-e-simulado --strict`. Revisar implementação com a skill de verificação e consolidar comandos/resultados reais em `validacao.md`.

Sem mudança de lógica de produção, não é necessário repetir cobertura completa e todas as integrações apenas para este delta. As integrações anteriores continuam evidência histórica de concorrência/rollback; o novo E2E não deve alegar testar falha de commit por observar apenas o caminho de sucesso. Se uma falha indicar defeito de produto, registrar evidência e interromper a tarefa afetada para uma proposta de correção, preservando esta delimitação.

## Risks / Trade-offs

- **Dependência de MySQL/Chromium local:** usar preflight do runner; distinguir bloqueio de infraestrutura de falha funcional. Nenhum fallback para SQLite ou mocks.
- **Interferência entre testes:** conta e conteúdo exclusivos, contextos fechados, locators por identidade da fixture e verificação isolada quando necessário; limpeza central do schema em `finally`.
- **Amostra insuficiente ou mistura de origens:** cinco práticas reais antes do Plano; assertivas explícitas da tabela, com um branco fora do diagnóstico.
- **Suite maior ou instável:** massa de apenas três Questões e cinco práticas, esperas por eventos/DOM e configuração existente. Não afrouxar asserts/gates para obter verde.
- **Virada do dia UTC:** comparar métricas, identidades e snapshots pertinentes, não timestamp calculado em requisições diferentes; a massa criada na execução permanece no período padrão.
- **Replay auxiliar confundido com percurso de usuário:** rotular como oracle de histórico, reaproveitar corpo/chave capturados e conferir que o atual permanece geração 2.
- **Complexidade para a banca:** acréscimo fica no teste; código de produção mantém as decisões aprovadas. Não acrescentar frameworks ou refatorar camadas por estética.

## Migration Plan

Nenhuma migration, mudança de procedure, contrato, segredo ou deploy. No apply, acrescentar o arquivo de teste e revisar os dois documentos; a descoberta/CI existente o inclui automaticamente. Se for necessário desfazer este delta, remover somente o novo teste e reverter os trechos documentais identificados pelo baseline, preservando o trabalho anterior. Sincronização de specs não aplicável; arquivar somente após verificação sem achados críticos. Publicação, AWS e material de estudo continuam fora deste fluxo.
