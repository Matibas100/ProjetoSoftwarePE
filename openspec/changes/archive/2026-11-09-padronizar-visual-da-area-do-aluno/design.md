# Design

## Context

A motivação está em [proposal.md](proposal.md). O aluno já possui dez páginas estáticas e oito destinos de menu. `navigation.js` monta também a navegação administrativa; `auth.css` e `desempenho.css` são compartilhados. As páginas usam IDs e atributos para autenticação, consultas, proteção de identidade, confirmação e testes.

O design é necessário porque o acabamento atravessa dez páginas e arquivos compartilhados. As imagens geradas são estudos, com controles e composições que não representam integralmente o comportamento implementado. O Desktop V1 permanece preservado.

## Goals / Non-Goals

**Objetivos técnicos:** concentrar regras visuais no estilo comum do aluno; manter HTML semântico; acrescentar ícones locais sem dependência; limitar JavaScript à montagem visual do menu. O resultado deve continuar fácil de explicar como HTML + CSS e um menu compartilhado.

**Limites:** não redesenhar a estrutura funcional das páginas, mover formulários entre painéis, adicionar requisições ou alterar cálculos. Backend, contratos HTTP, Services, Repositories, procedimentos, migrations, limites transacionais e dados ficam intactos. Não haverá novo framework, mecanismo de tema ou abstração de componentes.

## Decisions

### 1. Estilo comum, com isolamento da área do aluno

Usar `frontend/css/aluno.css` como base da aparência: variáveis CSS prefixadas `--aluno-`, fonte Noto Sans local, fundo claro, roxo existente, bordas leves e escala consistente de espaçamento. Corpo de texto em aproximadamente 15–16 px, títulos em 28–32 px e rótulos legíveis; reservar fontes menores para texto de apoio ainda legível.

Os ajustes nos arquivos específicos ficam limitados à harmonização visual, preservando seus layouts e conteúdo. Regras em `desempenho.css` que precisem mudar ficam qualificadas por `.aluno-shell` ou `.aluno-page`, pois a administração usa o mesmo arquivo. Não editar globalmente `auth.css` para melhorar apenas o aluno.

Alternativa rejeitada: copiar estilos por página ou aplicar overrides globais que modifiquem administração e login.

### 2. Menu com ícones decorativos e os mesmos links

Acrescentar `frontend/assets/aluno-icons.svg`, um sprite estático de ícones simples de interface. Usar os símbolos por `<svg><use>` com `aria-hidden="true"` e `focusable="false"`; manter texto visível e nomes acessíveis atuais. O logo oficial existente não será redesenhado.

Em `navigation.js`, a ramificação do aluno recebe classes e ícones próprios; a ramificação administrativa conserva sua saída e seu sprite. Preservar a ordem dos oito links, a resolução de `data-current` e o item Resumos indisponível. Agrupar Privacidade e termos sob Minha conta é apenas organização textual do mesmo destino. Não acrescentar Perfil, Redação ou outra opção acionável.

Usar seleção com fundo suave e indicador lateral, hover discreto e foco visível. Em desktop, a lateral pode ser aderente ao topo com rolagem própria para não perder itens em telas baixas. O nome e o botão Sair permanecem no cabeçalho atual; não duplicar controles de autenticação no rodapé para copiar as imagens.

Alternativas rejeitadas: pacote de ícones externo e menu recolhível com novo estado JavaScript. Ícones locais e links comuns atendem ao acabamento sem ampliar a explicação técnica.

### 3. Marcação mínima e contratos do DOM preservados

Alterar as dez páginas somente quando for necessário acrescentar classes, wrappers semânticos ou uniformizar o cabeçalho. Preservar IDs, `name`, `data-*`, relações `label`/campo, ordem de scripts, `role`, `aria-live`, diálogos, `hidden`, `disabled` e seletores usados pelos consumidores.

Nomes dos botões, links e mensagens funcionais permanecem. Não mover nem ocultar metadados UTC, base das respostas, amostra, evidências de privacidade ou advertências do tutor. É permitido harmonizar a apresentação desses textos, mantendo o conteúdo acessível e completo. Conteúdo sem dados continua sem dados.

