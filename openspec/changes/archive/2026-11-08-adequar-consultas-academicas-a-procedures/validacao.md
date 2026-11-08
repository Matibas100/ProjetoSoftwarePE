# Validação — Consultas acadêmicas por procedures

## Estado inicial — 07/11/2026

Schema OpenSpec: `spec-driven`; início com 0/17 tarefas. MySQL 8.0.44 disponível em preflight de conexão somente leitura. Nenhum DDL/DML executado no banco de uso. Testes usarão schemas descartáveis.

### Alterações anteriores à sessão

```text
 M README.md
 M docs/technical/diagrama-de-classes.md
 M docs/technical/entrega-academica.md
?? docs/technical/matriz-crud.md
?? docs/technical/modelagem-de-dominio.md
?? openspec/changes/adequar-catalogo-editorial-a-procedures/
?? openspec/changes/adequar-consultas-academicas-a-procedures/
?? openspec/changes/adequar-contas-privacidade-a-procedures/
?? openspec/changes/adequar-plano-estudos-a-procedures/
?? openspec/changes/adequar-praticas-simulados-a-procedures/
?? openspec/changes/archive/2026-11-07-formalizar-modelagem-e-cobertura-crud/
?? tmp/
```

As alterações documentais e demais changes acima são externas e serão preservadas. A change documental `formalizar-modelagem-e-cobertura-crud` está arquivada; matriz CRUD e modelagem estão presentes. Não há migrations 011/012 nem colisão de versões no estado inicial.

### Recorte conferido

C01/C02: catálogo administrativo → adaptadores de Conteúdo → CatalogoRepository; C03: gestão de Questões → QuestaoRepository; C04: diagnóstico → ConsultaMetricasMySQL → DesempenhoRepository; C05: dashboard Aluno → diagnóstico/atividades; C06: dashboard Administração → APIs públicas de Conteúdo/Simulados → contagens. Sete procedures e quatro views conforme inventário. Consultas restantes ficam nas próximas changes.

### SHA-256 inicial

A migration 002 contém a definição da procedure legada protegida. Contratos públicos e artefatos visuais também estão protegidos. Hashes documentais registram as alterações externas iniciais.

| Arquivo | SHA-256 |
|---|---|
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
| `backend/app/contracts/__init__.py` | `b8192eb073bff89e062128bf863108a1af090b8f73c767372fb78cdc1693eef7` |
| `backend/app/contracts/catalogo.py` | `254796eb1d93e925adfd64d7c6032df011f86fa60979533edd6783373023833e` |
| `backend/app/contracts/desempenho.py` | `e76fc41c0c3df5122ca96c50cdf0f59f78c446d6b0c4e7a25e2689e61ad19391` |
| `backend/app/contracts/questoes.py` | `47831dfc93bbc1a96d982c5b4d6d0808f13b5273488693c682685ba786913f44` |
| `backend/app/contracts/simulados.py` | `f895f1f34f52ae62aead79d61ef008be735540586ebf590c2776da226f2737f7` |
| `backend/app/routes.py` | `91e79070ece940db108b4e1ca37a178fd5e42520b69195637fe8d77fb239f6eb` |
| `backend/app/models/__init__.py` | `bf2e84b8c2c38919e9475057d2f7a41156d96bd0ff31c0f29c94f842b466f56e` |
| `README.md` | `8bbf9ff3540c82b70b82f14606df988f3fa038b7de08e883e05e4c10e508ead5` |
| `docs/technical/diagrama-de-classes.md` | `c94966b7ed9685c915d401c2f8e377330e276fc248798c658048da8a3d8282d9` |
| `docs/technical/entrega-academica.md` | `3febb4435408ca7014a25f64def5149910ad073626ef72065c56bba780d7798f` |
| `docs/technical/matriz-crud.md` | `2ca885a4fa3b53c01525b7bc97d0608bbad4602b1575e0ac2df5c869a028ca17` |
| `docs/technical/modelagem-de-dominio.md` | `cc60004f4cc9bf1ea8cdf00e475a10f1462bb2fe6983872e944aba2bc565828a` |
| `docs/design/desktop-v1/ERRATA.md` | `73bb5a35ebf96dec7aac843ea859f888344493daf368563969df1e5249481171` |
| `docs/design/desktop-v1/Plataforma_ENEM_Handoff_Mestre_Desktop_FINAL.pdf` | `f99f7656901fa552f06dd47286b8dd30475941b86516adb5d773c0247b089d87` |
| `docs/design/desktop-v1/Plataforma_ENEM_Inventario_Mestre_Desktop_FINAL.xlsx` | `bf8d051467c6620eb88132cb56f8ed72d3c1ea6142fa9f415319a7b898fbb22e` |
| `docs/design/desktop-v1/Plataforma_ENEM_Logo_Oficial_SVG_FINAL.zip` | `ce4aeba68a05f607942b711341c7ba1cbb77598cadea06d14199df921809456e` |
| `docs/design/desktop-v1/Plataforma_ENEM_Prototipo_Clicavel_Desktop_FINAL.pdf` | `2c673428337bb14330406a28a9c16dba1f4634335b5c68e5c918bdb78a853a52` |
| `docs/design/desktop-v1/README.md` | `ce74102e5c860ff123acb9840594230d285d27a484f4634a59ff321ed8ed361c` |

