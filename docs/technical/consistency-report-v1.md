# Relatório de Consistência v1 — Plataforma ENEM

## 1. Escopo e fontes

Esta análise cruza o Inventário Mestre, o Handoff Mestre, o Protótipo Desktop V1 e os contratos existentes no MVP. Ela registra lacunas sem criar telas, rotas, entidades ou regras para preenchê-las.

## 2. Contagens verificadas

| Verificação | Resultado |
|---|---|
| IDs oficiais de telas | 60, todos únicos |
| Telas sem ambiente | Nenhuma |
| Telas sem módulo funcional | Nenhuma |
| Telas sem perfil | Nenhuma |
| Telas sem status de aprovação | Nenhuma |
| Telas aprovadas | 60 |
| Modais oficiais | 2, com IDs únicos |
| Estados catalogados | 80 |
| Páginas do Protótipo | 63: 60 telas, 1 variante visual adicional de resultado e 2 modais |
| Lacunas bloqueantes já registradas como resolvidas | 4 |
| Lacunas ainda abertas no inventário | 14: 10 importantes e 4 melhorias |
| Achados identificados originalmente neste relatório | 21 |
| Bloqueantes resolvidos nesta revisão | 1 |
| Achados ainda abertos | 20: 16 antes dos módulos correspondentes e 4 melhorias futuras |
| Bloqueantes para iniciar a modelagem técnica | 0 |

Não foram encontrados IDs duplicados, tela sem módulo, tela sem perfil ou tela sem aprovação. O número de páginas do protótipo não representa 63 telas únicas: a diferença é explicada por uma variante de resposta correta/incorreta e pelos dois modais.

## 3. Histórico do bloqueante resolvido

| Ref. | Tipo | Achado original | Resolução |
|---|---|---|---|
| EST-DUP-001 | Estado inconsistente | “Possível duplicidade” aparece corretamente como indicador transversal, mas uma célula da planilha o descreve como “mutuamente exclusivo no mesmo eixo”. Uma modelagem literal criaria uma máquina de estados incorreta. | **RESOLVIDO — definição corrigida por errata técnica.** Possível duplicidade pode coexistir com o estado principal, exige decisão própria e não substitui o estado editorial/processual. **Bloqueada por duplicidade** permanece estado principal, sem avanço até resolução explícita. |

A correção está formalizada em [Errata — Desktop V1](../design/desktop-v1/ERRATA.md). Os artefatos binários congelados não foram modificados.

## 4. Resolver antes do respectivo módulo

| Ref. | Tipo | Achado | Classificação | Encaminhamento necessário |
|---|---|---|---|---|
| PUB-AUT-002 | Informação ausente | A verificação de e-mail pendente existe como estado, mas não possui tela/rota aprovada. | Resolver antes de `autenticacao`. | Aprovar fluxo, destino, expiração e reenvio antes do contrato. |
| ADM-CON-001/002 | Modal/destino ausente | Confirmações de exclusão e descarte são especificadas, mas não existem como modais isolados aprovados. | Resolver antes de `catalogo_academico`. | Validar reutilização do componente modal e textos; não criar tela automaticamente. |
| ADM-QUE-002 | Botão sem destino fechado | “Visualizar como aluno” não possui estado/tela exclusiva de preview. | Resolver antes de `questoes`. | Aprovar reutilização somente leitura ou contrato de preview. |
| ADM-QUE-005 | Estado final ausente | Conclusão e retomada da importação não possuem tela final separada. | Resolver antes de `importacoes`. | Definir se a tela de validação acumula esses estados. |
| GLOBAL-NOT | Botão sem destino | Ícone de notificações no cabeçalho não possui painel ou rota definida. | Resolver antes de `usuarios`/`auditoria`. | Aprovar destino ou manter ação indisponível. |
| GLOBAL-PERFIL-ADM | Tela/perfil divergente | O perfil aparece no ambiente administrativo, mas a única tela de Perfil aprovada é do Aluno. | Resolver antes de `usuarios`. | Decidir reutilização autorizada ou novo artefato em versão futura. |
| GLOBAL-SESSAO | Fluxo ausente | Sessão expirada e retorno seguro ao destino original não estão representados no board. | Resolver antes de `autenticacao`. | Documentar redirect, contexto preservado e mensagens antes de implementar. |
| ADM-QUE-001 | Nomenclatura divergente | Uma coluna usa “Nível”, enquanto o termo congelado é “Dificuldade”. | Resolver antes de `questoes`. | Usar “Dificuldade” no contrato futuro e corrigir a fonte na próxima versão. |
| ORIGEM-IA | Nomenclatura divergente | Há “Gerada por IA” e “Gerado com auxílio de IA”. | Resolver antes de `questoes`/`importacoes`. | Canonizar: Manual, Oficial ENEM, Gerado com auxílio de IA, Conteúdo adaptado com fonte. |
| ADM-RED-002 | Estado/eixo ambíguo | Falha, timeout, revisão humana e outros indicadores podem ser interpretados como categorias acumuláveis. | Resolver antes de `redacao`. | Aprovar eixo principal exclusivo e indicadores transversais. |
| API-MAT | Rota atual incompatível com a tela completa | CRUD atual não possui área, status editorial, contagens, paginação ou governança exigidos pela administração definitiva. | Resolver antes de evoluir `catalogo_academico`. | Preservar contratos atuais e definir contratos adicionais/versionados. |
| API-ASS | Rota atual incompatível com a tela completa | CRUD atual não possui status editorial, contagens, paginação nem unicidade formal por matéria. | Resolver antes de evoluir `catalogo_academico`. | Preservar endpoints atuais; aprovar schema e contratos complementares. |
| API-QUE | Rota/modelo atual incompatível com o domínio completo | Questão atual não representa mídia, origem editorial, versão, autoria, taxonomia ampla ou indicador de duplicidade. | Resolver antes de evoluir `questoes`. | Evoluir por migrations versionadas e compatibilidade temporária. |
| API-BUSCA-QUE | Consulta limitada | A consulta existente exige `assunto_id` e não cobre gestão completa, filtros, paginação nem sessão de prática. | Resolver antes de `questoes`/`praticas`. | Manter a procedure atual e definir novas consultas somente após contratos. |
| AUTZ-001 | Permissão ausente | As rotas atuais não aplicam autenticação ou autorização por perfil. | Resolver antes de expor módulos definitivos. | Escolher estratégia de autenticação e matriz de permissões; não adaptar silenciosamente o MVP. |
| FK-MAT-ASS | Política divergente/aberta | A experiência administrativa pressupõe tratamento controlado da exclusão, enquanto a política definitiva Matéria → Assunto não está aprovada. | Resolver antes de `catalogo_academico`. | Decidir entre restrição, arquivamento e transferência; preservar dados existentes. |

