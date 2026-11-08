# Design — Procedures para consultas acadêmicas

## Context

Ver [proposta](proposal.md), [inventário e assinaturas](inventario-consultas.md) e deltas de [consultas](specs/consultas-academicas-mysql/spec.md) e [migrations](specs/migrations-sql/spec.md). O sistema tem seis módulos, 21 Models e uma procedure funcional de busca por Assunto. Os Repositories atuais executam as consultas especializadas corretamente separados dos Services, mas em SQLAlchemy.

O diagnóstico compõe projeções públicas de Práticas e Simulados, usando a classificação histórica de Conteúdo. Ele é reutilizado pelo Plano em uma conexão/transação externa. Mudar somente o texto da consulta, abrindo outra conexão, perderia o snapshot e violaria ADRs 006, 008, 009 e 010. As listagens atuais também retornam entidades/tuplas internas que serão substituídas por registros, sem alterar JSON.

## Goals / Non-Goals

**Goals:** entregar um primeiro conjunto verificável de consultas por procedures com interfaces SQL pequenas, parametrização, isolamento e compatibilidade. Manter as regras/fórmulas de negócio no Service e a seleção/agregação no MySQL.

**Non-Goals:** conversão geral de persistência, CRUD em Repository, nova camada de negócio, tabelas/Models, bibliotecas, alterações de privacidade ou redesign visual. Permanecem fora as famílias pendentes do inventário; esta change não certifica todo o sistema perante o enunciado.

## Decisions

### 1. Seis consultas de entrada e sete procedures

As assinaturas e a ordem dos resultados úteis são as do inventário, sem decisões de produto pendentes no apply. Usar duas migrations: 011 para as três listas administrativas e contagens de Conteúdo; 012 para contratos SQL de origem, métricas/atividades e contagens de Simulados. A implementação segue grupos pequenos com seus testes antes de avançar.

Usar SQL estático com parâmetros IN, `READS SQL DATA` e `SQL SECURITY INVOKER`. Não usar SQL dinâmico, parâmetros OUT, tabelas temporárias, transações dentro das routines nem construção de JSON HTTP no banco. Parâmetros opcionais vazios são normalizados pelos adaptadores conforme a semântica atual. As routines recusam com `SIGNAL SQLSTATE '45000'` paginação não positiva/limite acima de 100, IDs opcionais não positivos, estados/dificuldades inválidos e usuário/intervalo ausentes ou inválidos nas métricas/atividades. Não substituir validações HTTP dos Services.

**Alternativas:** converter todo o backend na mesma change aumenta risco e mistura controles de escrita; apenas documentar as consultas ORM não atende ao mecanismo exigido. Uma procedure genérica com nome de tabela/campo fornecido pelo cliente cria acoplamento e riscos desnecessários. Adotar procedures específicas por intenção.

### 2. Listas retornam registros de leitura, sem hidratar ORM

As procedures C01–C03 retornam dois conjuntos úteis: linhas da página e uma linha com total. Selecionar colunas explícitas e aliases com prefixo por recurso para os dados relacionados. Adaptadores do proprietário montam os mesmos registros e datas ISO atuais; não criar instâncias ORM a partir de linhas parciais nem consultar relacionamentos por lazy loading. Proteger tipos de contagem, nulos, campos e nomes atuais por comparação de payloads com fixtures sintéticas.

`ConsultaMateriasMySQL` e `ConsultaAssuntosMySQL` preservam seus Protocols e retornos de registros independentes de ORM. Para Questões, `QuestaoRepository.listar_admin` passa a retornar os registros completos da listagem com total; `ListarQuestoesAdminService` deixa apenas de percorrer tuplas ORM para serializar, mantendo filtros/validações/envelope. É alteração interna delimitada; nenhuma nova dependência de SQL/driver entra no Service. Conversores ficam no proprietário Conteúdo, pequenos e compartilhados somente onde necessário.

