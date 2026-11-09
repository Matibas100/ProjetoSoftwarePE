# tutoria-revisao-ia Specification

## Purpose

Permitir que o Aluno envie uma dúvida de estudo para revisão do ENEM e receba apoio pedagógico do Gemini, com acesso protegido, envio consciente, limites e falhas explícitas, sem histórico persistente.

## Requirements

### Requirement: Consulta pontual de revisão
`POST /api/tutoria` SHALL receber somente `disciplina`, `nivel`, `assunto` e `duvida`. SHALL retornar 200 com `disciplina`, `assunto` e `resposta` textual, em português, contendo explicação simples, exemplo, pergunta de compreensão e exercício curto sem gabarito. A instrução pedagógica SHALL orientar revisão para o ENEM, sem atribuir nota ou executar ações no sistema.

#### Scenario: Revisar uma dúvida
- **GIVEN** Aluno autorizado e provedor disponível
- **WHEN** envia disciplina `Física`, nível `ensino_medio`, assunto `Eletricidade` e dúvida sobre corrente e tensão
- **THEN** recebe os dois contextos e uma resposta com as quatro partes identificáveis, sem solução do exercício proposto
- **AND** o fluxo não publica conteúdo, altera desempenho ou gera plano de estudos

#### Scenario: Enviar outra dúvida
- **GIVEN** uma resposta anterior na tela
- **WHEN** Aluno confirma novo envio
- **THEN** apenas o contexto e a dúvida deste envio seguem ao provedor, sem mensagens, identificadores de interação ou respostas anteriores

### Requirement: Validação anterior ao consumo externo
A API SHALL rejeitar com 400 JSON ausente, inválido ou não objeto, campos faltantes/extras, tipos incorretos e textos vazios. Após trim, disciplina SHALL ter 1–100 caracteres, assunto 1–150, dúvida 10–2000 e nível SHALL ser `ensino_medio`. Corpo acima de 16 KiB SHALL retornar 413. Nenhuma dessas falhas SHALL consumir o provedor.

#### Scenario: Corpos inválidos
- **WHEN** Aluno envia HTML, JSON malformado, `null`, lista, objeto incompleto, valor booleano, campo extra ou dúvida fora do limite
- **THEN** recebe 400 com erro compreensível e não ocorre chamada externa

#### Scenario: Limites e normalização
- **WHEN** Aluno envia textos com espaços externos e comprimentos válidos
- **THEN** o servidor usa os valores aparados e aceita os limites inclusivos, sem interpretar o texto como instrução administrativa

#### Scenario: Corpo excessivo
- **WHEN** Aluno autorizado envia corpo maior que 16384 bytes
- **THEN** recebe 413 estruturado, sem chamar o provedor ou alterar o limite global de outros endpoints

### Requirement: Autorização e proteção do endpoint de tutoria
O endpoint SHALL exigir sessão válida de Aluno, Origin permitido, CSRF e aceite vigente de uso antes de qualquer envio externo. Anônimo SHALL receber 401, Administrador ou origem/CSRF inválidos 403 e uso pendente 409 `termos_uso_pendentes`. Respostas SHALL usar `no-store`. A autorização dos endpoints atuais SHALL permanecer.

#### Scenario: Bloquear antes de consumir
- **WHEN** anônimo, Administrador ou cliente sem Origin/CSRF válidos tenta enviar, inclusive com JSON inválido
- **THEN** recebe a falha de autorização aplicável antes da validação do conteúdo e nenhuma chamada ao Gemini ocorre

#### Scenario: Não ampliar acesso por prefixo
- **WHEN** cliente solicita `/api/tutoria-outra` ou uma rota administrativa existente
- **THEN** não recebe permissão de Aluno pela semelhança do caminho com `/api/tutoria`

#### Scenario: Uso ainda não aceito
- **GIVEN** Aluno com aceite ausente ou anterior ao uso vigente
- **WHEN** envia dúvida válida
- **THEN** recebe 409 `termos_uso_pendentes`, com orientação para a página de privacidade, sem consumir o provedor

### Requirement: Segredo protegido e integração sem histórico
A chave SHALL existir somente no ambiente do backend e seguir em cabeçalho para o endpoint HTTPS fixo do Gemini. O envio SHALL conter somente instruções pedagógicas e os quatro campos de estudo, com armazenamento de interação desativado. Dúvidas, respostas, chave, cookies, identidade e resultados pessoais SHALL NOT ser registrados em logs ou enviados como contexto automático.

#### Scenario: Inspecionar a chamada externa
- **WHEN** a chamada é observada em teste unitário
- **THEN** usa `store=false`, não inclui `previous_interaction_id`, ferramentas ou execução em segundo plano e não contém nome, e-mail, ID da conta, sessão, histórico ou desempenho
- **AND** a chave não está em URL, resposta HTTP ou ativo do frontend

#### Scenario: Conferir ausência de persistência
- **WHEN** a consulta termina e a página é recarregada ou a conta é trocada
- **THEN** a dúvida e a resposta não são restauradas por banco, cache da aplicação ou armazenamento do navegador
- **AND** o sistema não promete ausência absoluta de processamento ou retenção operacional pelo provedor externo

