# Desenho técnico: URLs de autenticação sem extensão HTML

## Contexto

Veja a [proposta](proposal.md) para motivação e escopo. O frontend é multipágina, sem framework, servido hoje por `python -m http.server 5500 --directory frontend`. Login e cadastro são arquivos na raiz pública, com recursos relativos, links com `.html` e navegação para `/login.html` nos scripts de autenticação. O tipo de formulário é identificado por `data-kind`, não pela URL.

A API Flask permanece em `127.0.0.1:5000`. O [ADR-002](../../../docs/technical/adr/ADR-002-estrategia-de-autenticacao.md) e a [operação de autenticação](../../../docs/technical/operacao-autenticacao-escolar.md) exigem origem explícita, CSRF e cookie de sessão no servidor. A mudança atravessa entrega de páginas, links, scripts e operação; este design resolve o mapeamento HTTP antes da implementação.

## Objetivos e limites técnicos

- Reaproveitar os HTML existentes como fonte única das telas, sem copiar formulários para novos diretórios.
- Resolver rotas públicas no servidor do frontend, sem inserir entrega de HTML nas camadas de negócio da API.
- Manter `127.0.0.1:5500` como origem padrão e os destinos autenticados atuais. A mudança não cria navegação de SPA nem suporte de produção.
- Tratar somente os caminhos explicitamente descritos no [delta](specs/autenticacao-escolar/spec.md); não inferir uma rota para cada arquivo HTML.

## Decisões

### 1. Servidor local pequeno com biblioteca padrão do Python

Criar `scripts/serve_frontend.py` com `ThreadingHTTPServer` e um handler derivado de `SimpleHTTPRequestHandler`. O comando será `python scripts/serve_frontend.py`, a partir da raiz do projeto, com bind padrão e fixo em `127.0.0.1` e porta padrão 5500. Oferecer `--port` para uso local com porta diferente, documentando que outra origem precisa estar autorizada na API.

A raiz pública será calculada a partir da localização do script e fixada em `frontend`, independentemente do diretório de trabalho. Não carregar `.env`, iniciar Flask, conectar ao MySQL ou disponibilizar seleção arbitrária de diretório público. Resolver o arquivo final sob essa raiz e impedir entrega de arquivos externos, inclusive por symlinks/junctions que escapem dela.

Alternativas consideradas: servir tudo pelo Flask muda origem e responsabilidades sem necessidade; instalar bundler/proxy adiciona dependência para duas rotas; mover páginas para `login/index.html` e `cadastro/index.html` impõe barra final e ajustes de recursos. O handler local conserva os arquivos e a topologia atual com menor impacto.

### 2. Mapeamento explícito antes da entrega estática

Separar pathname e query string. Compartilhar a resolução entre GET e HEAD para evitar respostas divergentes.

| Caminho solicitado | Resposta |
| --- | --- |
| `/login` | 200, arquivo `frontend/login.html`, sem redirect |
| `/cadastro` | 200, arquivo `frontend/cadastro.html`, sem redirect |
| `/login.html`, `/login/` | 302, Location `/login` |
| `/cadastro.html`, `/cadastro/` | 302, Location `/cadastro` |
| Arquivo público existente | Entrega estática usual, preservando o MIME type |
| Caminho inexistente, incluindo `/api/auth/login` | 404, sem fallback de página |

Acrescentar a query string original ao Location apenas quando existir. Destino sempre escolhido da tabela fixa, nunca de `next`, `redirect` ou parâmetro semelhante. Emitir redirecionamento com `Content-Length: 0` e sem corpo; HEAD de páginas também não envia corpo. Usar 302 para evitar cache permanente de uma decisão local reversível. Não adicionar redirecionamento da raiz `/`, que continua entregando `index.html`.

Alternativa rejeitada: remover `.html` apenas no JavaScript com History API não resolve entrada direta nem recarga. Fallback universal para HTML mascara 404 e falhas de recursos.

### 3. Navegação canônica e recursos a partir da raiz pública

Em `login.html` e `cadastro.html`, usar links `/cadastro` e `/login`. Tornar os recursos dessas duas páginas relativos à raiz (`/css/auth.css`, `/assets/...`, `/js/...`) para evitar dependência da grafia da URL de entrada. Os recursos internos do CSS mantêm sua resolução em relação ao arquivo CSS.

