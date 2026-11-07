# Diagrama de classes implementadas

Referência: [Models](../../backend/app/models/), migrations
[000–010](../../backend/database/migrations/) e [arquitetura](architecture-master-v1.md).
As visões de domínio cobrem as **21 Models concretas** atuais. Classes
repetidas entre visões são referências à mesma entidade, sem duplicar tabelas.
`PK` indica chave primária; `FK` indica referência; `?` indica campo opcional.
Os atributos são os principais, não uma reprodução integral do schema.

## Privacidade — uma Model adicional

```mermaid
classDiagram
class ModeloBase
class Usuario
class RegistroPrivacidade {
  bigint id PK
  int usuario_id FK
  string tipo
  string acao
  string versao
  char64 documento_sha256
  datetime registrado_em
  uuid chave_envio
  bigint revisao_base
}
ModeloBase <|-- RegistroPrivacidade
Usuario "1" --> "0..*" RegistroPrivacidade
PrivacidadeController --> ConsultarTermosService
PrivacidadeController --> ConsultarPrivacidadeService
PrivacidadeController --> AceitarTermosUsoService
PrivacidadeController --> ConsentirPlanoService
PrivacidadeController --> RecusarConsentimentoPlanoService
PrivacidadeController --> RevogarConsentimentoPlanoService
ConsultarPrivacidadeService --> PrivacidadeRepository
AceitarTermosUsoService --> RegistroPrivacidade
ConsentirPlanoService --> RegistroPrivacidade
RecusarConsentimentoPlanoService --> PrivacidadeRepository
RevogarConsentimentoPlanoService --> PrivacidadeRepository
ValidarPermissaoPlanoService --> PrivacidadeRepository
GerarPlanoService --> ValidarPermissaoPlanoService
RecalcularPlanoService --> ValidarPermissaoPlanoService
ConsultarPlanoService --> ValidarPermissaoPlanoService
ConcluirPlanoItemService --> ValidarPermissaoPlanoService
CadastrarAlunoService --> RegistroPrivacidade
```

`RegistroPrivacidade` possui salvar/consultar e guards de imutabilidade, sem
atualizar/deletar. A negativa confirmada usa eliminação especializada de planos
no Repository, sem relaxar seus guards ORM, conforme [ADR-009](adr/ADR-009-consentimento-e-eliminacao-do-plano.md).

## Herança e persistência

```mermaid
classDiagram
direction LR
class dbModel["db.Model"]
class ModeloBase {
  <<abstract>>
  salvar(confirmar=True)
  listar_todos()
  buscar_por_id(id)
}
class ModeloAtualizavel {
  <<abstract>>
  atualizar(confirmar=True, dados)
}
class CrudMixin {
  <<abstract>>
  deletar(confirmar=True)
}
dbModel <|-- ModeloBase
ModeloBase <|-- ModeloAtualizavel
ModeloAtualizavel <|-- CrudMixin
```

Cada Model herda de uma única base abstrata, por um único caminho até `db.Model`.
O import legado de `CrudMixin` permanece em `app.models.crud_mixin`.
CRUD simples usa Active Record; `confirmar=False` participa da fronteira do
Service via `TransactionManager`. Consultas especializadas ficam nos
Repositories. As setas de herança nas visões seguintes tornam o caminho explícito.

## Catálogo e identidade — sete Models

```mermaid
classDiagram
direction LR
class CrudMixin
class AreaEnem {
  int id PK
  string codigo
  string nome
  int ordem
}
class Materia {
  int id PK
  int area_enem_id FK
  string nome
  string status
}
class Assunto {
  int id PK
  int materia_id FK
  string nome
  string nome_normalizado
  string status
}
class AssuntoTransferencia {
  bigint id PK
  int assunto_id FK
  int materia_origem_id FK
  int materia_destino_id FK
  int questoes_impactadas
  datetime criado_em
}
class Usuario {
  int id PK
  string nome
  string email
  string senha_hash
  string perfil
  bool ativo
}
class Sessao {
  bigint id PK
  int usuario_id FK opcional
  string identificador_hash
  datetime expira_em
  datetime reautenticada_em opcional
  datetime revogada_em opcional
}
class AuthLimite {
  string chave_hash PK
  int falhas
  datetime janela_inicio
  datetime bloqueado_ate opcional
}
CrudMixin <|-- AreaEnem
CrudMixin <|-- Materia
CrudMixin <|-- Assunto
CrudMixin <|-- AssuntoTransferencia
CrudMixin <|-- Usuario
CrudMixin <|-- Sessao
CrudMixin <|-- AuthLimite
AreaEnem "1" <-- "0..*" Materia : area_enem_id
Materia "1" <-- "0..*" Assunto : materia_id
Assunto "1" <-- "0..*" AssuntoTransferencia : assunto_id
Materia "1" <-- "0..*" AssuntoTransferencia : origem
Materia "1" <-- "0..*" AssuntoTransferencia : destino
Usuario "0..1" <-- "0..*" Sessao : usuario_id
```

