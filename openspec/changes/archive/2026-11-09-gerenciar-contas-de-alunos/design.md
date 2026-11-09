# Design

## Context

Ver [escopo escolhido](proposal.md). Usuario já possui `nome`, `email` único, `senha_hash`, `perfil`, `ativo` e `criado_em`. Seu CRUD existe na Model, mas a atualização permitida hoje se limita a ativo/senha. Autenticação já rejeita inativos, usa locks ao validar credenciais/criar sessão e oferece revogação por usuário em procedure. Privacidade/histórico usam FKs `RESTRICT`; uma conta do cadastro público já tem um vínculo por seu aceite.

O usuário escolheu gestão somente de Alunos, com exclusão condicionada. As páginas 58–59 do protótipo oficial fornecem ADM-USU-001/002; perfis avançados, auditoria, exportação, e-mail verificado e estudos alheios desse material não integram este recorte. Os binários e documentos legais publicados são imutáveis.

## Goals / Non-Goals

**Goals:** demonstrar CRUD permitido de Usuario pela interface; tratar contas utilizadas com desativação; preservar domínio e autenticação existentes; introduzir apenas duas consultas especializadas novas.

**Non-Goals:** administração do próprio operador ou de outros Administradores, nova camada/framework, alteração de senha pelo gestor, exclusão geral/anonimização, tabela de auditoria ou de consentimento, promoção de perfil, cancelamento de requisições já autorizadas ou revisão de retenção para usuários reais.

## Decisions

### 1. Contas continua proprietário

Adicionar `UsuarioController`, um Service por ação (`CriarAlunoAdminService`, `ListarAlunosAdminService`, `BuscarAlunoAdminService`, `AtualizarAlunoAdminService`, `DesativarAlunoService`, `ReativarAlunoService`, `ExcluirAlunoAdminService`) e `UsuarioRepository` dentro de Contas. Services coordenam sem SQL ou `db.session`; Controller interpreta HTTP e adapta respostas.

Leitura individual usa `Usuario.buscar_por_id`; criação/atualização/exclusão usam `salvar/atualizar/deletar`. Ampliar `campos_atualizaveis` somente com `nome` e `email`, preservando ativo/senha para os casos existentes; perfil/criação não entram na allowlist. Acrescentar serialização administrativa separada, com `id,nome,email,perfil,ativo,criado_em`, sem alterar `to_dict` da autenticação. Data é UTC ISO com `Z`, ativo é booleano.

Listagem recebe contrato pequeno `ConsultaAlunosAdmin` e registros sem ORM em `app.contracts.usuarios`, ligados à implementação de Contas na composição por aplicação. Demais casos seguem o padrão CRUD direto da Model. Não criar Repository de CRUD nem abstrair todo o módulo. Mutações recebem somente alvo/entrada; identidade do operador vem da sessão/hook, nunca do corpo.

### 2. Contrato HTTP e autorização

Todos os caminhos pertencem ao Blueprint de Contas, agregado sob `/api` uma vez:

| Método/caminho | Entrada | Sucesso |
| --- | --- | --- |
| GET `/admin/usuarios` | `busca,status,pagina,por_pagina` | 200, envelope paginado |
| POST `/admin/usuarios` | `nome,email,senha,senha_confirmacao` | 201, DTO administrativo |
| GET `/admin/usuarios/<int:usuario_id>` | ID | 200, DTO administrativo |
| PUT `/admin/usuarios/<int:usuario_id>` | exatamente `nome,email` | 200, DTO administrativo |
| POST `/admin/usuarios/<int:usuario_id>/desativar` | `{"confirmar":true}` | 200, DTO administrativo |
| POST `/admin/usuarios/<int:usuario_id>/reativar` | `{"confirmar":true}` | 200, DTO administrativo |
| DELETE `/admin/usuarios/<int:usuario_id>` | `{"confirmar":true}` | 204, sem corpo |

GET/HEAD exigem Administrador; todas as mutações desse namespace também exigem Origin/CSRF e reautenticação recente de 15 minutos pelo mecanismo atual. Adaptar a classificação de sensibilidade em `auth_http` para o caminho exato da coleção e seus segmentos, sem ampliar exceções de leitura. Nesse namespace não é necessário interpretar JSON antes de autorizar/classificar a ação. Aplicar `no-store`, inclusive nos erros anteriores ao negócio. OPTIONS e rotas/métodos inexistentes mantêm as políticas atuais.

Validar IDs inteiros não booleanos de 1 a 2147483647; fora do intervalo roteado recebe 400. Texto/negativo preservam 404 do roteador. Buscar Aluno inexistente ou ID de Administrador produz 404 `usuario_nao_encontrado`, sem dados. Essa restrição também impede agir sobre o próprio operador e dispensa fluxo de último Administrador neste recorte.

