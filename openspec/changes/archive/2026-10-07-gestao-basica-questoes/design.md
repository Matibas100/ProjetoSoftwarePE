# Design — Gestão básica de Questões

## Context

Ver [proposal.md](proposal.md). `Questao` guarda conteúdo mutável; o cadastro retorna seus campos legados e a busca usa `sp_questoes_por_assunto`. A autenticação já restringe esses endpoints ao Administrador. `TransactionManager` e CRUD com `confirmar=False` já existem. Aplicam-se as conventions e os ADRs 001–006; não haverá mídia.

## Goals / Non-Goals

**Goals:** evoluir a estrutura atual para versões estáveis sem quebrar o MVP; permitir Administração utilizável e leitura futura segura por Services de conteúdo.

**Non-Goals:** reorganizar pastas em módulos, mudar framework, implementar revisão multiperfil ou usar os PDFs como conteúdo do banco. A publicação mínima abaixo é uma decisão proposta para o recorte escolar, não um contrato já existente no Desktop V1.

## Decisions

### 1. Identidade e rascunho compatíveis

Manter `questoes.id` e seus campos atuais como rascunho/representação administrativa de compatibilidade. Acrescentar `status` (`rascunho`, `publicada`, `arquivada`), `revisao` inteira iniciando em 1, datas e `versao_publicada_id` anulável. Edição incrementa revisão, sem alterar o ponteiro publicado. Alternativa rejeitada: atualizar conteúdo publicado diretamente, incompatível com ADR-005.

Criar `questao_versoes`: ID, `questao_id`, número sequencial, `revisao_origem`, estado do snapshot (`rascunho` no backfill ou `publicada`), conteúdo completo A–E/gabarito/explicação/dificuldade, IDs e nomes de Assunto/Matéria/Área, autoria anulável para legado, origem (`legado` ou `manual`) e instante UTC. `UNIQUE(questao_id, numero)` e FKs `RESTRICT`; ponteiro somente para versão da própria Questão, validado na transação. Snapshots são append-only; versões publicadas jamais editáveis. A revisão de origem permite reconhecer publicação repetida sem criar nova versão.

Criar `questao_eventos`: Questão, versão opcional, ator, ação (`cadastro`, `edicao`, `revisao`, `aprovacao`, `publicacao`, `arquivamento`), motivo e instante UTC. Cadastro/edição registram o operador e motivo técnico da ação; revisão/aprovação/publicação/arquivamento registram o motivo confirmado. Registro append-only acompanha cada operação na mesma transação, sem credenciais. Retenção automática e exclusão física estão fora deste recorte.

### 2. Revisão mínima e retirada de uso

`POST /api/questoes` preserva validações/payload/status 201 e cria rascunho. `PUT /api/questoes/<id>` recebe campos de conteúdo e `revisao` obrigatória; valida como cadastro e aceita alteração parcial, recusando campos desconhecidos. Questão arquivada não aceita edição ou publicação (409); reativação fica fora do escopo.

Publicar é ação explícita do Administrador: `{revisao, confirmar: true, motivo}` com motivo de 3–500 caracteres após trim. Conferir conteúdo obrigatório, cinco alternativas não vazias, gabarito A–E, dificuldade e catálogo ativo. Criar snapshot, registrar revisão/aprovação/publicação pelo mesmo operador e atualizar o ponteiro atomicamente. Não há publicação automática no cadastro/backfill nem exigência de segundo usuário. Nova edição gera nova publicação; versão anterior permanece consultável para histórico. Publicação de revisão já publicada retorna a mesma versão, sem duplicar eventos.

Arquivar exige confirmação, revisão, motivo e reautenticação recente de 15 minutos; deixa o ponteiro preservado para históricos, bloqueando novos usos. Repetição de arquivamento já concluído retorna estado atual sem outro evento. Não criar `DELETE` de Questão.

### 3. Contratos propostos

