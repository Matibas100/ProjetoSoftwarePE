# Tarefas: melhorar legibilidade e documentação

## 1. Preflight

- [x] 1.1 Ler proposta/design, AGENTS.md, conventions e decisões do escopo; registrar baseline não sensível, representações AST/DOM/CSS e estado Git em `test-results/legibilidade/`, com contexto em `validacao.md`. Verificar a lista de 25 arquivos e preservar especialmente a reorganização local de migrations, o texto novo do README, specs, temporários/change antiga e binários oficiais. Não abrir/expor `.env`, escrever no banco operacional ou atribuir mudanças preexistentes a esta change.

## 2. Formatação do frontend

- [x] 2.1 Formatar somente os cinco CSS listados no design, com blocos/declaracões legíveis e ordem/tokens significativos intactos. Comparar estrutura, seletores, valores, prioridades, media queries, URLs/strings e comentários contra baseline usando ferramentas já disponíveis; conferir que `styles.css`, dependências e configurações não mudaram. Executar regressão DOM pertinente sem criar testes que apenas espelhem espaços.
- [x] 2.2 Formatar as oito páginas do Aluno listadas no design, preservando textos, atributos, IDs, elementos, links, ordem dos scripts e whitespace significativo, especialmente inline/pre-wrap/literais. Comparar DOM/textos significativos antes/depois e executar testes DOM existentes de Práticas, Simulados, Desempenho, Plano e navegação; verificar que a mudança é somente de apresentação do código, sem wrappers, redesign ou expectativas de testes alteradas.

## 3. Clareza do Python

- [x] 3.1 Revalidar os 14 imports candidatos nos oito Controllers e pesquisar consumidores/patches antes de remover somente os comprovadamente dispensáveis; preservar e registrar eventuais reexportações legítimas. Conferir por AST que o restante das classes/corpos é idêntico e executar os unitários existentes de HTTP/Controllers, sem remover imports de outros módulos ou modificar testes para ocultar incompatibilidade.
- [x] 3.2 Tornar os nomes locais da finalização de Simulado descritivos conforme mapeamento do design e separar operações por linha. Comparar AST normalizada somente por esse mapeamento e executar unitários existentes do domínio, preservando validações, replay antes da revisão, ordem das gravações, branco, Decimal e fronteira transacional. Não extrair helpers, mudar imports/contratos, corrigir outras regras ou escrever testes que apenas verifiquem os novos nomes.

## 4. Documentação atual

- [x] 4.1 Corrigir no README/matriz as afirmações desatualizadas de primeira publicação e CI, vinculando o checkpoint comprovado ao SHA/execução indicados no design e distinguindo alterações posteriores ainda locais; consultar GitHub em modo leitura para qualquer afirmação de estado remoto atual. Atualizar em `docs/conventions/testes.md` a descrição limitada a quatro scripts. Conferir links, lista/matriz de vinte itens, requisitos das duas atividades, preservação da explicação de migrations e dos relatórios históricos; manter a regra permanente de autorização Git e não publicar nada nesta tarefa.

## 5. Validação integrada

- [x] 5.1 Executar cobertura backend com integrações/migrations MySQL reais e cobertura frontend pelos comandos oficiais, opt-ins apenas no processo e gates intactos. Conferir os cenários existentes de Simulado/Controllers, suítes DOM, nenhum arquivo executável zerado e preservação dos testes versionados; registrar resultados reais em `validacao.md`, sem mocks/SQLite em integração ou evidência histórica apresentada como execução nova.
- [x] 5.2 Executar os dois E2E pelo runner oficial e completar inspeção visual de login, administração, Plano, desempenho e resolução/resultado de Simulado em 1440/390 px, aproveitando capturas existentes e QA temporário conforme design. Verificar persistência, foco/navegação, aparência/textos preservados e limpeza de schema/processos; registrar as telas efetivamente inspecionadas, sem mudar runner/testes ou repetir a suíte completa apenas para obter capturas.
- [x] 5.3 Aplicar `openspec-verify-change`, executar `openspec validate melhorar-legibilidade-e-documentacao --strict`, conferir whitespace, links, AST/DOM/CSS e hashes contra baseline. Consolidar delta permitido, resultados/limites e preservação do restante, especialmente API JS, helpers, banco/migrations e visuais oficiais. Resolver achados críticos da limpeza antes de concluir, revisando a proposta se for necessária alteração de comportamento/layout.

## Workflow follow-up

- Sync não aplicável: `skip_specs: true`, nenhuma mudança funcional especificada.
- Arquivar pela skill apropriada após tarefas concluídas e verificação sem achados críticos.
- Propor a correção funcional de JSON inválido em change independente; não aplicá-la junto desta limpeza.
- Extração de helpers, commit/push/merge, AWS, guia de estudo, slides e vídeo permanecem fora desta change.
