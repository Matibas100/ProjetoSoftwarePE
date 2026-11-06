# Proposta: consolidar a entrega acadêmica

## Why

O código já contém mais de vinte casos de uso, mas o README não os enumera, falta um diagrama de classes e a validação atual não cobre o percurso completo no navegador. Corrigir os pontos de manutenção identificados e produzir evidências rastreáveis permite preparar a entrega exigida pelo professor sem ampliar o produto.

## What Changes

- Mover o JOIN da listagem de Assuntos ativos para `CatalogoRepository`, mantendo CRUD simples nas Models e Service próprio para listar.
- Eliminar consultas por item nas leituras de Questões elegíveis e Simulados, preservando filtros, paginação, propriedade, disponibilidade e snapshots históricos.
- Compartilhar a adaptação HTTP de sucesso/erros e o registro sanitizado de falhas internas, mantendo os contratos de cada recurso e os cookies/headers da autenticação.
- Compartilhar a navegação das páginas do Aluno, disponibilizando o Plano de Estudos em todas elas e preservando indicação da página atual, teclado e recuperação de sessão. Reutilizar apenas a infraestrutura de navegação compatível no Admin, sem reescrever formulários ou o MVP legado.
- Acrescentar testes de navegador com API Flask e MySQL reais, além de CI no GitHub para testes, cobertura e regressão de ponta a ponta.
- Atualizar o README com uma seção `Funcionalidades Implementadas` numerada, preparação até a migration 009, tecnologias, limites reais e links para diagrama e evidências.
- Documentar as Models implementadas, atributos, herança e relacionamentos em `docs/technical/diagrama-de-classes.md`; acrescentar matriz dos vinte fluxos em `docs/technical/entrega-academica.md`.

### Fora de escopo

Novas funcionalidades de domínio; mudanças de schema/migrations/procedure; novos perfis; reescrita em framework; alterações dos binários oficiais do Desktop V1; gravação/envio do vídeo; commit, push ou merge. O vídeo será gravado pelo usuário. A change vazia `mover-join-assuntos-para-repository` e os temporários preexistentes serão preservados; seu tema técnico será resolvido nesta consolidação, sem alterar sua metadata.

## Capabilities

### New Capabilities

Nenhuma. Documentação, automação, sanitização e otimizações internas não criam funcionalidades para inflar a contagem acadêmica.

### Modified Capabilities

- `plano-estudos-basico`: tornar o acesso ao plano consistente na navegação de todas as páginas implementadas do Aluno.

## Impact

- Backend: `models/assunto.py`, `services/listar_assuntos_service.py`, Services de leitura de Questões/Simulados, Repositories de Catálogo/Questões/Simulados e adaptação HTTP compartilhada em `backend/app/`, com Controllers mantidas como classes por recurso.
- Frontend: navegação de `frontend/aluno/*.html`, molduras administrativas compatíveis e scripts de navegação; formulários, IDs e scripts específicos preservados.
- Qualidade: testes unitários/DOM/MySQL afetados, nova suíte de navegador, `package.json`/lockfile, `Makefile`, scripts de execução e `.github/workflows/`. Playwright será dependência exclusiva de desenvolvimento; CI usará MySQL 8 descartável e credenciais exclusivas de teste.
- Documentação: README, diagrama, matriz e relatório de validação. Arquitetura de referência e ADRs aceitos permanecem normativos.
- Contratos: sem novas rotas nem mudanças de payload, status, ordenação, permissões, sessão ou regras de publicação. A evolução observável é a presença consistente do link do plano.
- Decisões relacionadas: ADR-001 (migrations), ADR-002 (sessão/segredos), ADR-003 (exclusão preservável), ADR-005 (versionamento) e ADR-006 (transações).
- Dependências: ambiente Python/Node existente, MySQL 8 e instalação do navegador de testes. A execução local usará schemas descartáveis com opt-in; não haverá escrita no banco operacional.
- Compatibilidade: manter os dez casos originais, os 29 testes de integração originais, as suítes ampliadas e os gates de 90% de linhas/85% de branches. Resultado ainda não executado não será registrado como aprovado.
