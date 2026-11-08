# Design — Documentação do domínio e da cobertura CRUD

## Context

Ver [proposta](proposal.md) e [levantamento atual](levantamento-crud.md). O diagrama existente já cobre as 21 Models, mas intercala visões de domínio com Controllers/Services/composição. A matriz de entrega rastreia vinte funcionalidades, não o CRUD de cada tabela.

Esta change é exclusivamente documental. As decisões de persistência, autorização e retenção continuam nas specs/ADRs existentes; a documentação não aprova exceções em nome do professor e não implementa os casos ausentes.

## Goals / Non-Goals

**Goals:** fornecer uma modelagem atual identificável e uma leitura honesta da cobertura CRUD, com fontes verificáveis e próximos passos definidos por lacuna.

**Non-Goals:** transformar todas as tabelas em telas de gestão, acrescentar métodos incompatíveis às Models ou escolher políticas novas de exclusão/gestão de contas. As decisões necessárias às futuras funcionalidades são registradas como pendências dessas funcionalidades, sem impedir a conclusão documental.

## Decisions

### 1. Uma modelagem atual, sem inventar histórico de entrega

Criar `docs/technical/modelagem-de-dominio.md` com contexto do problema, conceitos, proprietários e relações principais: catálogo, conteúdo versionado, identidade, tentativas, Simulados, plano e privacidade. Identificar que descreve o sistema implementado na data da revisão, não um documento entregue ou aprovado anteriormente.

Usar as 21 Models reais e seus seis módulos como inventário fechado. Os seis recursos centrais do levantamento são uma classificação proposta para análise, não uma declaração de que o professor dispensou CRUD para os demais. As quinze outras Models também permanecem identificadas com seu papel e capacidades. Desempenho continua projeção, sem classe ORM/tabela inventada.

Não duplicar integralmente atributos e cardinalidades em outro diagrama: o novo documento usa glossário/contexto e aponta para as visões de domínio do diagrama existente. Isso mantém uma fonte de verdade para classes/FKs. Exemplos não incluem senhas, tokens, dados pessoais reais ou documentos de usuários.

### 2. Separar domínio e aplicação no diagrama existente

Reorganizar `docs/technical/diagrama-de-classes.md` em blocos identificados de domínio (Models, bases, atributos e relacionamentos) e aplicação (Controllers, Services, APIs e composição). Os vínculos de aplicação atualmente misturados à visão de privacidade/propriedade passam ao bloco de aplicação.

Conservar todas as classes, atributos principais, cardinalidades, herança e visões já documentadas. Não modificar relações para parecer que uma operação CRUD existe, nem introduzir composição/cascade ou entidades de exemplo do professor. Corrigir somente explicações locais necessárias, como a exceção de eliminação do plano após negativa: recálculo conserva gerações durante uso autorizado, mas a recusa/revogação confirmada elimina os derivados conforme ADRs 009/010.

Verificar os blocos Mermaid após a reorganização com as ferramentas já disponíveis; não instalar renderizador/dependência nova. Comparar inventário e relações antes/depois e conferir links/âncoras afetados.

### 3. Matriz com três níveis de evidência

Criar `docs/technical/matriz-crud.md`, derivada do levantamento, distinguindo:

1. **Model:** métodos herdados e invariantes, por introspecção/AST sem banco.
2. **API/caso de uso:** rota real → Controller → Service → Model/Repository; método de persistência sozinho não comprova esse nível.
3. **Interface:** tela/ação que efetua a operação; listagem de sessão, CLI e operação interna não viram automaticamente uma tela CRUD.

Usar uma tabela de recursos centrais e outra para as demais Models, com detalhes de rotas/fontes por recurso. Registrar todos os 21 nomes uma vez no inventário, incluindo Models de itens/histórico/infraestrutura. Não equiparar recálculo a PUT genérico nem arquivamento/desativação a DELETE físico. A limpeza decorrente de consentimento é uma operação especializada explícita, não exclusão manual de plano.

Matéria e Assunto têm as quatro operações CRUD pela interface, com DELETE condicionado; registrar também que GET individual dedicado ainda não existe. As respectivas Models oferecem `buscar_por_id` para os casos existentes. Usuário não tem gestão CRUD completa de ponta a ponta. Questões/Simulados têm gestão editorial restrita; as bases de snapshots/eventos/evidências não oferecem atualizar/deletar por decisão de domínio.

