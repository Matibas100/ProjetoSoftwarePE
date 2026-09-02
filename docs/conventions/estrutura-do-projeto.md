# Estrutura do projeto

## Regra central

A Plataforma ENEM é um projeto existente. Não recrie sua estrutura nem trate o repositório como aplicação nova.

```text
frontend/                  HTML, CSS e JavaScript
backend/
  app/
    controllers/           adaptação HTTP
    services/              casos de uso
    models/                entidades e CRUD Active Record
    repositories/          consultas especializadas e procedures
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
python -m http.server 5500 --directory frontend
```

Não instale dependências nem execute comandos que escrevam no banco sem que o escopo aprovado exija isso.
