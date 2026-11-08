# Modelagem de domínio atual

Elaborada em **07/11/2026**, a partir do sistema implementado. Esta é a
formalização atual do domínio; não representa uma entrega anterior nem aprovação
do professor. A [matriz CRUD](matriz-crud.md) registra capacidades e lacunas.

## Contexto e vocabulário

A Plataforma ENEM organiza conteúdo para estudo, registra respostas próprias e
produz diagnóstico por Matéria/Assunto. O Aluno pratica e realiza Simulados; o
Administrador mantém catálogo e conteúdo. O plano básico opcional usa esse
diagnóstico mediante aceites vigentes de uso e da finalidade do plano.

| Conceito | Significado no recorte implementado |
| --- | --- |
| Catálogo | Área ENEM → Matéria → Assunto; classificação para conteúdo e leitura do desempenho. |
| Identidade editorial | Questão ou Simulado editável conforme seu ciclo; aponta para versão publicada. |
| Versão / snapshot | Conteúdo e classificação preservados para reproduzir o que foi respondido. |
| Tentativa | Execução própria do Aluno, ligada à versão usada; resposta e correção obedecem ao fluxo. |
| Evento | Fato editorial registrado com ação, motivo e ator; não é cadastro independente editável. |
| Desempenho | Projeção de respostas concluídas; não é uma Model ou tabela adicional. |
| Geração do plano | Conjunto derivado de prioridades e itens, com indicação do plano atual e vínculo ao anterior. |
| Evidência de privacidade | Registro imutável de decisão, versão e hash documental; não contém o documento completo. |
| Arquivamento | Mudança de estado que preserva identidade/histórico; difere de exclusão física. |

## Seis módulos e papéis das 21 Models

Os proprietários implementados seguem o [mapa modular](organizacao-modular.md)
e o [ADR-010](adr/ADR-010-organizacao-modular-do-backend.md). A divisão mais
granular da [arquitetura mestre](architecture-master-v1.md) permanece roadmap.
Os links abaixo apontam para as classes canônicas; `app.models` apenas as registra.

| Módulo | Model | Papel no domínio |
| --- | --- | --- |
| Contas | [Usuario](../../backend/app/modules/contas/models/usuario.py) | Identidade, perfil Aluno/Administrador e disponibilidade da conta. |
| Contas | [Sessao](../../backend/app/modules/contas/models/sessao.py) | Sessão pré-autenticada/autenticada, expiração, reautenticação e revogação. |
| Contas | [AuthLimite](../../backend/app/modules/contas/models/auth_limite.py) | Controle de falhas de autenticação por chave de hash, sem FK de Usuário. |
| Contas | [RegistroPrivacidade](../../backend/app/modules/contas/models/registro_privacidade.py) | Evidência de aceite de uso e das decisões sobre o plano. |
| Conteúdo | [AreaEnem](../../backend/app/modules/conteudo/models/area_enem.py) | Quatro áreas de referência fixa do catálogo. |
| Conteúdo | [Materia](../../backend/app/modules/conteudo/models/materia.py) | Disciplina vinculada à área, com ciclo de disponibilidade. |
| Conteúdo | [Assunto](../../backend/app/modules/conteudo/models/assunto.py) | Tópico vinculado à Matéria, com unicidade normalizada e transferência controlada. |
| Conteúdo | [AssuntoTransferencia](../../backend/app/modules/conteudo/models/assunto_transferencia.py) | Histórico de origem/destino e impacto da transferência. |
| Conteúdo | [Questao](../../backend/app/modules/conteudo/models/questao.py) | Identidade e conteúdo editorial corrente, com revisão e versão publicada. |
| Conteúdo | [QuestaoVersao](../../backend/app/modules/conteudo/models/questao_versao.py) | Snapshot imutável de conteúdo/classificação e autoria da publicação. |
| Conteúdo | [QuestaoEvento](../../backend/app/modules/conteudo/models/questao_evento.py) | Rastro imutável de ações editoriais da Questão. |
| Práticas | [PraticaTentativa](../../backend/app/modules/praticas/models/pratica_tentativa.py) | Execução de Questão publicada, resposta definitiva e correção própria. |
| Simulados | [Simulado](../../backend/app/modules/simulados/models/simulado.py) | Identidade editorial de uma composição manual fixa. |
| Simulados | [SimuladoRascunhoItem](../../backend/app/modules/simulados/models/simulado.py) | Posição e versão de Questão na composição em edição. |
| Simulados | [SimuladoVersao](../../backend/app/modules/simulados/models/simulado.py) | Snapshot publicado do Simulado. |
| Simulados | [SimuladoVersaoItem](../../backend/app/modules/simulados/models/simulado.py) | Composição ordenada e imutável da versão publicada. |
| Simulados | [SimuladoEvento](../../backend/app/modules/simulados/models/simulado.py) | Fatos imutáveis do ciclo editorial. |
| Simulados | [SimuladoTentativa](../../backend/app/modules/simulados/models/simulado.py) | Execução própria ligada à versão; consolida resultado na finalização. |
| Simulados | [SimuladoResposta](../../backend/app/modules/simulados/models/simulado.py) | Alternativa por item da tentativa, corrigida ao finalizar. |
| Plano de Estudos | [PlanoEstudo](../../backend/app/modules/plano_estudos/models/plano_estudo.py) | Geração própria derivada do diagnóstico, com vínculo à anterior. |
| Plano de Estudos | [PlanoEstudoItem](../../backend/app/modules/plano_estudos/models/plano_estudo.py) | Prioridade por Assunto, snapshot e conclusão manual. |

