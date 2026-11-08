# Design — Plano de Estudos

## Context

Ver [proposta](proposal.md) e [inventário](inventario-procedures.md). Esta etapa depende de `adequar-praticas-simulados-a-procedures` aplicada, verificada e sincronizada. A primeira change introduz infraestrutura de resultados e contratos SQL; não duplicar helpers nem recriar suas routines/views. A versão reservada aqui é 015, após 014.

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

### Plano e eliminação especializada

A operação mantém: lock de identidade pela API de Contas → permissão vigente → replay/atual/item → diagnóstico/seleção → escrita → único commit externo. O lock continuará implementado como hoje até 016; não criar cópia em Plano nem antecipar sua conversão. Parâmetros não recebem usuário do cliente, mas o dono já autorizado.

Plano atual/replay/itens retornam entidades gerenciadas completas. Item próprio retorna um único conjunto JOIN de Item/Plano com aliases distintos e os mesmos locks. A elegibilidade de pares é routine de Conteúdo chamada por QuestaoRepository e API pública existente; não importar sua persistência em Plano. Com bloquear=true, manter FOR SHARE e locks de identidade/versão/classificação equivalentes ao predicado atual, inclusive igualdade entre Matéria atual e snapshot.

Ranking, taxa exata e limite de três itens continuam no Service; o diagnóstico vem da primeira etapa, na mesma Connection/instante. Criar/substituir gerações e concluir itens continuam usando Models, guards e TransactionManager, sem fórmula SQL nova nem confirmação adicional.

sp_eliminar_planos_proprios é MODIFIES SQL DATA, recebe somente usuario_id do participante autorizado e não abre transação. Sob o lock do dono já adquirido, percorrer planos por ID decrescente (cursor SQL local), bloquear as linhas correspondentes, eliminar itens próprios antes de cada plano e repetir predicado de usuário na remoção do plano. Isso preserva a FK plano_anterior_id RESTRICT sem desativar constraints, cascatas ou guards ORM. Retornar contagens em uma linha; o participante mantém o contrato externo atual sem retornar resultado HTTP novo.

Não mover evidências/decisão para a routine nem revalidar consentimento no participante de eliminação. O Service de negativa grava e elimina na mesma transação; replay é resolvido antes de chamar o participante. Nenhum endpoint público genérico chama a routine. Após DML especializado, sincronizar apenas entidades derivadas afetadas já carregadas, preservando os dados pendentes da negativa; não usar expire_all/commit escondido.

**Verificação:** várias gerações referenciadas e itens concluídos, outra conta, negativa concorrente com recálculo, falha após excluir itens e antes de remover plano, replay de negativa antiga após nova autorização e plano novo. Dados e hashes legais, respostas e evidências permanecem.

### Evolução SQL e documentação por grupo

Acrescentar apenas `015_plano_estudos_procedures.sql`, sem editar SQLs já aplicados. Instalação cria definições, não executa as funcionalidades das procedures. Consolidar bootstrap, reconhecimento e preflight até 015, reaproveitando o mecanismo aprovado pela primeira etapa. Validar assinaturas, corpos, colunas/resultados e segurança contra referência oficial gerada em schema descartável, nunca contra o banco a adotar. Metadado insuficiente/recurso parcial bloqueia, sem recuo que o esconda. Conferir prefixos antigos, checksums e procedure legada.

Atualizar a seção deste domínio em docs/technical/consultas-academicas-mysql.md, README e matrizes acadêmica/CRUD, preservando as vinte funcionalidades e seu significado. Documentar chamadas internas/CLI como auxiliares; a presença de uma rotina não cria requisito/tela. Registrar atualidade das consultas e as pendências atribuídas às próximas etapas. Preservar alterações legítimas externas e os visuais Desktop V1.

## Risks / Trade-offs

- [Mudar predicado ou ordem de locks] → Caracterização e concorrência em duas conexões MySQL, sem copiar regra de outra rotina aparentemente semelhante.
- [Entidade antiga no identity map] → Mapeamento completo com populate_existing e teste de leitura corrente seguido de mutação/rollback.
- [Resultados pendentes ou commit oculto] → Drenagem/close e teste na mesma conexão emprestada, incluindo vazios e erro.
- [Várias changes reservarem a mesma versão] → Dependências lineares e conferência prévia; colisão exige atualizar planejamento antes de aplicar.
- [Ajuste técnico virar requisito de produto] → Manter as decisões funcionais atuais e escopo fechado, sem promessa de aceite acadêmico.

## Migration Plan

1. Conferir dependência sincronizada e prefixo 014; registrar baseline de código/rotas/metadata/hashes e alterações externas, sem .env/segredos.
2. Ensaiar em schemas descartáveis MySQL: instalação limpa até 015, upgrade com dados, baseline/restauração equivalente e comparação com bootstrap; segunda atualização deve executar zero migrations.
3. Disponibilizar código dependente somente após a migration estar aplicada e verificada no ambiente de destino. Testes da change não aplicam DDL no banco de uso como efeito colateral.
4. Falha DDL mantém o fluxo RUNNING/FAILED/reconciliação atual. Reversão exige primeiro código anterior e depois restauração/compensação revisada das novas routines, preservando dados, versões, views e recursos das dependências. Não apagar histórico/checksums nem prometer rollback DDL.
5. Registrar comandos/resultados reais no validacao.md, executar gates/integrações/cobertura/E2E pertinentes, verificar e sincronizar os deltas antes de arquivar. Nenhuma operação Git/deploy/envio acadêmico está incluída.