Em `auth-page.js`, o cadastro concluído retorna diretamente a `/login`. Em `auth-session.js`, atualizar o bootstrap de página protegida sem sessão válida e o logout confirmado para `/login`. Preservar mensagens, pré-preenchimento de e-mail, validação, prevenção de envio duplicado e tratamento de falha de rede. Login e sessão válida continuam usando os destinos fixos de Aluno e Administrador; o diálogo de recuperação de sessão continua funcionando no contexto existente.

Alternativa: depender sempre do alias `/login.html` preservaria funcionalidade, mas deixaria links novos usando o endereço que o usuário quer simplificar e acrescentaria um redirect a cada retorno.

### 4. API, dados e fronteiras de segurança

Fluxo de entrega: navegador -> servidor estático local -> HTML/CSS/JavaScript. Fluxo de negócio permanece frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL. O servidor de páginas não é proxy da API e não toma decisões de autenticação.

Nenhum Controller, Service, Repository, contrato `/api`, transação, Stored Procedure, migration ou schema será alterado. Cookies permanecem Path `/api`, HttpOnly e SameSite=Lax, com CSRF e `credentials: include`. Os exemplos usam `127.0.0.1` tanto no frontend quanto na API, sem misturar `localhost`. Senhas e tokens continuam fora dos endereços e do armazenamento JavaScript. Os quatro binários oficiais do Desktop V1 permanecem congelados.

### 5. Validação proporcional

- Testar o servidor por HTTP real em loopback e porta temporária, sem Flask ou MySQL: páginas canônicas, aliases, GET/HEAD, query, recursos, 404 e contenção da raiz pública. Colocar os testes Python em `scripts/tests/test_serve_frontend.py`, executáveis com `python -m unittest discover -s scripts/tests -p 'test_serve_frontend.py'`.
- Atualizar `frontend/tests/auth.test.js` para exigir `/login` nos retornos existentes e verificar links e recursos dos dois HTML, preservando as demais asserções e cenários.
- Executar `npm run test:unit` e `npm run test:coverage`, mantendo os gates existentes. A lógica nova do servidor deve ser exercitada pelos testes HTTP; a suíte de backend não substitui esses testes.
- No navegador real com API e MySQL configurados, verificar entrada direta/recarga, cadastro, login dos dois perfis, logout, sessão inválida e uso dos aliases; conferir recursos sem 404 e composição a 1440/390 px. Não usar mocks ou SQLite em integrações existentes. Como a API não muda, não é necessário repetir integrações destrutivas de migrations para esta change.

## Riscos e escolhas

- Comando antigo não entende URLs sem extensão -> atualizar README, documentação operacional e comandos atuais da convention; não reescrever artefatos arquivados.
- Recursos relativos podem quebrar em URLs alternativas -> URLs de recursos a partir da raiz nas duas páginas e teste de recarga após redirect.
- Redirecionamento acidental em ciclo ou para destino externo -> tabela fixa e testes HTTP sem seguir redirect automaticamente.
- Bind ou raiz pública incorretos podem expor arquivos do projeto -> bind local, raiz calculada por `__file__` e verificação do caminho resolvido.
- Origem diferente impede cookie/CORS -> manter porta/host padrão e documentar a configuração necessária somente para porta alternativa.
- O servidor local não é infraestrutura de produção -> hosting e servidor de produção ficam fora desta change; eventual implantação deve reproduzir o contrato de rotas em change própria.

## Plano de adoção e reversão

1. Implementar e validar servidor, links, navegação e documentação como uma entrega coerente.
2. Encerrar o servidor estático antigo e iniciar `python scripts/serve_frontend.py`; manter o backend no comando atual.
3. Abrir `http://127.0.0.1:5500/login` e validar os dois perfis. Links antigos serão encaminhados para o endereço canônico.
4. Em reversão, restaurar conjuntamente links/scripts/documentação ao comportamento anterior e retomar `python -m http.server 5500 --directory frontend`. Não há alteração de dados a desfazer.