### 4. Adaptação simples às larguras menores

Em desktop, manter lateral de aproximadamente 224 px e conteúdo com largura máxima e margens consistentes. Abaixo de aproximadamente 800 px, reorganizar a navegação em faixa superior com links legíveis e quebra de linha, empilhar controles e permitir rolagem vertical. Não depender de hover para alcançar informações.

Retirar ou limitar seletores amplos como `.aluno-nav span { display: none; }` no mobile para não esconder nomes de links ou avisos novos. Tabelas mantêm seus contêineres de rolagem; a página não deve transbordar horizontalmente. Diálogos respeitam a largura disponível e preservam foco e confirmação.

Alternativa rejeitada: reduzir todo o conteúdo, rótulos e botões para caber em uma linha.

### 5. Referências visuais e compatibilidade

As treze imagens em `output/imagegen/area-aluno-propostas/` orientam cores, ícones, legibilidade e acabamento, não a reprodução integral. Ficam explicitamente excluídos gráficos de barras/donut, novas abas, botões por assunto, banner de continuidade no início, alterações de estrutura do tutor e quaisquer dados ou métricas ilustrativos.

A implementação preserva as specs atuais dos casos de uso e acrescenta apenas `interface-area-aluno`. ADR-002 continua protegendo identidade/CSRF; ADR-009 mantém decisões explícitas e consequências de revogação. Não é necessária nova decisão arquitetural ou alteração da cadeia Frontend → Route → Controller → Service → Model/Repository → MySQL.

### 6. Verificação proporcional ao acabamento

Executar primeiro os testes existentes de navegação e das áreas afetadas; depois `npm run test:coverage`, mantendo os gates atuais. Atualizar assertions de apresentação existentes somente quando a nova marcação exigir, sem substituir a prova funcional por comparações de strings de CSS.

Inspecionar as dez páginas em 1440×900, 1366×768, 768×1024 e 390×844. Conferir também ampliação de 200%, texto longo, foco por teclado e estados relevantes: vazio/erro, questão respondida, simulado em andamento/finalizado/correção, plano pendente/concluído, tutor indisponível/resposta e privacidade autorizada/recusada. Reutilizar os fluxos e dados sintéticos existentes; não criar nova chamada paga a LLM para testar estilo.

Como a navegação é compartilhada, conferir login e as listas administrativas para detectar vazamento de estilo. Rodar a suíte E2E existente pelo runner oficial com MySQL descartável, preservando o banco operacional e as contas de demonstração. Registrar capturas e resultados em `test-results/` ou `tmp/`, sem credenciais, traces, HAR ou estado autenticado.

## Risks / Trade-offs

- **Estilos compartilhados alterarem a administração:** qualificar seletores pelo aluno e conferir as páginas externas ao recorte.
- **Ícones mudarem nomes acessíveis ou quebrarem os testes:** SVG decorativo, texto atual preservado e regressão de navegação nas duas áreas.
- **Novas regras revelarem blocos ocultos:** preservar `hidden`/`disabled` e conferir erros, identidade e confirmações.
- **A lateral não caber em uma tela baixa:** permitir rolagem e testar 1366×768 e ampliação, sem fixar conteúdo por altura rígida.
- **Imagens sugerirem funções não implementadas:** usar somente seu padrão visual; reconciliar qualquer detalhe com o escopo antes de editar.
- **Prazo curto:** limitar a entrega ao acabamento compartilhado. Reorganizações e novos gráficos ficam fora desta change, sem tarefas implícitas de segunda fase.

## Migration Plan

1. Registrar capturas e a lista de arquivos do frontend afetados.
2. Aplicar os estilos, ícones e ajustes mínimos de marcação.
3. Executar verificações visuais e regressão, mantendo todos os dados existentes.
4. Após validação, disponibilizar os arquivos estáticos pelo processo atual. Não há atualização de banco ou segredo.
5. Se houver regressão, reverter somente os arquivos desta change; nenhuma recuperação de dados é necessária.
