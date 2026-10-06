## Purpose

Definir um catálogo acadêmico íntegro e preservável que organize Áreas do ENEM, Matérias, Assuntos e Questões, com ciclo de vida, unicidade e operações administrativas seguras.

## ADDED Requirements

### Requirement: Áreas oficiais do ENEM
O sistema SHALL manter exatamente as áreas `Linguagens`, `Ciências Humanas`, `Ciências da Natureza` e `Matemática`, com identificadores estáveis, disponíveis para consulta e indisponíveis para criação, edição ou exclusão pelo CRUD administrativo desta change.

#### Scenario: Consulta das quatro áreas
- **WHEN** um consumidor consulta as Áreas do ENEM
- **THEN** o sistema retorna as quatro áreas oficiais uma única vez e em ordem determinística

#### Scenario: Tentativa de alterar o catálogo fixo
- **WHEN** um consumidor tenta criar, editar ou excluir uma Área por uma API desta change
- **THEN** o sistema não disponibiliza essa operação

### Requirement: Matéria obrigatoriamente vinculada a uma Área
O sistema SHALL exigir que toda Matéria pertença a uma Área do ENEM existente e SHALL preservar o identificador e os demais dados das Matérias existentes durante o backfill.

#### Scenario: Criação válida de Matéria
- **WHEN** são enviados nome, Área válida e demais campos válidos
- **THEN** o sistema cria a Matéria vinculada à Área informada

#### Scenario: Área ausente ou inexistente
- **WHEN** uma criação ou atualização deixaria a Matéria sem Área válida
- **THEN** o sistema rejeita a operação com erro de validação e não persiste alteração parcial

#### Scenario: Matéria existente sem mapeamento seguro
- **GIVEN** uma Matéria anterior à change que não pode ser classificada por um mapeamento aprovado
- **WHEN** o upgrade tenta tornar o vínculo com Área obrigatório
- **THEN** o upgrade é bloqueado com identificação da pendência, sem excluir nem classificar silenciosamente o registro

### Requirement: Ciclo de vida de Matérias e Assuntos
O sistema SHALL representar Matérias e Assuntos nos estados `ativa`, `inativa` ou `arquivada`. Somente itens ativos SHALL estar disponíveis para novos vínculos; itens inativos ou arquivados SHALL permanecer consultáveis na gestão e em referências históricas.

#### Scenario: Inativação sem perda
- **WHEN** uma Matéria ou um Assunto ativo é inativado
- **THEN** o registro e seus vínculos permanecem preservados e o item deixa de ser oferecido para novos vínculos

#### Scenario: Arquivamento de Assunto utilizado
- **GIVEN** um Assunto com Questões vinculadas
- **WHEN** o administrador arquiva o Assunto
- **THEN** o sistema preserva o Assunto e as Questões, marca-o como arquivado e impede novos vínculos

#### Scenario: Arquivamento de Matéria com Assunto disponível
- **GIVEN** uma Matéria que possui Assunto ativo ou inativo
- **WHEN** o administrador tenta arquivar a Matéria
- **THEN** o sistema bloqueia a operação e informa que os Assuntos devem ser transferidos ou arquivados primeiro

#### Scenario: Reativação válida
- **WHEN** um item inativo ou arquivado é reativado e suas dependências permitem uso ativo
- **THEN** o sistema o torna novamente disponível sem criar outro registro

### Requirement: Unicidade normalizada de Assunto por Matéria
O sistema SHALL manter `nome` na forma apresentada e `nome_normalizado` derivado por uma regra única que considere equivalentes diferenças apenas de caixa, espaços externos, sequências de espaços internos, acentuação e formas Unicode equivalentes. O par `(materia_id, nome_normalizado)` SHALL ser único mesmo quando o registro existente estiver arquivado.

#### Scenario: Duplicidade por caixa, espaço e acento
- **GIVEN** o Assunto `Álgebra Linear` em uma Matéria
- **WHEN** é criada ou renomeada nessa Matéria uma variante como `  ALGEBRA   LINEAR `
- **THEN** o sistema retorna conflito, preserva os dados enviados para correção e não cria duplicata

#### Scenario: Mesmo nome em Matérias diferentes
- **WHEN** nomes normalizados iguais são cadastrados em Matérias distintas
- **THEN** o sistema aceita ambos os Assuntos

#### Scenario: Conflito com Assunto arquivado
- **GIVEN** um Assunto equivalente arquivado na Matéria
- **WHEN** é solicitada a criação de outro Assunto equivalente
- **THEN** o sistema retorna conflito e orienta a reativação do registro existente

