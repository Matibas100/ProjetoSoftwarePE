# Design

## Context

Ver [motivação e escopo](proposal.md). A navegação ainda marca Tutor indisponível. O inventário e o protótipo Desktop V1, página 26, já definem `ALU-TUT-001`, mas incluem conversa e ações contextuais futuras. Este recorte adapta essa composição a uma dúvida independente, sem inventar funcionalidades secundárias.

O backend possui seis módulos, composição por aplicação, 21 Models e autenticação por cookie com Origin/CSRF. `proteger_api` hoje considera rotas fora de `/api/aluno/` administrativas, salvo exceções; portanto, adicionar apenas o Blueprint de `/api/tutoria` bloquearia o Aluno. A privacidade usa documentos imutáveis, versões/hashes e evidências; uso 1.0 afirma que não há envio à LLM. As leituras de privacidade existentes já possuem procedures e não precisam de novo SQL.

## Goals / Non-Goals

**Goals:** acrescentar um sétimo módulo coeso; encapsular toda comunicação com Gemini em um Service; usar contratos pequenos e composição existente; limitar consumo e espera; tornar falhas verificáveis; atualizar transparência sem reescrever evidências.

**Non-Goals:** persistência de conversa, generalização de um framework de IA, novas tabelas/procedures, agente com acesso a ferramentas, personalização por respostas/desempenho ou preparação para usuários reais. O limite em memória é adequado à demonstração em um processo, não um controle distribuído de cobrança.

## Decisions

### 1. Módulo próprio, sem Model ou Repository artificiais

Adicionar `backend/app/modules/tutor_ia/` com `routes.py`, `controllers/tutoria_controller.py`, `services/gerar_tutoria_service.py`, `services/gemini_service.py` e helpers locais estritamente necessários. A Controller é classe e só interpreta HTTP, extrai a identidade da sessão e adapta sucesso/erro. O Service do caso de uso valida, verifica permissão, reserva limite e solicita a geração.

`app/contracts/tutoria.py` declara um Protocol de geração de texto com uma única operação e DTOs de entrada/saída sem ORM. A composição injeta Gemini e a validação pública de Contas. O Service não localiza dependências via Flask nem importa persistência de outro módulo. GeminiService é responsável por configuração, headers, HTTP e extração do texto; não recebe identidade ou resultados do aluno.

Fluxo externo: `Tela → Route → Controller → GerarTutoriaService → GeminiService → Gemini`. Autenticação e evidência de uso continuam `Contas → Model/Repository → MySQL`. A consulta externa não necessita de Repository ou entidade persistente. Não contabilizar isso como CRUD adicional para os critérios de banco do professor.

Alternativas rejeitadas: colocar o cliente no Controller; chamar API no navegador; Repository para HTTP externo; herdar um CRUD de chat que não existe; SDK/containers/agentes adicionais. Registrar adendo ao ADR-010 e atualizar as conventions/mapa modular para sete proprietários, sem alterar sua regra de fronteiras.

### 2. Contrato HTTP pequeno e alinhado à aula

Usar uma única rota `POST /api/tutoria`, sem alias. Blueprint do módulo é agregado sob `/api` uma vez. Requisição:

```json
{
  "disciplina": "Física",
  "nivel": "ensino_medio",
  "assunto": "Eletricidade",
  "duvida": "Qual é a diferença entre corrente elétrica e tensão?"
}
```

Resposta 200: `{"disciplina":"Física","assunto":"Eletricidade","resposta":"..."}`. O texto utiliza, nesta ordem e em linhas próprias, os títulos `1. Explicação simples`, `2. Exemplo`, `3. Verifique sua compreensão` e `4. Exercício curto`, cada qual com conteúdo não vazio. O último trecho propõe exercício sem gabarito. Normalizar quebras de linha; validar presença única/ordem dos quatro títulos e conteúdo; limitar resposta a 12000 caracteres. Formato inválido recebe 502, sem nova tentativa automática. Não é necessária saída JSON estruturada do modelo nem parser Markdown.

