# ADR-011 — Interfaces SQL de leitura

**Aceito** pela aplicação da change `adequar-consultas-academicas-a-procedures`,
em 07/11/2026. Complementa os ADRs 001, 006, 008 e 010.

## Decisão

As seis consultas administrativas/de desempenho delimitadas no
[inventário](../../../openspec/changes/archive/2026-11-08-adequar-consultas-academicas-a-procedures/inventario-consultas.md)
usam sete procedures específicas, estáticas, `READS SQL DATA` e
`SQL SECURITY INVOKER`. CALL fica exclusivamente no Repository. CRUD básico,
validações, percentuais e envelopes continuam na aplicação.

Conteúdo, Práticas e Simulados publicam quatro views explícitas, também com
segurança do invocador. Desempenho consulta essas interfaces históricas;
isso não permite acesso genérico ou escrita na persistência de outro módulo.
Não há Model para view nem mudança nas 21 Models, APIs Python ou contratos HTTP.

Resultados independentes da página preservam o total de páginas vazias.
Registros de leitura não são entidades ORM. O helper neutro consome todos os
conjuntos e fecha o cursor na mesma conexão SQLAlchemy participante. O contexto
externo conserva conexão, snapshot, relógio e responsabilidade por commit/rollback.
Falha não aciona consulta alternativa nem resposta parcial; falha de drenagem
invalida a conexão.

As migrations 011/012 e o bootstrap publicam os mesmos recursos. O baseline
confere tabelas anteriores e referências oficiais dos recursos novos, geradas
somente em schemas descartáveis. Recursos parciais/divergentes bloqueiam o
reconhecimento, sem recuar silenciosamente para versões anteriores.

## Alternativas e consequências

Rejeitados procedure genérica por nome de tabela, import privado entre módulos,
hidratação ORM parcial e conexão independente. Acrescentam-se contratos SQL
versionados e testes de equivalência/concorrência. As demais famílias de consulta
continuam pendentes; não há declaração de adequação acadêmica integral.

Assinaturas, proprietários, resultados e operação estão no
[documento técnico](../consultas-academicas-mysql.md).

## Adendo — Catálogo editorial (013)

A change `adequar-catalogo-editorial-a-procedures` acrescenta quinze routines
específicas de seletores, impactos, locks e versões/elegibilidade. Leituras que
alimentam mutação retornam entidades ORM completas/gerenciadas por mapeamento
textual, na mesma sessão; os locks recarregam o estado corrente. A listagem de
apresentação continua retornando registros e filtrando conteúdo permitido.

Preservam-se Questão → Assunto → Matéria na publicação e Assunto → Matérias
em ordem crescente na transferência. A view histórica pública existente é
reutilizada; não há Model/tabela nova nem mudança de política editorial. O
reconhecimento de 013 exige 012 íntegro e as quinze referências adicionais,
preservando as onze referências SQL anteriores e todos os checksums 000–012.

## Adendo — Práticas e Simulados (014)

Dezesseis interfaces específicas cobrem propriedade/replay, composição,
andamento, respostas, históricos e fatos. Entidades/par/tripla retornadas para
mutação continuam gerenciadas na sessão proprietária; páginas usam registros
de apresentação e total separado. Locks mantêm leitura corrente e ordem, sem
commit/rollback dentro das routines. Correção e totais continuam nos Services;
escritas permanecem nas Models. As quatro views de desempenho são reutilizadas.
O reconhecimento exige 013 íntegro e dezesseis referências novas, preservando
as 26 anteriores e os checksums 000–013.

## Adendo — Plano de Estudos (015)

Seis interfaces preservam a sequência lock de Contas → permissão → derivados.
Atual/replay/itens e JOIN Item/Plano retornam entidades completas gerenciadas;
elegibilidade de pares pertence a Conteúdo e conserva FOR SHARE e igualdade de
vínculo/snapshot. Ranking, diagnóstico, escrita individual e conclusão permanecem
nos Services/Models. O lock de identidade continua reservado à etapa 016.

`sp_eliminar_planos_proprios` é a exceção especializada `MODIFIES SQL DATA`:
sob lock do dono, elimina itens antes de cada geração decrescente, com FK RESTRICT
ativa. Participa somente da negativa autorizada, sem controlar transação nem
apagar evidências/respostas. Expiração seletiva sincroniza derivados carregados
sem afetar a decisão pendente. As cinco leituras são READS SQL DATA; todas usam
SQL SECURITY INVOKER. O runner exige 014 físico íntegro antes de RUNNING/DDL de
015; seis referências oficiais novas preservam as 42 anteriores e SQLs 000–014.
Contas permanece na próxima etapa; não há declaração de adequação integral.

## Adendo — Contas e Privacidade (016)

Onze interfaces cobrem identidade, sessões, preparação concorrente de limite,
limpeza e decisões correntes. Seis leituras são READS SQL DATA; renovação,
revogações, upsert do limite e limpeza são MODIFIES SQL DATA participantes,
sem controle transacional próprio. Senha, HMAC, relógio e regras continuam na
aplicação. Usuário/Sessão/limite/evidências mantêm identidade ORM; revogações
sincronizam apenas o atributo afetado. Não há novo CRUD em Repository.

Últimas decisões preservam dois locks correntes sequenciais (uso → plano),
capturando as colunas em variáveis locais e devolvendo um único conjunto de
evidências gerenciadas. O ensaio demonstrou a limitação do caminho ORM para
dois conjuntos; o ajuste foi autorizado e registrado antes da conversão.
Lock de identidade inclui conta inativa; replay, append-only e eliminação da
015 sob a mesma transação permanecem. A limpeza não remove conta/evidência.

Runner exige 015 físico íntegro antes de RUNNING/DDL. Onze referências oficiais
novas preservam as 48 anteriores e SQLs 000–015. A auditoria dos seis módulos
rastreia executores e projeções de compatibilidade até os consumidores; estas
últimas têm execução somente em regressão de equivalência. A cobertura técnica
do inventário não presume aceite acadêmico ou resolve gestão geral de Usuários.
