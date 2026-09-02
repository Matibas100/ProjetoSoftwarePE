## Context

O backend possui 29 testes de integração em `unittest`, executados contra o MySQL configurado no `.env`. Eles atravessam Route, Controller, Service e Model/Repository para os dez casos de uso do MVP, porém não existe coleta de cobertura nem testes dedicados para configuração, health check, falhas inesperadas e vários ramos de validação. O frontend usa quatro scripts clássicos, sem gerenciador de pacotes ou testes. Consulte `proposal.md` para a motivação e o escopo.

## Goals / Non-Goals

**Goals:**

- Tornar mensurável a cobertura de todo arquivo Python e JavaScript de produção.
- Preservar os 29 testes existentes como regressão e manter o MySQL real nas integrações.
- Separar testes rápidos dos testes que dependem de infraestrutura.
- Exercitar contratos HTTP, regras de validação, persistência, Stored Procedure e interações DOM sem mudar o comportamento do MVP.
- Falhar a validação completa quando os limites de cobertura não forem atingidos ou quando algum módulo executável ficar sem cobertura.

**Non-Goals:**

- Buscar 100% numérico a qualquer custo ou testar detalhes sem valor comportamental.
- Trocar o framework Python atual, substituir o MySQL ou redesenhar camadas da aplicação.
- Automatizar migrations contra o banco de desenvolvimento.
- Adicionar CI, navegador ponta a ponta ou comparação visual por pixel.

## Decisions

### 1. Manter `unittest` no backend e adicionar `coverage.py`

Os novos testes Python usarão `unittest`, preservando a suíte e o comando já conhecidos. `coverage.py` coletará linhas e branches de `backend/app/` e `backend/run.py`, incluindo arquivos que os testes não importarem.

Uma dependência de desenvolvimento separada evitará incluir ferramentas de teste no ambiente de produção. A validação falhará abaixo de 90% de linhas ou 85% de branches e também quando um módulo executável tiver cobertura nula.

No backend, um validador versionado lerá o relatório JSON do `coverage.py` para calcular separadamente os percentuais agregados de linhas e branches. A coleta enumerará todos os arquivos `.py` de `backend/app/` e `backend/run.py`, inclusive os não importados. Qualquer arquivo com instruções executáveis e zero linhas cobertas reprovará a validação; arquivos sem instruções executáveis não serão tratados como zerados.

Alternativas consideradas:

- Migrar para pytest: descartado porque não é necessário para atingir a cobertura e contraria a escolha atual do projeto.
- Exigir 100%: descartado como meta inicial porque incentiva testes frágeis; a cobertura total das superfícies e comportamentos críticos será controlada por matriz explícita.

### 2. Separar testes Python por finalidade

- **Unitários:** configuração, serialização, validações puras e tradução de falhas. Podem usar `unittest.mock` somente para isolar colaboradores; não substituem nenhuma integração existente.
- **Integração:** rotas, persistência, constraints e `sp_questoes_por_assunto` continuam contra MySQL 8 real, com dados de nome único e `addCleanup`.

Os testes unitários ficarão em `backend/tests/unit/`. Os testes de integração manterão o sufixo `*_integration.py`, inclusive os 29 testes originais, permitindo descoberta independente sem renomeá-los nem removê-los.

Um launcher Python versionado executará os testes unitários em processo isolado, bloqueará o carregamento do `.env` e definirá uma `DATABASE_URL` fictícia antes do primeiro import de `app`. A URL servirá apenas para inicializar a configuração: a suíte unitária não abrirá conexão com MySQL. O Makefile e o comando Python direto usarão o mesmo launcher.

O preflight das integrações verificará conexão, tabelas e Stored Procedure e falhará com mensagem clara se a infraestrutura estiver indisponível. Nenhum teste exibirá valores do `.env`.

### 3. Usar Vitest, jsdom e cobertura V8 no frontend

Vitest será configurado como dependência de desenvolvimento com jsdom para testar o DOM sem servidor. A cobertura incluirá todos os arquivos em `frontend/js/`, com os mesmos limites de 90% de linhas e 85% de branches e sem arquivo executável zerado.

Um validador Node versionado lerá o `coverage-summary.json` produzido pela cobertura V8. Ele recalculará separadamente os percentuais agregados de linhas e branches e reprovará qualquer arquivo JavaScript com linhas executáveis e zero linhas cobertas. A configuração do Vitest incluirá explicitamente os quatro arquivos de produção no relatório, mesmo quando algum deles não for carregado pelos testes.

Os quatro scripts permanecerão clássicos. Um helper de teste carregará `frontend/index.html` e executará os scripts no mesmo contexto global do jsdom, na ordem declarada pelo HTML. Cada teste reconstruirá o DOM e controlará `fetch`, `confirm`, rolagem e eventos necessários. A change não converterá os scripts para ES Modules.

Os testes montarão o HTML necessário, controlarão `fetch`, confirmações e eventos, e verificarão:

- sucesso, `204`, erro HTTP e resposta inválida do cliente de API;
- status da API;
- carregamento, vazio, erro, cadastro, edição, cancelamento e exclusão de matérias e assuntos;
- carregamento de seletores, cadastro, busca vazia, busca com resultado e falha de questões;
- escape de conteúdo antes da renderização.

O tratamento de JSON inválido será caracterizado sem alterar o contrato atual de `api.js`: resposta `204` retorna `null`; resposta HTTP bem-sucedida com corpo não parseável retorna objeto vazio; resposta HTTP de erro com corpo não parseável lança `ApiError` com a mensagem padrão e o status recebido. Uma mudança futura dessa semântica exigirá change funcional própria.

