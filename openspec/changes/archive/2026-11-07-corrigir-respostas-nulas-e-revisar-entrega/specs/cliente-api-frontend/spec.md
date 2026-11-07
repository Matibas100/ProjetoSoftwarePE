# Spec Delta — Respostas JSON nulas

## MODIFIED Requirements

### Requirement: Sucesso HTTP com resposta ilegível
Exceto em HTTP 204, sucesso HTTP cujo corpo não puder ser lido como JSON ou cujo JSON raiz seja `null` SHALL ser rejeitado com erro de nome `ApiError`, código `resposta_invalida`, detalhes nulos e status HTTP original. A mensagem SHALL ser clara e orientar consulta dos dados antes de repetir a ação, sem incluir corpo recebido, detalhes internos do parser ou exceção de acesso a propriedades.

#### Scenario: Leitura retorna HTML ou JSON malformado
- **GIVEN** HTTP 200 com HTML, corpo vazio ou JSON malformado
- **WHEN** a interpretação do corpo falha
- **THEN** o cliente rejeita com `resposta_invalida` e status 200, sem devolver sucesso `{}` ou expor o corpo recebido

#### Scenario: Gravação recebe corpo ilegível
- **GIVEN** uma gravação já enviada e resposta HTTP 201 cujo JSON não pode ser lido
- **WHEN** o cliente processa a resposta
- **THEN** rejeita com status 201 e orienta conferir os dados, sem afirmar que a gravação foi revertida

#### Scenario: Sucesso HTTP com JSON raiz nulo
- **GIVEN** resposta HTTP 200 ou 201 cujo corpo é o JSON válido `null`
- **WHEN** o cliente interpreta a resposta
- **THEN** rejeita com `ApiError`, código `resposta_invalida`, detalhes nulos e status original
- **AND** a mensagem é `Resposta inválida do servidor. Confira os dados antes de tentar novamente.`, sem expor `TypeError` nem retornar `null` como sucesso

#### Scenario: Nulos internos continuam válidos
- **GIVEN** resposta de sucesso contendo objeto ou lista JSON válidos com campos ou itens nulos
- **WHEN** o cliente interpreta a resposta
- **THEN** preserva o objeto ou lista, seus valores nulos e os demais campos/itens
- **AND** a checagem específica do JSON raiz nulo não interfere no retorno antecipado de HTTP 204 sem leitura do corpo

### Requirement: Preservação dos erros HTTP
Resposta HTTP de erro com JSON válido não nulo SHALL manter mensagem, código, detalhes e status já fornecidos pela API. Sem JSON legível ou com JSON raiz `null`, SHALL produzir a mensagem genérica existente de operação não concluída, conservar o status HTTP e usar código/detalhes nulos. Falha de leitura ou raiz nula SHALL NOT converter um erro HTTP em sucesso ou em status de falha de conexão.

#### Scenario: Erro de conflito estruturado
- **GIVEN** HTTP 409 com mensagem, código e detalhes válidos da API
- **WHEN** o cliente interpreta a resposta
- **THEN** rejeita preservando esses dados e o status 409

#### Scenario: Erro HTTP sem JSON
- **GIVEN** HTTP 401 ou 500 cujo corpo é vazio ou malformado
- **WHEN** a leitura JSON falha
- **THEN** rejeita com mensagem genérica, status original e código/detalhes nulos, sem inventar evento de recuperação de sessão a partir do corpo ilegível

#### Scenario: Erro HTTP com JSON raiz nulo
- **GIVEN** HTTP 400, 401, 403, 409 ou 500 cujo corpo é o JSON válido `null`
- **WHEN** o cliente interpreta a resposta
- **THEN** rejeita com `ApiError`, status original, código/detalhes nulos e mensagem `Não foi possível concluir a operação.`
- **AND** não expõe exceção técnica, não transforma o status em 0 e não infere recuperação de sessão a partir do corpo nulo

### Requirement: Ausência de repetição e efeitos indevidos
Falha de leitura ou JSON raiz `null` SHALL NOT causar nova requisição automática, repetição de gravação, evento de autenticação inferido ou atualização de CSRF com conteúdo ilegível ou nulo. Os controles existentes de credenciais, origem e CSRF SHALL permanecer. Nova tentativa SHALL depender de ação explícita do usuário ou consumidor.

#### Scenario: Bootstrap CSRF ilegível
- **GIVEN** gravações concorrentes aguardando obtenção de CSRF e resposta ilegível desse bootstrap
- **WHEN** a leitura falha
- **THEN** nenhuma gravação dependente é enviada, ambas recebem erro e uma tentativa explícita posterior pode obter um novo token válido

#### Scenario: Resposta perdida após envio
- **GIVEN** token já válido e uma gravação enviada cuja resposta é ilegível
- **WHEN** o erro é devolvido ao consumidor
- **THEN** existe somente o envio original dessa gravação, sem recuperação de sessão ou repetição automática; consulta e decisão posteriores continuam possíveis

#### Scenario: Erro válido de sessão
- **GIVEN** erro JSON válido com código de sessão/CSRF reconhecido pelo fluxo existente
- **WHEN** a resposta é interpretada
- **THEN** a recuperação existente continua sendo sinalizada, sem reenviar automaticamente a gravação recusada

#### Scenario: Bootstrap CSRF com JSON raiz nulo
- **GIVEN** duas mutações concorrentes aguardando o mesmo bootstrap CSRF, que retorna HTTP 200 e JSON raiz `null`
- **WHEN** a resposta é processada
- **THEN** existe somente uma consulta inicial de CSRF, ambas as mutações são rejeitadas com `resposta_invalida` e nenhuma delas é enviada
- **AND** não há evento de recuperação inferido, e uma nova tentativa explícita pode obter token válido e então enviar sua mutação

#### Scenario: Resposta nula após gravação enviada
- **GIVEN** token válido e uma gravação enviada cuja resposta HTTP 200 ou 201 contém JSON raiz `null`
- **WHEN** o erro é devolvido ao consumidor
- **THEN** existe somente o envio original, sem repetição, recuperação de sessão ou afirmação de rollback
- **AND** o token válido permanece para ação explícita posterior, e uma consulta independente continua possível
