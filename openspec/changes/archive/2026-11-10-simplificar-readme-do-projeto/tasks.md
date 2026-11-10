# Tarefas

## 1. Preservar a fonte local

- [x] 1.1 Registrar hash, linhas, títulos/IDs, vinte itens e seções do README local, além do estado das alterações preexistentes e hashes não sensíveis das fontes/configurações. Verificar a diferença em relação à referência da proposta e iniciar o mapa de destinos em `validacao.md`; preservar a simplificação das ferramentas sem restaurar arquivos do HEAD ou editar seu arquivo arquivado.

## 2. Organizar os detalhes técnicos

- [x] 2.1 Criar `docs/technical/operacao-do-projeto.md` com as informações exclusivas do README destinadas a ele na tabela do design: contratos legados do catálogo, manutenção do banco, particularidades de testes/Make, checkpoints/histórico, clones antigos e preferências locais. Verificar cada seção contra a origem, conferir comandos por leitura e resolver seus links/âncoras; preservar precondições, resultados históricos e hook aposentado, usando links às fontes existentes quando já suficientes. Atualizar o mapa de transferência nessa etapa.
- [x] 2.2 Criar `docs/technical/operacao-tutor-ia.md` com configuração opcional, contrato, respostas HTTP, limites, dados e evidências do Tutor. Verificar preservação das informações e limitações da seção original, links relativos e correspondência com as fontes atuais; distinguir testes controlados da prova real anterior, sem chamar Gemini nem editar termos legais. Atualizar o mapa de transferência nessa etapa.

## 3. Simplificar a entrada do projeto

- [x] 3.1 Reorganizar o README conforme o design, com até 350 linhas, destaques não CRUD e os mesmos vinte itens sob `Funcionalidades Implementadas`; corrigir informações atuais para migration 017 e seis E2E. Manter preparação/execução suficientes, links para criação administrativa, diagramas/fluxogramas, contratos, testes e roteiro oficial. Verificar a lista contra a origem, comandos contra código/conventions, contagens por leitura estática e preservação de todos os IDs antigos como títulos ou âncoras junto aos novos destinos; manter a distinção entre as entregas, os limites acadêmicos e as evidências históricas.

## 4. Conferência integrada da documentação

- [x] 4.1 Concluir `validacao.md` com o mapa completo de seções, redução de linhas, links/âncoras, comandos conferidos e preservação de evidências. Verificar links locais dos três documentos e referências antigas ao README, bem como os hashes/estado dos demais arquivos em relação ao início; executar `git diff --check` e `openspec validate --all --strict`. Confirmar que somente README, os dois novos documentos e artefatos desta change foram alterados nesta execução. Não executar testes, descoberta E2E, instalação, operações Git de publicação, migrations ou limpeza de relatórios/temporários.

## Workflow follow-up

- Verificar a implementação antes do arquivamento; não há specs a sincronizar (`skip_specs: true`).
- Arquivar pelo workflow após a verificação; preservar os artefatos da change anterior já arquivada.
- Commit e push dependem de autorização explícita, inclusive para as alterações locais da simplificação das ferramentas.
