# Tarefas: URLs de autenticação sem extensão HTML

## 1. Entrega local das páginas e compatibilidade de URLs

- [x] 1.1 Criar `scripts/serve_frontend.py` conforme o design, com bind em `127.0.0.1`, porta padrão 5500, opção `--port` e raiz pública fixa em `frontend`, sem carregar `.env`, Flask ou MySQL; verificar inicialização pelo comando documentado e entrega da mesma página ao executar o script de outro diretório.
- [x] 1.2 Implementar GET/HEAD de `/login` e `/cadastro`, redirects 302 dos aliases com preservação de query, entrega dos recursos existentes e 404 sem fallback; verificar por testes HTTP reais que cada rota retorna status, Content-Type, Location e corpo corretos, sem ciclos ou destino externo.
- [x] 1.3 Adicionar `scripts/tests/test_serve_frontend.py` com servidor em loopback/porta temporária e encerramento garantido, cobrindo entrada direta, aliases, HEAD sem corpo, query, recursos, páginas legadas, raiz `/`, caminhos inexistentes, `/api/auth/login` e tentativas de acesso fora da raiz pública; verificar com `python -m unittest discover -s scripts/tests -p 'test_serve_frontend.py'`, sem ler segredos ou alterar dados.
- [x] 1.4 Atualizar o comando de execução e endereço inicial no `README.md` e os comandos atuais em `docs/conventions/estrutura-do-projeto.md`, incluindo a necessidade de autorizar outra origem ao usar porta alternativa; verificar que o comando escrito inicia o servidor e que `http://127.0.0.1:5500/login` carrega diretamente.

## 2. Links públicos e retorno ao login

- [x] 2.1 Atualizar `frontend/login.html` e `frontend/cadastro.html` para links `/cadastro` e `/login` e recursos a partir da raiz pública, preservando composição, campos e acessibilidade; verificar links, scripts, estilos, logo e fontes nos testes HTML/HTTP, sem 404 nas URLs canônicas.
- [x] 2.2 Atualizar o retorno após cadastro em `frontend/js/auth-page.js` e o bootstrap sem sessão/logout confirmado em `frontend/js/auth-session.js` para `/login`, mantendo destinos dos perfis e recuperação no contexto; verificar em `frontend/tests/auth.test.js` cadastro com e-mail pré-preenchido, acesso anônimo protegido, logout e falha de rede, preservando as demais asserções de autenticação.
- [x] 2.3 Atualizar `docs/technical/operacao-autenticacao-escolar.md` com o comando local, URLs canônicas e redirects de compatibilidade; verificar coerência com README, design e delta, mantendo instruções de cookie/origem/CSRF e sem reescrever arquivos arquivados.

## 3. Validação integrada e evidências

- [x] 3.1 Executar os testes HTTP do servidor e `npm run test:coverage` para validar conjuntamente recursos, navegação e regressão do frontend; verificar sucesso dos testes e gates de 90% de linhas/85% de branches, registrando comandos, resultados e limitações em `validacao.md` desta change.
- [x] 3.2 Validar em navegador real, com API e MySQL configurados, entrada direta/recarga de `/login` e `/cadastro`, redirects antigos, cadastro/login de Aluno, login de Administrador, logout e retorno ao login por sessão inválida; verificar destinos atuais dos perfis e recursos sem 404, registrando evidências sem senhas, tokens ou dados pessoais reais.
- [x] 3.3 Conferir em navegador a 1440/390 px composição, teclado, foco e ausência de rolagem horizontal nas duas telas; verificar preservação dos comportamentos visuais existentes e registrar resultado em `validacao.md`, sem alterar binários oficiais.
- [x] 3.4 Revisar o diff e a correspondência com os quatro requisitos do delta, garantindo ausência de alterações em contratos `/api`, schema, migrations, regras de sessão/perfil ou artefatos visuais congelados; verificar com a skill `openspec-verify-change` e `openspec validate urls-sem-extensao-html --strict`, registrando pendências antes da sincronização e do arquivamento.