## Caracterização anterior à substituição

- `RUN_MYSQL_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_catalogo_admin_integration tests.test_desempenho_integration -v`: 18 testes aprovados, 27,267 s. Abrange as seis rotas, amostras 0/4/5, histórico/transferência, branco, autorização, microssegundos, snapshot e rollback externo.
- `python -m unittest tests.test_consultas_academicas_integration -v` (mesmo opt-in): 2 testes novos aprovados, 5,043 s. Campos/datas/nulos comparados aos retornos atuais, JOIN com múltiplas Questões, filtros combinados, LIKE vs substring literal, entrada semelhante a SQL e paginação/IDs acima de 2^31. A expectativa inicial foi corrigida para a chave contratual existente `total_itens`.

## Infraestrutura participante

- `PYTHONPATH=backend; python -m unittest tests.unit.test_procedures_mysql -v`: 5 testes aprovados (parâmetros, vazio útil, terminal, drenagem, fechamento e invalidação).
- `RUN_MYSQL_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_consultas_academicas_integration -v`: 3 testes aprovados, 4,711 s. Procedure sintética real retorna vazio e total; SELECT posterior funciona na mesma conexão e escrita anterior é revertida pela transação externa.

## Migration 011 e listagens

- `python -m unittest tests.test_consultas_migrations_integration -v` com os dois opt-ins MySQL: 1 teste aprovado, 2,779 s; instalação parcial 011, quatro routines INVOKER/READS SQL DATA, rejeição estrutural, página vazia e SELECT subsequente. Ajustada a posição de DELIMITER ao parser oficial antes da instalação bem-sucedida.
- `python -m unittest tests.test_consultas_academicas_integration tests.test_catalogo_admin_integration tests.test_questoes_versionadas_integration -v`: 18 testes aprovados, 14,963 s, já pelas procedures.
- `python -m unittest tests.unit.test_arquitetura_modular -v`: 6 testes aprovados, 2,427 s. ADR-011 e documento técnico adicionados; nenhum novo mapper/Model/import privado entre módulos.

## Migration 012, reconhecimento e participação