Contagens: Contas 4, Conteúdo 7, Práticas 1, Simulados 7 e Plano 2 = **21**.
O sexto módulo, **Desempenho**, possui zero Models: seus
[Services](../../backend/app/modules/desempenho/services/) coordenam consultas e
[projeções](../../backend/app/modules/desempenho/repositories/), sem gravar uma
tabela de diagnóstico inventada.

## Relações e invariantes principais

Os atributos, heranças e cardinalidades têm fonte única nas
[visões de domínio do diagrama](diagrama-de-classes.md#visoes-de-dominio),
conferidas com Models e migrations. Esta seção explica o significado das relações.

- **Catálogo:** Matéria pertence a uma área; Assunto pertence a uma Matéria.
  Transferência guarda o Assunto e as Matérias de origem/destino. Exclusão física
  é condicionada à ausência de vínculos; arquivar não apaga conteúdo histórico.
- **Questões e práticas:** a identidade aponta opcionalmente à versão publicada;
  versões/eventos guardam ator opcional. A tentativa pertence ao Usuário e à
  versão respondida, preservando sua classificação. Uma edição/transferência
  posterior não reescreve respostas anteriores.
- **Simulados:** rascunho e versão têm itens ordenados referenciando versões de
  Questões. A tentativa pertence ao Usuário e à versão do Simulado; cada resposta
  liga tentativa e item publicado. Publicação exige 1–180 itens; finalização
  consolida respostas/correção, preservadas após arquivamento.
- **Identidade e evidências:** sessão pode existir antes de autenticação, sem
  Usuário. Evidência de privacidade exige Usuário. O cadastro público grava conta
  e aceite de uso na mesma transação; esse vínculo protegido já impede prometer
  DELETE de qualquer conta apenas por não possuir práticas.
- **Plano:** Usuário possui gerações e seus itens; recálculo conserva anteriores
  durante uso autorizado. Recusa/revogação confirmada elimina todos os planos,
  itens e conclusões próprios na mesma transação da negativa. A exceção dos
  [ADRs 009](adr/ADR-009-consentimento-e-eliminacao-do-plano.md) e
  [010](adr/ADR-010-organizacao-modular-do-backend.md) não elimina respostas,
  Simulados, evidências ou dados de outra conta. Nova autorização inicia outro
  histórico de plano, sem recuperar derivados eliminados.

As FKs usam `RESTRICT`, sem cascata destrutiva. As bases de persistência seguem o
[ADR-008](adr/ADR-008-contratos-e-capacidades-de-persistencia.md): 13 Models em
`CrudMixin`, duas em `ModeloAtualizavel` e seis em `ModeloBase`. Métodos herdados
respeitam campos permitidos e guards; não garantem CRUD público de cada tabela.

## Alcance da formalização

As [vinte funcionalidades oficiais](entrega-academica.md#rastreabilidade-dos-vinte-casos)
permanecem com os mesmos IDs. A classificação dos seis recursos centrais na
[matriz CRUD](matriz-crud.md) serve à análise e não dispensa as outras quinze
Models da avaliação. Gestão de Usuários, consultas individuais dedicadas e
aceitação acadêmica das restrições continuam como pendências explícitas;
formalização documental não comprova envio, aprovação ou CRUD integral.