Será permitida somente refatoração mínima para expor funções ou inicialização aos testes, preservando IDs, scripts, eventos, chamadas HTTP e resultado visual. A alternativa de Playwright foi descartada nesta change por exigir navegador e infraestrutura completa; poderá complementar a suíte futuramente.

### 4. Validar o contrato estrutural do HTML

Um teste carregará `frontend/index.html` para confirmar a presença dos elementos e a ordem dos scripts exigidos pelo JavaScript. CSS será excluído da métrica de cobertura; regressão visual não é adequadamente provada por cobertura de código.

### 5. Definir uma matriz de cobertura por superfície

Além dos percentuais, a conclusão exige cobertura explícita destas superfícies:

| Superfície | Validação principal |
| --- | --- |
| Application factory, configuração e health | Testes unitários e HTTP |
| 11 rotas e 10 casos de uso | Integração MySQL de sucesso e erros relevantes |
| Models e `CrudMixin` | Persistência, atualização, exclusão e rollback |
| `QuestaoRepository` | Resultado e fechamento da Stored Procedure |
| Cliente HTTP do frontend | Testes unitários com `fetch` controlado |
| Formulários e listas | Testes DOM de estado e interação |
| HTML | Teste de contrato de elementos e scripts |

Cobertura percentual é um indicador complementar: não substitui as asserções da matriz.

No `QuestaoRepository`, o fechamento do objeto de resultado será provado por teste unitário com colaborador controlado, inclusive quando ocorrer falha durante o mapeamento. A ordenação e o conjunto vazio serão provados por integração com a Stored Procedure no MySQL real.

### 6. Preservar banco, contratos e segurança

Não haverá alteração de schema ou migration. As integrações continuarão usando o banco indicado pelo ambiente, mas o runner exigirá `RUN_MYSQL_INTEGRATION=1` antes de abrir conexão ou escrever dados. A autorização será informada apenas no processo de execução, não persistida no `.env`, e não conterá credenciais.

Cada teste criará dados temporários identificáveis e registrará limpeza somente pelas chaves primárias exatas que ele criou. Não haverá exclusão automática por prefixo nem limpeza ampla; eventual resíduo de interrupção abrupta será reportado para remoção controlada. O teste da Stored Procedure observará seu contrato por meio do Repository, preservando o fluxo arquitetural. Relatórios de cobertura e caches serão ignorados pelo Git.

### 7. Orquestrar os comandos pelo Makefile

Um `Makefile` na raiz será a interface reproduzível da suíte, preservando também os comandos Python e npm diretamente executáveis:

- `make test-unit`: testes unitários Python e testes Vitest/jsdom sem MySQL;
- `make test-integration`: testes `*_integration.py` contra MySQL real, após o preflight;
- `make test-backend`: suíte Python completa com relatório e gates de cobertura;
- `make test-frontend`: suíte frontend completa com cobertura V8;
- `make test-coverage`: executa e valida a cobertura das duas stacks;
- `make test`: alias da validação completa.

Os alvos que dependem de MySQL falharão claramente quando a infraestrutura estiver indisponível e nunca exibirão credenciais.

GNU Make será um pré-requisito de desenvolvimento para usar esses atalhos. Para funcionar no Windows, as receitas conterão somente dependências entre alvos e chamadas a executáveis ou scripts versionados, sem atribuição de variáveis ou operadores específicos de PowerShell, `cmd` ou Bash. A documentação fornecerá o comando Python ou npm equivalente para cada alvo.

O `package.json` declarará `engines.node` como `>=22.9.0` e `packageManager` como `npm@11.6.2`, mantendo compatibilidade com o ambiente local validado em Node `25.2.1`. As dependências de teste serão fixadas pelo lockfile. Como GNU Make não está instalado no ambiente atual, a documentação o tratará como pré-requisito manual e exigirá confirmar sua disponibilidade com `make --version` antes de usar os atalhos.

## Risks / Trade-offs

- **Testes de integração podem falhar por indisponibilidade do MySQL** → executar preflight e relatar infraestrutura indisponível sem declarar regressão do código.
- **Dados temporários podem permanecer após interrupção abrupta** → usar identificadores únicos e `addCleanup` por chave primária exata; reportar resíduos sem executar limpeza ampla automática.
- **Integração pode apontar para um banco com dados relevantes** → exigir opt-in explícito por processo antes da conexão e limitar toda remoção aos registros criados pelo próprio teste.
- **GNU Make pode não estar disponível no Windows** → verificar o pré-requisito com `make --version`, orientar sua instalação e documentar comandos Python/npm equivalentes.
- **Cobertura pode incentivar asserções superficiais** → exigir a matriz comportamental além dos percentuais.
- **jsdom difere de um navegador real** → limitar afirmações a DOM e lógica; manter E2E e regressão visual fora do escopo.
- **Pequenas adaptações para testabilidade podem alterar inicialização do frontend** → preservar a ordem dos scripts e adicionar testes de contrato antes da refatoração.
- **Mocks em testes unitários podem esconder integração quebrada** → nunca remover nem substituir os testes MySQL; usar mocks apenas nos testes rápidos.

## Migration Plan

1. Adicionar ferramentas, configurações de desenvolvimento e os alvos do Makefile sem modificar dependências de produção.
2. Criar testes de caracterização do comportamento atual antes de qualquer ajuste mínimo para testabilidade.
3. Completar testes backend e frontend por superfície, mantendo os 29 testes aprovados.
4. Ativar os limites de cobertura somente após a matriz estar completa.
5. Atualizar documentação e executar validações rápidas e completas.

Rollback: remover apenas configurações, dependências de desenvolvimento e novos testes. Nenhuma reversão de banco, contrato HTTP ou dado é necessária.