Validar no caso de uso os quatro campos exatos, tipos string, trim, comprimentos 1–100/1–150/10–2000 para disciplina/assunto/dúvida e `nivel == "ensino_medio"`. Rejeitar caracteres de controle exceto tabulação e quebra de linha na dúvida. O nível fica fixo e visível na tela, pois esta versão atende revisão de ensino médio para o ENEM, sem níveis de dificuldade adicionais.

Os nomes de Matéria/Assunto são contexto pedagógico textual, não identificadores autorizadores. A tela usa os GETs existentes do catálogo ativo e envia os nomes selecionados. O endpoint valida os limites textuais, sem fazer consultas novas para comprovar pertencimento ao catálogo. Nenhum texto recebido autoriza acesso a recurso ou gera escrita. Isso preserva os quatro campos da aula e evita novos contratos entre Tutor e Conteúdo.

Corpo máximo de 16384 bytes aplicado apenas à rota; retornar JSON 413 pelo tratamento HTTP local. JSON ausente, inválido ou raiz não objeto retorna 400. Não mudar `MAX_CONTENT_LENGTH` de toda a API.

| Status/código | Situação |
| --- | --- |
| 400 `dados_invalidos` | Corpo ou contexto fora do contrato |
| 401/403 existentes | Sessão, perfil, origem ou CSRF |
| 409 `termos_uso_pendentes` | Uso vigente ainda não aceito |
| 413 `corpo_muito_grande` | Mais de 16 KiB |
| 429 `limite_tutoria` | Janela, chamada já em andamento ou capacidade esgotada; `Retry-After` |
| 503 `tutor_indisponivel` | Desabilitado/chave ou modelo ausentes |
| 502 `tutor_timeout` | Timeout do transporte |
| 502 `tutor_provedor_indisponivel` | Rede, rejeição HTTP, inclusive quota do provedor |
| 502 `tutor_resposta_invalida` | JSON/esquema/texto inválido, bloqueio, incompleto ou excessivo |
| 500 `erro_interno` | Falha inesperada sanitizada |

Erros mantêm envelope `{erro, codigo}` existente e nunca incluem payload bruto, exceção HTTP ou headers. Quota do provedor não se confunde com o 429 do limite local.

### 3. Reconhecimento exato da autorização e leitura curta

Em Contas, tratar somente o caminho exato `/api/tutoria` como operação exclusiva de Aluno, com mutação protegida por Origin/CSRF. Não usar `startswith('/api/tutoria')`. Aplicar também `no-store` explícito ao endpoint. Autorizar antes de interpretar o JSON; nesse caminho, a classificação da permissão não precisa ler o corpo. Respostas 401/403 precedem 400/413 para quem não tem acesso. OPTIONS e caminhos inexistentes preservam o comportamento atual.

Criar em Contas `ValidarPermissaoTutoriaService`, exportado em sua `api.py` e injetado como colaborador de uma operação. Ele consulta as decisões existentes e exige `aceite_vigente(..., 'uso')`. Não exige consentimento do plano e não fornece dados de conta ao Tutor. A leitura é encerrada por `TransactionManager.executar` antes de devolver a permissão; nenhuma chamada externa fica dentro dessa fronteira.

Capturar o ID primitivo da sessão antes da verificação, não acessar atributos ORM após o fechamento da leitura e não transportar instâncias de sessão/usuário para Gemini. Confirmar por integração que não há conexão/transação retida durante a espera externa. A renovação da sessão continua no caso de autenticação existente. Não manter lock para a rede nem criar decisões de privacidade por conta dessa leitura.

Ordem do caso de uso após a autorização HTTP: validar entrada → conferir uso vigente e encerrar leitura → verificar configuração → reservar limite → preparar prompt → uma chamada Gemini → validar formato → devolver resposta; liberar a reserva em `finally`.

### 4. REST do Gemini e correção do exemplo didático

Usar `requests` com versão fixada compatível e sem chamadas na importação/factory. Endpoint fixo `https://generativelanguage.googleapis.com/v1beta/interactions`, HTTPS verificado, chave em `x-goog-api-key`, sem redirecionamento HTTP. Não aceitar endpoint/modelo/chave pelo corpo enviado pelo navegador.

