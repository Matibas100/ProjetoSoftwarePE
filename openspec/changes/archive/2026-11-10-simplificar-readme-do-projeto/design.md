# Design: README curto com documentação rastreável

## Context

Ver [proposal.md](proposal.md). A fonte é o README local de 701 linhas, já alterado pela change de ferramentas arquivada. O HEAD ainda contém a instalação antiga do hook; restaurar o README do Git perderia trabalho legítimo.

Há duas referências atuais ao README com fragmento fora do histórico: `funcionalidades-implementadas` e `checkpoint-publicado-e-ci`. Outros documentos e relatórios antigos também podem apontar para seus títulos. A organização precisa preservar navegação e informação, além de reduzir linhas.

## Goals / Non-Goals

**Objetivo:** entrada compreensível para a equipe e a banca, com até 350 linhas e acesso direto aos detalhes operacionais.

**Limites:** editar somente `README.md`, criar `docs/technical/operacao-do-projeto.md` e `docs/technical/operacao-tutor-ia.md`, além dos artefatos desta change. Não revisar todo o acervo, reproduzir documentos já suficientes ou escrever material de estudo/apresentação nesta etapa.

## Decisions

### 1. Preservar o estado local e mapear o destino de cada seção

Antes de editar, registrar o hash e inventário das seções do README local. O SHA da proposta identifica a referência observada, não autoriza sobrescrever modificações legítimas posteriores. Comparar eventuais diferenças e usar a versão local vigente; não fazer checkout/reset. Preservar as demais alterações da simplificação das ferramentas e seus artefatos arquivados.

Registrar em `validacao.md` um mapa da origem de cada seção para seu resumo, novo documento ou fonte existente. Não é necessário copiar o README inteiro para os artefatos versionados. O mapa deve cobrir:

| Conteúdo atual | Destino |
| --- | --- |
| Objetivo, público, tecnologias e arquitetura | Resumo no README; detalhes de domínio, SOLID e módulos permanecem nas fontes atuais |
| Gestão de Alunos e recursos adicionais | Destaques curtos e links para as operações de domínio já existentes |
| Vinte funcionalidades | Mesmo título e vinte itens no README, sem renumeração ou alteração de significado |
| Componentes, Services e Repositories | Resumo do papel das camadas e links para modelagem, mapa modular e operações; não manter uma lista parcial como inventário completo |
| Consulta individual, payloads, erros e rotas legadas de catálogo | Parte contratual em `operacao-do-projeto.md`; README aponta também para a matriz dos casos e documentação dos domínios |
| Preparação e execução básica | Passos essenciais no README, com orientação para configuração privada e schema vazio |
| Adoção/baseline, reconciliação e recuperação do banco | `operacao-do-projeto.md`, preservando precondições, limitações DDL, privilégios e referências aos ADRs |
| Testes e Make | Comandos básicos no README; detalhes já canônicos em `docs/conventions/testes.md` e equivalências particulares ainda necessárias em `operacao-do-projeto.md` |
| Checkpoints, CI e histórico de validação | Evidências datadas em `operacao-do-projeto.md`; seção curta `Checkpoint publicado e CI` no README com link |
| Clones antigos e preferências do VS Code | `operacao-do-projeto.md`, mantendo hook aposentado, configuração restrita ao clone e arquivo do editor ignorado |
| Evolução 011–017 e consultas por procedures | Links para `consultas-academicas-mysql.md`, ADR-011 e gestão de Alunos; preservar a distinção entre recorte histórico e estado atual |
| Tutor: configuração, contrato, códigos HTTP, limites e evidências | `operacao-tutor-ia.md`; uso e ativação opcionais resumidos no README |
| Termos, limites acadêmicos e entregas | Resumo visível com links para `docs/legal/README.md`, privacidade, matriz CRUD e entrega acadêmica; detalhes operacionais e evidências em seus destinos |

Alternativa rejeitada: cortar trechos sem destino para atingir uma contagem menor. A redução é da página de entrada, não da informação disponível.

### 2. Estruturar a página de entrada para leitura prática

Ordem recomendada: apresentação/público; recursos principais; `Funcionalidades Implementadas`; tecnologias e arquitetura resumida; preparação e execução; testes e CI; índice de documentação e referências da entrega. Utilizar os mesmos comandos e caminhos implementados, sem inventar instalação simplificada que omita dependências, banco ou configuração.

