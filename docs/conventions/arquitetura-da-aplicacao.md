# Arquitetura da aplicação

## Fluxo obrigatório

```text
Frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL
```

## Responsabilidades

- Routes apenas mapeiam URLs e Controllers.
- Controllers são classes, interpretam HTTP e retornam resposta; não contêm regra de negócio, SQL ou `db.session`.
- Cada caso de uso possui Service próprio. Services validam e coordenam sem SQL ou `db.session`.
- Os helpers `inteiro_filtro` e `envelope_paginado` ficam em [`backend/app/core/paginacao.py`](../../backend/app/core/paginacao.py); cada Service continua responsável pelas validações específicas e pela coordenação do seu caso de uso.
- Models herdam de `db.Model` por um único caminho e mantêm as capacidades Active Record adequadas: `ModeloBase`, `ModeloAtualizavel` ou `CrudMixin`, conforme o [ADR-008](../technical/adr/ADR-008-contratos-e-capacidades-de-persistencia.md).
- Repositories existem apenas para consultas especializadas, JOINs, relatórios, rankings e Stored Procedures.
- Todo `CALL` fica exclusivamente no Repository.
- `db` permanece compartilhado por `backend/app/extensions.py` e a aplicação usa application factory.

## Fronteiras modulares

- Cada caso de uso pertence a um dos seis módulos do [mapa modular](../technical/organizacao-modular.md).
- Módulos externos usam somente `api.py` com `__all__` explícito ou contratos públicos; não importam Models/Repositories/Services privados.
- APIs não exportam ORM nem Repository completo. Projeções de leitura delimitadas são agregadas somente em Repository.
- Composição e registro ORM são as exceções estritas para importar implementações proprietárias; Services não resolvem composição.
- As bases canônicas ficam em `app.core.persistencia`; `app.models.crud_mixin` reexporta as mesmas classes e `db`.
- Núcleo/contratos não dependem de negócio. SQLAlchemy de exceções pode ser usado para tratar falhas, sem executar SQL nos Services.
- Blueprint de cada módulo preserva URLs; `/api` é aplicado uma vez. Hooks de Contas e CLI são registrados uma vez pela factory.
- Eliminação do plano é participante injetado nas negativas de Contas, com uma única transação, conforme [ADR-010](../technical/adr/ADR-010-organizacao-modular-do-backend.md).

## Compatibilidade

- Preserve contratos atuais até que uma change aprove explicitamente sua evolução.
- Mudança de schema exige decisão e migration versionada compatível com o ADR-001.
- Respeite os ADRs aceitos sobre autenticação, catálogo, unicidade, versionamento, transações e mídias.
- Não refatore o MVP inteiro para antecipar a arquitetura definitiva.
