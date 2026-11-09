# Validação — Tutor de revisão com Gemini

Data: **09/11/2026**, America/Sao_Paulo. Implementação local, specs sincronizadas
e change arquivada. Sem commit, push ou merge. Dados de testes são sintéticos.

## Situação

**18/18 tarefas concluídas.** Implementação, prova real e verificação concluídas. A configuração local foi autorizada pelo
responsável: chave somente no `.env` ignorado pelo Git, Tutor habilitado e API
reiniciada. A presença da chave foi conferida sem exibir seu valor.
Nenhum sucesso controlado de transporte é tratado como evidência do provedor real.

A prova real usou Chromium, API e MySQL descartável, sem interceptação do Gemini.
Houve HTTP 200, quatro partes exibidas e revisão pedagógica transitória do conteúdo.
Dúvida/resposta, chave, cookies e capturas de sessão não são incluídos neste relatório.
Implantação, avaliação jurídica, vídeo e slides continuam fora deste apply.

## Evidências executadas

| Validação | Comando / evidência | Resultado |
| --- | --- | --- |
| Unitários Python | `.venv/Scripts/python.exe backend/tests/run_unit.py` | 194 aprovados, incluindo sanitização de erro interno e cabeçalho de limite |
| Backend agregado | `python backend/tests/run_backend_coverage.py`, com ambos os opt-ins MySQL | 194 unitários + 200 integrações aprovados, sem skips; linhas 97,70% (4590/4698), branches 92,60% (989/1068) |
| Frontend | `npm run test:coverage` | 220 aprovados; linhas 99,30% (1994/2008), branches 88,81% (1445/1627) |
| Servidor público | `python -m unittest scripts.tests.test_serve_frontend -q` | 7 aprovados; GET/HEAD de documentos e leitura sem JS |
| Chromium/MySQL | `scripts.run_e2e.executar_suite`, configuração MySQL resolvida pelo loader existente, `RUN_MYSQL_E2E=1` | 4 aprovados em 51,5 s; Tutor reexecutado após o ajuste final de timeout: 1 aprovado em 5,4 s; schemas removidos |
| Layout isolado | `node tmp/tutor-layout.mjs` | Quatro seções com texto longo a 1440/390 px, sem overflow; somente HTML/CSS, sem API ou sessão |
| Gemini real / Chromium / MySQL descartável | `RUN_GEMINI_REAL_PROOF=1 python tmp/tutor-prova-real.py`, execução separada das suítes comuns | HTTP 200; quatro partes e checklist pedagógico aprovados; HTTP 400 inválido; processos/schema limpos em finally |
| OpenSpec | `openspec validate adicionar-tutor-revisao-com-gemini --strict` | Válido |
| Diff | `git diff --check` | Sem erros de whitespace |

O E2E recebe configuração de banco em memória, sem exibir credenciais. O runner
não lê `.env`, remove `GEMINI_API_KEY`, força Tutor desabilitado e não intercepta
o Gemini. As suítes comuns não fazem chamadas pagas. Capturas de teste sintéticas
ficam em `test-results/`, ignorado pelo Git, sem HAR, trace, vídeo ou storage state.

## Rastreabilidade

| Requisito / decisão | Implementação | Evidência |
| --- | --- | --- |
| Quatro campos e quatro partes | `contracts/tutoria.py`, `tutor_ia/domain/tutoria.py`, `GerarTutoriaService` | Unitários `TutoriaValidacaoTest`; prova real HTTP 200 e conferência pedagógica do conteúdo recebido na interface |
| Validação antes de consumo, limite de corpo local | `TutoriaController`, validação do domínio | Unitários e `TutoriaIntegrationTest.test_contrato_http_autorizacao_antes_do_corpo_e_no_store`, inclusive 400 e 16384/16385 bytes |
| Sessão, Aluno, Origin/CSRF, caminho exato e no-store | `contas/auth_http.py` | HTTP/MySQL: 401/403 antes de corpo inválido/excessivo, 409, 413, 503; rota parecida 404 e Administração preservada |
| Uso vigente, independente do plano; leitura encerrada | `ValidarPermissaoTutoriaService`, API pública de Contas | MySQL: uso ausente/1.0/2.0, plano recusado/aceito/revogado, `in_transaction()==False` e zero conexões emprestadas após retorno |
| Segredo e REST sem histórico | `GeminiService` | `GeminiUnitTest`: payload mínimo, chave só em cabeçalho, `store=false`, sem identidade/histórico/ferramentas, extração de último `model_output`, pensamentos ignorados |
| Falhas, timeouts, limites de resposta e no-retry | `GeminiService`, Controller | Timeout 5/30, rede/HTTP/quota, JSON inválido, incompleto, excessivo, quatro seções inválidas, fechamento e sanitização em unidade; nenhuma simulação em integração |
| Consumo local limitado | `LimiteTutoria` por aplicação | Janela fixa de quatro tentativas/60 s, concorrência mesma conta/duas globais, saturação, expiração, Retry-After e falhas contadas/liberação em finally |
| Sete proprietários, 21 mappers e factories independentes | Composição, gate modular, ADR-010/conventions/mapa | Unitários de arquitetura/composição; sem SQL ou HTTP na factory, sem persistência nova |
| Uso 2.0, documentos imutáveis e escolhas independentes | Novo HTML legal e mapa de versões em Contas | Hashes de documentos, GET/HEAD público, MySQL preservando evidência 1.0, plano e decisão ao novo aceite; recusa/revogação continuam independentes |
| Tela do recorte ALU-TUT-001 | `aluno/tutor.html`, CSS/JS próprios e navegação | Protótipo oficial página 26 consultado; capturas Chromium a 1440/390, foco por Tab e texto longo isolado |
| Estados, segurança textual e ciclo de identidade | `aluno-tutor.js`, `apiRequest`, AuthUI | 37 casos DOM: XSS como texto, catálogo vazio/falho, filtros atrasados, envio único, erro, sucesso anterior associado à pergunta, 45 s incluindo identidade, abort, troca/saída e resultado tardio |
| Preservação da entrega anterior | Sem alteração de migrations, snapshot, procedures ou Models | Suíte MySQL completa, E2E dos vinte casos anteriores, gate dos 21 mappers e conferência de arquivos protegidos |

