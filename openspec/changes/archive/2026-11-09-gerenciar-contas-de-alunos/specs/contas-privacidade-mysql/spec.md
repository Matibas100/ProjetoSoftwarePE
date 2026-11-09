# Spec Delta

## ADDED Requirements

### Requirement: Consultas administrativas de Alunos por procedures
A listagem administrativa SHALL usar `sp_alunos_admin` com filtros/paginação vinculados, retorno limitado e total no mesmo snapshot. Mutações sobre conta existente SHALL usar `sp_usuario_gestao_bloqueado` para ler a identidade corrente sob lock, incluindo inativos. CALL SHALL permanecer no Repository e as routines SHALL NOT confirmar/reverter transações. CRUD e validações SHALL continuar na aplicação/Model.

#### Scenario: Paginar e conferir total consistente
- **GIVEN** Alunos e Administradores, com status e datas distintos
- **WHEN** a consulta administrativa recebe filtros válidos
- **THEN** a procedure retorna somente Alunos nos campos de apresentação previstos, sem senha/hash, com ordem estável e total correspondente aos mesmos filtros e snapshot

#### Scenario: Bloquear conta sem usar snapshot antigo
- **GIVEN** instância de usuário carregada antes de alteração concorrente
- **WHEN** uma mutação administrativa obtém o lock do alvo
- **THEN** a aplicação recebe a linha corrente, sem filtro de ativo e sem sobrescrever campos com a instância antiga; perfil e existência são verificados antes da escrita

#### Scenario: Preservar routines e fronteiras anteriores
- **WHEN** casos administrativos usam revogação de sessões ou retornam conflito de exclusão
- **THEN** reutilizam a revogação existente na transação do caso, não consultam persistência privada de outros módulos e não modificam procedures antigas, decisões, FKs ou política de limpeza

### Requirement: Falhas administrativas não deixam efeitos parciais
Falha em criação, atualização, status ou exclusão administrativa SHALL reverter a transação integralmente. Leitura bloqueante e revogação SHALL usar a mesma conexão da operação. Procedure ausente/divergente SHALL produzir falha segura, sem fallback ORM de consulta especializada. Exclusão SHALL manter FKs como autoridade final, sem desabilitá-las nem remover dependências para forçar sucesso.

#### Scenario: Falhar entre desativação e revogação
- **WHEN** a operação falha depois de alterar o ativo e antes de confirmar revogações
- **THEN** o rollback mantém estado e sessões anteriores, não altera outra conta nem anuncia sucesso parcial

#### Scenario: Nova referência durante exclusão
- **WHEN** a exclusão encontra uma referência protegida, inclusive criada concorrentemente
- **THEN** a conta é preservada com erro seguro 409, sem consulta SQL dinâmica, limpeza em cascata ou bypass dos guards de evidência

#### Scenario: Routine administrativa indisponível
- **WHEN** listagem ou lock não pode executar sua routine oficial
- **THEN** a API falha sem expor SQL/dados de conta e sem mudar para consulta ORM especializada alternativa
