# Cliente da API no frontend

## Purpose

Interpretar respostas HTTP da API de forma previsível no frontend, distinguindo conteúdo válido, resposta ilegível e erro do servidor sem repetir gravações automaticamente.

## ADDED Requirements

### Requirement: Preservação das respostas válidas e sem conteúdo
O cliente compartilhado SHALL preservar o conteúdo dos objetos/listas JSON válidos devolvidos pelos endpoints existentes. Respostas HTTP 204 SHALL produzir resultado nulo sem tentar ler JSON.

#### Scenario: Objeto e lista válidos
- **GIVEN** resposta de sucesso com um objeto JSON ou lista JSON válidos
- **WHEN** o cliente interpreta a resposta
- **THEN** devolve os dados sem substituí-los por objeto vazio nem alterar seus campos/itens

#### Scenario: Operação sem conteúdo
- **GIVEN** resposta HTTP 204, inclusive logout ou exclusão
- **WHEN** o cliente interpreta a resposta
- **THEN** devolve resultado nulo sem ler o corpo nem indicar erro de JSON

### Requirement: Sucesso HTTP com resposta ilegível
Exceto em HTTP 204, sucesso HTTP cujo corpo não puder ser lido como JSON SHALL ser rejeitado com erro de nome `ApiError`, código `resposta_invalida`, detalhes nulos e status HTTP original. A mensagem SHALL ser clara e orientar consulta dos dados antes de repetir a ação, sem incluir corpo recebido ou detalhes internos do parser.

#### Scenario: Leitura retorna HTML ou JSON malformado
- **GIVEN** HTTP 200 com HTML, corpo vazio ou JSON malformado
- **WHEN** a interpretação do corpo falha
- **THEN** o cliente rejeita com `resposta_invalida` e status 200, sem devolver sucesso `{}` ou expor o corpo recebido

#### Scenario: Gravação recebe corpo ilegível
- **GIVEN** uma gravação já enviada e resposta HTTP 201 cujo JSON não pode ser lido
- **WHEN** o cliente processa a resposta
- **THEN** rejeita com status 201 e orienta conferir os dados, sem afirmar que a gravação foi revertida

### Requirement: Preservação dos erros HTTP
Resposta HTTP de erro com JSON válido SHALL manter mensagem, código, detalhes e status já fornecidos pela API. Sem JSON legível, SHALL produzir a mensagem genérica existente de operação não concluída, conservar o status HTTP e usar código/detalhes nulos. Falha de leitura SHALL NOT converter um erro HTTP em sucesso ou em status de falha de conexão.

#### Scenario: Erro de conflito estruturado
- **GIVEN** HTTP 409 com mensagem, código e detalhes válidos da API
- **WHEN** o cliente interpreta a resposta
- **THEN** rejeita preservando esses dados e o status 409

#### Scenario: Erro HTTP sem JSON
- **GIVEN** HTTP 401 ou 500 cujo corpo é vazio ou malformado
- **WHEN** a leitura JSON falha
- **THEN** rejeita com mensagem genérica, status original e código/detalhes nulos, sem inventar evento de recuperação de sessão a partir do corpo ilegível

### Requirement: Ausência de repetição e efeitos indevidos
Falha de leitura de resposta SHALL NOT causar nova requisição automática, repetição de gravação, evento de autenticação inferido ou atualização de CSRF com conteúdo ilegível. Os controles existentes de credenciais, origem e CSRF SHALL permanecer. Nova tentativa SHALL depender de ação explícita do usuário ou consumidor.

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
