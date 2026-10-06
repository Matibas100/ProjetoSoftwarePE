## Context

Consulte [proposal.md](proposal.md) para a motivação. O MVP mantém `Materia`, `Assunto` e `Questao` em Flask-SQLAlchemy, CRUD Active Record com commit interno, listagens sem filtros e uma única página HTML. No MySQL, Matéria → Assunto ainda usa `ON DELETE CASCADE`; Assunto → Questão já usa `RESTRICT`.

A implementação deve respeitar o Desktop V1, o runner de migrations SQL puro e os ADRs 001, 003, 004 e 006. Não existe módulo de Resumos, autenticação ou autorização que possa ser usado por esta change.

## Goals / Non-Goals

**Goals:**

- alcançar o schema Área → Matéria → Assunto → Questão sem perder IDs ou registros;
- entregar ADM-CON-001 e ADM-CON-002 funcionais contra o MySQL real;
- manter CRUD simples nas Models e reservar Repository para filtros, contagens, locks e impacto;
- preservar os consumidores legados sempre que não houver conflito com a obrigatoriedade de Área;
- garantir que transferência e seu registro sejam confirmados ou revertidos juntos.

**Non-Goals:**

- criar CRUD de Áreas, autenticação, perfis, permissões ou auditoria geral da plataforma;
- implementar Resumos ou fabricar suas contagens;
- alterar o modelo editorial de Questões ou a Stored Procedure existente;
- criar versão mobile ou redesenhar o Desktop V1;
- trocar Flask, SQLAlchemy, MySQL ou o frontend sem framework.

## Decisions

### 1. Modelo relacional incremental

```text
+----------------+       +----------------+       +----------------+
| areas_enem     | 1   N | materias       | 1   N | assuntos       |
| id             |<------| area_enem_id   |<------| materia_id     |
| codigo         |       | status         |       | nome_normaliz. |
| nome           |       | atualizado_em  |       | status         |
+----------------+       +----------------+       +-------+--------+
        RESTRICT                  RESTRICT                 | 1
                                                            | N
                                                    +-------v--------+
                                                    | questoes       |
                                                    | assunto_id     |
                                                    +----------------+
                                                          RESTRICT
```

`areas_enem` terá linhas fixas e códigos estáveis, nesta ordem: `linguagens` (`Linguagens`), `ciencias-humanas` (`Ciências Humanas`), `ciencias-natureza` (`Ciências da Natureza`) e `matematica` (`Matemática`). Não haverá rotas de mutação para essa tabela. As FKs Área → Matéria, Matéria → Assunto e Assunto → Questão usarão `ON DELETE RESTRICT`; atualizações de identificador continuarão proibidas na prática por IDs estáveis.

`materias` receberá `area_enem_id`, `status`, `criado_em` e `atualizado_em`. `assuntos` receberá `nome_normalizado`, `status`, `criado_em` e `atualizado_em`. O estado usa valores de domínio `ativa`, `inativa` e `arquivada`, evitando combinações contraditórias entre booleano e data de arquivamento.

Será criada `assunto_transferencias` com Assunto, Matéria de origem, Matéria de destino, impacto confirmado e instante. Suas FKs serão restritivas: um registro transferido passa a possuir uso histórico e não poderá ser apagado fisicamente.

Alternativas rejeitadas: enum nativo do MySQL, que torna evolução de valores mais rígida; Área como texto na Matéria, que não garante catálogo fixo; soft delete booleano separado, que permitiria estados conflitantes.

### 2. Normalização controlada com constraint no MySQL

A normalização de nomes seguirá uma função única no domínio:

1. normalizar a forma Unicode para NFC;
2. aplicar `trim` e converter toda sequência Unicode de espaços em um espaço ASCII;
3. converter para minúsculas;
4. validar novamente comprimento e vazio.

`nome_normalizado` usará collation `utf8mb4_0900_ai_ci`, tornando caixa, acentos e formas Unicode equivalentes na comparação. A constraint `UNIQUE (materia_id, nome_normalizado)` será a proteção concorrente definitiva. Criação, renomeação, reativação e transferência executarão validação legível no Service, mas converterão eventual violação concorrente em HTTP 409.

O registro original em `nome` não será reescrito para a forma normalizada. Registros arquivados permanecerão no mesmo índice; a API indicará reativação em vez de aceitar duplicata.

Alternativas rejeitadas: depender apenas de `nome`, por não tratar espaços; remover acentos manualmente em Python, pois seria difícil reproduzir com fidelidade no backfill SQL puro; índice parcial, indisponível no MySQL 8 para esta regra.

### 3. Backfill bloqueia classificação ou fusão arbitrária

As próximas migrations serão consecutivas e separarão preparação de imposição de constraints:

- criar as quatro Áreas e adicionar colunas inicialmente anuláveis;
- preencher status como `ativa`, timestamps e `nome_normalizado` dos registros existentes;
- classificar somente nomes de Matéria contemplados pelo mapeamento explícito abaixo;
- auditar Matérias sem Área e colisões normalizadas antes das constraints finais;
- interromper a migration de validação com mensagem segura quando houver pendência, sem excluir, fundir ou escolher valor padrão;
- após resolução explícita, tornar colunas obrigatórias, criar índices/constraints e trocar a FK Matéria → Assunto para `RESTRICT`;
- atualizar `create_database.sql` para equivalência de instalação limpa.

