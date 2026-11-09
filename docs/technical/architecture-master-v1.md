# Arquitetura Mestre v1 — Plataforma ENEM

## 1. Objetivo e princípios

Este documento define limites preliminares para a evolução do MVP em um Monólito Modular. Ele não autoriza criação de schema, endpoints ou código e não substitui decisões que permanecem abertas.

Princípios:

- `main` deve permanecer estável;
- cada funcionalidade deve ser entregue ponta a ponta;
- preservar `Route → Controller → Service → Model/Repository → MySQL`;
- regras de negócio pertencem ao módulo responsável e aos seus Services;
- módulos colaboram por contratos explícitos, identificadores públicos, eventos ou Services de aplicação;
- nenhum módulo acessa diretamente tabelas internas de outro módulo sem contrato aprovado;
- evolução do banco ocorre por migrations versionadas e preservação dos dados atuais;
- contratos do MVP permanecem compatíveis durante a transição;
- menor privilégio, versionamento editorial e auditoria são requisitos transversais.

## Situação implementada — 07/11/2026

O [ADR-010](adr/ADR-010-organizacao-modular-do-backend.md) organiza o recorte
entregue em seis módulos: Contas, Conteúdo, Práticas, Simulados, Desempenho e
Plano de Estudos. As mesmas 21 Models e vinte funcionalidades permanecem.
Blueprints próprios preservam HTTP; APIs/contratos delimitam colaboração.
Ver [propriedades e interfaces](organizacao-modular.md).
As seções seguintes preservam a visão futura mais granular como roadmap;
seus módulos e entidades futuros não são declarados implementados.

## Recorte Tutor — 09/11/2026

O sétimo módulo `tutor_ia` implementa revisão pontual em `ALU-TUT-001` com Gemini,
quatro campos de estudo e resposta em quatro partes. `POST /api/tutoria` exige
Aluno, Origin/CSRF e uso 2.0. Permissão de Contas encerra a leitura antes da rede;
cliente e limite pertencem à aplicação. Não acrescenta Model, tabela, Repository
ou CRUD. As 21 Models e os vinte casos anteriores permanecem.
Abertura contextual, chat persistente, resumos e escrita no plano continuam futuros.
Ver [design](../../openspec/changes/archive/2026-11-09-adicionar-tutor-revisao-com-gemini/design.md).

## 2. Forma do Monólito Modular

A organização futura poderá adotar `backend/app/modules/<modulo>/`, mantendo dentro de cada módulo as separações exigidas pela disciplina. A estrutura exata ainda depende de aprovação; nenhuma pasta de módulo foi criada nesta etapa.

```text
app/
├── core/                         # infraestrutura compartilhada, sem negócio
├── modules/
│   ├── autenticacao/
│   ├── usuarios/
│   ├── autorizacao/
│   ├── catalogo_academico/
│   ├── questoes/
│   ├── praticas/
│   ├── simulados/
│   ├── desempenho/
│   ├── plano_estudos/
│   ├── resumos/
│   ├── redacao/
│   ├── tutor_ia/
│   ├── importacoes/
│   ├── revisao_editorial/
│   └── auditoria/
└── legacy/                       # apenas se necessário durante transição
```

## 3. Limites preliminares dos módulos

Entidades futuras abaixo são propostas de propriedade, não aprovação de schema. Seus nomes e campos permanecem sujeitos a decisões e migrations futuras.

### 3.1 autenticacao

- **Responsabilidade:** credenciais, login, logout, recuperação de senha, verificação, sessões e reautenticação.
- **Entidades que possui:** credencial, sessão, token opaco de recuperação/verificação. Nomes finais: **A definir**.
- **Casos de uso:** autenticar; encerrar/revogar sessão; solicitar recuperação neutra; redefinir senha; reautenticar ação crítica.
- **Telas:** PUB-AUT-001 a PUB-AUT-005; ações de segurança em ALU-PER-001 e ADM-USU-002.
- **Dependências permitidas:** `usuarios` por identificador estável; `autorizacao` para emissão de contexto; adaptador de e-mail; `auditoria` por evento.
- **Dependências proibidas:** conteúdo acadêmico, tentativas, redações ou tabelas internas desses módulos.
- **Eventos:** sessão criada/revogada; recuperação solicitada/concluída; senha alterada; falha ou bloqueio relevante.
- **Repository/Procedure provável:** revogação/consulta de sessões e tokens, quando a operação deixar de ser CRUD simples.
- **Model/CRUD:** credenciais, tokens, sessões individuais.
- **Serviços externos:** e-mail transacional.

