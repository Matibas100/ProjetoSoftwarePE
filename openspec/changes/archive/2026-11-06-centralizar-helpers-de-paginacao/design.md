# Design: utilitários neutros de paginação

## Context

Ver [proposal.md](proposal.md). `_inteiro_filtro` e `_envelope` são definidos em `listar_catalogo_admin_service.py`, mas usados por sete módulos de outros casos de uso. Nenhum desses dois helpers contém regra específica de catálogo. Os validadores de recursos, por outro lado, possuem defaults, campos permitidos e níveis de rigor diferentes que devem permanecer.

Esta refatoração resolve os dois helpers privados identificados na revisão. Reuso de validações de domínio, como confirmação editorial ou início de tentativa, não autoriza movê-las para um utilitário genérico nesta change.

## Goals / Non-Goals

**Goals:** um local neutro e público para conversão genérica de filtro inteiro e envelope paginado; importação direta pelos consumidores; comportamento, consultas e classes de Service idênticos.

**Non-Goals:** padronizar todas as entradas HTTP, criar base de Service, abstrair repositorios, endurecer conversões, alterar mensagens/limites ou mover validações específicas. Nenhuma nova classe é necessária.

## Decisions

### 1. Um módulo com duas funções

Criar `backend/app/services/paginacao.py`, com somente:

- `inteiro_filtro(valor, campo, minimo=1, maximo=None)`: corpo atual de `_inteiro_filtro`, preservando defaults, retorno `None` para `None`/string vazia, conversão por `int`, intervalo e mesmas exceções/mensagens.
- `envelope_paginado(itens, pagina, por_pagina, total)`: corpo atual de `_envelope`, com as mesmas chaves, valores e `ceil(total / por_pagina)` quando total não é zero.

Dependências limitadas a `math.ceil` e `DadosInvalidosError`. Nenhum Flask, ORM, Model, Repository, SQL, consulta, commit, `current_app`, protocolo ou estado global. O módulo é um apoio de aplicação, não um caso de uso, por isso não precisa ser uma classe de Service.

Mover os corpos, não reimplementá-los com outro algoritmo. Não trocar `int` por parsing estrito, rejeitar `bool`/floats antes aceitos diretamente, impor máximo global novo, ajustar páginas vazias, tratar zero por página de outro modo ou alterar acentuação de mensagens. Essas seriam correções funcionais distintas. Os validadores estritos que já rejeitam certas entradas continuam fazendo isso antes de chamar o helper.

### 2. Migrar todos os consumidores dos dois nomes privados

| Arquivo em `backend/app/services/` | Uso final |
| --- | --- |
| `listar_catalogo_admin_service.py` | Ambos os helpers públicos; `_parametros`, status/busca/filtros e classes continuam no catálogo |
| `gestao_questao_service.py` | Ambos os helpers públicos |
| `gestao_simulado_service.py` | Envelope público |
| `listar_historico_simulados_service.py` | Envelope público |
| `listar_praticas_service.py` | Envelope público |
| `listar_questoes_aluno_service.py` | Envelope público |
| `listar_simulados_aluno_service.py` | Envelope público |
| `pratica_validacao.py` | Inteiro público, mantendo sua validação estrita/padrões |

Atualizar imports e chamadas explicitamente. Remover as definições privadas antigas e o import `ceil` que deixar de ser usado no catálogo. Não criar alias antigo ou função wrapper sem consumidor real. Antes de remover, buscar consumidores adicionais/patches; os nomes são privados, mas a pesquisa deve confirmar que todo uso do repositório foi migrado. Se surgir consumidor de produção fora da lista, registrar e revisar o escopo em vez de deixar cópia divergente.

Preservar nomes/classes, assinaturas públicas de Services e os contratos de composição/SOLID. No restante de cada arquivo, alterar apenas import/chamada dos helpers, sem reformatar toda a lógica. `_parametros` continua específico do catálogo; `parametros`, `corpo` e `inicio` permanecem em `pratica_validacao.py`, e validações de Simulados/Plano/Questões permanecem em seus módulos. Reuso de helper público não move responsabilidade de domínio.

### 3. Escopo de onze arquivos

