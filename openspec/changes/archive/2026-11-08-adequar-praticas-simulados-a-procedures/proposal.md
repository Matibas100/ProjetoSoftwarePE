# Proposta — Práticas e Simulados por procedures

## Why

Históricos, composição, retomada e consultas de propriedade ainda executam filtros e JOINs em ORM. A mudança deve trocar o mecanismo de persistência especializada preservando correção, revisão e idempotência. O objetivo é cumprir a exigência de acesso além do CRUD por procedures encapsuladas no Repository, mantendo o sistema demonstrável e compreensível.

## What Changes

- Converter o recorte fechado: Histórico/fatos/propriedade/replay de Práticas; catálogo administrativo e do Aluno, composição individual/em lote, andamento, respostas, histórico, fatos e locks de Simulados.
- Criar 16 procedures específicas, descritas em [inventário](inventario-procedures.md), com SQL estático e parâmetros vinculados; CALL permanece exclusivamente nos Repositories.
- Acrescentar `014_praticas_simulados_procedures.sql`, bootstrap equivalente, reconhecimento conservador do prefixo 014, preflight e testes MySQL reais.
- Preservar DTOs públicos, respostas HTTP, permissões, semântica temporal, locks e uma única transação externa; os métodos que alimentam escrita continuam retornando entidades ORM gerenciadas no proprietário.
- Atualizar documentação de procedures, rotas, Modules/Models/Repositories e cobertura da exigência. Não acrescentar funcionalidades à lista oficial por contar métodos SQL.

### Fora de escopo

CRUD de tentativas/respostas/rascunhos nas Models, cálculo da correção no Service, métricas/contagens/views da primeira change e elegibilidade de Questões já reservada à 013. Sem novas telas, regras de produto, tabelas/colunas/FKs, bibliotecas, uso real de dados pessoais, gravação de vídeo, AWS ou operações Git.

## Capabilities

### New Capabilities

- `praticas-simulados-mysql`: interfaces MySQL específicas do domínio para o recorte inventariado, com compatibilidade, autorização e participação transacional verificáveis.

### Modified Capabilities

- `migrations-sql`: acrescentar comprovação do prefixo 014 e seus objetos SQL, sem enfraquecer os prefixos anteriores.

As specs funcionais existentes continuam válidas. Os novos requisitos descrevem a interface SQL externa e garantias de compatibilidade, sem reabrir decisões de negócio.

## Impact

- **Dependência obrigatória:** aplicar, verificar e sincronizar `adequar-catalogo-editorial-a-procedures` antes desta change. A sequência planejada é primeira etapa 011/012 → Catálogo 013 → Práticas/Simulados 014 → Plano 015 → Contas 016. Não aplicar essas changes simultaneamente; conferir eventual colisão de versão antes de editar.
- **Superfícies:** `praticas/repositories/pratica_repository.py`, `simulados/repositories/{simulado_repository,consultas_simulados}.py` e Services/Controllers desses módulos. Caminhos relativos a `backend/app/modules/`.
- **Entradas mantidas:** Rotas existentes `/api/aluno/praticas`, `/api/admin/simulados`, `/api/aluno/simulados` e `/api/aluno/tentativas-simulado`, incluindo detalhes, respostas, resultado, correção e finalização. Telas e Controllers atuais atendem às mesmas funcionalidades; não criar Controller por procedure auxiliar.
- **Invariantes:** Dono obtido da sessão, 404 uniforme, gabarito só na etapa permitida, versões capturadas, uma tentativa em andamento, revisão e replay, correção/finalização atômicas.
- **Banco:** somente novas routines sobre as 21 Models existentes, sem DML funcional durante instalação/baseline. Procedures especializadas de escrita só executam no caso de uso autorizado, nunca pela migration.
- **ADRs:** preservar 001/002/003/004/005/006/008/009/010 conforme o domínio, complementando o ADR-011 e as interfaces SQL introduzidas pela primeira etapa sem alterar decisões históricas.
- **Testes:** `test_praticas_integration.py`, `test_simulados_integration.py`, testes de migrations correspondentes, `test_desempenho_integration.py` e E2E de Práticas/Simulados. Preservar também as 29 integrações originais, gates de arquitetura, cobertura e E2E. Mocks somente em unitários.
- **Compatibilidade:** SQLs/checksums anteriores a 014, procedure legada, dados e artefatos oficiais permanecem. Nenhuma autorização para commit, push, DDL no banco de uso ou deploy é inferida deste planejamento.
