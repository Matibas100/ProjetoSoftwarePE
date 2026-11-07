# Design: separar responsabilidades do runner SQL

## Context

Motivação e escopo em [proposal.md](proposal.md). O arquivo atual possui quatro classes/records e funções de configuração, leitura SQL, execução, histórico, CLI e inspeção de schemas históricos. A maior parte da inspeção não participa da instalação limpa; ela é necessária para o comando explícito de adoção de banco existente.

O [ADR-001](../../../../docs/technical/adr/ADR-001-estrategia-de-migrations.md) e a spec [migrations-sql](../../../specs/migrations-sql/spec.md) permanecem válidos. Os caminhos desses links foram conferidos no destino arquivado.

`database` hoje funciona como namespace package, sem `__init__.py`. O comando documentado é `python backend/database/migrate.py`, enquanto testes e runner usam `from database import migrate`. Unitários fazem patch em nomes de `database.migrate`; integrações também acessam fingerprints e alguns helpers desse módulo. A extração deve respeitar essas fronteiras.

## Goals / Non-Goals

**Goals:** localizar separadamente execução, leitura de scripts e reconhecimento histórico; reduzir a concentração em `migrate.py` sem duplicar lógica; preservar os consumidores e as proteções verificadas.

**Non-Goals:** impor tamanho máximo arbitrário aos arquivos, reduzir a contagem de regras, substituir tecnologia, introduzir classes de serviço/repository para infraestrutura ou alterar os critérios da disciplina. A melhoria é de organização e legibilidade, não de funcionalidade.

## Decisions

### 1. Quatro arquivos com responsabilidades delimitadas

| Arquivo em `backend/database/` | Responsabilidade |
| --- | --- |
| `migrate.py` existente | Configuração/conexão; histórico e locks; aplicação/recuperação; adoção do baseline; apresentação e comandos CLI. Também preserva os nomes de entrada usados atualmente. |
| `migration_types.py` novo | Somente as definições existentes de `MigrationError` e `Migration`, com os mesmos campos, imutabilidade e comportamento. |
| `sql_scripts.py` novo | `canonical_sql`, `discover_migrations`, `split_sql`, `_without_leading_comments`, `validate_statements`, `execute_statements` e suas constantes de parsing/caminho. |
| `legacy_schema.py` novo | `_user_tables`, constantes de estrutura/fingerprints, `_sql_tokens`, `_check_tokens`, todos os `_detect_*_prefix` e `detect_legacy_prefix`. Apenas reconhece a estrutura; não registra baseline nem aplica SQL de alteração. |

`DatabaseSettings` e `HistoryState` permanecem em `migrate.py`: os módulos extraídos não precisam delas. Evitar um arquivo de configuração adicional, abstrações genéricas ou fragmentação de cada verificação de tabela. `run_baseline` permanece coordenador no arquivo original, usando o reconhecimento extraído e o histórico existente.

`HISTORY_TABLE`, usada por `_user_tables`, acompanha esse helper em `legacy_schema.py` e é reexportada por `migrate.py`; manter uma única definição. Constantes de configuração de conexão continuam no módulo principal. Não copiar valores para resolver dependências circulares.

Dependências, sem retorno ao módulo principal:

```text
migrate.py --> sql_scripts.py --> migration_types.py
     |
     +------> legacy_schema.py --> migration_types.py
     |
     +------> migration_types.py
```

Os módulos novos não importam `migrate`, Flask, Models ou Services. Importá-los não carrega `.env`, não conecta, não executa SQL e não dispara CLI. A configuração continua sendo carregada apenas pelas funções existentes quando chamadas. `legacy_schema.py` reutiliza somente `hashlib`/`re` e o erro compartilhado; não inventar dependência entre reconhecimento e parser de scripts.

Alternativas descartadas: manter tudo no mesmo arquivo deixa a dificuldade de localização; reescrever com Alembic contraria a decisão atual e amplia o escopo; criar um framework ou dezenas de módulos acrescenta conceitos desnecessários.

### 2. Extração sem mudança de algoritmo ou SQL

Mover as funções/constantes com alterações mínimas de importação, comentários explicativos curtos e espaçamento. Manter textos SQL, expressões regulares, condições, ordem de chamadas, comparações e mensagens. Não substituir a máquina de estados do parser por `split(';')`: procedures, delimitadores, strings e comentários já possuem semântica testada.

Preservar integralmente:

