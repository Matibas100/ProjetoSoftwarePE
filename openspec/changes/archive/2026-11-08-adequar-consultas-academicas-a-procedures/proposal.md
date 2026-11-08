# Proposta — Adequar consultas acadêmicas a procedures

## Why

O enunciado de funcionalidades de acesso ao banco exige consultas além do CRUD por procedures encapsuladas em Repository. A busca de Questões por Assunto já atende, mas listagens administrativas e desempenho ainda executam consultas SQLAlchemy; esta primeira etapa corrige um recorte fechado e demonstrável sem reescrever o backend.

## What Changes

- Migrar as listagens administrativas de Matérias, Assuntos e Questões, o diagnóstico de desempenho e os dashboards do Aluno e da Administração para procedures, preservando telas, filtros, paginação, autorização e JSON atuais.
- Criar sete procedures de leitura e quatro views de contrato entre módulos, conforme o [inventário](inventario-consultas.md). As views permitem agregar fatos históricos sem abrir acesso irrestrito às tabelas privadas de outros módulos.
- Acrescentar migrations `011_consultas_admin_procedures.sql` e `012_desempenho_procedures.sql`, consolidar o bootstrap e reconhecer esses estados com segurança. Preservar SQLs/checksums `000`–`010`, tabelas, dados e `sp_questoes_por_assunto`.
- Tratar resultados múltiplos das procedures na mesma conexão/transação do caso de uso, sem commit interno ou fallback ORM silencioso.
- Acrescentar testes MySQL reais de equivalência, isolamento, filtros, ordenação, paginação e reaproveitamento de conexão; atualizar a documentação acadêmica com procedimentos, rotas e pendências reais.

### Limites

Não converter CRUD básico, autenticação, privacidade, locks, operações de escrita, histórico de Práticas, catálogo/execução de Simulados, seletores de Plano ou outras consultas fora do inventário desta etapa. Não criar novas funcionalidades, alterar regras de negócio, redefinir Models, instalar frameworks ou mudar visuais oficiais. As consultas restantes ficam registradas para próximas changes: concluir esta não significa adequação integral ao enunciado.

## Capabilities

### New Capabilities

- `consultas-academicas-mysql`: contrato de leitura por procedures para as seis consultas HTTP delimitadas, incluindo interfaces SQL entre módulos, parâmetros vinculados, resultados e participação transacional.

### Modified Capabilities

- `migrations-sql`: acrescentar reconhecimento conservador e equivalência dos recursos SQL oficiais dos prefixos 011/012, preservando os estados anteriores.

As regras funcionais existentes de catálogo, gestão administrativa, desempenho e Plano continuam válidas; muda a implementação de leitura, sem alterar os seus contratos HTTP.

## Impact

- **Rotas preservadas:** `GET /api/admin/materias`, `/api/admin/assuntos`, `/api/admin/questoes`, `/api/aluno/desempenho`, `/api/aluno/dashboard` e `/api/admin/dashboard`.
- **Telas preservadas:** `frontend/admin/{materias,assuntos,questoes,dashboard}.html` e `frontend/aluno/{desempenho,inicio}.html`. Nenhuma mudança visual planejada.
- **Código:** Repositories/adaptadores de Conteúdo e Desempenho; contagens de Simulados; serialização das três listagens; primitivas neutras para cursor e acesso participante ao ContextoLeitura; contratos públicos SQL mínimos dos proprietários. Controllers/Services mantêm suas responsabilidades e não executam CALL.
- **Banco:** sete procedures e quatro views, sem tabelas/colunas/FKs novas. Instalação exige privilégios DDL correspondentes; aplicação exige EXECUTE/SELECT adequados, sem credenciais hardcoded.
- **Decisões:** complementar ADRs 001, 006, 008 e 010 com um ADR-011 de interfaces SQL de leitura; preservar snapshots, transações e classificação histórica dos ADRs 005/009.
- **Validação:** regressões afetadas e ampliadas, 29 integrações originais, schemas descartáveis, gates de arquitetura e cobertura atuais e E2E existente. Sem testes de integração substituídos por mocks/SQLite.
- **Dependência:** a change documental `formalizar-modelagem-e-cobertura-crud` está sendo concluída em paralelo; preservar suas alterações e integrar links somente após conferir seu conteúdo final. Ela não é dependência de runtime. Não realizar commit, push, deploy ou migration no banco de uso durante o planejamento.
