# Spec Delta

## Purpose

Permitir que o Administrador gerencie contas de Aluno de ponta a ponta, com CRUD condicionado aos vínculos existentes, controle de acesso e preservação de sessões, evidências e histórico conforme cada operação.

## ADDED Requirements

### Requirement: Gestão exclusiva de contas de Aluno
Rotas de `/api/admin/usuarios` SHALL exigir Administrador autenticado e usar `no-store`. Mutações SHALL exigir Origin/CSRF válidos e reautenticação nos últimos 15 minutos. Anônimo SHALL receber 401 e Aluno 403 antes das validações. Alvo inexistente ou Administrador SHALL retornar 404 uniforme. Perfil, senha armazenada, evidências e identidade do operador SHALL NOT ser controlados pelo cliente.

#### Scenario: Bloquear acesso indevido
- **WHEN** anônimo ou Aluno tenta listar, consultar ou alterar contas, inclusive com corpo inválido
- **THEN** recebe 401 ou 403 respectivamente sem dados nem efeito no banco

#### Scenario: Administrador não administra outro Administrador
- **GIVEN** sessão administrativa válida
- **WHEN** consulta ou modifica ID de Administrador, inclusive o próprio
- **THEN** recebe 404 igual ao de alvo inexistente, sem mudança de perfil ou bloqueio da conta administrativa

#### Scenario: Senha recente necessária
- **WHEN** Administrador com reautenticação vencida tenta criar, editar, alterar status ou excluir
- **THEN** recebe 403 `reautenticacao_necessaria`, nenhum efeito acontece e a interface exige recuperar identidade e confirmar novamente

### Requirement: Criação administrativa sem aceite presumido
`POST /api/admin/usuarios` SHALL aceitar somente nome, e-mail, senha e confirmação, criar Aluno ativo e retornar 201 com dados administrativos mínimos. SHALL aplicar a validação/normalização do cadastro atual, proteger a senha com hash e recusar e-mail duplicado com 409. SHALL NOT autenticar o Aluno, criar evidência de termos/plano ou modificar a sessão do Administrador.

#### Scenario: Provisionar conta de estudo
- **WHEN** Administrador envia os quatro campos válidos para endereço ainda não usado
- **THEN** recebe conta Aluno ativa, sem senha/hash na resposta, e nenhuma sessão ou decisão de privacidade do titular é criada
- **AND** a tela informa que o titular deverá registrar suas próprias decisões de termos na área disponível

#### Scenario: Campos indevidos ou duplicidade
- **WHEN** criação inclui `perfil`, `ativo`, aceite de termos, campo extra, dados inválidos ou e-mail já usado por qualquer perfil
- **THEN** campos/validação recebem 400 e duplicidade recebe 409, sem criação parcial ou promoção de conta

#### Scenario: Cadastro público permanece independente
- **WHEN** visitante usa o cadastro público ou Aluno provisionado consulta sua privacidade após login
- **THEN** cadastro público continua exigindo uso vigente; conta provisionada vê decisões ausentes e não recebe autorização automática de plano ou Tutor

### Requirement: Listagem paginada e detalhe mínimo
`GET /api/admin/usuarios` SHALL listar somente Alunos, com busca literal por nome/e-mail e status ativo/inativo, paginação e ordem estável por criação/ID decrescentes. Itens SHALL conter ID, nome, e-mail mascarado, perfil, ativo e criação. `GET /api/admin/usuarios/{id}` SHALL devolver esses dados com e-mail completo para edição, sem sessão, hash, decisões ou desempenho. HEAD SHALL manter acesso e não conter corpo.

#### Scenario: Filtrar e paginar
- **WHEN** Administrador combina busca, status, página e tamanho válidos
- **THEN** recebe `itens`, `pagina`, `por_pagina`, `total_itens` e `total_paginas`, sem Administradores e com total independente da página
- **AND** pesquisa sem resultado ou página além do fim retorna coleção vazia coerente

#### Scenario: Conferir exposição de dados
- **WHEN** consulta listagem e detalhe próprio do recorte
- **THEN** listagem devolve `email_mascarado` e detalhe devolve `email`; nenhum inclui senha, hash, cookies, identificadores de sessão, resultados ou comprovantes de privacidade

#### Scenario: Validar identificadores e filtros
- **WHEN** envia ID roteado fora de 1–2147483647, paginação inválida, busca maior que 254 caracteres ou filtro desconhecido
- **THEN** recebe 400 sem consulta funcional indevida; segmentos não roteados preservam 404 e a query não pode incluir Administradores

### Requirement: Atualização de identificação e sessões
`PUT /api/admin/usuarios/{id}` SHALL aceitar somente nome e e-mail válidos, preservar perfil, senha, ativo, criação e histórico e retornar 200. E-mail duplicado SHALL gerar 409 com rollback. Mudança efetiva de e-mail SHALL revogar sessões do alvo atomicamente e impedir confirmação de nova sessão vinculada ao endereço antigo. Mudança só de nome ou valores idênticos SHALL NOT revogar sessões.

#### Scenario: Corrigir nome
- **WHEN** Administrador altera somente o nome do Aluno
- **THEN** identificação é atualizada sem alterar decisões, atividades, senha ou sessões válidas

#### Scenario: Trocar e-mail
- **GIVEN** Aluno com múltiplas sessões válidas
- **WHEN** mudança de e-mail é confirmada
- **THEN** o novo endereço normalizado é persistido e as sessões anteriores deixam de autorizar; login futuro usa o novo endereço

