# Mapa funcional-técnico das telas — Desktop V1

## Escopo e fontes

Este documento relaciona as 60 telas oficiais do Desktop V1 a casos de uso e limites técnicos preliminares. A fonte canônica de IDs, nomes, perfis, objetivos, entradas, ações, destinos, dependências, estados e aprovação é o Inventário Mestre. O Handoff Mestre e o Protótipo foram usados para validar navegação, governança e composição visual. A arquitetura atual do MVP foi confrontada diretamente com o código em `backend/app` e `frontend`.

Regras de interpretação:

- campos não definidos pelas fontes permanecem como **A definir**;
- URLs novas não são inventadas e usam **NOVO — contrato ainda será definido**;
- “entidades” futuras são tratadas como conceitos preliminares até aprovação de schema;
- os contratos atuais do MVP permanecem compatíveis durante a evolução;
- aprovação visual não significa funcionalidade já implementada.

Regra de governança corrigida pela [Errata do Desktop V1](../design/desktop-v1/ERRATA.md):

- **Possível duplicidade** é indicador transversal, pode coexistir com o estado editorial/processual principal, exige decisão própria e pode impedir uma ação de aprovação conforme a política; não substitui o estado principal;
- **Bloqueada por duplicidade** é estado principal de governança, torna o avanço indisponível e exige resolução explícita.

## Resumo

| Ambiente | Telas |
| --- | ---: |
| Público | 5 |
| Aluno | 21 |
| Administração | 34 |
| **Total** | **60** |

## Mapa das telas

### 1. PUB-AUT-001 — Login

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `PUB-AUT-001` |
| Ambiente | Público |
| Módulo funcional oficial | Autenticação |
| Módulo técnico preliminar | `autenticacao` |
| Nome oficial | Login |
| Perfil autorizado | Público |
| Objetivo | Autenticar usuário existente. |
| Caso de uso principal | Entrar — Autenticar usuário existente. |
| Casos de uso secundários | Esqueci minha senha; Criar uma conta |
| Ponto de entrada | URL pública ou sessão expirada |
| Destino principal | ALU-DASH-001 |
| Dados necessários | e-mail; senha; sessão; política de acesso |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: e-mail; senha; sessão; política de acesso. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo de e-mail quando aplicável. |
| Permissões necessárias | Perfil oficial: **Público**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; e-mail inválido; credenciais inválidas; loading; erro; sucesso; botão desabilitado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Entrar** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-DASH-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_02_Login_1440px.png`. |

### 2. PUB-AUT-002 — Cadastro

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `PUB-AUT-002` |
| Ambiente | Público |
| Módulo funcional oficial | Autenticação |
| Módulo técnico preliminar | `autenticacao` |
| Nome oficial | Cadastro |
| Perfil autorizado | Público |
| Objetivo | Criar a conta inicial sem antecipar preferências de estudo. |
| Caso de uso principal | Criar minha conta — Criar a conta inicial sem antecipar preferências de estudo. |
| Casos de uso secundários | Entrar |
| Ponto de entrada | Login ou URL pública |
| Destino principal | ALU-ONB-001 |
| Dados necessários | nome; e-mail; senha; aceite aplicável |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: nome; e-mail; senha; aceite aplicável. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo de e-mail quando aplicável. |
| Permissões necessárias | Perfil oficial: **Público**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; inválido; e-mail duplicado; loading; erro; sucesso; senha divergente |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Criar minha conta** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-ONB-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_03_Cadastro_1440px.png`. |

### 3. PUB-AUT-003 — Recuperar senha

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `PUB-AUT-003` |
| Ambiente | Público |
| Módulo funcional oficial | Autenticação |
| Módulo técnico preliminar | `autenticacao` |
| Nome oficial | Recuperar senha |
| Perfil autorizado | Público |
| Objetivo | Solicitar instruções sem revelar a existência da conta. |
| Caso de uso principal | Enviar instruções — Solicitar instruções sem revelar a existência da conta. |
| Casos de uso secundários | Voltar ao login |
| Ponto de entrada | Login |
| Destino principal | PUB-AUT-004 |
| Dados necessários | e-mail; limite de reenvio; serviço de e-mail |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: e-mail; limite de reenvio; serviço de e-mail. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD + serviço externo de e-mail. |
| Permissões necessárias | Perfil oficial: **Público**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; e-mail inválido; loading; erro de envio; sucesso |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar instruções** somente ao perfil autorizado; preservar contexto e encaminhar para **PUB-AUT-004**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_04_Recuperar_Senha_1440px.png`. |

### 4. PUB-AUT-004 — Confirmação de recuperação

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `PUB-AUT-004` |
| Ambiente | Público |
| Módulo funcional oficial | Autenticação |
| Módulo técnico preliminar | `autenticacao` |
| Nome oficial | Confirmação de recuperação |
| Perfil autorizado | Público |
| Objetivo | Confirmar o processamento de forma neutra e segura. |
| Caso de uso principal | Voltar ao login — Confirmar o processamento de forma neutra e segura. |
| Casos de uso secundários | Reenviar quando disponível |
| Ponto de entrada | PUB-AUT-003 |
| Destino principal | PUB-AUT-005 ou PUB-AUT-001 |
| Dados necessários | e-mail mascarado; contador de reenvio |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: e-mail mascarado; contador de reenvio. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Sem persistência direta de tela; leitura de token/contador por Service. |
| Permissões necessárias | Perfil oficial: **Público**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Enviado; reenvio bloqueado; reenviando; erro; sucesso |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Voltar ao login** somente ao perfil autorizado; preservar contexto e encaminhar para **PUB-AUT-005 ou PUB-AUT-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_04B_Confirmacao_Recuperacao_1440px.png`. |

### 5. PUB-AUT-005 — Definir nova senha

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `PUB-AUT-005` |
| Ambiente | Público |
| Módulo funcional oficial | Autenticação |
| Módulo técnico preliminar | `autenticacao` |
| Nome oficial | Definir nova senha |
| Perfil autorizado | Público com link seguro válido |
| Objetivo | Definir uma nova senha e concluir a recuperação sem expor dados da conta. |
| Caso de uso principal | Redefinir senha — Definir uma nova senha e concluir a recuperação sem expor dados da conta. |
| Casos de uso secundários | Mostrar/ocultar; voltar ao Login; solicitar novo link |
| Ponto de entrada | Link seguro recebido por e-mail |
| Destino principal | PUB-AUT-001 ou PUB-AUT-003 |
| Dados necessários | token opaco; validade; uso do link; política de senha; revogação futura de sessões |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: token opaco; validade; uso do link; política de senha; revogação futura de sessões. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo de e-mail quando aplicável. |
| Permissões necessárias | Perfil oficial: **Público com link seguro válido**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Link válido; salvando; senha alterada; link inválido; link expirado; link já utilizado; erro recuperável |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Redefinir senha** somente ao perfil autorizado; preservar contexto e encaminhar para **PUB-AUT-001 ou PUB-AUT-003**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_06_Definir_Nova_Senha_1440px.png`. |

### 6. ALU-ONB-001 — Objetivo

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-ONB-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Primeiro acesso |
| Módulo técnico preliminar | `usuarios` + `plano_estudos` |
| Nome oficial | Objetivo |
| Perfil autorizado | Aluno novo |
| Objetivo | Registrar o objetivo inicial sem prometer personalização definitiva. |
| Caso de uso principal | Continuar — Registrar o objetivo inicial sem prometer personalização definitiva. |
| Casos de uso secundários | Sair |
| Ponto de entrada | Cadastro concluído |
| Destino principal | ALU-ONB-002 |
| Dados necessários | usuário; opções de objetivo; respostas temporárias |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: usuário; opções de objetivo; respostas temporárias. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Aluno novo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; selecionado; alterações não salvas; erro; loading |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Continuar** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-ONB-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_05A_Onboarding_Objetivo_1440px.png`. |

### 7. ALU-ONB-002 — Disponibilidade

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-ONB-002` |
| Ambiente | Aluno |
| Módulo funcional oficial | Primeiro acesso |
| Módulo técnico preliminar | `usuarios` + `plano_estudos` |
| Nome oficial | Disponibilidade |
| Perfil autorizado | Aluno novo |
| Objetivo | Registrar dias e tempo médio disponível. |
| Caso de uso principal | Continuar — Registrar dias e tempo médio disponível. |
| Casos de uso secundários | Voltar; Sair |
| Ponto de entrada | ALU-ONB-001 |
| Destino principal | ALU-ONB-003 |
| Dados necessários | dias; duração diária; resposta anterior |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: dias; duração diária; resposta anterior. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Aluno novo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; selecionado; inválido; alterações não salvas; erro |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Continuar** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-ONB-003**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_05B_Onboarding_Disponibilidade_1440px.png`. |

