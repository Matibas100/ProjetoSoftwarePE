# Design: consolidação da entrega acadêmica

## Context

Ver `proposal.md` para motivação e escopo. A aplicação já tem catálogo, autenticação, Questões versionadas, Práticas, Simulados, Desempenho e Plano. A arquitetura aceita mantém camadas em `backend/app/` e CRUD Active Record por `CrudMixin(db.Model)`. Não será necessário mover essas pastas nem criar migrations.

A consulta `Assunto.listar_ativos()` faz JOIN na Model; as leituras de Questões elegíveis e Simulados repetem consultas por item. Controllers têm wrappers similares com tratamento divergente de erro e traceback. Navegação repetida em HTML deixou o Plano ausente em seis das oito páginas do Aluno. Vitest/jsdom não comprova o fluxo em navegador real; não existe workflow CI versionado. O repositório remoto é hospedado no GitHub.

## Goals / Non-Goals

**Goals:** reduzir acoplamento e trabalho repetido mantendo comportamento; comprovar os casos acadêmicos por interface/API/banco real; documentar o domínio implementado e a entrega reproduzível.

**Non-Goals:** reorganizar todo o monólito em módulos, mudar regras editoriais, introduzir API/estado/modelo novo, editar dados operacionais ou produzir o vídeo. Tampouco tratar automação, segurança ou diagrama como funcionalidades adicionais na contagem.

## Decisions

### 1. Consultas especializadas e compatibilidade da Model

Adicionar listagem especializada em `CatalogoRepository` com os mesmos filtros de status de Assunto e Matéria, ordenação por nome normalizado/ID e filtro opcional de Matéria. `ListarAssuntosService` passa a coordenar esse Repository. CRUD e `listar_todos()` continuam nas Models. Se `Assunto.listar_ativos()` tiver consumidores internos/testes, mantê-lo como delegação compatível sem SQL/JOIN ou atualizar esses consumidores na mesma tarefa; a API não muda.

Alternativa rejeitada: manter JOIN na Model ou duplicar cadastro/edição no Repository. São incompatíveis com a divisão obrigatória. Não migrar os demais CRUDs nem criar camada extra para cada método.

### 2. Leituras em lote mantendo a fronteira do conteúdo

Criar contrato interno de leitura em lote no Service de Questões para elegibilidade/conteúdo histórico. A validação de uso continua sendo do módulo de Questões; Repositories executam consultas parametrizadas. Preservar as operações unitárias e os locks usados por criar/publicar/iniciar/responder/finalizar.

Nas leituras:

- `ListarQuestoesAlunoService`: serializar as versões já obtidas por consulta elegível, sem consultar cada versão de novo. Manter DTO sem gabarito/explicação.
- Listagem administrativa de Simulados: obter composição dos IDs da página em lote, respeitando rascunho versus versão publicada.
- Catálogo do Aluno: obter composições da página, conjunto de versões elegíveis e tentativas próprias em andamento em consultas por conjunto. Uma versão retirada continua tornando o simulado indisponível. GET não adquire os locks de início de tentativa.
- Detalhe/correção: buscar versões históricas de todos os itens em lote por Service autorizado, sem expor correção antes de finalização. Histórico pode buscar títulos por conjunto.

Teste de consultas no MySQL compara cenários pequenos e grandes: a quantidade de SELECTs de cada leitura não cresce proporcionalmente ao número de itens. Incluir cenário misto (disponível/retirado e tentativa de outro Aluno) e regressões de publicação/transferência/histórico. Evitar um teto absoluto frágil que conte renovação da sessão junto da consulta de domínio.

Alternativa rejeitada: cache global. Introduziria invalidação de elegibilidade e risco de isolamento entre usuários sem necessidade comprovada.

### 3. Adaptação HTTP comum com contratos explícitos

Adicionar helper de resposta em `backend/app/` para transformar sucesso/erro esperado e registrar falha interna sanitizada. Controllers permanecem classes ligadas aos recursos e continuam chamando Services. O helper não conhece regras de catálogo, autoria ou persistência.

Preservar status de criação/204, envelopes, `detalhes`, formato legado de erro de Questões e contratos particulares da autenticação (`codigo`, Retry-After, limpeza de cookie). Respostas Flask já montadas por autenticação não devem ser serializadas de novo. A autenticação da requisição usa a mesma política sanitizada de logging sem transferir suas regras para o helper. Não adicionar handler global que altere erros de roteamento/HTTP não relacionados.