Manter Python/MySQL e bibliotecas do backend como requisitos de execução; Node/npm são necessários às ferramentas de testes do frontend e Make é opcional. Na primeira preparação, orientar copiar `.env.example` somente se ainda não existir `.env`, sem expor ou substituir configuração privada. Explicar criação do schema vazio, configuração de `AUTH_SECRET_KEY`, aplicação das migrations, os dois processos locais, a URL `/login`, cadastro de Aluno e link direto à CLI documentada de Administrador, sem senha padrão.

Incluir links visíveis para diagrama de classes, modelagem, os dois fluxogramas, matriz dos vinte casos, contratos por domínio e testes. Tutor continua opcional e plano depende de autorização/amostra, sem prometer que seja gerado por IA. Não apresentar recursos futuros como implementados.

### 3. Corrigir informações atuais sem apagar evidências antigas

O preparo atual exige migration 017; a descoberta estática identifica seis testes em seis arquivos E2E. Corrigir apenas declarações atuais de 016/quatro testes, preservando números de migrations e resultados datados nos históricos. Não executar `test:e2e:list` para contar testes, pois o comando pode sobrescrever o relatório local.

Explicar brevemente e referenciar o [roteiro oficial](https://github.com/gleisonbt/RoteiroApresentacaoPS2026/blob/main/Roteiro_Apresentacao_Projeto_Rubrica.md): até sete minutos, cinco casos com telas e demonstração de quatro ações principais não CRUD em até dois minutos. Nesse roteiro a separação pode ser demonstrada localmente e hospedagem é bônus; isso não dispensa automaticamente o vídeo de até cinco minutos da atividade anterior. Preservar as ressalvas de aceite docente, Models auxiliares, exclusão/arquivamento, contato fictício e ausência de comprovação de hospedagem.

Não atribuir o CI de um SHA anterior às mudanças locais atuais. Evidências conservam SHA, data, comando, resultado e limites; nem descoberta E2E nem checagem de Markdown comprovam aprovação funcional.

### 4. Preservar navegação e validar sem efeitos operacionais

Ao mover conteúdo, recalcular links relativos à pasta de destino e conferir âncoras. Preservar todos os IDs de títulos atuais do README: como títulos quando mantidos ou âncoras HTML explícitas junto ao link para o novo destino quando a seção sair. Assim as referências antigas continuam encontrando uma orientação, sem editar o histórico ou arquivos oficiais.

Conferir o mapa de transferência, a presença dos mesmos vinte itens, títulos/âncoras, blocos de comandos/contratos e evidências. O texto pode ser resumido, mas precondições e limitações precisam estar no resumo ou no documento vinculado. Verificar comandos por leitura do código/conventions, sem executá-los. Usar somente leitura estática para seis E2E, migrations e configuração.

Registrar contagens de linhas antes/depois, destinos das seções, links/âncoras, diferenças em relação ao estado local inicial e limitações em `validacao.md`. Executar `git diff --check` e `openspec validate --all --strict`. Proteger hashes das fontes e configurações, incluindo as modificações locais anteriores: não executar testes, instalar pacotes, tocar relatórios, ler `.env`, abrir MySQL ou invocar Gemini.

## Risks / Trade-offs

- **Perder alterações da change anterior:** usar o README local e registrar o estado inicial, sem reconstruir pelo HEAD.
- **Resumo esconder configuração necessária:** manter sequência mínima de execução e links específicos para manutenção e contas administrativas.
- **Links quebrados após movimentação:** rebasing dos caminhos e preservação dos IDs anteriores, inclusive os usados pelo histórico.
- **Documentação duplicada divergir:** mover somente informações exclusivas e referenciar os documentos de domínio/conventions existentes.
- **Contagem confundida com comprovação:** distinguir os vinte casos da lista, seis testes E2E e quatro ações da demonstração, mantendo o alcance real das evidências.

## Migration Plan

Sem migration ou alteração de implantação. Criar os destinos, reorganizar o README e conferir navegação/preservação do conteúdo. Para reverter, desfazer somente as edições desta change, mantendo os ajustes legítimos já existentes. Não há delta specs a sincronizar (`skip_specs: true`). Verificar antes de arquivar; commit e push dependem de autorização explícita.