### 8. ALU-ONB-003 — Prioridades

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-ONB-003` |
| Ambiente | Aluno |
| Módulo funcional oficial | Primeiro acesso |
| Módulo técnico preliminar | `usuarios` + `plano_estudos` |
| Nome oficial | Prioridades |
| Perfil autorizado | Aluno novo |
| Objetivo | Registrar prioridades declaradas ou ausência de preferência. |
| Caso de uso principal | Montar meu plano inicial — Registrar prioridades declaradas ou ausência de preferência. |
| Casos de uso secundários | Voltar; Ainda não sei |
| Ponto de entrada | ALU-ONB-002 |
| Destino principal | ALU-DASH-001 |
| Dados necessários | matérias; respostas anteriores; plano inicial |
| Entidades envolvidas | `Materia` (existente); preferências, respostas e plano — **A definir**. |
| Endpoint | Reuso parcial: `GET /api/materias`; onboarding e plano inicial: **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Aluno novo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; selecionado; loading; erro; sucesso; alterações não salvas |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Montar meu plano inicial** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-DASH-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Parcialmente existe** — há contratos ou Models reutilizáveis, mas não a tela definitiva completa. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_05C_Onboarding_Prioridades_1440px.png`. |

### 9. ALU-DASH-001 — Dashboard do aluno

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-DASH-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Dashboard |
| Módulo técnico preliminar | `desempenho` + `plano_estudos` |
| Nome oficial | Dashboard do aluno |
| Perfil autorizado | Aluno |
| Objetivo | Responder como estou, o que precisa de atenção e o próximo passo. |
| Caso de uso principal | Continuar estudando — Responder como estou, o que precisa de atenção e o próximo passo. |
| Casos de uso secundários | Abrir módulos; prioridades; plano do dia |
| Ponto de entrada | Login, onboarding ou sidebar |
| Destino principal | Destino contextual da atividade |
| Dados necessários | métricas; período; plano; histórico; recomendações |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: métricas; período; plano; histórico; recomendações. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Repository/Procedure para agregações; Model/CRUD para preferências ou ações simples. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Loading parcial; sem dados; erro parcial; amostra pequena; sucesso |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Continuar estudando** somente ao perfil autorizado; preservar contexto e encaminhar para **Destino contextual da atividade**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Dashboard_1440px_v2.png`. |

### 10. ALU-QUE-001 — Questões

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-QUE-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `praticas` + `questoes` |
| Nome oficial | Questões |
| Perfil autorizado | Aluno |
| Objetivo | Montar ou iniciar uma prática orientada. |
| Caso de uso principal | Começar prática — Montar ou iniciar uma prática orientada. |
| Casos de uso secundários | Pontos fracos; questões erradas; oficiais; continuar prática |
| Ponto de entrada | Dashboard, sidebar, resumo ou desempenho |
| Destino principal | ALU-QUE-002 |
| Dados necessários | áreas; matérias; assuntos; dificuldade; histórico; recomendação |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | Dados parciais: `GET /api/materias`, `GET /api/assuntos` e `GET /api/questoes/por-assunto?assunto_id=<id>`; prática, resposta e resultado persistido: **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository apenas quando a consulta for especializada. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; filtros sem resultado; poucos dados; loading; erro; continuação |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Começar prática** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-QUE-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Parcialmente existe** — há contratos ou Models reutilizáveis, mas não a tela definitiva completa. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_01_Questoes_1440px.png`. |

### 11. ALU-QUE-002 — Resolver Questão

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-QUE-002` |
| Ambiente | Aluno |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `praticas` + `questoes` |
| Nome oficial | Resolver Questão |
| Perfil autorizado | Aluno |
| Objetivo | Responder com leitura confortável e progresso visível. |
| Caso de uso principal | Responder — Responder com leitura confortável e progresso visível. |
| Casos de uso secundários | Sair da prática; navegação permitida |
| Ponto de entrada | ALU-QUE-001 ou filtro contextual |
| Destino principal | ALU-QUE-003 |
| Dados necessários | questão; alternativas; mídia; classificação; posição da prática |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | Dados parciais: `GET /api/materias`, `GET /api/assuntos` e `GET /api/questoes/por-assunto?assunto_id=<id>`; prática, resposta e resultado persistido: **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository apenas quando a consulta for especializada. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Não selecionada; selecionada; loading; mídia indisponível; erro; resposta enviada |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Responder** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-QUE-003**; falhas não podem apagar dados válidos. |
| Situação atual | **Parcialmente existe** — há contratos ou Models reutilizáveis, mas não a tela definitiva completa. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_02_Resolver_Questao_1440px.png`. |

### 12. ALU-QUE-003 — Resultado da Questão

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-QUE-003` |
| Ambiente | Aluno |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `praticas` + `questoes` |
| Nome oficial | Resultado da Questão |
| Perfil autorizado | Aluno |
| Objetivo | Explicar acerto ou erro e direcionar a evolução. |
| Caso de uso principal | Próxima questão — Explicar acerto ou erro e direcionar a evolução. |
| Casos de uso secundários | Revisar assunto; abrir Tutor IA |
| Ponto de entrada | ALU-QUE-002 |
| Destino principal | ALU-QUE-002 ou ALU-RES-002 |
| Dados necessários | resposta escolhida; gabarito; explicação; impacto; assunto |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | Dados parciais: `GET /api/materias`, `GET /api/assuntos` e `GET /api/questoes/por-assunto?assunto_id=<id>`; prática, resposta e resultado persistido: **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD + processamento de importação; Repository para validações especializadas. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Correto; incorreto; loading; erro; sem impacto disponível |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Próxima questão** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-QUE-002 ou ALU-RES-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Parcialmente existe** — há contratos ou Models reutilizáveis, mas não a tela definitiva completa. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_03_Resultado_Correto_1440px.png \| output/pdf/Plataforma_ENEM_03_Resultado_Incorreto_1440px.png`. |

### 13. ALU-SIM-001 — Simulados

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-SIM-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Simulados |
| Perfil autorizado | Aluno |
| Objetivo | Escolher a modalidade de avaliação mais adequada. |
| Caso de uso principal | Iniciar simulado — Escolher a modalidade de avaliação mais adequada. |
| Casos de uso secundários | Rápido; personalizado; prova oficial; último simulado |
| Ponto de entrada | Dashboard ou sidebar |
| Destino principal | ALU-SIM-002 |
| Dados necessários | tipos; banco elegível; histórico; disponibilidade; recomendações |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: tipos; banco elegível; histórico; disponibilidade; recomendações. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Sem histórico; banco insuficiente; indisponível; loading; erro; recomendado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Iniciar simulado** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-SIM-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_01_Simulados_1440px.png`. |

### 14. ALU-SIM-002 — Realizar Simulado

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-SIM-002` |
| Ambiente | Aluno |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Realizar Simulado |
| Perfil autorizado | Aluno |
| Objetivo | Executar uma avaliação ampla com tempo e progresso controlados. |
| Caso de uso principal | Finalizar simulado — Executar uma avaliação ampla com tempo e progresso controlados. |
| Casos de uso secundários | Anterior; próxima; mapa de questões; sair |
| Ponto de entrada | ALU-SIM-001 |
| Destino principal | ALU-SIM-003 |
| Dados necessários | questões; respostas; cronômetro; configuração; versão do simulado |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: questões; respostas; cronômetro; configuração; versão do simulado. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Respondida; não respondida; tempo esgotado; salvando; erro; alterações preservadas |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Finalizar simulado** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-SIM-003**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_02_Realizar_Simulado_1440px.png`. |

### 15. ALU-SIM-003 — Resultado do Simulado

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-SIM-003` |
| Ambiente | Aluno |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Resultado do Simulado |
| Perfil autorizado | Aluno |
| Objetivo | Explicar desempenho, destaques e próximos passos. |
| Caso de uso principal | Continuar estudando — Explicar desempenho, destaques e próximos passos. |
| Casos de uso secundários | Acessar correção; revisar prioridades |
| Ponto de entrada | Finalização do simulado |
| Destino principal | ALU-SIM-004 ou ALU-PLA-001 |
| Dados necessários | tentativa; versão; acertos; áreas; comparação; recomendações |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: tentativa; versão; acertos; áreas; comparação; recomendações. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Sem comparação; amostra pequena; loading; erro; resultado disponível |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Continuar estudando** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-SIM-004 ou ALU-PLA-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_03_Resultado_Simulado_1440px.png`. |

### 16. ALU-SIM-004 — Correção do Simulado

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-SIM-004` |
| Ambiente | Aluno |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Correção do Simulado |
| Perfil autorizado | Aluno dono da tentativa |
| Objetivo | Revisar questão a questão sem alterar retroativamente a tentativa concluída. |
| Caso de uso principal | Próxima questão — Revisar questão a questão sem alterar retroativamente a tentativa concluída. |
| Casos de uso secundários | Anterior; revisar assunto; praticar semelhantes; adicionar ao plano; voltar ao resultado |
| Ponto de entrada | ALU-SIM-003 · Acessar correção |
| Destino principal | ALU-SIM-004, ALU-SIM-003, ALU-RES-002, ALU-QUE-001 ou ALU-PLA-001 |
| Dados necessários | tentativa imutável; versão do simulado; versões das questões; respostas; gabaritos; explicações; taxonomia |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: tentativa imutável; versão do simulado; versões das questões; respostas; gabaritos; explicações; taxonomia. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Aluno dono da tentativa**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Loading; falha por questão; mídia indisponível; explicação indisponível; anulada; arquivada; sem permissão; versão preservada |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Próxima questão** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-SIM-004, ALU-SIM-003, ALU-RES-002, ALU-QUE-001 ou ALU-PLA-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_04_Correcao_Simulado_1440px.png`. |

### 17. ALU-RED-001 — Central de Redação

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-RED-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Redação |
| Módulo técnico preliminar | `redacao` |
| Nome oficial | Central de Redação |
| Perfil autorizado | Aluno |
| Objetivo | Apresentar panorama e convite principal para escrever. |
| Caso de uso principal | Começar redação — Apresentar panorama e convite principal para escrever. |
| Casos de uso secundários | Abrir histórico; tema da semana; recomendação |
| Ponto de entrada | Dashboard ou sidebar |
| Destino principal | ALU-RED-002 |
| Dados necessários | redações; nota estimada; competências; tema; meta |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: redações; nota estimada; competências; tema; meta. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo para correção automatizada quando aplicável; Repository para filas/relatórios. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Sem dados; loading; erro parcial; tema indisponível; sucesso |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Começar redação** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-RED-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_01_Central_Redacao_1440px.png`. |