### 3.2 usuarios

- **Responsabilidade:** conta, perfil do aluno, preferências, disponibilidade, consentimentos e ciclo de vida da conta.
- **Entidades que possui:** usuário, perfil, preferência, disponibilidade, consentimento. Nomes finais: **A definir**.
- **Casos de uso:** cadastrar conta; concluir onboarding; editar perfil; consultar usuário; solicitar exclusão/anonimização.
- **Telas:** ALU-ONB-001 a 003, ALU-PER-001, ADM-USU-001 e ADM-USU-002.
- **Dependências permitidas:** `autenticacao`, `autorizacao`, `catalogo_academico`, `plano_estudos` e `auditoria` por contrato.
- **Dependências proibidas:** alterar diretamente sessões, respostas, tentativas ou conteúdo editorial.
- **Eventos:** usuário criado; onboarding concluído; perfil alterado; exclusão solicitada/concluída; consentimento alterado.
- **Repository/Procedure provável:** busca administrativa, exportação do titular e anonimização coordenada.
- **Model/CRUD:** perfil, preferências e disponibilidade.
- **Serviços externos:** e-mail e armazenamento somente quando necessários ao perfil.

### 3.3 autorizacao

- **Responsabilidade:** papéis, permissões, escopos e decisão de acesso sob menor privilégio.
- **Entidades que possui:** papel, permissão, concessão e escopo. Nomes finais: **A definir**.
- **Casos de uso:** calcular permissões efetivas; conceder/revogar acesso; impedir elevação superior ao operador; exigir reautenticação.
- **Telas:** ADM-SEG-001 e controles de permissão em todas as telas administrativas.
- **Dependências permitidas:** `usuarios`, `autenticacao` e `auditoria`.
- **Dependências proibidas:** implementar regras editoriais ou alterar conteúdo em nome de outro módulo.
- **Eventos:** papel concedido/revogado; tentativa negada; permissão efetiva alterada.
- **Repository/Procedure provável:** cálculo de permissões efetivas e consultas hierárquicas.
- **Model/CRUD:** papéis, permissões e concessões simples.
- **Serviços externos:** nenhum previsto.

### 3.4 catalogo_academico

- **Responsabilidade:** áreas, matérias, assuntos, taxonomia e vínculos acadêmicos.
- **Entidades que possui:** `Materia` e `Assunto` existentes; Área e demais classificações: **A definir**.
- **Casos de uso:** manter catálogo; pesquisar e filtrar; validar vínculo; informar impacto; ativar/arquivar conforme política.
- **Telas:** ADM-CON-001, ADM-CON-002 e seletores/filtros acadêmicos de Aluno e Administração.
- **Dependências permitidas:** `autorizacao`, `revisao_editorial` quando o catálogo ganhar governança e `auditoria`.
- **Dependências proibidas:** excluir ou alterar diretamente Questões, Práticas, Simulados ou Resumos.
- **Eventos:** matéria/assunto criado ou alterado; vínculo alterado; item arquivado.
- **Repository/Procedure provável:** contagens de vínculos, impacto de exclusão, filtros e relatórios.
- **Model/CRUD:** cadastro, listagem e atualização simples de Matéria/Assunto.
- **Serviços externos:** nenhum previsto.

### 3.5 questoes

