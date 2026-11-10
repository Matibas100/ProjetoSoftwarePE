# Design: formatação com comportamento preservado

## Context

Ver [proposal.md](proposal.md) para motivação e [analise-de-complexidade.md](analise-de-complexidade.md) para a preocupação com volume. O baseline é `663891af9f6b0cbe7c1df0b7841e104ae7f2cbf1`, já validado e publicado. Não há change funcional ativa concorrente no momento da proposta.

A intervenção atravessa linguagens e testes. O design é necessário para impedir que uma limpeza de aparência altere espaços significativos do HTML, JavaScript, SQL embutido ou referências de integridade.

## Goals / Non-Goals

**Objetivos:** tornar os arquivos existentes fáceis de percorrer e apresentar, com blocos reconhecíveis e uma instrução por linha; conservar a mesma estrutura sintática e os mesmos literais; revisar em grupos pequenos.

**Limites:** formatação não é simplificação de arquitetura. Não remover arquivos, extrair código, criar classes/helpers de produção, mudar nomes, reorganizar imports, substituir loops/condições ou reduzir linhas por compactação. Não criar framework ou cadeia de ferramentas de formatação. O diagnóstico de tamanho não gera tarefas de refatoração nesta change.

## Decisions

### 1. Conjunto elegível fechado pelo baseline

Selecionar somente arquivos que já existam em `git ls-tree -r --name-only 663891af9f6b0cbe7c1df0b7841e104ae7f2cbf1` e atendam à tabela. Antes de editar, produzir em `tmp/` a lista concreta e os hashes de origem; comparar com a árvore local para preservar qualquer alteração legítima posterior. Arquivo novo de outro trabalho não entra automaticamente.

| Grupo | Seleção permitida | Limites |
| --- | --- | --- |
| Aplicação Python | `backend/app/**/*.py` e `backend/run.py` | Todos os sete módulos, contratos e infraestrutura; manter ordem de imports, declarações e efeitos |
| Ferramentas Python de banco | `backend/database/**/*.py` | Formatar somente código Python; valores SQL, metadados, ordem e hashes de referência continuam iguais |
| Testes Python | `backend/tests/**/*.py` e `scripts/**/*.py` | Não mudar fixtures, literais, assertions, cenários, filtros ou thresholds |
| Frontend | `frontend/**/*.js`, `frontend/**/*.css`, `frontend/**/*.html` | Excluir `frontend/legal/**`; incluir testes e E2E próprios; manter semântica de texto/DOM e cascata |
| Scripts Node | `scripts/**/*.mjs` | Mesmas operações, comandos e saídas |
| Configurações existentes | `playwright.config.js`, `vitest.config.js`, `Makefile` | Mesmos valores e comandos; receitas Make preservam tabulações obrigatórias |
| Sprites próprios | `frontend/assets/admin-icons.svg`, `frontend/assets/aluno-icons.svg` | Somente indentação entre elementos; identificadores, paths, atributos e desenho intactos |
| Convenção | `docs/conventions/documentacao-e-nomenclatura.md` | Acrescentar apenas o padrão breve de formatação |

O conjunto é de revisão, não uma obrigação de alterar cada arquivo. Arquivos vazios, inicializadores mínimos e código já organizado podem permanecer byte a byte iguais. Não há meta de reduzir linhas.

**Proteções integrais:** todos os `.sql`, `frontend/legal/*.html`, logo/fontes e outros assets, `.env` e credenciais, dependências/lockfiles, fixtures de dados não executáveis, `sql_resources_reference.json`, relatórios de cobertura, `.github/`, hooks, `.agents/`, artefatos oficiais, documentação histórica, specs e changes arquivadas. Não modificar checksums para acomodar formatação. Não limpar `tmp/`, `output/`, caches, backups ou arquivos externos.

### 2. Padrão simples por linguagem

- Python: quatro espaços; separar instruções com ponto e vírgula em linhas próprias; duas linhas entre declarações de topo e uma entre métodos; listas, dicionários, imports e argumentos extensos em múltiplas linhas, sem mudar a ordem. Protocols com `...` podem ser expandidos sem mudar seu corpo.
- JavaScript: dois espaços; blocos com chaves e instruções em linhas próprias; manter declarações, ponto e vírgula, callbacks, imports, operadores, ordem e fluxo atuais. Declarações com várias variáveis podem ser quebradas visualmente, sem transformá-las em declarações diferentes.
- CSS: dois espaços; uma declaração por linha; separar regras; manter seletores, propriedades, valores, prioridades e ordem. Não ordenar propriedades nem juntar regras parecidas.
- HTML/SVG: dois espaços por nível; separar tags de blocos e atributos extensos quando seguro; manter atributos e sua ordem. Scripts externos devem continuar reconhecíveis pelos consumidores existentes.
- Preferir linhas de até aproximadamente 100 caracteres quando a quebra for segura. Strings, regexes, URLs, `pre`, `textarea`, template literals, SQL embutido e valores de CSS podem permanecer longos para preservar o conteúdo.
- Preservar UTF-8, acentos, comentários e linhas relevantes a diretivas. Não adicionar comentários explicativos em massa, mudar aspas por preferência ou normalizar todos os finais de linha.

Documentar essas regras na convenção existente, sem acrescentar formatter, `.editorconfig`, dependência, arquivo de configuração ou CI novo. A implementação pode usar ferramentas temporárias já disponíveis, com escopo fechado e comparação posterior; não usar regex global como prova de equivalência.

### 3. Verificação estrutural antes dos testes