### 18. ALU-RED-002 — Escrever Redação

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-RED-002` |
| Ambiente | Aluno |
| Módulo funcional oficial | Redação |
| Módulo técnico preliminar | `redacao` |
| Nome oficial | Escrever Redação |
| Perfil autorizado | Aluno |
| Objetivo | Produzir texto com conforto e preservação de rascunho. |
| Caso de uso principal | Enviar para correção — Produzir texto com conforto e preservação de rascunho. |
| Casos de uso secundários | Salvar rascunho; sair sem perder; tempo opcional |
| Ponto de entrada | ALU-RED-001, histórico ou plano |
| Destino principal | ALU-RED-003 |
| Dados necessários | tema; motivadores; versão; rascunho; contador |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: tema; motivadores; versão; rascunho; contador. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo para correção automatizada quando aplicável; Repository para filas/relatórios. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; rascunho salvo; salvando; alterações não salvas; erro; envio |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar para correção** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-RED-003**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_02_Escrever_Redacao_1440px.png`. |

### 19. ALU-RED-003 — Correção da Redação

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-RED-003` |
| Ambiente | Aluno |
| Módulo funcional oficial | Redação |
| Módulo técnico preliminar | `redacao` |
| Nome oficial | Correção da Redação |
| Perfil autorizado | Aluno |
| Objetivo | Ensinar por meio da nota estimada e das cinco competências. |
| Caso de uso principal | Reescrever redação — Ensinar por meio da nota estimada e das cinco competências. |
| Casos de uso secundários | Voltar para Redação |
| Ponto de entrada | Correção concluída ou histórico |
| Destino principal | ALU-RED-002 ou ALU-RED-001 |
| Dados necessários | texto versionado; correção versionada; C1-C5; feedback; estimativa |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: texto versionado; correção versionada; C1-C5; feedback; estimativa. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo para correção automatizada quando aplicável; Repository para filas/relatórios. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Na fila; em correção; corrigida; falha; revisão humana; invalidada |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Reescrever redação** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-RED-002 ou ALU-RED-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_03_Correcao_Redacao_1440px.png`. |

### 20. ALU-RED-004 — Histórico de Redações

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-RED-004` |
| Ambiente | Aluno |
| Módulo funcional oficial | Redação |
| Módulo técnico preliminar | `redacao` |
| Nome oficial | Histórico de Redações |
| Perfil autorizado | Aluno |
| Objetivo | Consultar versões anteriores e evolução estimada. |
| Caso de uso principal | Ver devolutiva — Consultar versões anteriores e evolução estimada. |
| Casos de uso secundários | Buscar; filtrar; abrir redação |
| Ponto de entrada | Central ou Correção |
| Destino principal | ALU-RED-003 |
| Dados necessários | lista de redações; temas; datas; notas estimadas; status |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: lista de redações; temas; datas; notas estimadas; status. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo para correção automatizada quando aplicável; Repository para filas/relatórios. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; filtros sem resultado; loading; erro; sem comparação |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Ver devolutiva** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-RED-003**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_04_Historico_Redacoes_1440px.png`. |

### 21. ALU-DES-001 — Desempenho

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-DES-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Desempenho |
| Módulo técnico preliminar | `desempenho` |
| Nome oficial | Desempenho |
| Perfil autorizado | Aluno |
| Objetivo | Transformar respostas em diagnóstico acionável. |
| Caso de uso principal | Praticar assunto prioritário — Transformar respostas em diagnóstico acionável. |
| Casos de uso secundários | Adicionar ao plano; trocar aba/período; abrir resumo |
| Ponto de entrada | Dashboard ou sidebar |
| Destino principal | ALU-QUE-001, ALU-PLA-001 ou ALU-RES-002 |
| Dados necessários | respostas; período; áreas; matérias; assuntos; simulados; redações |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: respostas; período; áreas; matérias; assuntos; simulados; redações. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Repository/Procedure para agregações; Model/CRUD para preferências ou ações simples. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Sem dados; amostra pequena; sem comparação; loading; erro parcial |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Praticar assunto prioritário** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-QUE-001, ALU-PLA-001 ou ALU-RES-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_01_Desempenho_1440px.png`. |

### 22. ALU-PLA-001 — Plano de Estudos

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-PLA-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Plano de Estudos |
| Módulo técnico preliminar | `plano_estudos` |
| Nome oficial | Plano de Estudos |
| Perfil autorizado | Aluno |
| Objetivo | Organizar uma rotina semanal editável e explicável. |
| Caso de uso principal | Continuar plano de hoje — Organizar uma rotina semanal editável e explicável. |
| Casos de uso secundários | Iniciar; concluir; reagendar; mover; editar; remover; adicionar |
| Ponto de entrada | Dashboard, desempenho, resumo ou perfil |
| Destino principal | Destino do tipo de atividade |
| Dados necessários | disponibilidade; meta; agenda; desempenho; preferências; atividades |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: disponibilidade; meta; agenda; desempenho; preferências; atividades. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para recomendações e recálculo. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Plano não criado; semana vazia; concluída; atrasada; recalculado; erro sem perda |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Continuar plano de hoje** somente ao perfil autorizado; preservar contexto e encaminhar para **Destino do tipo de atividade**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_02_Plano_de_Estudos_1440px.png`. |

