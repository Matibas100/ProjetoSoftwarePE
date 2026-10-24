# Design — Prática e histórico

## Context

Ver [proposal.md](proposal.md). O item 2 entrega versões publicadas e o item 1 já oferece sessão, CSRF e recuperação no contexto. O middleware atual trata quase toda API não acadêmica como administrativa: abrir rotas de Aluno exige regra explícita, sem liberar o gabarito legado. Aplicam-se ADRs 001/002/003/005/006.

## Goals / Non-Goals

**Goals:** uma tentativa por Questão, correção no servidor, resultado repetível e privado; preservar a classificação e a versão estudada.

**Non-Goals:** selecionar sequências, contar desempenho aqui, reutilizar tentativas de prática para armazenar respostas de simulados ou guardar progresso em storage do navegador.

## Decisions

### 1. Dados da tentativa

Criar `pratica_tentativas`: ID, `usuario_id`, `questao_versao_id`, `chave_envio` UUID, estado (`em_andamento`, `respondida`), alternativa escolhida anulável, `correta` anulável, início/resposta em UTC e IDs/rótulos de classificação copiados da versão. FKs `RESTRICT`, `UNIQUE(usuario_id, chave_envio)`, índice por usuário/data/ID e check de estados/resposta A–E. Estado respondida exige resposta, correção e data; em andamento mantém esses campos nulos. A FK à versão congela conteúdo/gabarito e o snapshot de classificação protege agrupamento futuro.

Não criar uma sessão de prática com itens neste MVP. Novas tentativas podem repetir uma Questão e são registros independentes; reenvio da mesma chave não é uma nova tentativa.

### 2. API segura e correção

| Operação | Contrato proposto |
| --- | --- |
| `GET /api/aluno/questoes` | Filtros `materia_id`, `assunto_id` positivos e paginação 1/20, máximo 100; envelope do catálogo; ordem `questao_id` crescente; itens `{questao_id, questao_versao_id, enunciado, alternativa_a..e, dificuldade, assunto, materia}` sem gabarito/explicação |
| `POST /api/aluno/praticas` | `{questao_versao_id, chave_envio}`; 201 `{id, estado, questao: <DTO seguro>}`; chave repetida com mesmo conteúdo retorna a mesma tentativa com 200, divergência retorna 409 |
| `GET /api/aluno/praticas` | Histórico somente de respondidas, filtro `assunto_id`, envelope paginado; ordem resposta/ID decrescente; item `{id, questao_versao_id, resposta_escolhida, correta, respondida_em, assunto, materia}` |
| `GET /api/aluno/praticas/<id>` | Estado e questão segura; se respondida, acrescentar resposta, correta, gabarito, explicação, data e classificação histórica |
| `POST /api/aluno/praticas/<id>/resposta` | Somente `{alternativa}` em A–E; 200 com detalhe corrigido persistido; campos extras inclusive `correta`, gabarito ou usuário geram 400 |

Antes de iniciar, verificar elegibilidade via Service do item 2; versão inexistente 404 e indisponível/superada 409, sem trocar versão silenciosamente. Depois de iniciada, pode concluir com a versão capturada mesmo que nova versão seja publicada ou conteúdo arquivado. A explicação ausente aparece como indisponível, sem texto inventado.

Comparar alternativa ao gabarito da versão no servidor. Reenvio de mesma resposta retorna o resultado persistido; resposta diferente após conclusão retorna 409. Corrigir nunca modifica versão nem recalcula resposta histórica.

### 3. Permissão, propriedade e transação

Adicionar política `/api/aluno/*` para perfil `aluno`; Administrador não usa esses endpoints para se passar por estudante (403). Usuário vem da sessão, jamais do corpo/query. Detalhes de recurso ausente ou pertencente a outro Aluno retornam o mesmo 404; coleção já filtra dono. Manter rotas administrativas, HEAD, 404/405, no-store, cookies/CSRF/Origin e logout existentes.

Cada caso de uso tem Service próprio; Controller adapta HTTP e não acessa sessão SQLAlchemy. Models mantêm CRUD com `confirmar=False`; Repository só seleção elegível especializada, histórico/locks. Service usa `TransactionManager`; lock de tentativa serializa correção, constraint trata criação idempotente. Concorrência com mesma resposta devolve o mesmo resultado, com respostas diferentes apenas uma vence e a outra recebe 409. Falha antes do commit não cria tentativa parcialmente corrigida.

Service de leitura de práticas fornece a desempenho fatos concluídos com `{id, usuario_id, questao_versao_id, respondida_em, alternativa, correta, classificacao}`. Não conceder acesso de escrita externo nem duplicar esses fatos em simulados.

### 4. Interface

Criar `/aluno/questoes.html`, `/aluno/questao.html?tentativa_id=<id>` e `/aluno/historico.html`; link no início existente. ALU-QUE-001 filtra/escolhe e inicia tentativa; ALU-QUE-002 responde; ALU-QUE-003 é o estado de correção persistida no mesmo contexto. Histórico reutiliza esses componentes sem inventar novo ID oficial Desktop V1.

Após recarga, consultar tentativa no servidor. Antes de resposta não incluir gabarito em HTML, script, payload ou atributos DOM. Preservar seleção local em falha de rede/sessão e permitir reenvio explícito; não armazenar dados em localStorage. Troca de conta exige limpar/recuperar contexto segundo `AuthUI`; não mostrar histórico da identidade anterior. Teclado, labels, foco, carregamento/vazio/erro/sucesso seguem referências oficiais.

## Risks / Trade-offs

- Aluno repete a mesma questão -> permitido e contado como tentativa real; métricas futuras explicitarão isso.
- Reenvio após falha -> chave estável e correção idempotente, não desabilitação visual como única defesa.
- Retenção geral ainda aberta (OD-08) -> não introduzir purge, exclusão de conta ou prazo definitivo nesta change.

## Migration Plan

Prérequisito: item 2 aplicado/verificado/sincronizado/arquivado. Criar próxima migration consecutiva (esperada 007), snapshot equivalente e índices; não backfillar tentativas fictícias. Validar instalação limpa/upgrade/idempotência/rollback operacional no MySQL real, mantendo procedure e catálogo. Reversão por backup/compensação, preservando respostas; código não deve ser disponibilizado com schema incompleto. Antes de apply, reler a versão final dos contratos do item 2 e reconciliar qualquer divergência nos artefatos.
