# Validação — fingerprint de schema portável

Resultado final: 166 unitários, 136 integrações MySQL e 3 testes Playwright
aprovados, sem skips. Cobertura de produção: 97,67% linhas e 91,68% branches,
com gates e verificação de arquivo executável sem cobertura aprovados.

## Ambiente e limites

Execução em 2026-11-07, Windows, Python 3.14, MySQL Community 8.0.44.
Instância nova e exclusiva de teste em loopback, porta 33379, datadir em
`tmp/schema-portavel/mysql-data`. Não foi lido `.env`; configuração e opt-ins
existem apenas nos processos de teste. Nenhuma operação no banco operacional.
MySQL 8.0.46 não está disponível: não foi ensaiada comunicação entre versões.

## Referência inicial

Árvore já continha alterações documentais de outra change; foram preservadas.
Antes da troca dos detectores, a suíte direcionada do runner executou 20 testes
em 131,826 s, todos aprovados, sem skips:

```text
python -m unittest tests.test_migrations_integration tests.test_simulados_migration_integration tests.test_planos_migration_integration tests.test_privacidade_migration_integration -v
```

Comando executado com `PYTHONPATH=backend`, configuração da instância exclusiva,
`RUN_MYSQL_INTEGRATION=1` e `RUN_MYSQL_MIGRATION_INTEGRATION=1` somente no processo.
Logs locais em `tmp/schema-portavel/` (não são artefatos versionados).

Módulo original: `database.legacy_schema`; reexportações preservadas em
`database.migrate`: `SIMULADOS_FINGERPRINTS`, `PLANOS_FINGERPRINTS`,
`PRIVACIDADE_FINGERPRINT`, `_detect_simulados_prefix`, `_detect_planos_prefix`,
`_detect_privacidade_prefix`, `detect_legacy_prefix`. As referências eram hashes
de `SHOW CREATE TABLE` sem contador AUTO_INCREMENT. Validadores 000–007 mantidos.

### SHA-256 dos bytes oficiais antes da implementação

| Arquivo | SHA-256 |
| --- | --- |
| `backend/database/migrations/000_create_mvp_schema.sql` | `1e51d54b93a4d8125961a17e283e2933fa3fe1f0b8b385b6d50ede1bcdf868a8` |
| `backend/database/migrations/001_restrict_delete_assuntos.sql` | `329594db44e2ee7f6a71b4c8a871cc5efb1dd849642ed4397b49a3ae7dca0b5d` |
| `backend/database/migrations/002_create_sp_questoes_por_assunto.sql` | `7d19427eaed0f6e63ec4116aee0aa56cf07a2e12b6e559c2a09f5409414abd38` |
| `backend/database/migrations/003_prepare_catalogo_academico.sql` | `dd27f63de40fd06585c4a3cbd33a9f164574ae983b3eeb3cffb8ff91a8decbd4` |
| `backend/database/migrations/004_restrict_catalogo_academico.sql` | `de6bedc463391556498fe641cb61fe74a59717b421c59e0dfcb1d6ff71a804d8` |
| `backend/database/migrations/005_create_autenticacao_escolar.sql` | `a650da20e8785b4de919e0324928844a282f63b76bacce0f752fdb55332fb8c2` |
| `backend/database/migrations/006_create_questoes_versionadas.sql` | `97160b8fb019d8dc59e7f83452808b5fefd9a1944f20850d6336880822e2b36c` |
| `backend/database/migrations/007_create_pratica_tentativas.sql` | `2ca7fc6c974dfa2e0011d72bc532a00a0e4cca8d9ab0055cdd9c4b93f58c3161` |
| `backend/database/migrations/008_create_simulados.sql` | `b21286bbfcb77ba6bad04c1eda72d7fbc71b39dc825c847238cce1b73d71fe36` |
| `backend/database/migrations/009_create_planos_estudo.sql` | `22763b2c463d65995f79a93aaa34a6ff3a760f591d94cfb19822be646126a624` |
| `backend/database/migrations/010_create_registros_privacidade.sql` | `d91e31207a77afc6077c7dc7002b08fa7f2180f6df2dbe43a920d2107915d2dc` |
| `backend/database/create_database.sql` | `cb0d46ef5afea63217a4f5e3ad872a4b680062a6aae13b89c1d9d8ab5d62358b` |

