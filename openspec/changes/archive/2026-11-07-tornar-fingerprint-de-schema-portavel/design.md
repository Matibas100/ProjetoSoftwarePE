# Design — Assinatura estrutural do schema

## Context

Ver [proposta](proposal.md). `backend/database/legacy_schema.py` reconhece estados históricos para baseline. Os validadores anteriores a 008 já consultam metadados; os prefixos 008–010 dependem de hashes de `SHOW CREATE TABLE`. O ensaio 8.0.44 → 8.0.46 encontrou DDL com charset redundante, sem diferença de metadados ou dados.

`run_up` com histórico válido não depende dessa comparação em cada execução. O defeito afeta reconhecimento/baseline de estados conhecidos e conferência de restaurações; não se presume que um upgrade normal com histórico esteja quebrado.

## Goals / Non-Goals

**Goals:** comparar a estrutura de dez tabelas de forma determinística e conservadora; aceitar o caso conhecido de apresentação de charset; manter detecção de divergência e a explicação simples para o grupo.

**Non-Goals:** equivalência algébrica de SQL, portabilidade universal entre versões, novas camadas ou biblioteca de migrations. A infraestrutura permanece em `backend/database/`; nenhuma consulta é movida para Controller/Service e nenhum Repository de CRUD é criado. Transações da aplicação, `CALL sp_questoes_por_assunto` e contratos HTTP permanecem intactos.

## Decisions

### 1. Um helper privado no módulo existente

Adicionar um helper pequeno de leitura/canonicalização estrutural em `legacy_schema.py`, usado pelos três detectores existentes. Preservar `SIMULADOS_FINGERPRINTS`, `PLANOS_FINGERPRINTS`, `PRIVACIDADE_FINGERPRINT`, detectores e reexportações consumidas pelos testes. Os valores dessas referências internas mudarão para o novo formato, sem alterar sua finalidade ou os checksums persistidos.

Alternativas rejeitadas: retirar o hash enfraquece a proteção; substituir texto por regex resolve só um exemplo e pode esconder diferenças; criar um framework de introspecção aumenta a complexidade. O helper consulta metadados explícitos e serializa uma estrutura fixa com a biblioteca padrão.

| Prefixo | Tabelas com assinatura nova |
| --- | --- |
| 008 | `simulados`, `simulado_rascunho_itens`, `simulado_versoes`, `simulado_versao_itens`, `simulado_eventos`, `simulado_tentativas`, `simulado_respostas` |
| 009 | `planos_estudo`, `plano_estudo_itens` |
| 010 | `registros_privacidade` |

Manter a composição dos detectores: 010 valida também 009, 008 e os prefixos anteriores; cada etapa conserva suas verificações de tabelas parciais/excedentes e catálogo. Ajuste aprovado durante o apply: adicionar em 008 a conferência do corpo e dos parâmetros da procedure, herdada por 009/010; o catálogo anterior apenas verificava sua existência. Reutilizar a comparação já adotada pelo MVP (tokens do corpo e assinatura IN p_assunto_id INT), sem alterar o comportamento dos validadores 000–007. Não ampliar incidentalmente o recorte para reescrever esses validadores.

### 2. Conteúdo da assinatura

Ler `information_schema` somente no schema selecionado, com nomes de tabela parametrizados. Converter os resultados em campos explícitos e ordenados, serializar deterministicamente e calcular SHA-256 em UTF-8. Não depender da ordem implícita do cursor ou de `dict.values()`.

| Dimensão | Campos estruturais incluídos |
| --- | --- |
| Tabela | Nome, engine, collation, row format, opções persistentes de criação e comentário |
| Colunas | Ordem/nome, tipo completo com tamanho/precisão/unsigned, nulabilidade, default, atributos `EXTRA`, charset/collation, expressão gerada e comentário |
| Índices | Nome, unicidade, ordem dos componentes, coluna ou expressão, tamanho de prefixo, tipo e visibilidade |
| FKs | Nome, ordem das colunas, tabela/coluna de destino, schema de destino e regras ON UPDATE/ON DELETE |
| CHECKs | Nome, expressão e estado `ENFORCED` |

Usar metadados de `TABLES`, `COLUMNS`, `STATISTICS`, `KEY_COLUMN_USAGE`, `REFERENTIAL_CONSTRAINTS`, `TABLE_CONSTRAINTS` e `CHECK_CONSTRAINTS`. Manter `None` distinto da string `NULL` e strings/literais sem conversões que alterem caixa ou conteúdo. Expressões CHECK/geradas são comparadas na representação de metadados retornada pelo MySQL, sem parser nem normalização arbitrária de SQL.

Excluir contadores e estatísticas variáveis: próximo AUTO_INCREMENT, cardinalidade, quantidade de linhas, datas, tamanhos de armazenamento, host, versão pontual e nome físico do banco. O atributo AUTO_INCREMENT da coluna permanece incluído. Mapear referência FK ao próprio schema para um marcador estável; referência externa não pode ser confundida com uma interna e deve divergir. Não remover o schema referenciado sem verificar sua identidade.

Isso reconhece estruturas com metadados iguais, mesmo que um charset seja implícito ou explícito no DDL exibido. Não promete equivalência entre expressões diferentes nem aceita diferenças reais de collation ou charset.

### 3. Referências esperadas derivadas de fonte oficial

Gerar as dez assinaturas de referência somente em schemas descartáveis construídos com migrations oficiais imutáveis e conferir a estrutura contra os SQLs. Registrar no relatório a versão MySQL, os campos utilizados e a origem de cada referência. Nunca calcular e aceitar automaticamente a assinatura esperada a partir do banco operacional encontrado.

