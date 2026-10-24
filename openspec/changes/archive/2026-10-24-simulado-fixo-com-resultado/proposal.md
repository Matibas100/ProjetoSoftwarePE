# Proposta — 4. Simulado fixo com resultado persistido

## Why

A prática individual não substitui uma avaliação com várias Questões. Esta entrega permite ao Administrador disponibilizar uma composição manual fixa e ao Aluno realizá-la, finalizar e consultar resultado e correção persistidos.

## What Changes

- Cadastrar simulado com título e sequência fixa de versões de Questões; revisar/publicar explicitamente pelo Administrador.
- Listar simulados disponíveis, iniciar/retomar tentativa própria e salvar respostas sem correção antecipada.
- Finalizar atomicamente, contar acertos, erros e respostas em branco e preservar resultado por versão.
- Arquivar simulado sem apagar tentativas e impedir novas tentativas com conteúdo retirado de uso.
- Fora de escopo: geração automática, composição dinâmica, importação de prova oficial, TRI, ranking, agendamento e limite de tempo. O MVP mostra progresso e usa finalização manual; não reproduz a avaliação ENEM oficial.

## Capabilities

### New Capabilities

- `simulados-fixos`: composição versionada manual, tentativa, respostas e resultado persistido.

### Modified Capabilities

- `gestao-administrativa-conteudo`: adicionar recorte de ADM-SIM-001/002 para criar, revisar/publicar e arquivar composição fixa.

## Impact

- Superfícies: Models de simulado/versão/itens/tentativa/respostas/evento, Services por caso de uso, Repositories especializados, Controllers, autorização e frontend administrativo/Aluno.
- Contratos propostos: gestão em `/api/admin/simulados`, catálogo em `/api/aluno/simulados`, tentativas em `/api/aluno/tentativas-simulado`; resultado e correção exclusivamente após finalização.
- Telas: ADM-SIM-001/002 e ALU-SIM-001/002/003/004, com recursos futuros indisponíveis e sem números fictícios.
- Dependências: item 2 (`gestao-basica-questoes`) fornece versões publicadas; item 3 (`pratica-questoes-com-historico`) estabelece autorização de Aluno, propriedade e padrão de correção. Localizar predecessoras pelo nome, inclusive após arquivamento. Executar depois do item 3 encerrado, embora respostas de simulado pertençam ao próprio módulo.
- Banco: migrations aditivas, FKs `RESTRICT` e resultado imutável; ADRs 001, 002, 003, 005 e 006.
- Compatibilidade: sem mudança nos contratos de prática, autenticação ou catálogo, sem alteração dos binários Desktop V1 e sem reorganização em módulos futuros.