## Reprodução controlada

Dois schemas descartáveis receberam DDL sintético com `titulo VARCHAR(150)`
e a variante `titulo VARCHAR(150) CHARACTER SET utf8mb4`, ambos com a mesma
collation efetiva `utf8mb4_unicode_ci`. As dez propriedades de coluna consultadas
foram idênticas. SHA-256 dos textos: `c8ad848ec3eb432b37f45439fcf6ce299df9291e97611958fe91ba1d2bab2cd2`
e `229a859042479e948025491fc906ff719aff182d7ac0a27be588f4fb7c1102a9`.
Isso reproduz a distinção texto/estrutura: o mesmo servidor pode reapresentar
ambos de forma idêntica em SHOW CREATE; não se afirma ter reproduzido a saída
espontânea de uma segunda versão MySQL. Ambos os schemas foram limpos em finally.

## Helper e referências oficiais

`python backend/tests/run_unit.py`: 165 testes aprovados, sem skips.
Campos e limites registrados no adendo 22 do ADR-001. JSON preserva tipos,
None e literais; ordenação é explícita, sem dict.values(). FK interna recebe
marcador separado de FK externa. Estatísticas e contador são excluídos.

Referências obtidas em schema novo pelas migrations oficiais: 000–008 para
Simulados, depois 009 para Plano e 010 para Privacidade, MySQL 8.0.44. Nenhuma
referência foi derivada de banco operacional ou aceita automaticamente em runtime.

| Tabela | Assinatura estrutural SHA-256 |
| --- | --- |
| `simulados` | `1c9c6c1cc599d13db8607931c86747d02f5ff4faa475e574082be3753d99cac0` |
| `simulado_rascunho_itens` | `89db7740776b97059799d404cb8e8d5153ccd2f2c01b84a96ed03a59a62f0182` |
| `simulado_versoes` | `b5ff6a140da0d85ef1188eed770cd529a49f871ee036cd3211e2e67cb9280c07` |
| `simulado_versao_itens` | `a82779747c285833b71c110d55f4bbc03e7c1429a0f3c14cf1aee460f2babee2` |
| `simulado_eventos` | `13e72b2969786b4dd9bc9c8a5dee5e6a78e86907d1441e075a1ae95b881ecfd5` |
| `simulado_tentativas` | `47186f84d68d4b6cf7d58dea8b9ed7bd4a734d4984b7ee2172824db2385fcbb5` |
| `simulado_respostas` | `3e2ed942cb7dc25662475a4a4f128d7901068c77bb2505fa55df6dad8f330541` |
| `planos_estudo` | `652f8ce81ef5b55d8eeec892cd9b0e8f7e58adf214c399f734d88f299f27f8ff` |
| `plano_estudo_itens` | `432ca52b0d7eea3174e818db3047a50093858c7f33e243332301be366d8c31d1` |
| `registros_privacidade` | `f5c5422548c01b7860a17350f97ec340f439e303f535bd32988ef7a90af38174` |

Revisão contra SQL 008: sete tabelas InnoDB/utf8mb4_unicode_ci, índices únicos
compostos, FKs RESTRICT, marcador STORED da tentativa em andamento e CHECKs de
estado/revisão/posição/resposta. SQL 009: duas tabelas, usuario_atual STORED,
JSON de período/snapshot, unicidade de geração/chave/plano atual e limites de
posição. SQL 010: uma tabela, hashes/chaves ASCII binários, quatro CHECKs,
FK de usuário RESTRICT e índices de replay/última evidência. Invariantes são
verificadas independentemente também nas integrações existentes de cada prefixo.

## Regressão e conferência final

Integrações de Simulados/Plano/Privacidade após troca das referências: 7 testes
aprovados em 51,813 s, sem skips. Links do adendo e comandos status/up/baseline/
reconcile conferidos contra o help real do runner. README preservou as alterações
anteriores da outra change. Documentação de Plano/Privacidade distingue os três
hashes e limita explicitamente a portabilidade.