O teste deve ter uma fonte independente de expectativa: prefixo oficial, invariantes explícitos e variantes de DDL/metadados. Apenas comparar o helper com um hash produzido pelo próprio helper na mesma fixture não demonstra correção.

### 4. Baseline conservador e três hashes distintos

A leitura da estrutura não executa DDL/DML funcional. Incompatibilidade, ausência de metadado obrigatório ou referência desconhecida resulta em `MigrationError`, sem fallback permissivo. Mensagem identifica o contexto/tabela sem credenciais nem dados pessoais.

Baseline só registra versões após todas as verificações atuais, incluindo procedure; não presume consentimentos e não altera dados. Manter checksums dos arquivos SQL, locks, estados RUNNING/FAILED e recusa de histórico inconsistente. Não criar migration 011 nem alterar migrations 000–010 ou bootstrap.

São mecanismos diferentes: assinatura estrutural reconhece o schema; checksum do SQL protege arquivos já aplicados; hash dos HTMLs legais identifica documentos aceitos. Esta change modifica somente o primeiro. Não alterar `.gitattributes` ou os hashes legais.

### 5. Testes com MySQL real e restauração isolada

Reutilizar `MySQLMigrationTestCase`, prefixo validado, opt-ins existentes e limpeza em `finally`/tearDown, incluindo eventual segundo schema. Não conectar testes ao schema operacional. Usar dados exclusivamente sintéticos e não imprimir configuração sensível.

- Unitários: serialização estável com ordem de linhas diferente; preservação de tipos/defaults/literais; exclusão de estatísticas e identidade física; sensibilidade às dimensões estruturais. Mocks apenas aqui.
- Integrações dos prefixos 008, 009 e 010: schema oficial reconhecido; faltas/excessos e deriva continuam recusados. Cobrir tipo, nulabilidade/default, charset/collation, índice/ordem/unicidade, destino/regra FK, expressão gerada, CHECK/ENFORCED e engine, agrupando mutações independentes em subtests quando conveniente.
- Round-trip: criar schema oficial com fixture existente; obter DDL das tabelas e rotina, restaurar em outro schema descartável e preservar dados sintéticos. O teste não depende de `mysqldump` ou Docker instalado. Desabilitar verificação FK apenas durante a montagem da cópia descartável, caso necessário; reabilitar antes da conferência.
- Demonstrar a diferença conhecida de apresentação: fixture controlada com charset redundante no DDL e metadados iguais. Se o servidor local não reproduzir a diferença espontaneamente, construir a variante na cópia, sem mocks nem edição do validador para passar.
- Sem histórico na cópia: reconhecer prefixo correto, baseline registrar somente versões comprovadas, dados inalterados, `up` aplicar apenas posteriores e segunda execução aplicar zero. Com histórico válido restaurado: checksums preservados e nenhuma reexecução indevida. Não confundir essa invariância com bloqueio total de DML do histórico pelo baseline.
- Drift real: recusar baseline e verificar que nenhuma versão presumida foi registrada nem dado funcional alterado. Preservar regressões de checksum, lock, falha parcial, procedure e prefixos anteriores.

Round-trip local prova restauração e independência da apresentação; a comparação real 8.0.44/8.0.46 é evidência adicional quando disponível, não pré-requisito oculto nem promessa de testar versão ausente.

### 6. Documentação e convivência com a outra change

Atualizar o trecho de migrations do README, `docs/technical/operacao-plano-estudos.md`, `operacao-privacidade.md` e acrescentar adendo no ADR-001 explicando assinatura e limites. Não reescrever a decisão histórica como se sempre usasse metadados. Registrar comandos/resultados reais no `validacao.md` desta change.

Aplicar preferencialmente após `alinhar-documentacao-de-entrega`: ambas podem tocar README em seções diferentes, portanto reler o arquivo e preservar edições anteriores. Esta change tem delta apenas em `migrations-sql`; a outra não altera essa capability. Não há dependência de implantação entre elas.

## Risks / Trade-offs

- [Campo estrutural omitido aceita drift] → Inventário explícito, revisão contra DDL e casos negativos por dimensão, incluindo enforcement e FKs externas.
- [Metadados também variam em outra versão] → Escopo MySQL 8/caso conhecido; falhar fechado e registrar limitação em vez de normalizar SQL indiscriminadamente.
- [Referência esperada contaminada pelo banco encontrado] → Derivar de migrations oficiais em schemas descartáveis, conferir invariantes e preservar SQLs por checksum.
- [Custo extra de introspecção] → Consultas restritas a dez tabelas durante reconhecimento operacional; sem introspecção por requisição HTTP ou cache complexo.
- [Referências internas importadas por testes] → Preservar nomes/reexportações e executar regressão do runner.

## Migration Plan

1. Registrar hashes dos SQLs/bootstrap e baseline dos testes relevantes antes da implementação.
2. Implementar e validar somente em schemas descartáveis. Nenhum comando de baseline, upgrade ou restauração será executado no banco operacional por esta change.
3. Executar regressões backend/migrations, cobertura com gates atuais e E2E afetado uma vez após os checks direcionados. Documentar indisponibilidades; não contar testes pulados como aprovados.
4. Verificar o delta e realizar sync/archive pelo workflow depois da implementação concluída.

Não há migração de dados nem alteração persistida de hashes históricos. Reversão do código restaura o reconhecedor anterior e sua limitação de apresentação; nenhum rollback SQL é necessário. Commit, push e hospedagem exigem instruções próprias do usuário.
