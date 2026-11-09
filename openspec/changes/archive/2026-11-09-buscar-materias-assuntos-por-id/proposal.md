# Proposal

## Why

Matéria e Assunto já possuem `buscar_por_id` na Model, mas não têm GET individual na API, como registra a pendência F02 da matriz CRUD. Hoje o formulário administrativo é preenchido com uma cópia da listagem, que pode estar desatualizada; consultar o registro antes da edição completa esse caminho de leitura e melhora a demonstração acadêmica.

## What Changes

- Adicionar `GET /api/materias/{id}` e `GET /api/assuntos/{id}`, exclusivos de Administrador autenticado, incluindo registros ativos, inativos e arquivados.
- Implementar um Service de consulta por recurso e delegação nas Controllers existentes, reutilizando `Model.buscar_por_id` e `to_dict`.
- Fazer o botão **Editar** de ADM-CON-001 e ADM-CON-002 carregar o detalhe real antes de preencher o formulário existente.
- Preservar campos, filtros e alterações não salvas diante de erro; impedir que leituras atrasadas sobrescrevam uma seleção ou edição mais recente.
- Acrescentar testes HTTP/MySQL, DOM e navegador real e atualizar README/matriz CRUD para encerrar apenas F02 após comprovação ponta a ponta.

### Fora de escopo

Gestão de usuários (F01), novas telas ou pesquisa digitada por ID, mudanças no ciclo editorial/exclusão, novas contagens, JOINs, relatórios, Repository para CRUD, migrations, novas dependências, redefinição dos vinte casos acadêmicos e alterações nos binários oficiais do Desktop V1.

## Capabilities

### New Capabilities

Nenhuma; a consulta pertence ao catálogo e à gestão existentes.

### Modified Capabilities

- `catalogo-academico`: consulta individual protegida de Matéria e Assunto, com payloads simples e erros previsíveis.
- `gestao-administrativa-conteudo`: edição começa com leitura individual atual, preservando contexto, permissão e rascunhos.

## Impact

- Backend: rotas e Controllers de Conteúdo; novos `BuscarMateriaPorIdService` e `BuscarAssuntoPorIdService`. CRUD simples segue na Model, conforme ADR-008; fronteiras do ADR-010 permanecem.
- Segurança: usar a autorização administrativa já aplicada aos caminhos individuais; manter Aluno apenas nas leituras de catálogo que já lhe são permitidas. GET/HEAD não exigem CSRF nem reautenticação sensível e usam `no-store` pelo fluxo existente.
- Frontend: `frontend/js/admin-materias.js` e `admin-assuntos.js`; pequenos estados de leitura nos formulários atuais, sem redesenho. Assunto mantém sua Matéria corrente selecionável mesmo inativa/arquivada, sem oferecer esses registros para novos vínculos.
- Testes e documentação: suíte de catálogo, testes DOM administrativos, E2E específico, README e `docs/technical/matriz-crud.md`.
- Compatibilidade: URLs de escrita, listas, filtros, transferência, arquivamento, exclusão condicionada, autenticação, Tutor e termos não mudam. Nenhuma alteração de Model, schema, migration, procedure ou quantidade de módulos/mappers.
- Dependências: nenhuma nova; MySQL real e ferramentas de testes existentes serão usados durante a implementação. A proposta não executa testes com escrita nem modifica código de produção.
