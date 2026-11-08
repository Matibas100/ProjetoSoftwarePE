# Proposta — Contas e Privacidade por procedures

## Why

Consultas de identidade/consentimento e operações especializadas de sessões/limites ainda usam ORM direto. Elas exigem procedures com preservação rigorosa das regras e da atomicidade, sem mover validação de senha ou decisões de consentimento para o banco. O objetivo é cumprir a exigência de acesso além do CRUD por procedures encapsuladas no Repository, mantendo o sistema demonstrável e compreensível.

## What Changes

- Converter o recorte fechado: Consulta por e-mail, sessão e usuário ativo bloqueado; renovação/revogação/limpeza de sessões; preparação concorrente do limite; lock de identidade e decisões correntes/replay de privacidade.
- Criar 11 procedures específicas, descritas em [inventário](inventario-procedures.md), com SQL estático e parâmetros vinculados; CALL permanece exclusivamente nos Repositories.
- Acrescentar `016_contas_privacidade_procedures.sql`, bootstrap equivalente, reconhecimento conservador do prefixo 016, preflight e testes MySQL reais.
- Preservar DTOs públicos, respostas HTTP, permissões, semântica temporal, locks e uma única transação externa; os métodos que alimentam escrita continuam retornando entidades ORM gerenciadas no proprietário.
- Atualizar documentação de procedures, rotas, Modules/Models/Repositories e cobertura da exigência. Não acrescentar funcionalidades à lista oficial por contar métodos SQL.

### Fora de escopo

Novas permissões, MFA/JWT, recuperação de senha, gestão/exclusão de Usuários, políticas legais novas, novos limites/retencões e CRUD básico de Usuário/Sessão/evidências nas Models. Sem novas telas, regras de produto, tabelas/colunas/FKs, bibliotecas, uso real de dados pessoais, gravação de vídeo, AWS ou operações Git.

## Capabilities

### New Capabilities

- `contas-privacidade-mysql`: interfaces MySQL específicas do domínio para o recorte inventariado, com compatibilidade, autorização e participação transacional verificáveis.

### Modified Capabilities

- `migrations-sql`: acrescentar comprovação do prefixo 016 e seus objetos SQL, sem enfraquecer os prefixos anteriores.

As specs funcionais existentes continuam válidas. Os novos requisitos descrevem a interface SQL externa e garantias de compatibilidade, sem reabrir decisões de negócio.

## Impact

- **Dependência obrigatória:** aplicar, verificar e sincronizar `adequar-plano-estudos-a-procedures` antes desta change. A sequência planejada é primeira etapa 011/012 → Catálogo 013 → Práticas/Simulados 014 → Plano 015 → Contas 016. Não aplicar essas changes simultaneamente; conferir eventual colisão de versão antes de editar.
- **Superfícies:** `contas/repositories/{autenticacao_repository,privacidade_repository}.py`, `contas/models/usuario.py`, Services de autenticação/privacidade e CLI existente. Caminhos relativos a `backend/app/modules/`.
- **Entradas mantidas:** `/api/auth/{csrf,cadastro,login,sessao,logout,reautenticar}`, rotas existentes `/api/aluno/privacidade` e decisões, mais CLI `limpar-autenticacao` e consumidores internos do lock de identidade. Telas e Controllers atuais atendem às mesmas funcionalidades; não criar Controller por procedure auxiliar.
- **Invariantes:** Mesmos cookies/CSRF/origens, códigos de erro, limites temporais, mensagens neutras, hash/verificação de senha no Service, revogação efetiva, evidências append-only e lock de identidade exato sem filtro novo de ativo.
- **Banco:** somente novas routines sobre as 21 Models existentes, sem DML funcional durante instalação/baseline. Procedures especializadas de escrita só executam no caso de uso autorizado, nunca pela migration.
- **ADRs:** preservar 001/002/003/004/005/006/008/009/010 conforme o domínio, complementando o ADR-011 e as interfaces SQL introduzidas pela primeira etapa sem alterar decisões históricas.
- **Testes:** `test_autenticacao_integration.py`, `test_privacidade_integration.py`, `test_planos_integration.py`, regressões completas e E2E de sessão/privacidade. Preservar também as 29 integrações originais, gates de arquitetura, cobertura e E2E. Mocks somente em unitários.
- **Compatibilidade:** SQLs/checksums anteriores a 016, procedure legada, dados e artefatos oficiais permanecem. Nenhuma autorização para commit, push, DDL no banco de uso ou deploy é inferida deste planejamento.
