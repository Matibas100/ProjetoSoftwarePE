# Proposta — 5. Dashboards e desempenho real

## Why

Com respostas e simulados persistidos, a plataforma pode mostrar dados verificáveis e identificar dificuldade por Matéria e Assunto. Esta entrega transforma o início do Aluno em dashboard útil e acrescenta uma visão administrativa básica da operação.

## What Changes

- Calcular total de respostas, acertos e percentual por Matéria/Assunto a partir de práticas corrigidas e simulados finalizados.
- Exibir base, período e quantidade da amostra; ausência de dados não representa desempenho zero.
- Entregar dashboard do Aluno e tela de desempenho; dashboard administrativo com contagens reais de catálogo, Questões, simulados e tentativas finalizadas, sem históricos individuais de Alunos.
- Mostrar até cinco atividades próprias no mesmo período do diagnóstico, uma por tentativa concluída, com ordenação e destinos definidos; simulado em branco é atividade, mas não acrescenta resposta ao desempenho.
- Disponibilizar contrato de diagnóstico para o plano do item 6, participando da leitura consistente e do relógio da transação externa sem encerrá-la.
- Entregar payload completo por endpoint; blocos da mesma requisição compartilham loading/erro e recarga, preservando navegação e descartando respostas atrasadas de outro período ou identidade.
- Fora de escopo: TRI, projeção de nota, comparação estatística, redação, IA, ranking, materialização de métricas e recomendações de plano antes do item 6.

## Capabilities

### New Capabilities

- `desempenho-real`: métricas derivadas e dashboards com período, origem e amostra explícitos.

### Modified Capabilities

Nenhuma. O destino existente `/aluno/inicio.html` é preservado; novas leituras seguem a autorização definida no item 3.

## Impact

- Superfícies: Services de dashboard/diagnóstico, Repositories de agregação, Controllers/rotas e frontend de ALU-DASH-001, ALU-DES-001 e ADM-DASH-001.
- Contratos propostos: `/api/aluno/dashboard`, `/api/aluno/desempenho` e `/api/admin/dashboard`. Não são contratos herdados do Desktop V1: são definidos nesta proposta para o recorte mínimo.
- Dependências: item 3 (`pratica-questoes-com-historico`) e item 4 (`simulado-fixo-com-resultado`) concluídos, verificados, sincronizados e arquivados; localizar artefatos pelo nome inclusive no arquivo. Ordem operacional 2 -> 3 -> 4 -> 5 -> 6.
- Banco: consultas sobre registros de origem, sem nova tabela de métricas e sem migration prevista. Projeções dos Repositories de origem preservam a semântica dos fatos oferecidos pelos Services predecessores; agregação no MySQL e contexto de leitura consistente ficam explicitados no design.
- Decisão proposta para o MVP: cinco respostas por grupo distinguem amostra pequena; é um limiar operacional, não garantia estatística e não resolução geral da OD-17. Período padrão: últimos 30 dias em UTC.
- ADRs 002, 003 e 005 para autorização e preservação histórica; ADR-006 para propriedade e participação em transações. ADR-001 continua válido caso uma necessidade de schema seja descoberta, exigindo revisão desta change antes do apply.
- Compatibilidade: manter destinos de login, práticas e resultados imutáveis, dez casos de uso, testes e fontes visuais oficiais; sem framework novo.
