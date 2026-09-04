## Context

Veja [proposal.md](proposal.md) para a motivação. Atualmente `create_database.sql` representa o schema consolidado, enquanto `001_restrict_delete_assuntos.sql` e `002_create_sp_questoes_por_assunto.sql` dependem de execução manual, contêm `USE plataforma_enem` e não possuem histórico persistente.

O MySQL 8 oferece atomicidade por instrução DDL em InnoDB, mas DDL encerra transações implicitamente. Assim, uma migration com várias instruções não pode prometer rollback total. `DELIMITER`, usado pela migration `002`, é interpretado pelo cliente MySQL e não deve ser enviado ao servidor.

A infraestrutura é operacional e fica fora das camadas de negócio. Ela não passa por Route, Controller, Service ou Repository e não altera o uso de `QuestaoRepository` para `CALL sp_questoes_por_assunto`.

## Goals / Non-Goals

**Goals:**

- Manter SQL MySQL explícito como conteúdo exclusivo das migrations.
- Criar um runner pequeno, determinístico, auditável e coberto por testes.
- Atender tanto schema vazio quanto os estados legados conhecidos sem perda de dados.
- Detectar drift, concorrência, falhas parciais e execução interrompida antes de avançar.
- Preservar a configuração, dependências, contratos e comportamento do MVP.

**Non-Goals:**

- Criar um framework genérico de migrations ou interpretar toda a gramática SQL.
- Executar migrations automaticamente na inicialização do Flask.
- Oferecer downgrade automático ou prometer atomicidade entre múltiplos DDLs.
- Alterar schema funcional além de formalizar o histórico já existente.
- Aceitar automaticamente schemas desconhecidos como baseline.

## Decisions

### 1. Runner Python mínimo e migrations em SQL puro

O comando operacional será `python backend/database/migrate.py <comando>`. O runner usará PyMySQL, já presente no projeto, para conexão e a biblioteca padrão para CLI, descoberta e SHA-256. Não haverá Alembic, Flask-Migrate, metadata ORM ou nova dependência.

Comandos previstos:

- `status`: valida arquivos e histórico, mostra versões e estados sem alterar o banco além da criação inicial controlada da tabela técnica quando necessário;
- `up`: aplica o sufixo pendente da sequência;
- `baseline`: sob confirmação explícita, reconhece um estado legado validado sem executar seus DDLs;
- operação de reconciliação documentada: desbloqueia uma falha somente após intervenção consciente, sem tentar desfazer DDL automaticamente.

Alternativas rejeitadas: Alembic/Flask-Migrate contraria o escopo; chamar o executável `mysql` complicaria credenciais, portabilidade e coordenação entre conexões; executar na inicialização da API misturaria deploy com tráfego e ampliaria privilégios da aplicação.

### 2. Convenção e sequência imutável

Arquivos oficiais seguirão `NNN_descricao_em_snake_case.sql`, em UTF-8 e LF. A descoberta aceitará somente esse formato, converterá `NNN` para ordem numérica e exigirá versões únicas e consecutivas a partir de `000`.

O histórico aplicado deve ser prefixo exato dos arquivos locais. Arquivo aplicado ausente/renomeado, checksum divergente, lacuna, duplicidade ou nova migration abaixo da maior versão aplicada interrompe toda operação antes do primeiro SQL pendente.

O `.gitattributes` fixará LF para `backend/database/**/*.sql`. O checksum será SHA-256 do conteúdo canônico em UTF-8/LF, evitando diferença meramente causada pelo checkout entre Windows e Unix.

### 3. Histórico como máquina de estados

`schema_migrations` será InnoDB e conterá, no mínimo:

- `version` como chave primária textual, preservando zeros à esquerda;
- `script_name` único e `description`;
- `checksum` SHA-256;
- `status`: `RUNNING`, `APPLIED` ou `FAILED`;
- `started_at`, `finished_at`, contador de tentativa e código de erro sanitizado quando aplicável.

Fluxo:

```text
PENDING --inicia--> RUNNING --sucesso--> APPLIED
                        |
                        +--erro--------> FAILED
                        |
                        +--interrupcao-> RUNNING persistente

FAILED/RUNNING persistente --reconciliacao explicita--> nova tentativa segura
```

O registro `RUNNING` é persistido antes do SQL. `APPLIED` só é gravado depois da última instrução. Erro conhecido grava `FAILED`; perda de conexão pode deixar `RUNNING`. Ambos bloqueiam versões posteriores e reexecução automática. Mensagens persistidas e exibidas não incluem SQL integral, dados ou credenciais.

A reconciliação não mascara a limitação transacional do MySQL: o operador deverá inspecionar o schema, restaurar backup ou preparar correção segura antes de liberar nova tentativa. Migrations futuras devem documentar pré-condições, preservação/backfill e irreversibilidade ou compensação.

### 4. Exclusão mútua no próprio MySQL

Antes de criar/ler o histórico, o runner obterá `GET_LOCK` com nome derivado do schema e timeout finito, mantendo a mesma conexão até o fim. Resultado diferente de aquisição bem-sucedida encerra a operação. `RELEASE_LOCK` será executado em `finally`; o fechamento da conexão permanece a salvaguarda final.

O lock serializa runners oficiais, inclusive durante o primeiro bootstrap da tabela. Ele não pretende impedir DDL manual; a política operacional proibirá alterações fora de migrations.

### 5. Executor consciente de delimitadores

O parser reconhecerá `DELIMITER` somente como diretiva em linha própria, removerá a diretiva e dividirá instruções pelo delimitador ativo. Aspas simples, duplas, identificadores entre crases e comentários de linha/bloco serão respeitados para não cortar conteúdo interno.

