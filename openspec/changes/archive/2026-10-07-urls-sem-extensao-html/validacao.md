# Validação: URLs sem extensão HTML

Data: 7 de outubro de 2026. Ambiente: Windows, Python, Chrome, API Flask e MySQL real.

## Testes automatizados

| Comando | Resultado |
| --- | --- |
| `python -m unittest discover -s scripts/tests -p 'test_serve_frontend.py'` | 7 testes aprovados, com múltiplos casos GET/HEAD por teste |
| `npm run test:unit` | 54 testes aprovados em 8 arquivos |
| `npm run test:coverage` | 54 testes aprovados; 98,81% de linhas (915/926), 86,49% de branches (365/422) |
| `git diff --check` | Sem erros de whitespace |
| `openspec validate urls-sem-extensao-html --strict` | Change válida |

Os gates de 90% de linhas e 85% de branches foram atendidos. Todos os arquivos
JavaScript executáveis possuem cobertura. O servidor Python foi exercitado por
HTTP real, em loopback e porta temporária, sem API, configuração ou banco.

Cobertura HTTP: entrada direta, recarga, query, aliases 302 com destino local
fixo, HEAD sem corpo, conteúdo exato das páginas, links canônicos, scripts,
estilos, logo e fontes; páginas legadas e raiz; 404 sem fallback para caminhos
inexistentes, `/api/auth/login`, traversal e symlink/junction externo.
O processo CLI também entregou `/login` iniciado de outro diretório.

## Navegador com API e MySQL reais

Foi iniciado o comando documentado `python scripts/serve_frontend.py`, na porta
5500. A API usou a infraestrutura existente de testes, com schema MySQL
descartável de nome validado e contas sintéticas. Migrations existentes foram
aplicadas exclusivamente na fixture; o banco da aplicação não foi modificado.
A fixture foi encerrada e confirmou a remoção do schema ao final.

| Verificação | Evidência observada |
| --- | --- |
| Entrada direta e recarga | `/login` e `/cadastro` mantiveram a URL canônica e renderizaram o formulário correto |
| Alternância | Criar uma conta abriu `/cadastro`; Entrar abriu `/login` |
| Compatibilidade | Os quatro aliases terminaram nas URLs canônicas, preservando `origem=local` |
| Destino externo | `next=https://example.com` permaneceu como query de `/login`, sem navegação externa |
| Cadastro de Aluno | POST de cadastro retornou 201; navegação para `/login`, mensagem de sucesso, e-mail preenchido e senha vazia; storage de transferência removido |
| Login de Aluno | POST retornou 200; destino `/aluno/inicio.html`, saudação da conta sintética e conteúdo visível |
| Sessão válida em página pública | Aluno voltou ao seu início ao abrir `/login`; Administrador voltou à gestão ao abrir `/cadastro` |
| Logout | POST retornou 204; retorno a `/login`; novo acesso à página protegida exigiu login |
| Falha de rede no logout | Em modo Offline, erro visível e permanência no início de Aluno; após restabelecer rede, logout confirmado |
| Login de Administrador | POST retornou 200; destino `/admin/materias.html`, identidade correta e consultas administrativas 200 |
| Sessão expirada | Sessões expiradas somente na fixture; recarga protegida recebeu 401 e retornou a `/login` |
| Recursos das duas telas | CSS, três scripts, logo e duas fontes com 200; nenhum recurso declarado retornou 404 |

## Composição e teclado

As duas telas foram inspecionadas visualmente em Chrome com viewport real
emulado de 1440×1000 e 390×844. A largura foi confirmada por `innerWidth`.
Em todas as combinações, `document.documentElement.scrollWidth > innerWidth`
foi falso. A composição desktop e a adaptação mobile existentes foram mantidas.
Tab alcançou o primeiro campo e mostrou contorno violeta visível. Enter enviou
os formulários de cadastro/login; labels, botões de senha e links permaneceram
acessíveis. As capturas foram inspecionadas na sessão, sem alterar os binários
oficiais, o CSS ou a identidade visual.

## Limitações e execução

- O sandbox Windows impediu subprocessos do Vitest e acesso a diretórios
  temporários Python; os comandos foram repetidos fora do sandbox e passaram.
- O navegador solicitou `/favicon.ico` inexistente, comportamento preexistente;
  isso não afetou os recursos declarados das telas. Não foi criado novo asset.
- A ferramenta de navegador não permitiu salvar capturas no workspace; elas
  foram retornadas e inspecionadas diretamente na sessão.
- A suíte de backend e as integrações destrutivas de migrations não foram
  repetidas: a implementação não altera backend, contrato, schema ou migrations.
- Trata-se do servidor local de desenvolvimento previsto no design; hosting
  e infraestrutura de produção permanecem fora do escopo.

## Correspondência com o delta

| Requisito | Implementação e validação |
| --- | --- |
| URLs canônicas das páginas públicas de autenticação | `scripts/serve_frontend.py` e os 7 testes HTTP; navegador validou entrada/recarga, aliases e recursos |
| Cadastro público exclusivo de Aluno | Apenas o retorno em `auth-page.js` e o link da página foram atualizados; testes DOM e cadastro real confirmaram `/login` e pré-preenchimento |
| Login por credenciais com rotação de sessão | URL pública e link atualizados; contrato e lógica da API preservados; ambos os perfis autenticaram na API real |
| Navegação autenticada e telas utilizáveis | `auth-session.js` usa `/login` no bootstrap inválido e logout; testes DOM, sessão expirada real, falha de rede, teclado e viewports confirmados |

A revisão do diff confirmou mudanças restritas ao servidor, testes, URLs de
recursos/links, destinos de retorno e documentação. Nenhum arquivo de backend,
spec principal, migration, regra de sessão/perfil ou binário visual oficial foi
alterado. Sincronização e arquivamento são as próximas etapas do workflow.

## Verificação OpenSpec

Revisão feita com `openspec-verify-change`, após consulta de status, instruções
apply, artefatos, conventions, ADR-002 e diff completo, incluindo os arquivos novos.

| Dimensão | Resultado |
| --- | --- |
| Completude | As 11 tarefas foram executadas; os quatro requisitos estão representados acima |
| Correção | Testes HTTP/DOM, cobertura e cenários reais de navegador aprovados |
| Coerência | Mapeamento explícito, raiz fixa, API separada, destinos dos perfis e composição preservados conforme design |

Nenhum achado crítico ou pendência de implementação. As limitações operacionais
estão registradas acima e não impedem sincronizar/arquivar esta change.
