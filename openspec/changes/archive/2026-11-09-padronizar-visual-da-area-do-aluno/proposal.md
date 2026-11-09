# Proposta

## Why

A área do aluno funciona, mas apresenta navegação sem ícones, espaçamentos irregulares e componentes com acabamento desigual. Antes da apresentação, a equipe quer melhorar a leitura e a consistência visual com uma intervenção simples de explicar e de verificar.

## What Changes

- Padronizar o menu lateral das dez páginas do aluno, com ícones decorativos, agrupamentos claros, seleção atual e foco visível.
- Harmonizar tipografia, cabeçalho, espaçamentos, cards, campos, botões, paginação e avisos, usando a identidade roxa e os ativos locais existentes.
- Melhorar a adaptação dos mesmos componentes às larguras menores, preservando acesso aos oito destinos atuais e ao logout.
- Preservar conteúdo, IDs, formulários, filtros, mensagens, estados e fluxos existentes. A mudança é a primeira parte do acabamento visual, sem reorganização funcional das páginas.
- Usar as imagens em `output/imagegen/area-aluno-propostas/` somente como estudo visual complementar. Elas não substituem os artefatos oficiais do Desktop V1 nem aprovam os dados, gráficos e controles ilustrados.

### Escopo

Páginas em `frontend/aluno/`: `inicio.html`, `questoes.html`, `questao.html`, `historico.html`, `simulados.html`, `simulado.html`, `desempenho.html`, `plano.html`, `tutor.html` e `privacidade.html`. Os estados de resposta, correção e resultado permanecem nas páginas atuais.

### Fora de escopo

Novos gráficos, indicadores, atalhos contextuais, banner de retomada, agrupamento de práticas, calendário, estimativas de tempo, abas novas, histórico de conversa, renderizador de Markdown/LaTeX, funcionalidades indisponíveis e reprodução integral das treze imagens. Também ficam fora administração de usuários, login/cadastro, backend, banco, migrations, hospedagem, vídeo e material de estudo.

## Capabilities

### New Capabilities

- `interface-area-aluno`: apresentação consistente, navegação acessível e adaptação de layout das páginas existentes do aluno.

### Modified Capabilities

Nenhuma. Os contratos de autenticação, práticas, simulados, diagnóstico, plano, tutor e privacidade continuam vigentes.

## Impact

- **Frontend:** `frontend/css/aluno.css`, ajustes delimitados nos estilos de desempenho, plano, tutor e privacidade quando necessários, `frontend/js/navigation.js`, marcação das dez páginas e um sprite local de ícones do aluno.
- **Compatibilidade:** preservar os oito links na ordem atual, parâmetros `tentativa_id`/`assunto_id`, nomes acessíveis, IDs usados pelos scripts/testes, estados `hidden`/`disabled`, ações explícitas e proteção de identidade. Navegação administrativa e estilos compartilhados exigem isolamento.
- **Arquitetura e segurança:** nenhuma mudança na cadeia Frontend → Route → Controller → Service → Model/Repository → MySQL; ADR-002 e ADR-009 permanecem aplicáveis. Não há SDK, dependência, contrato HTTP, procedure, schema ou transação nova.
- **Dependências:** fonte Noto Sans e logo locais; CSS, SVG e JavaScript simples. A implementação não depende do provedor Gemini, de novas credenciais nem de bibliotecas visuais.
- **Validação:** testes frontend existentes, cobertura, navegação por teclado, inspeção em desktop e celular e regressão E2E existente com MySQL descartável. Preservar o banco e as contas de demonstração e os quatro binários oficiais de design.