#### Scenario: Troca concorre com login antigo
- **WHEN** login com endereço antigo aguarda validação bloqueante ou criação de sessão enquanto a troca é confirmada
- **THEN** o login é recusado se o endereço esperado deixou de ser corrente antes da confirmação de sua sessão, sem criar sessão utilizável com identidade antiga

#### Scenario: Falha ou concorrência no endereço
- **WHEN** e-mail conflita, há duas atualizações concorrentes para o mesmo endereço ou ocorre falha na revogação antes do commit
- **THEN** unicidade é mantida; conflito retorna 409 e falha reverte identificação e revogações, sem sucesso parcial

### Requirement: Desativação e reativação preservam histórico
POSTs `/api/admin/usuarios/{id}/desativar` e `/reativar` SHALL exigir `confirmar:true` como único campo e retornar 200. Desativação SHALL marcar conta inativa e revogar suas sessões na mesma transação, bloqueando novos logins. Reativação SHALL permitir novo login sem recuperar sessões revogadas. Repetição no estado já solicitado SHALL ser segura, sem apagar respostas, planos ou aceites.

#### Scenario: Desativar com histórico
- **WHEN** Administrador confirma desativação de Aluno com sessões, respostas, simulados, planos e decisões
- **THEN** a conta fica inativa e sessões são revogadas; histórico e decisões permanecem iguais, sem equivaler a recusa/revogação do plano

#### Scenario: Reativar sem ressuscitar sessão
- **WHEN** Administrador reativa a conta e o Aluno tenta usar cookie antigo ou fazer novo login
- **THEN** cookie revogado continua inválido e novo login com credenciais corretas pode criar nova sessão

#### Scenario: Login ou falha durante desativação
- **WHEN** criação de sessão concorre com desativação ou a revogação falha antes do commit
- **THEN** não resta sessão válida após desativação confirmada; falha reverte estado e revogações integralmente

### Requirement: Exclusão física somente sem vínculos impeditivos
`DELETE /api/admin/usuarios/{id}` SHALL exigir somente `confirmar:true` e retornar 204 apenas se a exclusão não violar vínculos. Sessões, aceites, autoria ou histórico referenciando a conta SHALL impedir exclusão com 409 `usuario_com_vinculos`. Nenhuma dependência SHALL ser removida para permitir o DELETE. Falha SHALL preservar conta e histórico, oferecendo desativação como ação distinta.

#### Scenario: Excluir conta administrativa recém-criada
- **GIVEN** Aluno provisionado pelo Administrador que ainda não tem sessões, decisões ou outros vínculos
- **WHEN** exclusão é confirmada
- **THEN** somente a conta é removida, resposta é 204 e consulta posterior retorna 404

#### Scenario: Conta com aceite ou sessão
- **GIVEN** conta com evidência de uso, sessão ainda que revogada, ou outra referência impeditiva
- **WHEN** Administrador confirma DELETE
- **THEN** recebe 409 e nada é apagado; a interface explica a restrição sem prometer eliminar histórico

#### Scenario: Novo vínculo concorre com exclusão
- **WHEN** um vínculo é criado durante a tentativa de excluir
- **THEN** a integridade do banco decide a ordem sem registro órfão: ou exclusão confirma sem vínculo, ou DELETE é recusado e a referência é preservada

### Requirement: Telas administrativas coerentes com o recorte
`/admin/usuarios.html` e `/admin/usuario.html` SHALL oferecer listagem, criação, detalhe/edição, status e exclusão confirmada, com acesso verificado, teclado/foco e estados reais. SHALL preservar filtros e rascunho em falha, impedir duplicação/retry automático e descartar respostas obsoletas. Recursos futuros de perfis, recuperação, exportação, estudos alheios e auditoria SHALL permanecer indisponíveis.

#### Scenario: Executar CRUD pela interface
- **WHEN** Administrador cria Aluno, encontra na lista, abre detalhe, edita e exclui uma conta sem vínculos
- **THEN** cada ação usa a API real, mostra resultado confirmado e percorre Controller, Service, Model/Repository e MySQL

#### Scenario: Recuperar falha ou identidade
- **WHEN** gravação falha ou expira a autenticação
- **THEN** nome/e-mail e contexto são preservados; recuperação ocorre no padrão existente, sem reenviar a ação, e trocar de conta exige descarte/recarga

#### Scenario: Dados sensíveis e saída
- **WHEN** criação termina, identidade se perde/troca ou usuário abandona o formulário
- **THEN** campos de senha inicial são limpos e não aparecem em URL, armazenamento persistente, resposta de detalhe, log ou mensagem de erro

#### Scenario: Consulta em duas larguras
- **WHEN** as telas são usadas por teclado a 1440 px e 390 px
- **THEN** campos, tabela adaptada, mensagens e confirmações permanecem legíveis, com foco e sem overflow horizontal da página

### Requirement: Compatibilidade e prova do recorte
A entrega SHALL preservar cadastro público, CLI administrativa, contratos de autenticação, termos imutáveis e os casos acadêmicos anteriores. SHALL comprovar CRUD permitido, exclusão bloqueada e sessões com MySQL/navegador reais e testes de concorrência/rollback. F01 SHALL ser encerrada somente para a gestão de Alunos demonstrada, sem afirmar cobertura de outros perfis ou exclusão geral de contas.

#### Scenario: Verificar a entrega
- **WHEN** a change é validada
- **THEN** evidências distinguem exclusão permitida, desativação e impedimento por FK, mantêm sete módulos/21 mappers e não tratam telas/rotas isoladas como funcionalidades completas
