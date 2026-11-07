# Design — Monólito modular com seis domínios

## Context

Ver [proposta](proposal.md). A aplicação já tem Controllers como classes, Services por ação, Models Active Record, Repositories especializados e composição explícita. Os materiais do professor (`Arquitetura_Monolito_Modular.pdf`, `layers.pdf`, `modules.pdf`) acrescentam organização das camadas por domínio, dentro da mesma aplicação e infraestrutura.

O plano mestre atual apresenta uma visão futura mais granular; não é necessário implementar os módulos futuros para organizar o recorte entregue. Os ADRs 002, 006, 008 e 009 continuam determinando autenticação, transações, persistência e consentimento. Esta mudança desloca implementações e explicita fronteiras, sem mudar as onze specs funcionais; por isso usa `skip_specs: true`.

## Goals / Non-Goals

**Goals:** deixar visível a propriedade de cada caso de uso, entidade e rota; impedir imports de persistência privada de outro módulo; conservar os vinte casos e extensões atuais, com o mesmo MySQL e factory.

**Non-Goals:** modularização máxima, framework de plugins, regras genéricas de domínio, novo mecanismo de transação, migração de dados ou qualquer funcionalidade prevista somente no protótipo. Não alterar comportamento para acomodar a reorganização.

## Decisions

### 1. Seis módulos coesos, em vez de um módulo por entidade

Estrutura canônica:

```text
backend/app/
  __init__.py                 # factory da aplicação
  config.py, extensions.py    # configuração e ORM únicos
  composition.py              # ligações entre colaboradores
  routes.py                   # somente agregação e health
  core/                       # bases e helpers neutros existentes
  contracts/                  # Protocols/DTOs públicos sem ORM
  models/                     # registro/reexportações de compatibilidade
  modules/
    contas/
    conteudo/
    praticas/
    simulados/
    desempenho/
    plano_estudos/
```

Cada módulo contém `routes.py`, `controllers/`, `services/`, `repositories/` quando utilizados e `api.py` para colaboração externa. Models e primitivas de domínio ficam em `models/` e `domain/` do proprietário. Não criar pastas vazias, entidade de Desempenho ou tabelas fictícias para completar o desenho: Desempenho continua sendo projeção.

| Módulo | Propriedade e arquivos atuais |
| --- | --- |
| `contas` | Controllers Autenticação/Privacidade; Models `Usuario`, `Sessao`, `AuthLimite`, `RegistroPrivacidade`; Repositories Autenticação/Privacidade; `autenticacao_service.py`, `aceitar_termos_uso_service.py`, `consentir_plano_service.py`, `recusar_consentimento_plano_service.py`, `revogar_consentimento_plano_service.py`, `consultar_termos_service.py`, `consultar_privacidade_service.py`, `privacidade_validacao.py`, `validar_permissao_plano_service.py`; domínio de autenticação/privacidade; hooks HTTP e CLI de autenticação. |
| `conteudo` | Controllers Área/Matéria/Assunto/Questão; Models `AreaEnem`, `Materia`, `Assunto`, `AssuntoTransferencia`, `Questao`, `QuestaoVersao`, `QuestaoEvento`; Repositories Catálogo/Questão e adaptadores `consultas_catalogo`/`consultas_questoes`; CRUD e listagens do catálogo, impacto/status/transferência, `catalogo_validacao.py`, `criar_questao_service.py`, `gestao_questao_service.py`, `buscar_questoes_por_assunto_service.py`; domínio do catálogo. |
| `praticas` | `PraticaController`, `PraticaTentativa`, `PraticaRepository`; iniciar/consultar/responder/listar Práticas e validação específica; `ListarQuestoesAlunoService` pertence aqui como catálogo para iniciar prática, recebendo a consulta de Conteúdo por contrato. |
| `simulados` | `SimuladoController`; sete Models do arquivo `simulado.py`; `SimuladoRepository`/`consultas_simulados`; gestão, catálogo/histórico, início, consulta, resposta, finalização e validação de Simulados. |
| `desempenho` | `DesempenhoController`, `DesempenhoRepository`/`consultas_desempenho`; diagnóstico, dashboards e validação de período. Sem Model nova. |
| `plano_estudos` | `PlanoEstudoController`, `PlanoEstudo`/`PlanoEstudoItem`, `PlanoEstudoRepository`; consulta, seleção, geração, recálculo, conclusão e validação do plano; passa a possuir também a eliminação especializada dos próprios derivados. |

