# Design — Contas e Privacidade

## Context

Ver [proposta](proposal.md) e [inventário](inventario-procedures.md). Esta etapa depende de `adequar-plano-estudos-a-procedures` aplicada, verificada e sincronizada. A primeira change introduz infraestrutura de resultados e contratos SQL; não duplicar helpers nem recriar suas routines/views. A versão reservada aqui é 016, após 015.

## Goals / Non-Goals

**Goals:** substituir o acesso especializado inventariado mantendo comportamento ponta a ponta, estado gerenciado de entidades alteráveis, locks e transações já existentes.
**Non-Goals:** criar funções de produto, CRUD em Repository, framework de persistência, tabela/índice/Model novo ou política de segurança/negócio alternativa.

## Decisions

### Interfaces pequenas e parâmetros fechados

Aplicar o inventário, seus tipos e ordem de resultados como contrato. Usar SQL estático, IN vinculado e SQL SECURITY INVOKER. READS SQL DATA nas leituras; MODIFIES SQL DATA somente nos comandos especializados explicitamente inventariados. Proibir COMMIT, ROLLBACK, START TRANSACTION, SQL dinâmico, desativação de FKs e DDL em runtime. Não copiar toda validação de negócio ao banco: a routine verifica formato estrutural mínimo dos seus parâmetros sem alterar regras dos Services.

