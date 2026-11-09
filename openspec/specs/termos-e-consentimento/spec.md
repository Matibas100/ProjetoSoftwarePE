# termos-e-consentimento Specification

## Purpose

Apresentar os termos adaptados à Plataforma ENEM e registrar decisões explícitas sobre o uso opcional do desempenho para o plano personalizado, com consulta, recusa e revogação efetivas no servidor.

## Requirements

### Requirement: Documentos públicos adaptados e versionados
O sistema SHALL publicar Termo de Uso e Termo de Consentimento do plano completos, acessíveis sem sessão, com versão, data, responsável, finalidades e consequências das escolhas. SHALL manter versões publicadas acessíveis e imutáveis, identificar seu conteúdo por hash e disponibilizar metadados vigentes em `GET /api/termos`. O README SHALL indicar as fontes legíveis e imprimíveis dos dois documentos.

#### Scenario: Ler antes de se cadastrar
- **GIVEN** visitante sem conta
- **WHEN** abre os links oferecidos em login ou cadastro
- **THEN** lê os dois documentos integralmente sem autenticação ou JavaScript, com versão e linguagem adequada ao público que se prepara para o ENEM

#### Scenario: Consultar metadados
- **WHEN** cliente solicita GET ou HEAD de `/api/termos`
- **THEN** recebe 200 com metadados vigentes e `no-store`, sem exigir cookie; HEAD não possui corpo e a resposta não contém dados de usuários

#### Scenario: Identificar o documento aceito
- **GIVEN** uma versão publicada e seu hash registrado
- **WHEN** o conteúdo precisa de alteração
- **THEN** nova versão é publicada, a anterior permanece acessível e seu hash continua correspondendo ao texto originalmente apresentado

### Requirement: Transparência dos limites da entrega acadêmica
Os documentos SHALL identificar Matheus Gabriel Oliveira Martins como responsável informado e `contato@plataformaenem.example` como fictício, não operacional. SHALL declarar uso demonstrativo com dados sintéticos e pendências antes de dados reais: contato válido, retenção geral e proteção/autorização de menores. SHALL NOT criar limite etário de produto nem afirmar conformidade integral, certificação ou recursos inexistentes.

#### Scenario: Adaptar o modelo ao sistema real
- **WHEN** os termos são revisados contra cadastro, sessões, respostas, resultados, plano e Tutor existentes
- **THEN** descrevem esses dados e suas finalidades, incluindo o envio opcional da dúvida ao Gemini, sem prometer armazenamento de documentos, coleta de CPF, personalização por IA do plano, conformidade ISO, atendimento por e-mail ou exclusão geral de conta já implementados

#### Scenario: Público amplo sem autorização fictícia de responsável
- **GIVEN** público composto por pessoas que se preparam para o ENEM, inclusive menores
- **WHEN** a demonstração é apresentada
- **THEN** o sistema não exige idade para limitar o produto, não registra marcação do aluno como autorização parental verificada e explicita que o atendimento real a menores depende de outra change

### Requirement: Aceite de uso separado da autorização do plano
O cadastro público SHALL registrar apenas aceite explícito do Termo de Uso vigente, nunca consentimento automático do plano. Contas existentes SHALL poder aceitar o uso em `/aluno/privacidade.html`; ausência de registro SHALL NOT ser interpretada como aceite. Consentir com o plano SHALL exigir aceite de uso vigente e ser uma escolha separada, desmarcada por padrão.

#### Scenario: Cadastro não autoriza personalização
- **WHEN** visitante conclui cadastro válido com aceite de uso
- **THEN** apenas a conta e a evidência de uso são criadas; o plano permanece sem decisão e exige autorização própria

#### Scenario: Conta anterior sem registro
- **GIVEN** conta criada antes desta entrega
- **WHEN** consulta privacidade
- **THEN** vê o uso pendente e plano `nao_informado`, podendo aceitar os termos sem perder acesso às funções independentes do plano

#### Scenario: Termo de Uso ainda pendente
- **GIVEN** Aluno sem aceite de uso vigente
- **WHEN** tenta autorizar o plano
- **THEN** recebe 409 `termos_uso_pendentes` sem registrar autorização

