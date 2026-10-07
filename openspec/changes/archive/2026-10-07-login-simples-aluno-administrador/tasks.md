# Tarefas

## 1. Preparar persistência compatível

- [x] 1.1 Fazer preflight somente leitura dos artefatos, conventions, ADR-001/002/006, migrations, testes e referências oficiais PUB-AUT-001/002; verificar que contratos e superfícies concordam com esta change e registrar incompatibilidade antes de editar.
- [x] 1.2 Criar migration `005_create_autenticacao_escolar.sql`, Models e snapshot equivalente para usuários, sessões e limites, sem contas padrão nem alteração de migrations antigas; verificar constraints, unicidade, FKs e preservação de catálogo com novos testes MySQL de instalação/upgrade/idempotência.
- [x] 1.3 Estender apenas o reconhecimento do estado 005 no fingerprint/baseline do runner; verificar snapshot equivalente, rejeição de estados parciais e regressão dos prefixos 000–004 em testes unitários e MySQL, documentando pré-condições/reversão em `docs/technical/operacao-autenticacao-escolar.md`.

## 2. Entregar o ciclo de sessão e CSRF

- [x] 2.1 Implementar geração/hash de identificador, consulta/revogação individual/global e expiração com UTC, usando Model/Repository e `TransactionManager`; verificar nos unitários e MySQL limites inclusivos de tempo, duas sessões, conta inativa e concorrência entre revogação e último acesso.
- [x] 2.2 Implementar GET CSRF/sessão, validação de chave, cookie, Origin/CSRF e CORS na factory/config/Controller/Services; verificar flags, no-store, falta de chave, origem inválida, token de outra sessão e preflight com unitários e integrações sem bypass.
- [x] 2.3 Documentar variável de chave vazia em `.env.example`, geração fora de logs, origens e uso de HTTP local/HTTPS em `operacao-autenticacao-escolar.md`; verificar que exemplos não contêm credencial real e não exigem modificar `.env` por código.

## 3. Entregar login, logout e reautenticação

- [x] 3.1 Implementar Service/Controller/rotas de login com hash scrypt, mensagens neutras e rotação atômica, e limite concorrente de tentativas em `auth_limites`; verificar senha incorreta/desconhecida/inativa, quinta falha, Retry-After, retomada e rollback com unitários e MySQL real.
- [x] 3.2 Implementar logout idempotente e reautenticação da conta atual com janela de 15 minutos, códigos distintos e limite próprio; verificar logout de um cliente, cookie removido, falha de senha sem perda da sessão e renovação da janela em testes unitários/integração.
- [x] 3.3 Documentar os seis endpoints novos, respostas/erros e durações em `operacao-autenticacao-escolar.md`; verificar cada exemplo contra testes de contrato, sem registrar corpo sensível.

## 4. Entregar cadastro e provisionamento local

- [x] 4.1 Implementar cadastro público de Aluno com validação estrita, confirmação de senha, normalização única e conflito de e-mail, sem login automático; verificar 201, 400, 409, rejeição de perfil/campos extras, cadastro autenticado e corrida de duplicidade em unitários/MySQL.
- [x] 4.2 Implementar comando `criar-administrador` na factory usando Service e prompt oculto; verificar criação/login real, senha divergente e e-mail existente sem promoção/alteração, com testes de CLI e schema MySQL descartável.
- [x] 4.3 Implementar comando `limpar-autenticacao` com remoção restrita a registros antigos; verificar que mantém conta, sessão válida, catálogo/histórico, e documentar ambos os comandos e o fluxo de contas na operação/README.

## 5. Proteger as APIs existentes e preservar regressão

- [x] 5.1 Aplicar a matriz de autorização do design às 24 regras atuais sem mover camadas; verificar cada superfície com cliente anônimo, Aluno e Administrador, incluindo status=todos, consulta legada com gabarito, HEAD/OPTIONS e 404/405, em testes de contrato e MySQL.
- [x] 5.2 Aplicar janela sensível em DELETE, ações de status/transferência e PUT alternativos; verificar rejeição antes de efeitos, CSRF/origem e regras de negócio preservadas nos testes das rotas afetadas.
- [x] 5.3 Adaptar preparação compartilhada de integrações para criar Administrador temporário e autenticar pela API com cookie/CSRF/Origin; verificar os 29 cenários originais e regressões ampliadas sem remover asserts de negócio, sem flag de bypass e sem mocks/SQLite; ajustar unitários de factory/Controller para o novo contrato.
- [x] 5.4 Atualizar documentação das políticas BREAKING e pré-requisitos dos consumidores no README/operação; verificar que URLs/payloads de sucesso seguem documentados e nenhuma rota de gestão fica pública como fallback.

