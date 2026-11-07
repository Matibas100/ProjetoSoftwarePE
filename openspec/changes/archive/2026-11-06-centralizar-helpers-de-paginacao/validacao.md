# Validação: centralizar helpers de paginação

## Preflight — 06/11/2026

Schema `spec-driven`, com `skip_specs: true`. Legibilidade e JSON verificadas
e arquivadas antes deste apply. Conferidos proposta, design, tarefas,
AGENTS.md, conventions, arquitetura mestre e ADRs de autenticação,
versionamento, transações e persistência. Nenhum runner concorrente encontrado;
nenhum subagente iniciado. Orientações de apply compatíveis com o escopo.

Baseline fresco em `test-results/paginacao/`: 496 hashes SHA-256 de arquivos
não sensíveis, nove cópias dos arquivos existentes do escopo, corpos AST
originais, estado Git e inventário dos dois helpers. Pesquisa em backend,
frontend e scripts confirmou somente os oito módulos previstos, sem patches
ou consumidores adicionais dos nomes privados.

Escopo fechado: nove arquivos de produção (um novo), um novo unitário e a
convenção de arquitetura, além do checklist e deste registro. Alterações
locais anteriores de migrations, legibilidade, JSON, frontend, README,
specs, demais changes, `tmp/` e visuais oficiais integram o baseline e devem
ser preservadas. Nenhum `.env` aberto, configuração sensível copiada,
dependência instalada ou escrita no banco operacional.

## Resultados

### Extração e regressão focada

- Criado `backend/app/services/paginacao.py` com somente as duas funções e
  imports de `ceil` e `DadosInvalidosError`. Os corpos AST são idênticos aos
  originais, normalizando apenas os nomes das funções.
- Oito módulos passaram a importar/chamar diretamente as funções públicas.
  Removidas as definições antigas e o import de `ceil` no catálogo, sem alias
  ou wrappers. Comparação AST dos consumidores confirma que nenhuma outra
  lógica, assinatura de Service, validação ou chamada foi alterada.
- Novo `test_paginacao.py`: **9 testes aprovados**. Cobrem ausência/vazio,
  conversões anteriores (incluindo bool, float, Unicode e bytes), limites
  inclusivos, máximo opcional, mensagens/causas de erro e envelopes com total
  zero/exato/parcial, página além da última e preservação da lista/ordem.
  O comportamento anterior de zero por página também foi caracterizado.
- Regressão focada: **61 testes aprovados**, sem falhas/erros, nos módulos
  `test_catalogo`, `test_services`, `test_praticas`, `test_simulados`,
  `test_composition`, `test_consultas_compostas` e `test_substituicao_catalogo`.
  Carregados pelo ambiente isolado de `backend/tests/run_unit.py` e executados
  por `unittest`, sem dotenv ou conexão MySQL.
- Validadores estritos continuam rejeitando filtros repetidos, Unicode e
  valores não string onde já rejeitavam. Defaults, campos, mensagens e
  políticas específicas permanecem. Busca em backend/frontend/scripts não
  encontra mais os dois nomes privados.
- Acrescentada somente uma frase com link válido na convenção de arquitetura,
  preservando a responsabilidade dos Services, CRUD nas Models e consultas
  especializadas nos Repositories.

Evidências em `test-results/paginacao/`: `unitarios-consumidores.log`,
`helpers-ast.json`, cópias originais e `preservacao.json`.

### Regressão integrada

Executada pelos runners oficiais, sem alteração de thresholds ou testes
existentes. Configuração somente no processo, dotenv desabilitado e logs
com redaction. A primeira chamada do invólucro sem stdin encerrou antes de
abrir conexão por configuração incompleta; retomada com a senha fornecida
pelo usuário via stdin, sem gravá-la em arquivos. MySQL local 8.0.44 confirmado.

| Comando | Resultado |
| --- | --- |
| `python backend/tests/run_backend_coverage.py`, com `RUN_MYSQL_INTEGRATION=1` e `RUN_MYSQL_MIGRATION_INTEGRATION=1` | **154 unitários + 115 integrações aprovados**, saída 0 |
| Gate backend | **97,47% linhas (3617/3711), 91,24% branches (812/890)** |
| `backend/app/services/paginacao.py` | **100% linhas (14/14) e branches (4/4)** |
| Limpeza backend | Listas de schemas descartáveis vazias antes/depois |

