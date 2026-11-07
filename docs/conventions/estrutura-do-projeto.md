# Estrutura do projeto

## Regra central

A Plataforma ENEM é um projeto existente. Não recrie sua estrutura nem trate o repositório como aplicação nova.

```text
frontend/                  HTML, CSS e JavaScript
backend/
  app/
    modules/               seis proprietários com rotas e camadas próprias
      contas/              identidade, sessões e privacidade
      conteudo/            catálogo e Questões versionadas
      praticas/            catálogo do Aluno e tentativas
      simulados/           composição e execução
      desempenho/          projeções, diagnóstico e dashboards
      plano_estudos/       gerações e itens do plano
    core/                  bases e helpers neutros; health
    contracts/             Protocols e DTOs públicos sem ORM
    models/                registro explícito e compatibilidade estática
    composition.py         ligações por aplicação
    routes.py              agregador dos Blueprints e health
  database/                bootstrap e migrations SQL
  tests/                   testes unitários e integração com MySQL real
docs/
  design/desktop-v1/       fonte visual oficial e congelada
  technical/               arquitetura, ADRs e planejamento
openspec/                  specs e changes futuras
```

## Fontes de verdade

- O código atual define o comportamento implementado.
- `docs/technical/adr/` contém decisões arquiteturais aprovadas.
- `docs/design/desktop-v1/` contém a referência visual oficial; a Errata prevalece somente no ponto que corrige.
- `backend/database/create_database.sql` é o bootstrap consolidado atual.
- Changes OpenSpec documentam evoluções futuras, sem substituir silenciosamente essas fontes.

## Comandos atuais

```powershell
python -m pip install -r backend\requirements.txt
python backend\run.py
python scripts/serve_frontend.py
```

Abra `http://127.0.0.1:5500/login`. Para usar outra porta, execute
`python scripts/serve_frontend.py --port 5501` e autorize
`http://127.0.0.1:5501` em `CORS_ORIGINS` na configuração local da API.
O servidor fixa a raiz pública em `frontend`, mesmo iniciado de outro diretório.

Não instale dependências nem execute comandos que escrevam no banco sem que o escopo aprovado exija isso.