- **Responsabilidade:** conteúdo da Questão, alternativas, gabarito, explicação, classificação, origem, mídia, versões e elegibilidade.
- **Entidades que possui:** `Questao` existente; versão, mídia, origem, classificação e alerta: **A definir**.
- **Casos de uso:** criar rascunho; editar; consultar; classificar; versionar; arquivar; verificar duplicidade; disponibilizar versão publicada.
- **Telas:** ADM-QUE-001, ADM-QUE-002, ADM-QUE-006 a 010; fornece conteúdo para ALU-QUE e Simulados.
- **Dependências permitidas:** `catalogo_academico`, `autorizacao`, `revisao_editorial`, `importacoes`, armazenamento de arquivos e `auditoria`.
- **Dependências proibidas:** alterar resposta/tentativa do aluno ou publicar sem decisão editorial válida.
- **Eventos:** questão criada/versionada; enviada à revisão; publicada; arquivada; duplicidade sinalizada.
- **Repository/Procedure provável:** busca filtrada, similaridade, elegibilidade, lotes, rankings e `sp_questoes_por_assunto` existente.
- **Model/CRUD:** rascunho, metadados, alternativas e mídia simples.
- **Serviços externos:** LLM somente por Service específico do caso de geração; armazenamento de mídia.

### 3.6 praticas

- **Responsabilidade:** montagem de prática, sequência, resposta do aluno, feedback e continuidade.
- **Entidades que possui:** prática, item da prática, resposta e progresso. Nomes finais: **A definir**.
- **Casos de uso:** montar prática; continuar; responder; corrigir; mostrar resultado; praticar pontos fracos/erros/oficiais.
- **Telas:** ALU-QUE-001, ALU-QUE-002 e ALU-QUE-003.
- **Dependências permitidas:** leitura de versões publicadas de `questoes`; `usuarios`; `catalogo_academico`; publicação de eventos para `desempenho` e `plano_estudos`.
- **Dependências proibidas:** modificar Questões publicadas ou calcular permissões administrativas.
- **Eventos:** prática iniciada/concluída; resposta registrada/corrigida; assunto revisado.
- **Repository/Procedure provável:** seleção orientada, erros anteriores, pontos fracos, recomendação e continuidade.
- **Model/CRUD:** prática e respostas individuais.
- **Serviços externos:** nenhum obrigatório.

### 3.7 simulados

- **Responsabilidade:** definição, composição, regras dinâmicas, versões, disponibilidade, tentativa, cronômetro, resultado e correção.
- **Entidades que possui:** simulado, versão, item, regra, agendamento, tentativa e resposta. Nomes finais: **A definir**.
- **Casos de uso:** criar composição manual/fixa/dinâmica/oficial; revisar/publicar; iniciar/finalizar tentativa; corrigir; preservar versão respondida.
- **Telas:** ALU-SIM-001 a 004, ADM-SIM-001 a 006 e ADM-SIM-M001.
- **Dependências permitidas:** `questoes` por versão publicada; `catalogo_academico`; `usuarios`; `autorizacao`; `revisao_editorial`; eventos para `desempenho`.
- **Dependências proibidas:** alterar retroativamente versão ou gabarito usado por tentativa concluída.
- **Eventos:** simulado criado/aprovado/agendado/publicado/encerrado; tentativa iniciada/finalizada; resultado disponível.
- **Repository/Procedure provável:** composição por critérios, banco elegível, distribuição, resultados e comparações.
- **Model/CRUD:** dados gerais, itens fixos, agendamento e tentativa individual.
- **Serviços externos:** relógio confiável; importação oficial por `importacoes`.

### 3.8 desempenho

- **Responsabilidade:** projeções e diagnósticos derivados de respostas, simulados e redações, sempre com base e período explícitos.
- **Entidades que possui:** leitura agregada, snapshot ou métrica materializada: **A definir**.
- **Casos de uso:** consultar desempenho; comparar períodos; identificar assunto prioritário; produzir blocos do dashboard.
- **Telas:** ALU-DASH-001, ALU-DES-001 e indicadores pertinentes do ADM-DASH-001.
- **Dependências permitidas:** consumir eventos de `praticas`, `simulados` e `redacao`; consultar catálogo e usuário por contrato.
- **Dependências proibidas:** alterar respostas/tentativas de origem ou tratar ausência de dados como zero.
- **Eventos:** diagnóstico atualizado; limiar de amostra atingido; prioridade alterada.
- **Repository/Procedure provável:** agregações, séries temporais, comparações, assuntos prioritários e rankings.
- **Model/CRUD:** snapshots/materializações, se aprovados.
- **Serviços externos:** nenhum obrigatório.

