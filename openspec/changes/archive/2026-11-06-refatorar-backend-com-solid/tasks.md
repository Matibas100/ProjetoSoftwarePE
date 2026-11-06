# Tarefas: refatorar o backend com SOLID

## 1. Baseline e critérios de preservação

- [x] 1.1 Ler artefatos, AGENTS.md, conventions, arquitetura mestre e ADRs aplicáveis; registrar o estado local e os diffs preexistentes em `validacao.md` desta change, sem expor segredos nem alterar a entrega anterior, `tmp/` ou a change vazia. Verificar que a refatoração parte da consolidação já aplicada, sem reset/stash/commit automático.
- [x] 1.2 Caracterizar os payloads/erros das nove consultas e as capacidades atuais das Models com as suítes focadas existentes de catálogo, Services, Controllers, Questões versionadas, Simulados, desempenho e plano. Registrar comandos e resultados reais; verificar disponibilidade de MySQL 8 descartável com opt-in antes das integrações, sem fallback para mocks/SQLite.

## 2. Capacidades de persistência e herança

- [x] 2.1 Extrair `ModeloBase` e `ModeloAtualizavel` abstratas e manter `CrudMixin` como extensão de CRUD completo pelo caminho único até `db.Model`. Verificar testes do CRUD convencional (retornos, campos permitidos, flush, commit, rollback e `confirmar=False`) e metadados/mappers sem novas tabelas/colunas; documentar a hierarquia e a compatibilidade do import legado no diagrama e no ADR-008.
- [x] 2.2 Migrar `QuestaoVersao`, `QuestaoEvento`, `SimuladoVersao`, `SimuladoVersaoItem` e `SimuladoEvento` para `ModeloBase`, removendo a promessa de atualizar/deletar e preservando guards ORM. Adaptar testes internos para verificar ausência das capacidades e recusa de mutação/exclusão via ORM, com rollback e conteúdo/eventos intactos no MySQL; atualizar as respectivas visões do diagrama e exemplos LSP/ISP em `aplicacao-solid.md`.
- [x] 2.3 Migrar `PlanoEstudo` e `PlanoEstudoItem` para `ModeloAtualizavel`, mantendo apenas transições permitidas e bloqueio ORM de exclusão/snapshot. Verificar geração/recálculo/conclusão, imutabilidade de histórico, replays e falhas compostas em testes unitários e MySQL; atualizar diagrama e documentação do plano sem mudar seu contrato HTTP.

## 3. Contratos e composição

- [x] 3.1 Criar os Protocols e registros de leitura definidos no design em `backend/app/contracts/`, incluindo contexto opaco/escopo de leitura e diagnóstico reutilizável. Verificar que contratos não importam Flask, ORM, Models ou Repositories concretos e que cada interface contém apenas a capacidade consumida; documentar assinaturas e formatos em `aplicacao-solid.md`, sem criar Repository CRUD genérico.
- [x] 3.2 Criar `backend/app/composition.py` e registrar composição própria por aplicação na factory; disponibilizar acesso somente à camada HTTP. Verificar inicialização sem conexão ao banco, composição isolada entre duas aplicações, ausência de identidade/conexão capturada e substituição explícita de colaboradores em unitários; registrar a decisão de composição no ADR-008. Acrescentar ligações reais à medida que cada domínio for convertido, sem anunciar consultas migradas antes da hora.

## 4. Consultas do catálogo

- [x] 4.1 Converter `ListarMateriasAdminService` e `ListarAssuntosAdminService` para construtores com os respectivos contratos; acrescentar adaptadores especializados e migrar Controllers/consumidores/testes para instâncias compostas. Verificar validações, combinação de filtros, paginação, contagens, representação dos campos e 401/403 com unitários e integrações reais; manter CRUD nas Models.
- [x] 4.2 Demonstrar substituição das consultas do catálogo por duas implementações válidas nos unitários, sem alterar a lógica do Service nem conectar ao MySQL; executar a mesma semântica com o adaptador MySQL em integração. Documentar o exemplo real de DIP/OCP e as ligações do catálogo no diagrama de aplicação, com referências aos testes.

## 5. Consultas de Questões

- [x] 5.1 Converter `BuscarQuestoesPorAssuntoService` para receber consulta e verificação de existência por dependências obrigatórias; compor a verificação com `Assunto.buscar_por_id`, sem duplicar CRUD. Migrar Controller/consumidores/testes e verificar 400/404, payload/ordem administrativos e `CALL` exclusivamente no Repository com a suíte legada real, incluindo os cenários originais.
- [x] 5.2 Converter `ListarQuestoesAlunoService` para contrato que devolve registros seguros já obtidos em lote; migrar consumidores e verificar paginação, versão atual elegível, retirada/superação, ausência de gabarito/explicação e SELECTs constantes em unitários/MySQL. Atualizar operação de Questões e exemplo de contrato pequeno no documento SOLID, preservando a fronteira de conteúdo.

