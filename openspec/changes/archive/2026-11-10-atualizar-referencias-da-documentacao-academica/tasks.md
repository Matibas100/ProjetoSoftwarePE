# Tarefas

## 1. Rastreabilidade dos fluxogramas

- [x] 1.1 Corrigir os 24 links antigos nas duas tabelas de `docs/technical/fluxogramas-casos-de-uso.md` e conferir os símbolos associados: rotas proprietárias, validação compartilhada, persistência canônica, classes de Simulado mantidas em `backend/app/modules/simulados/models/simulado.py` (incluindo `SimuladoTentativa.resultado`) e consulta de desempenho por procedure. Verificar existência de todos os destinos locais do documento e declaração/chamador de cada símbolo alterado; preservar os dois diagramas, rotas e regras. Não mover ou separar Models, nem apresentar `fatos` inexistente ou projeções ORM de regressão como produção.

## 2. Retrato atual da entrega

- [x] 2.1 Atualizar `docs/technical/entrega-academica.md` para distinguir os seis módulos do recorte original dos sete Blueprints atuais e descrever os seis arquivos/casos E2E. Verificar os registros em `backend/app/routes.py`, executar `npm run test:e2e:list` e conferir que os vinte IDs continuam passos do percurso acadêmico, sem contar setup ou ferramentas como funcionalidades.
- [x] 2.2 No mesmo documento, acrescentar a evidência publicada do SHA `bb9823de87f3be6ae4d0a0cb3484ff2725353d7e` e da execução `42736058343`, mantendo as evidências antigas e suas datas. Verificar a correspondência SHA/CI, os links e a distinção entre validação publicada e esta alteração documental; preservar auditorias históricas, ressalvas CRUD, limites de prova, AWS, vídeo e aceite docente.

## 3. Conferência integrada da documentação

- [x] 3.1 Registrar em `validacao.md` os comandos, destinos corrigidos, símbolos conferidos, contagens e limites. Verificar todos os links locais dos dois documentos e as âncoras alteradas, executar `git diff --check` e `openspec validate --all --strict`, e conferir que apenas os dois documentos e artefatos desta change mudaram. Não rodar a suíte da aplicação para corrigir Markdown, instalar ferramentas, ler credenciais, chamar serviços externos ou modificar temporários preexistentes.

Exceção autorizada pelo usuário em 10/11/2026: registrar a sobrescrita já ocorrida de `test-results/e2e.json` pela descoberta, sem cópia anterior e sem considerar o arquivo evidência de execução dos E2E. Concluir 3.1 após as demais checagens, sem repetir a descoberta ou alterar novamente o relatório.

## Workflow follow-up

- Verificar a implementação antes do arquivamento; não há specs a sincronizar (`skip_specs: true`).
- Arquivar pelo workflow após a verificação. Commit e push dependem de autorização explícita.
- As ressalvas acadêmicas sobre arquivamento e Models auxiliares permanecem para alinhamento com o professor; esta change não altera código para resolvê-las.