Os seis grupos totalizam as mesmas 21 Models: 4 + 7 + 1 + 7 + 0 + 2. Preservar nomes das classes e arquivos sempre que possível.

Contas reúne cadastro/aceites porque já são atômicos e compartilham identidade e locks. Conteúdo reúne catálogo/versionamento porque as consultas editoriais fazem JOINs e validam a mesma classificação. Separá-los agora criaria interfaces adicionais sem necessidade do recorte. A divisão futura do plano mestre permanece documentada como possibilidade, não como algo já implementado.

### 2. Uma única fonte de implementação e compatibilidade mínima

Mover os arquivos canônicos, atualizar imports internos, testes, alvos de patch e scripts conhecidos. Ao concluir, não deixar implementações de negócio nas pastas globais `controllers`, `services`, `repositories` e `domain`. Não manter uma segunda cópia funcional em diretório `legacy` nem usar aliases dinâmicos em `sys.modules`.

Manter `app.models` como registro/reexportação explícita das mesmas classes canônicas e `app.models.crud_mixin` como ponte estática para as três bases, conforme a compatibilidade do ADR-008. A ponte não redefine classes nem mapeia tabelas: exporta `ModeloBase`, `ModeloAtualizavel`, `CrudMixin` e a mesma instância `db`. Os testes passam a apontar patches para o local realmente usado, sem remover asserções para acomodar falhas.

`__init__.py` dos módulos não inicia aplicação, não registra rotas automaticamente e não importa Services em cascata. O registro de Models importa explicitamente os pacotes proprietários antes da resolução dos relacionamentos. FKs por nome e relacionamentos ORM compartilhados permanecem, mas não autorizam um Service a acessar Models privadas de outro módulo.

### 3. Núcleo neutro sem nova infraestrutura

`extensions.py` e `config.py` ficam na raiz, com as mesmas instâncias de SQLAlchemy/CORS. `TransactionManager`, `ContextoLeitura`, exceções gerais, resposta HTTP e acesso à composição também permanecem compartilhados nos arquivos atuais, com imports ajustados quando necessário. Não introduzir outro ORM, sessão, pool ou container.

Mover para `core/` somente:

- `persistencia.py`: as bases atualmente em `models/crud_mixin.py`, sem mudar capacidades ou commits/flush/guards;
- `relogio.py`: a função UTC já usada por vários domínios, retirando a dependência do relógio em autenticação;
- `paginacao.py`: os helpers existentes de paginação;
- `validacao.py`: partes puras realmente compartilhadas de corpo, parâmetros, referência/UUID e confirmação editorial, hoje emprestadas de Práticas/Questões por outros casos de uso.

Preservar mensagens, campos permitidos, normalização de UUID e limites de cada fluxo. Validadores com políticas diferentes não serão unificados: o UUID estritamente canônico de privacidade, por exemplo, continua em Contas. Wrappers locais podem preservar nomes atuais de funções específicas. Não transferir regra de disponibilidade, consentimento, correção ou estado para o núcleo.

O núcleo e `app.contracts` não dependem de módulos de negócio. O contexto de leitura importa o relógio neutro. A infraestrutura não executa DDL na inicialização; migrations continuam sendo o único caminho operacional.

### 4. Rotas próprias, URLs preservadas

Cada `routes.py` cria um Blueprint com o nome do módulo e registra somente suas Controllers. `app.routes.api_blueprint` torna-se agregador dos seis Blueprints, mantendo `/api` aplicado uma vez. Não inserir `/contas`, `/conteudo` ou outro segmento novo nas URLs existentes. `/api/health` permanece infraestrutura compartilhada, usando seu Controller/Service próprios em `core/`.

