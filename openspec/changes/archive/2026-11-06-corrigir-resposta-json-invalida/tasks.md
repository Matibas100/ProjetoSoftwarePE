# Tarefas: corrigir resposta JSON inválida

## 1. Preflight após a limpeza

- [x] 1.1 Confirmar encerramento/verificação da change de legibilidade e ausência de apply concorrente; ler proposta, design, spec do cliente, AGENTS.md, conventions e requisitos de autenticação pertinentes. Registrar baseline fresco dos arquivos não sensíveis em `test-results/json-invalido/` e contexto em `validacao.md`, preservando todos os deltas anteriores, migrations, changes, `tmp/` e visuais oficiais. Não abrir/expor `.env` ou escrever no banco operacional.

## 2. Interpretação previsível da resposta

- [x] 2.1 Ajustar somente a leitura JSON em `frontend/js/api.js` conforme a tabela do design, preservando fetch/status 0, retorno 204, dados válidos e erros JSON da API. Atualizar a caracterização antiga e acrescentar em `frontend/tests/api.test.js` casos de HTTP 200/201 ilegível, erro 401/500 ilegível, status/código/detalhes/mensagem previstos e ausência de exposição do corpo/parser; executar `npm run test:unit -- frontend/tests/api.test.js` e manter os casos válidos existentes.
- [x] 2.2 Criar `docs/technical/cliente-api-frontend.md` com a tabela de respostas, código `resposta_invalida`, preservação do status e orientação de consultar dados antes de repetir gravação; verificar links para implementação/testes/operação de autenticação e coerência com spec/design. Não contar como funcionalidade acadêmica nem alterar README, páginas ou documentação da limpeza.

## 3. Preservação de CSRF e operações incertas

- [x] 3.1 Acrescentar testes no mesmo arquivo para POST com resposta ilegível sem reenvio/evento de sessão, bootstrap CSRF concorrente ilegível sem POST dependente, limpeza da promise e tentativa explícita posterior válida. Verificar contagem de requests, token/credenciais e possibilidade de consulta após erro, conservando testes atuais de sessão/CSRF; executar a regressão focada sem alterar scripts consumidores ou validar schemas fora do escopo.

## 4. Verificação integrada

- [x] 4.1 Executar `npm run test:coverage` com gates existentes e os dois E2E pelo runner oficial com MySQL/API reais, opt-in e configuração somente no processo. Conferir cadastro/login, logout/204, vinte percursos e Plano/Simulado, além da limpeza de schema/processos; registrar resultados reais distinguindo os erros de parser provocados nos unitários da regressão E2E sem mocks. Cobertura backend não precisa ser repetida por esse delta exclusivamente frontend.
- [x] 4.2 Aplicar `openspec-verify-change`, executar `openspec validate corrigir-resposta-json-invalida --strict` e conferir links, whitespace e hashes contra baseline. Consolidar em `validacao.md` escopo dos três arquivos mais artefatos, cenários cobertos, limitações e preservação das outras changes. Resolver achados críticos antes de concluir; não aplicar helpers, alterar backend ou publicar nada nesta tarefa.

## Workflow follow-up

- Sincronizar a nova capability `cliente-api-frontend` após verificação e antes de arquivar, usando as skills correspondentes.
- Aplicar `centralizar-helpers-de-paginacao` somente após encerrar/verificar esta change.
- Commit/push/merge, AWS, slides, vídeo e guia de estudo não são parte desta change.