Cada instrução resultante será enviada separadamente pelo PyMySQL, e resultados adicionais serão drenados antes da próxima. Isso permite enviar `CREATE PROCEDURE ... BEGIN ... END` como uma única instrução, preservando o formato auditável da migration `002`.

Comandos de cliente que mudem conexão ou arquivo, como `SOURCE`, serão recusados. `USE` será removido das migrations: o schema permitido vem exclusivamente da configuração validada.

### 6. Histórico reconstruído e baseline por fingerprint

Será criada `000_create_mvp_schema.sql` para representar o estado anterior às duas migrations manuais: as três tabelas originais, a FK histórica de Questão e ausência da procedure. As migrations `001` e `002` serão incorporadas como sequência oficial, sem alterar seu efeito funcional e sem `USE` fixo.

O baseline reconhecerá somente fingerprints correspondentes aos prefixos:

- `000`: tabelas do MVP no estado histórico anterior às duas migrations;
- `000..001`: FK `RESTRICT`, ainda sem a procedure;
- `000..002`: estado consolidado atual, com FK `RESTRICT` e `sp_questoes_por_assunto`.

O fingerprint consultará `information_schema` para colunas, tipos, nulabilidade, chaves, índices, ações referenciais, checks e rotina/parâmetro esperados. A adoção exige confirmação explícita, registra os checksums dos arquivos oficiais e só modifica `schema_migrations`. Qualquer combinação desconhecida será recusada.

Um schema vazio usa `up` e executa `000`, `001` e `002`. `create_database.sql` continuará sendo o snapshot consolidado para compatibilidade e referência; testes compararão seus objetos oficiais com o resultado da sequência para evitar duas verdades divergentes.

### 7. Configuração e privilégios

O runner reutilizará `DATABASE_URL` ou `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` e `DB_CHARSET`, sem imprimir valores. O schema deve existir e ser selecionado explicitamente; criação de servidor/schema e administração de usuários permanecem fora do runner.

O usuário operacional precisa apenas dos privilégios exigidos pelas migrations, pelo lock e por `schema_migrations`. O processo da API não recebe responsabilidade de executar migrations. Arquivos SQL não conterão credenciais nem `DEFINER` fixo para Stored Procedures.

### 8. Testes em camadas

Testes unitários cobrirão nomes/ordem, checksum, parser de delimitadores, estado, mensagens sanitizadas e bloqueios usando doubles somente fora das integrações. Testes MySQL 8 reais usarão schema descartável explicitamente autorizado e validarão:

- instalação vazia e segunda execução sem efeito;
- adoção dos três prefixos históricos sem alteração de dados;
- drift de checksum, versão inválida e lock concorrente;
- estados `FAILED` e `RUNNING` bloqueando avanço;
- criação e execução de `sp_questoes_por_assunto`;
- equivalência estrutural com `create_database.sql`;
- aprovação das 29 integrações originais e da suíte ampliada atual.

O nome do schema descartável deverá satisfazer uma regra restritiva de teste antes de qualquer limpeza. As integrações nunca usarão SQLite ou mocks e não declararão sucesso quando o MySQL estiver indisponível.

### 9. Documentação arquitetural coerente

ADR-001 passará de aceito condicionalmente para aceito com o runner SQL como decisão final. O índice de ADRs, o pacote/mapa de impactos e `open-decisions-v1.md` serão atualizados para remover a pendência sobre Alembic. README e comandos de projeto explicarão `status`, `baseline`, `up`, falhas, backup e privilégios.

## Risks / Trade-offs

- **DDL múltiplo pode deixar estado parcial** → registrar antes da execução, bloquear automaticamente após falha e exigir recuperação documentada; usar backup para migrations críticas.
- **Parser SQL próprio crescer indevidamente** → limitar o contrato a SQL MySQL revisado e `DELIMITER`, com testes de aspas e comentários; ampliar somente por change futura.
- **Baseline incorreto poderia legitimar drift** → aceitar apenas fingerprints históricos completos e confirmação explícita, sem modo permissivo.
- **Snapshot e sequência podem divergir** → comparar estruturalmente os dois caminhos em integração e revisar ambos na mesma change quando necessário.
- **Checksum variar entre plataformas** → codificação UTF-8, LF obrigatório e canonicalização definida.
- **Lock consultivo pode ser ignorado por execução manual** → documentar migrations como único caminho oficial e manter detecção de drift como defesa adicional.
- **Privilégio de DDL aumenta impacto de credencial comprometida** → separar usuário operacional do usuário da API e conceder apenas privilégios necessários.

## Migration Plan

1. Implementar e testar o runner sem conectá-lo à inicialização da aplicação.
2. Formalizar `000`, adaptar `001` e `002` ao schema configurado e estabilizar seus checksums.
3. Validar instalação em schema MySQL 8 vazio e equivalência com o bootstrap.
4. Fazer backup do banco MVP e executar `status`/`baseline` em cópia restaurada.
5. Confirmar dados, constraints, Stored Procedure e toda a regressão automatizada.
6. Repetir o baseline no ambiente existente somente após aprovação da cópia.
7. Usar exclusivamente `up` para evoluções posteriores.

Não haverá downgrade automático desta adoção. Se a infraestrutura precisar ser retirada antes de qualquer migration futura, o runner pode deixar de ser usado e `schema_migrations` permanecer como metadado inerte; remover a tabela exigirá operação explícita e backup. Falhas de migrations futuras serão revertidas por restauração ou migration compensatória conforme o caso.
