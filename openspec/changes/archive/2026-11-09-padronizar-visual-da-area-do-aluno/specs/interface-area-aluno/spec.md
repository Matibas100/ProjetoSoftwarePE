# Especificação da interface da área do aluno

## Purpose

Oferecer apresentação visual consistente e navegação acessível nas páginas existentes do aluno, preservando os fluxos de estudo, suas informações e seus estados autorizados.

## ADDED Requirements

### Requirement: Navegação comum com destinos preservados

A área do aluno SHALL apresentar os oito destinos atuais na mesma ordem, com texto visível, ícone decorativo e indicação única da seção atual. Destinos indisponíveis SHALL continuar identificados e sem ação. Ícones SHALL NOT substituir nomes acessíveis nem criar paradas de foco.

#### Scenario: Seção atual nas páginas de estudo
- **GIVEN** uma das dez páginas existentes da área do aluno
- **WHEN** o menu é apresentado
- **THEN** aparecem Meu início, Praticar questões, Meu histórico, Simulados, Tutor IA, Desempenho, Plano de Estudos e Privacidade e termos, com os mesmos destinos
- **AND** a página atual ou sua seção correspondente possui uma única indicação de seleção; resolver questão seleciona Praticar questões e realizar ou corrigir simulado seleciona Simulados

#### Scenario: Recurso indisponível e navegação por teclado
- **GIVEN** o menu contendo o aviso de Resumos indisponível
- **WHEN** o aluno percorre os controles com Tab e ativa um link com Enter
- **THEN** os links disponíveis recebem foco visível e abrem seus destinos atuais
- **AND** o item indisponível não recebe link, ação ou parada de foco

### Requirement: Apresentação consistente dos componentes

As dez páginas do aluno SHALL compartilhar identidade roxa, logo existente, tipografia legível, hierarquia de títulos e tratamento coerente de campos, botões, cards, paginação e avisos. Ações principais, secundárias e destrutivas SHALL permanecer distinguíveis por texto e tratamento visual.

#### Scenario: Consistência entre páginas
- **GIVEN** início, questões, questão individual, histórico, simulados, tentativa, desempenho, plano, tutor e privacidade
- **WHEN** o aluno alterna entre essas páginas
- **THEN** menu, cabeçalho, espaçamentos, campos e ações mantêm um padrão visual reconhecível
- **AND** as páginas continuam exibindo seus próprios conteúdos e controles existentes

### Requirement: Layout adaptável com conteúdo acessível

A interface SHALL manter navegação, identificação, logout, conteúdo e controles utilizáveis em desktop e larguras menores, sem sobreposição ou rolagem horizontal da página. Tabelas extensas SHALL poder rolar dentro de seu próprio contêiner. Textos longos SHALL quebrar sem encobrir ações.

#### Scenario: Desktop e celular
- **GIVEN** tela de 1440 ou 1366 pixels de largura e tela reduzida para 768 ou 390 pixels
- **WHEN** o aluno usa cada página e percorre seu conteúdo
- **THEN** consegue acessar os oito destinos, Sair e as ações existentes
- **AND** o conteúdo se reorganiza sem cortes, sobreposição ou largura excedente da página; eventual rolagem de tabela fica delimitada à tabela

#### Scenario: Texto longo e ampliação
- **GIVEN** nome de usuário, assunto ou enunciado longo
- **WHEN** a interface é apresentada em desktop com ampliação de 200%
- **THEN** os textos continuam legíveis e os controles permanecem alcançáveis, inclusive por rolagem vertical

### Requirement: Interação acessível e semântica preservada

Controles interativos SHALL manter nomes e rótulos visíveis, operação por teclado, foco visível e estados reconhecíveis. Texto normal SHALL ter contraste de pelo menos 4,5:1. Controles de ação e links do menu SHALL ter área de interação de pelo menos 44 pixels de altura. Cor isolada SHALL NOT ser a única indicação de resultado, seleção ou erro.

#### Scenario: Questão respondida e erro de formulário
- **GIVEN** uma resposta correta ou incorreta, um campo inválido ou uma ação desabilitada
- **WHEN** a página apresenta esse estado após a ação existente
- **THEN** mantém os rótulos e mensagens correspondentes, sem depender somente de cor
- **AND** o acabamento visual preserva rótulos, foco, mensagens acessíveis e operação por teclado

### Requirement: Estados e proteções existentes permanecem operacionais

O acabamento SHALL preservar loading, vazio, erro, sucesso, indisponibilidade, estado de identidade e confirmações atuais. Conteúdo marcado como oculto ou controles desabilitados SHALL continuar assim até o fluxo existente permitir sua apresentação ou uso.

#### Scenario: Consulta pendente e identidade alterada
- **GIVEN** uma consulta em andamento e posterior troca ou expiração da identidade
- **WHEN** chega a resposta anterior
- **THEN** os mecanismos atuais continuam impedindo a apresentação de dados da identidade anterior
- **AND** o novo estilo não revela blocos ocultos nem desabilita a recuperação de sessão

#### Scenario: Alteração não salva e confirmação
- **GIVEN** alternativa ainda não salva ou ação que exige confirmação, como finalizar simulado ou revogar consentimento
- **WHEN** o aluno tenta sair ou concluir a ação
- **THEN** as proteções e confirmações atuais permanecem acionáveis, legíveis e alcançáveis por teclado

### Requirement: Conteúdo de estudo e contexto permanecem íntegros

A interface SHALL manter valores, filtros, datas UTC, origem e quantidade de respostas, denominadores, amostra, avisos de IA e decisões de privacidade fornecidos pelos fluxos atuais. A padronização SHALL NOT gerar métricas, iniciar atividades, presumir consentimento ou acrescentar chamadas externas.

#### Scenario: Desempenho e plano existentes
- **GIVEN** dados reais retornados pelo diagnóstico e pelo plano
- **WHEN** as páginas recebem o acabamento visual
- **THEN** preservam contagens, percentuais, período, base, amostra e significado da conclusão manual
- **AND** nenhuma métrica ilustrativa das propostas é utilizada como dado do sistema

#### Scenario: Tutor e privacidade
- **GIVEN** a tela do tutor ou a tela de privacidade
- **WHEN** o aluno consulta as informações e utiliza os controles existentes
- **THEN** permanecem disponíveis os avisos sobre IA e envio ao provedor e a distinção entre aceite de uso e consentimento do plano
- **AND** entrar, navegar ou carregar uma página não provoca envio ao Gemini nem aceite automático

### Requirement: Isolamento das outras áreas

A nova apresentação SHALL ficar restrita à área do aluno. As páginas administrativas e públicas SHALL preservar navegação, estilo e comportamento vigentes, inclusive quando utilizam arquivos compartilhados com o aluno.

#### Scenario: Navegação compartilhada
- **GIVEN** uma página administrativa ou pública que compartilha estilos ou a montagem do menu
- **WHEN** ela é aberta após a padronização do aluno
- **THEN** mantém links, perfil, marcação de seleção, aparência e controles anteriores
