# Design — Alinhamento editorial da entrega

## Context

Ver [motivação e escopo](proposal.md). A documentação reúne evidências de épocas diferentes. O contrato atual está em onze capabilities, enquanto 31 descrições de requisitos de sete delas excedem o limite recomendado pelo validador. O problema é editorial; o código não será usado como justificativa para mudar silenciosamente uma regra normativa.

## Goals / Non-Goals

**Goals:** reduzir os avisos sem perder cláusulas; permitir que o grupo encontre as vinte funcionalidades e os três percursos de navegador; distinguir execução histórica, publicação e demonstração acadêmica.

**Non-Goals:** criar requisitos novos, renomear requisitos, prometer conformidade legal ou interpretar a rubrica como dispensa do vídeo. Não há alteração no fluxo Frontend → Controller → Service → Model/Repository → MySQL, nas transações ou na Stored Procedure.

## Decisions

### 1. Edição das fontes principais, sem delta funcional

Esta change usa `skip_specs: true`: não existe comportamento novo a sincronizar. A implementação editará diretamente os sete arquivos principais delimitados abaixo. Criar deltas MODIFIED com o mesmo comportamento duplicaria texto e poderia sobrescrever edições posteriores na sincronização.

Preservar todos os títulos de requisitos, seus identificadores, Purpose e todos os cenários existentes. Cada descrição longa passará a conter a obrigação central, com até 500 caracteres; detalhes serão transferidos para cenários existentes ou novos cenários que expressem exclusivamente cláusulas já presentes. Não dividir, excluir ou renomear requisitos para contornar o aviso.

### 2. Inventário obrigatório dos 31 blocos

Cada capability corresponde a `openspec/specs/<nome>/spec.md`.

| Capability | Títulos dos requisitos a reorganizar |
| --- | --- |
| `autenticacao-escolar` (10) | Cadastro público exclusivo de Aluno; Login por credenciais com rotação de sessão; Ciclo de vida da sessão no servidor; Proteção de origem e CSRF; Autorização por perfil e recurso; Reautenticação de ações sensíveis; Limite básico de tentativas de senha; Navegação autenticada e telas utilizáveis; Evolução compatível do banco e do MVP; URLs canônicas das páginas públicas de autenticação |
| `catalogo-academico` (1) | Compatibilidade dos consumidores existentes |
| `desempenho-real` (4) | Métricas derivadas de fatos concluídos; Período e classificação históricos explícitos; Dashboards privados e operacionais; Contrato reutilizável e interface honesta |
| `gestao-administrativa-conteudo` (4) | Proteção de alterações não salvas; Acesso administrativo autenticado; Gestão mínima utilizável de Questões; Gestão mínima utilizável de Simulados fixos |
| `plano-estudos-basico` (5) | Priorização determinística baseada em desempenho; Geração persistida exclusiva do dono; Início de prática e conclusão manual; Recálculo explícito com preservação de histórico; Privacidade e fluxo mínimo acessível |
| `questoes-versionadas` (3) | Listagem e detalhe administrativos de Questões; Cadastro e edição de rascunho compatíveis; Publicação explícita com versão imutável |
| `simulados-fixos` (4) | Composição fixa revisada e publicada; Início e retomada de tentativa própria; Finalização atômica com resultado imutável; Consulta privada e preservação histórica |

As quatro capabilities restantes e os demais requisitos desses sete arquivos ficam intactos. Se a leitura atual revelar obrigação contraditória, interromper aquela edição e registrar o achado; esta change não autoriza resolvê-lo alterando o contrato.

### 3. Rastreabilidade por cláusula

Antes da edição, registrar revisão Git, títulos e contagens dos requisitos/cenários e salvar uma referência verificável dos blocos originais. Criar `validacao.md` nesta change durante o apply, com uma linha por cláusula normativa transferida: capability, requisito, obrigação original e cenário/trecho de destino. A referência pode usar o conteúdo Git se corresponder ao arquivo; havendo edição legítima ainda não commitada, conservar o trecho original no relatório.

A revisão deve preservar `SHALL`/`MUST` e proibições, perfis/dono, payloads e literais, URLs e status HTTP, valores numéricos, defaults, limites, datas/fuso, idempotência, atomicidade e condições de erro. Contagens e busca de palavras auxiliam, mas não substituem a comparação semântica. Uma descrição curta sem essas regras realocadas não atende ao aceite.

### 4. Evidências e contexto atualizados sem reescrever o histórico

- README e `docs/technical/entrega-academica.md` devem listar os três arquivos reais: `entrega-academica.spec.js` (vinte casos numerados), `plano-simulado.spec.js` e `privacidade.spec.js`. Descoberta de testes não significa execução aprovada. Não inflar os vinte IDs contando passos técnicos ou os novos testes como funcionalidades.
- Atualizar o estado de publicação com evidência identificável: commit `6f40f1303560cad908fbdd752fd0aaa4dd285b3b` e [execução de CI aprovada](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42337772001). Não atribuir esse resultado a alterações posteriores. Relatórios arquivados continuam descrevendo sua execução original.
- No `context` textual de `openspec/config.yaml`, distinguir dez funcionalidades do MVP original das vinte entregues; manter a referência às 29 integrações originais e à suíte ampliada. Preservar `schema`, `rules`, `operations` e os demais guardrails.
- Preservar as obrigações externas existentes: vídeo/slides, AWS, contato real e tratamento de menores continuam com o estado já documentado. Não criar roteiro.

### 5. Superfície de edição e validação

A implementação tem lista fechada de dez arquivos principais: sete specs da tabela, `README.md`, `docs/technical/entrega-academica.md` e `openspec/config.yaml`; além do relatório/tarefas desta change. Não editar código, dependências, SQL, HTML legal, ADRs históricos ou artefatos visuais.

Validar cada capability após sua edição; ao final executar `openspec validate --specs --strict` sem erros nem avisos. Conferir links, parsing YAML sem dependência nova, diff de títulos/cenários e correspondência da matriz 1–20 com as fontes. Executar `npm run test:e2e:list` para confirmar os três testes descobertos, sem conexão MySQL nem alegação de execução E2E. A suíte da aplicação não precisa ser executada por edição textual.

## Risks / Trade-offs

- [Regra perdida ao encurtar um parágrafo] → Matriz por cláusula, comparação com baseline e conservação dos cenários anteriores.
- [Texto atual apresentado como evidência histórica] → Identificar SHA/run e separar explicitamente descoberta, execução e entrega do grupo.
- [Contagens envelhecem] → Apontar para fontes e comandos, evitando repetir totais de testes em novos lugares.
- [Edição concorrente] → Reler os arquivos antes de editar e preservar mudanças legítimas; limitar os blocos afetados.

## Migration Plan

Aplicar esta change primeiro e depois a de fingerprint. Não há deploy, migration ou operação de banco. Reversão consiste em restaurar somente os trechos documentais desta change, preservando edições concorrentes. Ao concluir, verificar e arquivar pelo workflow; não há delta de capability para sincronizar.