### 23. ALU-RES-001 — Biblioteca de Resumos

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-RES-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Resumos |
| Módulo técnico preliminar | `resumos` |
| Nome oficial | Biblioteca de Resumos |
| Perfil autorizado | Aluno |
| Objetivo | Localizar conteúdos de revisão conectados à prática. |
| Caso de uso principal | Abrir resumo — Localizar conteúdos de revisão conectados à prática. |
| Casos de uso secundários | Buscar; filtrar; continuar; salvos; pontos fracos |
| Ponto de entrada | Sidebar, desempenho ou plano |
| Destino principal | ALU-RES-002 |
| Dados necessários | catálogo; taxonomia; progresso; recomendações; plano |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: catálogo; taxonomia; progresso; recomendações; plano. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; nenhum histórico; poucos dados; filtros sem resultado; loading; erro |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Abrir resumo** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-RES-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_01_Biblioteca_Resumos_1440px.png`. |

### 24. ALU-RES-002 — Detalhe do Resumo

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-RES-002` |
| Ambiente | Aluno |
| Módulo funcional oficial | Resumos |
| Módulo técnico preliminar | `resumos` |
| Nome oficial | Detalhe do Resumo |
| Perfil autorizado | Aluno |
| Objetivo | Oferecer leitura longa e passagem direta à prática. |
| Caso de uso principal | Praticar agora — Oferecer leitura longa e passagem direta à prática. |
| Casos de uso secundários | Salvar; adicionar ao plano; concluir; anterior; seguinte; Tutor |
| Ponto de entrada | ALU-RES-001, desempenho ou plano |
| Destino principal | ALU-QUE-001 |
| Dados necessários | conteúdo versionado; índice; progresso; mídia; assunto |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: conteúdo versionado; índice; progresso; mídia; assunto. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Não iniciado; em andamento; concluído; mídia ampliada; erro; progresso salvo |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Praticar agora** somente ao perfil autorizado; preservar contexto e encaminhar para **ALU-QUE-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_02_Detalhe_Resumo_1440px.png`. |

### 25. ALU-TUT-001 — Tutor IA

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-TUT-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Tutor IA |
| Módulo técnico preliminar | `tutor_ia` |
| Nome oficial | Tutor IA |
| Perfil autorizado | Aluno |
| Objetivo | Apoiar o raciocínio preservando o contexto de estudo. |
| Caso de uso principal | Enviar dúvida — Apoiar o raciocínio preservando o contexto de estudo. |
| Casos de uso secundários | Explicar de outro jeito; exemplo; praticar; resumo; plano |
| Ponto de entrada | Sidebar ou abertura contextual |
| Destino principal | Destino contextual |
| Dados necessários | matéria; assunto; contexto de origem; conversa atual; disponibilidade da IA |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: matéria; assunto; contexto de origem; conversa atual; disponibilidade da IA. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Serviço externo + Model/CRUD para contexto e conversa. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Conversa vazia; enviando; respondendo; timeout; falha; resposta incompleta; limite |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar dúvida** somente ao perfil autorizado; preservar contexto e encaminhar para **Destino contextual**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_03_Tutor_IA_1440px.png`. |

### 26. ALU-PER-001 — Perfil

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ALU-PER-001` |
| Ambiente | Aluno |
| Módulo funcional oficial | Perfil |
| Módulo técnico preliminar | `usuarios` + `autenticacao` |
| Nome oficial | Perfil |
| Perfil autorizado | Aluno |
| Objetivo | Gerenciar conta, estudos, segurança, notificações e acessibilidade. |
| Caso de uso principal | Salvar alterações — Gerenciar conta, estudos, segurança, notificações e acessibilidade. |
| Casos de uso secundários | Trocar aba; alterar senha; revogar sessões; excluir conta |
| Ponto de entrada | Sidebar ou header |
| Destino principal | Tela atual ou ALU-PLA-001 |
| Dados necessários | conta; preferências; disponibilidade; sessões; consentimentos |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: conta; preferências; disponibilidade; sessões; consentimentos. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Aluno**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Salvando; salvo; erro sem perda; e-mail pendente; reautenticação; exclusão |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Salvar alterações** somente ao perfil autorizado; preservar contexto e encaminhar para **Tela atual ou ALU-PLA-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_04_Perfil_1440px.png`. |

### 27. ADM-DASH-001 — Dashboard Administrativo

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-DASH-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Dashboard |
| Módulo técnico preliminar | `revisao_editorial` + `auditoria` |
| Nome oficial | Dashboard Administrativo |
| Perfil autorizado | Visualizador; Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Mostrar situação operacional, pendências e ações pertinentes. |
| Caso de uso principal | Adicionar questões — Mostrar situação operacional, pendências e ações pertinentes. |
| Casos de uso secundários | Revisar pendências; criar simulado; tema; resumo |
| Ponto de entrada | Login administrativo ou troca de ambiente |
| Destino principal | ADM-QUE-M001 ou destino contextual |
| Dados necessários | indicadores; pendências; permissões; atividade; origens |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: indicadores; pendências; permissões; atividade; origens. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Repository/Procedure para agregações; Model/CRUD para preferências ou ações simples. |
| Permissões necessárias | Perfil oficial: **Visualizador; Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Sem dados; nenhuma pendência; loading parcial; erro de bloco; sem permissão |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Adicionar questões** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-M001 ou destino contextual**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_01_Dashboard_1440px.png`. |

### 28. ADM-CON-001 — Gestão de Matérias

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-CON-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Conteúdo |
| Módulo técnico preliminar | `catalogo_academico` |
| Nome oficial | Gestão de Matérias |
| Perfil autorizado | Visualizador; Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Consultar e manter matérias e seus vínculos. |
| Caso de uso principal | Nova matéria — Consultar e manter matérias e seus vínculos. |
| Casos de uso secundários | Buscar; filtrar; visualizar; editar; ativar; excluir |
| Ponto de entrada | Sidebar admin |
| Destino principal | Tela atual |
| Dados necessários | matérias; áreas; contagens; status; vínculos |
| Entidades envolvidas | `Materia` (existente); Área, status e vínculos — **A definir**. |
| Endpoint | Existentes: `POST/GET /api/materias`, `PUT/DELETE /api/materias/<id>`; filtros, status, ativação e impacto exigem **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Visualizador; Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; sem resultado; erro; sucesso; duplicado; exclusão bloqueada; não salvo |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Nova matéria** somente ao perfil autorizado; preservar contexto e encaminhar para **Tela atual**; falhas não podem apagar dados válidos. |
| Situação atual | **Parcialmente existe** — há contratos ou Models reutilizáveis, mas não a tela definitiva completa. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_02_Materias_1440px.png`. |

### 29. ADM-CON-002 — Gestão de Assuntos

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-CON-002` |
| Ambiente | Administração |
| Módulo funcional oficial | Conteúdo |
| Módulo técnico preliminar | `catalogo_academico` |
| Nome oficial | Gestão de Assuntos |
| Perfil autorizado | Visualizador; Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Consultar e manter assuntos vinculados a matérias. |
| Caso de uso principal | Novo assunto — Consultar e manter assuntos vinculados a matérias. |
| Casos de uso secundários | Buscar; filtrar; editar; alterar matéria; excluir |
| Ponto de entrada | Sidebar admin |
| Destino principal | Tela atual |
| Dados necessários | assuntos; matérias; áreas; contagens; vínculos |
| Entidades envolvidas | `Assunto` e `Materia` (existentes); Área, status e contagens — **A definir**. |
| Endpoint | Existentes: `GET /api/materias`, `POST/GET /api/assuntos`, `PUT/DELETE /api/assuntos/<id>`; filtros e impactos exigem **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Visualizador; Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; sem resultado; erro; impacto de vínculo; exclusão bloqueada; não salvo |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Novo assunto** somente ao perfil autorizado; preservar contexto e encaminhar para **Tela atual**; falhas não podem apagar dados válidos. |
| Situação atual | **Parcialmente existe** — há contratos ou Models reutilizáveis, mas não a tela definitiva completa. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_03_Assuntos_1440px.png`. |

