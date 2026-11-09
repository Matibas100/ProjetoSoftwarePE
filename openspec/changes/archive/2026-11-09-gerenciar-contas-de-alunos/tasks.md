# Tasks

Aplicar conforme [design](design.md) e os três delta specs. Preservar as mudanças legítimas existentes da busca por ID e o escopo escolhido: somente Alunos, com exclusão condicionada. A proposta não executa migration nem altera código de produção.

## 1. Acrescentar interfaces SQL oficiais

- [x] 1.1 Criar `017_gestao_alunos_procedures.sql` e atualizar bootstrap com `sp_alunos_admin` e `sp_usuario_gestao_bloqueado`; verificar em MySQL descartável assinatura, retorno, parâmetros vinculados, filtros/literais, ordenação/total, lock incluindo inativos e nenhuma senha no retorno de listagem, sem transação própria ou alteração de tabelas/FKs/migrations antigas.
- [x] 1.2 Estender referência oficial e reconhecimento/preflight para 017; verificar MySQL real em instalação limpa, upgrade 016 com dados, snapshot equivalente, baseline, reexecução zero, drift/parcial, dependência anterior inválida, falha/checksum/lock e prefixos históricos. Habilitar ambos os opt-ins de integração/migrations somente no processo e documentar pré-requisito/comandos de 017 no README.
- [x] 1.3 Implementar `UsuarioRepository`, contrato de listagem e composição por aplicação, consumindo/liberando resultados no padrão atual; verificar unidades e integração real de paginação/snapshot e bloqueio corrente, sem SQL nos Services, fallback ORM especializado ou acesso a persistência privada de outro módulo. Documentar as duas routines e a revogação existente reutilizada.

## 2. Entregar os casos administrativos de Contas

- [x] 2.1 Acrescentar validação/DTO administrativos, permitir nome/e-mail na Model e implementar criação, listagem e detalhe; verificar unidade/MySQL para perfil fixo Aluno, hash protegido, ausência de sessão/aceite automático, duplicidade normalizada, e-mail mascarado, paginação, busca literal, IDs e 404 para Administrador. Preservar `Usuario.to_dict`, cadastro público e CLI atuais.
- [x] 2.2 Implementar edição de nome/e-mail com lock e revogação atômica quando o endereço mudar; transportar o e-mail esperado nos dois pontos de lock do login/criação de sessão. Verificar unidade e concorrência MySQL real para no-op, nome sem revogação, endereço duplicado, duas contas concorrentes, login antigo nos dois intervalos e falha/rollback sem efeito parcial.
- [x] 2.3 Implementar Services separados de desativar/reativar, com confirmação e revogação existente na mesma transação; verificar MySQL real com múltiplas sessões, reenvio seguro, login concorrente, falha entre etapas, conta inativa e reativação sem restaurar cookies, preservando decisões e dados de estudo.
- [x] 2.4 Implementar exclusão pela Model condicionada às FKs, com rollback e 409 específico; verificar MySQL real em conta administrativa nova sem vínculos, conta com aceite, sessão revogada, histórico/autoria e referência concorrente, sem apagar dependências ou tocar outra conta. Verificar também sanitização dos erros e conflitos de lock.
- [x] 2.5 Criar `UsuarioController` e rotas sob `/api/admin/usuarios`, adaptar sensibilidade/cache no hook existente e erros/limite local de corpo; verificar HTTP/MySQL para 200/201/204, 400/401/403/404/409/413, HEAD/OPTIONS, campo extra, CSRF/origem, senha recente e ausência de enumeração/dados sensíveis. Documentar contratos e efeitos de sessão no README, preservando as rotas anteriores.

## 3. Entregar as duas telas administrativas

- [x] 3.1 Criar listagem `/admin/usuarios.html`, CSS/JS e navegação de Usuários, seguindo ADM-USU-001 no recorte de Alunos; verificar DOM para perfil antes das consultas, busca/status/paginação, máscara, vazio/sem resultado/rede, dados atuais e seleção do detalhe. Atualizar mapa de telas com o alcance implementado, sem habilitar filtros/perfis futuros.
- [x] 3.2 Criar `/admin/usuario.html` para criação/detalhe/edição e ações confirmadas de status/exclusão; verificar DOM de campos exatos, senha inicial somente na criação, limpeza após sucesso/saída, troca de modo/URL após POST, PUT explícito, 409 por vínculo e ausência de fallback, replay, senha em storage/URL ou funcionalidades fictícias. Documentar diferenças em relação a ADM-USU-002.
- [x] 3.3 Integrar guard/AuthUI/reauth e proteção de consultas atrasadas nas telas; verificar DOM e revisão visual a 1440/390 px para rascunho, senha limpa ao perder identidade, nova confirmação após recuperação, conta diferente, XSS como texto, teclado/foco, diálogos e ausência de overflow. Documentar desativação distinta de exclusão e limitações do recorte; preservar binários oficiais e HTMLs legais imutáveis.

## 4. Comprovar e verificar a entrega

- [x] 4.1 Acrescentar E2E com Chromium/MySQL descartável, sem interceptação: CRUD de conta nova sem vínculos, outra conta com login/aceite e DELETE bloqueado, desativação/reativação e troca de e-mail com sessões. Verificar requisições e persistência reais, registrar evidências sintéticas sem credenciais e atualizar matriz/modelagem/mapa modular/README, encerrando F01 somente para Alunos após sucesso.
- [x] 4.2 Executar regressão backend/frontend, cobertura e E2E afetado, incluindo suítes de migration habilitadas; verificar os mínimos das conventions, 29 testes originais, vinte casos anteriores, F02, sete módulos/21 mappers, hashes legais/visuais e checksums 000–016 preservados. Registrar comandos, resultados e limitações reais em `validacao.md`, sem chamadas externas ao Gemini.
- [x] 4.3 Verificar implementação contra proposal/design/specs/tasks, revisar escopo, segredos, links e UTF-8 e executar `openspec validate gerenciar-contas-de-alunos --strict`; corrigir achados críticos e confirmar rastreabilidade e separação Model/Repository. Não declarar exclusão geral, gestão de Administradores, auditoria completa ou aceite acadêmico presumido.

## Workflow follow-up

- Depois de aplicação e verificação, sincronizar as três capabilities e arquivar a change.
- Atualização de banco operacional segue o procedimento vigente de backup validado e migration; não confundir com teste em schema descartável.
- Commit/push somente após autorização explícita. Revisão técnica final, AWS, vídeo, slides e guia de estudo permanecem etapas posteriores.
