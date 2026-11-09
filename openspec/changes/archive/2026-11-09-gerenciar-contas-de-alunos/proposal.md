# Proposal

## Why

O sistema permite cadastro e login, mas ainda não oferece a gestão administrativa da Model Usuario, registrada como F01 na matriz CRUD. A equipe escolheu completar esse recorte para contas de Aluno, com exclusão condicionada e preservação dos dados existentes, antes da revisão final da entrega.

## What Changes

- Entregar o recorte de ADM-USU-001/002 para Administrador criar, listar, consultar e editar nome/e-mail de Alunos, desativar/reativar e excluir somente contas sem vínculos impeditivos.
- Criar rotas sob `/api/admin/usuarios`, Controller em classe e Services por caso de uso no módulo Contas. Não permitir escolher/promover perfil ou administrar contas de Administrador.
- Criar contas administrativas de Aluno com senha inicial protegida, sem sessão automática nem aceite de termos em nome do titular. Cadastro público continua com seu aceite obrigatório atual.
- Desativar e revogar sessões na mesma transação; reativação não recupera sessões antigas. Alterar e-mail revoga as sessões e impede finalizar login com identificação antiga, inclusive sob concorrência.
- Manter CRUD básico na Model e usar Repository/procedures somente para a listagem paginada/filtrada e a leitura bloqueante necessária às mutações.
- Acrescentar migration 017 com duas procedures, snapshot e reconhecimento equivalente, sem alterar tabelas, FKs, evidências ou migrations aplicadas.
- Implementar listagem e formulário/detalhe com a identidade visual oficial, confirmação, reautenticação, proteção de rascunho e estados reais. Atualizar README, matriz CRUD e evidências após testes ponta a ponta.

### Fora de escopo

Gestão de Administradores, alteração de perfil, reset/recuperação de senha, envio de e-mail, verificação de endereço, exclusão em cascata, anonimização, eliminação de histórico/aceites, auditoria administrativa completa, exportação, visualização de estudos individuais por Administrador e implantação para dados reais. Operações futuras dos protótipos permanecem indisponíveis.

## Capabilities

### New Capabilities

- `gestao-administrativa-alunos`: gestão ponta a ponta das contas de Aluno pelo Administrador, com proteção de identidade, sessões e vínculos.

### Modified Capabilities

- `contas-privacidade-mysql`: interfaces especializadas de listagem administrativa e leitura bloqueante de usuário, complementando as routines de autenticação já existentes.
- `migrations-sql`: instalação, equivalência e reconhecimento conservador do prefixo 017.

## Impact

- Backend: Contas ganha `UsuarioController`, Services CRUD/status e `UsuarioRepository`; Model Usuario mantém CRUD, com nome/e-mail permitidos para atualização e serialização administrativa separada. Login recebe verificação do e-mail esperado nos pontos de lock, preservando o contrato HTTP atual.
- API: listagem/criação em `/api/admin/usuarios`; detalhe/edição/exclusão em `/api/admin/usuarios/{id}`; ações explícitas de desativar/reativar. Leituras exigem Administrador e mutações também Origin/CSRF e senha recente.
- MySQL: somente duas definições novas em 017: `sp_alunos_admin` e `sp_usuario_gestao_bloqueado`. Atualizar referência/runner/bootstrap conforme ADR-001, sem novo esquema de dados. FKs existentes decidem os vínculos impeditivos da exclusão.
- Frontend: `/admin/usuarios.html` e `/admin/usuario.html`, navegação e CSS/JS próprios reaproveitando shell, AuthUI e AdminUI. Referências oficiais: protótipo páginas 58–59, preservado integralmente; registrar diferenças do recorte aprovado.
- Arquitetura: sete módulos e 21 mappers permanecem. ADRs 002, 006, 008 e 010 orientam segurança, atomicidade, Active Record e fronteiras. Não criar nova camada ou dependência.
- Compatibilidade: cadastro público, CLI de Administradores, contrato `Usuario.to_dict`, termos publicados, consentimento/plano, Tutor e os vinte casos anteriores permanecem. A gestão não presume aceites nem converte desativação em revogação do plano.
- Documentação: F01 será encerrada para este recorte de Alunos somente depois de comprovados CRUD, limites e sessões; E01–E03 e critérios de aceitação acadêmica permanecem independentes. Os dados e alterações locais da change anterior serão preservados; não há autorização de commit/push nesta proposta.