### Requirement: Consulta privada e decisões atribuídas à sessão
`GET /api/aluno/privacidade` SHALL expor últimas decisões próprias, versão, hash, data e autorização atual do plano, sem gerar registros. Mutações SHALL obter identidade somente da sessão e registrar instante e hash no servidor. Anônimo SHALL receber 401 e Administrador 403; mutações SHALL exigir Origin/CSRF e respostas privadas SHALL usar `no-store`. Campos extras e dados inválidos SHALL retornar 400.

#### Scenario: Consultar evidência depois de recarregar
- **GIVEN** Aluno que realizou uma decisão válida
- **WHEN** recarrega a página de privacidade
- **THEN** vê ação, versão e instante persistidos para sua conta e o estado atual, sem depender de armazenamento do navegador

#### Scenario: Forjar identidade ou evidência
- **GIVEN** Aluno autenticado
- **WHEN** envia usuário alvo, hash, timestamp ou outros campos extras numa decisão
- **THEN** recebe 400 sem registrar dados para si ou para terceiros

#### Scenario: Verificar perfil e controles de segurança
- **WHEN** anônimo, Administrador ou cliente sem origem/CSRF válidos tenta uma operação privada
- **THEN** os controles existentes retornam 401/403 conforme o caso e nenhuma decisão ou exclusão é realizada

### Requirement: Escolha opcional e atualização explícita de versão
O sistema SHALL permitir aceitar, recusar e revogar a finalidade específica do plano. Recusa/revogação SHALL manter questões, práticas, simulados e desempenho disponíveis. Aceite SHALL valer somente para sua versão/hash, sem migração automática de decisão. Versão antiga em novo aceite/recusa SHALL retornar 409 `termo_desatualizado`; revogação SHALL continuar disponível para a última aceitação mesmo desatualizada.

#### Scenario: Recusar e continuar estudando
- **GIVEN** Aluno com uso aceito e sem consentimento do plano
- **WHEN** confirma recusa na interface e acessa questões, simulados e desempenho
- **THEN** decisão é persistida como `recusado`, o plano permanece bloqueado e as outras funções continuam utilizáveis

#### Scenario: Aceitar não gera plano automaticamente
- **WHEN** Aluno autoriza a versão vigente com uso aceito
- **THEN** a decisão fica `aceito` e libera o plano, sem gerar/recalcular plano ou alterar respostas por conta própria

#### Scenario: Nova versão exige nova decisão
- **GIVEN** última aceitação com versão ou hash anterior ao vigente
- **WHEN** consulta privacidade e tenta usar o plano
- **THEN** vê `desatualizado`, o plano não é processado e uma nova aceitação explícita é necessária

#### Scenario: Revogar versão antiga
- **GIVEN** última decisão de plano é uma aceitação que deixou de ser vigente
- **WHEN** confirma sua revogação com a versão dessa decisão
- **THEN** a negativa é registrada e tem o mesmo efeito de revogação de uma aceitação vigente

### Requirement: Negativa confirmada elimina somente derivados do plano
Recusa e revogação SHALL exigir aviso de eliminação e confirmação explícita. A decisão e a eliminação de todos os planos, itens e conclusões próprios SHALL confirmar atomicamente. Respostas, simulados, catálogo, outra conta e evidências de decisão SHALL permanecer. Cancelamento ou falha SHALL NOT deixar negativa parcial ou exclusão parcial. Nova autorização SHALL NOT recuperar planos eliminados.

#### Scenario: Cancelar antes de eliminar
- **GIVEN** Aluno vendo o aviso de consequências
- **WHEN** cancela recusa ou revogação
- **THEN** nenhuma mutação é enviada e os dados e a decisão permanecem como estavam

#### Scenario: Revogar com várias gerações
- **GIVEN** Aluno com plano atual, gerações anteriores e itens concluídos
- **WHEN** confirma revogação válida
- **THEN** todas as gerações próprias são eliminadas juntamente com seus itens, a decisão fica `revogado` e as respostas e resultados continuam disponíveis

#### Scenario: Recusar após upgrade com planos legados
- **GIVEN** conta sem decisão importada pelo upgrade e com planos anteriores
- **WHEN** confirma a recusa após o aviso
- **THEN** os derivados legados próprios são eliminados e a recusa é registrada sem inventar uma autorização anterior

