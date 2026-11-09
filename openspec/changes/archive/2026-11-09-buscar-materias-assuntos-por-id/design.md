# Design

## Context

Ver [proposta](proposal.md). Os caminhos `/materias/<int:materia_id>` e `/assuntos/<int:assunto_id>` já recebem PUT/DELETE, mas não GET. As Models herdam `buscar_por_id` de `ModeloBase`, implementado com `db.session.get`; seus `to_dict` já definem os campos básicos. As Controllers existentes possuem adaptação compartilhada de sucesso/erro.

Em `admin-materias.js` e `admin-assuntos.js`, Editar encontra a linha em `state.items` e passa esse objeto diretamente a `edit`. Em Assunto, o objeto também define `state.editing.materia_id`, usado para detectar transferência ao salvar. Esse valor precisa vir do novo detalhe, não da listagem potencialmente antiga.

As rotas individuais já se enquadram como administrativas no hook de Contas: somente as URLs exatas das listas são liberadas para leitura do Aluno. A nova leitura não precisa mudar o hook, os módulos, os mappers ou o banco.

## Goals / Non-Goals

**Goals:** fechar F02 com dois casos de leitura por chave primária; integrar a leitura ao formulário existente; preservar segurança, alterações locais e associação corrente; demonstrar o caminho `Interface → Flask → Controller → Service → Model → MySQL`.

**Non-Goals:** aumentar artificialmente a contagem de funcionalidades, implementar F01, criar Repository/procedure para leitura por PK, mudar endpoints de escrita, adicionar ETag/versionamento de edição, campo de busca digitada por ID, telas novas ou abstrações de formulário.

## Decisions

### 1. Dois Services simples no módulo Conteúdo

Criar `services/buscar_materia_por_id_service.py` e `buscar_assunto_por_id_service.py`, classes `BuscarMateriaPorIdService` e `BuscarAssuntoPorIdService`, com `executar(id)` no padrão dos casos CRUD atuais. Cada uma valida o ID, chama a Model proprietária, lança `RecursoNaoEncontradoError` se necessário e devolve `to_dict`.

Usar `validar_id` existente para tipo inteiro não booleano e valor positivo; validar adicionalmente o teto 2147483647 nos novos casos, compatível com `INT` assinado do schema. Não alterar o helper compartilhado de maneira a mudar os casos existentes. Esse limite evita encaminhar inteiros enormes ao driver e convertê-los em erro 500.

Acrescentar método `buscar_por_id` em cada Controller, delegando somente ao Service e usando `_responder`. Registrar GET no mesmo caminho já usado por PUT/DELETE, com endpoint interno próprio por recurso. HEAD/OPTIONS seguem o mecanismo existente do Flask, sem implementação paralela.

CRUD básico continua Active Record conforme ADR-008 e a aula. Nenhum Repository, `CALL`, JOIN ou filtro de coleção é necessário. O acesso fica dentro de Conteúdo, preservando ADR-010. Não criar um Protocol/factory novo apenas para envolver uma busca simples.

### 2. Payload do detalhe e erros

Retornar o objeto básico da Model, não o item enriquecido da listagem administrativa:

| Recurso | Campos do HTTP 200 |
| --- | --- |
| Matéria | `id`, `nome`, `descricao`, `area_enem_id`, `status`, `criado_em`, `atualizado_em` |
| Assunto | `id`, `nome`, `nome_normalizado`, `descricao`, `materia_id`, `status`, `criado_em`, `atualizado_em` |

Datas seguem `isoformat` já usado por `to_dict`, sem introduzir outro padrão. Descrição nula permanece `null`. Não incluir Área/Matéria aninhada nem contagens; a tela resolve os nomes pelos seletores existentes.

IDs válidos inexistentes retornam 404 com `erro` do recurso; zero e valores acima do teto, 400 com `erro`. Preservar mensagens/serialização das exceções existentes. Texto e negativos não passam pelo converter `<int:...>` e mantêm 404 de roteamento, sem novo handler global ou promessa de JSON para rota inexistente. Falha inesperada usa 500 genérico e log sanitizado pelo adaptador atual.