### 3.9 plano_estudos

- **Responsabilidade:** plano inicial, agenda semanal, atividades, metas, reagendamento e recálculo explicável.
- **Entidades que possui:** plano, semana, atividade, meta e disponibilidade aplicada. Nomes finais: **A definir**.
- **Casos de uso:** montar plano inicial; adicionar/mover/reagendar/concluir atividade; recalcular com segurança.
- **Telas:** ALU-ONB-001 a 003, ALU-PLA-001 e blocos do ALU-DASH-001.
- **Dependências permitidas:** `usuarios`, `catalogo_academico`, recomendações de `desempenho` e links para Práticas, Resumos, Simulados e Redação.
- **Dependências proibidas:** alterar registros internos das atividades de destino.
- **Eventos:** plano criado/recalculado; atividade adicionada/concluída/atrasada/reagendada.
- **Repository/Procedure provável:** recálculo, agenda por período e priorização.
- **Model/CRUD:** plano, metas e atividades simples.
- **Serviços externos:** calendário/notificação somente após decisão futura.

### 3.10 resumos

- **Responsabilidade:** biblioteca, conteúdo estruturado, fontes, mídias, versões e progresso de leitura.
- **Entidades que possui:** resumo, versão, seção, fonte, mídia e progresso. Nomes finais: **A definir**.
- **Casos de uso:** criar/editar/revisar/publicar; buscar; ler; salvar; concluir; iniciar prática contextual.
- **Telas:** ALU-RES-001, ALU-RES-002, ADM-RES-001 a 003.
- **Dependências permitidas:** `catalogo_academico`, `autorizacao`, `revisao_editorial`, armazenamento e links para `praticas`/`plano_estudos`.
- **Dependências proibidas:** publicar sem revisão ou alterar a versão já usada em histórico.
- **Eventos:** resumo versionado/publicado/arquivado; progresso alterado.
- **Repository/Procedure provável:** busca, filtros, recomendações e pontos fracos.
- **Model/CRUD:** rascunho, seções, fontes, mídia e progresso.
- **Serviços externos:** armazenamento; LLM somente para sugestão governada.

### 3.11 redacao

- **Responsabilidade:** temas, textos do aluno, versões, submissões, correções automatizadas/humanas e competências C1-C5.
- **Entidades que possui:** tema, motivador, fonte, redação, versão, submissão, correção e competência. Nomes finais: **A definir**.
- **Casos de uso:** manter temas; salvar rascunho; enviar; corrigir; reescrever; consultar histórico; revisar/invalidar/reprocessar correção.
- **Telas:** ALU-RED-001 a 004, ADM-TEM-001 a 005 e ADM-RED-001 a 003.
- **Dependências permitidas:** `usuarios`, `catalogo_academico`, `autorizacao`, `revisao_editorial`, `importacoes`, serviço de correção e `auditoria`.
- **Dependências proibidas:** alterar texto original após envio ou expor texto integral a perfil sem permissão.
- **Eventos:** redação enviada; correção enfileirada/concluída/falhou; revisão humana iniciada/concluída; correção invalidada.
- **Repository/Procedure provável:** filas, histórico, métricas por competência, monitoramento e relatórios.
- **Model/CRUD:** tema, rascunho, versão, submissão e correção individual.
- **Serviços externos:** correção/LLM, moderação e armazenamento.

### 3.12 tutor_ia