Preservar a semântica atual das buscas: Matérias/Assuntos usam LIKE com curingas fornecidos pelo termo; Questões usa substring literal com escape. Não interpolar termo, status, IDs, LIMIT ou OFFSET em SQL. Calcular deslocamento dentro da routine a partir dos parâmetros validados; preservar ordenação e contagens DISTINCT do catálogo. Testar caracteres `%`, `_`, aspas, barras, acentos e página vazia com total não zero. Não alterar collation nem acrescentar índices nesta change.

**Alternativas:** retornar somente uma janela com COUNT OVER perde o total de uma página vazia; reconstruir entidades ORM agrega estado e consultas ocultas. Adotar resultados independentes para linhas e total e registros simples no adaptador.

Os filtros numéricos e a página usam BIGINT UNSIGNED no contrato SQL para não limitar a API a INT de 32 bits apenas por trocar a implementação. Não acrescentar limites HTTP novos: incluir regressão para página/ID acima de 2^31 com retorno vazio e total correto, dentro da faixa já executável pelo MySQL.

### 3. Views como contratos de origem, sem abrir persistência privada

Criar as quatro views nominadas no inventário, com colunas explícitas, `SQL SECURITY INVOKER`, sem qualificar schema externo e sem escrita. Conteúdo publica classificação histórica; Práticas publica fatos respondidos; Simulados publica fatos respondidos e atividades finalizadas. A view de fatos de Simulados se relaciona com a view pública de classificação de Conteúdo, nunca com taxonomia corrente. Registrar proprietário, colunas, filtros e consumidores no novo ADR-011 e em `docs/technical/consultas-academicas-mysql.md`.

O Repository de Desempenho chama as procedures de métricas/atividades, que só leem as views de origem autorizadas. Contagens ficam nas procedures de seus proprietários. Desempenho continua compondo o dashboard administrativo pelas APIs públicas de Conteúdo/Simulados, cujas funções de contagem passam a chamar as respectivas routines. Os dois formatos públicos de contagem de Conteúdo podem adaptar a mesma linha SQL; chamadas separadas usam o mesmo ContextoLeitura. Não acrescentar cache global de resultados.

Isso complementa explicitamente o ADR-010 com interfaces SQL de leitura; não autoriza imports privados, ORM público, uso genérico de tabelas externas ou escrita cruzada. Preservar as APIs Python existentes, inclusive projeções ainda necessárias a outros consumidores, sem duplicá-las como fallback para as seis rotas convertidas. Não criar Model para view e não alterar o registro das 21 Models.

**Alternativas:** SQL de Desempenho lendo livremente tabelas privadas quebra a fronteira modular; exportar metadados ORM pelo api.py também. Transportar todos os fatos para agrupar em Python perde a agregação no banco e aumenta dados trafegados. Quatro views pequenas preservam as projeções já existentes sem criar outro serviço ou tabela.

### 4. Métricas continuam históricas e reutilizáveis

`sp_desempenho_resumo` retorna geral, grupos de Matéria e grupos de Matéria/Assunto nesta ordem. Somar fatos respondidos por `UNION ALL`, com contagens por origem; não juntar fatos de duas origens por coincidência de IDs. Conservar a lógica atual de janela/ROW_NUMBER para o rótulo mais recente, desempate por instante/tipo/ID e ordem dos grupos. O SQL apenas calcula contagens; percentual, arredondamento, erros, limiar/amostra, período e envelopes permanecem nos Services.

As views não filtram pelo estado atual de publicação/arquivamento de Questão, Assunto ou Simulado: aplicam os mesmos critérios históricos das projeções atuais. Usar `respondida_em` na Prática e `finalizada_em` no Simulado, precisão de microssegundos e intervalo `[inicio, fim)`. A atividade de Simulado vem da tentativa finalizada uma única vez, inclusive quando todas as respostas estão em branco; não derivá-la da view de respostas elegíveis. `sp_atividades_recentes` limita cinco pela ordem existente.