#### Scenario: Concorrência na criação
- **WHEN** duas requisições concorrentes tentam criar o mesmo nome normalizado na mesma Matéria
- **THEN** apenas uma persiste e a outra recebe conflito previsível

### Requirement: Exclusão física sem cascata destrutiva
O sistema SHALL usar restrição de integridade entre Área e Matéria, Matéria e Assunto, e Assunto e Questão. A exclusão física SHALL ocorrer apenas quando o registro não possuir vínculo impeditivo e MUST NOT excluir dependências em cascata.

#### Scenario: Exclusão de Matéria com Assuntos
- **GIVEN** uma Matéria com ao menos um Assunto
- **WHEN** sua exclusão física é solicitada
- **THEN** o sistema retorna conflito com o impacto e preserva a Matéria e todos os Assuntos

#### Scenario: Exclusão de Assunto com Questões
- **GIVEN** um Assunto com ao menos uma Questão
- **WHEN** sua exclusão física é solicitada
- **THEN** o sistema retorna conflito e preserva o Assunto e todas as Questões

#### Scenario: Exclusão de registro sem vínculos
- **GIVEN** uma Matéria ou Assunto sem vínculos impeditivos
- **WHEN** sua exclusão física confirmada é solicitada
- **THEN** o sistema exclui somente o registro solicitado e retorna sucesso sem conteúdo

### Requirement: Impacto e transferência explícita de Assunto
O sistema SHALL permitir transferir um Assunto para outra Matéria apenas após validar destino, disponibilidade, unicidade e impacto. A operação SHALL preservar o identificador do Assunto e seus vínculos, ser atômica e registrar origem, destino, instante e contagens confirmadas.

#### Scenario: Prévia de impacto
- **GIVEN** um Assunto e uma Matéria de destino válidos
- **WHEN** o impacto da transferência é consultado
- **THEN** o sistema informa origem, destino e quantidade de Questões que passarão a ser classificadas pela nova Matéria

#### Scenario: Transferência confirmada
- **GIVEN** uma prévia válida e explicitamente confirmada
- **WHEN** a transferência é executada
- **THEN** o sistema altera somente a Matéria do Assunto, preserva suas Questões e registra a transferência na mesma transação

#### Scenario: Nome conflitante no destino
- **GIVEN** um Assunto equivalente na Matéria de destino
- **WHEN** a transferência é validada ou executada
- **THEN** o sistema retorna conflito e mantém o Assunto na Matéria original

#### Scenario: Impacto mudou após a prévia
- **GIVEN** uma prévia apresentada ao administrador
- **WHEN** os vínculos mudam antes da confirmação
- **THEN** o sistema não confirma silenciosamente, retorna o impacto atualizado e exige nova confirmação

#### Scenario: Alteração legada de materia_id
- **WHEN** o contrato legado de atualização recebe `materia_id` diferente do atual
- **THEN** o sistema aplica as mesmas validações e a mesma transação do caso de uso de transferência, sem atualização silenciosa

### Requirement: Consultas administrativas do catálogo
O sistema SHALL oferecer consultas administrativas paginadas de Matérias e Assuntos com filtros combináveis, ordenação determinística, contagens de vínculos e dados suficientes para ADM-CON-001 e ADM-CON-002.

#### Scenario: Filtragem de Matérias
- **WHEN** a listagem de Matérias recebe busca por nome ou descrição e filtro de status
- **THEN** o sistema retorna apenas os itens correspondentes, com Área, quantidade de Assuntos, quantidade de Questões, status e atualização

#### Scenario: Filtragem de Assuntos
- **WHEN** a listagem de Assuntos recebe busca, Área, Matéria e status
- **THEN** o sistema combina os filtros e retorna nome, Área, Matéria, descrição, quantidade de Questões e status

#### Scenario: Página sem resultados
- **WHEN** filtros válidos não encontram itens
- **THEN** o sistema retorna uma página vazia com metadados coerentes, sem tratar o resultado como erro

### Requirement: Compatibilidade dos consumidores existentes
O sistema SHALL preservar as rotas de leitura existentes e os campos legados de Matéria e Assunto. Seletores destinados a novos vínculos SHALL obter apenas itens ativos, enquanto consultas administrativas SHALL poder incluir todos os estados.

#### Scenario: Leitura legada
- **WHEN** um consumidor existente consulta `/api/materias` ou `/api/assuntos`
- **THEN** os campos legados permanecem presentes e novos campos são aditivos

#### Scenario: Seletor de novo vínculo
- **WHEN** um formulário solicita opções para criar uma Questão ou um Assunto
- **THEN** itens inativos e arquivados não são oferecidos