`Sessao.usuario_id` nulo representa a sessão pré-autenticação. `AuthLimite`
é indexada por hash de limite: **não possui FK de usuário** e não recebe uma
associação inventada. Transferências guardam origem/destino e contagem histórica.

## Questões e Práticas — quatro Models

```mermaid
classDiagram
direction LR
class CrudMixin
class ModeloBase
class Questao {
  int id PK
  int assunto_id FK
  int versao_publicada_id FK opcional
  string status
  int revisao
  text enunciado
  text alternativa_a_ate_e
  char resposta_correta
  string dificuldade
}
class QuestaoVersao {
  int id PK
  int questao_id FK
  int numero
  int revisao_origem
  string estado
  text enunciado
  text alternativa_a_ate_e
  char resposta_correta
  text explicacao opcional
  int assunto_id FK
  int materia_id FK
  int area_enem_id FK
  int ator_id FK opcional
  string origem
}
class QuestaoEvento {
  bigint id PK
  int questao_id FK
  int versao_id FK opcional
  int ator_id FK opcional
  string acao
  string motivo
}
class PraticaTentativa {
  bigint id PK
  int usuario_id FK
  int questao_versao_id FK
  int assunto_id FK
  int materia_id FK
  string chave_envio
  string estado
  char resposta_escolhida opcional
  bool correta opcional
  datetime respondida_em opcional
}
CrudMixin <|-- Questao
ModeloBase <|-- QuestaoVersao
ModeloBase <|-- QuestaoEvento
CrudMixin <|-- PraticaTentativa
Assunto "1" <-- "0..*" Questao : assunto_id
Questao "1" <-- "0..*" QuestaoVersao : questao_id
Questao "0..*" --> "0..1" QuestaoVersao : versao_publicada_id
Questao "1" <-- "0..*" QuestaoEvento : questao_id
QuestaoVersao "0..1" <-- "0..*" QuestaoEvento : versao_id
Usuario "0..1" <-- "0..*" QuestaoEvento : ator_id
Usuario "0..1" <-- "0..*" QuestaoVersao : ator_id
Assunto "1" <-- "0..*" QuestaoVersao : assunto_id
Materia "1" <-- "0..*" QuestaoVersao : materia_id
AreaEnem "1" <-- "0..*" QuestaoVersao : area_enem_id
Usuario "1" <-- "0..*" PraticaTentativa : usuario_id
QuestaoVersao "1" <-- "0..*" PraticaTentativa : questao_versao_id
Assunto "1" <-- "0..*" PraticaTentativa : assunto_id
Materia "1" <-- "0..*" PraticaTentativa : materia_id
```

`alternativa_a_ate_e` abrevia cinco atributos reais (`alternativa_a`, …,
`alternativa_e`). Versões e tentativas conservam nomes/classificação como
snapshots; não recalculam o passado pela taxonomia atual. Autoria editorial
fica no ator da versão/evento; não há FK de autor na identidade `Questao`.

## Simulados — sete Models