## 5. Melhoria futura

| Ref. | Tipo | Achado | Encaminhamento futuro |
|---|---|---|---|
| RESP-001 | Cobertura visual | O Desktop está aprovado, mas prioridades de colunas, empilhamento e comportamento responsivo não foram testados. | Tratar o mobile/responsivo como versão própria e validar por breakpoint. |
| ADM-TAB-001 | Usabilidade | Densidade, cabeçalho fixo e navegação por teclado das tabelas administrativas aguardam validação funcional. | Incluir testes de acessibilidade e uso com grande volume. |
| ALU-TUT-001 | Navegação | Retorno contextual/deep link do tutor está conceitual, sem especificação fechada. | Definir contrato de contexto e fallback ao evoluir `tutor_ia`. |
| ALU-DES-001 | Regra de apresentação | Limiares mínimos de amostra para insights não estão congelados. | Aprovar com a equipe pedagógica antes de mostrar tendências. |

## 6. Entidades citadas e ainda não definidas no schema

As fontes citam conceitos que não existem no banco do MVP. Eles não são automaticamente Models nem autorização para criar tabelas:

- usuário, perfil, papel e permissão;
- sessão, verificação de e-mail e recuperação de senha;
- prática, resposta, tentativa e sessão de estudo;
- simulado, versão, agendamento, aplicação e resultado;
- desempenho, recomendação e plano de estudos;
- resumo, versão editorial e publicação;
- tema, redação, correção automática e revisão humana;
- conversa, mensagem e contexto do tutor;
- lote de importação, item importado e validação;
- revisão editorial, parecer e solicitação de ajuste;
- evento e trilha de auditoria;
- mídia, arquivo e notificação.

Para cada conceito, propriedade do módulo, identidade, ciclo de vida e persistência permanecem **A definir** até aprovação arquitetural.

## 7. Compatibilidade dos contratos atuais

| Contrato atual | Reuso imediato | Evolução posterior |
|---|---|---|
| `POST /api/materias` | Cadastro básico administrativo | status, auditoria, autorização e eventual versionamento |
| `GET /api/materias` | Selects e listagem básica | paginação, filtros, contagens e estados editoriais |
| `PUT /api/materias/<id>` | Edição básica | concorrência, autorização e governança |
| `DELETE /api/materias/<id>` | Exclusão sob regras atuais | política definitiva de dependências/arquivamento |
| `POST /api/assuntos` | Cadastro básico administrativo | taxonomia, status e auditoria |
| `GET /api/assuntos` | Selects e listagem básica | filtro por matéria, paginação e contagens |
| `PUT /api/assuntos/<id>` | Edição básica | concorrência e governança editorial |
| `DELETE /api/assuntos/<id>` | Exclusão restrita por questões | arquivamento e política editorial |
| `POST /api/questoes` | Cadastro mínimo | mídia, origem, versão, autoria e workflow |
| `GET /api/questoes/por-assunto` | Busca especializada básica | filtros administrativos, paginação e contratos de prática |

Nenhuma incompatibilidade autoriza alterar as rotas existentes nesta etapa. Endpoints futuros permanecem registrados no mapa como `NOVO — contrato ainda será definido`.

## 8. Conclusão

O conjunto visual é internamente contável e não possui lacuna visual bloqueante declarada. Dos 21 achados identificados originalmente, o único bloqueante foi resolvido pela Errata técnica; permanecem 20 achados abertos — 16 para resolver antes dos módulos correspondentes e 4 melhorias futuras. Assim, existem 0 bloqueantes para iniciar a modelagem técnica. Nenhuma tela ou funcionalidade foi criada para preencher as lacunas restantes.
