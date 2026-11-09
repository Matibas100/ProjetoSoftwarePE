# Spec Delta

## ADDED Requirements

### Requirement: Consulta individual administrativa de Matéria e Assunto
O sistema SHALL disponibilizar `GET /api/materias/{id}` e `GET /api/assuntos/{id}` ao Administrador autenticado. Registro existente SHALL retornar 200 com objeto JSON simples e seus próprios campos persistidos, incluindo status e vínculo por ID, sem envelope paginado, contagens ou agregações. Itens ativos, inativos e arquivados SHALL permanecer consultáveis. A consulta SHALL NOT alterar o registro.

#### Scenario: Consultar uma Matéria existente
- **GIVEN** Administrador com sessão válida e uma Matéria cadastrada
- **WHEN** solicita seu GET individual
- **THEN** recebe somente `id`, `nome`, `descricao`, `area_enem_id`, `status`, `criado_em` e `atualizado_em`, com os valores atuais e descrição nula preservada

#### Scenario: Consultar um Assunto existente
- **GIVEN** Administrador com sessão válida e um Assunto cadastrado
- **WHEN** solicita seu GET individual
- **THEN** recebe somente `id`, `nome`, `nome_normalizado`, `descricao`, `materia_id`, `status`, `criado_em` e `atualizado_em`, com os valores atuais e descrição nula preservada

#### Scenario: Consultar estados indisponíveis para novos vínculos
- **GIVEN** Matéria ou Assunto inativo ou arquivado, inclusive Assunto com Matéria inativa ou arquivada
- **WHEN** Administrador consulta seu ID
- **THEN** recebe 200 com o status real, sem reativação automática ou remoção de vínculos

### Requirement: Erros previsíveis na consulta por identificador
IDs roteados SHALL ser inteiros entre 1 e 2147483647. Valor numérico fora do intervalo SHALL retornar 400 no envelope de erro existente; ID válido inexistente SHALL retornar 404 com erro do recurso. Segmentos não aceitos pelo roteador, como texto ou negativo, SHALL manter 404. Falhas internas SHALL retornar 500 genérico, sem SQL, credenciais ou traceback.

#### Scenario: Registro não encontrado
- **WHEN** Administrador consulta ID positivo válido que não existe
- **THEN** recebe 404 com `erro`, sem objeto vazio de sucesso ou criação de registro

#### Scenario: Identificador numérico fora do intervalo
- **WHEN** Administrador consulta ID zero ou maior que 2147483647
- **THEN** recebe 400 de validação, sem encaminhar esse valor à consulta persistente

#### Scenario: Segmento inválido para a rota
- **WHEN** cliente solicita `/api/materias/abc`, `/api/assuntos/abc` ou caminho com ID negativo
- **THEN** o roteamento retorna 404 conforme o padrão atual, sem mudar o tratamento global das rotas inexistentes

### Requirement: Permissão e compatibilidade das leituras individuais
Consultas individuais SHALL exigir Administrador, retornando 401 ao anônimo e 403 ao Aluno antes de consultar o registro, inclusive para ID inexistente roteado. GET/HEAD SHALL usar `no-store`, sem exigir CSRF ou reautenticação sensível. Leituras legadas, seletores, listagens administrativas e operações de escrita SHALL conservar seus contratos e permissões.

#### Scenario: Anônimo ou Aluno tenta consultar detalhe
- **WHEN** consumidor sem sessão ou Aluno solicita caminho individual roteado
- **THEN** recebe 401 ou 403 respectivamente, sem dados nem indicação de existência do registro

#### Scenario: Administrador realiza leitura sem mutação
- **GIVEN** sessão válida de Administrador
- **WHEN** solicita GET sem CSRF ou HEAD do mesmo recurso
- **THEN** recebe 200 e `Cache-Control: no-store`; HEAD não contém corpo e a leitura não exige senha recente
- **AND** nome, descrição, status, vínculos e timestamps do registro permanecem iguais

#### Scenario: Preservar consumidores anteriores
- **WHEN** Aluno consulta as listas ativas ou Administrador filtra/pagina/edita/arquiva/transfere/exclui pelo fluxo existente
- **THEN** payloads, validações e permissões anteriores continuam válidos, sem estender a leitura individual ao Aluno ou contornar proteção de vínculos
