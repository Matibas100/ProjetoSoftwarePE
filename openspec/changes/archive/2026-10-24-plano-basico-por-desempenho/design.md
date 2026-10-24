# Design — Plano básico

## Context

Ver [proposal.md](proposal.md). O item 5 fornece diagnóstico com origem/período/amostra; itens 2/3 fornecem elegibilidade e prática. Não existem disponibilidade/agenda ou metas no perfil. O plano mínimo é uma lista ordenada, sem inferir duração, data ou prioridade de assunto nunca respondido. ADRs 001/002/003/005/006 se aplicam.

## Goals / Non-Goals

**Goals:** priorização determinística e persistida, explicação estável e recálculo seguro.

**Non-Goals:** reproduzir calendário semanal completo, recalcular automaticamente, modificar métricas ou concluir práticas em nome do Aluno.

## Decisions

### 1. Seleção e explicação

Usar Service de diagnóstico do item 5 com período padrão de 30 dias UTC. Elegíveis: grupos de Assunto com >=5 respostas, Assunto/Matéria atuais ativos e ao menos uma Questão com versão atual publicada elegível. Exigir que o vínculo atual Assunto–Matéria coincida com o grupo histórico para não recomendar dificuldade antiga sob classificação nova após transferência. Sem correspondência, excluir grupo e orientar novas práticas; não reclassificar fatos.

Ordenar por taxa exata de acerto crescente (comparar frações antes do arredondamento), total de respostas decrescente e `assunto_id` crescente. Selecionar no máximo três, sem preencher vaga com assunto de amostra insuficiente. Mesmo 100% pode aparecer se houver dados suficientes; explicar como prioridade relativa entre os assuntos praticados, sem afirmar dificuldade inexistente. Exemplo: 2/10 precede 4/10; empate 2/10 e 1/5 prioriza 2/10 pela maior amostra.

Snapshot de cada item guarda IDs/rótulos, acertos, total, percentual exibido, período, limiar, posição e justificativa textual derivada desses dados. Diagnóstico indisponível é erro, não falta de dados. Sem candidatos, retornar estado `sem_base_suficiente` sem criar plano vazio; plano anterior permanece intacto em tentativa de recálculo.

### 2. Persistência e concorrência

Criar `planos_estudo` (ID, usuário, geração sequencial, atual bool, período, gerado_em UTC, `chave_envio` UUID) e `plano_estudo_itens` (ID, plano, Assunto/Matéria, posição, snapshot de justificativa, estado pendente/concluido, concluido_em UTC). `UNIQUE(usuario_id, geracao)`, `UNIQUE(usuario_id, chave_envio)`, posição/Assunto únicos por plano e FKs `RESTRICT`. Garantir um plano atual por usuário com chave única em coluna gerada que retorna usuário somente quando `atual=true`, NULL nos anteriores. Snapshots são imutáveis; somente estado/data de conclusão muda.

Service de geração/recálculo usa `TransactionManager`; serializar pelo usuário via Repository especializado para lock, leitura final de elegibilidade e persistência. Leitura do diagnóstico participa da mesma visão consistente da geração; relógio/período fixados uma vez. Calcular novo plano antes de desativar anterior; criar novo plano, seus itens e trocar atual em um commit. Models CRUD com `confirmar=False`; Repository não duplica gravação. Nunca limpar itens concluídos do plano anterior.

### 3. API proposta

| Operação | Contrato |
| --- | --- |
| `GET /api/aluno/plano` | 200 `{estado:sem_plano, plano:null}` ou `{estado:disponivel, plano:{id, geracao, periodo, gerado_em, itens:[...]}}`; item inclui posição, snapshot, estado/data e `disponivel_para_pratica` calculada no momento da consulta |
| `POST /api/aluno/plano/gerar` | `{chave_envio}` -> 201 com plano; sem candidatos -> 200 `{estado:sem_base_suficiente, plano:null}`; havendo plano atual, 409 orientando consulta/recálculo |
| `POST /api/aluno/plano/recalcular` | `{chave_envio, plano_atual_id, confirmar:true}` -> 201 com novo plano; prévia desatualizada -> 409; sem candidatos -> 200 `sem_base_suficiente` com plano anterior preservado no payload |
| `POST /api/aluno/plano/itens/<id>/concluir` | `{confirmar:true}` -> 200 com item concluído; só item próprio do plano atual; repetição retorna mesmo estado/data; item histórico não pode mudar (409) |

Chave UUID e corpo estrito, sem `usuario_id`, taxa, prioridades ou período enviados pelo cliente. Replay da mesma chave e operação/dados retorna mesmo plano com 200, inclusive se hoje ele já for histórico; chave divergente retorna 409. Armazenar tipo e ID de plano anterior associados à chave para validar replay. Erros 400 entrada, 401 sessão, 403 perfil/CSRF/Origin, 404 recurso ausente/alheio; no-store e origem/CSRF em mutações. Sem geração automática no GET.

Itens concluem por decisão manual do Aluno, não significam domínio pedagógico nem conclusão automática de uma prática. Iniciar prática é link para `/aluno/questoes.html?assunto_id=<id>`; o fluxo do item 3 valida a seleção e inicia tentativa. Se conteúdo foi retirado, conservar o item/justificativa e indicar indisponibilidade, sem criar Questão fictícia. Não expor usuário alvo ao Administrador nem alterar histórico acadêmico.

### 4. Interface

Criar `/aluno/plano.html` usando hierarquia e identidade de ALU-PLA-001 para o recorte de lista. Oferecer gerar, iniciar prática, concluir e recalcular com confirmação de substituição do plano atual. Link no dashboard sem alterar a resposta de desempenho do item 5. Mostrar explicação como `2 acertos em 10 respostas nos últimos 30 dias`, datas reais, amostra insuficiente e ausência de conteúdo. Recursos de calendário/reagendamento futuros indisponíveis. Falha de API/sessão preserva plano visível e exige reenvio explícito; troca de identidade limpa contexto. Validar teclado/foco/estados e referência visual sem editar binários.

## Risks / Trade-offs

- Poucos dados -> não gerar prioridades e orientar prática livre; não inventar diagnóstico.
- Conteúdo fica indisponível -> item preservado e consulta calcula disponibilidade atual; recálculo explícito pode substituir.
- Plano não se atualiza com cada resposta -> snapshot explica o momento da geração e o botão de recálculo deixa a decisão com o Aluno.

## Migration Plan

Item 5 deve estar encerrado; reler contratos finais no preflight. Próxima migration consecutiva disponível (esperada 009 se item 5 não adicionar schema), snapshot equivalente, tabelas vazias sem planos artificiais. Validar banco vazio/upgrade/reexecução, unique de plano atual, rollback de geração e regressão no MySQL real. Backup ou compensação para reversão, preservando planos anteriores e conclusões. Não definir purge/retenção geral, ainda fora do escopo da OD-08.