Lotes usam JSON_TABLE com IDs deduplicados; consultas ordenadas conservam a ordem anterior, e arrays vazios preservam vazio/nenhuma consulta conforme o método atual. Não interpolar IN/CSV, nomes de coluna ou critérios fornecidos pelo cliente. Referência primária: [MySQL — JSON_TABLE](https://dev.mysql.com/doc/refman/8.0/en/json-table-functions.html).

### Mapear entidades sem trocar a unidade de trabalho

Para um resultado que participa de escrita, usar mapeamento textual ORM no Repository (select da entidade ou tupla de entidades, from_statement de CALL parametrizado), com todas as colunas mapeadas, aliases explícitos e populate_existing onde já existente. LEFT JOIN de sessão usa carregamento explícito da relação, sem lazy query de identidade no Service. Não usar Model transiente, merge de registro incompleto, sessão/engine nova ou mapeador genérico criado para esta change.

Esse caminho preserva tipos JSON/Boolean/datas, identity map, guards e métodos salvar/atualizar/deletar. Fazer caracterização MySQL do resultado textual de CALL e de JOIN antes de converter o grupo; fechar o Result em finally e drenar conjuntos terminais pela infraestrutura existente. Referência: [SQLAlchemy — resultados ORM textuais](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#getting-orm-results-from-textual-statements). Os literais CALL ficam exclusivamente no Repository, inclusive em mapeamento ORM.

Leitura de apresentação com múltiplos resultados usa o helper participante da primeira etapa e registros tipados; adaptar apenas serialização do consumidor, sem levar SQL ao Service. Total é resultado independente da página, inclusive vazia. Não construir objeto ORM falso para atender um teste de método. Preservar autoflush anterior onde necessário sem confirmar a transação; locks continuam na mesma conexão e duram até o dono decidir commit/rollback.

**Alternativas rejeitadas:** nova sessão perde locks/snapshot; hidratação manual de instâncias parciais perde identidade/guards; converter todos os Services para dicionários aumenta escopo das mutações. Os métodos CRUD básicos existentes continuam adequados para buscas simples por PK e escrita individual.

### Contas, sessões e privacidade

Usuario.buscar_por_email passa a delegar ao Repository proprietário; SQL compara o e-mail normalizado pelo Service com utf8mb4_bin, sem nova normalização nem retorno público de senha_hash. Hash/verificação de senha, hash fictício contra enumeração, HMAC de chave e relógio ficam na aplicação. Routines recebem hashes/chaves estritamente necessários, nunca senha em claro ou segredo HMAC.

Consulta de sessão reproduz o LEFT JOIN original e popula Sessao.usuario no mesmo mapeamento textual, inclusive sessão anônima sem usuário. Manter populate_existing para ambas as entidades e a mesma validade no Service. Não filtrar ativo na consulta de sessão nem confundir usuario_ativo_bloqueado com bloquear_identidade_privacidade: este último bloqueia exatamente a identidade, inclusive inativa, conforme ADR-010.

Renovação deve preservar os predicados > de expiração/inatividade e o booleano de linha correspondente, inclusive quando ultimo_acesso_em já é igual a agora. Não usar rowcount do próprio CALL como contagem. A routine faz leitura corrente bloqueante do alvo sob os predicados, UPDATE e retorna correspondencias (0/1); um valor inalterado continua correspondência válida. Revogações retornam contagens próprias da operação. Sincronizar na identity map apenas atributos afetados das sessões carregadas com os valores confirmados pela routine, para que renovação/reautenticação não ressuscitem estado obsoleto.

Preparação do limite usa o mesmo upsert idempotente da chave e depois SELECT FOR UPDATE, sem substituir contadores existentes ou resetar janela no banco. O Service mantém cinco falhas/15 minutos, reset, bloqueio e Retry-After. Operações de escrita SQL são MODIFIES SQL DATA, participantes; não confirmar a criação da chave antes da transação do caso de uso.

Limpeza mantém os cortes exatos do método atual: corte=agora−24h; sessões por expiração/revogação anterior ao corte ou autenticadas com acesso anterior a corte−30min; limites por janela anterior a corte−15min e sem bloqueio vigente naquele corte. Capturar contagens de cada DELETE em variáveis próprias, sem usar o resultado terminal do CALL. Não incluir registros_privacidade ou usuarios, nem modificar retenção de evidências.

Privacidade mantém duas leituras correntes bloqueantes sequenciais, uso e plano, ordenadas por ID decrescente, e busca de replay corrente por dono/chave. Não substituir por snapshot, JOIN agregado não bloqueante ou filtro de ativo. Consentimento/revisão/versão/hash/replay continuam no Service. O participante de eliminação da 015 continua injetado, sem commit próprio.

As últimas decisões retornam um único conjunto de até duas evidências completas, na ordem uso → plano. Cada leitura `SELECT ... INTO ... FOR UPDATE` captura todas as colunas em variáveis locais; a projeção final estática devolve esses valores, omitindo o tipo ausente, sem reler snapshot. O Repository mapeia esse conjunto com `from_statement`/`populate_existing` e recompõe o dicionário atual de entidades gerenciadas ou `None`. O ensaio MySQL demonstrou que o Result ORM do caminho adotado não expõe os dois conjuntos originalmente planejados. Este ajuste foi autorizado pelo usuário em 08/11/2026, preserva locks e contratos públicos e evita novo mapeador ou hidratação manual.

**Verificação:** igualdades exatas de prazos, revogação concorrente com renovação, sessão anônima, conta inativa, senha correta durante bloqueio, primeiro upsert concorrente, segredo ausente de respostas/logs, contagens/rollback da limpeza e decisão nova após snapshot antigo de autenticação. Ao final, auditar todos os executores especializados dos seis módulos contra a matriz das cinco etapas e registrar qualquer achado real sem declarar cumprimento integral por contagem de routines.

### Evolução SQL e documentação por grupo

Acrescentar apenas `016_contas_privacidade_procedures.sql`, sem editar SQLs já aplicados. Instalação cria definições, não executa as funcionalidades das procedures. Consolidar bootstrap, reconhecimento e preflight até 016, reaproveitando o mecanismo aprovado pela primeira etapa. Validar assinaturas, corpos, colunas/resultados e segurança contra referência oficial gerada em schema descartável, nunca contra o banco a adotar. Metadado insuficiente/recurso parcial bloqueia, sem recuo que o esconda. Conferir prefixos antigos, checksums e procedure legada.

Atualizar a seção deste domínio em docs/technical/consultas-academicas-mysql.md, README e matrizes acadêmica/CRUD, preservando as vinte funcionalidades e seu significado. Documentar chamadas internas/CLI como auxiliares; a presença de uma rotina não cria requisito/tela. Registrar atualidade das consultas e as pendências atribuídas às próximas etapas. Preservar alterações legítimas externas e os visuais Desktop V1.

## Risks / Trade-offs

- [Mudar predicado ou ordem de locks] → Caracterização e concorrência em duas conexões MySQL, sem copiar regra de outra rotina aparentemente semelhante.
- [Entidade antiga no identity map] → Mapeamento completo com populate_existing e teste de leitura corrente seguido de mutação/rollback.
- [Resultados pendentes ou commit oculto] → Drenagem/close e teste na mesma conexão emprestada, incluindo vazios e erro.
- [Várias changes reservarem a mesma versão] → Dependências lineares e conferência prévia; colisão exige atualizar planejamento antes de aplicar.
- [Ajuste técnico virar requisito de produto] → Manter as decisões funcionais atuais e escopo fechado, sem promessa de aceite acadêmico.

## Migration Plan

1. Conferir dependência sincronizada e prefixo 015; registrar baseline de código/rotas/metadata/hashes e alterações externas, sem .env/segredos.
2. Ensaiar em schemas descartáveis MySQL: instalação limpa até 016, upgrade com dados, baseline/restauração equivalente e comparação com bootstrap; segunda atualização deve executar zero migrations.
3. Disponibilizar código dependente somente após a migration estar aplicada e verificada no ambiente de destino. Testes da change não aplicam DDL no banco de uso como efeito colateral.
4. Falha DDL mantém o fluxo RUNNING/FAILED/reconciliação atual. Reversão exige primeiro código anterior e depois restauração/compensação revisada das novas routines, preservando dados, versões, views e recursos das dependências. Não apagar histórico/checksums nem prometer rollback DDL.
5. Registrar comandos/resultados reais no validacao.md, executar gates/integrações/cobertura/E2E pertinentes, verificar e sincronizar os deltas antes de arquivar. Nenhuma operação Git/deploy/envio acadêmico está incluída.