Exemplos de propriedade: Contas registra `/auth/*`, `/termos` e `/aluno/privacidade*`; Conteúdo registra catálogo e gestão/busca de Questões; Práticas registra `/aluno/questoes` e `/aluno/praticas*`; os outros três recebem seus endpoints atuais.

Capturar antes/depois o mapa completo de URL, métodos, parâmetros/conversores, defaults, redirecionamentos/strict-slashes e função responsável. `HEAD`/`OPTIONS` automáticos continuam equivalentes. Namespaces Flask internos poderão mudar de `api.<ação>` para `api.<módulo>.<ação>`: registrar a correspondência e adaptar referências internas se existirem, sem mudar HTTP. A busca atual não encontrou consumidor de `url_for`/`request.endpoint` fora do registro; confirmar no baseline.

Preservar o hook de autorização de Contas registrado uma única vez na aplicação e o hook de cache. As políticas atuais são por caminhos/métodos, não por nomes dos Blueprints; continuar protegendo rotas aninhadas, públicas, leituras de catálogo e casos de Aluno/Admin. Preservar CSRF/origem, cookie, reautenticação e neutralidade dos erros. CLI `criar-administrador`/`limpar-autenticacao` continua registrada pela factory.

### 5. Colaboração por interfaces explícitas

Imports entre módulos devem utilizar `api.py` público ou os Protocols/DTOs existentes em `app.contracts`. Proibir imports de `models`, `repositories`, `controllers`, `services`, `domain` e helpers privados de outro módulo. Não exportar Models/instâncias ORM ou classes Repository completas na API pública para contornar a regra.

Cada `api.py` declara exportações explícitas em `__all__`; imports de implementação usados só para delegação recebem nomes privados. Não usar wildcard ou descoberta automática de símbolos. A interface deve ser revisável como uma lista curta de operações de domínio e projeções autorizadas.

| Proprietário | Interface necessária aos consumidores |
| --- | --- |
| Contas | Bloquear a linha de usuário na transação corrente; validar permissão vigente do plano. A consulta do lock deve manter a semântica exata atual, sem adicionar filtro de usuário ativo ou outra validação. |
| Conteúdo | Consultar versões elegíveis/históricas, individualmente/em lote; pares elegíveis do plano; projeção de classificação histórica e contagens administrativas. Usar Services existentes para autorização/validação aplicável e Repository somente no acesso especializado. |
| Práticas | Projeções de fatos concluídos e atividades próprias, já existentes. |
| Simulados | Projeções de desempenho, atividades e contagens existentes. |
| Desempenho | Diagnóstico pelo contrato `DiagnosticoAluno`, já injetado no seletor do plano. |
| Plano | Operação interna especializada de eliminação dos planos próprios dentro da transação externa, sem rota pública. |

DTOs/dicionários continuam fora do ORM. Projeções SQLAlchemy já usadas na agregação podem ser publicadas somente como interfaces de leitura para os Repositories consumidores: o dono monta a projeção, o consumidor agrega em seu Repository e no mesmo contexto. Controllers/Services não recebem métodos de execução SQL. Não duplicar consultas ou transferir a regra de disponibilidade de Simulados para um adaptador.

`composition.py` é o ponto autorizado de ligação entre implementações e contratos; pode importar implementações proprietárias para construí-las. O registro ORM é a outra exceção estritamente delimitada para carregar Models. Nenhuma dessas exceções autoriza acesso a dados privados durante uma regra de negócio.

Grafo principal, excluindo apenas a composição que liga colaboradores:

```text
praticas ---------> conteudo
simulados --------> conteudo
desempenho -------> praticas, simulados, conteudo
plano_estudos ----> contas, conteudo, DiagnosticoAluno
todos -----------> infraestrutura/contratos comuns
```

Manter os colaboradores de leitura já recebidos por construtor e a composição por aplicação. Não criar service locator no domínio, registro dinâmico, eventos ou container de injeção.

### 6. Consentimento e plano: retirar o ciclo sem perder atomicidade

Hoje `PrivacidadeRepository` importa Models do plano e empresta seu lock de usuário; o plano importa a verificação de privacidade. A separação precisa resolver essa dependência, além de mover arquivos.