| Operação | Resposta e regra |
| --- | --- |
| `GET /api/admin/questoes` | Envelope atual do catálogo: `itens`, `pagina`, `por_pagina`, `total_itens`, `total_paginas`; padrão 1/20, máximo 100; filtros `busca` (enunciado, até 100 caracteres), `area_enem_id`, `materia_id`, `assunto_id`, `dificuldade`, `status`; ordem ID decrescente; sem status inclui todos |
| `GET /api/questoes/<id>` | `{questao: <campos legados>, status, revisao, versao_publicada_id, versoes: [{id, numero, estado}]}`; somente Administrador |
| `PUT /api/questoes/<id>` | 200 com o mesmo envelope de detalhe; não publica |
| `POST /api/questoes/<id>/publicar` | 200 com detalhe e versão publicada, confirmação/revisão/motivo e reautenticação |
| `POST /api/questoes/<id>/arquivar` | 200 com detalhe; confirmação/revisão/motivo e reautenticação |

POST legado e procedure continuam com os mesmos campos, ordenação e comportamento de consulta administrativa, inclusive sobre indisponíveis. Não alterar o SQL da procedure para o Aluno. Erros novos: 400 entrada/filtro inválido, 404 recurso ausente, 409 revisão/estado conflitante; manter 401/403 e códigos existentes de autenticação. HEAD herda GET. Busca/filtros combináveis retornam página vazia, não erro.

### 4. Integração, atomicidade e segurança

Preservar `Frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL`. Models fazem CRUD; Repository somente listagem filtrada, snapshots especializados e locks; todo `CALL` continua no Repository. Services de conteúdo expõem versão publicada elegível e versão histórica por ID aos próximos módulos, com DTO público separado do conteúdo de correção. Elegibilidade: identidade não arquivada, versão igual ao ponteiro publicado e Assunto/Matéria referenciados ativos; nomes/classificação da versão são congelados. Arquivamento não remove leitura de uma tentativa já iniciada.

Service envolve rascunho/snapshot/eventos/ponteiro em `TransactionManager`; Models usam `confirmar=False`. Lock da Questão serializa numeração e revisão; divergência de revisão retorna 409, sem retry automático. Publicação confere e bloqueia catálogo relevante na mesma transação para evitar publicação concorrente com inativação. Adicionar política explícita de publicação sensível em `auth_http.py`, mantendo CSRF/Origin/no-store e autorização administrativa. Renderizar textos com `textContent`, sem HTML arbitrário.

### 5. Interface mínima

Criar `/admin/questoes.html` e `/admin/questao.html` com moldura existente e referências ADM-QUE-001/002. Revisão/publicação é ação contextual com resumo e confirmação; não criar uma fila completa. Botões/importação/IA/mídia fora do recorte não executam ações fictícias. Preservar formulários/filtros em erro, recuperação de sessão e reautenticação no contexto, foco, teclado e proteção de alterações não salvas.

## Risks / Trade-offs

- Duplicação entre rascunho e snapshot -> um único Service de publicação e adaptador legado explícito.
- Taxonomia pode ser renomeada/transferida -> snapshot preserva IDs e rótulos publicados; filtros administrativos usam catálogo atual, histórico usa snapshot.
- Revisão pelo próprio Administrador -> decisão mínima explícita e auditada; governança definitiva permanece para outra change.

## Migration Plan

Usar a próxima versão consecutiva livre do runner (atualmente 006), sem editar migrations aplicadas. Auditar dados e backup antes do upgrade; backfill cria snapshot inicial de origem `legado`, não publicado, preservando IDs e conteúdo. Autoria histórica permanece nula, sem inventar usuário/data de criação original. Novas Questões começam sem snapshot até a publicação.

Validar banco vazio, upgrade de 005, backfill, repetição do runner, equivalência do snapshot `create_database.sql`, procedure e regressões. Disponibilizar API/telas somente com schema aplicado. Falha operacional exige reconciliação do runner; reversão por backup ou migration compensatória, sem apagar versões utilizadas. Não executar migrations nesta fase de proposta.
