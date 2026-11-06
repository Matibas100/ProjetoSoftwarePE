# Proposta: validar os fluxos de Plano e Simulado

## Why

A suíte de navegador percorre as vinte funcionalidades enumeradas, mas ainda não gera/recalcula um Plano nem finaliza um Simulado. Essas ações já existem e possuem testes de integração; falta comprovar sua ligação completa com a interface e distinguir, na documentação, as exigências de demonstração de duas atividades diferentes.

## What Changes

- Adicionar um teste independente em `frontend/e2e/plano-simulado.spec.js`, usando o runner Playwright/MySQL existente e dados sintéticos próprios. Preservar o teste atual dos vinte casos.
- Percorrer cadastro/publicação do conteúdo, práticas suficientes, geração do Plano, conclusão manual de item, execução/finalização de Simulado e recálculo confirmado. Verificar persistência, cancelamentos e diferenças entre as fórmulas do resultado e do diagnóstico.
- Atualizar README e `docs/technical/entrega-academica.md` com a evidência adicional e a distinção entre a atividade anterior (vinte funcionalidades e vídeo de até cinco minutos) e a rubrica final (quatro funcionalidades principais não CRUD, demonstração de até dois minutos, por vídeo ou execução hospedada). Não presumir que a rubrica dispensa uma entrega anterior.
- Manter a contagem oficial das vinte funcionalidades. Testes adicionais não representam novas funcionalidades nem garantem pontuação.

### Fora de escopo

Alterações de produção, refatoração, novas interfaces/abstrações de teste, dependências, mudanças em `playwright.config.js`, runner, CI, CSS, telas, autenticação, contratos, banco, migrations, procedure, specs principais ou binários oficiais. AWS, slides, roteiro, vídeo, guia de estudo, commit/push/merge e envio de atividade ficam para depois. Falha que exija correção de produto deve ser registrada e tratada por proposta própria, sem ampliar silenciosamente esta change.

## Capabilities

### New Capabilities

Nenhuma: ampliamos evidências automatizadas de comportamentos já implementados.

### Modified Capabilities

Nenhuma. As specs `plano-estudos-basico`, `simulados-fixos` e `desempenho-real` já descrevem os cenários. `skip_specs: true` dispensa deltas por se tratar somente de testes e documentação, sem mudança de comportamento especificado.

## Impact

- Arquivos de teste/documentação: somente novo `frontend/e2e/plano-simulado.spec.js`, `README.md` e `docs/technical/entrega-academica.md`, além dos registros da própria change.
- Telas exercitadas: `/index.html`, `/cadastro`, `/login`, edição/publicação administrativa de Questões e Simulado; questões/resolução, plano, execução/correção de Simulado e desempenho do Aluno.
- APIs existentes: cadastro/login; catálogo/Questões/publicação; Práticas; `/api/aluno/plano` e suas ações; execução/finalização/correção de Simulados; diagnóstico de desempenho. Nenhum novo endpoint ou payload.
- Arquitetura e decisões: preservar Frontend -> Route -> Controller -> Service -> Model/Repository -> MySQL e ADRs 002, 005, 006 e 008. Sessões, snapshots e fronteiras transacionais não serão simplificados para acomodar o teste.
- Dependências: implementação local consolidada, Node/Playwright/Chromium e MySQL 8 já utilizados. O runner requer configuração por ambiente e privilégio para schema descartável; nenhuma leitura de `.env`, nenhuma escrita no banco operacional.
- Validação: descoberta dos dois testes, execução real pelo runner com opt-in apenas no processo, conferência de resultados e limpeza, links e preservação do escopo. O desenho detalhado e as evidências esperadas estão em `design.md`.
