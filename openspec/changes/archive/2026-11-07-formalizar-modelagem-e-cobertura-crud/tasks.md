# Tarefas

## 1. Consolidar as fontes atuais

- [x] 1.1 Registrar no `validacao.md` desta change o estado inicial e hashes dos cinco documentos previstos no design, indicando os dois ainda inexistentes; preservar uma referência das visões do diagrama para comparação. Verificar que nenhum arquivo de configuração sensível, dado pessoal real ou conteúdo de `.env` foi registrado.
- [x] 1.2 Conferir o inventário de `levantamento-crud.md` contra Models, rotas, Controllers, Services e telas atuais; registrar comandos e divergências no `validacao.md`. Verificar as 21 Models, distribuídas em 13 CrudMixin, duas ModeloAtualizavel e seis ModeloBase, e as rotas reais sem conectar ao banco, com dotenv desabilitado e configuração sintética. Essa inspeção é estrutural, sem alegar nova execução de integração.

## 2. Formalizar a modelagem atual

- [x] 2.1 Criar `docs/technical/modelagem-de-dominio.md` com contexto, glossário, seis módulos, papéis das 21 Models e relações principais, referenciando o diagrama como fonte de atributos/cardinalidades. Verificar cobertura pelo inventário da tarefa 1.2, ausência de Model fictícia para Desempenho e indicação explícita de modelagem atual, sem afirmar entrega/aprovação anterior.
- [x] 2.2 Reorganizar `docs/technical/diagrama-de-classes.md` em visões de domínio e de aplicação, preservando classes, atributos, heranças, cardinalidades e visões existentes; explicitar a eliminação de planos derivados após negativa de consentimento conforme ADRs 009/010. Verificar a comparação antes/depois e links/âncoras; validar os blocos Mermaid com ferramentas já disponíveis, registrando o alcance real dessa validação, sem instalar dependências.

## 3. Publicar a cobertura CRUD e as pendências

- [x] 3.1 Criar `docs/technical/matriz-crud.md` com inventário único das 21 Models, separado entre os seis recursos centrais de análise e as outras quinze Models, distinguindo métodos de persistência, API/caso de uso e ação na interface. Verificar cada afirmação por caminhos canônicos, classes, rotas e telas; identificar Controllers/Services do recurso responsável por itens auxiliares. Não contar método herdado, CLI, arquivamento ou recálculo como CRUD público ausente.
- [x] 3.2 Registrar na matriz D01, F01, F02 e E01–E03 com evidências, limites e continuidade: gestão de Usuários ausente, buscas individuais dedicadas de Matéria/Assunto ausentes, restrições de histórico e diferença entre arquivamento e DELETE físico. Verificar que o vínculo protegido de aceite dos termos com Usuário está explicado e que nenhuma dispensa acadêmica, nova política de exclusão, alteração de FK ou implementação funcional foi prometida. F01/F02 permanecem candidatos a changes próprias; esta entrega documental não os encerra.

## 4. Integrar os documentos à entrega existente

- [x] 4.1 Acrescentar referências para modelagem, diagrama e matriz CRUD em `README.md` e `docs/technical/entrega-academica.md`, com contexto sobre o alcance das evidências. Verificar links relativos e comparar as vinte funcionalidades oficiais e seus IDs com o estado inicial: nenhuma renumeração, nova funcionalidade ou afirmação de execução/aprovação deve ser introduzida.

## 5. Conferir a entrega documental completa

- [x] 5.1 Completar `validacao.md` com a conferência cruzada dos cinco documentos, inventário de 21 Models, relações, bases, links, pendências e preservação das vinte funcionalidades; executar `openspec validate formalizar-modelagem-e-cobertura-crud --strict` e `git diff --check`. Verificar pelo estado inicial e pelo diff que alterações desta change se limitam aos cinco documentos e aos seus artefatos, preservando alterações externas, código, contratos, schema, migrations e visuais oficiais. Registrar limitações reais das ferramentas e não executar cobertura, E2E ou operações de banco para esta mudança exclusivamente documental.

## Continuidade do workflow

- Verificar a implementação e arquivar pela skill OpenSpec correspondente quando as tarefas estiverem concluídas; `skip_specs: true` dispensa deltas funcionais e sua sincronização nesta change.
- Tratar as funcionalidades candidatas e suas decisões de produto em exploração/propostas próprias; a justificativa técnica das restrições continua sujeita à avaliação do professor.
- O grupo decide e realiza a entrega acadêmica. Commit, push e envio ao Classroom não fazem parte desta change.
