# Contas e Privacidade — Interfaces MySQL

## Purpose

Definir as interfaces MySQL especializadas de identidade, sessão, limites e decisões de privacidade, preservando os controles de segurança e a atomicidade já implementados.

## ADDED Requirements

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