### 30. ADM-QUE-001 — Gestão de Questões

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `questoes` |
| Nome oficial | Gestão de Questões |
| Perfil autorizado | Visualizador; Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Gerenciar o banco completo de questões. |
| Caso de uso principal | Adicionar questões — Gerenciar o banco completo de questões. |
| Casos de uso secundários | Filtrar; visualizar; editar; revisar; publicar; arquivar; lote |
| Ponto de entrada | Sidebar admin ou dashboard |
| Destino principal | ADM-QUE-M001 |
| Dados necessários | questões; taxonomia; origem; dificuldade; status; permissões |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | Parcial: `GET /api/questoes/por-assunto?assunto_id=<id>` e `POST /api/questoes`; gestão completa, filtros, lote e ciclo editorial: **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository apenas quando a consulta for especializada. |
| Permissões necessárias | Perfil oficial: **Visualizador; Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; filtros sem resultado; carga parcial; erro; sem permissão; seleção incompatível |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Adicionar questões** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-M001**; falhas não podem apagar dados válidos. |
| Situação atual | **Parcialmente existe** — há contratos ou Models reutilizáveis, mas não a tela definitiva completa. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_04_Questoes_1440px.png`. |

### 31. ADM-QUE-002 — Cadastro Manual de Questão

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-002` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `questoes` |
| Nome oficial | Cadastro Manual de Questão |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Cadastrar conteúdo, alternativas, resposta, explicação e classificação. |
| Caso de uso principal | Enviar para revisão — Cadastrar conteúdo, alternativas, resposta, explicação e classificação. |
| Casos de uso secundários | Salvar rascunho; visualizar como aluno; cancelar |
| Ponto de entrada | ADM-QUE-M001 |
| Destino principal | ADM-QUE-009 |
| Dados necessários | taxonomia; editor; mídia; validações; duplicidade; permissões |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | Parcial: `GET /api/assuntos` e `POST /api/questoes`; rascunho, mídia, duplicidade e revisão: **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository apenas quando a consulta for especializada. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Rascunho salvo; não salvo; erro sem perda; upload; falha; duplicidade; sem permissão |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar para revisão** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-009**; falhas não podem apagar dados válidos. |
| Situação atual | **Parcialmente existe** — há contratos ou Models reutilizáveis, mas não a tela definitiva completa. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Questoes_01_Cadastro_Manual_1440px.png`. |

### 32. ADM-QUE-003 — Importação Oficial - Identificar Prova

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-003` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `importacoes` + `questoes` |
| Nome oficial | Importação Oficial - Identificar Prova |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Identificar prova, gabarito e referência oficial. |
| Caso de uso principal | Iniciar processamento — Identificar prova, gabarito e referência oficial. |
| Casos de uso secundários | Salvar rascunho; cancelar |
| Ponto de entrada | ADM-QUE-M001 |
| Destino principal | ADM-QUE-004 |
| Dados necessários | ano; aplicação; dia; caderno; idioma; fonte; arquivos |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD + processamento de importação; Repository para validações especializadas. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; upload; arquivo inválido; prova sem gabarito; erro sem perda |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Iniciar processamento** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-004**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Questoes_02_Importacao_Identificar_1440px.png`. |

### 33. ADM-QUE-004 — Importação Oficial - Processamento

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-004` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `importacoes` + `questoes` |
| Nome oficial | Importação Oficial - Processamento |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Exibir extração progressiva sem prometer perfeição. |
| Caso de uso principal | Continuar para validação — Exibir extração progressiva sem prometer perfeição. |
| Casos de uso secundários | Cancelar restante; retomar |
| Ponto de entrada | ADM-QUE-003 |
| Destino principal | ADM-QUE-005 |
| Dados necessários | arquivos; páginas; extração; mídia; gabarito; fila |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD + processamento de importação; Repository para validações especializadas. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Fila; processando; parcial; interrompido; páginas ilegíveis; retomada; erro |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Continuar para validação** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-005**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Questoes_03_Importacao_Processamento_1440px.png`. |

### 34. ADM-QUE-005 — Importação Oficial - Validação

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-005` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `importacoes` + `questoes` |
| Nome oficial | Importação Oficial - Validação |
| Perfil autorizado | Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Validar itens, alertas, duplicidades e metadados antes de importar. |
| Caso de uso principal | Importar itens válidos — Validar itens, alertas, duplicidades e metadados antes de importar. |
| Casos de uso secundários | Corrigir pendências; abrir item; ignorar; salvar rascunho |
| Ponto de entrada | ADM-QUE-004 |
| Destino principal | ADM-QUE-009 ou ADM-QUE-010 |
| Dados necessários | itens extraídos; gabarito; mídia; classificação; duplicidades |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD + processamento de importação; Repository para validações especializadas. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Válida; alerta; erro; possível duplicidade transversal; sem gabarito; parcial |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Importar itens válidos** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-009 ou ADM-QUE-010**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Questoes_04_Importacao_Validacao_1440px.png`. |

### 35. ADM-QUE-006 — IA - Configuração da Geração

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-006` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `questoes` + `tutor_ia` |
| Nome oficial | IA - Configuração da Geração |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Configurar geração limitada e governada de questões. |
| Caso de uso principal | Gerar questões — Configurar geração limitada e governada de questões. |
| Casos de uso secundários | Salvar configuração; cancelar |
| Ponto de entrada | ADM-QUE-M001 |
| Destino principal | ADM-QUE-007 |
| Dados necessários | taxonomia; quantidade; objetivo; regras; configuração da IA |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Serviço externo de IA + Model/CRUD; Repository para lote/duplicidade. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Sem configuração; limite; inválido; possível duplicidade; sem permissão |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Gerar questões** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-007**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Questoes_05_IA_Configuracao_1440px.png`. |

### 36. ADM-QUE-007 — IA - Processamento

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-007` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `questoes` + `tutor_ia` |
| Nome oficial | IA - Processamento |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Acompanhar geração e preservar itens concluídos. |
| Caso de uso principal | Ver resultado — Acompanhar geração e preservar itens concluídos. |
| Casos de uso secundários | Cancelar restante |
| Ponto de entrada | ADM-QUE-006 |
| Destino principal | ADM-QUE-008 |
| Dados necessários | lote; progresso; custos quando aplicável; respostas da IA |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Serviço externo de IA + Model/CRUD; Repository para lote/duplicidade. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Gerando; parcial; timeout; falha por item; cancelado; conexão recuperada |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Ver resultado** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-008**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Questoes_06_IA_Processamento_1440px.png`. |

### 37. ADM-QUE-008 — IA - Resultado

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-008` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `questoes` + `tutor_ia` |
| Nome oficial | IA - Resultado |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Apresentar rascunhos gerados, alertas e próximos passos. |
| Caso de uso principal | Enviar para revisão — Apresentar rascunhos gerados, alertas e próximos passos. |
| Casos de uso secundários | Revisar; excluir rascunho; gerar novamente; corrigir classificação |
| Ponto de entrada | ADM-QUE-007 |
| Destino principal | ADM-QUE-009 ou ADM-QUE-010 |
| Dados necessários | lote; rascunhos; alertas; duplicidades; custo quando configurado |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Serviço externo de IA + Model/CRUD; Repository para lote/duplicidade. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Gerado; alerta; erro; duplicidade; conteúdo inadequado; parcial |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar para revisão** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-009 ou ADM-QUE-010**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Questoes_07_IA_Resultado_1440px.png`. |

### 38. ADM-QUE-009 — Revisão e Aprovação de Questão

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-009` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `questoes` + `revisao_editorial` |
| Nome oficial | Revisão e Aprovação de Questão |
| Perfil autorizado | Revisor; Administrador completo |
| Objetivo | Validar conteúdo, classificação, origem e acessibilidade. |
| Caso de uso principal | Aprovar e publicar — Validar conteúdo, classificação, origem e acessibilidade. |
| Casos de uso secundários | Aprovar; solicitar ajustes; editar; rejeitar; arquivar; voltar à fila |
| Ponto de entrada | Fila, importação ou geração |
| Destino principal | ADM-QUE-001 ou ADM-QUE-010 |
| Dados necessários | questão; checklist; origem; alertas; histórico; permissão |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository apenas quando a consulta for especializada. |
| Permissões necessárias | Perfil oficial: **Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Checklist incompleto; duplicidade; ajustes solicitados; aprovada; publicada; rejeitada |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Aprovar e publicar** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-001 ou ADM-QUE-010**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Questoes_08_Revisao_Aprovacao_1440px.png`. |

### 39. ADM-QUE-010 — Fila e Revisão em Lote

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-QUE-010` |
| Ambiente | Administração |
| Módulo funcional oficial | Questões |
| Módulo técnico preliminar | `questoes` + `revisao_editorial` |
| Nome oficial | Fila e Revisão em Lote |
| Perfil autorizado | Revisor; Administrador completo |
| Objetivo | Selecionar, atribuir e agir apenas sobre itens compatíveis. |
| Caso de uso principal | Aprovar itens elegíveis — Selecionar, atribuir e agir apenas sobre itens compatíveis. |
| Casos de uso secundários | Enviar; atribuir; alterar classificação; arquivar; rejeitar |
| Ponto de entrada | ADM-QUE-001 ou envios de conteúdo |
| Destino principal | ADM-QUE-009 ou ADM-QUE-001 |
| Dados necessários | fila; seleção; elegibilidade; alertas; estados; permissões |
| Entidades envolvidas | `Questao`, `Assunto` e `Materia` quando aplicáveis (existentes no MVP); demais conceitos citados — **A definir formalmente**. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository apenas quando a consulta for especializada. |
| Permissões necessárias | Perfil oficial: **Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Sem itens; seleção parcial; elegível; bloqueado; incompatível; erro sem perda |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Aprovar itens elegíveis** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-QUE-009 ou ADM-QUE-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Questoes_09_Fila_Revisao_Lote_1440px.png`. |

### 40. ADM-SIM-001 — Gestão de Simulados

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-SIM-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Gestão de Simulados |
| Perfil autorizado | Visualizador; Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Gerenciar simulados, disponibilidade e versões. |
| Caso de uso principal | Novo simulado — Gerenciar simulados, disponibilidade e versões. |
| Casos de uso secundários | Filtrar; visualizar; editar; duplicar; revisar; publicar; arquivar |
| Ponto de entrada | Sidebar admin |
| Destino principal | ADM-SIM-M001 |
| Dados necessários | simulados; versões; disponibilidade; tentativas; permissões |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: simulados; versões; disponibilidade; tentativas; permissões. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Visualizador; Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; sem resultado; erro; publicação bloqueada; versão desatualizada |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Novo simulado** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-SIM-M001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_01_Gestao_Simulados_1440px.png`. |