Novos corpos são objetos JSON com campos exatos. Limite local de 16 KiB, com 413 `corpo_muito_grande`; não alterar limite global da API. Erros do recorte usam `{erro,codigo}`: 400 `dados_invalidos`, 409 `email_em_uso`/`usuario_com_vinculos`, além de 401/403 existentes e 500 `erro_interno` sanitizado. Usar os adaptadores existentes, sem retornar mensagem SQL ou exceção de driver. Falhas transitórias de lock/deadlock, após rollback, retornam 409 `operacao_concorrente`, sem retry automático.

### 3. Criação e identificação

Reusar validações vigentes: nome 2–100 após trim; e-mail ASCII normalizado por trim/lower, até 254 e regras atuais; senha 8–128 sem transformação e confirmação igual. Reusar a preparação/hash `scrypt` já adotados, extraindo somente validação neutra de nome se necessária ao editar. Não importar helpers privados de outro caso nem criar política de senha distinta.

`CriarAlunoAdminService` fixa perfil `aluno` e ativo verdadeiro. Pode reutilizar a criação já usada pelo CLI, fornecendo perfil constante no servidor. Essa operação não chama cadastro público, não cria sessão do alvo, não registra termos e não troca a sessão do gestor. Body com perfil, ativo, aceite, hash ou ator é recusado. Unicidade é garantida pelo índice existente e violação específica de e-mail retorna 409; outros erros não são mascarados como duplicidade.

Uma conta recém-provisionada poderá ser excluída antes de receber qualquer vínculo. Após login, o titular consulta/aceita os termos por seu fluxo existente; plano e Tutor continuam sujeitos às permissões atuais. A ausência de aceite não se torna autorização presumida nem bloqueia funções que já eram independentes.

Editar exige ambos nome e e-mail, inclusive para conta inativa; demais campos são recusados. Nome/e-mail idênticos são no-op com 200. Mudança só de nome preserva sessões. Mudança real de e-mail atualiza a Model e revoga todas as sessões do alvo na mesma transação. Senha, perfil, ativo, criação e decisões permanecem.

### 4. Listagem especializada e dados mínimos

`ListarAlunosAdminService` valida somente `busca,status,pagina,por_pagina`; campos desconhecidos, inclusive filtro de perfil, retornam 400. Defaults: página 1 e 20 itens, tamanho 1–100, página 1–2147483647. Vazio explícito de paginação é inválido; busca vazia significa sem busca, com trim e até 254 caracteres. Status vazio/ausente significa todos os Alunos; valores válidos são `ativo` e `inativo`.

Busca é substring literal em nome ou e-mail; `%`, `_` e barras não viram curingas/instruções. Nome segue a comparação textual do catálogo MySQL, e busca no e-mail é normalizada para minúsculas. Ordem `criado_em DESC,id DESC`. Procedure retorna linhas limitadas e segundo conjunto `total_itens` no mesmo snapshot `ContextoLeitura`; página vazia conserva o total filtrado. Usar `envelope_paginado` existente.

Listagem retorna `id,nome,email_mascarado,perfil,ativo,criado_em`. Máscara é produzida na aplicação, mantendo só primeira letra local, `***` e domínio; fallback seguro `***` para eventual dado legado inválido. Não é anonimização nem autorização por si só. Detalhe autorizado usa e-mail completo por necessidade de edição; não expor decisões, atividades, sessões, hashes, user-agent ou métricas futuras. Senha nunca integra DTO.

### 5. Duas procedures novas, sem alteração de tabelas

Criar `017_gestao_alunos_procedures.sql`, com `SQL SECURITY INVOKER`, validação de parâmetros e nenhuma transação própria:

- `sp_alunos_admin(IN p_busca VARCHAR(254), IN p_ativo TINYINT, IN p_offset BIGINT, IN p_limite INT)`: ativo nulo/0/1, offset não negativo, limite 1–100. Somente `perfil='aluno'`; primeiro conjunto `id,nome,email,perfil,ativo,criado_em`, segundo `total_itens`. Nunca selecionar senha/hash para a listagem.
- `sp_usuario_gestao_bloqueado(IN p_usuario_id INT)`: retorna linha completa de Usuario por PK com `FOR UPDATE`, sem filtro de ativo. Resultado vazio indica ausência. A aplicação verifica perfil e serializa somente campos permitidos; hash presente no mapeamento privado não atravessa HTTP/logs.

`UsuarioRepository` encapsula CALL e consumo de resultados. Leitura de listagem fecha seu contexto próprio; lock usa `db.session` da transação externa e `populate_existing=True`, no padrão existente, para obter valores correntes em vez de snapshot/identity map antigos. Nenhum commit/rollback no Repository.