Falhas inesperadas registram somente mensagem fixa de contexto e nome da classe da exceção; não registram `str(exception)`, traceback com exceção SQL, parâmetros, corpo, query string, headers, cookie ou configuração. Nenhuma resposta 500 expõe esses valores. Testar com sentinelas de senha/token/SQL em exceções simuladas, além de status e headers esperados. Não adicionar correlação pública ou novos campos de payload nesta change.

Alternativa rejeitada: trocar todos os erros por um envelope novo, que quebraria consumidores. Wrappers de sucesso específicos podem permanecer quando necessários; a parte comum será reutilizada sem criar uma classe-base de negócio.

### 4. Menu compartilhado, sem substituir páginas

Adicionar `frontend/js/navigation.js` com definições constantes por ambiente e renderização de slots explícitos nos menus de `frontend/aluno/*.html` e `frontend/admin/*.html`. Compartilhar apenas itens do menu, indicação atual e recursos indisponíveis; preservar logos, molduras, cabeçalhos, formulários, usuário real e logout. O script é executado antes dos scripts de sessão/tela quando necessário para o registro de eventos.

Menu do Aluno: início, questões, histórico, simulados, desempenho e plano; Resumos/Tutor continuam marcadores sem ação. Resolução e execução indicam suas respectivas seções como atuais; o Plano marca somente seu próprio link. Menu administrativo mantém os destinos existentes e itens indisponíveis. O `frontend/index.html` legado mantém seus scripts e estrutura.

Usar elementos/atributos estáveis, nomes acessíveis, foco via CSS existente e uma única indicação `aria-current="page"` por menu. Menus renderizados continuam sujeitos às confirmações de alterações não salvas e aos handlers de troca de identidade. Atualizar testes DOM e verificar no navegador a 1440 px e 390 px, sem afirmar que houve redesign mobile. Não alterar os binários visuais oficiais.

Alternativas rejeitadas: migração para framework ou templates servidos por Flask, que ampliariam implantação/contratos; duplicar manualmente o link, que manteria a causa da inconsistência.

### 5. Evidência de vinte funcionalidades de ponta a ponta

Os vinte casos de referência serão os listados abaixo. A matriz final inclui tela/ação, método/rota, Controller, classe Service, Model/Repository/tabela, teste correspondente e resultado realmente observado.

| ID | Caso de uso | Interface principal |
|---|---|---|
| 1–4 | Cadastrar, listar, atualizar e excluir Matéria sem vínculos | `/index.html` e gestão de Matérias |
| 5–8 | Cadastrar, listar, atualizar e excluir Assunto sem vínculos | `/index.html` e gestão de Assuntos |
| 9–10 | Cadastrar Questão e buscar por Assunto | `/index.html` |
| 11–12 | Cadastrar Aluno e fazer login | `/cadastro`, `/login` |
| 13–15 | Editar, publicar e arquivar Questão | `/admin/questao.html` |
| 16–18 | Iniciar prática, responder com correção e consultar histórico | páginas de Questões/Histórico do Aluno |
| 19 | Criar Simulado manual | `/admin/simulado.html` |
| 20 | Consultar desempenho por Matéria/Assunto | `/aluno/desempenho.html` |

Criar testes Playwright com Chromium e scripts npm/Make. Um runner Python dedicado prepara schema aleatório com prefixo rigidamente validado, aplica migrations oficiais nesse schema, cria operador de teste via Service existente e inicia API/frontend em processos locais. Credenciais geradas e URL do schema vão somente no ambiente dos subprocessos; nunca em argumentos/logs/relatórios. Exigir opt-in no processo; sem opt-in ou sem MySQL falhar, não pular a suíte nem usar mocks/SQLite. O runner deve limpar processos e schema em `finally` e validar o nome antes de qualquer DROP. Dados de aluno/conteúdo utilizados na demonstração são cadastrados pela UI ou por setup claramente separado; o caso em avaliação sempre é executado pela interface real.

Os testes verificam requisições reais e persistência por recarga e/ou leitura independente no mesmo schema descartável. Não interceptar respostas da API para simular sucesso. Fluxos encadeados são permitidos (cadastro/publicação antes da prática), com dados exclusivos; exclusão usa registros sem vínculos e testa também o bloqueio de vinculado. A conta pública nunca ganha perfil administrativo. Acrescentar smoke de navegação das oito páginas e cancelamento de saída com resposta local não salva.

