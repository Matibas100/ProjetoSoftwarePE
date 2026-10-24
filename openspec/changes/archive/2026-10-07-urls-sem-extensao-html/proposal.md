# Proposta: URLs de autenticação sem extensão HTML

## Motivação

Hoje o acesso às telas exige `/login.html` e `/cadastro.html`, pois o frontend usa o servidor estático padrão do Python. O objetivo é permitir os endereços mais simples `/login` e `/cadastro`, mantendo os formulários e fluxos de autenticação já validados.

## O que muda

- Disponibilizar `/login` e `/cadastro` como URLs canônicas das telas PUB-AUT-001 e PUB-AUT-002, inclusive para entrada direta e recarga.
- Redirecionar os endereços antigos com `.html` e as variantes `/login/` e `/cadastro/` para as respectivas URLs canônicas, preservando a query string.
- Atualizar links entre formulários e retornos ao login após cadastro, logout ou acesso anônimo a página protegida.
- Adicionar um servidor local do frontend com mapeamento explícito dessas duas páginas, mantendo a porta 5500 e a API Flask separada na porta 5000.
- Documentar o novo comando de execução e verificar navegação, recursos estáticos e compatibilidade dos fluxos existentes.

### Fora de escopo

Remover `.html` das páginas administrativas, do início de Aluno ou do MVP; mudar o destino da raiz `/`; migrar para SPA ou framework; unificar frontend e API; implantar hosting; alterar layout, contratos `/api`, autenticação, banco ou migrations.

## Capacidades

### Novas capacidades

Nenhuma. O comportamento fica na capacidade de autenticação existente.

### Capacidades modificadas

- `autenticacao-escolar`: URLs públicas canônicas de login/cadastro, compatibilidade dos endereços antigos e navegação de retorno ao login. As regras de credenciais, perfis e sessão permanecem vigentes.

## Impactos

- Superfícies prováveis: novo `scripts/serve_frontend.py`, `frontend/login.html`, `frontend/cadastro.html`, `frontend/js/auth-page.js`, `frontend/js/auth-session.js` e testes de navegação/servidor.
- Documentação operacional: `README.md`, comandos atuais de `docs/conventions/estrutura-do-projeto.md` e `docs/technical/operacao-autenticacao-escolar.md`. Artefatos arquivados são históricos e não serão reescritos.
- Dependências: biblioteca padrão do Python já exigido pelo projeto; nenhuma dependência nova de produção. O servidor de páginas não carrega `.env`, Flask ou configuração MySQL.
- Compatibilidade com o MVP: páginas administrativas, recursos estáticos, destinos dos perfis e contratos da API permanecem iguais. Links antigos continuam utilizáveis por redirecionamento.
- Operação: `python -m http.server 5500 --directory frontend` será substituído pelo comando do servidor local para suportar URLs sem extensão; o comando antigo, isoladamente, não oferece `/login` e `/cadastro`.
- Arquitetura e segurança: preserva frontend separado e `Route -> Controller -> Service -> Model/Repository -> MySQL`. Mantém host/origens, cookie, CSRF e autorização do ADR-002; nenhuma transação, Stored Procedure ou migration é necessária. Os binários visuais oficiais permanecem congelados.