Reutilizar `sp_revogar_sessoes_usuario` através do Repository de autenticação. Não alterar as routines de 016 nem consultar tabelas privadas de Práticas, Simulados ou Plano para tentar prever exclusão. FKs fazem essa verificação em definitivo.

Atualizar `sql_resources.py`, referência oficial, pontos de reconhecimento/preflight e bootstrap para 017. As referências novas vêm da sequência oficial em schema descartável; não recalcular assinaturas antigas a partir do banco operacional. Estado parcial/drift deve bloquear reconhecimento sem recuo silencioso. Tabelas/índices/FKs, 21 mappers, sete módulos e migrations 000–016 permanecem iguais.

### 6. Atomicidade, concorrência e efeitos em login

Usar `TransactionManager` como único commit/rollback e Models com `confirmar=False`. Para editar, alterar status ou excluir: obter lock corrente do usuário → verificar perfil Aluno → validar ação/valores → atualizar/deletar → revogar sessões quando aplicável → confirmar. Consultas de detalhe não fazem lock de escrita. Helpers compartilhados de validação/erros devem ser pequenos e neutros, sem repositório CRUD genérico.

Desativação define ativo falso e revoga sessões. Repetição de desativação pode reforçar revogação sem mudar timestamps já revogados; reativação define ativo verdadeiro, sem tocar sessões. Login/criação de sessão já bloqueiam a mesma linha de Usuario; por isso uma sessão criada antes da desativação é alcançada pela revogação, e uma posterior é recusada. Ações já autorizadas antes da mudança não são canceladas por este recurso.

Troca de e-mail exige cuidado adicional: hoje login lê por endereço e depois bloqueia pelo ID. Um login iniciado com endereço antigo poderia atravessar a troca. Preservar e-mail normalizado esperado desde `LoginService`, conferindo-o tanto na leitura bloqueante de `ValidarSenhaService` quanto em `CriarSessaoService` antes de gravar a sessão. Usar parâmetro opcional para preservar chamadas de sessão anônima/reauth já existentes. Reusar os locks/procedures atuais; divergência recebe recusa neutra de credenciais, sem revelar a mudança. Não confiar no objeto ORM que pode ter sido atualizado/expirado após commit.

O ponto de ordenação é o commit da criação da sessão: se anterior à troca, a sessão é revogada; se a troca já confirmou, não confirmar sessão com e-mail esperado antigo. Uma resposta de login pode chegar depois por latência sem tornar utilizável uma sessão já revogada. Reativação nunca limpa `revogada_em`.

Excluir usa Model.deletar e deixa a FK arbitrar vínculos, sob o lock do alvo. Capturar somente erro MySQL 1451 para 409 `usuario_com_vinculos`, após rollback. Não remover sessões, comprovantes, autoria ou histórico para liberar a exclusão. Referência concorrente e DELETE são serializados pelo banco sem órfãos. Incluir sessão revogada como vínculo enquanto existir; limpeza operacional continua com suas regras anteriores.

Unicidade de e-mail usa constraint e mapeia apenas duplicidade 1062 da chave esperada. Erros 1205/1213 geram conflito transitório após rollback; não há retry automático. Falha ao revogar, atualizar ou confirmar não pode deixar e-mail/status parcialmente gravados. Testar por falhas reais controladas em schema descartável; mocks ficam restritos às unidades.

### 7. Duas telas com o padrão existente

Criar `/admin/usuarios.html` e `/admin/usuario.html`, JS/CSS próprios, usando shell, tokens, ativos oficiais, AuthUI, AdminUI/modal/guard e `apiRequest`. Habilitar somente Usuários na navegação. A listagem usa nome/e-mail mascarado, perfil fixo Aluno, status e criação, busca/status/paginação reais e ação Adicionar usuário. Não preencher métricas, status de verificação, perfis avançados ou datas fictícias.

Sem query, `/admin/usuario.html` é criação com nome/e-mail/senha inicial/confirmação; `?id=ID` é detalhe/edição por GET. Senha inicial não é chamada de temporária: não existe expiração ou troca obrigatória implementada. Usar `type=password`, `autocomplete=new-password`; não gerar/enviar senha por e-mail nem prometer esse recurso. Após POST confirmado, limpar senha/confirmação e trocar estado/URL para detalhe do ID devolvido, impedindo novo POST por Salvar ou recarregar.