Configuração por aplicação: `TUTOR_IA_ENABLED=false` por padrão, `GEMINI_API_KEY` vazia por padrão e `GEMINI_MODEL=gemini-3.6-flash`, conforme exemplo e modelo listado na documentação consultada. Usar configuração explícita na factory/composição, sem ler `.env` nos Services. Valor vazio de chave/modelo ou flag falsa desabilita o cliente sem impedir inicialização do restante da aplicação. `.env.example` recebe apenas placeholders e aviso de possível consumo/custo; não ler nem preencher `.env` como parte automática do apply.

Payload externo: `model`, `system_instruction`, `input`, `store:false` e `generation_config.max_output_tokens:4096`. Instrução pedagógica estável no caso de uso; os quatro campos são serializados como dados, sem interpolar texto do aluno na instrução de sistema. Pedir português, as quatro seções, revisão compatível com ENEM e nenhum gabarito/nota. Não enviar ferramentas, histórico, `previous_interaction_id`, metadata de usuário, anexos, modo background ou streaming de produto.

O material da aula mostra acesso REST a `output_text`; a documentação atual descreve esse atributo como conveniência do SDK. No REST, validar `status == 'completed'` e percorrer os blocos textuais da última etapa `type == 'model_output'`, em `steps[].content[]`, unindo apenas blocos `type == 'text'`. Ignorar pensamentos e rejeitar respostas sem texto final, estados diferentes de completed e esquema inesperado. Não fazer fallback silencioso para respostas inventadas, API antiga ou outro modelo.

Aplicar timeout de conexão de 5 s e leitura de 30 s; `requests` distingue esses tempos de um prazo global de geração. Limitar leitura do corpo externo a 1 MiB, fechando a resposta inclusive após erro; leitura em blocos é apenas controle de transporte, sem transmissão parcial ao navegador. Nenhum retry de rede/modelo automático. A interface encerra sua espera após 45 s; abortar o navegador não garante interrupção/cancelamento da chamada já recebida pelo provedor.

Fontes técnicas oficiais consultadas em 09/11/2026:

- [Geração de texto e diferença entre SDK e REST](https://ai.google.dev/gemini-api/docs/text-generation?authuser=09).
- [Referência de Interactions e etapas de saída](https://ai.google.dev/api/interactions-api?authuser=5&hl=en).
- [Armazenamento de interações e opção store=false](https://ai.google.dev/gemini-api/docs/interactions-overview?authuser=108).
- [Modelo Gemini 3.6 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash?hl=en).
- [Timeouts do Requests](https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts).

Disponibilidade na conta só pode ser comprovada por chamada real; se o contrato/documentação mudar materialmente, atualizar estes artefatos antes de implementar outra abordagem.

### 5. Limite em memória, sem infraestrutura adicional

Um limitador por aplicação, criado na composição, usa lock e relógio monotônico: janela fixa de 60 s com até quatro tentativas externas por ID, uma em andamento por ID e duas em andamento globalmente. Reservar atomicamente apenas após entrada/permissão/configuração válidas; falhas externas contam. Liberar vagas em `finally` sem apagar tentativas da janela. Rejeitar excesso imediatamente com 429 e `Retry-After` em segundos inteiros, no mínimo 1; para janela cheia usar o tempo restante arredondado para cima.

Guardar somente IDs e contadores/instantes, jamais dúvidas/respostas. Expirar registros ociosos após a janela; capacidade máxima de 1024 contas por processo. Se essa capacidade estiver ocupada por registros ainda válidos, rejeitar nova reserva com 429, sem remover um limite ativo para admiti-la. Sem temporizador, Redis, tabela ou migração. Reinício limpa contadores e múltiplos workers não compartilham o limite; isso consta no README e não é apresentado como proteção global de orçamento para produção.

### 6. Termo 2.0 e escolhas independentes

Publicar `frontend/legal/termo-de-uso-v2.html`; acrescentar versão/hash e definir somente uso vigente como 2.0 em `contas/domain/privacidade.py`. Manter bytes, hashes e URLs de uso 1.0 e consentimento do plano 1.0. Usar os Services/endpoints existentes para aceitar uso; nenhum registro é fabricado por upgrade e nenhum novo tipo de consentimento é adicionado.

A nova minuta descreve que o usuário escolhe enviar cada dúvida e seu contexto ao Google Gemini; não se envia automaticamente identidade, desempenho ou respostas do sistema. A tela exibe o aviso antes do botão `Enviar dúvida ao Gemini`; abrir a tela ou aceitar uso não gera solicitação. Não tratar o aceite de uso como autorização genérica nem a decisão do plano como autorização para IA.

O plano permanece determinístico e seu documento 1.0 continua correto. Conta com uso antigo precisa aceitar uso 2.0 para Tutor e, pela regra já existente, para liberar novamente o plano. Isso não apaga nem restaura planos, não muda a decisão do plano e não bloqueia questões, simulados ou desempenho. Atualizar testes que codificam versão vigente, preservando cenários de evidência histórica e recusa/revogação.

`store=false` desativa armazenamento da interação segundo o contrato do recurso, não fundamenta promessa de retenção operacional zero, ausência de tratamento externo ou conformidade integral. Permanecem demonstração sintética, contato fictício e pendências antes de uso real, inclusive menores e avaliação das condições do provedor. A revisão jurídica e uma eventual autorização específica persistida para outro uso não são substituídas por este recorte acadêmico.

### 7. Tela e estados sem reconstruir o frontend

Criar HTML/CSS/JS próprios aproveitando shell do Aluno, estilos/tokens, AuthUI e `apiRequest`. Preservar cores, hierarquia, contexto lateral, aviso e quatro seções do protótipo oficial. Disponibilizar Tutor em ESTUDAR e remover somente as menções de indisponibilidade desse recurso; não habilitar Resumos, Perfil, Redação ou outras funções futuras.

Matéria/Assunto reutilizam catálogo ativo já autenticado; mudança de Matéria limpa o Assunto e ignora resultado de filtro atrasado. Catálogo vazio/falho tem estado próprio e impede envio. O nível de ensino médio é fixo. Não exibir questão de origem, data, usuário ou conversa fictícios. Entrada pela sidebar é o único ponto desta versão. Registrar em documento técnico a adaptação do chat/contexto futuro para envio pontual, sem modificar os quatro binários oficiais.

Preservar a pergunta durante processamento; desabilitar envio duplicado; enviar uma vez com AbortController/sinal já aceito pelo cliente compartilhado. Prazo local de 45 s, sem alterar globalmente `apiRequest`. Identificar timeout local no controlador da tela, pois o cliente atual traduz interrupção de fetch como falha de conexão. Após erro, manter rascunho em memória apenas para a mesma conta; não usar localStorage, sessionStorage, IndexedDB, URL ou Service Worker para dados da dúvida.

Renderizar quatro seções com nós DOM e `textContent`, nunca `innerHTML`, parser Markdown ou links gerados. Manter a última resposta bem-sucedida associada à pergunta original até novo sucesso, deixando claro quando uma nova tentativa falhou. Troca de contexto não pode rotular resposta antiga com novos filtros. Ações `explicar de outro jeito`, resumo e adicionar ao plano ficam ausentes ou explicitamente indisponíveis; `Praticar questões` pode apontar para página existente, sem alegar ter criado exercício corrigível.

Reusar os eventos de identidade e recuperação existentes; limpar conteúdo ao perder/trocar sessão, sair ou abandonar página. Invalidar identificador local da requisição para ignorar respostas atrasadas. Recuperação de sessão nunca reenvia automaticamente a dúvida. Revalidar a mesma identidade ao retornar à aba antes de aceitar resultado pendente. Testar foco, aria-live, teclado, 1440/390 px e texto longo sem overflow.

### 8. Verificação e demonstração real separadas

- Unitários Python: transporte controlado exclusivamente em unidade, schema REST realista, múltiplos blocos, pensamentos ignorados, ausência de output_text, respostas inválidas/incompletas, limites, erro HTTP, timeout, no-retry e sanitização de logs. Relógio controlável apenas em unidade para janela/concorrência.
- Arquitetura/factory: sete módulos, Tutor sem Models, 21 mappers preservados, limites/clientes independentes entre aplicações, sem chamadas na factory, imports públicos e ausência de SQL/HTTP no Controller.
- Integração MySQL real: uso 2.0, evidências antigas, autorização/perfil/CSRF, persistência de decisões e regressão do plano. Nos testes HTTP de integração, usar entradas que não chegam à rede ou Tutor desabilitado; nenhum provedor falso nesse nível. Verificar o fechamento da transação na preparação de permissão por caso dedicado real, sem substituir banco.
- DOM: seletores reais, estados, formato, XSS como texto, dupla confirmação, abort/45 s, rascunho, troca de conta, respostas atrasadas e ausência de armazenamento. Simulação de fetch só nos unitários DOM.
- E2E/MySQL descartável: navegação e consulta de termos, aviso, aceite 2.0 e indisponibilidade real com Tutor desabilitado. Não interceptar rede do Gemini para fabricar sucesso e não encaminhar chave real ao runner padrão. Preservar E2E dos vinte casos.
- Prova real opt-in: com configuração local fornecida pelo responsável, usar a tela autenticada e dúvida sintética, confirmar resposta com quatro partes, sem gabarito e sem dado pessoal. Registrar somente data, modelo, status e checklist pedagógico/arquitetural em relatório, sem corpo da dúvida/resposta, credenciais, HAR ou trace autenticado. Se não houver chave/acesso/quota, manter essa task pendente; não declarar integração real concluída pelo resultado dos unitários.

README deve trazer contrato, execução, versões de termos, env placeholders, códigos, limites, diferença entre teste controlado e real e passos de demonstração da rota/400. Relacionar o caso à atividade de LLM sem alterar indevidamente os vinte casos com persistência já entregues.

## Risks / Trade-offs

- IA pode errar ou fornecer gabarito apesar da instrução → aviso, quatro partes verificáveis e revisão pedagógica da chamada real; não prometer validação semântica automática.
- Prompt pode conter dados pessoais → orientar antes do envio, contexto mínimo e demonstração sintética; não prometer anonimização automática de texto livre.
- Provider pode reter dados fora do recurso Interaction → `store=false` e transparência sobre limites, sem alegar garantia jurídica ou operacional ampla.
- Chamada pode consumir quota/custo mesmo após abort local → sem retry automático, limites pequenos e confirmação explícita; produção distribuída fica para outra change.
- Nova versão de uso bloqueia plano até novo aceite pela regra atual → aviso e fluxo de privacidade existente, com preservação dos dados e decisão separada do plano.
- Formato de quatro títulos pode ser recusado por resposta divergente → 502 específico em vez de falsa resposta completa; validar prompt e modelo na prova real.

## Migration Plan

1. Implementar com `TUTOR_IA_ENABLED=false`, sem alterações em schema, migrations 000–016, snapshot SQL, procedures ou views.
2. Publicar uso 2.0 e metadados; testar versões históricas e novo aceite com MySQL real. Documentar efeito no plano antes de habilitar Tutor.
3. Instalar dependência fixada, validar testes/contratos e atualizar documentação/ADRs/conventions/configuração contextual do OpenSpec de seis para sete módulos.
4. O responsável configura a chave somente no ambiente local e habilita o recurso para a prova sintética. A ausência dessa configuração deixa a validação real pendente.
5. Rollback operacional: desabilitar Tutor e manter endpoint com 503. Depois de publicado, não remover uso 2.0 nem voltar o vigente automaticamente; preservar evidências e oferecer versão corretiva caso necessária. Não há downgrade de banco.

Sincronizar e arquivar somente depois de implementação verificada. Commit/push continuam dependentes de autorização própria.
