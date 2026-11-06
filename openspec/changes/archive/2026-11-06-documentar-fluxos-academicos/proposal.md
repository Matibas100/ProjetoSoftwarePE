# Proposta: documentar os fluxos acadêmicos

## Why

A rubrica exige dois fluxogramas de casos de uso, um de recuperação e outro de entrada de dados, percorrendo as camadas e incluindo Repository; esses artefatos ainda não existem no repositório. A tela de desempenho e dois documentos operacionais também anunciam o Plano como indisponível, embora o plano básico já esteja implementado.

## What Changes

- Criar `docs/technical/fluxogramas-casos-de-uso.md` com dois fluxogramas Mermaid independentes: consultar diagnóstico de desempenho e finalizar tentativa de Simulado.
- Representar interface, rota Flask, proteção de acesso, Controller, Service, contratos/adaptadores, Repository, Models pertinentes e MySQL, com decisões, erros e retorno à tela. Os diagramas descrevem o código atual, inclusive leitura consistente, confirmação, revisão, replay e commit/rollback.
- Acrescentar referências no README e na matriz `docs/technical/entrega-academica.md`, mantendo a numeração das vinte funcionalidades. Finalizar Simulado é um caso já implementado adicional, não uma funcionalidade criada por esta documentação.
- Corrigir somente o aviso textual em `frontend/aluno/desempenho.html`, retirando a indisponibilidade do Plano básico e distinguindo recomendações avançadas ainda não implementadas.
- Alinhar as afirmações de disponibilidade em `docs/technical/operacao-desempenho.md` e `operacao-simulados.md`, apontando para a operação do Plano básico e preservando seus limites de agenda e automação.

### Fora de escopo

Slides, vídeo, roteiro, publicação/envio da atividade, commit/push/merge, hospedagem, IA, consentimento, novas funcionalidades, refatoração de camadas, mudanças em rotas/payloads, banco, migrations, procedure, layout ou binários oficiais do Desktop V1. Não implementar uma chamada desnecessária a Repository apenas para satisfazer o desenho.

## Capabilities

### New Capabilities

Nenhuma: documentação técnica de casos existentes e correção de informação textual.

### Modified Capabilities

Nenhuma. Os requisitos e cenários existentes de `desempenho-real`, `simulados-fixos` e `plano-estudos-basico` permanecem válidos; a correção textual apenas os reflete. A change usa `skip_specs: true`, sem inventar delta funcional para fluxogramas ou alterar contratos de produto.

## Impact

- Arquivos de implementação: exclusivamente o texto de um aviso em `frontend/aluno/desempenho.html`. Scripts, estilos, seletores, navegação, autenticação e comportamento não mudam.
- Documentação: novo documento de fluxogramas; links no README/matriz; correção das duas referências operacionais desatualizadas. Não reescrever documentação histórica arquivada.
- Casos representados: `GET /api/aluno/desempenho` em ALU-DES-001; `POST /api/aluno/tentativas-simulado/<id>/finalizar` no recorte de execução/resultado de Simulados. Referenciar símbolos concretos após a refatoração SOLID, sem editar o backend.
- Decisões preservadas: arquitetura mestre e ADRs 002 (sessão), 005 (versionamento), 006 (transações) e 008 (contratos e persistência). Fluxograma de leitura não grava métricas; fluxograma de entrada grava pelas Models, com consultas e locks no Repository.
- Validação: conferir os caminhos contra código/specs, renderizar e inspecionar os dois Mermaid, verificar links, aviso e regressão DOM pertinente. Não exigir integração MySQL ou cobertura completa apenas para documentação/texto sem alteração de lógica.
- Dependências: estado local das changes acadêmica e SOLID já aplicadas/arquivadas; ferramenta Mermaid já utilizada no projeto. Sem dependência adicional de produção e sem executar comandos que escrevam no banco operacional.
- Preservação: manter alterações legítimas ainda não commitadas, `tmp/`, changes anteriores e quatro binários oficiais. A rubrica orienta os artefatos, sem copiar o DOCX externo para o repositório ou presumir pontuação garantida.