Não criar relógio SQL paralelo (`NOW`) nem calcular o período independentemente do Service. Não aceitar usuário alvo HTTP. Geração/recalculo do Plano consome o mesmo diagnóstico e contexto já autorizado, mantendo locks, consentimento e rollback existentes.

### 5. Consumir múltiplos resultados na conexão participante

Adicionar somente um helper neutro de infraestrutura em `app/core/procedures_mysql.py` para executar SQL parametrizado, ler resultados e fechar cursor. Os nomes e literais `CALL` permanecem nos Repositories; o helper não conhece nomes de procedures, tabelas ou regras. Cada Repository informa o número/formato esperado dos conjuntos úteis e recusa resultado inesperado; um conjunto com colunas e zero linhas é útil, não deve ser descartado como o conjunto terminal sem descrição.

Usar cursor PyMySQL obtido da conexão DBAPI subjacente à **mesma** Connection SQLAlchemy já participante. Para listagens, a conexão pertence à sessão atual; para métricas/contagens/atividades, `ContextoLeitura` fornece uma operação neutra `executar_resultados(comando, parametros)` que valida seu estado e delega usando sua conexão. Não expor sessão/cursor ao Service nem criar engine, raw_connection independente ou novo TransactionManager. O helper nunca confirma/reverte/fecha a conexão emprestada; cursor é fechado em `finally` e todos os conjuntos são drenados com `nextset()`.

Não depender de ORM autoflush implícito para dados participantes: manter os flushes já realizados pelas Models/TransactionManager; onde uma consulta substituída dependia de autoflush da sessão, preservar esse comportamento no Repository antes do cursor, sem commit. No ContextoLeitura externo, não adicionar flush próprio nem mudar isolamento. Se houver falha de protocolo que impeça drenagem segura, invalidar a conexão pela API de infraestrutura e propagar a falha; não devolvê-la ao pool como saudável nem mascarar erro com resultado vazio.

