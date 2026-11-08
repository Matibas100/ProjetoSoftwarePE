# Catálogo e Questões editoriais — Interfaces MySQL

## Purpose

Garantir acesso especializado ao catálogo e conteúdo editorial por interfaces MySQL explícitas, preservando disponibilidade, classificação histórica, segurança e os contratos existentes.

## Requirements

### Requirement: Interfaces especializadas por procedures
O recorte inventariado SHALL executar filtros, JOINs, ordenações e operações especializadas pelas procedures oficiais do domínio, com parâmetros vinculados e CALL somente no Repository. CRUD básico SHALL permanecer nas Models e regras de negócio nos Services. SQL dinâmico e fallback ORM para rotina indisponível SHALL NOT ser usados.

#### Scenario: Consulta ou operação especializada autorizada
- **GIVEN** banco atualizado e cliente autorizado para a funcionalidade existente
- **WHEN** executa um caso de uso do inventário
- **THEN** o acesso especializado usa a procedure correspondente e mantém status, campos, tipos, nulos, ordenação e efeitos atuais

#### Scenario: Entrada vinculada e lote vazio
- **GIVEN** filtros textuais com caracteres especiais e listas de IDs vazias, repetidas ou com itens ausentes
- **WHEN** o caso de uso consulta seus dados
- **THEN** entradas são dados, sem execução de SQL adicional; lotes preservam a semântica de conjunto, vazios e ordenação atual sem duplicar registros

### Requirement: Compatibilidade e autorização do domínio
As interfaces SQL SHALL preservar permissões, identidade do servidor e respostas de validação/ausência/conflito existentes. Consultas de apresentação SHALL manter paginação, total independente da página, datas e conteúdo permitido. Procedures auxiliares SHALL NOT criar novas rotas, permissões ou funcionalidades declaradas.

#### Scenario: Cliente não autorizado ou parâmetro inválido
- **GIVEN** cliente anônimo, perfil insuficiente ou entrada inválida
- **WHEN** solicita uma operação protegida
- **THEN** recebe o mesmo erro atual sem conteúdo protegido, mutação parcial ou detalhe SQL

#### Scenario: Página sem resultados
- **GIVEN** listagem paginada do recorte com filtros válidos
- **WHEN** solicita uma página sem linhas
- **THEN** recebe itens vazios e total real correspondente aos filtros, sem linha fictícia ou alteração do envelope

### Requirement: Participação transacional e falha integral
As procedures SHALL usar a conexão e transação do caso de uso, preservar locks, leituras correntes e identidade dos registros alteráveis e SHALL NOT iniciar, confirmar ou reverter transações. Resultados SHALL ser consumidos e cursores liberados sem encerrar conexão emprestada. Falha SHALL manter os erros seguros atuais, sem sucesso parcial.

#### Scenario: Falha depois da leitura bloqueante
- **GIVEN** operação composta que mantém locks e realiza uma escrita após ler pela procedure
- **WHEN** uma etapa posterior falha antes do commit
- **THEN** o rollback externo restaura todas as alterações e os objetos carregados não levam a gravação parcial ou estado obsoleto

#### Scenario: Reutilização após resultado vazio ou erro
- **GIVEN** chamadas sucessivas na mesma conexão, incluindo resultado útil vazio e falha de routine
- **WHEN** o caso termina e uma nova operação usa a infraestrutura
- **THEN** não há resultados pendentes, conexão inválida é descartada e a API não retorna dados artificiais nem expõe SQL, parâmetros sensíveis ou credenciais

### Requirement: Disponibilidade atual e histórico editorial distintos
Seletores SHALL respeitar estados ativos e as quatro Áreas fixas. Elegibilidade SHALL exigir os mesmos vínculos e ponteiro de publicação atuais; consulta histórica SHALL preservar versões publicadas antigas independentemente de retirada posterior. Gabarito SHALL continuar limitado ao perfil/etapa permitidos.

#### Scenario: Conteúdo publicado posteriormente retirado
- **GIVEN** versão usada em tentativa e identidade ou catálogo depois arquivado
- **WHEN** consulta novos usos e a referência histórica já capturada
- **THEN** o novo uso é bloqueado e a referência histórica continua íntegra, sem expor gabarito antecipado ao Aluno

#### Scenario: Seletor ativo e consulta de todos os estados
- **GIVEN** catálogo com itens ativos, inativos e arquivados
- **WHEN** Aluno consulta opções e Administrador consulta todos os estados
- **THEN** cada perfil recebe somente o conteúdo permitido atualmente, com as mesmas Áreas, vínculos e ordem

### Requirement: Impacto e unicidade preservados sob concorrência
Impactos, equivalência de nomes e leituras bloqueantes SHALL manter os predicados e a ordem atual de aquisição de locks. Transferência, publicação e validação de vínculos SHALL continuar revalidando o estado corrente, com restrições e evidências atuais, sem regras ou normalização alternativas no banco.

#### Scenario: Conflito no destino e impacto alterado
- **GIVEN** Assunto equivalente no destino ou mudança de vínculos após a prévia
- **WHEN** Administrador confirma transferência
- **THEN** recebe o conflito/impacto atualizado atual, sem mover parcialmente o Assunto ou reclassificar fatos históricos

#### Scenario: Transferência concorre com uso editorial
- **GIVEN** transferência e publicação/início que usam as mesmas linhas de classificação
- **WHEN** as operações são executadas em conexões diferentes
- **THEN** os locks serializam a validação e nenhuma operação confirma uma combinação inválida de Assunto, Matéria ou versão
