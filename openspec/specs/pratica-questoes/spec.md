# Especificação — Prática de Questões

## Purpose

Permitir que o Aluno resolva Questões publicadas com correção no servidor e mantenha histórico próprio persistido e vinculado à versão original.

## Requirements

### Requirement: Seleção segura de Questões
`GET /api/aluno/questoes` SHALL listar somente versões publicadas elegíveis, com filtros positivos de Matéria/Assunto, ordenação por Questão crescente e envelope paginado padrão 1/20, máximo 100. SHALL mostrar enunciado, alternativas, dificuldade e classificação, sem gabarito ou explicação antes de responder. SHALL exigir Aluno; filtro inválido SHALL retornar 400 e lista vazia SHALL ser sucesso sem conteúdo fictício.

#### Scenario: Seleção de Questão publicada
- **GIVEN** Aluno autenticado e versões elegíveis
- **WHEN** consulta Questões por Assunto
- **THEN** recebe somente conteúdo seguro correspondente e nenhum gabarito/explicação em resposta, HTML ou DOM

#### Scenario: Ausência de banco ou filtro inválido
- **GIVEN** Aluno na seleção
- **WHEN** não há Questão elegível ou filtro enviado é inválido
- **THEN** recebe página vazia ou 400 respectivamente, sem criar conteúdo de exemplo

### Requirement: Tentativa individual vinculada à versão
`POST /api/aluno/praticas` SHALL receber somente `questao_versao_id` e `chave_envio` UUID, atribuir dono pela sessão e criar tentativa em andamento com versão/classificação congeladas e sucesso 201. Versão inexistente SHALL retornar 404; não elegível SHALL retornar 409. Mesma chave e versão SHALL retornar a mesma tentativa com 200; mesma chave e versão diferente SHALL retornar 409. Repetir Questão com chave nova SHALL constituir nova tentativa real.

#### Scenario: Início e replay
- **GIVEN** Aluno e versão elegível
- **WHEN** inicia com chave válida e repete a requisição idêntica
- **THEN** existe uma única tentativa e o replay recupera seu ID e versão sem duplicação

#### Scenario: Publicação muda após início
- **GIVEN** tentativa já iniciada
- **WHEN** sua Questão recebe outra publicação ou é arquivada
- **THEN** a tentativa preserva a versão original e ainda pode ser respondida; novos inícios na versão retirada são bloqueados

### Requirement: Correção persistida e idempotente
`POST /api/aluno/praticas/<id>/resposta` SHALL aceitar somente `{alternativa}` A–E e SHALL calcular acerto no servidor com gabarito da versão capturada. SHALL persistir resposta, correção e instante atomicamente antes de retornar 200 com gabarito/explicação. Entrada inválida ou campos extras SHALL gerar 400. Reenvio da mesma alternativa SHALL retornar resultado existente; alternativa diferente após conclusão SHALL retornar 409. Concorrência SHALL manter no máximo uma resposta definitiva.

#### Scenario: Resposta correta ou incorreta
- **GIVEN** tentativa própria em andamento
- **WHEN** Aluno envia alternativa válida com sessão/origem/CSRF válidos
- **THEN** recebe correção correspondente à versão, com resposta, gabarito, explicação disponível e data persistidos

#### Scenario: Reenvio concorrente
- **GIVEN** duas requisições para a mesma tentativa
- **WHEN** enviam respostas iguais ou diferentes
- **THEN** iguais retornam a mesma correção e diferentes deixam uma única resposta final com 409 para a conflitante

#### Scenario: Dados inválidos ou falha de gravação
- **GIVEN** tentativa em andamento
- **WHEN** há entrada inválida ou falha antes do commit
- **THEN** não existe correção parcial nem resultado de sucesso não persistido

### Requirement: Histórico próprio e estável
`GET /api/aluno/praticas` SHALL listar somente tentativas respondidas do dono, com filtro de Assunto, paginação padrão 1/20, máximo 100 e ordem resposta/ID decrescente. `GET /api/aluno/praticas/<id>` SHALL recuperar tentativa própria e revelar correção somente quando respondida. Recurso inexistente ou alheio SHALL produzir o mesmo 404. Edição, transferência do catálogo ou retirada de conteúdo SHALL NOT alterar conteúdo, correção ou classificação histórica da tentativa.

#### Scenario: Histórico após recarga ou novo login
- **GIVEN** Aluno com resposta persistida
- **WHEN** recarrega ou autentica novamente e abre histórico/detalhe
- **THEN** recebe a mesma resposta, versão, correção, data e classificação

#### Scenario: Outro Aluno tenta acessar
- **GIVEN** Aluno B autenticado
- **WHEN** consulta coleção ou ID de tentativa do Aluno A
- **THEN** coleção contém somente dados de B e detalhe de A retorna 404 sem conteúdo

### Requirement: Fluxo de prática acessível e recuperável
As telas de seleção, execução/correção e histórico SHALL usar referências ALU-QUE-001/002/003 e sessão existente. SHALL oferecer seleção por teclado, estados de loading/vazio/erro/sucesso e preservar alternativa local em falha. Recuperação de sessão SHALL exigir reenvio explícito e troca de conta SHALL limpar contexto antigo. Resultado SHALL depender da persistência no servidor, sem correção no navegador ou dados pessoais em localStorage.

#### Scenario: Falha ao responder e recuperação
- **GIVEN** alternativa selecionada e rede ou sessão falha
- **WHEN** Aluno recupera acesso
- **THEN** a seleção permanece no contexto da mesma conta e só é enviada novamente por ação explícita

#### Scenario: Resultado acessível
- **GIVEN** resposta corrigida
- **WHEN** Aluno usa a tela por teclado
- **THEN** acerto/erro e explicação são anunciados sem depender apenas de cor e histórico pode ser consultado