- **Responsabilidade:** conversa contextual, políticas pedagógicas de resposta e rastreabilidade do uso de IA.
- **Entidades que possui:** conversa, mensagem, contexto, consumo e feedback. Nomes finais: **A definir**.
- **Casos de uso:** enviar dúvida; explicar de outro modo; exemplificar; retornar ao contexto; lidar com limite/timeout.
- **Telas:** ALU-TUT-001; integrações contextuais em Questões, Resumos e Plano.
- **Dependências permitidas:** contexto autorizado de `usuarios`, `catalogo_academico`, `questoes`, `resumos` e `plano_estudos`; cliente de LLM compartilhado.
- **Dependências proibidas:** publicar conteúdo editorial ou alterar desempenho sem evento/contrato explícito.
- **Eventos:** conversa criada; resposta concluída/falhou; limite atingido; conteúdo inadequado sinalizado.
- **Repository/Procedure provável:** histórico contextual e análise de consumo; não para chamadas ao LLM.
- **Model/CRUD:** conversa, mensagens e feedback.
- **Serviços externos:** provedor de LLM e moderação.

### 3.13 importacoes

- **Responsabilidade:** upload, identificação, processamento, retomada e validação preliminar de arquivos/lotes.
- **Entidades que possui:** lote, arquivo, item extraído, erro e checkpoint. Nomes finais: **A definir**.
- **Casos de uso:** importar prova/gabarito; importar tema; acompanhar; cancelar restante; retomar; validar itens.
- **Telas:** ADM-QUE-003 a 005 e ADM-TEM-003.
- **Dependências permitidas:** armazenamento; `catalogo_academico`; contratos de ingestão de `questoes` e `redacao`; `auditoria`.
- **Dependências proibidas:** publicar automaticamente ou contornar revisão editorial.
- **Eventos:** lote criado/processado/parcial/interrompido/concluído; item validado/rejeitado.
- **Repository/Procedure provável:** conciliação de gabarito, duplicidade, progresso, retomada e relatórios de lote.
- **Model/CRUD:** lote, arquivos, checkpoints e erros.
- **Serviços externos:** OCR/extrator, armazenamento e eventualmente serviços oficiais.

### 3.14 revisao_editorial

- **Responsabilidade:** fila, atribuição, checklist, comentários, decisão, aprovação, publicação e histórico editorial.
- **Entidades que possui:** revisão, checklist, comentário, decisão, atribuição e transição. Nomes finais: **A definir**.
- **Casos de uso:** enviar para revisão; atribuir; solicitar ajustes; aprovar; rejeitar; publicar; agir em lote elegível.
- **Telas:** ADM-QUE-009/010, ADM-SIM-006, ADM-RES-003, ADM-TEM-005 e revisão humana em ADM-RED-003.
- **Dependências permitidas:** contratos editoriais de Questões, Simulados, Resumos e Redação; `autorizacao`; `auditoria`.
- **Dependências proibidas:** editar diretamente tabelas internas do conteúdo ou aprovar sem permissão/checklist.
- **Eventos:** revisão solicitada/atribuída; ajustes solicitados; conteúdo aprovado/rejeitado/publicado/arquivado.
- **Repository/Procedure provável:** fila, elegibilidade em lote, SLA e pendências.
- **Model/CRUD:** revisão individual, checklist, comentários e decisão.
- **Serviços externos:** notificações/e-mail quando aprovados.

### 3.15 auditoria

- **Responsabilidade:** registro imutável e consulta de eventos administrativos e ações críticas.
- **Entidades que possui:** evento de auditoria, correlação e registro de exportação. Nomes finais: **A definir**.
- **Casos de uso:** registrar evento; consultar; filtrar; abrir detalhe; exportar com minimização.
- **Telas:** ADM-AUD-001 e trilhas das ações críticas em todos os módulos.
- **Dependências permitidas:** consumir eventos publicados pelos demais módulos; `autorizacao` para consulta/exportação.
- **Dependências proibidas:** executar ou reverter ações de negócio; armazenar senha, token, chave ou conteúdo sensível desnecessário.
- **Eventos:** a auditoria consome eventos; a própria exportação também gera evento auditável.
- **Repository/Procedure provável:** filtros complexos, antes/depois, correlação, retenção e exportação.
- **Model/CRUD:** gravação append-only de evento individual.
- **Serviços externos:** armazenamento seguro de exportação quando aprovado.

