# Contas e Privacidade — Interfaces MySQL

## Purpose

Definir as interfaces MySQL especializadas de identidade, sessão, limites e decisões de privacidade, preservando os controles de segurança e a atomicidade já implementados.

## Requirements

### Requirement: Interfaces especializadas por procedures
O recorte inventariado SHALL executar filtros, JOINs, ordenações e operações especializadas pelas procedures oficiais do domínio, com parâmetros vinculados e CALL somente no Repository. CRUD básico SHALL permanecer nas Models e regras de negócio nos Services. SQL dinâmico e fallback ORM para rotina indisponível SHALL NOT ser usados.

#### Scenario: Consulta ou operação especializada autorizada
- **GIVEN** banco atualizado e cliente autorizado para a funcionalidade existente
- **WHEN** executa um caso de uso do inventário
- **THEN** o acesso especializado usa a procedure correspondente e mantém status, campos, tipos, nulos, ordenação e efeitos atuais

#### Scenario: Entrada de identidade vinculada
- **GIVEN** e-mail normalizado, chave UUID e hashes de sessão/limite usados nos fluxos existentes
- **WHEN** o caso de uso consulta identidade ou decisão
- **THEN** entradas permanecem dados, sem execução de SQL adicional, e mantêm a comparação/collation e a distinção de dono atuais

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

### Requirement: Sessões e credenciais mantêm a política existente
Consulta, renovação e revogação SHALL preservar os predicados atuais, limites absolutos/inatividade e o efeito imediato de conta inativa ou sessão revogada. Normalização e verificação de senha SHALL permanecer na aplicação. Rotinas SHALL NOT receber senha em claro ou expor hashes/identificadores internos no HTTP, logs ou documentação.

#### Scenario: Limites temporais e renovação sem mudança de valor
- **GIVEN** sessões válidas, vencidas, anônimas, revogadas e renovação com o mesmo instante persistido
- **WHEN** consulta ou renova acesso
- **THEN** mantém os resultados atuais inclusive nas igualdades de fronteira, sem considerar renovação válida como falha apenas por não alterar o valor

#### Scenario: Revogação concorrente e identidade carregada
- **GIVEN** uma sessão carregada e revogação concorrente com renovação
- **WHEN** tenta autorizar acesso após a revogação
- **THEN** a sessão não reaparece por cache/estado em memória e recebe a recusa atual; outra conta permanece intacta

### Requirement: Preparação do limite e limpeza restrita
Preparação concorrente da chave do limite SHALL ser atômica e preservar o contador existente. Regra de cinco falhas/janela/bloqueio SHALL continuar no Service. Limpeza SHALL remover somente sessões e limites elegíveis pelos mesmos cortes atuais, retornando contagens sem excluir contas, catálogo, respostas ou evidências.

#### Scenario: Primeira falha concorrente
- **GIVEN** chave ainda ausente e tentativas simultâneas de senha
- **WHEN** preparam o limite e registram falhas
- **THEN** há uma única linha do limite, sem perda de contagem ou colisão 500, e a quinta falha mantém 429/Retry-After atuais

#### Scenario: Limpeza e rollback
- **GIVEN** sessões/limites antigos junto de sessões válidas e evidências
- **WHEN** a limpeza é executada ou falha antes da confirmação
- **THEN** sucesso elimina apenas os registros elegíveis com contagens reais e falha reverte todas as remoções

### Requirement: Decisões de privacidade continuam leituras correntes
Consulta das últimas decisões e replay SHALL permanecer bloqueante, por dono e tipo, após o lock exato de identidade sem filtro adicional de ativo. Estado recente SHALL prevalecer sobre snapshot anterior de autenticação. Decisões SHALL continuar append-only, sem presumir aceite ou reexecutar negativa histórica.

#### Scenario: Negativa confirmada depois do snapshot de autenticação
- **GIVEN** autenticação com snapshot aberto antes da confirmação de revogação em outra conexão
- **WHEN** a conta tenta usar Plano e as decisões são relidas sob lock
- **THEN** a revogação corrente é respeitada antes de replay/derivados/diagnóstico, sem autorizar pelo estado antigo

#### Scenario: Novas escolhas e rollback do participante
- **GIVEN** decisões concorrentes ou negativa cuja eliminação participante falha
- **WHEN** a transação é resolvida
- **THEN** revisão/chave mantém o conflito ou replay atual e falha reverte negativa e derivados juntos, sem perder evidências anteriores

#### Scenario: Últimas decisões em um conjunto gerenciado
- **GIVEN** nenhuma evidência, somente um tipo ou ambos os tipos de decisão
- **WHEN** a routine captura uso e depois plano por leitura corrente FOR UPDATE
- **THEN** retorna um único conjunto com as evidências completas presentes em ordem uso/plano, mapeadas na mesma sessão como entidades gerenciadas, sem reler snapshot

### Requirement: Consultas administrativas de Alunos por procedures
A listagem administrativa SHALL usar `sp_alunos_admin` com filtros/paginação vinculados, retorno limitado e total no mesmo snapshot. Mutações sobre conta existente SHALL usar `sp_usuario_gestao_bloqueado` para ler a identidade corrente sob lock, incluindo inativos. CALL SHALL permanecer no Repository e as routines SHALL NOT confirmar/reverter transações. CRUD e validações SHALL continuar na aplicação/Model.

#### Scenario: Paginar e conferir total consistente
- **GIVEN** Alunos e Administradores, com status e datas distintos
- **WHEN** a consulta administrativa recebe filtros válidos
- **THEN** a procedure retorna somente Alunos nos campos de apresentação previstos, sem senha/hash, com ordem estável e total correspondente aos mesmos filtros e snapshot

#### Scenario: Bloquear conta sem usar snapshot antigo
- **GIVEN** instância de usuário carregada antes de alteração concorrente
- **WHEN** uma mutação administrativa obtém o lock do alvo
- **THEN** a aplicação recebe a linha corrente, sem filtro de ativo e sem sobrescrever campos com a instância antiga; perfil e existência são verificados antes da escrita

#### Scenario: Preservar routines e fronteiras anteriores
- **WHEN** casos administrativos usam revogação de sessões ou retornam conflito de exclusão
- **THEN** reutilizam a revogação existente na transação do caso, não consultam persistência privada de outros módulos e não modificam procedures antigas, decisões, FKs ou política de limpeza

### Requirement: Falhas administrativas não deixam efeitos parciais
Falha em criação, atualização, status ou exclusão administrativa SHALL reverter a transação integralmente. Leitura bloqueante e revogação SHALL usar a mesma conexão da operação. Procedure ausente/divergente SHALL produzir falha segura, sem fallback ORM de consulta especializada. Exclusão SHALL manter FKs como autoridade final, sem desabilitá-las nem remover dependências para forçar sucesso.

#### Scenario: Falhar entre desativação e revogação
- **WHEN** a operação falha depois de alterar o ativo e antes de confirmar revogações
- **THEN** o rollback mantém estado e sessões anteriores, não altera outra conta nem anuncia sucesso parcial

#### Scenario: Nova referência durante exclusão
- **WHEN** a exclusão encontra uma referência protegida, inclusive criada concorrentemente
- **THEN** a conta é preservada com erro seguro 409, sem consulta SQL dinâmica, limpeza em cascata ou bypass dos guards de evidência

#### Scenario: Routine administrativa indisponível
- **WHEN** listagem ou lock não pode executar sua routine oficial
- **THEN** a API falha sem expor SQL/dados de conta e sem mudar para consulta ORM especializada alternativa
