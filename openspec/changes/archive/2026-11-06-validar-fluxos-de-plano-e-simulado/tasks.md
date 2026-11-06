# Tarefas: validar Plano e Simulado pelo navegador

## 1. Preflight e cenário independente

- [x] 1.1 Ler proposta/design, AGENTS.md, conventions, specs de Plano/Simulados/Desempenho e decisões relevantes; conferir símbolos/seletores atuais. Registrar estado anterior e hashes em QA ignorado (`test-results/plano-simulado/`) e limites em `validacao.md`; verificar preservação das alterações legítimas, teste dos vinte casos, `tmp/`, specs e visuais oficiais, sem ler `.env` ou executar operações no banco operacional.
- [x] 1.2 Criar `frontend/e2e/plano-simulado.spec.js` com um teste adicional, guard do runner, helpers privados pequenos, identidade/conteúdo exclusivos e contextos fechados em `finally`. Preparar pela interface Matéria, Assunto, três Questões de gabarito A, publicação e Simulado fixo; cadastrar/autenticar Aluno próprio. Conferir a descoberta por `npm run test:e2e:list` e, no runner protegido, o preparo real sem dados do outro teste, mocks ou mutações diretas de setup acadêmico.

## 2. Geração do Plano e conclusão manual

- [x] 2.1 No novo teste, concluir quatro práticas reais (duas A/duas B), tentar gerar e verificar `sem_base_suficiente`, ausência de plano após GET/recarga e nenhuma criação vazia. Concluir quinta prática B, gerar pela tela e verificar 201, geração 1, um item com duas corretas em cinco respostas/40%, justificativa, ID e snapshot preservados após GET independente/recarga; conferir assertions em execução do cenário pelo runner.
- [x] 2.2 Concluir manualmente o item pela tela e verificar estado/data persistidos, diagnóstico ainda 2/5 e 40%, sem nova resposta ou afirmação de domínio. Manter o corpo original de geração em memória para a verificação auxiliar posterior e conferir comportamento pelo runner, sem registrar chave/cookies/credenciais no relatório.

## 3. Finalização de Simulado e atualização do diagnóstico

- [x] 3.1 Iniciar pela interface o Simulado próprio de três itens, salvar A no primeiro e B no segundo, manter o terceiro em branco e recarregar. Verificar escolhas persistidas, ausência de correção antecipada e diagnóstico ainda 2/5; abrir confirmação, conferir um branco, cancelar e comprovar zero POSTs de finalização e estado em andamento, com observação de requests e GET real.
- [x] 3.2 Confirmar finalização pela interface e verificar 200, foco, resultado com total 3/respondidas 2/acertos 1/erros 1/branco 1/33,33%, recarga/GET e correção dos três itens pela tela com edição bloqueada. Na tela/API de desempenho, verificar total 7/acertos 3/erros 4/42,86% e base prática 5/simulado 2, sem incluir o branco; executar essas assertivas pelo runner.

## 4. Recálculo e histórico preservado

- [x] 4.1 Consultar o Plano pela interface após finalizar o Simulado e verificar geração 1 concluída/snapshot 2/5 preservados. Cancelar recálculo sem POST/troca; confirmar depois e verificar 201, ID novo/geração 2, item pendente e snapshot 3/7/42,86%, persistidos após recarga/GET. Conferir a sequência pelo runner sem alterar contratos ou estado interno da tela.
- [x] 4.2 Acrescentar passo explicitamente auxiliar de verificação de histórico: repetir uma vez pelo `apiRequest` HTTP real o corpo/chave originais da geração 1, após criar geração 2. Verificar 200, geração 1 `atual:false`, snapshot/conclusão originais e GET atual ainda geração 2. Identificar no teste e na evidência que esse replay técnico não foi acionado por botão e não substitui geração/recálculo feitos pela interface; confirmar execução real sem SQL direto ou endpoint de teste.

## 5. Documentação dos critérios e da evidência

- [x] 5.1 Atualizar somente os trechos pertinentes de README e `docs/technical/entrega-academica.md`, ligando o novo arquivo de teste e distinguindo dois testes Playwright dos vinte casos numerados do primeiro. Separar exigências da atividade anterior (vinte funcionalidades/vídeo até cinco minutos) e rubrica final (quatro ações principais não CRUD/demonstração até dois minutos, vídeo ou execução hospedada), sem presumir dispensa/substituição, criar roteiro ou garantir nota. Conferir links relativos, lista/matriz de vinte itens e preservação dos relatórios históricos.

## 6. Verificação integrada

- [x] 6.1 Executar a suíte E2E completa pelo runner oficial com MySQL 8 real, configuração no ambiente e `RUN_MYSQL_E2E=1` somente no processo. Verificar aprovação dos dois testes, preservação dos vinte percursos anteriores, ausência de mocks/fallback, encerramento dos processos e remoção do schema descartável. Consolidar comandos, resultados e limitações reais em `validacao.md`; falha funcional que demande código de produção deve ser documentada para proposta própria, sem marcar aprovação ou ampliar escopo.
- [x] 6.2 Aplicar `openspec-verify-change` e executar `openspec validate validar-fluxos-de-plano-e-simulado --strict`; conferir links, whitespace e hashes contra o baseline. Verificar delta restrito aos três arquivos previstos e artefatos desta change, sem mudanças em backend, frontend de produção, runner, configuração, dependências, CI, banco, specs ou visuais. Registrar achados e resolver problemas do teste/documentação antes de fechar; não atribuir à nova execução provas de rollback/concorrência que pertencem a integrações históricas.

## Workflow follow-up

- Sincronização de specs não aplicável: `skip_specs: true`, sem deltas funcionais.
- Arquivar pela skill apropriada somente após as tarefas e a verificação, sem achados críticos.
- Commit/push/merge, AWS, apresentação, roteiro, vídeo, guia de estudo e envio da atividade permanecem fora desta change.