## Critérios da aula e limites reais

- **400 sem chamada externa:** entrada inválida é rejeitada antes de verificar
  permissão/configuração/reserva ou chamar o gerador; provado em unidade e HTTP real.
- **Timeout:** comprovado em unidade com transporte controlado. Não é uma falha
  observada em chamada real ao Gemini. A espera da interface também é limitada.
- **Camadas:** Route → Controller → caso de uso → GeminiService. Contas usa
  Model/Repository/MySQL e termina sua transação antes da rede; o contrato externo
  não recebe identidade ou desempenho.
- **Sem CRUD adicional:** não há Model, Repository artificial, tabela, migration,
  histórico, conversa, escrita no plano ou persistência de dúvidas/respostas.
- **Limitações:** IA pode errar e a instrução não garante semanticamente ausência
  de gabarito. `store=false` não garante retenção operacional zero. Limites são por
  processo; reinício zera contadores. Abort local não garante cancelamento externo.

## Prova real — tarefa 5.1

| Campo permitido | Registro |
| --- | --- |
| Data | 09/11/2026, America/Sao_Paulo |
| Modelo | `gemini-3.6-flash`; listado na consulta real autenticada de modelos |
| Status da chamada real pela interface | HTTP 200 |
| Quatro partes com conteúdo | Aprovado: explicação, exemplo, compreensão e exercício |
| Pertinência ao ENEM | Aprovado na conferência do conteúdo: conceitos, unidades e analogia de revisão compatíveis com ensino médio |
| Exercício sem gabarito | Aprovado na conferência: enunciado e alternativas sem marcar opção correta nem apresentar resolução |
| Envios independentes e nenhuma ação no plano | Aprovado: somente os quatro campos de estudo, plano não utilizado e sem escrita de conversa |
| Entrada inválida | HTTP 400 `dados_invalidos`, antes de qualquer geração |
| Limpeza | Navegador/processos e MySQL descartável encerrados/removidos; sem conta ou conteúdo de prova no banco operacional |

Cadastro, aceite 2.0, login, seleção do catálogo e envio ocorreram na interface
real, sem resposta externa fabricada. O browser de prova não recebeu a chave;
somente o processo backend a recebeu. Conteúdo foi conferido transitoriamente,
sem salvar payloads em arquivos, HAR, trace ou capturas autenticadas.

Execuções manuais também observaram HTTP 502 `tutor_provedor_indisponivel` e
`tutor_resposta_invalida`, além dos sucessos HTTP 200. A causa da primeira falha
não foi inferida. A aplicação manteve erros seguros, sem resposta fictícia nem
retry automático. Novas execuções foram iniciadas explicitamente na validação.
O timeout continua comprovado em unidade; não se afirma timeout real observado.
O resultado desta prova não garante qualidade semântica nem disponibilidade
contínua de respostas futuras.

## Fontes técnicas