## 4. Núcleo compartilhado

O núcleo contém infraestrutura reutilizável, nunca regras específicas de Matéria, Questão, Simulado, Redação ou outro domínio.

| Capacidade | Pode ficar no núcleo | Deve permanecer no módulo |
| --- | --- | --- |
| Extensions | Instâncias de SQLAlchemy, CORS e futuras extensões | Decisão de quando usar cada extensão |
| Config | Leitura e validação de ambiente | Parâmetros de negócio |
| Erros | Tipos base, serialização HTTP e correlação | Mensagem e causa do caso de uso |
| Autenticação da requisição | Extração/verificação técnica da identidade | Login, recuperação e políticas de sessão em `autenticacao` |
| Autorização | Mecanismo de enforcement e decorators/adapters | Papéis, concessões e decisões em `autorizacao` |
| Validações | Primitivas como texto obrigatório, ID positivo e paginação | Regras contextuais e invariantes do módulo |
| Serialização | Convenções de envelope, data e paginação | Campos expostos por recurso |
| Logging | Formato, correlação e redaction | Eventos de negócio relevantes |
| Transações | Contexto/unit of work e rollback técnico | Limites atômicos definidos pelo Service do caso de uso |
| Datas | Relógio injetável, timezone e conversões | Regras de prazo e período |
| E-mail | Cliente/adaptador e entrega | Destinatário, template e momento definidos pelo módulo |
| LLM | Cliente, timeout, retry e métricas | Prompt, contexto, validação e governança definidos pelo módulo |
| Arquivos | Interface de armazenamento, checksum e acesso | Tipos permitidos, retenção e vínculo definidos pelo módulo |

O núcleo não pode se transformar em uma pasta genérica de “helpers” com dependências circulares ou regras de negócio compartilhadas por conveniência.

## 5. Regras obrigatórias de dependência

1. Routes registram URLs e chamam Controllers.
2. Controllers interpretam HTTP, chamam Services e serializam respostas.
3. Controllers não acessam `db.session`, SQL, procedure ou integração externa.
4. Cada caso de uso possui Service próprio.
5. Services validam e coordenam Models, Repositories e Services externos específicos.
6. Services não executam SQL nem `CALL`.
7. CRUD simples permanece na Model/Active Record.
8. Consultas complexas, filtros avançados, agregações, relatórios e procedures usam Repository.
9. Todo `CALL` permanece exclusivamente em Repository.
10. Repository não repete CRUD simples.
11. Integração externa fica atrás de Service/adapter específico do caso de uso.
12. Um módulo não acessa tabela interna de outro módulo sem contrato aprovado.
13. Frontend consome API e nunca acessa banco.
14. A autorização é aplicada no servidor; ocultar botão não concede segurança.
15. Ações críticas exigem confirmação, motivo, reautenticação quando prevista e auditoria.
16. Conteúdo usado em tentativa/submissão preserva a versão histórica.
17. Eventos entre módulos carregam somente dados necessários e identificadores estáveis.

## 6. Perfis e menor privilégio

| Perfil | Ambientes | Visualização | Criação/edição | Revisão/aprovação/publicação | Exportação e ações críticas |
| --- | --- | --- | --- | --- | --- |
| Público | Público/Autenticação | Páginas públicas e link seguro recebido | Própria conta e própria senha com link válido | Não permitido | Não permitido |
| Aluno | Aluno | Próprios dados e conteúdos publicados | Respostas, redações, preferências, perfil e rascunhos próprios | Apenas próprio histórico; sem aprovação/publicação | Próprios dados quando permitido; conta própria com reautenticação |
| Visualizador | Administração | Metadados do escopo; sem texto integral de Redação por padrão | Não permitido | Não permitido | Somente permissão explícita; sem ação crítica |
| Editor de conteúdo | Administração | Conteúdo e metadados permitidos | Cria e edita conteúdo, inclusive ajustes | Envia à revisão; não decide aprovação/publicação | Não por padrão |
| Revisor | Administração | Filas e conteúdos autorizados; texto integral de Redação apenas quando autorizado | Ajustes com histórico conforme regra | Revisa, aprova e publica quando autorizado | Exporta apenas com permissão; pode invalidar correção com motivo |
| Administrador completo | Aluno/Administração quando aplicável | Dados necessários, ainda sujeitos à privacidade | Permitido conforme módulo | Permitido | Confirmação, motivo, reautenticação, minimização e auditoria |