#### Scenario: Falha durante a eliminação
- **GIVEN** plano com histórico e uma negativa em processamento
- **WHEN** ocorre falha antes do commit
- **THEN** os planos/itens permanecem íntegros e nenhuma negativa parcial é apresentada como concluída

#### Scenario: Autorizar novamente
- **GIVEN** negativa concluída e base de respostas preservada
- **WHEN** Aluno autoriza novamente e solicita geração com nova chave
- **THEN** pode obter um plano novo calculado da base atual, sem restaurar os snapshots ou conclusões eliminados

### Requirement: Reenvios e decisões concorrentes preservam a intenção atual
Mutações de privacidade SHALL receber chave UUID e revisão da última decisão do tipo. Reenvio idêntico SHALL retornar 200, sem novos efeitos, com registro original e estado atual; nova decisão SHALL retornar 201. Chave conflitante ou revisão obsoleta SHALL retornar 409 `decisao_desatualizada`. Decisão antiga SHALL NOT reautorizar nem eliminar dados novamente após uma escolha posterior.

#### Scenario: Resposta perdida na rede
- **GIVEN** decisão confirmada no banco, mas resposta perdida
- **WHEN** usuário reenvia explicitamente a mesma chave, ação, versão e revisão
- **THEN** recebe 200, o mesmo registro e a autorização atual, sem duplicar decisão ou eliminação

#### Scenario: Reenvio depois de nova autorização
- **GIVEN** negativa concluída, nova aceitação e novo plano
- **WHEN** cliente reenvia a chave original da negativa
- **THEN** recebe o registro original e estado atual aceito, sem apagar o plano novo

#### Scenario: Abas com a mesma revisão
- **GIVEN** duas abas enviando decisões diferentes a partir da mesma revisão
- **WHEN** as requisições concorrem
- **THEN** somente uma decisão nova confirma e a outra recebe 409, devendo consultar o estado antes de nova escolha

### Requirement: Interface acessível não presume sucesso nem mantém dados indevidos
A página de privacidade e o fluxo do plano SHALL oferecer estados reais, leitura dos termos e decisões por teclado com foco e mensagens acessíveis. Falhas SHALL permitir tentativa explícita sem repetir POST automaticamente. Troca de conta, perda de permissão ou resposta obsoleta SHALL retirar/ignorar dados privados do plano. A interface SHALL mostrar a decisão vigente, distinguindo reenvio histórico de autorização atual.

#### Scenario: Interface em duas larguras
- **WHEN** o fluxo é usado por teclado a 1440 px e visualizado a 390 px
- **THEN** documentos, escolhas e confirmação são legíveis, sem rolagem horizontal, com foco visível e recusa acessível

#### Scenario: Sessão ou rede interrompida
- **GIVEN** uma decisão pendente
- **WHEN** ocorre erro de rede ou expiração de sessão
- **THEN** não se anuncia sucesso, a mesma conta pode recuperar e reenviar explicitamente a intenção; conta diferente não recebe os dados privados anteriores

#### Scenario: Revogação em outra aba
- **GIVEN** plano aberto e consentimento revogado em outra aba
- **WHEN** o usuário retorna à aba do plano ou sua consulta recebe 403
- **THEN** dados e ações pendentes anteriores são retirados, a permissão é consultada novamente e resposta atrasada não restaura o plano

### Requirement: Evolução sem consentimento presumido ou perda no upgrade
A entrega SHALL adicionar persistência de privacidade por migration versionada e snapshot equivalente, sem alterar migrations aplicadas nem criar decisões para contas existentes. Instalação limpa, upgrade e reexecução SHALL preservar usuários, respostas, planos e procedure. Exclusão de planos SHALL ocorrer somente pelo caso de negativa confirmada, nunca durante instalação ou bootstrap.

#### Scenario: Upgrade com dados existentes
- **GIVEN** banco em 009 com duas contas, planos e respostas
- **WHEN** aplica a nova migration e consulta os dados
- **THEN** a tabela de privacidade está vazia, os dados anteriores permanecem e ninguém recebeu aceite ou consentimento presumido

#### Scenario: Instalação e reexecução
- **WHEN** schema vazio é atualizado pela sequência, comparado ao snapshot e o runner é executado novamente
- **THEN** estruturas são equivalentes, o baseline reconhece o estado final e nenhuma migration aplicada é reexecutada

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