Ligar as linhas a arquivos/Classes e às rotas efetivas, usando caminhos canônicos modulares e links relativos. Reaproveitar a matriz acadêmica para as vinte funcionalidades sem duplicar IDs ou contar esta documentação como funcionalidade nova. Registrar separadamente a evidência histórica de E2E, sem alegar nova execução ou aprovação por mera leitura estática.

### 4. Pendências e propostas de continuidade delimitadas

Transportar os IDs D01, F01, F02 e E01–E03 do levantamento para a matriz final:

- D01 é resolvido documentalmente por esta change; envio/aceite acadêmico não é realizado nem presumido.
- F01 permanece uma candidata a change funcional de gestão de Usuários. Exige definir ator, campos, listagem/detalhe, validações de identidade, efeitos nas sessões e política de desativação/exclusão antes de prometer CRUD completo.
- F02 registra a possível necessidade de demonstrar busca individual de Matéria/Assunto; não adicionar rotas ou botões nesta change.
- E01–E03 registram a diferença entre exigência literal e operações/capacidades do domínio; justificativa técnica não equivale a autorização do professor para dispensar CRUD.

Explicar a restrição de Usuário já comprovada: o aceite de uso gravado no cadastro referencia a conta com RESTRICT e é protegido. Portanto, uma futura proposta não pode prometer excluir qualquer conta “sem práticas”, omitir esse vínculo ou remover evidências silenciosamente. Não definir agora uma nova regra de retenção ou alteração de FKs.

### 5. Superfície de edição e validação proporcional

No apply, editar somente estes cinco documentos principais, além dos artefatos desta change:

- `docs/technical/modelagem-de-dominio.md` (novo);
- `docs/technical/matriz-crud.md` (novo);
- `docs/technical/diagrama-de-classes.md`;
- `docs/technical/entrega-academica.md` (links e contexto, sem renumerar a matriz);
- `README.md` (links/contexto, sem prometer funcionalidades ausentes).

Antes das edições, registrar hashes/estado atual e uma referência das visões de domínio. Conferir os 21 mappers e métodos sem conexão MySQL, com `.env` desabilitado e configuração sintética; inventariar as rotas por factory sem SQL. Essa verificação é estática/estrutural, não simulação de integração nem evidência de persistência funcionando.

Conferir nomes, atributos principais, relações/FKs e métodos contra as fontes atuais; preservar 13 Models em CrudMixin, duas em ModeloAtualizavel e seis em ModeloBase. Validar links/âncoras, blocos Mermaid, contagem única e cobertura das linhas da matriz. Confirmar que a lista de vinte funcionalidades e seus IDs permanece idêntica. Executar OpenSpec estrito e diff/check de escopo, sem cobertura, E2E, migrations ou banco operacional por mudança documental.

Registrar comandos, evidências e limites reais no `validacao.md` desta change. Nenhuma aprovação externa, regularização no Classroom ou cumprimento integral das exigências é inferida dos testes documentais.

## Risks / Trade-offs

- [Matriz apresentar método herdado como funcionalidade pronta] → Colunas separadas para Model, API/caso de uso e interface.
- [Tratar restrição de domínio como dispensa acadêmica] → Status e pendências explícitos, sem afirmar aceite do professor.
- [Nova documentação divergir do diagrama] → Referenciar a fonte única de classes/relações e comparar o inventário atual.
- [Modelo atual parecer entrega anterior] → Data/contexto de elaboração claros e nenhuma afirmação retroativa de envio/aprovação.
- [Ajuste de documentação virar nova gestão de contas] → Lista fechada de cinco documentos; F01/F02 somente em changes funcionais próprias.

## Migration Plan

Publicar os dois documentos, reorganizar as visões e acrescentar links nos pontos de entrada da documentação. Não há migration, deploy ou operação de dados. Reversão afeta apenas os hunks documentais desta change, preservando alterações externas.

Após aplicar, verificar e arquivar pelo workflow. Não há delta funcional a sincronizar. Commit, push, envio ao professor e definição das funcionalidades futuras ficam para instruções próprias.