Nove de produção (módulo novo e oito linhas da tabela), novo `backend/tests/unit/test_paginacao.py` e somente `docs/conventions/arquitetura-da-aplicacao.md`. Registrar numa frase da convenção onde ficam os helpers e que cada caso de uso continua sendo coordenado por seu Service, sem virar uma classe genérica.

README, frontend, Controllers, Models, Repositories, composição, SQL, schema, migrations, runners, pacotes, CI, demais testes e documentos históricos permanecem intactos. Não mexer nos arquivos da change de JSON nem na finalização de Simulado formatada pela limpeza.

### 4. Validação de equivalência e limites

No preflight do apply, guardar corpos AST originais e inventário de consumidores em QA ignorado, sem dados sensíveis. Comparar os corpos extraídos com os originais, normalizando somente os dois nomes de função; demais diferenças de lógica não são aceitas. Nos consumidores, conferir que somente import/chamadas mudaram.

O novo unitário cobre contratos reutilizáveis, não a localização de cada import: ausência/vazio, número válido/string, limites mínimo/máximo e mensagens de erro; envelope vazio, total exato e parcial, página além da última com itens vazios e o mesmo total informado, preservação da lista/ordem de itens. Incluir casos de conversão já aceitos por `int` e pelo contexto anterior, sem usá-los para propor uma política nova.

Reexecutar unitários existentes do catálogo, Questões, Práticas, Simulados e composição. Os testes de validadores estritos existentes devem continuar rejeitando filtro repetido, Unicode numérico e valores não string onde já rejeitavam. Não mudar esses testes para adotar o rigor do helper genérico. O teste do helper não prova sozinho a segurança de entrada de cada endpoint.

Antes do fechamento, executar `python backend/tests/run_backend_coverage.py` com opt-ins de integração/migrations apenas no processo, gates 90%/85% intactos e MySQL real. Verificar regressões de filtros/paginações, HTTP, origens, propriedade e dados persistidos. Executar também os dois E2E pelo runner oficial; confirmar uso da interface, schema descartável e limpeza de processos. Não substituir MySQL por mocks/SQLite ou rodar operações contra banco operacional.

Como nenhum frontend muda, não repetir cobertura DOM só por este delta. As duas implementações anteriores precisam estar encerradas/verificadas; seu estado local integra o baseline desta change e não deve ser atribuído à extração. Configuração só pelos mecanismos autorizados e sem abrir/expor `.env`, persistir segredos ou exportar sessões.

### 5. Ordem e registro

Sequência operacional: legibilidade -> JSON inválido -> helpers. Não iniciar apply enquanto outro modifica/valida o mesmo working tree. Criar baseline fresco em `test-results/paginacao/`, ignorado, e preservar todo trabalho anterior, `tmp/`, visuais oficiais e changes existentes.

Registrar comandos/resultados/limitações reais em `validacao.md`; conferir busca final sem imports dos dois nomes antigos, links/whitespace, hashes de preservação, verificação da change e validação estrita. Não escrever relatório de aprovação durante este planejamento nem executar testes de integração agora.

## Risks / Trade-offs

- **Extração endurece regras sem querer:** copiar corpos e comparar AST; preservar parâmetros/retornos/mensagens e validadores específicos.
- **Criar um utilitário sem limite:** somente dois helpers de paginação, sem funções de UUID, confirmação, identidade ou início de tentativa.
- **Quebrar import/patch ou manter duplicação:** inventário antes/depois e regressão; migrar os sete consumidores externos, sem wrappers desnecessários.
- **Atribuir falha de outra change à extração:** implementação sequencial, baseline próprio e escopo de onze arquivos.
- **Arquivo novo sem cobertura:** testes de comportamento e gate oficial, sem alterar thresholds ou exclusões.

## Migration Plan

Nenhuma migration, alteração de dados, novo contrato ou deploy. Criar módulo/testes, atualizar consumidores, documentar a localização e validar. Para desfazer, restaurar somente os arquivos da extração a partir do baseline e remover seus arquivos novos, preservando trabalho legítimo anterior/posterior. Sync não aplicável (`skip_specs: true`); arquivar após verificação sem achados críticos. Commit/push/merge e AWS ficam fora do escopo.