Não adicionar filtros ao detalhe: query string não altera status consultável, perfil ou conteúdo retornado. A política é Administrador em todos os estados, independentemente de `?status=ativa` ou `?status=todos`.

### 3. Segurança e fronteira de leitura

Manter `contas/auth_http.py` sem ampliar exceções: GET/HEAD dos caminhos individuais exigem Administrador. Para caminhos roteados, autenticação precede validação/busca, retornando 401 ao anônimo e 403 ao Aluno, sem revelar existência. A leitura não exige CSRF nem janela de senha recente. `sem_cache_auth` já acrescenta `no-store` à resposta de cliente autenticado; verificar isso em GET/HEAD e falhas protegidas.

O Service não acessa `db.session`, não executa SQL e não chama `commit`. A Model faz a leitura por PK na sessão da requisição; o teardown existente libera o contexto. Não criar transação com lock ou escrita para detalhe. A renovação da sessão pelo mecanismo de autenticação permanece; o teste de ausência de mutação compara os registros do catálogo, não exige que a infraestrutura de sessão deixe de atualizar seus próprios acessos.

### 4. Reutilizar Editar como entrada de consulta

No clique de Editar, usar o ID da linha apenas para montar o GET. Confirmar descarte se o formulário estiver alterado, mas não limpar os campos nem chamar `guard.markPersisted` antes da leitura. Carregamento usa a mensagem/contexto do editor, preservando tabela, filtros, paginação e rascunho anterior.

Matéria: esperar opções de Área já carregadas e o GET `/materias/{id}`; preencher o formulário com o detalhe validado. Não solicitar contagens/impacto apenas para editar.

Assunto: consultar `/assuntos/{id}` e atualizar as opções de Matéria usando a rota existente `/materias?status=todos` antes de aplicar os campos. Isso cobre Matéria criada, transferida ou inativada depois da abertura da página. Essa é a listagem já existente, não um novo filtro ou JOIN. Se uma leitura falhar ou a Matéria corrente não estiver nas opções retornadas, não preencher parcialmente nem deixar seleção em branco como se fosse válida; mostrar orientação de atualização/repetição explícita.

Preservar filtros/página quando as opções de edição forem atualizadas; não reinicializar seletores de busca. Oferecer no formulário apenas Matérias ativas mais a Matéria corrente do detalhe, mesmo inativa/arquivada. A origem em `state.editing` passa a ser o detalhe, evitando que um simples Salvar gere transferência por causa da linha antiga. As validações do PUT/transferência continuam sendo a autoridade no momento da escrita.

Validar localmente objeto não nulo/não lista, ID igual ao solicitado, nome/status/vínculo e tipos dos campos necessários ao formulário. Resposta JSON legível com formato incompatível também é falha; não mudar o comportamento global de `apiRequest` para isso. Não usar a linha como fallback quando o GET falhar.

### 5. Coordenar a nova leitura sem sobrescrever intenção

Cada arquivo mantém um contador de leitura e AbortController local. Iniciar seleção, novo cadastro, cancelamento, salvamento, mudança de campos ou bloqueio/troca de identidade invalida o token anterior e aborta quando possível. A invalidação não apaga campos. Capturar token antes da confirmação de descarte e conferir novamente depois dela, evitando que uma confirmação atrasada inicie seleção já abandonada.

Só aplicar o resultado quando token, identidade e contexto do formulário continuam válidos. Ignorar também erros e `finally` de tokens antigos, para uma leitura anterior não liberar controles ou substituir mensagens da atual. Ao invalidar, restaurar imediatamente os controles próprios do estado anterior; abort é otimização e o token é a garantia contra resposta tardia.