A dependência Playwright fica somente em desenvolvimento, com versão resolvida/fixada no lockfile e browser instalado pelo comando documentado. A instalação não altera dependências de produção. Autenticação, banco e migrations mantêm suas próprias suítes completas.

### 6. CI reproduzível no GitHub

Criar workflow em `.github/workflows/` para `push`, `pull_request` e disparo manual; não executar nenhum push. Usar runner Linux, Python 3.12, Node 22 e serviço MySQL 8 com health check. Credenciais exclusivas de teste são efêmeras; a chave de autenticação é gerada para o job. Variáveis e opt-ins são limitados aos processos de teste.

Executar `npm ci`, instalação de requirements-dev, testes/cobertura backend com os dois opt-ins de integração, cobertura frontend e navegador. Os gates atuais de 90%/85% e a reprovação de arquivo executável zerado permanecem. Configurar timeout, permissão mínima `contents: read` e limpeza. Relatórios não contêm estado de autenticação, dumps nem `.env`; não publicar traces/HAR/storage state. Screenshots, se usados, são exclusivamente das contas sintéticas do schema de teste.

Alternativa rejeitada: depender apenas do pre-push, que depende da configuração de cada clone. O hook permanece compatível; a suíte de navegador terá comando próprio para não aumentar silenciosamente seu escopo.

### 7. Diagrama, README e matriz de funcionalidades

Criar diagrama de classes em Markdown/Mermaid versionável, dividido em visões legíveis por domínio com uma visão de herança. Cobrir as vinte Models concretas atuais e `CrudMixin` abstrata, atributos principais, chaves estrangeiras, cardinalidades, ponteiros opcionais de versão atual, autor/ator e autoassociação de plano anterior. Indicar herança de `db.Model` via mixin. Composição/agregação só será usada onde a semântica estiver sustentada pelo domínio; `RESTRICT` não será apresentado como cascata destrutiva. `AuthLimite`, sem FK de usuário, não ganhará associação inventada. Desempenho é projeção, não uma Model fictícia.

README é a lista numerada oficial, com vinte entradas separadas e outras entregues identificadas adicionalmente quando verificadas. A matriz apenas referencia essa numeração. Atualizar migrations até 009, capacidade atual do `QuestaoRepository`, comandos, requisitos e links; resultados históricos terão data explícita e não serão apresentados como execução atual.

`docs/technical/entrega-academica.md` inclui a matriz dos vinte fluxos e suas evidências, sem dados sensíveis. Explicitar pendências externas: vídeo obrigatório do usuário e commit/push ainda dependentes de autorização. O relatório `validacao.md` da change registra comandos, ambiente, resultados e limitações; só haverá declaração de conclusão técnica após a verificação.

## Risks / Trade-offs

- Refatoração de respostas pode alterar payload/headers → testes de caracterização e contrato antes da migração dos wrappers.
- Lote pode alterar ordem, disponibilidade ou isolamento → comparar resultados em estados mistos, propriedade e snapshots, mantendo locks das escritas.
- Renderização compartilhada pode quebrar seletores/ordem de scripts → preservar slots/IDs e validar DOM, teclado, fluxo real e capturas nas duas larguras.
- MySQL/browser indisponível → registrar bloqueio real e não declarar validação completa nem substituir a integração.
- CI e navegador acrescentam tempo/dependências → um único browser inicialmente, timeout explícito e dependências exclusivamente de desenvolvimento.
- Duplicidade com change vazia preexistente → não editar/remover a change alheia; registrar que a implementação do JOIN será realizada aqui.

## Migration Plan

1. Após aprovação desta proposta, executar preflight das alterações locais e caracterização focada.
2. Implementar consultas, adaptação HTTP e navegação em incrementos pequenos, com regressão correspondente.
3. Acrescentar navegador/CI e documentação baseada nas Models e nos fluxos finais.
4. Executar suítes completas com MySQL descartável, navegador e gates; registrar evidências sem credenciais.
5. Verificar artefatos versus código, sincronizar a delta de navegação e arquivar somente após tasks completas e ausência de achado crítico.

Não há migration de banco, backfill ou DDL operacional. Reversão consiste em reverter somente os arquivos desta change, preservando mudanças legítimas preexistentes. Commit/push, gravação e envio de vídeo são etapas externas à conclusão técnica local.