```mermaid
classDiagram
direction LR
class CrudMixin
class ModeloBase
class Simulado {
  int id PK
  int autor_id FK
  int simulado_versao_id FK opcional
  string titulo
  string estado
  int revisao
}
class SimuladoRascunhoItem {
  int id PK
  int simulado_id FK
  int questao_id FK
  int questao_versao_id FK
  int posicao
}
class SimuladoVersao {
  int id PK
  int simulado_id FK
  int autor_id FK
  string titulo
  int numero
  int revisao_origem
}
class SimuladoVersaoItem {
  int id PK
  int simulado_versao_id FK
  int questao_id FK
  int questao_versao_id FK
  int posicao
}
class SimuladoEvento {
  bigint id PK
  int simulado_id FK
  int versao_id FK opcional
  int ator_id FK
  string acao
  string motivo
}
class SimuladoTentativa {
  bigint id PK
  int usuario_id FK
  int simulado_versao_id FK
  string estado
  int revisao
  datetime finalizada_em opcional
  int total opcional
  int acertos opcional
  int erros opcional
  int em_branco opcional
  decimal percentual_acerto opcional
}
class SimuladoResposta {
  bigint id PK
  bigint tentativa_id FK
  int item_id FK
  char alternativa opcional
  bool correta opcional
}
CrudMixin <|-- Simulado
CrudMixin <|-- SimuladoRascunhoItem
ModeloBase <|-- SimuladoVersao
ModeloBase <|-- SimuladoVersaoItem
ModeloBase <|-- SimuladoEvento
CrudMixin <|-- SimuladoTentativa
CrudMixin <|-- SimuladoResposta
Usuario "1" <-- "0..*" Simulado : autor_id
Simulado "1" <-- "0..*" SimuladoRascunhoItem : simulado_id
Questao "1" <-- "0..*" SimuladoRascunhoItem : questao_id
QuestaoVersao "1" <-- "0..*" SimuladoRascunhoItem : questao_versao_id
Simulado "1" <-- "0..*" SimuladoVersao : simulado_id
Usuario "1" <-- "0..*" SimuladoVersao : autor_id
Simulado "0..*" --> "0..1" SimuladoVersao : simulado_versao_id
SimuladoVersao "1" <-- "0..*" SimuladoVersaoItem : simulado_versao_id
Questao "1" <-- "0..*" SimuladoVersaoItem : questao_id
QuestaoVersao "1" <-- "0..*" SimuladoVersaoItem : questao_versao_id
Simulado "1" <-- "0..*" SimuladoEvento : simulado_id
SimuladoVersao "0..1" <-- "0..*" SimuladoEvento : versao_id
Usuario "1" <-- "0..*" SimuladoEvento : ator_id
Usuario "1" <-- "0..*" SimuladoTentativa : usuario_id
SimuladoVersao "1" <-- "0..*" SimuladoTentativa : simulado_versao_id
SimuladoTentativa "1" <-- "0..*" SimuladoResposta : tentativa_id
SimuladoVersaoItem "1" <-- "0..*" SimuladoResposta : item_id
```

Composição editorial publicada possui 1–180 itens; durante a construção do
rascunho o conjunto pode estar vazio. Cada tentativa inicializada tem uma
resposta por item, inicialmente com alternativa/correção nulas. O diagrama
mostra as cardinalidades das FKs; regras dos Services acrescentam esses limites.

## Plano — duas Models

```mermaid
classDiagram
direction LR
class ModeloAtualizavel
class PlanoEstudo {
  bigint id PK
  int usuario_id FK
  bigint plano_anterior_id FK opcional
  int geracao
  bool atual
  JSON periodo
  string operacao
  string chave_envio
  datetime gerado_em
}
class PlanoEstudoItem {
  bigint id PK
  bigint plano_id FK
  int assunto_id FK
  int materia_id FK
  int posicao
  JSON snapshot
  string estado
  datetime concluido_em opcional
}
ModeloAtualizavel <|-- PlanoEstudo
ModeloAtualizavel <|-- PlanoEstudoItem
Usuario "1" <-- "0..*" PlanoEstudo : usuario_id
PlanoEstudo "0..*" --> "0..1" PlanoEstudo : plano_anterior_id
PlanoEstudo "1" <-- "0..*" PlanoEstudoItem : plano_id
Assunto "1" <-- "0..*" PlanoEstudoItem : assunto_id
Materia "1" <-- "0..*" PlanoEstudoItem : materia_id
```

O Service gera até três prioridades com base suficiente. Cada Aluno tem no
máximo um plano atual, protegido pelo índice de `usuario_atual` calculado.
Recálculo cria nova geração; anterior e snapshots permanecem preservados.

## Semântica dos vínculos

Usamos associações com cardinalidade, sem diamantes de composição/agregação:
as FKs são `RESTRICT`, não exclusão em cascata. Itens pertencem semanticamente
a uma composição/plano e não são compartilhados como objetos mutáveis, mas o
histórico deve sobreviver a arquivamento. Isso não autoriza exclusão destrutiva.
`Desempenho` é projeção de respostas concluídas via Repository; não existe uma
Model ou tabela fictícia com esse nome. Segredos não são valores de exemplo no
diagrama: aparecem apenas os nomes dos atributos de hash já implementados.


## Aplicação: consultas compostas