O runner já bloqueia avanço após falha. A migration de validação fará prechecks antes do DDL final; sua rotina auxiliar será removível e idempotente para permitir reconciliação e nova execução consciente.

O backfill compara nomes após trim, colapso de espaços, caixa e acentos. O mapeamento fechado é:

| Área | Nomes aceitos no backfill |
| --- | --- |
| Linguagens | Português, Língua Portuguesa, Literatura, Inglês, Língua Inglesa, Espanhol, Língua Espanhola, Artes, Educação Física, Tecnologias da Informação e Comunicação |
| Ciências Humanas | História, Geografia, Filosofia, Sociologia |
| Ciências da Natureza | Biologia, Física, Química |
| Matemática | Matemática |

Qualquer outro nome será reportado como não classificado. A implementação não ampliará essa lista durante o apply sem atualizar os artefatos.

Alternativas rejeitadas: quinta Área “A classificar”, porque viola o catálogo de quatro áreas; atribuição automática a uma Área genérica, porque corrompe semântica; mesclagem automática de Assuntos colidentes, porque perde identidade.

### 4. Ciclo de vida sem cascata de estado

- `ativa`: disponível para novos vínculos e edição normal;
- `inativa`: preservada e visível na administração, mas indisponível para novos vínculos;
- `arquivada`: preservada, omitida das consultas operacionais padrão e disponível para reativação controlada.

Arquivar Assunto com Questões é permitido e não altera as Questões. Arquivar Matéria com Assunto ativo ou inativo é bloqueado; os filhos devem ser arquivados ou transferidos individualmente, sem cascata de status. Reativar Assunto exige Matéria ativa e ausência de conflito normalizado. Reativar Matéria exige Área válida.

### 5. Contratos HTTP aditivos e casos de uso explícitos

As rotas existentes continuam para compatibilidade e recebem campos aditivos. `POST /api/materias` e alterações de Área exigirão `area_enem_id`; essa é a quebra declarada na proposta.

| Método e rota | Uso |
| --- | --- |
| `GET /api/areas-enem` | opções fixas para filtros e formulários |
| `GET /api/admin/materias` | busca, status, paginação e contagens de ADM-CON-001 |
| `GET /api/admin/assuntos` | busca, Área, Matéria, status, paginação e contagens de ADM-CON-002 |
| `GET /api/materias/<id>/impacto-exclusao` | contagens antes de excluir ou arquivar |
| `POST /api/materias/<id>/inativar|arquivar|reativar` | mudanças explícitas de ciclo de vida |
| `GET /api/assuntos/<id>/impacto-transferencia?materia_destino_id=<id>` | prévia da transferência |
| `POST /api/assuntos/<id>/transferir` | confirmação com destino e impacto esperado |
| `GET /api/assuntos/<id>/impacto-exclusao` | contagens antes da exclusão |
| `POST /api/assuntos/<id>/inativar|arquivar|reativar` | mudanças explícitas de ciclo de vida |

Listagens administrativas retornarão `{itens, pagina, por_pagina, total_itens, total_paginas}`. `pagina` terá padrão 1; `por_pagina`, padrão 20 e máximo 100; valores inválidos retornarão 400. A busca terá até 100 caracteres, comparação sem diferença de caixa ou acento e incidirá sobre nome e descrição. Ordenação padrão será por nome normalizado e ID, garantindo estabilidade. As contagens consideram vínculos de todos os estados para não ocultar impacto.

`GET /api/materias` e `GET /api/assuntos` manterão arrays e campos antigos; por padrão servirão itens ativos para novos vínculos e aceitarão um filtro administrativo explícito quando necessário. O campo `resumos` não será fabricado: a listagem administrativa de Assuntos retornará `resumos: null`, que a tela representa como `—` e “indisponível nesta versão”.

Para preservar o consumidor legado, `PUT /api/assuntos/<id>` continuará aceitando `materia_id`; quando houver troca real, o Controller encaminhará ao mesmo caso de uso transacional de transferência. ADM-CON-002 utilizará os endpoints de impacto e transferência para exigir confirmação visual.

### 6. Arquitetura e fronteira transacional

```text
Frontend
   --> Route
      --> Controller
         --> Service
            --> Model (CRUD simples)
            --> CatalogoRepository (filtros, contagens e locks)
            --> TransactionManager
               --> MySQL
```

Models continuarão responsáveis por busca por ID, criação, atualização e exclusão simples. `CatalogoRepository` concentrará JOINs, agregações, impacto e leituras com lock, sem duplicar CRUD ou confirmar transações. Nenhuma Stored Procedure nova é necessária; `sp_questoes_por_assunto` permanece no `QuestaoRepository`.

