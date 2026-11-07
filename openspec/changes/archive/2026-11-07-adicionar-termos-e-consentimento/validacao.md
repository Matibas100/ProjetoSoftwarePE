# Validação — Termos e consentimento

## Preflight em 06/11/2026

Lidos proposal, design, as três delta specs, cinco conventions, arquitetura mestre e ADRs 001/002/006/008. Schema `spec-driven`, estado inicial `ready`, 0/16 tarefas. Aplicação autorizada pelo usuário; commit, push e banco operacional fora da execução.

O escopo aprovado envolve documentos públicos, privacidade, cadastro, quatro operações do plano, migration 010, testes e documentação correspondente. Preservar seletor, diagnóstico independente, contratos de sessão e artefatos oficiais.

Baseline local: `tmp/termos-baseline/baseline.json`, cópias byte a byte em `tmp/termos-baseline/files/` e inventário Git em `tmp/termos-baseline/status.txt`. Inclui os arquivos existentes potencialmente afetados e registra o estado local anterior. Esses temporários não são entregáveis.

Alterações locais prévias: README; Controllers e Services de paginação; runner e módulos de migrations; convenções; entrega acadêmica; navegação HTML/CSS; cliente API e testes; changes anteriores arquivadas e change de JOIN. Nenhuma será revertida. A própria change de termos já existia como não rastreada.

Não foram lidos `.env` ou valores de credenciais operacionais. Configuração dos testes sintética e restrita ao processo, com `PYTHON_DOTENV_DISABLED=1`. MySQL 8.0 em container descartável, somente loopback, sem volumes operacionais; schemas aleatórios das fixtures oficiais. Binários de Desktop V1 e migrations anteriores permanecem protegidos.

Modelos encontrados em `C:/Users/Matheus/Downloads`: `MODELO DE TERMO DE USO DO SISTEMA - LGPD.docx` e `MODELO DE TERMO DE CONSENTIMENTO - LGPD.docx`. Leitura somente para adaptação, sem modificar fontes. O design prevalece nas exclusões de promessas não implementadas, dados excessivos e aceite presumido. Referências oficiais de LGPD/ANPD/ECA Digital reconferidas durante aplicação. Os HTML foram elaborados em 06/11/2026; a validação continuou em 07/11/2026, sem alterar a data editorial dos documentos.

## SHA-256 das migrations anteriores

| Arquivo | SHA-256 inicial |
| --- | --- |
| `000_create_mvp_schema.sql` | `1e51d54b93a4d8125961a17e283e2933fa3fe1f0b8b385b6d50ede1bcdf868a8` |
| `001_restrict_delete_assuntos.sql` | `329594db44e2ee7f6a71b4c8a871cc5efb1dd849642ed4397b49a3ae7dca0b5d` |
| `002_create_sp_questoes_por_assunto.sql` | `7d19427eaed0f6e63ec4116aee0aa56cf07a2e12b6e559c2a09f5409414abd38` |
| `003_prepare_catalogo_academico.sql` | `dd27f63de40fd06585c4a3cbd33a9f164574ae983b3eeb3cffb8ff91a8decbd4` |
| `004_restrict_catalogo_academico.sql` | `de6bedc463391556498fe641cb61fe74a59717b421c59e0dfcb1d6ff71a804d8` |
| `005_create_autenticacao_escolar.sql` | `a650da20e8785b4de919e0324928844a282f63b76bacce0f752fdb55332fb8c2` |
| `006_create_questoes_versionadas.sql` | `97160b8fb019d8dc59e7f83452808b5fefd9a1944f20850d6336880822e2b36c` |
| `007_create_pratica_tentativas.sql` | `2ca7fc6c974dfa2e0011d72bc532a00a0e4cca8d9ab0055cdd9c4b93f58c3161` |
| `008_create_simulados.sql` | `b21286bbfcb77ba6bad04c1eda72d7fbc71b39dc825c847238cce1b73d71fe36` |
| `009_create_planos_estudo.sql` | `22763b2c463d65995f79a93aaa34a6ff3a760f591d94cfb19822be646126a624` |

## Execução

Implementação e validações concluídas em 07/11/2026. As mudanças são locais,
sem commit, push, merge, publicação ou implantação no banco operacional.