1. Mover a consulta exata de lock do usuário para o Repository de Contas e publicá-la pela interface de Contas. Privacidade usa o lock local; Plano chama essa interface sem importar `Usuario`.
2. Mover o SQL de `eliminar_planos_proprios` para o Repository de Plano, mantendo filtros por dono, ordem descendente dos planos e exclusão de itens antes dos planos. Expor um Service interno participante, sem `TransactionManager`/commit próprios e sem validar novamente consentimento para efetuar a negativa já autorizada.
3. Fazer Recusar/Revogar receberem por construtor um colaborador `Callable[[int], None]` para eliminar derivados. A composição injeta o Service interno de Plano; a Controller usa essas duas instâncias da composição. Contas não importa Plano e não chama composição a partir do Service.
4. Conservar a ordem: lock do usuário, replay/revisão/versão, evidência da negativa, eliminação e resposta; um único `TransactionManager` confirma tudo. Replay antigo não reaplica exclusão nem restaura estado. Falha na eliminação reverte também o registro da decisão.
5. Os casos de geração/recálculo/consulta/conclusão continuam verificando permissão depois do mesmo lock de usuário e antes de replay, snapshot, diagnóstico ou item. A eliminação interna não ganha endpoint nem entra como funcionalidade nova.

Assinaturas Python internas das duas negativas passarão de chamada estática para instâncias com dependência explícita; ajustar os consumidores conhecidos e testes. O contrato HTTP permanece idêntico. A operação injeta somente comportamento, nunca usuário/conexão de uma requisição em estado global. Testar duas aplicações para descartar vazamento de composição.

### 7. Banco, metadata e arquivos protegidos

Antes dos movimentos registrar uma representação estrutural das 21 Models: tabelas/colunas/tipos/defaults/índices/constraints/relacionamentos/capacidades e guards; comparar com o resultado, permitindo apenas o caminho Python canônico diferente. Cada tabela mantém uma única classe mapeada. Não recriar tabelas, alterar nomes ou executar `db.create_all()` no startup para reproduzir o exemplo didático.

Registrar e preservar SHA-256 dos SQLs 000–010, bootstrap e HTMLs legais. Não criar migration 011, mudar runner/fingerprints ou recalcular documentos de privacidade. A instância operacional não recebe baseline, upgrade, restore ou dados de teste nesta change.

### 8. Verificação e documentação junto a cada etapa

O baseline é o working tree atual, preservando `tmp/` e alterações legítimas. Registrar os resultados conhecidos e executar regressões antes/depois nas superfícies afetadas; não usar relatórios históricos como aprovação do novo código.

- Testes unitários de arquitetura: seis módulos registrados; rotas sem SQL/regra; Controllers sem persistência; Services sem SQL/`db.session`; CRUD nas bases/Models; domínio/núcleo sem Flask/composição; nenhuma importação privada cruzada nem implementação de negócio nas pastas antigas.
- Verificar imports locais e dinâmicos, não só `ImportFrom` no topo. Proibir reexportar ORM/Repository em `api.py`. As exceções são composição, registro ORM e a ponte explicitamente delimitada; não criar allowlist ampla por pastas antigas.
- Testes de factory/mapa de rotas/metadata não abrem banco e não leem `.env`; configuração sintética MySQL é suficiente. Verificar registro repetido em instâncias independentes e uma única identidade ORM, sem SQLAlchemy duplicado.
- Integrações MySQL reais: regressão original, propriedade/perfis, versões e histórico, índices/FKs, procedure, concorrência e negativa/geração do plano; falha de eliminação deve comprovar rollback com fixture real em schema descartável, sem mocks. Reutilizar os testes existentes e acrescentar apenas lacunas criadas pela nova fronteira.
- Preservar asserções de negócio ao atualizar imports/patches. O novo teste de arquitetura protege fronteiras e invariantes, não quantidade de arquivos ou uma fotografia semântica vazia.
- Antes do fechamento executar cobertura backend completa com os dois opt-ins e gates atuais (90% linhas/85% branches, nenhum arquivo executável sem cobertura), testes do servidor frontend e uma execução dos três E2E existentes com MySQL descartável. Frontend de produção não muda; cobertura frontend já existente só precisa ser repetida se surgir uma alteração autorizada nessa superfície.

