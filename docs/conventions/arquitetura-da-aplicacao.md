# Arquitetura da aplicação

## Fluxo obrigatório

```text
Frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL
```

## Responsabilidades

- Routes apenas mapeiam URLs e Controllers.
- Controllers são classes, interpretam HTTP e retornam resposta; não contêm regra de negócio, SQL ou `db.session`.
- Cada caso de uso possui Service próprio. Services validam e coordenam sem SQL ou `db.session`.
- Models herdam de `db.Model` por um único caminho e mantêm as capacidades Active Record adequadas: `ModeloBase`, `ModeloAtualizavel` ou `CrudMixin`, conforme o [ADR-008](../technical/adr/ADR-008-contratos-e-capacidades-de-persistencia.md).
- Repositories existem apenas para consultas especializadas, JOINs, relatórios, rankings e Stored Procedures.
- Todo `CALL` fica exclusivamente no Repository.
- `db` permanece compartilhado por `backend/app/extensions.py` e a aplicação usa application factory.

## Compatibilidade

- Preserve contratos atuais até que uma change aprove explicitamente sua evolução.
- Mudança de schema exige decisão e migration versionada compatível com o ADR-001.
- Respeite os ADRs aceitos sobre autenticação, catálogo, unicidade, versionamento, transações e mídias.
- Não refatore o MVP inteiro para antecipar a arquitetura definitiva.
