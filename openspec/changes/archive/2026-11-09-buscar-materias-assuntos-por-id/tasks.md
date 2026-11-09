# Tasks

Aplicar conforme [design](design.md) e os dois delta specs. A proposta não conclui tarefas de implementação. Preservar alterações locais legítimas, `.env`, dados e artefatos oficiais.

## 1. Entregar consultas individuais na API

- [x] 1.1 Implementar `BuscarMateriaPorIdService`, delegação na `MateriaController` e GET no caminho existente; verificar testes de entrada/intervalo, retorno básico, descrição nula, ausência de registro e erro seguro, sem novo Repository ou acesso direto à sessão no Service/Controller.
- [x] 1.2 Implementar `BuscarAssuntoPorIdService`, delegação na `AssuntoController` e GET no caminho existente; verificar testes equivalentes incluindo `nome_normalizado`, `materia_id` atual e estados inativo/arquivado, preservando os contratos de escrita.
- [x] 1.3 Acrescentar integração HTTP com MySQL real para ambos os recursos: GET/HEAD, três estados, 400/401/403/404, ID máximo, query string sem ampliação de permissão, `no-store`, leitura sem CSRF/reautenticação e registro não alterado. Documentar rotas/payloads/perfil/erros no README; verificar testes reais afetados e exemplos coerentes, sem mocks/SQLite nem alteração dos 29 testes originais.

## 2. Integrar leitura ao formulário existente

- [x] 2.1 Alterar Editar em `admin-materias.js` para buscar detalhe antes de preencher, esperando opções de Área, anunciando carregamento e bloqueando Salvar durante a leitura; verificar DOM com dado diferente da listagem, 404/rede/resposta inválida sem fallback, preservação de filtros/rascunho e PUT correto somente após ação explícita.
- [x] 2.2 Alterar Editar em `admin-assuntos.js` para consultar detalhe, atualizar opções de Matéria pela rota existente e definir a origem de edição com a resposta atual; verificar DOM para transferência ocorrida fora da tela, Matéria corrente inativa/arquivada ou criada depois da abertura, falha das opções sem preenchimento parcial e Salvar comum sem transferência indevida.
- [x] 2.3 Acrescentar invalidação/token/abort e integração com o guard/AuthUI nos dois fluxos; verificar DOM de descarte cancelado sem GET, resposta A/B fora de ordem, erro antigo, digitação, Novo/Cancelar/Salvar durante consulta, sessão bloqueada/trocada e revalidação de identidade, sem retry automático. Atualizar a descrição do fluxo no README e verificar foco/mensagens acessíveis na composição existente, sem alterar binários oficiais ou o cliente HTTP global.

## 3. Comprovar o fluxo e encerrar F02

- [x] 3.1 Acrescentar E2E administrativo com MySQL descartável, sem interceptação: editar Matéria e Assunto usando os novos GETs, comprovar atualização feita em segunda aba e vínculo atual de Assunto, mantendo escrita explícita. Verificar no navegador e registrar evidência em `validacao.md`; somente após sucesso atualizar linhas, cadeias e pendência F02 da matriz CRUD, mantendo F01/E01–E03 e evidências históricas sem reescrita.
- [x] 3.2 Executar regressão backend/frontend e coberturas conforme conventions, com MySQL real nos casos aplicáveis e regressão E2E afetada; verificar os mínimos de cobertura, preservação dos vinte casos, 21 mappers e sete módulos, sem nova migration/procedure/dependência. Registrar comandos, resultados e limitações reais no relatório.
- [x] 3.3 Verificar implementação contra design/specs/tasks, revisar diffs, links, UTF-8 e ausência de segredos; executar `openspec validate buscar-materias-assuntos-por-id --strict` e corrigir achados críticos antes do fechamento. Confirmar que apenas F02 foi resolvida e que não há gestão de usuários ou mudança de exclusão fora do escopo.

## Workflow follow-up

- Após aplicação e verificação, sincronizar as duas capabilities e arquivar a change.
- Commit/push somente com autorização explícita. Explorar gestão de usuários em outra change depois desta etapa.