### Requirement: Disponibilidade e falhas externas explícitas
O Tutor SHALL retornar 503 `tutor_indisponivel` quando desabilitado ou sem configuração. Timeout SHALL retornar 502 `tutor_timeout`; rede, rejeição HTTP, bloqueio, resposta incompleta, JSON inválido ou texto ausente/malformado SHALL retornar 502 com código seguro específico. Erro interno SHALL retornar 500 genérico. Nenhuma falha SHALL produzir resposta de estudo fictícia ou repetição automática.

#### Scenario: Sistema sem Gemini configurado
- **WHEN** a aplicação inicia sem chave ou com Tutor desabilitado e Aluno habilitado tenta enviar
- **THEN** os recursos anteriores continuam funcionando e o Tutor responde 503 sem chamada externa

#### Scenario: Resposta REST válida
- **WHEN** Gemini retorna interação concluída com blocos textuais finais nas etapas de saída
- **THEN** a API extrai somente o texto final e valida as quatro seções, sem exigir um campo JSON `output_text` nem mostrar raciocínio interno

#### Scenario: Provedor não conclui
- **WHEN** ocorre timeout, erro HTTP, resposta bloqueada, sem texto, sem as quatro seções, excessiva ou JSON inválido
- **THEN** a API retorna 502 com mensagem segura, não expõe corpo/credenciais do provedor e não anuncia sucesso

### Requirement: Consumo limitado na demonstração
Cada processo SHALL admitir no máximo uma chamada em andamento e quatro tentativas externas por janela de 60 segundos por conta, além de duas chamadas externas simultâneas no total. Excesso SHALL retornar 429 `limite_tutoria` com `Retry-After`, sem consumir o provedor. Os limites SHALL ser atômicos e limitados em memória; a documentação SHALL explicitar reinício e ausência de coordenação entre processos.

#### Scenario: Envios concorrentes da mesma conta
- **WHEN** a mesma conta envia duas dúvidas simultaneamente
- **THEN** no máximo uma segue ao provedor e a outra recebe 429 sem iniciar chamada

#### Scenario: Janela ou capacidade esgotada
- **WHEN** a conta esgota quatro tentativas em 60 segundos ou as duas vagas globais estão ocupadas
- **THEN** recebe 429; falhas externas contam como tentativa e todas as vagas em andamento são liberadas ao terminar, inclusive após erro

### Requirement: Tela de revisão acessível e fiel ao recorte
`/aluno/tutor.html` SHALL oferecer Matéria, Assunto, dúvida, aviso de IA falível e de não envio de dados pessoais, além de envio explícito ao Gemini. SHALL reutilizar o padrão visual oficial e disponibilizar estados vazio, enviando, sucesso, validação, uso pendente, limite, timeout e falha. Ações futuras de chat, resumos e escrita no plano SHALL permanecer indisponíveis.

#### Scenario: Escolher contexto e enviar
- **WHEN** Aluno abre o Tutor pela navegação
- **THEN** seleciona Matéria e Assunto do catálogo ativo, informa a dúvida e envia conscientemente os nomes selecionados e o nível fixo `ensino_medio`
- **AND** não existe envio automático ao abrir, selecionar filtros ou preencher sugestão; catálogo vazio ou falho impede envio e mostra estado real

#### Scenario: Responder com segurança
- **WHEN** a resposta contém marcação HTML, scripts, links ou sintaxe Markdown
- **THEN** a tela mostra o conteúdo como texto, sem execução, navegação automática ou interpretação de HTML
- **AND** as quatro seções permanecem legíveis por teclado, a 1440 px e 390 px, sem rolagem horizontal

#### Scenario: Falha com dúvida preenchida
- **GIVEN** mesma conta e uma dúvida em processamento
- **WHEN** ocorre erro ou o limite de espera da interface é alcançado
- **THEN** a dúvida continua disponível para tentativa explícita, o botão é liberado e nenhuma repetição automática ocorre
- **AND** uma resposta anterior, se mantida, fica identificada com sua própria pergunta, sem representar sucesso do envio que falhou

#### Scenario: Troca de identidade ou saída
- **WHEN** a sessão se perde, o Aluno sai, troca de conta ou abandona a página durante o envio
- **THEN** os dados privados são retirados, a requisição local é cancelada quando possível e resposta atrasada não reaparece para outra conta

### Requirement: Evidência de funcionamento sem substituir integração real
A entrega SHALL documentar contrato, configuração, limites, falhas e validação de uma chamada real com dúvida sintética. Suítes comuns SHALL funcionar sem chave e sem chamadas pagas; simulações de transporte SHALL existir somente em testes unitários. Integrações de autenticação e privacidade SHALL usar MySQL real. Sem evidência do provedor real, a entrega SHALL declarar essa validação pendente.

#### Scenario: Validar o material da aula
- **WHEN** a funcionalidade é verificada
- **THEN** há evidência sem segredos de sucesso real, erro 400 sem consumo externo, timeout controlado, separação Controller/Services e chave ausente do frontend
- **AND** o teste controlado de timeout é identificado como unitário, sem ser apresentado como falha observada no provedor real

#### Scenario: Preservar a entrega anterior
- **WHEN** a suíte e os fluxos anteriores são executados após a alteração
- **THEN** permanecem os vinte casos, os 21 mappers e os recursos SQL atuais, sem nova persistência de conversa ou regressão de consentimento do plano