O primeiro ensaio da nova suíte teve 30 erros de limpeza (`Already closed`),
apesar de os corpos dos cenários passarem: `recreate_schema` já fechava as
conexões registradas em addCleanup. A limpeza passou a conferir `connection.open`;
reexecução aprovada: 6 testes em 132,594 s, sem skips. Não se contabiliza a
primeira execução como aprovação.

Comando direcionado: `python -m unittest tests.test_schema_portavel_integration -v`
(mesma configuração isolada/opt-ins). O arquivo é descoberto automaticamente
por `run_integration.py`. Round-trip usa SHOW CREATE de tabelas/rotina e INSERT
de dados exclusivamente sintéticos, sem mysqldump/Docker. Colunas geradas são
recalculadas pelo servidor, não inseridas. FOREIGN_KEY_CHECKS é restaurado antes
da validação. Compara todos os dados funcionais antes/depois, prefixo oficial,
histórico/checksums, pendências 2/1/0 e segunda execução zero; copia também um
histórico válido completo. Há teste explícito de limpeza após falha no segundo
schema e addCleanup para o primeiro mesmo se setUp falhar.

Os 27 subcasos negativos executados cobrem tipo, nulabilidade, default literal,
collation, charset, ordem/adição de coluna, atributo AUTO_INCREMENT, ausência/
ordem/unicidade/visibilidade/prefixo/expressão de índice, regra/destino de FK,
expressão CHECK, ENFORCED, expressão gerada, row format, opção persistente,
comentários de tabela/coluna, engine, tabela ausente/excedente e procedure
ausente. Outro teste cobre FK externa com tabela/coluna iguais; outro confirma
corpo de procedure incompatível no MVP 002. Cada recusa verifica histórico vazio
e igualdade de dados funcionais. A recusa de corpo/parâmetros nos prefixos novos
foi acrescentada após a decisão abaixo e comprovada na suíte final.

### Conflito de planejamento identificado

Um ensaio isolado com migrations 000–010 e procedure recriada como `SELECT 1`
continuou reconhecendo prefixo 010. É comportamento herdado: o validador do
catálogo apenas conta a procedure, enquanto o validador MVP 000–002 compara
corpo e parâmetros. O cenário novo exige bloqueio por procedure incompatível,
mas o design manda preservar validações 000–007. Solicitada decisão explícita
sobre ampliar somente a validação dos prefixos 008–010 ou revisar o cenário;
nenhuma alteração dessa validação foi feita antes da resposta.

O usuário aprovou explicitamente incluir a validação nos prefixos 008–010.
Proposal/design/spec/tasks foram reconciliados e aprovados pelo validador estrito
antes da implementação. O contrato existente de corpo/parâmetros foi extraído
para reutilização, mantendo o comportamento 000–007; 008 passa a exigi-lo e
009/010 herdam a proteção. Acrescentados 15 subcasos (corpo, nome/modo/tipo e
quantidade de parâmetros em cada prefixo) e unitário de metadados indisponíveis.
Unitários finais: 166 aprovados em 4,183 s. A cobertura completa será repetida
após esse ajuste autorizado; a execução iniciada antes dele é intermediária.

Teste direcionado adicional de procedure: 1 teste com 15 subcasos, aprovado em
13,648 s, sem skips. E2E executado uma vez com `RUN_MYSQL_E2E=1` no processo e
MySQL isolado fornecido por ambiente: `npm run test:e2e`, 3 testes Playwright
aprovados em 58,3 s. Inclui os vinte casos originais e os fluxos atuais de
Plano/Simulado/Privacidade. O runner confirmou a remoção do schema descartável.
Node 25.2.1, npm 11.6.2, Python 3.14.0. Um aviso NO_COLOR/FORCE_COLOR do Node
não interferiu nos testes.

### Rastreabilidade dos cenários do delta