O design preserva o contrato aprovado de Interactions. A consulta às fontes nesta
sessão confirmou etapas `model_output` e o significado limitado de `store=false`
na [documentação oficial indexada](https://ai.google.dev/gemini-api/docs/interactions-overview?authuser=108).
Algumas URLs oficiais redirecionaram para AI Studio e não puderam ser abertas;
isso não foi tratado como prova de disponibilidade do modelo na conta.
`requests==2.34.2` foi confirmado no índice PyPI e no
[histórico oficial](https://github.com/psf/requests/blob/main/HISTORY.md), compatível
com Python >=3.10. Os [timeouts Requests](https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts)
são de conexão/leitura, não um prazo global de geração.


## Integridade e revisão estática

Comparação byte a byte contra `HEAD` confirmou os dois documentos 1.0 e os quatro
binários oficiais intactos. Hashes históricos legais preservados:

- Uso 1.0: `e5bcdf3f002508592ee44a3e4cea2ec6dafcbe172a6e28996c2a105232cd9dd5`.
- Plano 1.0: `6233efccc924f73474e3c9b724f05d30729d55ae7fb177f6c47d3282d1d7b233`.

`backend/database/` não tem diff: migrations 000–016, snapshot e referência SQL
permanecem. Os três arquivos dos 29 testes originais de Matéria/Assunto/Questão
não foram alterados. Gate modular confirma sete proprietários e 21 mappers.
Verificação de 73 arquivos textuais alterados/novos não encontrou assinatura de
segredo nem caractere de substituição UTF-8; destinos locais dos links Markdown
modificados existem. Após autorização explícita do responsável, somente a configuração local do Tutor
foi atualizada no `.env`; o arquivo permanece ignorado e seu conteúdo não foi exibido.

## Verificação OpenSpec

| Dimensão | Resultado |
| --- | --- |
| Completude | 18/18 tarefas; implementação, regressões, prova real, documentação e revisão final concluídas |
| Correção | Unidade, DOM e MySQL aprovados; E2E comum separado do Gemini; envio real HTTP 200 e conferência pedagógica, sem substituir provedor por mocks |
| Coerência | Design, ADR-010, sete módulos, 21 mappers, documentos imutáveis, sem SQL/persistência nova ou controles de funções futuras |

Nenhuma divergência crítica de implementação ou requisito pendente foi identificada.
Limites já declarados permanecem: IA falível, recusa de formato, falhas externas,
controle por processo, retenção operacional do provedor e possível consumo após abort.
A verificação final confirma rastreabilidade, integridade, UTF-8, links e ausência
da chave em arquivos versionáveis. Sync/archive concluídos conforme o registro de fechamento abaixo.

Fechamento local: gates backend/frontend aprovados (mínimos 90% de linhas e
85% de branches), regressão completa sem skips, vinte casos E2E preservados,
29 integrações originais e 21 mappers mantidos. Nenhuma operação de
commit/push/merge foi realizada.

## Configuração local e checagens operacionais — 09/11/2026

`python backend/database/migrate.py status` confirmou migrations 000–016 já
aplicadas no banco configurado. A preparação não aplicou migration nem criou
conta/conteúdo de prova no banco operacional. As escritas da prova ocorreram
somente em schemas descartáveis com prefixo validado.

A configuração efetiva confirma `tutor_habilitado=True` e `chave_configurada=True`.
API e frontend estão em segundo plano em `127.0.0.1:5000` e `127.0.0.1:5500`,
com debug desabilitado. Checagens reais:

- `/api/health`: 200.
- `/api/termos`: 200, uso 2.0 e plano 1.0.
- `/aluno/tutor.html`: 200.
- `POST /api/tutoria` sem sessão: 401 e `Cache-Control: no-store`.

Os 194 unitários Python foram reexecutados após configurar a chave real e
passaram; o runner mantém `PYTHON_DOTENV_DISABLED=1`, Tutor desabilitado e
credencial externa vazia, sem enviar a chave da aplicação para testes comuns.
A chave não é reproduzida neste documento nem nos exemplos do README.


## Resultado final

Verificação final concluída: 73 arquivos textuais conferidos, sem a credencial em
arquivos versionáveis, links locais existentes, UTF-8 válido e `git diff --check`
sem erros. Documentos legais históricos e quatro binários preservados byte a byte;
hashes dos três documentos legais conferidos. SQL e migrations sem diff.
`openspec validate adicionar-tutor-revisao-com-gemini --strict` aprovado.
Sem achados críticos pendentes: **specs sincronizadas e change arquivada**.
Progresso **18/18**; nenhum commit, push ou merge realizado.


## Sincronização e arquivamento — 09/11/2026

Autorizados pelo responsável nesta sessão, com todas as 18 tasks concluídas e
sem achados críticos pendentes.

- `termos-e-consentimento`: um requisito modificado e dois adicionados; Purpose
  e demais requisitos/cenários anteriores preservados.
- `tutoria-revisao-ia`: spec principal criada com Purpose do delta e oito requisitos.
- Comparação completa dos deltas com as duas specs principais: sem diferença
  restante a aplicar; nenhum cabeçalho de operação delta nas specs principais.
- `openspec validate --specs --strict`: 17 aprovadas, zero falhas.
- `openspec validate adicionar-tutor-revisao-com-gemini --strict`: aprovado antes do archive.
- `openspec archive adicionar-tutor-revisao-com-gemini --skip-specs --yes --json`:
  aprovado. `--skip-specs` evitou repetir o merge já realizado e conferido.
- Destino: `openspec/changes/archive/2026-11-09-adicionar-tutor-revisao-com-gemini/`.
- Links do README e da arquitetura atualizados para o arquivo; `.openspec.yaml`
  preservado. Código, SQL, configuração local e credenciais não foram alterados
  nesta operação de sync/archive. Sem commit/push/merge.
