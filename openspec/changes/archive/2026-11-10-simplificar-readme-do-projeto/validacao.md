# Validação: simplificar README do projeto

## Estado inicial — 10/11/2026

- HEAD: `2a82c77b6978efdf32ecfc11deb25d529e576fc2`.
- README local: **701 linhas**, UTF-8, CRLF; SHA-256 `b62fe537d6a9e92d59f3921e4e51513c7ba7d25bc7e4be76e74e82c40f0aee5a`.
- Referência da proposta: mesmo HEAD e mesmo SHA-256; nenhuma diferença na fonte local.
- Fonte usada: arquivo local vigente. Não foi restaurada a versão do HEAD.
- Snapshot em memória de **740 arquivos existentes**, por SHA-256: fontes, configurações públicas, documentação e changes, incluindo o arquivo arquivado das ferramentas. Ausências também registradas. Não foi lido nem calculado hash de `.env` privado.
- `output/` e `tmp/` já existiam, são externos ao inventário de fontes e não serão editados, limpos ou usados como destino desta execução.
- A conferência final comparará os arquivos existentes e o estado Git com este snapshot.

Estado Git anterior à primeira edição:

```text
 M .gitattributes
 D .githooks/pre-push
 M README.md
 M package.json
 D scripts/install-git-hooks.mjs
?? openspec/changes/archive/2026-11-10-simplificar-ferramentas-de-desenvolvimento/
?? openspec/changes/simplificar-readme-do-projeto/
?? output/
?? tmp/
```

A simplificação das ferramentas já estava aplicada/arquivada e ainda não publicada.
O hook e o instalador estavam ausentes; nenhuma instrução de instalação será reintroduzida.

### Hashes públicos de referência

| Arquivo | SHA-256 inicial |
| --- | --- |
| `.gitattributes` | `7a19596a8992a58c88d1cfa3f973228ab03c65e92eb14fa546df4473949da814` |
| `package.json` | `0fbc3877165793bb421f0b2ae1e4f70f624203bbd5a4cbce1b46d185ed64cacb` |
| `Makefile` | `237b7e5d977744bb753ecb04897307a459b4d86dbf1e7b2f8da890d35aeafa94` |
| `.gitignore` | `1cb31500a3790f5bba7003f1a14f925c874dcbf19b766457558c6cd4340ac651` |
| `.env.example` | `0ac0eca37b8602dfb9829d5c35fb5ab1861ada139e4355b431883b0b2c2ce3d2` |
| `package-lock.json` | `22ebb5c936cf78b65e1026c60c1401e4ed64db90adaa0f49da4c39b2d525c360` |
| `backend/app/config.py` | `71546052c2d89588c7dc88b71df4c11657b12ae0d5cdf96103a59e80d9b5de36` |
| `backend/database/migrate.py` | `85a5f1bbcbf7c685399604d7832aa7f0a392f1ed43441c095e7cfb95e4b356de` |
| `docs/conventions/testes.md` | `9d6ba4789604b4cfb4b08f5917326a6254bdd684110b8c225ec6af9fb89674a1` |

Os demais hashes ficaram no snapshot da sessão para comparação final; não foram copiados segredos.

## Inventário de seções e mapa de transferência

Todas as 26 entradas abaixo correspondem aos títulos/IDs da origem. Os intervalos
incluem o conteúdo até o próximo título. Os IDs continuarão acessíveis no README,
por título preservado ou âncora explícita junto à indicação do destino.
O mapa foi iniciado no preflight e conferido após a transferência de cada seção.