Referências primárias: [PyMySQL — múltiplos resultados e conjunto terminal](https://pymysql.readthedocs.io/en/latest/modules/cursors.html) e [SQLAlchemy — cursor DBAPI e procedures](https://docs.sqlalchemy.org/en/20/core/connections.html#working-with-the-dbapi-cursor-directly). Essas APIs pertencem à infraestrutura, não às camadas de negócio. Nenhuma nova dependência é necessária.

### 6. Migrations, reconhecimento e bootstrap coerentes

Acrescentar arquivos novos, sem editar migrations 000–010. 011 requer o prefixo 010; 012 requer 011. Documentar pré-condições/privilégios, preservação e compensação. Nenhuma carga/backfill ou DML funcional é necessária. O bootstrap consolidado inclui os mesmos sete procedimentos/quatro views em ordem de dependências e preserva a procedure legada; não usar DEFINER com conta ou host fixo. O SQL deve funcionar sob o MySQL 8 suportado pelo projeto.

Manter o runner e checksums; adaptar reconhecimento em infraestrutura SQL pequena, sem concentrar todo o novo validador em `legacy_schema.py`. Separar base tables de views ao inventariar tabelas. Para reconhecer 011/012, primeiro validar o estado 010 existente e então os recursos adicionais completos. Presença parcial de nomes oficiais novos exige erro; não recuar para um prefixo anterior para ignorá-los. 011 tem exatamente os quatro procedimentos aprovados nessa versão; 012 acrescenta três e quatro views conforme inventário.

Conferir assinatura IN/ordem/tipo, corpo SQL, modo de segurança, característica de leitura, colunas/tipos das views e suas dependências internas, usando referência gerada exclusivamente por instalação das migrations oficiais em schema descartável. Reutilizar a estratégia conservadora existente de comparação; normalizar apenas o nome físico do próprio schema e identidade do DEFINER, sem apagar destinos externos, literais, predicados ou segurança do invocador. Metadados insuficientes são erro. Não introduzir parser SQL genérico nem aceitar banco encontrado como referência esperada.

Testes de migrations/portabilidade passam a distinguir explicitamente expectativas históricas 010 das novas expectativas 011/012; não substituir cegamente todos os números históricos. Atualizar preflight de integração para exigir o conjunto atual antes de executar as suítes afetadas, com mensagens sem segredos. Não chamar migrations no startup Flask nem instalar rotinas automaticamente em caso de 500.

### 7. Validação por caso e evidência acadêmica

Antes da troca, caracterizar os payloads e resultados atuais com dados sintéticos: combinações de filtros, datas, classificações históricas, totais, nulos e autorização. Guardar fixtures/expectativas no teste, sem manter dois motores de consulta em produção. Cada grupo implementa SQL, Repository/adaptador, regressão MySQL e documentação mínima em conjunto.

Acrescentar testes de chamadas sucessivas na mesma conexão, conjuntos úteis vazios, falha após um resultado, reutilização do pool e falha integral de dashboard. Concorrência real verifica snapshot entre blocos e rollback do Plano após diagnóstico participante. Testes diretos de SQL verificam assinaturas/limites sem credenciais. Testes unitários isolam helper/conversores; não simulam as integrações existentes. Gates de arquitetura verificam ausência de SQL/CALL nos Services/Controllers e a manutenção das fronteiras dos módulos.

Documentar nomes, parâmetros, views/proprietários, rotas, telas, execução/upgrade e pendências em `docs/technical/consultas-academicas-mysql.md`, README e matriz acadêmica. Integrar a matriz CRUD nova somente após conferir seu estado final. Esta adequação não acrescenta funcionalidades à lista de vinte, não substitui a modelagem nem demonstra envio ao Classroom. `validacao.md` da change registra comandos e resultados reais, incluindo bloqueios de MySQL quando existirem.

## Risks / Trade-offs

- [Mais objetos SQL para manter] → Sete routines e quatro views nominadas, sem novos frameworks ou abstrações de domínio; inventário fechado e proprietário explícito.
- [Mudar LIKE, JSON ou total de página vazia] → Caracterização prévia e integração comparando contratos por caso.
- [Perder snapshot ao abrir conexão do driver] → Reusar conexão SQLAlchemy participante e testar concorrência/rollback reais.
- [Resultados pendentes contaminarem o pool] → Drenagem e liberação em sucesso/erro, sem descartar conjuntos úteis vazios.
- [Desempenho passar a ler taxonomia atual] → Views históricas específicas e teste após transferência/renomeação/arquivamento.
- [Reconhecimento antigo ignorar recursos parciais] → Detecção adicional conservadora, metadados independentes e regressão dos prefixos anteriores.
- [A documentação parecer adequação total] → Declarar recorte e consultas restantes; nenhuma garantia de pontuação ou aceite acadêmico.

## Migration Plan

1. Registrar estado inicial/hashes das migrations antigas, payloads e alterações externas já existentes; não sobrescrever a change documental em andamento.
2. Ensaiar 011 e depois 012 em schemas descartáveis, verificando dados, recursos, idempotência e upgrade/backup restaurado. Publicar bootstrap equivalente e documentação com os mesmos contratos.
3. Aplicar o código dependente somente em ambiente com as duas migrations concluídas e verificadas. Durante o apply desta change, usar banco descartável para testes; não aplicar DDL ao banco de uso como efeito colateral.
4. Em falha DDL, usar o processo RUNNING/FAILED e reconciliação existente; DDL MySQL não possui rollback transacional garantido. Não marcar sucesso parcial.
5. Reversão operacional: voltar primeiro ao código anterior, que não depende dos novos recursos; restaurar backup ou usar migration compensatória revisada removendo routines e depois views na ordem inversa de dependências. Preservar procedure legada, tabelas e dados; não apagar histórico/checksums nem criar downgrade automático nesta change.
6. Após implementação, executar verificação, sincronizar os dois deltas e arquivar. Commit/push/deploy e envio acadêmico exigem instruções próprias.