Manter snapshot privado em `tmp/` dos fontes elegíveis e hashes dos arquivos protegidos não sensíveis. Não ler/copiar `.env`, credenciais ou estado autenticado para esse snapshot. Registrar ferramentas e exceções na validação.

- **Python:** comparar AST com `type_comments=True`, desprezando apenas posições de origem; conservar tipos, ordem, identificadores, valores literais, comentários e diretivas. Normalizar somente posições também nos `type_ignores`, não seu significado. Diferença de AST impede aceitar a edição como formatação.
- **JavaScript:** comparar AST do código antes/depois, incluindo scripts/configurações/testes; ignorar apenas metadados de posição e representação literal equivalente. Preservar diretivas, valores e comentários. Não aceitar mudanças em nós de controle, operadores, chamadas, ordem ou quantidade de declarações. Isso evita alterações por inserção automática de ponto e vírgula.
- **CSS:** comparar a árvore ordenada de regras e declarações, seus seletores, valores, parâmetros e `important`, permitindo só espaços sintáticos equivalentes. Preservar comentários e valores de propriedades customizadas. Bibliotecas já instaladas, como PostCSS e css-tree, podem apoiar o diagnóstico temporário.
- **HTML/SVG:** comparar árvore de elementos/atributos e ordem, conteúdo de scripts/estilos e textos significativos. Não descartar indiscriminadamente todos os nós de whitespace: espaços entre elementos inline e conteúdo de `pre`, `textarea` e campos podem mudar a aparência. Usar também texto renderizado e inspeção visual para os trechos sensíveis.
- **Makefile:** comparar receitas/comandos e tabulações, sem aplicar a regra de dois espaços às receitas.

`ast` da biblioteca padrão, `@babel/parser`, parse5, PostCSS e css-tree já estavam disponíveis no ambiente de exploração. Seu uso é exclusivamente auxiliar, sem imports de runtime ou alteração de manifestos. Se não estiverem disponíveis no apply, não instalar dependência silenciosamente; resolver a estratégia de comparação antes de avançar.

Alternativa rejeitada: passar um formatador irrestrito em toda a árvore, confiar apenas em compilar ou aceitar o resultado porque a suíte passou. Os testes existentes complementam a equivalência, não substituem a proteção de literais e documentos.

### 4. Grupos pequenos com verificação imediata

Aplicar primeiro Python da aplicação, depois ferramentas Python, JavaScript, HTML/CSS/SVG e testes/scripts. Conferir equivalência a cada grupo antes de seguir. As separações no checklist são etapas internas da mesma change, não autorização para implementar parcialmente e marcar tudo concluído.

Usar os testes existentes correspondentes a cada grupo. Não criar testes de produção que apenas repitam a disposição de espaços. Não alterar assertions para tolerar uma mudança funcional; investigar e preservar os contratos. Testes que verificam código-fonte por posição/tokens exigem análise individual, e não enfraquecimento automático.

### 5. Validação final e preservação operacional

Rodar uma vez a cobertura backend com os opt-ins de integração e de migrations somente no processo; usar MySQL real e schemas descartáveis conforme os runners atuais. Rodar `npm run test:coverage` e o E2E oficial com `RUN_MYSQL_E2E=1`. Manter gates 90% de linhas/85% de branches, os 29 testes originais e a suíte ampliada.

Conferir aparência em 1440 e 390 px nas páginas cujo HTML/CSS foi alterado, incluindo menus, formulários, resposta/correção, simulado, plano, tutor e privacidade. Usar os mecanismos temporários e fixtures já disponíveis somente para comparação visual controlada; comprovar fluxos pela integração real. Não invocar Gemini real para validar espaços.

Registrar equivalência, hashes protegidos, testes, inspeções e exceções em `validacao.md` da change. Não alterar banco de demonstração, contas, dados, permissões, transações ou arquivos de instalação SQL. Não exibir segredos nem gerar HAR, traces ou exportação de sessão. A formatação mantém Frontend → Route → Controller → Service → Model/Repository → MySQL e todos os ADRs vigentes.

## Risks / Trade-offs

- **Diff extenso e difícil de revisar:** etapas internas por linguagem, lista fechada e equivalência por grupo; não modificar arquivos já adequados só para aumentar cobertura de formatação.
- **Indentação mudar semântica ou espaços visíveis:** comparar AST/DOM/cascata e inspecionar páginas, preservando regiões sensíveis.
- **Reordenar imports modificar registro ORM ou dependências:** preservar sua ordem e apenas quebrar listas visualmente.
- **SQL e termos perderem integridade:** proteção byte a byte dos arquivos externos e valores literais internos; nenhuma atualização de hash.
- **Confundir formatação com simplificação:** nomes, pastas, classes, regras e quantidade de funcionalidades não mudam. Eventuais candidatos são anotados, sem implementação nesta change.
- **Contagem de linhas crescer:** resultado esperado ao separar instruções; avaliar clareza e preservação, não quantidade mínima de linhas.

## Migration Plan

Sem migration de dados, contrato HTTP, alteração de versão legal ou instalação de pacote. Registrar baseline; aplicar os grupos; verificar equivalência e regressão; revisar o diff. Em caso de problema, desfazer somente as próprias edições de formatação, preservando mudanças legítimas posteriores, sem reset geral, limpeza de diretórios ou restauração de banco.

As specs não precisam ser sincronizadas (`skip_specs: true`). Depois de verificação sem bloqueios, arquivar pelo workflow. Commit e push dependem de nova autorização explícita.
