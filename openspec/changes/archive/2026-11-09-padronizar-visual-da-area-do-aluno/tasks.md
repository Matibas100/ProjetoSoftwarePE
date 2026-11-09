# Tarefas

## 1. Base visual compartilhada

- [x] 1.1 Registrar o estado inicial das dez páginas e conferir seletores/arquivos compartilhados; verificar por capturas identificadas e lista das superfícies a alterar, preservando dados e referências oficiais.
- [x] 1.2 Padronizar em `frontend/css/aluno.css` tipografia, cores, espaços, cabeçalho, cards, controles e estados de foco/disabled/hidden, com regras isoladas do aluno; verificar início, questão e privacidade em desktop e 390 px, incluindo texto longo e blocos ocultos.

## 2. Navegação das dez páginas

- [x] 2.1 Acrescentar `frontend/assets/aluno-icons.svg` e o tratamento visual do aluno em `frontend/js/navigation.js`, mantendo oito destinos, textos, ordem, seleção e Resumos indisponível; verificar com `frontend/tests/navigation.test.js` nas duas áreas e conferir ícones decorativos sem paradas de foco ou alteração de nomes acessíveis.
- [x] 2.2 Fazer apenas os ajustes de classes/wrappers necessários em `frontend/aluno/*.html`, mantendo IDs, atributos, scripts e nome/Sair no cabeçalho; verificar links, seleção atual, Tab/Enter e alcance do último item em desktop baixo e celular, com teste de navegação e captura correspondente.

## 3. Acabamento dos componentes existentes

- [x] 3.1 Harmonizar questões, histórico, simulados e seus estados de resolução, resposta, resultado e correção, mantendo listas, alternativas, mapa, paginação e confirmações atuais; verificar testes `aluno-praticas.test.js` e `simulados.test.js` e inspecionar os estados respondido, finalizado e em andamento no navegador.
- [x] 3.2 Harmonizar início, desempenho e plano, ajustando `desempenho.css` e `plano.css` somente no escopo do aluno; verificar testes `desempenho.test.js` e `aluno-plano.test.js`, metadados UTC/base/amostra, plano pendente/concluído e ausência de mudança visual no dashboard administrativo.
- [x] 3.3 Harmonizar tutor e privacidade em seus layouts atuais, incluindo avisos, ações e diálogos; verificar `tutor.test.js` e `privacidade.test.js` e inspecionar resposta/indisponibilidade e consentimento ativo/recusado sem nova chamada ao provedor para validar aparência.

## 4. Verificação integrada da primeira parte

- [x] 4.1 Executar `npm run test:coverage` com os gates existentes e conferir o diff, comprovando que a entrega ficou restrita à apresentação e não acrescentou dependências, contratos, dados ilustrativos em produção ou alterações de backend/design oficial; registrar comando e resultado.
- [x] 4.2 Executar o E2E existente pelo runner oficial com `RUN_MYSQL_E2E=1` somente no processo e MySQL descartável; verificar os percursos reais, confirmações e preservação da navegação administrativa, sem usar ou limpar o banco de demonstração.
- [x] 4.3 Conferir as dez páginas em 1440×900, 1366×768, 768×1024 e 390×844, ampliação de 200%, foco, contraste e alvos de ação; registrar em `validacao.md` a matriz, comandos, resultados e limites reais, com capturas em `tmp/` ou `test-results/` sem segredos ou estado autenticado.

## Workflow follow-up

- Verificar a implementação contra proposta, design e cenários antes de sincronizar `interface-area-aluno`.
- Arquivar somente após a verificação e a sincronização, preservando o Desktop V1 e os dados de demonstração.
- Commit e push dependem de autorização explícita própria; não fazem parte da conclusão automática desta change.
