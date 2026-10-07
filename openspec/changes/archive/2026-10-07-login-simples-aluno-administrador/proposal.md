# Proposta

## Why

A entrega escolar precisa distinguir Aluno e Administrador antes de persistir respostas e resultados individuais. Hoje as APIs e telas administrativas permitem acesso sem identidade; esta change entrega cadastro e login reais, mantendo o Flask, o MySQL e o frontend atual.

## What Changes

- Implementar cadastro público de Aluno, login por e-mail/senha, consulta da sessão atual e logout.
- Implementar PUB-AUT-001 em `/login.html` e PUB-AUT-002 em `/cadastro.html`, com os estados e identidade visual do Desktop V1.
- Criar Administrador exclusivamente por comando local com senha solicitada sem eco; o cadastro público nunca concede esse perfil.
- Usar sessão armazenada no MySQL, identificador opaco em cookie HttpOnly, expiração, proteção CSRF e limite básico de tentativas de senha, conforme ADR-002.
- **BREAKING:** exigir Administrador nas APIs atuais de gestão e na consulta legada de Questões que expõe gabarito. Leituras simples do catálogo passam a exigir usuário autenticado. URLs, payloads, regras e respostas de sucesso são preservados para o perfil autorizado; requisições anônimas passam a receber 401 e perfil indevido recebe 403.
- Integrar autenticação às duas telas administrativas e à página legada `/index.html`, incluindo saída e reautenticação para ações sensíveis já existentes.
- Disponibilizar `/aluno/inicio.html` como página mínima de conta autenticada com nome e saída, sem simular um dashboard ou funcionalidades ainda ausentes. Administrador entra em `/admin/materias.html`.

### Fora de escopo

Recuperação/verificação por e-mail, onboarding, troca de senha pela web, gestão de usuários/permissões, perfis adicionais, login social, JWT, serviços externos, reorganização modular, dashboards, prática, simulado, desempenho e plano de estudos. A auditoria completa e as funcionalidades premium continuam adiadas. São mantidas as garantias essenciais de sessão e autorização dos ADRs.

## Capabilities

### New Capabilities

- `autenticacao-escolar`: cadastro público exclusivo de Aluno, provisionamento local de Administrador, credenciais, sessões, CSRF, login/logout, reautenticação, autorização das rotas e navegação autenticada.

### Modified Capabilities

- `catalogo-academico`: explicitar o requisito de autenticação nas leituras legadas, mantendo campos, URLs, seletores e regras de integridade.
- `gestao-administrativa-conteudo`: proteger ADM-CON-001/002 por perfil e sessão, preservar dados locais em reautenticação e integrar identificação/saída sem alterar o restante da gestão.

## Impact

- **Superfícies:** application factory, config/CORS, `routes.py`, novos Controller e Services de autenticação, Models de usuário/sessão, Repository de consultas de sessão e o `TransactionManager` existente; sem SQL em Controller/Service.
- **HTTP:** novas rotas `/api/auth/csrf`, `/cadastro`, `/login`, `/sessao`, `/logout` e `/reautenticar` sob o prefixo `/api/auth`. Políticas explícitas para todas as rotas atuais estão no design.
- **Banco:** migration aditiva `005_create_autenticacao_escolar.sql` e atualização coerente do snapshot consolidado; nenhuma conta ou senha padrão na migration. Conteúdo, histórico do catálogo e procedure permanecem preservados.
- **Frontend:** novos arquivos de autenticação e início do Aluno; adaptação de `frontend/js/api.js`, `/index.html`, ADM-CON-001 e ADM-CON-002 para cookies, CSRF e controle de acesso. Os quatro binários oficiais do Desktop V1 permanecem congelados; diferenças do recorte escolar são registradas no design.
- **Operação:** comando `python -m flask --app backend/run.py criar-administrador`, documentação dos fluxos, origens e migração. Sem implantação ou troca de infraestrutura nesta change.
- **Decisões:** aplica ADR-001, ADR-002 e ADR-006; mantém a estrutura existente e o MVP. O recorte adia os fluxos avançados de conta, sem substituir a sessão de servidor por outro mecanismo.
- **Validação:** preservar os 29 cenários originais e demais regressões, adaptando preparação compartilhada para autenticar de verdade; novas integrações em MySQL real, unitários, testes DOM e verificação visual em navegador. Não haverá bypass de autenticação na aplicação para testes.
- **Dependências:** migrations 000–004, catálogo atual, Flask/Werkzeug e MySQL existentes; nenhuma nova plataforma. Antes do apply, revisar e aprovar os contratos propostos no design e nas specs.
