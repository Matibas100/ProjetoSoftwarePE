# Proposta: melhorar legibilidade e documentação

## Why

A revisão identificou HTML/CSS compactados, nomes locais pouco descritivos na finalização de Simulado, imports sem uso e informações atuais de publicação desatualizadas. Uma limpeza delimitada facilita leitura e explicação do projeto, sem introduzir ferramentas ou mudar o sistema validado.

## What Changes

- Formatar as oito páginas implementadas de `frontend/aluno/` e cinco folhas CSS compactadas (`aluno`, `auth`, `desempenho`, `plano`, `simulados`), preservando conteúdo, DOM funcional, aparência e ordem dos estilos.
- Tornar `FinalizarSimuladoService` mais legível: nomes locais descritivos e uma operação por linha, mantendo regras, validações, transação e resultados.
- Remover somente os 14 imports sem uso local confirmados em oito Controllers, após conferir que não são consumidos como reexportação.
- Atualizar README e a matriz de entrega sobre o checkpoint publicado/CI aprovado, distinguindo alterações posteriores ainda locais. Corrigir a referência desatualizada a quatro scripts na convenção de testes.
- Usar testes existentes, comparação estrutural e inspeção visual para verificar a preservação; não criar testes que apenas espelham formatação.

### Fora de escopo

Correção de JSON inválido em `api.js` (será uma change funcional separada); extração de helpers compartilhados; novas funcionalidades; mudanças de layout, textos da interface, contratos, arquitetura, autenticação, SQL, banco, migrations ou dependências. Não formatar o repositório inteiro, renomear Models/rotas ou reformar os demais Services/JavaScript. AWS, slides, guia de estudo, vídeo, commit/push/merge e edição de relatórios históricos ficam fora do escopo.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. A spec `simulados-fixos`, incluindo atomicidade, replay e cálculo da finalização, permanece intacta. A change usa `skip_specs: true` porque cobre organização textual, limpeza de imports e documentação, preservando o comportamento especificado.

## Impact

- Produto: oito HTML do Aluno, cinco CSS, oito Controllers e `finalizar_simulado_service.py`; lista exata e alterações permitidas em `design.md`.
- Documentação: README, `docs/technical/entrega-academica.md` e `docs/conventions/testes.md`. A lista/matriz oficial das vinte funcionalidades, requisitos das duas atividades, diagramas e links permanecem.
- API e persistência: nenhum contrato muda. O caso `POST /api/aluno/tentativas-simulado/<id>/finalizar` mantém a mesma ordem de decisões e gravações. Arquitetura mestre e ADRs existentes, especialmente 006/008, são preservados.
- Validação: unitários/cobertura backend com MySQL real, cobertura frontend, dois E2E existentes, equivalência estrutural do código/markup/CSS, inspeção visual proporcional e conferência documental. Sem novos testes de implementação ou dependências de formatação.
- Compatibilidade local: preservar a reorganização de migrations já aplicada/arquivada e ainda não commitada, `tmp/`, change antiga vazia, specs e artefatos oficiais congelados. A mudança do README parte do conteúdo local atual, sem apagar a explicação nova de migrations.