Enquanto uma leitura vigente está pendente, bloquear botão e handler de Salvar. Campos anteriores podem continuar legíveis/editáveis; digitar invalida a leitura pendente e preserva o rascunho. Novo cadastro, Cancelar e outra seleção continuam sujeitos ao guard de descarte. Não chamar `edit` nem marcar como persistido até sucesso completo. Após preencher com sucesso, manter comportamento atual de foco, rolagem e baseline do guard.

Capturar ID/perfil de `AuthUI.user` no início. Observar `auth-required` e `auth-identity-changed`; não aplicar detalhe se `AuthUI.blocked`/`changedAccount` estiver ativo. Antes de aplicar resultado, usar `AuthUI.checkIdentity` existente e conferir novamente token/ID/perfil. Isso revalida identidade, sem refazer GET de detalhe ou repetir mutação. Recuperação da mesma conta exige clicar Editar novamente; conta diferente mantém o fluxo administrativo de copiar/descartar e recarregar, sem nova implementação de autenticação.

Alternativas rejeitadas: confiar no cache da tabela; limpar formulário antes da rede; retry automático; trocar a tela por página nova; criar máquina de estados ou biblioteca genérica para dois carregamentos pequenos.

### 6. Testes e documentação do recorte

- Unitários backend verificam os dois Services, limites de ID, retorno/404 e delegação das Controllers. Doubles de Models somente em unidade; nenhuma simulação substitui MySQL de integração.
- Integração com MySQL real verifica GET/HEAD, três estados, descrição nula, normalização, vínculo, 400/401/403/404, erro seguro, `no-store` e ausência de mutação do registro. Usar dados próprios descartáveis; preservar os 29 testes originais e não ler/exibir `.env`.
- DOM administrativo: resposta diferente da linha, erro sem fallback, 404 com rascunho, confirmação cancelada sem GET, A/B fora de ordem, digitação/cancelamento/criação/salvamento durante leitura, erro antigo ignorado, opções de Matéria atualizadas, origem de transferência correta e identidade bloqueada/alterada. Verificar também Editar → Salvar com o PUT existente.
- E2E em MySQL descartável comprova os dois GETs pela interface administrativa. Atualizar um registro por uma segunda aba e depois editar pela primeira comprova o uso do servidor, sem interceptar respostas. No caso de Assunto, confirmar vínculo atual e salvamento comum sem transferência indevida. Usar cenários sintéticos e limpeza do runner; sem mocks, traces, HAR ou credenciais salvas.
- README mostra as duas rotas, perfil, payload/erros e a consulta pelo botão Editar. Na matriz CRUD, atualizar as duas linhas, cadeias e F02 para resolvida somente após a prova; preservar a seção histórica de alcance da validação e acrescentar evidência nova, sem reescrever resultados passados. F01 e E01–E03 continuam independentes.

## Risks / Trade-offs

- Uma leitura nova acrescenta latência → estado local de carregamento e opções reusadas, sem bloquear a navegação.
- Registro pode mudar novamente entre GET e PUT → validações de escrita continuam; esta change não promete bloqueio otimista ou resolução automática de conflito.
- Assunto pode mudar de Matéria enquanto a lista está aberta → origem e seletor vêm do detalhe atual; dependências necessárias são atualizadas antes do preenchimento.
- Novo trecho assíncrono pode apagar rascunho ou aplicar resultado antigo → confirmação sem limpeza antecipada, token/abort, verificação de identidade e cenários DOM específicos.
- API individual poderia ampliar leitura ao Aluno por engano → manter autorização administrativa atual e testar caminhos com e sem query string.

## Migration Plan

Implementação aditiva: backend primeiro, frontend consumidor depois. Não há migration, snapshot SQL, procedure, Model ou dependência a alterar. Publicar os dois lados juntos; frontend novo com backend antigo deve mostrar erro de consulta e preservar rascunho, sem fallback para o cache.

Rollback por reversão do código da change e atualização documental de F02 caso o recurso seja retirado; não exige operação no banco. Commit/push e sync/archive só no fluxo autorizado, após verificação.
