# Plano de Estudos — Interfaces MySQL

## Purpose

Definir os acessos especializados MySQL do plano de estudos e sua eliminação participante, preservando consentimento, propriedade, prioridade determinística e histórico autorizado.

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

### Requirement: Autorização precede qualquer derivado do plano
O fluxo SHALL manter o lock de identidade e os dois aceites vigentes antes de consultar plano, replay, item ou diagnóstico. As interfaces SQL SHALL restringir propriedade, manter prioridade determinística no Service e compartilhar conexão/instante com o diagnóstico autorizado.

#### Scenario: Sem consentimento e chave antiga
- **GIVEN** conta sem os aceites vigentes e chave de geração anterior
- **WHEN** consulta, gera, recalcula ou conclui item
- **THEN** recebe 403 uniforme antes de buscar derivados ou diagnóstico, sem ressuscitar plano eliminado

#### Scenario: Recálculo e conclusão concorrentes
- **GIVEN** plano próprio atual e duas ações concorrentes
- **WHEN** recalcula/conclui com revisão ou geração obsoleta
- **THEN** somente a operação válida confirma, a obsoleta mantém o conflito atual e nenhuma resposta ou métrica é alterada por conclusão manual

### Requirement: Eliminação especializada participante e restrita
A procedure de eliminação SHALL ser chamada somente pelo participante de Plano após negativa válida sob lock do dono. Ela SHALL remover itens antes das gerações, respeitar a ordem inversa das referências e compartilhar a transação da decisão, preservando FKs, evidências, respostas e dados de outras contas.

#### Scenario: Negativa com várias gerações
- **GIVEN** duas contas com planos, inclusive gerações anteriores e itens concluídos
- **WHEN** uma confirma recusa/revogação válida
- **THEN** somente todos os derivados dessa conta são removidos e sua negativa confirma na mesma transação, sem apagar respostas ou evidências

#### Scenario: Falha ou replay após nova autorização
- **GIVEN** eliminação em andamento ou negativa antiga seguida de nova autorização e novo plano
- **WHEN** ocorre falha antes do commit ou reenvio da chave antiga
- **THEN** falha reverte decisão e eliminação; replay antigo não elimina o plano novo nem altera a escolha atual

### Requirement: Elegibilidade de prioridades permanece no proprietário
A consulta de pares elegíveis SHALL ser implementada por Conteúdo e consumida pela sua interface pública. Ela SHALL manter estados, ponteiro de publicação e igualdade entre vínculo atual e classificação histórica, com locks compartilhados quando solicitados pela geração.

#### Scenario: Assunto transferido durante seleção
- **GIVEN** grupo histórico transferido para outra Matéria ou conteúdo retirado concorrendo com geração
- **WHEN** o plano confirma a disponibilidade final
- **THEN** não recomenda par incompatível/indisponível nem reclassifica fatos históricos, conservando a ordem de locks e as justificativas atuais