```mermaid
classDiagram
class Factory
class Composicao
class MateriaController
class AssuntoController
class ListarMateriasAdminService
class ListarAssuntosAdminService
class ConsultaMateriasAdmin {
  <<interface>>
  listar(filtros, pagina, limite)
}
class ConsultaAssuntosAdmin {
  <<interface>>
  listar(filtros, pagina, limite)
}
class ConsultaMateriasMySQL
class ConsultaAssuntosMySQL
Factory --> Composicao : cria por aplicação
MateriaController --> ListarMateriasAdminService
AssuntoController --> ListarAssuntosAdminService
Composicao --> ListarMateriasAdminService
Composicao --> ListarAssuntosAdminService
ListarMateriasAdminService --> ConsultaMateriasAdmin
ListarAssuntosAdminService --> ConsultaAssuntosAdmin
ConsultaMateriasAdmin <|.. ConsultaMateriasMySQL
ConsultaAssuntosAdmin <|.. ConsultaAssuntosMySQL
```


```mermaid
classDiagram
Composicao --> BuscarQuestoesPorAssuntoService
Composicao --> ListarQuestoesAlunoService
QuestaoController --> BuscarQuestoesPorAssuntoService
PraticaController --> ListarQuestoesAlunoService
BuscarQuestoesPorAssuntoService --> ConsultaQuestoesPorAssunto
BuscarQuestoesPorAssuntoService --> ExistenciaAssunto : Callable int para bool
Composicao --> Assunto : liga buscar_por_id à existência
ListarQuestoesAlunoService --> ConsultaQuestoesElegiveis
ConsultaQuestoesPorAssunto <|.. ConsultaQuestoesPorAssuntoMySQL
ConsultaQuestoesElegiveis <|.. ConsultaQuestoesElegiveisMySQL
```

```mermaid
classDiagram
Composicao --> ListarSimuladosAlunoService
Composicao --> ListarHistoricoSimuladosService
SimuladoController --> ListarSimuladosAlunoService
SimuladoController --> ListarHistoricoSimuladosService
ListarSimuladosAlunoService --> ConsultaCatalogoSimulados
ListarSimuladosAlunoService --> ConsultaElegibilidadeVersoes
ListarHistoricoSimuladosService --> ConsultaHistoricoSimulados
ConsultaCatalogoSimulados <|.. ConsultaCatalogoSimuladosMySQL
ConsultaHistoricoSimulados <|.. ConsultaHistoricoSimuladosMySQL
ConsultaElegibilidadeVersoes <|.. ConsultarVersoesElegiveisService
```

```mermaid
classDiagram
Composicao --> ConsultarDesempenhoService
Composicao --> ConsultarDashboardAlunoService
Composicao --> ConsultarDashboardAdminService
DesempenhoController --> ConsultarDesempenhoService
DesempenhoController --> ConsultarDashboardAlunoService
DesempenhoController --> ConsultarDashboardAdminService
ConsultarDesempenhoService --> ConsultaMetricasDesempenho
ConsultarDesempenhoService --> EscoposLeitura
ConsultarDashboardAlunoService --> DiagnosticoAluno
ConsultarDashboardAlunoService --> ConsultaAtividadesAluno
ConsultarDashboardAlunoService --> EscoposLeitura
ConsultarDashboardAdminService --> ConsultaContagensAdmin
ConsultarDashboardAdminService --> EscoposLeitura
DiagnosticoAluno <|.. ConsultarDesempenhoService
ConsultaMetricasDesempenho <|.. ConsultaMetricasMySQL
ConsultaAtividadesAluno <|.. ConsultaAtividadesMySQL
ConsultaContagensAdmin <|.. ConsultaContagensMySQL
EscoposLeitura <|.. EscoposLeituraMySQL
EscoposLeituraMySQL --> ContextoLeitura : delega usar
```

```mermaid
classDiagram
PlanoEstudoController --> GerarPlanoService
PlanoEstudoController --> RecalcularPlanoService
Composicao --> GerarPlanoService
Composicao --> RecalcularPlanoService
GerarPlanoService --> SelecionarPlanoService : passado a gerar
RecalcularPlanoService --> SelecionarPlanoService : mesmo seletor
SelecionarPlanoService --> DiagnosticoAluno
DiagnosticoAluno <|.. ConsultarDesempenhoService
GerarPlanoService --> TransactionManager
RecalcularPlanoService --> TransactionManager
```

As nove consultas são instâncias com dependências obrigatórias. A factory compõe
os adaptadores por aplicação; o acessor fica na camada HTTP. Diagramas de aplicação
mostram as ligações do recorte, sem prometer abstração das demais escritas.
Dashboard e seleção do plano recebem a mesma instância do diagnóstico. Os
contratos não oferecem conexão/SQL; ContextoLeitura fica na infraestrutura.
