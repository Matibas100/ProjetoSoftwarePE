# Tasks — Corrigir respostas nulas e revisar a entrega

## 1. Cliente da API e sua regressão

- [x] 1.1 Reler os artefatos e os dez arquivos principais delimitados no design; registrar em `validacao.md` o estado Git e uma referência do conteúdo atual, preservando alterações anteriores. Conservar cópias temporárias dos HTMLs/README em diretório ignorado e obter a referência visual sintética antes da formatação; verificar que nenhuma referência depende apenas de `HEAD` e que não contém dados reais, credenciais ou sessão exportada.
- [x] 1.2 Acrescentar testes em `frontend/tests/api.test.js` para JSON raiz `null` em HTTP 200/201 e 400/401/403/409/500, demonstrar a falha atual e ajustar `frontend/js/api.js` antes do acesso aos campos. Verificar com `npm run test:unit -- frontend/tests/api.test.js` os envelopes/mensagens/status previstos, objetos/listas com nulos internos, HTTP 204 sem leitura do corpo e regressões de JSON ilegível, sem validar novos tipos de payload nem alterar endpoints.
- [x] 1.3 Cobrir no mesmo teste o bootstrap CSRF nulo compartilhado entre duas mutações e a resposta nula após um POST com token válido; verificar apenas uma consulta inicial, nenhum POST dependente no bootstrap inválido, nova tentativa explícita possível, nenhum retry/evento de recuperação inferido e token válido preservado após POST já enviado. Executar a suíte direcionada e registrar os resultados/cenários no relatório desta change.

## 2. HTML administrativo legível

- [x] 2.1 Formatar `frontend/admin/materias.html` e `assuntos.html`, um arquivo por vez, preservando o contrato e whitespace significativo definidos no design; verificar comparação DOM com as cópias atuais, contratos/fluxos existentes de `frontend/tests/admin-pages.test.js` e navegação. Conferir antes/depois a 1440/390 px com dados sintéticos e registrar ausência de alteração visual/comportamental.
- [x] 2.2 Formatar `frontend/admin/dashboard.html`, `questoes.html` e `questao.html`, um arquivo por vez; verificar DOM/atributos/conteúdo, ordem dos scripts e suítes existentes relacionadas a desempenho/Questões, incluindo `frontend/tests/admin-questoes.test.js`. Conferir antes/depois a 1440/390 px, preservando formulários, foco, modais e espaços de texto; registrar os resultados sem criar testes que apenas espelhem a formatação.
- [x] 2.3 Formatar `frontend/admin/simulados.html` e `simulado.html`, um arquivo por vez; verificar comparação DOM, contratos/DOM existentes de Simulados e navegação, além da conferência visual 1440/390 px. Confirmar que conteúdo/ordem dos controles, scripts, avisos e estados permanecem iguais; documentar o resultado no relatório.

## 3. README coerente com a implementação

- [x] 3.1 Corrigir apenas os trechos atuais do README sobre 21 Models, cadeia de capacidades de persistência e migrations até 010/000–010; verificar contra Models, diretório de migrations, diagrama e ADR-008. Conferir links e lista intacta das vinte funcionalidades, preservando seções/evidências históricas e todas as alterações locais anteriores, sem executar banco nem modificar essas fontes.

## 4. Validação integrada

- [x] 4.1 Executar `npm run test:coverage`, comprovando os gates frontend de 90% linhas/85% branches e nenhum arquivo executável sem cobertura. Executar uma vez o E2E existente com `RUN_MYSQL_E2E=1` somente no processo e MySQL descartável por ambiente; registrar os três percursos reais, limpeza do schema e eventuais limitações. Não substituir integração por mocks, não usar banco operacional nem produzir outro vídeo.
- [x] 4.2 Executar validação estrita desta change e das specs principais, confrontar todos os cenários do delta com os testes e revisar o diff incremental contra o baseline atual. Confirmar apenas os dez arquivos previstos mais artefatos desta change, sem segredo, alteração de CSS/backend/SQL/HTML legal/dependência ou perda das mudanças anteriores; concluir `validacao.md` com comandos, resultados e conferência DOM/visual real.

## Workflow follow-up

- Verificar a implementação com `openspec-verify-change`, sincronizar somente o delta de `cliente-api-frontend` e arquivar após as tarefas e verificações concluídas.
- Vídeo, AWS, estudo/apresentação, commit, push e merge permanecem fora desta change.