### 41. ADM-SIM-002 — Criação Manual de Simulado

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-SIM-002` |
| Ambiente | Administração |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Criação Manual de Simulado |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Selecionar e ordenar questões publicadas elegíveis. |
| Caso de uso principal | Enviar para revisão — Selecionar e ordenar questões publicadas elegíveis. |
| Casos de uso secundários | Salvar rascunho; visualizar como aluno; cancelar |
| Ponto de entrada | ADM-SIM-001 |
| Destino principal | ADM-SIM-006 |
| Dados necessários | dados gerais; banco publicado; seleção; distribuição; disponibilidade |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: dados gerais; banco publicado; seleção; distribuição; disponibilidade. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Rascunho; duplicidade; questão indisponível; total divergente; erro sem perda |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar para revisão** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-SIM-006**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_02_Criacao_Manual_1440px.png`. |

### 42. ADM-SIM-003 — Gerador Automático Fixo

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-SIM-003` |
| Ambiente | Administração |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Gerador Automático Fixo |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Gerar uma composição fixa a partir de critérios. |
| Caso de uso principal | Gerar prévia — Gerar uma composição fixa a partir de critérios. |
| Casos de uso secundários | Ajustar critérios; aceitar quantidade disponível; cancelar |
| Ponto de entrada | ADM-SIM-001 |
| Destino principal | ADM-SIM-006 |
| Dados necessários | critérios; banco elegível; distribuição; repetição; tempo |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: critérios; banco elegível; distribuição; repetição; tempo. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Banco insuficiente; critérios incompatíveis; prévia; erro; sucesso |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Gerar prévia** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-SIM-006**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_03_Automatico_Fixo_1440px.png`. |

### 43. ADM-SIM-004 — Simulado Personalizado Dinâmico

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-SIM-004` |
| Ambiente | Administração |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Simulado Personalizado Dinâmico |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Definir regras e fallback de personalização em tempo de início. |
| Caso de uso principal | Testar regra — Definir regras e fallback de personalização em tempo de início. |
| Casos de uso secundários | Ajustar pesos; configurar fallback; cancelar |
| Ponto de entrada | ADM-SIM-001 |
| Destino principal | ADM-SIM-006 |
| Dados necessários | critérios; pesos; histórico; fallback; versão da regra |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: critérios; pesos; histórico; fallback; versão da regra. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Histórico insuficiente; regra inválida; banco insuficiente; prévia; erro |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Testar regra** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-SIM-006**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_04_Personalizado_Dinamico_1440px.png`. |

### 44. ADM-SIM-005 — Uso de Prova Oficial do ENEM

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-SIM-005` |
| Ambiente | Administração |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Uso de Prova Oficial do ENEM |
| Perfil autorizado | Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Disponibilizar importação íntegra preservando identidade oficial. |
| Caso de uso principal | Enviar para revisão — Disponibilizar importação íntegra preservando identidade oficial. |
| Casos de uso secundários | Criar cópia baseada; cancelar |
| Ponto de entrada | ADM-SIM-001 |
| Destino principal | ADM-SIM-006 |
| Dados necessários | importação; ano; aplicação; caderno; ordem; gabarito; fonte |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: importação; ano; aplicação; caderno; ordem; gabarito; fonte. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Item ausente; gabarito ausente; mídia quebrada; origem inválida; bloqueado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar para revisão** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-SIM-006**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_05_Prova_Oficial_1440px.png`. |

### 45. ADM-SIM-006 — Revisão, Publicação e Versionamento

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-SIM-006` |
| Ambiente | Administração |
| Módulo funcional oficial | Simulados |
| Módulo técnico preliminar | `simulados` |
| Nome oficial | Revisão, Publicação e Versionamento |
| Perfil autorizado | Revisor; Administrador completo |
| Objetivo | Revisar checklist contextual e preservar resultados por versão. |
| Caso de uso principal | Publicar ou agendar — Revisar checklist contextual e preservar resultados por versão. |
| Casos de uso secundários | Solicitar ajustes; aprovar; criar nova versão; arquivar |
| Ponto de entrada | Criação manual, automática, dinâmica ou oficial |
| Destino principal | ADM-SIM-001 |
| Dados necessários | simulado; tipo; questões/regra; checklist; versão; tentativas; período |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: simulado; tipo; questões/regra; checklist; versão; tentativas; período. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para composição, elegibilidade, tentativas e resultados. |
| Permissões necessárias | Perfil oficial: **Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Não se aplica; aprovado indisponível; agendado; publicado; bloqueado; arquivado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Publicar ou agendar** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-SIM-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_06_Revisao_Versionamento_1440px.png`. |

### 46. ADM-RES-001 — Gestão de Resumos

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-RES-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Resumos |
| Módulo técnico preliminar | `resumos` + `revisao_editorial` |
| Nome oficial | Gestão de Resumos |
| Perfil autorizado | Visualizador; Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Gerenciar biblioteca, origem editorial e versões. |
| Caso de uso principal | Novo resumo — Gerenciar biblioteca, origem editorial e versões. |
| Casos de uso secundários | Filtrar; visualizar; editar; duplicar; revisar; publicar; arquivar |
| Ponto de entrada | Sidebar admin |
| Destino principal | ADM-RES-002 |
| Dados necessários | resumos; taxonomia; origem editorial; uso de IA; fonte; versão |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: resumos; taxonomia; origem editorial; uso de IA; fonte; versão. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Visualizador; Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; sem resultado; loading; erro; sem permissão; publicado versionado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Novo resumo** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-RES-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_07_Gestao_Resumos_1440px.png`. |

### 47. ADM-RES-002 — Editor de Resumo

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-RES-002` |
| Ambiente | Administração |
| Módulo funcional oficial | Resumos |
| Módulo técnico preliminar | `resumos` + `revisao_editorial` |
| Nome oficial | Editor de Resumo |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Criar conteúdo estruturado com fontes e mídias acessíveis. |
| Caso de uso principal | Enviar para revisão — Criar conteúdo estruturado com fontes e mídias acessíveis. |
| Casos de uso secundários | Salvar rascunho; visualizar; gerar sugestão com IA; cancelar |
| Ponto de entrada | ADM-RES-001 |
| Destino principal | ADM-RES-003 |
| Dados necessários | taxonomia; seções; mídia; fonte; referência; autor; versão; IA |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: taxonomia; seções; mídia; fonte; referência; autor; versão; IA. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Rascunho; upload; erro sem perda; não salvo; duplicidade; sugestão IA |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar para revisão** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-RES-003**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_08_Editor_Resumo_1440px.png`. |

### 48. ADM-RES-003 — Revisão de Resumo

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-RES-003` |
| Ambiente | Administração |
| Módulo funcional oficial | Resumos |
| Módulo técnico preliminar | `resumos` + `revisao_editorial` |
| Nome oficial | Revisão de Resumo |
| Perfil autorizado | Revisor; Administrador completo |
| Objetivo | Validar correção, fontes, acessibilidade e CTA contextual. |
| Caso de uso principal | Aprovar e publicar — Validar correção, fontes, acessibilidade e CTA contextual. |
| Casos de uso secundários | Aprovar; solicitar ajustes; editar; rejeitar; arquivar |
| Ponto de entrada | ADM-RES-002 ou fila |
| Destino principal | ADM-RES-001 |
| Dados necessários | resumo; checklist; fonte; CTA; histórico; permissões |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: resumo; checklist; fonte; CTA; histórico; permissões. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Checklist incompleto; ajustes; aprovado; publicado; rejeitado; arquivado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Aprovar e publicar** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-RES-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_09_Revisao_Resumo_1440px.png`. |

### 49. ADM-TEM-001 — Gestão de Temas

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-TEM-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Temas de Redação |
| Módulo técnico preliminar | `redacao` + `revisao_editorial` |
| Nome oficial | Gestão de Temas |
| Perfil autorizado | Visualizador; Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Gerenciar propostas, origens, versões e uso em redações. |
| Caso de uso principal | Novo tema — Gerenciar propostas, origens, versões e uso em redações. |
| Casos de uso secundários | Filtrar; visualizar; editar; duplicar; revisar; publicar; arquivar |
| Ponto de entrada | Sidebar admin |
| Destino principal | ADM-TEM-002 |
| Dados necessários | temas; eixo; origem; ano; motivadores; uso; autor; status |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: temas; eixo; origem; ano; motivadores; uso; autor; status. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Visualizador; Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; sem resultado; erro; sem permissão; exclusão bloqueada; versionado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Novo tema** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-TEM-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_01_Gestao_Temas_1440px.png`. |

