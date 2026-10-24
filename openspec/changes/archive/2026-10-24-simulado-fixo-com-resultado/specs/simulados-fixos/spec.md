# Delta — Simulados fixos

## Purpose

Disponibilizar simulados de composição manual fixa com versões de Questões preservadas e tentativas próprias do Aluno com resultado persistido.

## ADDED Requirements

### Requirement: Composição fixa revisada e publicada
A gestão `/api/admin/simulados` SHALL exigir Administrador e permitir listar, cadastrar, consultar e editar rascunho com título de 3–150 caracteres e sequência de 1–180 versões elegíveis de Questões distintas. Listagem SHALL usar paginação padrão 1/20, máximo 100, filtro de estado e ordem ID decrescente. Publicar SHALL exigir revisão atual, confirmação, motivo 3–500 caracteres, reautenticação recente, origem/CSRF e revisão explícita, persistindo composição/decisão atomicamente. Publicado/arquivado SHALL NOT aceitar edição; nova composição SHALL exigir novo simulado. Publicação repetida SHALL retornar mesma versão sem duplicação.

#### Scenario: Cadastro e publicação manual
- **GIVEN** Administrador e versões elegíveis
- **WHEN** cadastra sequência válida e confirma sua publicação revisada
- **THEN** simulado preserva ordem e versões dos itens e fica disponível para o Aluno

#### Scenario: Composição inválida ou indisponível
- **GIVEN** rascunho administrativo
- **WHEN** contém zero/>180 itens, Questões repetidas ou versões não elegíveis
- **THEN** recebe 400 para estrutura inválida ou 409 para indisponibilidade, sem publicação parcial

#### Scenario: Edição obsoleta ou de publicado
- **GIVEN** revisão desatualizada ou simulado publicado
- **WHEN** tenta editar a composição
- **THEN** recebe 409 e a composição preservada não muda

### Requirement: Início e retomada de tentativa própria
`GET /api/aluno/simulados` SHALL listar publicados com quantidade real e disponibilidade atual sem gabarito. `POST /api/aluno/tentativas-simulado` SHALL aceitar versão e chave UUID, criar tentativa própria com composição congelada e 201 ou recuperar tentativa em andamento com 200. SHALL permitir no máximo uma tentativa em andamento por Aluno/versão; replay da chave SHALL NOT duplicar tentativa e chave divergente SHALL retornar 409. Conteúdo retirado/superado SHALL impedir novo início com 409, sem substituir Questões. Tentativa já iniciada SHALL continuar na composição original.

#### Scenario: Começar e retomar
- **GIVEN** Aluno e simulado disponível
- **WHEN** inicia, recarrega ou repete início da mesma versão enquanto em andamento
- **THEN** recupera a mesma tentativa própria e sequência fixa, sem duplicação ou gabarito

#### Scenario: Conteúdo retirado
- **GIVEN** simulado contendo Questão depois arquivada ou superada
- **WHEN** solicita nova tentativa ou retoma uma já iniciada
- **THEN** novo início é bloqueado e a tentativa existente permanece respondível com suas versões originais

### Requirement: Persistência de respostas sem correção antecipada
`PUT /api/aluno/tentativas-simulado/<id>/respostas/<item_id>` SHALL aceitar somente alternativa A–E ou null e revisão atual, persistir resposta de item próprio e retornar nova revisão. Respostas SHALL poder ser alteradas/limpas somente em andamento. Antes da finalização, nenhuma leitura SHALL revelar gabarito, explicação ou acerto por item. Entrada inválida SHALL retornar 400, revisão/estado conflitante 409 e item ausente/alheio 404. Falha SHALL preservar a última resposta confirmada.

#### Scenario: Salvar, alterar e recarregar
- **GIVEN** tentativa própria em andamento
- **WHEN** salva/atualiza uma alternativa válida e recarrega
- **THEN** encontra a última resposta persistida e não recebe correção antecipada

#### Scenario: Escritas concorrentes
- **GIVEN** duas ações com a mesma revisão de tentativa
- **WHEN** ambas tentam salvar ou finalizar
- **THEN** somente ação compatível com a revisão corrente confirma e a obsoleta recebe 409 sem sobrescrever dados

### Requirement: Finalização atômica com resultado imutável
`POST /api/aluno/tentativas-simulado/<id>/finalizar` SHALL exigir confirmação e revisão atual, corrigir com gabaritos capturados e persistir respostas/correções/totais/instante/estado atomicamente. Resultado SHALL conter total, respondidas, acertos, erros, em_branco e percentual `100 * acertos / total` com duas casas. Total SHALL igualar acertos + erros + em_branco. Replay de finalização concluída SHALL retornar o mesmo resultado com 200. Tentativa finalizada SHALL NOT aceitar alterações de respostas ou recálculo retroativo.

#### Scenario: Finalizar com itens em branco
- **GIVEN** composição de três Questões, uma correta, uma errada e uma em branco
- **WHEN** Aluno confirma finalização válida
- **THEN** resultado persistido contém total 3, respondidas 2, acertos 1, erros 1, em_branco 1 e percentual 33,33%

#### Scenario: Falha antes do commit e replay
- **GIVEN** finalização iniciada
- **WHEN** há falha de gravação ou reenvio após sucesso
- **THEN** falha não deixa resultado parcial e replay após sucesso retorna resultado original sem nova contabilização

### Requirement: Consulta privada e preservação histórica
Histórico, detalhe, resultado e correção SHALL ser exclusivos do Aluno dono. Resultado/correção antes da finalização SHALL retornar 409; após finalização SHALL apresentar alternativas escolhidas, versões, gabaritos e explicações originais. Histórico SHALL ser paginado padrão 1/20, máximo 100 e finalização/ID decrescentes. ID inexistente/alheio SHALL produzir o mesmo 404. Arquivamento administrativo confirmado e auditado SHALL impedir novos inícios sem excluir tentativas; publicação/transferência do catálogo SHALL NOT reescrever histórico.

#### Scenario: Consulta após novo login
- **GIVEN** tentativa finalizada e conteúdo posteriormente alterado/arquivado
- **WHEN** dono consulta histórico, resultado e correção
- **THEN** recebe o resultado e as versões/classificações originais

#### Scenario: Consulta alheia ou antecipada
- **GIVEN** outro Aluno ou tentativa própria em andamento
- **WHEN** consulta resultado/correção
- **THEN** recebe respectivamente 404 ou 409 sem gabarito ou resultado

### Requirement: Execução acessível sem cronômetro obrigatório
O fluxo ALU-SIM-001/002/003/004 SHALL permitir escolher, navegar, salvar, retomar, confirmar finalização e abrir correção com teclado, foco e estados reais. SHALL informar respostas em branco antes da finalização e preservar contexto em falha de rede/sessão sem replay automático. Este recorte SHALL usar finalização manual sem prazo de tempo, geração automática ou nota TRI.

#### Scenario: Confirmar com falha recuperável
- **GIVEN** respostas salvas e itens em branco
- **WHEN** abre confirmação de finalização e a requisição falha
- **THEN** vê quantidade em branco, conserva contexto e pode tentar novamente explicitamente