Regras adicionais:

- ninguém concede permissão superior à própria;
- permissões devem ser verificadas por ação e recurso, não apenas por tela;
- texto integral de Redação é dado restrito;
- exportação de auditoria deve excluir senha, token, chave e conteúdo sensível desnecessário.

## 7. Estados e governança

### 7.1 Conteúdo editorial

```text
Rascunho
  → Aguardando revisão
  → Ajustes solicitados
  → Aguardando revisão
  → Aprovado
  → Publicado
  → Arquivado
```

Rejeição, bloqueio por erro/duplicidade e criação de nova versão exigem transições explícitas com motivo e histórico.

### 7.2 Simulados

```text
Rascunho
  → Aguardando revisão
  → Aprovado
  → Agendado ou Publicado
  → Encerrado ou Arquivado
```

Tentativas concluídas permanecem vinculadas à versão respondida.

### 7.3 Redações

```text
Rascunho do aluno
  → Enviada
  → Na fila
  → Em correção
  → Corrigida
  → Em revisão humana
  → Correção revisada ou invalidada
```

“Em revisão humana” funciona como indicador transversal operacional durante parte do fluxo; a modelagem definitiva dos eixos deve evitar contagem dupla.

### 7.4 Indicador transversal de duplicidade

Conforme a [Errata do Desktop V1](../design/desktop-v1/ERRATA.md), **Possível duplicidade** é um indicador transversal. Ele pode coexistir com o estado editorial/processual principal, exige decisão própria e não substitui esse estado. Exemplos válidos incluem:

- Rascunho + Possível duplicidade;
- Válida + Possível duplicidade;
- Com alerta + Possível duplicidade;
- Com erro + Possível duplicidade;
- Aguardando revisão + Possível duplicidade.

Enquanto o indicador estiver ativo, a política do módulo pode impedir ações de aprovação até uma decisão própria, sem alterar automaticamente o estado editorial/processual.

**Bloqueada por duplicidade** é diferente: trata-se de estado principal de governança, usado quando a duplicidade foi confirmada ou impede formalmente o avanço. Nesse estado, o avanço fica indisponível até resolução explícita.

## 8. Relação entre MVP e arquitetura futura

### A. Permanece inicialmente

- application factory;
- `extensions` e `config`;
- exceções atuais;
- Models `Materia`, `Assunto` e `Questao`;
- Controllers e Services existentes;
- `QuestaoRepository`;
- `sp_questoes_por_assunto`;
- 29 testes de integração.

### B. Migração gradual

- `routes.py` único para Blueprints por módulo;
- camadas globais para limites modulares;
- validações duplicadas para schemas/validadores reutilizáveis;
- tratamento repetido de erros para handlers comuns;
- migrations SQL manuais para mecanismo versionado aprovado;
- commits internos do `CrudMixin` para limites transacionais coordenáveis.

### C. Substituição na versão definitiva

- frontend de página única;
- CSS atual;
- estado distribuído por eventos globais;
- URL fixa da API;
- composição visual do MVP.

A substituição do frontend não exige reescrita imediata do backend. Endpoints existentes devem continuar operacionais até que consumidores tenham migrado e a descontinuação seja aprovada.

## 9. Critérios para criação de um módulo

Um módulo só deve avançar para implementação quando possuir:

- telas e casos de uso associados;
- perfis e permissões definidos;
- entidades e propriedade de dados aprovadas;
- estados e transições definidos;
- dependências permitidas/proibidas registradas;
- estratégia de migration e preservação de dados;
- contratos HTTP ou eventos revisados;
- testes de aceitação e regressão planejados;
- decisões abertas bloqueantes resolvidas.
