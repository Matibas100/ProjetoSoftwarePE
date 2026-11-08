# Proposta — Catálogo e Questões editoriais por procedures

## Why

Seletores, impactos, validações de vínculo e elegibilidade ainda usam consultas especializadas ORM. A etapa amplia a adoção de procedures sem alterar o CRUD básico nem a política editorial. O objetivo é cumprir a exigência de acesso além do CRUD por procedures encapsuladas no Repository, mantendo o sistema demonstrável e compreensível.

## What Changes

- Converter o recorte fechado: Seletores de Áreas/Matérias/Assuntos, impactos e equivalência de Assunto, locks de transferência/publicação, versões e elegibilidade individual/em lote de Questões.
- Criar 15 procedures específicas, descritas em [inventário](inventario-procedures.md), com SQL estático e parâmetros vinculados; CALL permanece exclusivamente nos Repositories.
- Acrescentar `013_catalogo_editorial_procedures.sql`, bootstrap equivalente, reconhecimento conservador do prefixo 013, preflight e testes MySQL reais.
- Preservar DTOs públicos, respostas HTTP, permissões, semântica temporal, locks e uma única transação externa; os métodos que alimentam escrita continuam retornando entidades ORM gerenciadas no proprietário.
- Atualizar documentação de procedures, rotas, Modules/Models/Repositories e cobertura da exigência. Não acrescentar funcionalidades à lista oficial por contar métodos SQL.

### Fora de escopo

Listagens administrativas/contagens da primeira change, seleção de pares do Plano (reservada à 015), escritas CRUD e cálculo das regras editoriais. Sem novas telas, regras de produto, tabelas/colunas/FKs, bibliotecas, uso real de dados pessoais, gravação de vídeo, AWS ou operações Git.

## Capabilities

### New Capabilities

- `catalogo-editorial-mysql`: interfaces MySQL específicas do domínio para o recorte inventariado, com compatibilidade, autorização e participação transacional verificáveis.

### Modified Capabilities

- `migrations-sql`: acrescentar comprovação do prefixo 013 e seus objetos SQL, sem enfraquecer os prefixos anteriores.

As specs funcionais existentes continuam válidas. Os novos requisitos descrevem a interface SQL externa e garantias de compatibilidade, sem reabrir decisões de negócio.

## Impact

- **Dependência obrigatória:** aplicar, verificar e sincronizar `adequar-consultas-academicas-a-procedures` antes desta change. A sequência planejada é primeira etapa 011/012 → Catálogo 013 → Práticas/Simulados 014 → Plano 015 → Contas 016. Não aplicar essas changes simultaneamente; conferir eventual colisão de versão antes de editar.
- **Superfícies:** `conteudo/repositories/{catalogo_repository,questao_repository}.py`, `conteudo/models/{area_enem,materia,assunto}.py`, Services/Controllers do proprietário e seus consumidores públicos. Caminhos relativos a `backend/app/modules/`.
- **Entradas mantidas:** `/api/areas-enem`, `/api/materias`, `/api/assuntos`, impactos de exclusão/transferência, transferência, detalhe/publicação de Questões e `/api/aluno/questoes`. Telas e Controllers atuais atendem às mesmas funcionalidades; não criar Controller por procedure auxiliar.
- **Invariantes:** Catálogo ativo para novos vínculos, comparação normalizada atual, RESTRICT, classificação histórica e ordem de locks já implementada.
- **Banco:** somente novas routines sobre as 21 Models existentes, sem DML funcional durante instalação/baseline. Procedures especializadas de escrita só executam no caso de uso autorizado, nunca pela migration.
- **ADRs:** preservar 001/002/003/004/005/006/008/009/010 conforme o domínio, complementando o ADR-011 e as interfaces SQL introduzidas pela primeira etapa sem alterar decisões históricas.
- **Testes:** `test_catalogo_admin_integration.py`, `test_materias_integration.py`, `test_assuntos_integration.py`, `test_questoes_versionadas_integration.py` e início de Práticas/Simulados/Plano. Preservar também as 29 integrações originais, gates de arquitetura, cobertura e E2E. Mocks somente em unitários.
- **Compatibilidade:** SQLs/checksums anteriores a 013, procedure legada, dados e artefatos oficiais permanecem. Nenhuma autorização para commit, push, DDL no banco de uso ou deploy é inferida deste planejamento.
