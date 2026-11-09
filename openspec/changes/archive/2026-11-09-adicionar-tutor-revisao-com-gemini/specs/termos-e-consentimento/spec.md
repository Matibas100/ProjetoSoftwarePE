# Spec Delta

## MODIFIED Requirements

### Requirement: Transparência dos limites da entrega acadêmica
Os documentos SHALL identificar Matheus Gabriel Oliveira Martins como responsável informado e `contato@plataformaenem.example` como fictício, não operacional. SHALL declarar uso demonstrativo com dados sintéticos e pendências antes de dados reais: contato válido, retenção geral e proteção/autorização de menores. SHALL NOT criar limite etário de produto nem afirmar conformidade integral, certificação ou recursos inexistentes.

#### Scenario: Adaptar o modelo ao sistema real
- **WHEN** os termos são revisados contra cadastro, sessões, respostas, resultados, plano e Tutor existentes
- **THEN** descrevem esses dados e suas finalidades, incluindo o envio opcional da dúvida ao Gemini, sem prometer armazenamento de documentos, coleta de CPF, personalização por IA do plano, conformidade ISO, atendimento por e-mail ou exclusão geral de conta já implementados

#### Scenario: Público amplo sem autorização fictícia de responsável
- **GIVEN** público composto por pessoas que se preparam para o ENEM, inclusive menores
- **WHEN** a demonstração é apresentada
- **THEN** o sistema não exige idade para limitar o produto, não registra marcação do aluno como autorização parental verificada e explicita que o atendimento real a menores depende de outra change

## ADDED Requirements

### Requirement: Nova versão de uso descreve tutoria externa
O sistema SHALL publicar uso 2.0 em `/legal/termo-de-uso-v2.html` e seus metadados vigentes, preservando uso 1.0, consentimento do plano 1.0 e suas evidências. O novo texto SHALL explicar envio opcional ao Gemini, dados mínimos, riscos de erro, ausência de histórico na plataforma e limites de `store=false`, sem prometer retenção zero pelo provedor ou autorizar compartilhamento de desempenho.

#### Scenario: Consultar versões após atualização
- **WHEN** visitante consulta `/api/termos` e abre os documentos antigos e o uso 2.0
- **THEN** vê a versão 2.0 vigente para uso e 1.0 para plano, com hashes correspondentes, e todos os documentos permanecem acessíveis sem sessão
- **AND** os bytes e hashes dos dois documentos 1.0 permanecem idênticos aos publicados antes desta change

#### Scenario: Saber o que será enviado
- **WHEN** Aluno lê o novo termo e o aviso do Tutor antes de enviar
- **THEN** é informado de que a dúvida e seu contexto de estudo seguem ao Google Gemini, recebe orientação para não inserir dados pessoais e sabe que não há envio de histórico, respostas a questões, resultados ou dados de conta como contexto automático
- **AND** não se apresenta o envio como juridicamente certificado ou o aceite de uso como autorização genérica de tratamento

### Requirement: Nova finalidade exige ação própria sem ampliar autorização do plano
O Tutor SHALL verificar aceite de uso 2.0 e receber envio explícito de cada dúvida, sem decisão presumida ou aceite automático. O consentimento do plano SHALL continuar exclusivo da personalização determinística. Não usar Tutor SHALL NOT bloquear questões, simulados ou desempenho. Atualizar os termos SHALL NOT eliminar planos, recriar consentimentos ou alterar evidências anteriores.

#### Scenario: Conta com uso antigo
- **GIVEN** conta com uso 1.0 aceito, consentimento do plano e planos salvos
- **WHEN** os termos passam para uso 2.0
- **THEN** Tutor responde 409 até novo aceite explícito e o plano segue a regra existente de exigir uso vigente
- **AND** questões, simulados e desempenho continuam disponíveis; planos e decisões anteriores permanecem, sem perda ou consentimento fabricado

#### Scenario: Atualizar uso e preservar escolha do plano
- **GIVEN** conta com uso antigo e consentimento do plano 1.0 aceito
- **WHEN** aceita explicitamente uso 2.0 pelo fluxo existente
- **THEN** registra-se somente nova evidência de uso e o plano volta a ficar disponível conforme suas regras, sem nova autorização do plano ou envio ao Gemini

#### Scenario: Recusar plano e utilizar o Tutor
- **GIVEN** Aluno com uso 2.0 aceito e plano recusado ou revogado
- **WHEN** envia dúvida explicitamente na tela do Tutor
- **THEN** pode receber tutoria sem ler desempenho ou derivados do plano, sem reautorizar personalização e sem alterar a decisão negativa

#### Scenario: Navegar sem solicitar tutoria
- **WHEN** Aluno abre o sistema, aceita uso 2.0 ou consulta privacidade
- **THEN** nenhuma chamada ao Gemini é feita e nenhuma marcação substitui autorização real de responsável por menor