Detalhe mostra identificação, ativo e criação, permite editar somente nome/e-mail e oferece status e exclusão condicionada. Perfil fica imutável. Avisar antes da troca de e-mail sobre encerramento das sessões. Desativar/reativar/excluir exigem confirmação clara; exclusão avisa que vínculos a impedem e oferece desativação como ação separada após 409. Cancelar não envia mutação. Não fingir existência de auditoria/exportação/estudos/recuperação/alteração de perfil ou revogação manual autônoma; futuras ações ficam ausentes ou desabilitadas com motivo.

Preservar nome/e-mail/filtros em falhas, guard de descarte e recuperação no contexto. Senhas são limpas ao concluir criação, perder/trocar identidade ou confirmar saída/cancelamento. Nunca usar storage, URL, logs ou HTML de erro para a senha. Na mesma conta, a pessoa informa a senha novamente se necessário; conta diferente segue descarte/recarga e não pode enviar o rascunho antigo.

Desabilitar mutação pendente e não repeti-la automaticamente, inclusive após reauth, erro de rede ou JSON inválido. Usar token/abort para consultas atrasadas; nunca preencher detalhe de ID errado ou após troca/bloqueio de conta. DOM com `textContent`; mensagens acessíveis, foco visível/contido nos diálogos, retorno de foco e teclado. Adaptar a 1440/390 px sem overflow da página. Registrar o recorte em documento técnico, preservando os binários e os documentos legais publicados: não é exclusão geral nem nova finalidade do plano.

### 8. Verificação e documentação

Unidades cobrem contratos, DTO/máscara, campos extras, perfil fixo, IDs, confirmação, normalização, erros, no-op e efeitos de sessão. Integrações são MySQL real: rotina/paginação, CRUD, unicidade concorrente, email/login nos dois locks, desativação/login, reativação, rollback e FK/corrida de exclusão. Não substituir integração por transporte/banco falso.

Testar 017 em instalação vazia, upgrade de 016 com dados, snapshot equivalente, baseline de cópia, reexecução zero, drift/parcial, dependência anterior inválida e preservação de checksums/dados/termos. Executar as suítes de migrations com `RUN_MYSQL_MIGRATION_INTEGRATION=1` além de `RUN_MYSQL_INTEGRATION=1`; esse opt-in não pode ficar no `.env`.

DOM testa rascunho, senha limpa, reauth sem replay, falhas e identidade. E2E/MySQL descartável demonstra: criar/listar/detalhar/editar/excluir conta nova sem vínculo; criar outra conta, titular fazer login/aceitar termos e ter DELETE bloqueado; desativar revoga acesso, reativar exige login novo e conserva evidências/histórico. Sem interceptação, trace/HAR/storage state autenticado ou chamadas reais ao Gemini.

README documenta rotas, Models/Services/procedures e aplicação de 017. Matriz CRUD/modelagem/mapa modular/telas descrevem o alcance de Alunos e as exceções, sem afirmar CRUD irrestrito para Administradores ou auxiliares. Encerrar F01 apenas após a prova; manter F02 e E01–E03 independentes. Não reescrever relatórios históricos nem editar documentos legais imutáveis.

## Risks / Trade-offs

- Cadastro público sempre possui aceite protegido → sua exclusão geralmente será bloqueada; demonstrar DELETE em conta administrativa nova sem vínculos e desativação nas utilizadas.
- Senha inicial conhecida pelo gestor → uso sintético e acesso administrativo restrito; recuperação/troca obrigatória continuam fora do recorte e não são prometidas.
- Mudança de e-mail concorre com login → conferir identidade esperada nos dois pontos de lock e revogar em transação única.
- FK impede exclusão sem prever a referência específica → 409 claro com opção distinta de desativar; evitar acoplamento e limpeza de outras áreas.
- Recorte menor que protótipo futuro → documentar ações indisponíveis e não oferecer controles fictícios ou alegar gestão completa de perfis/auditoria.

## Migration Plan

1. Preflight preserva mudanças existentes, incluindo a busca por ID ainda sem commit. Não tocar `.env` ou banco operacional ao propor.
2. Implementar 017 com bootstrap/reconhecimento; testar primeiro em schemas descartáveis. Instalação não cria conta padrão, aceite ou novo dado funcional.
3. Implementar backend e frontend, validar coberturas/regressões e documentar o pré-requisito de atualizar o banco antes das novas rotas. Em ambiente operacional, exigir backup validado antes de `migrate.py up` pelo procedimento vigente; instalação e prova são etapas distintas.
4. Publicar os lados compatíveis juntos. Reverter código desabilita a navegação/gestão e pode deixar as routines adicionais inertes; não apagar usuários já criados, restaurar sessões revogadas ou executar downgrade automático do histórico. Correção de DDL deve seguir migration compensatória revisada.
5. Verificar, sincronizar e arquivar depois de tarefas concluídas; commit/push continuam exigindo autorização explícita.