- As onze referências em `backend/database/sql_resources_reference.json` foram geradas por instalação completa das migrations oficiais num schema aleatório `plataforma_enem_migration_test_*`, removido em `finally`. Nenhum banco encontrado foi adotado como referência. Reconhecimento retornou 012.
- `python backend/tests/run_unit.py`: 181 testes aprovados, 4,279 s (inclui arquitetura, guards e novos testes de metadados/normalização; não carrega `.env`).
- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; PYTHONPATH=backend; python -m unittest tests.test_consultas_academicas_integration tests.test_consultas_migrations_integration tests.test_desempenho_integration tests.test_planos_integration -v`: 29 testes aprovados, 110,582 s. Inclui subcasos de assinatura/corpo/segurança/view/coluna/destino externo, baseline/restauração de 011/012 com dados, leitura histórica, snapshots concorrentes e rollback real do Plano.
- As barreiras/falhas dos testes passaram a observar o cursor real de PyMySQL (`tests/sql_observer.py`), pois CALL direto não emite eventos ORM. As consultas/resultados seguem sendo executados no MySQL, sem mocks. Corrigida a comparação de assinatura da fixture para considerar a grafia de SHOW CREATE.
- Um teste novo ficou esperando metadata lock porque seu app_context externo manteve a sessão HTTP aberta durante o DDL de restauração. A execução foi interrompida e somente seu schema descartável validado foi removido. A fixture agora remove essa sessão antes do DDL; a nova execução de 29 testes acima passou. Nenhum DDL atingiu o banco de uso.

## Frontend e navegador

- `npm run test:coverage`: 15 arquivos/182 testes aprovados. Linhas 99,26% (1879/1893), branches 87,98% (1325/1506). Gates mantidos.
- `python scripts/run_e2e.py`, por processo com `RUN_MYSQL_E2E=1` e configuração MySQL transmitida no ambiente sem imprimir valores: 3 testes aprovados, 54,4 s. Exercita as vinte funcionalidades, Plano/Simulado e privacidade no Chromium com persistência real. O runner não leu `.env`; schema e servidores descartáveis foram encerrados.

## Complementos e revisão documental

- `python -m unittest tests.test_desempenho_integration.DesempenhoIntegrationTest.test_views_preservam_fatos_e_atividades_apos_arquivamento tests.test_desempenho_integration.DesempenhoIntegrationTest.test_procedures_aluno_ausentes_falham_sem_blocos_parciais_e_pool_recupera -v` com opt-in MySQL: 2 testes novos aprovados, 7,255 s. Fatos/atividades permanecem após arquivar Simulado, Questão, Assunto e Matéria; falta de cada rotina do dashboard Aluno gera apenas erro seguro e o pool volta a funcionar após restauração.
- Links locais dos seis documentos atualizados conferidos; vinte IDs da matriz acadêmica preservados exatamente (1–20). Matrizes e README receberam somente o complemento do recorte real, preservando o conteúdo externo.
- SHA-256 conferidos: migrations 000–010, contratos, registro ORM, rotas, diagrama/modelagem externos e artefatos Desktop V1 permanecem iguais ao estado inicial. Somente README, matriz acadêmica e matriz CRUD mudaram entre os hashes documentais iniciais, conforme escopo. As fontes legais também são verificadas pelos hashes contratuais dos unitários.

## Revisão do reconhecimento e primeira suíte completa

- Primeira execução de `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; python backend/tests/run_backend_coverage.py`: 181 unitários e 148 integrações aprovados (integrações: 384,192 s), incluindo as 29 integrações originais. Gates: linhas 97,46% (4136/4244), branches 91,75% (890/970).
- Após essa execução, a revisão acrescentou um teste que demonstrou colisão entre o marcador textual local e um schema externo com o mesmo nome do marcador. Corrigido com identidades tipadas distintas (`local` / `external` com nome preservado) nas dependências. As quatro referências de views foram regeneradas somente por instalação oficial descartável; os sete contratos de procedures não mudaram. O novo teste passou.
- O reconhecimento agora confere as tabelas de 010 antes de comparar os contratos adicionais. Inventário indisponível falha fechado. A suíte completa será repetida sobre esta versão final; os números acima são da primeira execução, não substituem a verificação final.
- Conferido também que o bootstrap anterior completo é prefixo textual do atual (normalizando somente CRLF para LF); as definições legadas foram preservadas e somente os blocos 011/012 acrescentados.

- `python -m unittest tests.test_consultas_migrations_integration.ConsultasMigrationsIntegrationTest.test_upgrade_010_011_012_dados_baseline_e_referencias_oficiais -v` com ambos os opt-ins: 1 teste aprovado, 9,271 s, já com as identidades tipadas finais. Baselines/restaurações 011/012, registros preservados, upgrade e idempotência conferidos.

## Revisão final de escopo

- `openspec validate adequar-consultas-academicas-a-procedures --strict`: aprovado.
- `git diff --check`: aprovado. O aviso de normalização CRLF/LF do bootstrap não é erro; seu prefixo anterior foi comparado e preservado integralmente após normalização de finais de linha.
- Rechecados SHA-256 protegidos, onze referências oficiais, sete procedures/quatro views, arquivos novos em UTF-8 sem BOM, whitespace e padrões de segredos. Nenhuma credencial encontrada nas alterações. Contratos HTTP/públicos, 21 Models, procedure legada, migrations antigas e artefatos congelados permanecem.
- As alterações externas iniciais foram preservadas; somente os três documentos previstos receberam complementos. Outras changes, diagrama e modelagem não foram editados. Não houve commit/push/merge, deploy ou DDL no banco de uso. Toda instalação e escrita de validação ocorreu em schemas descartáveis validados.

## Resultado final — versão corrigida

- `RUN_MYSQL_INTEGRATION=1; RUN_MYSQL_MIGRATION_INTEGRATION=1; python backend/tests/run_backend_coverage.py`: **183 testes unitários + 148 integrações MySQL aprovados**, incluindo as 29 integrações originais; nenhuma integração pulada. Unitários: 4,331 s; integrações: 391,705 s.
- Cobertura backend final: **97,46% de linhas (4140/4248)** e **91,74% de branches (888/968)**; gate de arquivo executável sem cobertura também aprovado. Logs locais: `tmp/consultas-backend-coverage.log`.
- Frontend já aprovado: **182 testes**, **99,26% de linhas** e **87,98% de branches**. E2E: **3 testes aprovados**, incluindo os vinte percursos e as extensões de Plano/Simulado/privacidade, com MySQL real e limpeza dos recursos descartáveis.
- Não foi necessário reduzir gates ou acrescentar dependências. A correção final afetou somente o reconhecimento SQL e suas referências, cobertos novamente pela suíte completa; contratos de aplicação não mudaram após o E2E.
- **17/17 tarefas da aplicação concluídas.** Próximas etapas: verificar pela skill OpenSpec, sincronizar os dois deltas e só então arquivar. A change de Catálogo continua condicionada à verificação/sincronização desta dependência.

## Verificação e sincronização concluídas

Na retomada do workflow, foram conferidos completude (17/17), correção dos cenários/testes e coerência com design/ADRs/conventions, sem achados críticos. Os 17 testes focados de arquitetura, cursor e reconhecimento passaram novamente (1,522 s); hashes protegidos e correspondência das fontes com a cobertura final foram conferidos. A verificação não alterou código ou artefatos.

Sincronizados os seis requisitos de `consultas-academicas-mysql` e o requisito de recursos SQL acadêmicos em `migrations-sql`, preservando os requisitos anteriores e Purpose. `openspec validate --specs`: 12 specs aprovadas. A dependência ficou liberada para Catálogo. A change permanece ativa, sem arquivamento ou operações Git.

## Reconferência e arquivamento — 08/11/2026

- Verificação atual sem achados críticos: `python backend/tests/run_unit.py` aprovou 183 testes; integrações focadas de consultas acadêmicas, migrations de consultas, catálogo administrativo, desempenho e planos aprovaram 38 testes MySQL reais em schemas descartáveis (71,565 s), com ambos os opt-ins somente no processo.
- Conferidos 24 hashes protegidos, os blocos 011/012 no bootstrap e os sete requisitos dos dois deltas já presentes integralmente nas specs principais. `openspec validate --specs`: 16 specs aprovadas; validação estrita da change e `git diff --check` aprovados.
- Arquivamento solicitado explicitamente e realizado pelo CLI, preservando `.openspec.yaml`. A atualização automática de specs foi dispensada por já estarem sincronizadas. Link do inventário no ADR-011 ajustado ao arquivo histórico. Nenhum código de aplicação ou banco de uso foi alterado nesta etapa; sem commit, push ou merge.