## 6. Entregar telas públicas e início do Aluno

- [x] 6.1 Adaptar `frontend/js/api.js` para host/configuração da API, credentials, bootstrap CSRF compartilhado em memória e códigos de `ApiError`, mantendo JSON/null; verificar testes DOM do cliente, erros de rede, token após login e proibição de retry automático de mutação.
- [x] 6.2 Criar `/login.html` e `/cadastro.html` com scripts/CSS e ativos locais conforme PUB-AUT-001/002, incluindo confirmação, envio único, erros acessíveis, cadastro -> login e prefill de e-mail consumido; verificar testes DOM e inspeção em navegador a 1440/390 px contra as fontes oficiais, sem alterar binários.
- [x] 6.3 Criar `/aluno/inicio.html` com identidade real/saída e destino fixo por perfil; verificar em DOM e navegador cadastro -> login -> início -> logout, recarga com sessão inválida e ausência de redirect externo/dados fictícios.
- [x] 6.4 Registrar no README e documentação operacional os destinos e o recorte visual (sem recuperação/onboarding/dashboard nesta etapa); verificar que todos os links ativos têm destino funcional.

## 7. Integrar sessão à gestão e ao MVP legado

- [x] 7.1 Integrar guard inicial, nome real, acesso negado e saída a `/index.html`, ADM-CON-001 e ADM-CON-002 antes de disparar consultas; verificar testes DOM dos três consumidores e navegador com os dois perfis, inclusive indisponibilidade de sessão.
- [x] 7.2 Implementar diálogo contextual para sessão expirada/reautenticação e troca de conta, mantendo campos/filtros e exigindo nova confirmação; verificar em DOM e navegador que erro de senha/rede não apaga edição e que nenhum POST/PUT/DELETE é repetido automaticamente.
- [x] 7.3 Conectar logout à proteção existente de alterações não salvas e tratar CSRF desatualizado após outra sessão; verificar cancelar/confirmar saída, foco do diálogo e regressão de todos os fluxos atuais de Matérias/Assuntos/Questões legadas.
- [x] 7.4 Documentar os diálogos, recuperação de contexto e limites do conteúdo HTML estático na operação; verificar correspondência com cenários de `gestao-administrativa-conteudo`, sem introduzir perfis ou telas avançadas.

## 8. Validar integração e preparar verificação OpenSpec

- [x] 8.1 Executar regressão completa com `.venv`, runners backend/MySQL e `npm run test:coverage`, usando opt-ins apenas no processo e schemas descartáveis; verificar 29 cenários originais, suíte ampliada e gates de 90% linhas/85% branches por stack, registrando comandos/resultados reais sem declarar sucesso se MySQL indisponível.
- [x] 8.2 Validar em navegador real cookie/CORS/CSRF entre portas 5500/5000 usando o mesmo host e fluxo dos dois perfis, bloqueio de gestão pelo Aluno, expiração/reautenticação e composição a 1440/390 px; registrar evidências sem senha/tokens e confirmar que dados funcionais preexistentes foram preservados.
- [x] 8.3 Revisar diff e rastreabilidade de todos os cenários contra implementação/testes, verificar ausência de segredos/mudança em binários/migrations antigas e executar `openspec validate login-simples-aluno-administrador --strict`; deixar pronta a etapa `openspec-verify-change`, sem marcar sync/archive como concluídos antes de executá-los no workflow.

## 9. Corrigir avisos reproduzidos na verificação

- [x] 9.1 Validar o nome de cadastro após trim e associar erro/foco ao campo; testar espaços, nome curto após trim, limite máximo e correção válida, sem alterar o contrato da API.
- [x] 9.2 Atualizar a referência do formulário ao iniciar edição de Matéria/Assunto no MVP legado; testar abertura sem alterações, edição real, reversão e cancelamento, mantendo proteção de logout; executar cobertura frontend e nova verificação dos avisos.