- sequência/convenção das migrations, UTF-8/canonicalização e cálculo SHA-256;
- rejeição de lacunas, duplicidade, scripts inválidos e comandos de cliente;
- mesmo diretório padrão de SQL, resolução da raiz do projeto e seleção explícita do schema;
- `GET_LOCK`/liberação, histórico `RUNNING`/`APPLIED`/`FAILED`, bloqueio e reconciliação explícita;
- adoção reconhecida de `000` a `009`, estrutura, procedure, checks/índices/FKs e fingerprints, incluindo a remoção exclusivamente do contador variável de `AUTO_INCREMENT` onde já ocorre;
- código de saída e sanitização; nenhuma mensagem deve revelar URL/senha;
- comandos/flags existentes e o fato de não existir downgrade automático.

O reconhecimento histórico permanece mais extenso; sua extensão representa versões já suportadas. Esta change não o substitui por validação mais permissiva. As instruções de banco não transitam por Controllers/Services: são operações de infraestrutura, preservando a separação das consultas de negócio nos Repositories.

### 3. Compatibilidade explícita de imports e execução direta

`migrate.py` importa/reexporta explicitamente as funções, classes e constantes extraídas que já oferecia. Manter nomes públicos e privados em uso, inclusive `_without_leading_comments`, `_detect_auth_prefix`, `_user_tables`, `SIMULADOS_FINGERPRINTS` e `PLANOS_FINGERPRINTS`. Usar imports explícitos, sem `import *`, `__getattr__`, manipulação dinâmica de módulos ou wrappers duplicando implementações.

Os coordenadores e a CLI permanecem definidos em `migrate.py`, resolvendo nesse módulo nomes como `connect`, `discover_migrations`, `status_lines`, `run_up`, `run_baseline` e `reconcile_failure`. Assim, os patches atuais dos unitários continuam verificando o mesmo ponto de chamada. `MigrationError` e `Migration` são as únicas definições de seus tipos, reexportadas pelo módulo original; não criar classes homônimas incompatíveis.

Inventário mínimo de consumidores a preservar, conferido no preflight do apply:

- `integration_support.py`, `migration_integration_support.py` e `scripts/run_e2e.py`: configuração, conexão, descoberta, parser e `run_up`;
- testes de migrations: execução, baseline, histórico, erro, helpers e fingerprints;
- unitários de autenticação: `_detect_auth_prefix`;
- unitários do runner: `from database.migrate import DatabaseSettings`.

Para execução por caminho, antes dos imports `database.*`, adicionar **somente quando `__package__` estiver vazio** a pasta `backend` absoluta, derivada do próprio `__file__`, ao início de `sys.path`. Depois, usar os mesmos imports absolutos da execução em pacote. Isso permite `python backend/database/migrate.py` sem depender do diretório de trabalho. Não usar fallback `try/except ImportError`, carregar módulos por string, alterar variáveis globais do Windows ou criar `__init__.py` só para contornar a estrutura atual.

Manter `PROJECT_ROOT` na localização original e o valor de `DEFAULT_MIGRATIONS_DIR` equivalente; a constante pode ser definida em `sql_scripts.py`, que fica na mesma pasta dos scripts e do runner, e reexportada. `migrate.pymysql` permanece disponível porque conexão e consumidores existentes ainda o utilizam. Não alterar Makefile, runners, CI ou integrações para ocultar uma quebra de compatibilidade.

### 4. Testes que comprovem o comportamento preservado

Ampliar apenas `backend/tests/unit/test_migrations.py`. Reaproveitar os casos de configuração, sequência/checksum, parsing/procedure, execução/falha, locks e CLI. Não substituir seus asserts nem mover mocks para integrações. Os testes existentes já exercitam a implementação extraída pelos nomes originais.

Adicionar verificações comportamentais focadas:

1. Importar os três módulos novos e `database.migrate` em processo isolado, com configuração inválida/fictícia e conexão bloqueada por mock unitário. A importação deve terminar sem carregar configuração, conectar ou executar a CLI. Validar a identidade do erro compartilhado pelo comportamento de captura de uma entrada inválida, sem teste que apenas espelhe imports do código.
2. Executar `python <caminho-absoluto>/backend/database/migrate.py --help` a partir de diretório temporário, com `.env` desabilitado. Esperar saída 0 e os quatro subcomandos, sem conexão.
3. Executar `python -m database.migrate --help`, com `PYTHONPATH` apontando para `backend`, em diretório temporário. Mesma saída funcional. Esses dois comandos detectam falha de resolução de pacote que unitários importados no mesmo processo não revelariam.

Usar `sys.executable` e limites de tempo nos subprocessos, preservando o ambiente do processo de teste sem exibir seu conteúdo. Não criar testes de contagem de linhas ou um teste por helper reexportado. Capturas antigas com patch da CLI e testes do runner E2E devem continuar aprovados sem alteração.