Integrações incluem filtros/paginações, HEAD/HTTP, permissões, propriedade,
persistência real, concorrência, replay, rollback na última gravação,
fingerprints, migrations e procedure. Os 29 testes originais permanecem
intactos. Sem mocks/SQLite nas integrações, escrita no banco operacional,
redução dos gates 90%/85% ou arquivo executável sem cobertura. Evidências:
`backend.log`, `backend-result.json` e `paginacao-coverage.json` no diretório
ignorado. E2E iniciado somente após término e limpeza do backend.

| Comando | Resultado |
| --- | --- |
| `python scripts/run_e2e.py`, com `RUN_MYSQL_E2E=1` somente no processo | **2 E2E aprovados em 32,2 s**, saída 0 |
| Vinte funcionalidades com persistência e regressões de navegação | Aprovado, 14,7 s |
| Plano/Simulado: geração, conclusão, finalização e recálculo persistidos | Aprovado, 15,9 s |
| Limpeza E2E | Schema removido; listas de schemas descartáveis vazias antes/depois; nenhum servidor/runner remanescente |

API/MySQL reais e Chromium pelo runner oficial intacto, com schema novo e
opt-in transitório. Nenhuma alteração em frontend, testes anteriores,
runners ou configuração. Sem traces, HAR, vídeo ou storage state. Aviso
`NO_COLOR`/`FORCE_COLOR` não afetou o resultado. Evidências em `e2e.log` e
`e2e-result.json`. Cobertura DOM não repetida por não haver delta frontend.

## Verificação final — openspec-verify-change

Status e instruções apply consultados novamente, com releitura dos três
contextFiles e conferência das conventions, implementação e evidências.
Revisão somente leitura concluída; este registro e o checklist são finalizados
em seguida pela tarefa 4.3 já autorizada, sem nova alteração de código.

| Dimensão | Resultado |
| --- | --- |
| Completude | As seis tarefas anteriores estão comprovadas; a sétima conclui esta revisão. Onze arquivos de implementação previstos atendidos, mais checklist e registro. |
| Correção | Corpos AST idênticos após renomear somente funções; consumidores equivalentes após atualizar imports/chamadas. Nove testes novos, 61 focados, 154 unitários completos, 115 integrações MySQL e dois E2E aprovados. |
| Coerência | Somente dois helpers neutros, sem classe/framework novo. Validações específicas nos Services preservadas, sem mudanças em contratos, consultas, persistência, schema ou transações. |

**Achados:** nenhum crítico, aviso ou sugestão pendente. Sem ampliação de
escopo ou necessidade de revisar proposta/design. A falha inicial de entrada
do invólucro foi resolvida antes de qualquer conexão e não afetou o produto.

`openspec validate centralizar-helpers-de-paginacao --strict` aprovado. O
único INFO confirma que zero deltas são aceitos com `skip_specs: true`.
`git diff --check`, whitespace dos arquivos novos e links locais aprovados.
Busca final sem os nomes privados em backend/frontend/scripts; módulo novo
contém exatamente dois imports e duas funções. Evidência em `static-qa.json`.

Baseline final: **486 dos 496 arquivos idênticos** por SHA-256. As dez
diferenças permitidas são os oito módulos consumidores, a convenção de
arquitetura e o checklist. Os únicos três arquivos novos versionáveis são
o módulo neutro, seu teste e este registro. Proposta/design e todas as demais
changes, specs principais, migrations locais, testes anteriores, frontend,
README, `tmp/` e visuais oficiais preservados. Gates e runners intactos.

Aplicação e verificação concluídas, sem pendências. Sync não aplicável por
`skip_specs: true`; pronta para arquivamento pela skill correspondente.
Sem abertura de `.env`, credenciais persistidas, escrita no banco operacional,
commit, push, merge, publicação ou arquivamento neste apply.

## Arquivamento

Change arquivada pelo CLI OpenSpec em
`2026-11-06-centralizar-helpers-de-paginacao`, após conferência de sete tarefas
concluídas, artefatos completos e verificação sem achados críticos. Validação
estrita aprovada novamente antes da operação. Sem delta de specs;
`--skip-specs` manteve as specs principais intactas.

Os cinco arquivos foram comparados por SHA-256 imediatamente após a mudança
de diretório, incluindo `.openspec.yaml`. Acrescentado somente este registro;
links relativos internos continuam válidos. Baseline fresco de arquivamento
inclui artefatos de outras changes criados após o apply, que foram preservados.
Nenhuma alteração de implementação, nova execução de testes, commit, push ou
merge neste arquivamento.
