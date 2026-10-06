## Why

O catálogo acadêmico atual cobre apenas o CRUD básico de Matérias e Assuntos, mantém uma exclusão destrutiva em cascata e não implementa as telas administrativas aprovadas ADM-CON-001 e ADM-CON-002. A evolução é necessária para entregar o fluxo completo Área do ENEM → Matéria → Assunto → Questão, preservar os dados existentes e tornar a gestão segura e utilizável de ponta a ponta.

## What Changes

- Criar e semear as quatro Áreas do ENEM como catálogo fixo e vincular obrigatoriamente cada Matéria a uma Área.
- Adicionar ciclo de vida ativo, inativo e arquivado para Matérias e Assuntos, com reativação e bloqueio de novos vínculos a itens indisponíveis.
- Remover o `ON DELETE CASCADE` e o `delete-orphan` entre Matéria e Assunto, adotando `RESTRICT` para vínculos que impedem exclusão física.
- Adicionar `nome_normalizado` a Assunto e garantir unicidade por Matéria independentemente de caixa, espaços, acentuação e forma Unicode, inclusive quando o registro equivalente estiver arquivado.
- Implementar avaliação de impacto, bloqueio de exclusão e transferência explícita, atômica e registrada de Assunto para outra Matéria.
- Evoluir as APIs de catálogo com filtros, paginação, contagens, estados e operações complementares, preservando respostas legadas sempre que o novo requisito não exigir mudança.
- Implementar ADM-CON-001 e ADM-CON-002 conforme o Desktop V1, incluindo navegação administrativa, filtros, tabelas, formulários, mensagens, estados vazios/erro/sucesso, alterações não salvas, bloqueios, arquivamento e transferência.
- Adicionar migrations SQL puro, testes unitários, integrações com MySQL real, testes DOM e validação visual, mantendo a suíte de regressão.
- **BREAKING**: criação e atualização de Matéria passam a exigir uma Área válida; consumidores que criam Matérias deverão enviar `area_enem_id`.
- Manter fora do escopo autenticação, usuários, permissões, simulados, redação, IA, desempenho, plano de estudos e implementação funcional de Resumos.

## Capabilities

### New Capabilities

- `catalogo-academico`: modelagem, integridade, ciclo de vida, normalização, exclusão segura, impacto, transferência e contratos de API para Áreas, Matérias e Assuntos.
- `gestao-administrativa-conteudo`: comportamento observável das telas ADM-CON-001 e ADM-CON-002, incluindo filtros, tabelas, formulários, estados e integração com as APIs.

### Modified Capabilities

- Nenhuma. A capability existente `migrations-sql` será utilizada sem alterar seus requisitos.

## Impact

- **Telas:** ADM-CON-001 e ADM-CON-002; seletores de Matéria e Assunto do MVP devem deixar de oferecer itens indisponíveis para novos vínculos.
- **Backend:** routes, controllers, services, Models `Materia` e `Assunto`, consultas especializadas de catálogo e infraestrutura transacional necessária à transferência.
- **APIs:** endpoints atuais `/api/materias` e `/api/assuntos`, além de contratos complementares para Áreas, listagens administrativas, impacto, arquivamento, reativação e transferência.
- **Banco:** novas estruturas e colunas, backfill preservador, constraints, índices e substituição da FK Matéria → Assunto; `create_database.sql` continuará equivalente às migrations.
- **Dependências:** runner SQL e `schema_migrations` já instituídos; ADR-001, ADR-003, ADR-004 e ADR-006.
- **Compatibilidade:** IDs e dados existentes serão preservados; os contratos de leitura legados permanecerão aproveitáveis, enquanto a obrigatoriedade de Área será uma evolução explícita dos contratos de escrita.
- **Testes:** regressão das funcionalidades atuais, novos testes de migration, domínio, APIs, concorrência, DOM, acessibilidade básica e aderência visual em 1440 px.