Documentar cada módulo concluído com propriedade/entradas/saídas e evidência em `validacao.md` desta change. No primeiro grupo criar o ADR-010, registrando estas decisões; ao final, atualizar README, conventions de estrutura/arquitetura, documentação operacional com paths, aplicação SOLID, matriz e diagrama. Criar `docs/technical/organizacao-modular.md` como mapa conciso das seis propriedades/interfaces. Acrescentar ao plano mestre a situação implementada, mantendo a visão futura identificada como roadmap. Não reescrever relatórios arquivados ou os ADRs anteriores; apenas relacioná-los ao novo adendo/ADR e corrigir links operacionais atuais.

O ADR-010 atualiza explicitamente a localização da operação especializada citada no ADR-009: ela passa do Repository de Privacidade para o proprietário Plano, chamada pelo colaborador participante. A política de negativa/eliminação, os guards e a atomicidade do ADR-009 continuam iguais. Registrar também a nova localização canônica das bases, preservando a ponte prevista no ADR-008.

O contexto textual de `openspec/config.yaml` pode refletir módulos, mantendo `schema`, `rules`, `operations` e guardrails. Specs principais não recebem alterações funcionais. Os PDFs do professor servem de referência de organização; não autorizam adotar SQLite, criar entidades de exemplo ou substituir migrations por `create_all()`.

## Risks / Trade-offs

- [Mudar imports altera alvos de patch sem testar o caminho real] → Atualizar consumidor/alvo canônico e manter asserções de negócio; executar primeiro a regressão do módulo movido.
- [Factory registra classe/Blueprint duas vezes] → Registro explícito, imports leves, testes de duas aplicações e inventário de mappers/rotas.
- [Módulos apenas aparentes com acesso cruzado a dados privados] → Interfaces publicadas e testes de fronteira, inclusive imports dentro de funções.
- [Refatoração da negativa perde rollback ou ordem de lock] → Colaborador participante sem commit e testes MySQL de falha/concorrência/replay.
- [API pública vira atalho de acesso ao ORM] → Somente Services/DTOs e projeções de leitura delimitadas; sem exportar Models/Repository inteiro.
- [Granularidade diferente da visão futura] → Seis módulos aprovados para o recorte atual, com justificativa no ADR; nenhum recurso futuro simulado.
- [Movimentos grandes dificultam a revisão] → Grupos por módulo, validação/documentação no próprio grupo e nenhuma mudança incidental de regra/estilo/frontend.

## Migration Plan

1. Registrar baseline e invariantes, depois preparar núcleo e testes de fronteira sem mudar comportamento.
2. Extrair Conteúdo, Práticas e Simulados, com interfaces e rotas próprias; validar e documentar cada grupo.
3. Extrair Desempenho e adaptar agregações aos produtores públicos.
4. Extrair Contas e Plano em um grupo acoplado, eliminando a dependência circular com o colaborador transacional. Manter a aplicação funcional nos pontos de validação; passagens temporárias são removidas antes da conclusão.
5. Consolidar factory/registro, atualizar consumidores, remover as implementações antigas, completar documentação e executar regressão integrada.

Em cada grupo, retirar do arquivo central as rotas já transferidas antes de registrar o Blueprint correspondente; as rotas ainda não migradas permanecem funcionais. Reexportações estáticas temporárias podem sustentar consumidores durante um movimento, sem redefinir classes, mas devem desaparecer ao atualizar os consumidores; ao final restam somente as duas pontes de Models delimitadas. Os testes de fronteira acompanham os módulos concluídos, e o gate final exige o conjunto completo, sem ampliar exceções para mascarar pendências.

Não existe migração de banco. Em caso de falha, restaurar somente os movimentos/imports/hunks desta change usando seu baseline, preservando SQLs/dados e alterações externas; não usar reset destrutivo do repositório. Nenhum commit/push/deploy é realizado por este planejamento ou automaticamente pelo apply.
