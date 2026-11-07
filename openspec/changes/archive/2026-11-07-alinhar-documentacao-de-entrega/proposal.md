# Proposta — Alinhar a documentação da entrega

## Why

A aplicação já possui vinte casos documentados, três testes de navegador e CI aprovado, mas README/matriz ainda mencionam dois testes. A validação global estrita do OpenSpec aponta 31 descrições longas, dificultando a manutenção dos contratos e a leitura pelo grupo.

## What Changes

- Atualizar README e matriz acadêmica para os três percursos existentes: vinte funcionalidades, plano/simulado e privacidade. Manter os vinte IDs e distinguir evidência de teste, publicação e demonstração do grupo.
- Reorganizar editorialmente os 31 requisitos longos em sete specs principais: descrição curta de um comportamento, detalhes e exceções nos cenários correspondentes. Preservar cabeçalhos, cenários anteriores e todas as regras normativas, sem alterar comportamento ou contratos.
- Corrigir no contexto textual de `openspec/config.yaml` a referência ambígua às dez funcionalidades, distinguindo o MVP original dos vinte casos atuais. Não alterar schema, rules ou operations do workflow.
- Registrar rastreabilidade entre cada cláusula original e sua localização após a edição, permitindo conferir que nenhum limite, autorização, payload ou erro foi perdido.

### Fora de escopo

Código, testes de aplicação, banco/migrations, regras de negócio, alteração de contrato, novas funcionalidades, normas legais, textos HTML publicados, AWS, estudo/slides/vídeo, commit e push. Relatórios/ADRs históricos e binários oficiais não serão reescritos para parecerem atuais. O rascunho vazio `mover-join-assuntos-para-repository` foi removido separadamente durante este planejamento, por autorização expressa do usuário.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma mudança de comportamento especificado. Sete arquivos em `openspec/specs/` receberão somente manutenção editorial, preservando identidade dos requisitos e seu conteúdo normativo. `skip_specs: true` evita inventar delta funcional para uma mudança exclusivamente documental; a edição futura das fontes principais está explicitamente delimitada no design.

## Impact

- `README.md`, `docs/technical/entrega-academica.md` e somente o trecho textual do contexto em `openspec/config.yaml`.
- Specs principais `autenticacao-escolar`, `catalogo-academico`, `desempenho-real`, `gestao-administrativa-conteudo`, `plano-estudos-basico`, `questoes-versionadas` e `simulados-fixos`: 31 blocos enumerados no design.
- Nenhuma dependência nova, tela, rota, Model, Repository ou ADR de comportamento muda. As 29 integrações originais e os vinte casos entregues permanecem como requisitos, sem necessidade de rerodar aplicação por edição textual.
- Verificação: comparação editorial com baseline, links, correspondência dos três E2E, contexto YAML íntegro e `openspec validate --specs --strict` global sem avisos. Sugerido aplicar antes da change de fingerprint; não há dependência de código entre elas.