## 6. Consultas de Simulados

- [x] 6.1 Converter `ListarSimuladosAlunoService` para consulta de catálogo e elegibilidade recebidas por construtor; implementar/adaptar leituras em lote e compor pelo módulo de inicialização. Verificar estados disponíveis/retirados, tentativas próprias versus alheias, ordem, paginação e consultas constantes em testes unitários/MySQL, sem alterar os locks dos inícios/respostas/finalizações.
- [x] 6.2 Converter `ListarHistoricoSimuladosService` para consulta histórica própria com título/resultado em lote, migrando Controller/consumidores/testes. Verificar propriedade, resultado persistido, retirada posterior do conteúdo e representação de datas, além da regressão de detalhe/correção não convertidos; atualizar documentação operacional e ligações de Simulados no diagrama de aplicação.

## 7. Desempenho, dashboards e integração com o plano

- [x] 7.1 Converter `ConsultarDesempenhoService` para receber consulta de métricas e escopos de leitura, expondo o contrato `DiagnosticoAluno` sem importar infraestrutura concreta. Verificar fórmula, denominador, períodos UTC, grupos históricos e amostra em unitários com alternativas de contrato e integrações MySQL; documentar o exemplo SRP/DIP e a fronteira de contexto.
- [x] 7.2 Converter os dois Services de dashboard para dependências pequenas de diagnóstico/atividades/contagens/escopos e migrar Controllers para a composição. Verificar snapshot/relógio compartilhados, propriedade, contagens administrativas sem dados individuais, até cinco atividades, falha completa e consultas concorrentes com os testes de desempenho reais; atualizar documentação de operação e diagrama de aplicação.
- [x] 7.3 Adaptar `SelecionarPlanoService`, `GerarPlanoService`, `RecalcularPlanoService` e a função interna `gerar` para receber o diagnóstico/seletor composto, atualizando o Controller de plano e todos os consumidores internos/testes. Verificar a mesma base do diagnóstico, contexto externo não encerrado, seleção/locks/replays e rollback integral, sem refatorar outras dependências de escrita; documentar o limite dessa adaptação no exemplo SOLID e na matriz acadêmica.

## 8. Evidência acadêmica e coerência arquitetural

- [x] 8.1 Completar `docs/technical/aplicacao-solid.md`, ADR-008 e índice de ADRs; revisar exemplos/documentação já entregues nas tarefas anteriores. Verificar um caso concreto e teste por princípio, uma troca de implementação sem edição do Service, interfaces mínimas e os limites honestos do recorte. Não copiar os PDFs nem criar dependência de caminhos locais do usuário.
- [x] 8.2 Finalizar README, diagrama de domínio/aplicação e matriz dos vinte fluxos com os símbolos e composição finais. Renderizar os diagramas, conferir links/cardinalidades/herança e correspondência com as vinte Models e casos de uso; atualizar somente as referências normativas necessárias à nova hierarquia. Não reescrever ADRs históricos, produzir roteiro/vídeo ou contar refatoração como nova funcionalidade.

## 9. Verificação integrada e fechamento técnico

- [x] 9.1 Executar verificação estrutural focada nas nove classes: dependências obrigatórias por construtor, ausência de imports de Model/Repository concreto, `current_app`, SQL e resolução própria de implementação; conferir Controllers, contratos e composição. Verificar que as alternativas unitárias exercitam comportamento, não apenas existência do Protocol, e que schemas/migrations/procedure/frontend oficial não sofreram alteração.
- [x] 9.2 Executar cobertura completa backend com MySQL 8 descartável e os dois opt-ins de integração, incluindo as 29 integrações originais, migrations, imutabilidade e concorrência; executar cobertura frontend, regressão do servidor aplicável e os vinte percursos Playwright com API/MySQL reais. Registrar resultados atuais e gates 90%/85% sem arquivo executável zerado; não marcar sucesso com MySQL/browser indisponível.
- [x] 9.3 Executar `openspec-verify-change`, conferir implementação versus proposta/design e resolver achados críticos. Registrar verificação, diffs da refatoração versus baseline anterior, preservação de credenciais/artefatos e pendências externas de publicação; validar a change com `openspec validate refatorar-backend-com-solid --strict` antes do fechamento.

## Workflow follow-up

- Registrar sincronização de specs como não aplicável: `skip_specs: true`, sem delta funcional; preservar as specs existentes.
- Arquivar com `openspec-archive-change` somente após tarefas concluídas e verificação sem achados críticos; conferir links e o estado final arquivado.
- Apresentar os resultados e o link do repositório para o checkpoint, distinguindo conclusão local e envio externo.
- Fazer commit/push/conferência remota somente após autorização explícita; o envio do link da atividade é do usuário. Não produzir roteiro nem vídeo.