| Linhas de origem | Título / ID antigo | Destino aprovado |
| --- | --- | --- |
| 1–22 | Plataforma ENEM — `plataforma-enem` | README: apresentação e limites acadêmicos; [privacidade](../../../../docs/technical/operacao-privacidade.md) |
| 23–34 | Gestão administrativa de Alunos — `gestão-administrativa-de-alunos` | README: destaque e [operação de Alunos](../../../../docs/technical/gestao-administrativa-alunos.md) |
| 35–46 | Tecnologias utilizadas — `tecnologias-utilizadas` | README: mesmo título |
| 47–105 | Arquitetura — `arquitetura` | README: mesmo título; [mapa modular](../../../../docs/technical/organizacao-modular.md), modelagem, SOLID e ADR-008/010 |
| 106–156 | Funcionalidades Implementadas — `funcionalidades-implementadas` | README: mesmo título e vinte itens literais |
| 157–188 | Componentes implementados — `componentes-implementados` | README: âncora junto aos links de modelagem, SOLID e mapa modular |
| 189–216 | Consulta individual do catálogo — `consulta-individual-do-catálogo` | [Operação do projeto](../../../../docs/technical/operacao-do-projeto.md#consulta-individual-do-catálogo) |
| 217–243 | Rotas legadas da API — `rotas-legadas-da-api` | [Operação do projeto](../../../../docs/technical/operacao-do-projeto.md#rotas-legadas-da-api) |
| 244–253 | Pré-requisitos — `pré-requisitos` | README: mesmo título |
| 254–273 | Preparação do ambiente — `preparação-do-ambiente` | README: mesmo título; cópia condicional da configuração privada |
| 274–299 | Criação e atualização do banco MySQL — `criação-e-atualização-do-banco-mysql` | README: instalação vazia; [operação](../../../../docs/technical/operacao-do-projeto.md#criação-e-atualização-do-banco-mysql) |
| 300–327 | Adoção de um banco MVP existente — `adoção-de-um-banco-mvp-existente` | [Operação do projeto](../../../../docs/technical/operacao-do-projeto.md#adoção-de-um-banco-mvp-existente) |
| 328–350 | Falhas e recuperação — `falhas-e-recuperação` | [Operação do projeto](../../../../docs/technical/operacao-do-projeto.md#falhas-e-recuperação) |
| 351–360 | Executando o backend — `executando-o-backend` | README: mesmo título |
| 361–373 | Executando o frontend — `executando-o-frontend` | README: mesmo título |
| 374–432 | Testes automatizados — `testes-automatizados` | README: comandos básicos; conventions e [particularidades](../../../../docs/technical/operacao-do-projeto.md#testes-e-atalhos-make) |
| 433–471 | Navegador e integração contínua — `navegador-e-integração-contínua` | README: seis testes e CI; [detalhes](../../../../docs/technical/operacao-do-projeto.md#navegador-e-integração-contínua) |
| 472–484 | Checkpoint publicado e CI — `checkpoint-publicado-e-ci` | README: mesmo título; [evidência datada](../../../../docs/technical/operacao-do-projeto.md#checkpoint-publicado-e-ci) |
| 485–510 | Testes locais e clones antigos — `testes-locais-e-clones-antigos` | [Operação do projeto](../../../../docs/technical/operacao-do-projeto.md#testes-locais-e-clones-antigos) |
| 511–537 | Visualização local no VS Code — `visualização-local-no-vs-code` | [Operação do projeto](../../../../docs/technical/operacao-do-projeto.md#visualização-local-no-vs-code) |
| 538–565 | Histórico de validação — `histórico-de-validação` | [Operação do projeto](../../../../docs/technical/operacao-do-projeto.md#histórico-de-validação) |
| 566–585 | Consultas acadêmicas por procedures — `consultas-acadêmicas-por-procedures` | README: âncora com [evolução histórica](../../../../docs/technical/operacao-do-projeto.md#consultas-acadêmicas-por-procedures), consultas MySQL e gestão de Alunos |
| 586–610 | Tutor IA: revisão pontual com Gemini — `tutor-ia-revisão-pontual-com-gemini` | README: resumo e [operação do Tutor](../../../../docs/technical/operacao-tutor-ia.md) |
| 611–651 | Contrato HTTP — `contrato-http` | [Operação do Tutor](../../../../docs/technical/operacao-tutor-ia.md#contrato-http) |
| 652–676 | Camadas, limites e dados — `camadas-limites-e-dados` | [Operação do Tutor](../../../../docs/technical/operacao-tutor-ia.md#camadas-limites-e-dados) |
| 677–701 | Evidências e demonstração — `evidências-e-demonstração` | [Operação do Tutor](../../../../docs/technical/operacao-tutor-ia.md#evidências-e-demonstração) |

### Vinte itens originais

Inventário literal da lista sob `Funcionalidades Implementadas`, para comparação após a edição:

1. Cadastrar Matéria.
2. Listar Matérias.
3. Atualizar Matéria.
4. Excluir Matéria sem vínculos.
5. Cadastrar Assunto.
6. Listar Assuntos.
7. Atualizar Assunto.
8. Excluir Assunto sem vínculos.
9. Cadastrar Questão.
10. Buscar Questões por Assunto.
11. Cadastrar Aluno.
12. Fazer login.
13. Editar Questão.
14. Publicar Questão com snapshot imutável.
15. Arquivar Questão preservando histórico.
16. Iniciar prática de Questão publicada.
17. Responder prática com correção persistida.
18. Consultar histórico próprio de práticas.
19. Criar Simulado manual com composição fixa.
20. Consultar desempenho por Matéria/Assunto.

## Execução das tarefas

- **1.1 concluída:** baseline, vinte itens, 26 títulos/IDs e mapa registrados;
  alterações locais anteriores preservadas.
- **2.1 concluída:** contratos legados e consulta individual, runner, adoção,
  recuperação, privilégios, Make/opt-ins, E2E, checkpoint, histórico, clones antigos
  e preferências locais transferidos. Fontes de domínio existentes continuam canônicas.
- **2.2 concluída:** seção original do Tutor transferida com links recalculados;
  configuração, contrato, HTTP, quatro partes, dados, limites e evidências preservados.
- **3.1 concluída:** README com 317 linhas, execução suficiente, destaques não CRUD,
  os mesmos vinte itens, 26 IDs anteriores e links para os destinos do mapa.
- **4.1 concluída:** links, comandos, contagens, evidências e integridade conferidos;
  `git diff --check` e validação OpenSpec estrita aprovados.

## Conferência de conteúdo e navegação

| Verificação estática | Resultado |
| --- | --- |
| README antes/depois | 701 → **317 linhas**; redução de 384 (**54,78%**); limite de 350 atendido |
| Codificação do README | UTF-8; 317 finais CRLF, preservando o padrão inicial |
| Lista de funcionalidades | **20/20 itens idênticos**, na mesma ordem, sob o mesmo título |
| IDs anteriores | **26/26 preservados** por títulos ou âncoras explícitas junto aos destinos |
| Links locais do README | **55**, arquivos e fragmentos resolvidos |
| Links locais da operação do projeto | **26**, arquivos e fragmentos resolvidos |
| Links locais da operação do Tutor | **4**, arquivos e fragmentos resolvidos |
| Total nos três documentos | **85 links locais, zero ausentes** |
| Links do mapa/relatório | 19 locais, também resolvidos |
| Referências antigas ao README | Busca em docs, openspec, .github e AGENTS; duas em entrega-academica.md, ambas válidas: `funcionalidades-implementadas` e `checkpoint-publicado-e-ci` |
| Migrations atuais | **18 arquivos SQL consecutivos: 000–017**, por leitura dos nomes e do runner |
| E2E atuais | **6 declarações `test(...)` em 6 arquivos**, por leitura; descoberta não executada |
| OpenSpec | **20 itens aprovados, zero falhas**: 19 specs e esta change; `skip_specs: true` aceito |
| Whitespace | `git diff --check`: saída 0, sem erros; avisos sobre futura conversão LF/CRLF em .gitattributes/package.json preexistentes, sem reescrita desses arquivos |

Arquivos E2E inventariados: `catalogo-detalhe.spec.js`, `entrega-academica.spec.js`,
`plano-simulado.spec.js`, `privacidade.spec.js`, `tutor.spec.js` e `usuarios.spec.js`,
todos em `frontend/e2e/`, com uma declaração de teste cada.
Essa leitura não comprova execução, aprovação funcional ou cobertura.

O mapa de transferência acima foi conferido seção a seção. JSON de detalhe e
payload do Tutor foram preservados; links relativos foram recalculados para
`docs/technical/`. A enumeração parcial de Services/Repositories foi substituída
pelo mapa modular, modelagem, SOLID e operações de domínio, sem pretender inventário
completo no README. O contrato da procedure legada e sua ordenação permanecem na
operação do projeto.

### Comandos e contratos conferidos por leitura

| Conteúdo documentado | Fontes conferidas |
| --- | --- |
| Python, bibliotecas e ferramentas opcionais | requirements.txt, requirements-dev.txt, package.json, package-lock.json e conventions |
| Configuração privada e cópia condicional | .env.example, .gitignore, backend/app/config.py e contrato de autenticação; .env privado não lido |
| Schema vazio e migrations status/up/baseline/reconcile | backend/database/migrate.py, migrations, ADR-001, Makefile e operação de autenticação |
| Backend na porta 5000 | backend/run.py |
| Frontend, /login, /cadastro, raiz pública e --port | scripts/serve_frontend.py e operação de autenticação |
| AUTH_SECRET_KEY e CLI criar-administrador | operação de autenticação e código de Contas |
| Unitários, integrações e opt-ins de migrations | run_unit.py, run_integration.py, run_backend_coverage.py, testes de migrations e conventions |
| Scripts npm, Make, E2E e CI | package.json, Makefile, scripts/run_e2e.py, seis specs E2E e .github/workflows/testes.yml |
| Detalhes do catálogo e erros | routes.py, Controllers/Services de Conteúdo, Models, auth_http.py, admin-materias.js e admin-assuntos.js |
| Tutor: entrada, formato e HTTP | Controller, domínio, Services de tutor_ia, permissão pública de Contas e auth_http.py |
| Tutor: tempo, limite e dados | GeminiService, LimiteTutoria e frontend/js/aluno-tutor.js |
| Evidências históricas | relatórios arquivados de consolidação, privacidade/Tutor e registro de checkpoint herdado |

Nenhum comando operacional desses exemplos foi executado; foram realizadas apenas
leituras, scripts estáticos de documentação/integridade e os dois validadores exigidos.

### Evidências e ressalvas preservadas

- **Checkpoint de 07/11/2026:** SHA `6f40f1303560cad908fbdd752fd0aaa4dd285b3b`
  e execução CI `42337772001` preservados com links, data e limite àquela revisão.
  Não se atribui essa aprovação às alterações locais atuais.
- **Histórico herdado:** o README citava 07/10/2026, 106 unitários + 58 integrações,
  95,54%/87,64%, e 48 testes frontend, 98,81%/85,55%. Os valores foram mantidos como
  relato herdado. O relatório vinculado da consolidação registra outra execução,
  em 06/11/2026 (128 + 114 e 143); essa diferença está explícita no novo documento.
- **Tutor de 09/11/2026:** modelo `gemini-3.6-flash`, HTTP 200, quatro partes e
  exercício sem gabarito, 400 inválido e 502 manuais mantidos. A prova real anterior
  é distinta dos testes controlados; timeout continua comprovado somente em unidade.
  Não houve chamada ao Gemini nesta execução.
- **Recorte SQL:** 011–016 continua histórico (55 procedures novas e quatro views,
  além da legada); a preparação atual exige 017 para gestão de Alunos.
- **Entrega acadêmica:** o
  [roteiro oficial](https://github.com/gleisonbt/RoteiroApresentacaoPS2026/blob/main/Roteiro_Apresentacao_Projeto_Rubrica.md)
  foi lido em 10/11/2026. README distingue apresentação de até sete minutos,
  cinco casos com telas e pelo menos quatro ações não CRUD em até dois minutos.
  Demonstração/separação local é admitida e hospedagem é bônus. O relato anterior
  de execução hospedada está identificado como histórico. Não se presume dispensa
  do vídeo de até cinco minutos da atividade anterior, aplicação do cronograma
  de 2025 à turma de 2026 ou aceite/pontuação garantidos.
- **Limites legais:** termos públicos/imprimíveis, aceite de uso, autorização
  opcional do plano e eliminação de derivados preservados. Contato fictício,
  dados sintéticos, proteção de menores e retenção/direitos continuam ressalvados.
  Nenhum HTML legal ou artefato oficial de design foi editado.

## Integridade e escopo final

Comparação com o snapshot inicial: **738 dos 740 arquivos existentes sem alteração
de bytes**. As únicas diferenças em arquivos existentes nesta execução foram
`README.md` e `tasks.md` desta change. Foram criados somente os dois documentos
técnicos aprovados e este `validacao.md`.

As alterações preexistentes de `.gitattributes` e `package.json` mantêm os mesmos
hashes; `.githooks/pre-push` e `scripts/install-git-hooks.mjs` continuam ausentes.
Os **cinco arquivos** da change de ferramentas arquivada permanecem idênticos.
Proposal, design e metadados desta change também permaneceram iguais.
Fontes, configurações públicas, testes, SQL, termos e artefatos oficiais de design
estão incluídos na comparação dos 738 arquivos.

| Arquivo protegido | SHA-256 inicial = final |
| --- | --- |
| `backend/database/create_database.sql` | `07bfe44e26322b36f9b5a96f7ef1a1f9aec194db0f2d97082b50c237a92beb65` |
| `backend/database/migrations/017_gestao_alunos_procedures.sql` | `43ed48939ad2dd00ace1a5420bdd315f33b3ab4035522e6702c845d46be9de15` |
| `frontend/legal/termo-de-uso-v1.html` | `e5bcdf3f002508592ee44a3e4cea2ec6dafcbe172a6e28996c2a105232cd9dd5` |
| `frontend/legal/termo-de-uso-v2.html` | `92b7b57086dabc193308be0af009189bcd4c32d4006a02cc5908cc649d2b71d1` |
| `frontend/legal/termo-de-consentimento-plano-v1.html` | `6233efccc924f73474e3c9b724f05d30729d55ae7fb177f6c47d3282d1d7b233` |

O estado Git final acrescenta somente os dois documentos técnicos ao inventário
de caminhos não rastreados; os artefatos desta change já apareciam como diretório.
HEAD permanece `2a82c77b6978efdf32ecfc11deb25d529e576fc2`.
`output/`, `tmp/` e relatórios locais não foram usados como destino, limpos ou
alterados por esta execução; não fazem parte da comparação de fontes.
Não foram executados testes da aplicação, descoberta E2E, instalação, migrations,
acesso MySQL, Gemini, commit, push, merge ou configuração de hooks.

## Encerramento do workflow

Aplicação: **5/5 tarefas concluídas**. Verificação formal concluída em 10/11/2026,
sem achados críticos.

| Dimensão | Resultado |
| --- | --- |
| Completude | Cinco tarefas cobertas; vinte itens e 26 IDs preservados |
| Correção | 85 links locais válidos; OpenSpec estrito e git diff --check aprovados |
| Coerência | Design e conventions respeitados; 738 arquivos anteriores preservados |

Não há delta specs a sincronizar (`skip_specs: true`). Arquivamento autorizado
pelo usuário, com destino `openspec/changes/archive/2026-11-10-simplificar-readme-do-projeto/`.
Os 19 links do mapa foram ajustados para esse diretório; os artefatos anteriores
de outras changes permanecem preservados. Publicação Git continua dependente
de autorização explícita.

