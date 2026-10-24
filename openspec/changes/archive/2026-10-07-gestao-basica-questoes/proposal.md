# Proposta — 2. Gestão básica de Questões

## Why

O MVP já cadastra Questões e busca por Assunto, mas não oferece gestão completa, edição ou retirada de uso. Esta entrega fecha esse fluxo e prepara versões estáveis para as respostas e simulados das entregas seguintes.

## What Changes

- Listar, filtrar, cadastrar, visualizar e editar Questões na Administração.
- Retirar de uso por arquivamento, sem exclusão física.
- Separar identidade lógica, rascunho e versão publicada imutável; publicar somente após revisão explícita pelo Administrador.
- Preservar o cadastro e a consulta legados, inclusive seus payloads e a Stored Procedure.
- Fora de escopo: importação, IA, mídias, lotes, detecção de duplicidade e fila editorial com múltiplos perfis. A revisão mínima é feita pelo único perfil Administrador existente, com validação, confirmação e registro da decisão; não equivale à governança definitiva do Desktop V1.

## Capabilities

### New Capabilities

- `questoes-versionadas`: gestão básica, elegibilidade e versões de Questões preserváveis.

### Modified Capabilities

- `gestao-administrativa-conteudo`: acrescentar o recorte mínimo de ADM-QUE-001 e ADM-QUE-002, mantendo Matérias e Assuntos.

## Impact

- Superfícies: `Questao`, novos modelos de versão/evento editorial, Services de cadastro/edição/publicação/arquivamento, `QuestaoRepository`, Controllers, `routes.py`, `auth_http.py` e frontend administrativo.
- Contratos propostos: manter `POST /api/questoes` e `GET /api/questoes/por-assunto`; adicionar `GET /api/admin/questoes`, `GET/PUT /api/questoes/<id>` e ações separadas de publicar/arquivar. Detalhes no design e nas specs, sujeitos à revisão desta change.
- Banco: migration aditiva e backfill auditado, sem publicar automaticamente conteúdo legado; snapshot equivalente e FKs restritivas.
- Dependências: item 1 concluído e catálogo já implementado. Executar esta change antes do item 3; não depende de changes futuras.
- ADRs: 001, 002, 003, 004, 005 e 006; 007 permanece sem implementação porque não haverá upload.
- Compatibilidade: preservar IDs, os dez casos de uso, os 29 testes originais, autenticação, catálogo e binários oficiais. Usar HTML/CSS/JS existentes e referências visuais do Desktop V1, sem reestruturação ampla.