Conforme ADR-006, o `CrudMixin` manterá o modo autônomo como padrão e ganhará uma forma explícita de participar sem commit de uma transação externa. `TransactionManager` encapsulará `begin`, `commit` e `rollback`, sem expor `db.session` a Controller ou Service.

Na transferência, a prévia retornará `assunto_id`, `materia_origem`, `materia_destino` e `impacto: {questoes}`. A confirmação enviará `materia_destino_id` e `impacto_esperado: {questoes}`. A transação bloqueará o Assunto e as Matérias relevantes, recalculará impacto e conflito, comparará `impacto_esperado`, atualizará `materia_id`, inserirá `assunto_transferencias` e confirmará uma vez. Mudança de impacto retorna 409 com a prévia atualizada; destino igual à origem ou indisponível retorna 400; recurso ausente retorna 404; qualquer falha reverte tudo.

### 7. Exclusão depende do banco e de mensagem de domínio

O Service consulta o impacto para produzir mensagem útil, mas a FK continua sendo a última barreira contra corrida. Violação de integridade é convertida em 409, sem expor SQL. DELETE retorna 204 somente quando a exclusão física for permitida. Nenhum relacionamento ORM usará `delete-orphan` ou cascade de remoção.

### 8. Frontend preserva o MVP e adiciona duas páginas administrativas

Serão criadas páginas próprias para Matérias e Assuntos, com CSS administrativo compartilhado, módulos JavaScript separados por tela e utilitários comuns de API, modal, estado e formulário. A gestão de Questões atual continuará disponível e não será reescrita.

As páginas usarão os SVGs oficiais copiados do pacote congelado, sidebar/header do Desktop V1, filtros e tabelas em 1440 px. Apenas Matérias e Assuntos terão navegação funcional; itens de módulos fora do escopo não executarão ações fictícias. A tela será desktop-first, com comportamento de segurança mínimo em larguras menores sem criar um design mobile.

Os painéis de “outros estados” presentes na prancha são referência de estados, não conteúdo simultaneamente permanente. A interface mostrará sucesso, erro, impacto e bloqueio somente no contexto correspondente. O formulário manterá valores após falha e usará modal acessível para descarte, exclusão, arquivamento e transferência.

### 9. Testes e verificação

- testes unitários da normalização, validações, ciclo de vida, compatibilidade e transação;
- integrações MySQL reais para upgrade, backfill, FKs, unique composta, concorrência, rollback, filtros e todas as operações HTTP;
- regressão das APIs atuais e da Stored Procedure;
- testes DOM dos filtros, paginação, formulários, estados, modais, preservação e navegação por teclado;
- inspeção visual das duas páginas em 1440 px contra ADM-CON-001/002 e verificação dos estados aprovados;
- execução final dos validadores de cobertura e da suíte completa com opt-in explícito para MySQL.

### 10. Segurança e observabilidade no escopo disponível

Erros públicos não incluirão SQL, nomes internos de constraints ou credenciais. O registro de transferência não terá identidade de usuário até a futura capability de autenticação; guardará apenas dados de domínio suficientes para rastrear a operação. Logs técnicos registrarão correlação e erro seguro, nunca conteúdo de `.env`.

## Risks / Trade-offs

- **Dados existentes fora do mapeamento aprovado** → bloquear a constraint final, emitir pendências e exigir classificação explícita antes de continuar.
- **Colisões normalizadas existentes** → não mesclar; bloquear o upgrade e resolver cada colisão preservando IDs e vínculos.
- **DDL MySQL não transacional** → separar preparação e validação, executar prechecks antes do DDL restritivo e usar o bloqueio/reconcile do runner.
- **Mudança concorrente entre prévia e transferência** → lock curto, recálculo dentro da transação e comparação com o impacto esperado.
- **Contratos legados e itens inativos** → manter forma das respostas antigas e testar seletores ativos separadamente das listagens administrativas.
- **Coluna de Resumos sem domínio implementado** → mostrar indisponibilidade explícita, nunca zero fictício.
- **Shell administrativo sem autenticação** → não alegar proteção de acesso; manter a capability futura fora desta change.
- **Prancha combina múltiplos estados de exemplo** → implementar cada estado de forma contextual e validar visualmente a composição base.

## Migration Plan

1. Fazer backup e executar as consultas de auditoria em uma cópia do banco MVP.
2. Aplicar a migration preparatória: Áreas, colunas anuláveis, estados, timestamps, transferência e backfills seguros.
3. Resolver explicitamente Matérias não classificadas e colisões reportadas, sem apagar nem fundir registros.
4. Reconciliar eventual bloqueio consciente e aplicar a migration restritiva: `NOT NULL`, unique composta e FKs `RESTRICT`.
5. Validar fingerprint do schema, contagens e preservação dos IDs; atualizar o snapshot `create_database.sql`.
6. Publicar backend e frontend somente após as migrations obrigatórias estarem aplicadas.
7. Executar regressão completa e inspeção visual das duas telas.

Rollback não usará downgrade automático. Antes do passo 4, as novas estruturas são aditivas. Depois dele, reversão exige backup ou migration compensatória revisada; restaurar cascade destrutivo não será aceito como rollback normal.
