# Design — Práticas e Simulados

## Context

Ver [proposta](proposal.md) e [inventário](inventario-procedures.md). Esta etapa depende de `adequar-catalogo-editorial-a-procedures` aplicada, verificada e sincronizada. A primeira change introduz infraestrutura de resultados e contratos SQL; não duplicar helpers nem recriar suas routines/views. A versão reservada aqui é 014, após 013.

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

### Práticas e Simulados

Preservar os filtros de usuário no SQL dos métodos de propriedade/replay, e os locks opcionais exatamente onde eram solicitados. O Service continua atribuindo dono e validando revisão, UUID, A–E, estado e confirmação; não passar essas decisões para stored procedure.

Composição deve distinguir rascunho (simulado_id) e versão (versao_id) pela mesma precedência do método atual. Listas/lotes retornam os mesmos tipos e agrupamentos, sem duplicar itens quando JSON contém IDs repetidos. A ordem é por identidade/posição onde já definida; não ordenar arbitrariamente resultados sem ordem contratada. Preservar no máximo uma tentativa em andamento por dono/versão e suas constraints.

Respostas retorna um único conjunto com colunas completas de Resposta/Item e aliases por entidade; usar mapeamento ORM textual para as entidades que serão atualizadas na finalização. Fatos retorna colunas completas da tripla Resposta/Item/Tentativa e mantém o intervalo e os predicados de finalização/não branco atuais. Histórico de apresentação com total em conjunto separado pode usar DTOs no adaptador e adaptação mínima de serialização no Service, sem transformar o Service em acesso SQL.

Correção e totais ficam no Service e gravações individuais nas Models sob TransactionManager. Publicação/cadastro de Simulado mantém a revisão, motivos, eventos e versões. Nenhuma routine aqui grava resposta ou finaliza tentativa.

As projeções públicas de diagnóstico continuam compatíveis com as views da primeira etapa; não criar segundo cálculo de métricas nem copiar gabaritos para o browser. O consumidor de fatos interno mantém sua interface e privacidade.

**Verificação:** duas contas com as mesmas chaves/IDs cruzados, replay após resposta de rede perdida, corrida salvar/finalizar, branco, composição retirada, recarga e histórico após nova publicação. Falha depois de corrigir parte das respostas deve reverter tudo.

### Evolução SQL e documentação por grupo

Acrescentar apenas `014_praticas_simulados_procedures.sql`, sem editar SQLs já aplicados. Instalação cria definições, não executa as funcionalidades das procedures. Consolidar bootstrap, reconhecimento e preflight até 014, reaproveitando o mecanismo aprovado pela primeira etapa. Validar assinaturas, corpos, colunas/resultados e segurança contra referência oficial gerada em schema descartável, nunca contra o banco a adotar. Metadado insuficiente/recurso parcial bloqueia, sem recuo que o esconda. Conferir prefixos antigos, checksums e procedure legada.

Antes de executar a migration 014, `run_up` deve chamar o detector físico existente
e exigir exatamente o prefixo 013, ainda sob o lock do runner e após as proteções
de histórico/checksum/reconciliação. A checagem precede o registro RUNNING e o DDL
de 014. Falha preserva histórico, dados e objetos encontrados; não cria um FAILED
para uma execução que não começou. Isso também vale para instalação vazia ao
chegar à 014 e para retry reconciliado, após a compensação necessária dos objetos
parciais. Prefixos anteriores mantêm o fluxo atual; nenhuma rotina/checksum muda.

Atualizar a seção deste domínio em docs/technical/consultas-academicas-mysql.md, README e matrizes acadêmica/CRUD, preservando as vinte funcionalidades e seu significado. Documentar chamadas internas/CLI como auxiliares; a presença de uma rotina não cria requisito/tela. Registrar atualidade das consultas e as pendências atribuídas às próximas etapas. Preservar alterações legítimas externas e os visuais Desktop V1.

## Risks / Trade-offs

- [Mudar predicado ou ordem de locks] → Caracterização e concorrência em duas conexões MySQL, sem copiar regra de outra rotina aparentemente semelhante.
- [Entidade antiga no identity map] → Mapeamento completo com populate_existing e teste de leitura corrente seguido de mutação/rollback.
- [Resultados pendentes ou commit oculto] → Drenagem/close e teste na mesma conexão emprestada, incluindo vazios e erro.
- [Várias changes reservarem a mesma versão] → Dependências lineares e conferência prévia; colisão exige atualizar planejamento antes de aplicar.
- [Ajuste técnico virar requisito de produto] → Manter as decisões funcionais atuais e escopo fechado, sem promessa de aceite acadêmico.

## Migration Plan

1. Conferir dependência sincronizada e prefixo 013; registrar baseline de código/rotas/metadata/hashes e alterações externas, sem .env/segredos.
2. Ensaiar em schemas descartáveis MySQL: instalação limpa até 014, upgrade com dados, baseline/restauração equivalente e comparação com bootstrap; segunda atualização deve executar zero migrations.
3. Disponibilizar código dependente somente após a migration estar aplicada e verificada no ambiente de destino. Testes da change não aplicam DDL no banco de uso como efeito colateral.
4. Falha DDL mantém o fluxo RUNNING/FAILED/reconciliação atual. Reversão exige primeiro código anterior e depois restauração/compensação revisada das novas routines, preservando dados, versões, views e recursos das dependências. Não apagar histórico/checksums nem prometer rollback DDL.
5. Registrar comandos/resultados reais no validacao.md, executar gates/integrações/cobertura/E2E pertinentes, verificar e sincronizar os deltas antes de arquivar. Nenhuma operação Git/deploy/envio acadêmico está incluída.
