# Tarefas: consolidar a entrega acadêmica

## 1. Preflight e catálogo

- [x] 1.1 Conferir artefatos, conventions, ADRs e alterações locais antes de editar; registrar no relatório da change a preservação de `tmp/`, da change preexistente e dos binários oficiais, sem ler/expor `.env`. Verificar `git status --short` e executar os testes focados existentes de catálogo como caracterização.
- [x] 1.2 Transferir o JOIN de Assuntos ativos para `CatalogoRepository` e coordenar por `ListarAssuntosService`, mantendo compatibilidade dos consumidores da Model e CRUD Active Record. Verificar filtros/status/ordem e regressão de Matérias/Assuntos em testes unitários e MySQL real; revisar a documentação operacional se houver descrição interna afetada.

## 2. Leituras de Questões e Simulados

- [x] 2.1 Remover consultas por versão da listagem do Aluno e introduzir leitura em lote de conteúdo elegível/histórico pelo Service de Questões. Verificar DTO sem correção antecipada, versões retiradas/superadas, ordenação/paginação e testes de Questões/Práticas, sem alterar os contratos unitários nem locks das escritas.
- [x] 2.2 Buscar composições, disponibilidade, tentativas próprias em andamento, títulos e conteúdo histórico em lote nos Services/Repositories de Simulados. Verificar listagens administrativa/Aluno, detalhe/correção/histórico, estados mistos e isolamento de contas no MySQL; acrescentar teste de quantidade de SELECTs com aumento da composição/página, mantendo crescimento independente da quantidade de itens.
- [x] 2.3 Atualizar a documentação operacional de Questões/Simulados quanto às fronteiras de leitura em lote e executar regressões de início, resposta, publicação, finalização e preservação histórica. Verificar que payloads e locks dos casos de escrita continuam compatíveis.

## 3. Respostas HTTP e proteção de logs

- [x] 3.1 Caracterizar status, payloads, detalhes e headers dos Controllers e criar helper HTTP compartilhado, mantendo classes por recurso e regras nos Services. Verificar testes de Controllers/API para 200/201/204, erros esperados e 500, incluindo o formato legado de Questões.
- [x] 3.2 Migrar tratamento comum e logging de Controllers/autenticação da requisição para a política sanitizada, preservando cookies, `codigo`, Retry-After e no-store. Verificar com exceções contendo sentinelas que senha/token/SQL/parâmetros não aparecem em logs ou respostas; executar regressão de autenticação e documentar a política no documento operacional correspondente.

## 4. Navegação compartilhada

- [x] 4.1 Criar menu compartilhado em `frontend/js/navigation.js` e slots nas oito páginas do Aluno e nas páginas administrativas, mantendo molduras, IDs de formulário, usuário/logout e o MVP legado. Verificar por testes DOM links/destinos de cada ambiente, indisponíveis sem ação, indicação atual única e acesso ao Plano em todas as páginas do Aluno.
- [x] 4.2 Verificar teclado/foco, ordem de inicialização dos scripts, proteção de alterações não salvas e troca/expiração de sessão após a extração; adaptar testes existentes sem retirar cobertura de comportamento. Documentar no relatório as verificações e preservar contratos de recuperação e confirmação.

## 5. Testes de navegador com MySQL real

- [x] 5.1 Adicionar Playwright como dependência de desenvolvimento com lockfile atualizado, configuração Chromium, scripts npm e alvo Make. Verificar instalação/descoberta da suíte, separação dos testes Vitest e comandos documentados; ignorar artefatos locais de browser que não devem ser versionados.
- [x] 5.2 Implementar runner de E2E com opt-in de processo, schema aleatório validado, migrations oficiais, operador sintético, API/frontend em processos locais e limpeza em `finally`. Verificar bloqueio sem opt-in, recusa de nomes inseguros e limpeza em sucesso/falha; usar ambiente para credenciais e não alterar banco operacional.
- [x] 5.3 Implementar e executar os vinte percursos de referência da seção 5 do design pela interface com API/banco reais, comprovando persistência por recarga ou leitura independente. Verificar também exclusão vinculada bloqueada, correção não antecipada, navegação ao plano, cancelamento de descarte e smoke visual a 1440/390 px; registrar evidências sem mocks de integração, credenciais, HAR ou storage state.

## 6. Integração contínua

- [x] 6.1 Criar workflow GitHub Actions com MySQL 8 descartável, health check, Python 3.12, Node 22, permissões mínimas e timeout; executar cobertura backend/frontend e E2E com opt-ins limitados ao processo. Verificar sintaxe e reprodução local dos comandos, preservação dos gates 90%/85% e ausência de segredos/estado de sessão nos artefatos. Documentar CI no README; execução remota ficará identificada como pendente até push autorizado.

## 7. Documentação acadêmica

- [x] 7.1 Criar `docs/technical/diagrama-de-classes.md` com Mermaid legível cobrindo as vinte Models concretas, principais atributos/FKs/cardinalidades, herança por `CrudMixin(db.Model)`, versões, autoria e plano anterior. Verificar renderização e comparar com Models/migrations; não inventar entidades nem associações e explicar composição/agregação somente onde houver semântica correspondente.
- [x] 7.2 Atualizar o README com seção exata `Funcionalidades Implementadas`, vinte entradas numeradas e links para diagrama/matriz, além de stack, arquitetura, migrations 000–009 e comandos reais. Verificar cada entrada contra interface, rota, Controller, Service e persistência; datar resultados históricos e não apresentar validações não executadas como atuais.
- [x] 7.3 Criar `docs/technical/entrega-academica.md` com matriz dos vinte casos (UI/API/Controller/Service/Model/Repository/tabela/teste/evidência). Verificar links e correspondência com o README; deixar explícitos vídeo obrigatório a cargo do usuário e commit/push ainda não autorizados.

## 8. Verificação integrada

- [x] 8.1 Executar testes unitários e a suíte completa de integração/cobertura com MySQL 8 descartável, incluindo os 29 testes originais e testes de migrations com os dois opt-ins. Executar cobertura frontend, suíte do navegador e testes do servidor frontend aplicáveis; registrar comandos/resultados reais em `validacao.md` e investigar falhas antes de marcar conclusão.
- [x] 8.2 Conferir implementação versus proposta/design/delta e exigências do professor usando `openspec-verify-change`; verificar diff, ausência de mudanças no schema/procedure/binários/temporários preexistentes e ausência de segredos. Registrar relatório de verificação e resolver achados críticos antes do fechamento técnico.

## Workflow follow-up

- Sincronizar a delta de `plano-estudos-basico` com a skill `openspec-sync-specs` após a verificação.
- Arquivar esta change com `openspec-archive-change` somente com todas as tarefas concluídas e sem achados críticos; validar o estado arquivado.
- Entregar ao usuário os arquivos e resultados; o vídeo será gravado/enviado por ele.
- Commit e push ao repositório oficial somente após autorização explícita. Não condicionar a conclusão técnica local à gravação ou publicação ainda não autorizada.