### 50. ADM-TEM-002 — Criação Manual de Tema

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-TEM-002` |
| Ambiente | Administração |
| Módulo funcional oficial | Temas de Redação |
| Módulo técnico preliminar | `redacao` + `revisao_editorial` |
| Nome oficial | Criação Manual de Tema |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Criar proposta autoral e motivadores com origem preservada. |
| Caso de uso principal | Enviar para revisão — Criar proposta autoral e motivadores com origem preservada. |
| Casos de uso secundários | Salvar rascunho; visualizar como aluno; cancelar |
| Ponto de entrada | ADM-TEM-001 |
| Destino principal | ADM-TEM-005 |
| Dados necessários | proposta; eixo; motivadores; fontes; direitos; versão; autor |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: proposta; eixo; motivadores; fontes; direitos; versão; autor. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Rascunho; não salvo; validação; upload; erro; duplicidade; sem permissão |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar para revisão** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-TEM-005**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_02_Tema_Manual_1440px.png`. |

### 51. ADM-TEM-003 — Importação de Tema Oficial

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-TEM-003` |
| Ambiente | Administração |
| Módulo funcional oficial | Temas de Redação |
| Módulo técnico preliminar | `redacao` + `revisao_editorial` |
| Nome oficial | Importação de Tema Oficial |
| Perfil autorizado | Editor de conteúdo; Revisor; Administrador completo |
| Objetivo | Extrair proposta oficial preservando identidade e integridade. |
| Caso de uso principal | Corrigir pendências — Extrair proposta oficial preservando identidade e integridade. |
| Casos de uso secundários | Criar cópia baseada; salvar importação; cancelar |
| Ponto de entrada | ADM-TEM-001 |
| Destino principal | ADM-TEM-005 |
| Dados necessários | ano; aplicação; fonte; arquivo; comando; motivadores; páginas |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: ano; aplicação; fonte; arquivo; comando; motivadores; páginas. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Extraindo; mídia com erro; ilegível; duplicidade; partes ausentes; íntegro |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Corrigir pendências** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-TEM-005**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_03_Importacao_Tema_Oficial_1440px.png`. |

### 52. ADM-TEM-004 — Geração de Tema com IA

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-TEM-004` |
| Ambiente | Administração |
| Módulo funcional oficial | Temas de Redação |
| Módulo técnico preliminar | `redacao` + `revisao_editorial` |
| Nome oficial | Geração de Tema com IA |
| Perfil autorizado | Editor de conteúdo; Administrador completo |
| Objetivo | Gerar proposta autoral como rascunho para revisão humana. |
| Caso de uso principal | Revisar tema — Gerar proposta autoral como rascunho para revisão humana. |
| Casos de uso secundários | Gerar novamente; excluir rascunho; enviar para revisão |
| Ponto de entrada | ADM-TEM-001 |
| Destino principal | ADM-TEM-005 |
| Dados necessários | configuração; regras; lote; modelo quando registrado; alertas |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: configuração; regras; lote; modelo quando registrado; alertas. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Editor de conteúdo; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Rascunho; gerando; parcial; erro; duplicidade; conteúdo inadequado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Revisar tema** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-TEM-005**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_04_Tema_com_IA_1440px.png`. |

### 53. ADM-TEM-005 — Revisão e Publicação de Tema

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-TEM-005` |
| Ambiente | Administração |
| Módulo funcional oficial | Temas de Redação |
| Módulo técnico preliminar | `redacao` + `revisao_editorial` |
| Nome oficial | Revisão e Publicação de Tema |
| Perfil autorizado | Revisor; Administrador completo |
| Objetivo | Revisar proposta, fontes, acessibilidade, origem e direitos humanos. |
| Caso de uso principal | Aprovar e publicar — Revisar proposta, fontes, acessibilidade, origem e direitos humanos. |
| Casos de uso secundários | Aprovar; solicitar ajustes; editar; rejeitar; arquivar |
| Ponto de entrada | Criação, importação ou IA |
| Destino principal | ADM-TEM-001 |
| Dados necessários | tema; motivadores; checklist; origem; IA; histórico; versão |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: tema; motivadores; checklist; origem; IA; histórico; versão. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Checklist incompleto; duplicidade crítica; ajustes; aprovado; publicado; rejeitado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Aprovar e publicar** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-TEM-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_05_Revisao_Tema_1440px.png`. |

### 54. ADM-RED-001 — Gestão de Redações Enviadas

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-RED-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Redações |
| Módulo técnico preliminar | `redacao` + `revisao_editorial` |
| Nome oficial | Gestão de Redações Enviadas |
| Perfil autorizado | Carla Souza · Revisora; Administrador completo; Editor somente metadados permitidos |
| Objetivo | Consultar submissões e acompanhar correções com acesso proporcional. |
| Caso de uso principal | Abrir correção — Consultar submissões e acompanhar correções com acesso proporcional. |
| Casos de uso secundários | Filtrar; encaminhar à revisão; abrir monitoramento |
| Ponto de entrada | Sidebar admin |
| Destino principal | ADM-RED-002 ou ADM-RED-003 |
| Dados necessários | metadados; tema; versão; status; estimativa; autorização de texto integral |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: metadados; tema; versão; status; estimativa; autorização de texto integral. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo para correção automatizada quando aplicável; Repository para filas/relatórios. |
| Permissões necessárias | Perfil oficial: **Carla Souza · Revisora; Administrador completo; Editor somente metadados permitidos**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Na fila; em correção; corrigida; falha; revisão humana; invalidada; arquivada |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Abrir correção** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-RED-002 ou ADM-RED-003**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_06_Gestao_Redacoes_1440px.png`. |

### 55. ADM-RED-002 — Monitoramento das Correções Automatizadas

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-RED-002` |
| Ambiente | Administração |
| Módulo funcional oficial | Redações |
| Módulo técnico preliminar | `redacao` + `revisao_editorial` |
| Nome oficial | Monitoramento das Correções Automatizadas |
| Perfil autorizado | Revisor; Administrador completo |
| Objetivo | Monitorar fila, tentativas, falhas e sobreposições operacionais. |
| Caso de uso principal | Atualizar fila — Monitorar fila, tentativas, falhas e sobreposições operacionais. |
| Casos de uso secundários | Reprocessar; revisão humana; cancelar; retomar; invalidar |
| Ponto de entrada | ADM-RED-001 |
| Destino principal | ADM-RED-003 |
| Dados necessários | fila; tentativa; serviço; tempo; falha; correções versionadas |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: fila; tentativa; serviço; tempo; falha; correções versionadas. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo para correção automatizada quando aplicável; Repository para filas/relatórios. |
| Permissões necessárias | Perfil oficial: **Revisor; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Aguardando; processando; concluída; falha; timeout; revisão humana transversal |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Atualizar fila** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-RED-003**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_07_Monitor_Correcoes_1440px.png`. |

### 56. ADM-RED-003 — Detalhe e Revisão da Correção

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-RED-003` |
| Ambiente | Administração |
| Módulo funcional oficial | Redações |
| Módulo técnico preliminar | `redacao` + `revisao_editorial` |
| Nome oficial | Detalhe e Revisão da Correção |
| Perfil autorizado | Carla Souza · Revisora; Administrador completo |
| Objetivo | Revisar correção sem alterar o texto original do aluno. |
| Caso de uso principal | Enviar devolutiva revisada — Revisar correção sem alterar o texto original do aluno. |
| Casos de uso secundários | Confirmar; ajustar com motivo; invalidar; reprocessar |
| Ponto de entrada | ADM-RED-001 ou ADM-RED-002 |
| Destino principal | ADM-RED-001 |
| Dados necessários | texto original imutável; versões; C1-C5; feedback; histórico; auditoria |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: texto original imutável; versões; C1-C5; feedback; histórico; auditoria. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; serviço externo para correção automatizada quando aplicável; Repository para filas/relatórios. |
| Permissões necessárias | Perfil oficial: **Carla Souza · Revisora; Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Correção atual; alteração justificada; reprocessamento; invalidada; erro sem perda |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Enviar devolutiva revisada** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-RED-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_08_Revisao_Correcao_1440px.png`. |

### 57. ADM-USU-001 — Gestão de Usuários

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-USU-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Usuários |
| Módulo técnico preliminar | `usuarios` + `autorizacao` |
| Nome oficial | Gestão de Usuários |
| Perfil autorizado | Administrador completo; Visualizador autorizado para consulta limitada |
| Objetivo | Gerenciar contas e perfis com dados protegidos. |
| Caso de uso principal | Adicionar usuário — Gerenciar contas e perfis com dados protegidos. |
| Casos de uso secundários | Visualizar; perfil; ativar; suspender; revogar; recuperar; exportar; excluir |
| Ponto de entrada | Sidebar admin |
| Destino principal | ADM-USU-002 |
| Dados necessários | usuários; perfis; status; acessos; verificação; permissões |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: usuários; perfis; status; acessos; verificação; permissões. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Administrador completo; Visualizador autorizado para consulta limitada**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; sem resultado; erro; sem permissão; e-mail pendente; exclusão |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Adicionar usuário** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-USU-002**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_09_Gestao_Usuarios_1440px.png`. |