No apply, as validações são sequenciais:

- Após extração de scripts: executar unitários de migrations, cobrindo parsing e CLI.
- Após extração do reconhecimento: executar unitários de migrations/autenticação/runner e conferir AST/corpos movidos, constantes e fingerprints com o baseline. Verificar descoberta de `000`–`009`, sem escrita no banco.
- Antes de concluir: `python backend/tests/run_backend_coverage.py`, com `RUN_MYSQL_INTEGRATION=1` e `RUN_MYSQL_MIGRATION_INTEGRATION=1` apenas no processo. As 29 integrações originais e regressões atuais, incluindo instalação limpa, baseline de todos os prefixos, drift, procedure, falhas, concorrência e equivalência do bootstrap, precisam passar no MySQL real. Gates mantidos: 90% linhas/85% branches e nenhum arquivo executável novo zerado.
- Executar `npm run test:e2e` pelo runner oficial com `RUN_MYSQL_E2E=1` apenas no processo. Confirmar os dois testes Playwright, migrations oficiais e limpeza do schema/processos. Essa validação cobre o consumidor `scripts/run_e2e.py`, sem modificá-lo.

Configuração deve ser fornecida por ambiente ou pelos loaders normais já autorizados, sem abrir/imprimir `.env`, persistir credenciais ou exportar sessões. Ausência de MySQL é impedimento real para aprovação, sem fallback para mocks/SQLite. Se uma autorização anterior não estiver disponível no contexto do apply, manter a configuração pendente em vez de ler o arquivo por conta própria. Nenhum comando de atualização, baseline ou reconciliação será executado no banco operacional; as escritas ocorrem somente nos schemas descartáveis dos testes.

Frontend não muda; sua suíte DOM/cobertura completa não precisa ser repetida apenas por esta extração. Registrar resultados novos e limites em `validacao.md`, separados das evidências históricas.

### 5. Documentação curta e escopo verificável

Atualizar somente o README, na árvore/explicação de migrations, com os três módulos e uma frase por responsabilidade. Explicitar que `migrate.py` continua sendo o comando oficial e que a divisão aplica responsabilidade única à infraestrutura. Preservar os exemplos `status/up/baseline/reconcile`, os avisos operacionais e links. Não criar guia de estudo, novo ADR ou reescrever decisões históricas.

O delta permitido contém seis arquivos de produto/teste/documentação: `migrate.py`, os três módulos novos, `backend/tests/unit/test_migrations.py` e README. Artefatos/registro da própria change ficam separados. No preflight, registrar hashes dos arquivos locais não sensíveis em `test-results/organizar-migrations/`, ignorado; guardar especialmente hashes das migrations SQL, bootstrap, specs, runners, configurações e visuais oficiais. Após aplicar, confirmar preservação do restante e ausência de arquivos/SQL alterados fora desse conjunto. Não ler ou incluir `.env`, temporários ou credenciais no manifesto.

## Risks / Trade-offs

- **Ciclo de imports ou erro de identidade de exceção:** tipos mínimos compartilhados; dependências num único sentido; testes de importação e captura do erro.
- **CLI funciona importada, mas falha por caminho:** smoke em subprocesso nos dois modos, fora da raiz; bootstrap estático de caminho apenas para execução direta.
- **Patches unitários deixam de atingir o coordenador:** manter CLI/coordenação no arquivo original e reexportar explicitamente; executar os testes anteriores intactos.
- **Mudança acidental de parser ou fingerprint:** extração mecânica, comparação de corpos/constantes e integrações reais; SQL/hash históricos intocados.
- **Dividir arquivo sem melhorar compreensão:** três módulos adjacentes com papéis explícitos, documentação curta e nenhuma abstração adicional. Não alegar redução das regras internas.
- **Novo módulo sem cobertura ou mudança de escopo:** gates existentes aplicados aos arquivos extraídos; não alterar omit/thresholds. Defeito funcional descoberto exige revisar a proposta antes de corrigir.

## Migration Plan

Nenhuma migration de banco ou deploy. Durante o apply: preflight; extração dos tipos/scripts com regressão unitária; extração da inspeção histórica com regressão; documentação e validações completas. Se falhar, corrigir somente a extração no escopo; não editar SQL ou contornar proteções. Para desfazer o delta, restaurar apenas os seis arquivos a partir do baseline e remover somente os três arquivos introduzidos, preservando mudanças legítimas posteriores.

Após verificação sem achados críticos, registrar sync não aplicável (`skip_specs: true`) e arquivar pela skill apropriada. Commit/push, AWS e guia de estudo não fazem parte desta proposta e não serão executados automaticamente.