| Validação concluída | Resultado |
| --- | --- |
| Regressão inicial de Matéria/Assunto/Questão | 30 testes passaram, incluindo os 29 cenários originais e complemento existente |
| Hashes e estados dos documentos | 2 unitários iniciais passaram; incluídos na suíte ampliada |
| HTML público sem JS | Dois documentos em 1440/390, teclado e impressão; capturas/PDFs temporários em `tmp/`, inspeção visual do uso em 390 |
| Migrations de privacidade | 3 testes passaram em MySQL real: constraints, upgrade sem backfill, snapshot/baseline/reexecução/drift |
| Integrações específicas | 11 testes passaram, incluindo transações, isolamento, replay, concorrência, snapshot anterior à negativa/nova autorização, falhas reais por trigger e falha fechada da leitura |
| Vitest com cobertura | 169 testes passaram; 99,26% linhas e 87,97% branches agregados; nenhum executável zerado |
| Backend com cobertura | 160 unitários; suíte de 128 integrações executada e cenário de autorização atualizado/reexecutado; complemento de 15 passou, incluindo o novo cenário (129 integrações distintas no conjunto final). 97,57% linhas e 91,22% branches; nenhum executável zerado |
| Servidor estático | 7 testes passaram, incluindo recursos e leitura pública dos dois HTML |
| E2E completo | 3 testes passaram: vinte casos originais; plano/simulado; privacidade independente com dados reais de estudo em MySQL |
| Visual | Capturas de privacidade inspecionadas em 1440/390; textos, evidências, ações e quebra do hash legíveis, sem overflow |
| OpenSpec | `openspec validate adicionar-termos-e-consentimento --strict`: válido |
| Revisão final | Diff contra baseline conferido; migrations 000–009, procedure e binários oficiais intactos; zero padrões de segredo detectados sem exibir valores |

O primeiro preflight MySQL recusou senha vazia sintética; o container recebeu
configuração de teste compatível e a regressão foi reexecutada. Um teste de
preservação do desempenho comparava também o instante de consulta; foi corrigido
para comparar métricas/base/agrupamentos, preservando a verificação funcional.
Expectativas anteriores de plano após falha foram atualizadas para a limpeza
exigida nesta change. Nenhuma exceção de requisito foi aceita.

A execução integral inicial do backend terminou com 127/128 integrações
aprovadas: a matriz antiga de autorização esperava plano 200 sem consentimento.
Foi atualizada para o novo contrato (403 para plano sem autorização e metadados
públicos) e reexecutada com sucesso no complemento. O complemento também valida
upgrade preservando duas contas, planos, itens e respostas corrigidas. Não foi
necessário repetir as outras 127 integrações, pois não houve nova mudança de
produção após a execução integral.

O primeiro E2E também revelou essa expectativa antiga no smoke acadêmico;
foi acrescentada a escolha explícita pela interface. No teste de retorno de
outra aba, `bringToFront` em Chromium headless não emitiu foco de forma confiável:
após abrir a aba real e revogar pela interface, o teste dispara o evento `focus`
para executar o mesmo handler de retorno. Autenticação, consultas, decisões e
persistência continuam reais, sem bypass ou respostas simuladas. Essa é uma
limitação do teste de ativação em headless, não uma alegação de ensaio manual em
todos os navegadores. A suíte completa reexecutada terminou 3/3 aprovada.

## Comandos e ambiente

Variáveis somente no processo: `PYTHON_DOTENV_DISABLED=1`,
`RUN_MYSQL_INTEGRATION=1`, `RUN_MYSQL_MIGRATION_INTEGRATION=1` ou
`RUN_MYSQL_E2E=1`, conforme o runner. Configuração MySQL exclusivamente sintética
para o container descartável, sem registrar seu valor neste documento.

```text
python -m unittest tests.test_materias_integration tests.test_assuntos_integration tests.test_questoes_integration -q
python -m unittest tests.test_privacidade_migration_integration -v
python -m unittest tests.test_privacidade_integration -q
python backend/tests/run_backend_coverage.py
python -m coverage run --parallel-mode -m unittest tests.test_autenticacao_integration.AutenticacaoIntegrationTest.test_autorizacao_todas_rotas_existentes tests.test_privacidade_integration tests.test_privacidade_migration_integration -q
python -m coverage combine
python -m coverage json
python scripts/validate_backend_coverage.py
npm run test:coverage
python -m unittest discover -s scripts/tests -q
python scripts/run_e2e.py
openspec validate adicionar-termos-e-consentimento --strict
git diff --check
```

Unitários do primeiro runner: 160/160. Complemento: 15/15. Cobertura backend:
3901/3998 linhas e 852/934 branches. Frontend: 1878/1892 linhas e 1323/1504
branches. Limiares 90%/85% satisfeitos em ambas as stacks.

Logs temporários: `tmp/termos-unit.log`, `tmp/termos-backend-coverage.log`,
`tmp/termos-backend-complementar.log`, `tmp/termos-frontend-coverage.log`,
`tmp/termos-e2e.log`; relatório E2E em `test-results/e2e.json`.
Capturas são sintéticas e ignoradas pelo Git. Não foram gerados vídeo, HAR,
trace ou storage state autenticado.