### 58. ADM-USU-002 — Detalhe do Usuário

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-USU-002` |
| Ambiente | Administração |
| Módulo funcional oficial | Usuários |
| Módulo técnico preliminar | `usuarios` + `autorizacao` |
| Nome oficial | Detalhe do Usuário |
| Perfil autorizado | Administrador completo; Visualizador autorizado para consulta limitada |
| Objetivo | Consultar conta, segurança, privacidade e histórico administrativo. |
| Caso de uso principal | Editar perfil — Consultar conta, segurança, privacidade e histórico administrativo. |
| Casos de uso secundários | Revogar sessões; exportar dados; suspender; excluir |
| Ponto de entrada | ADM-USU-001 |
| Destino principal | ADM-SEG-001 ou ADM-AUD-001 |
| Dados necessários | conta; dados mínimos; sessões; consentimentos; retenção; histórico |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: conta; dados mínimos; sessões; consentimentos; retenção; histórico. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository somente para filtros ou relatórios complexos. |
| Permissões necessárias | Perfil oficial: **Administrador completo; Visualizador autorizado para consulta limitada**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Ativo; suspenso; reautenticação; ação crítica; exclusão; erro sem perda |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Editar perfil** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-SEG-001 ou ADM-AUD-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_10_Detalhe_Usuario_1440px.png`. |

### 59. ADM-SEG-001 — Perfis e Permissões

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-SEG-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Segurança e Governança |
| Módulo técnico preliminar | `autorizacao` + `auditoria` |
| Nome oficial | Perfis e Permissões |
| Perfil autorizado | Administrador completo |
| Objetivo | Explicar e alterar acessos sob menor privilégio. |
| Caso de uso principal | Confirmar alteração — Explicar e alterar acessos sob menor privilégio. |
| Casos de uso secundários | Revisar alterações; cancelar |
| Ponto de entrada | ADM-USU-002 ou sidebar admin |
| Destino principal | ADM-AUD-001 |
| Dados necessários | perfis fixos; permissões efetivas; nível do operador; sessões |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: perfis fixos; permissões efetivas; nível do operador; sessões. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para consulta e exportação auditável. |
| Permissões necessárias | Perfil oficial: **Administrador completo**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Sem permissão; superior ao próprio perfil; reautenticação; sucesso; erro sem perda |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Confirmar alteração** somente ao perfil autorizado; preservar contexto e encaminhar para **ADM-AUD-001**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_11_Perfis_Permissoes_1440px.png`. |

### 60. ADM-AUD-001 — Registro de Auditoria

| Campo | Mapeamento v1 |
| --- | --- |
| ID oficial | `ADM-AUD-001` |
| Ambiente | Administração |
| Módulo funcional oficial | Segurança e Governança |
| Módulo técnico preliminar | `auditoria` |
| Nome oficial | Registro de Auditoria |
| Perfil autorizado | Administrador completo; auditor autorizado para consulta/exportação |
| Objetivo | Consultar eventos administrativos importantes e exportar com segurança. |
| Caso de uso principal | Exportar eventos — Consultar eventos administrativos importantes e exportar com segurança. |
| Casos de uso secundários | Buscar; filtrar; abrir detalhe |
| Ponto de entrada | Sidebar admin ou ação crítica |
| Destino principal | Tela atual |
| Dados necessários | eventos; ator; recurso; antes/depois; motivo; correlação; permissão |
| Entidades envolvidas | **A definir formalmente**. Conceitos de dados oficiais: eventos; ator; recurso; antes/depois; motivo; correlação; permissão. |
| Endpoint | **NOVO — contrato ainda será definido**. |
| Tipo de persistência | Model/CRUD; Repository/Procedure para consulta e exportação auditável. |
| Permissões necessárias | Perfil oficial: **Administrador completo; auditor autorizado para consulta/exportação**; validação no servidor e princípio de menor privilégio. |
| Estados principais | Vazio; sem resultado; loading; erro; sem permissão; exportando; exportado |
| Critérios iniciais de aceite | Exibir os dados previstos ou um dos estados oficiais; permitir **Exportar eventos** somente ao perfil autorizado; preservar contexto e encaminhar para **Tela atual**; falhas não podem apagar dados válidos. |
| Situação atual | **Ainda não existe**. |
| Aprovação visual | Aprovada; origem: `output/pdf/Plataforma_ENEM_Admin_Final_12_Auditoria_1440px.png`. |

## Relação explícita com as 10 funcionalidades do MVP

Extensão acadêmica implementada: `/aluno/privacidade.html` consulta evidências,
aceita uso de contas anteriores e autoriza/recusa/revoga a finalidade do plano.
Entrada fixa por início/plano e navegação do Aluno. `/login` e `/cadastro`
oferecem leitura pública dos dois documentos; cadastro exige somente uso.
ALU-PLA-001 exige ambos os aceites vigentes; negativa mantém outros fluxos de
estudo. Esta extensão não altera os IDs ou binários congelados do Desktop V1
nem renumera a matriz acadêmica. Ver [operação](operacao-privacidade.md).

| # | Funcionalidade existente | Tela administrativa relacionada | Contrato preservado | Evolução posterior |
| ---: | --- | --- | --- | --- |
| 1 | Cadastrar matéria | ADM-CON-001 | `POST /api/materias` | Adicionar área, status, permissões e auditoria sem quebrar o contrato atual. |
| 2 | Listar matérias | ADM-CON-001 | `GET /api/materias` | Paginação, filtros, contagens e estado editorial exigem contrato novo/evoluído. |
| 3 | Atualizar matéria | ADM-CON-001 | `PUT /api/materias/<id>` | Permissões, impacto de vínculos e concorrência precisam ser acrescentados. |
| 4 | Excluir matéria | ADM-CON-001 | `DELETE /api/materias/<id>` | Política de cascade versus bloqueio permanece em decisão aberta. |
| 5 | Cadastrar assunto | ADM-CON-002 | `POST /api/assuntos` | Área, status, autoria e auditoria serão evoluídos. |
| 6 | Listar assuntos | ADM-CON-002 | `GET /api/assuntos` | Paginação, filtros, contagens e busca exigem evolução. |
| 7 | Atualizar assunto | ADM-CON-002 | `PUT /api/assuntos/<id>` | Permissões, impacto de vínculos e concorrência serão acrescentados. |
| 8 | Excluir assunto | ADM-CON-002 | `DELETE /api/assuntos/<id>` | O bloqueio por Questões já existe; arquivamento precisa de contrato futuro. |
| 9 | Cadastrar questão | ADM-QUE-002 | `POST /api/questoes` | Rascunho, mídia, origem, versionamento e revisão exigem novos contratos. |
| 10 | Buscar questões por assunto | ADM-QUE-001; reaproveitamento parcial em ALU-QUE-001 | `GET /api/questoes/por-assunto?assunto_id=<id>` | Gestão completa e prática do aluno exigem listagens e respostas próprias. |

### Reuso transversal dos contratos atuais

- `GET /api/materias` pode alimentar ALU-ONB-003, filtros de Questões, Simulados, Resumos e telas administrativas durante a transição.
- `GET /api/assuntos` pode alimentar filtros, cadastro editorial e seleção contextual.
- `GET /api/questoes/por-assunto` pode apoiar prévias e filtros iniciais, mas não substitui seleção de prática, paginação, versionamento ou permissão.
- Os contratos atuais não incluem autenticação, autorização, paginação, autoria, estados editoriais, versões ou auditoria; essas capacidades devem ser adicionadas por compatibilidade, sem alteração silenciosa das respostas existentes.