| Cenário | Evidência |
| --- | --- |
| MVP consolidado e prefixos intermediários | `test_baseline_reconhece_todos_os_prefixos_sem_alterar_dados`, prefixos 000–010 |
| Schema desconhecido/divergente | Testes originais e 27 mutações da suíte portável |
| Cópia restaurada sem histórico | Round-trip 008/009/010, baseline, pendências 2/1/0, reexecução zero e dados iguais |
| Charset redundante | DDL variante submetido a MySQL real, metadados sintéticos iguais e prefixos oficiais reconhecidos |
| Nome físico/estatísticas | Segundo schema aleatório, AUTO_INCREMENT=9999, ANALYZE e unitário com estatísticas diferentes |
| Histórico restaurado íntegro | Round-trip com histórico e checksum divergente adicional recusado |
| Divergência estrutural | Dimensões listadas acima, histórico vazio e dados funcionais iguais após cada recusa |
| FK externa | Destino externo com mesmos nomes de tabela/coluna recusado |
| Metadados indisponíveis | Unitários de campos ausentes, None obrigatório, tipo não serializável e erro MySQL sanitizado |
| Proteções anteriores | Regressões de checksum, lock concorrente, RUNNING/FAILED e falha parcial/procedure preservadas |
| Corpo/parâmetros 008–010 | 15 subcasos reais recusados sem baseline nem DML funcional |

### Cobertura final

`python backend/tests/run_backend_coverage.py` executado com dotenv desabilitado,
configuração isolada e os dois opt-ins MySQL somente no processo. Coleta final
separada da intermediária por `COVERAGE_FILE` temporário, sem mudar a configuração
versionada. Unitários: 166 aprovados; integrações: 136 aprovadas em 418,539 s;
nenhum skip. Validador de produção aprovado: linhas 3949/4043 (97,67%) e branches
871/950 (91,68%), sem arquivo executável com zero linhas cobertas.

A coleta intermediária, iniciada antes do ajuste de procedure e com código
alterado durante sua execução, passou em 135 integrações, mas registrou 96,14%
linhas/82,63% branches e falhou no gate de branches. Não é usada como evidência
de cobertura da versão final; a coleta completa final acima a substitui.

### Integridade e verificação OpenSpec

`openspec validate tornar-fingerprint-de-schema-portavel --strict --json`:
aprovado, zero issues. `git diff --check`: aprovado. Os doze hashes de bytes
registrados permanecem idênticos; não existe migration 011. Não há diff em
contratos HTTP/Models/Services, SQLs/bootstrap, frontend/HTMLs legais,
`.gitattributes`, dependências ou artefatos visuais. O diff do README conserva
as mudanças preexistentes de entrega/CI. Nenhum segredo foi incluído no diff.

Conferência na instância exclusiva após todas as suítes: zero schemas além
dos quatro internos do MySQL; fixtures API/migrations/E2E removidas. Instância
encerrada por SHUTDOWN e credencial temporária removida via apply_patch.
A aprovação automática bloqueou os comandos de exclusão do datadir, com a
mensagem `blocked by policy`; seus arquivos permanecem somente em
`tmp/schema-portavel/mysql-data`, com o processo já encerrado. Esse resíduo
local não é uma fixture ativa nem deve ser versionado. Nenhum baseline,
upgrade ou restauração foi executado no banco operacional; não houve commit,
push ou publicação.

| Dimensão | Resultado |
| --- | --- |
| Completude | 8/8 tarefas e todos os cenários do delta cobertos |
| Correção | Unitários, integrações reais, E2E e gates aprovados |
| Coerência | Design/ADR/conventions atendidos; ajuste de procedure explicitamente aprovado |

Sem achados críticos. Limitação documentada: somente MySQL 8.0.44 disponível;
8.0.46 e portabilidade universal não foram alegadas.

### Sincronização e arquivamento (2026-11-07)

Delta `migrations-sql` sincronizado: um requisito modificado e dois adicionados,
preservando Purpose e todos os requisitos/cenários anteriores. Comparação
integral dos três blocos do delta confirmou igualdade com a spec principal.
`openspec validate --specs --strict --json`: 11/11 specs aprovadas; validação
estrita da change aprovada e `git diff --check` sem erros.

Arquivamento solicitado pelo usuário, com 8/8 tarefas e artefatos concluídos:
`openspec archive tornar-fingerprint-de-schema-portavel --skip-specs --yes --json`.
O flag `--skip-specs` evitou reaplicar o delta já sincronizado e conferido.
Destino confirmado pelo CLI:
`openspec/changes/archive/2026-11-07-tornar-fingerprint-de-schema-portavel/`.