Na revisão final, os links da página de privacidade foram ligados às URLs
vigentes retornadas pela API. O teste adicional cobre leitura da versão nova
e revogação da aceitação antiga; a cobertura frontend completa foi reexecutada.
O container MySQL criado para esta execução foi parado/removido após os testes;
as fixtures e o runner E2E removeram seus schemas e processos temporários.

## Correspondência de requisitos e evidências

| Requisitos/cenários | Implementação | Evidência |
| --- | --- | --- |
| Documentos públicos, versões, hashes e transparência acadêmica | `frontend/legal/`, `docs/legal/`, domínio de privacidade e `ConsultarTermosService` | Unitários de hash; HEAD/GET público; E2E sem JS, teclado e 1440/390; inspeção de texto/visual |
| Uso separado de plano, conta anterior e cadastro explícito atômico | `CadastrarAlunoService`, preparação compartilhada/CLI e `AceitarTermosUsoService` | Integrações de cadastro inválido, duplicidade concorrente existente, falha real da evidência, estado inicial/legado e aceite de uso; Vitest do checkbox/versão |
| Consulta própria, evidência e políticas HTTP | `PrivacidadeController`, `ConsultarPrivacidadeService`, middleware, Model e Repository | Integrações de 401/403, HEAD/no-store, 404/405, CSRF/Origin, campos extras, conta alheia e imutabilidade/UTC |
| Escolha opcional, versão/hash vigente, recusa e revogação antiga | Services específicos, validação e `estado_privacidade` | Unitários de estados/validação; integrações de transições e revogação de versão fora do mapa; API do plano bloqueada para aceitação antiga |
| Negativa confirmada, eliminação restrita, rollback e nova autorização | Repository especializado, FK RESTRICT e transação única | Integrações de múltiplas gerações/conclusões, legado sem decisão, outra conta preservada, resposta/desempenho preservados e trigger real falhando após exclusões parciais; E2E mantém simulado finalizado |
| Reenvio antigo não reaplica efeitos e decisões concorrentes | UUID por conta, revisão por tipo, lock de usuário e leitura corrente | Replay negativo após novo plano; conflito de revisão/chave; duas decisões concorrentes; snapshot antigo antes de revogação e nova autorização |
| Guard antes de recursos/replay/diagnóstico e disputa com geração/recálculo | `ValidarPermissaoPlanoService` e quatro casos de plano | Unitário de ordem lock→guard e ausência de consulta posterior; integração de 403 uniforme, falha real de leitura 500 e disputas com negativa; regressão completa de plano |
| Interface acessível, escolha equilibrada, retry, sessão/identidade e aba | Cadastro, privacidade, plano, AuthUI e apiRequest | Vitest com revisão/chave, cancelamento sem POST, replay histórico com estado atual, expiração/recuperação, troca de conta e resposta atrasada; E2E de três percursos |
| Evolução aditiva e preservação no upgrade | Migration 010, snapshot, fingerprint e baseline | Instalação vazia, equivalência, baseline 010, reexecução, drift e upgrade 009 com contas/planos/itens/respostas; checksums anteriores idênticos |
| Documentação e arquitetura | Operação, ADR-009, matriz, mapa, diagramas, README | Conferência das 21 Models e seis rotas novas; camadas respeitadas, sem SQL/session em Controllers/Services; vinte casos acadêmicos preservados |

## Limites e próximos passos

Não foi feita operação no banco real do projeto. Uso real permanece dependente
de contato operacional, política geral de retenção/direitos e proteção de menores,
como declarado nos dois documentos. A exclusão confirmada de planos é irreversível
na aplicação, sem promessa sobre exclusão imediata em backups.

A implementação está preparada para verificação OpenSpec, seguida de
sincronização/arquivamento pelo workflow. Esta execução de apply mantém a change
ativa e não altera as specs principais; commit/push continuam fora do escopo.

## Encerramento do workflow em 07/11/2026

Após o apply, a verificação não encontrou achados críticos. A sincronização
atualizou dois requisitos de autenticação e cinco do plano e criou a capability
de termos com nove requisitos e 28 cenários, preservando Purpose e conteúdo
não afetado. `openspec validate --specs` aprovou 11/11 specs, com avisos de
tamanho de descrições; a change também passou na validação estrita.

No preflight de arquivamento: todos os artefatos completos, 16/16 tarefas
concluídas, nenhuma pendência de sincronização nas três delta specs e destino
`archive/2026-11-07-adicionar-termos-e-consentimento/` disponível. Arquivamento
autorizado pelo usuário; sem novas alterações de código, banco ou operações Git.
