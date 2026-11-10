# Operação do Tutor IA

Abra `/aluno/tutor.html` pela navegação do Aluno. Selecione Matéria/Assunto ativos,
escreva uma dúvida de 10–2000 caracteres e confirme **Enviar dúvida ao Gemini**.
Uso 2.0 precisa estar aceito na [privacidade](../../frontend/aluno/privacidade.html).
Plano recusado/revogado não bloqueia a tutoria. Atualizar uso não altera decisões
nem apaga planos; o plano exige uso vigente pela sua regra anterior.
[Uso 1.0](../../frontend/legal/termo-de-uso-v1.html) e consentimento do plano 1.0 permanecem
consultáveis, com bytes/hashes/evidências preservados.

## Configuração opcional

Por padrão, o Tutor está desabilitado e a plataforma funciona sem chave. Instale
`backend/requirements.txt` (`requests==2.34.2`). O responsável configura somente
no ambiente do backend, antes de iniciar uma aplicação local:

```text
TUTOR_IA_ENABLED=true
GEMINI_API_KEY=<chave local; nunca no frontend ou no Git>
GEMINI_MODEL=gemini-3.6-flash
```

`.env.example` contém apenas placeholders. Não coloque chave em URL, logs, ativos,
testes ou capturas. As suítes comuns mantêm Tutor desabilitado e não recebem chave
real; transporte controlado existe somente nos testes unitários. Ativar pode
consumir quota/custo, inclusive se o navegador cancelar a espera.

## Contrato HTTP

`POST /api/tutoria`, JSON com **exatamente quatro strings**:

```json
{
  "disciplina": "Física",
  "nivel": "ensino_medio",
  "assunto": "Eletricidade",
  "duvida": "Qual é a diferença entre corrente elétrica e tensão?"
}
```

Disciplina: 1–100 caracteres; assunto: 1–150; dúvida: 10–2000, após trim.
Nível fixo `ensino_medio`, corpo até 16384 bytes. Somente Aluno com sessão válida,
Origin permitido, CSRF e uso vigente; autorização HTTP precede leitura do corpo.
Sucesso: 200 `{disciplina, assunto, resposta}`. `resposta` tem até 12000 caracteres,
com títulos únicos, ordenados e em linhas próprias:

1. `1. Explicação simples`
2. `2. Exemplo`
3. `3. Verifique sua compreensão`
4. `4. Exercício curto`

Cada seção tem conteúdo; a instrução pede exercício sem gabarito e português
compatível com ENEM. A prova real inclui conferência pedagógica do conteúdo, sem garantir a qualidade de respostas futuras.

| HTTP | Código / situação |
| --- | --- |
| 400 | `dados_invalidos`: corpo/campos inválidos, antes de qualquer consumo externo |
| 401/403 | Falhas existentes de sessão/perfil/Origin/CSRF |
| 409 | `termos_uso_pendentes`: aceitar uso na privacidade |
| 413 | `corpo_muito_grande`: limite exclusivo desta rota |
| 429 | `limite_tutoria`: limite local, com `Retry-After` em segundos |
| 503 | `tutor_indisponivel`: desabilitado, chave ou modelo ausentes |
| 502 | `tutor_timeout`, `tutor_provedor_indisponivel` ou `tutor_resposta_invalida` |
| 500 | `erro_interno`: erro sanitizado |

Erros usam `{erro,codigo}`, sem corpo/headers do provedor. Todas as respostas são
`no-store`. Não há resposta de estudo substituta nem repetição automática.

## Camadas, limites e dados

`Tela → Route → TutoriaController → GerarTutoriaService → GeminiService → Gemini`.
A Controller adapta HTTP e captura somente o ID primitivo. O caso de uso valida,
chama a permissão pública de Contas (uso vigente) e encerra sua leitura transacional
antes da rede, verifica configuração, reserva o limite e libera em `finally`.
`GeminiService` encapsula REST HTTPS fixo, chave no cabeçalho `x-goog-api-key`,
`store=false`, prompt estável, quatro campos como dados e até 4096 tokens de saída.
Extrai só texto final da última etapa `model_output` em `steps`, sem pensamentos
ou dependência da conveniência SDK `output_text`.

Timeouts Requests: conexão 5 s, leitura 30 s, que não representam prazo global;
corpo externo limitado a 1 MiB e resposta sempre fechada. Interface espera até
45 s e cancela localmente quando possível, sem garantir cancelamento no Gemini.
Limite atômico por aplicação/processo: quatro tentativas externas/60 s por conta,
uma em andamento por conta, duas globais e até 1024 contas em memória. Falhas
externas contam; reinício zera contadores e workers não compartilham limites.
Isso não é proteção distribuída de orçamento para produção.

Não há histórico, ferramentas, desempenho automático, persistência de conversa,
Model, Repository, tabela ou novo CRUD. Perguntas/respostas não entram em banco,
logs ou armazenamento do navegador. `store=false` não garante retenção operacional
zero pelo provedor; não envie dados pessoais. A demonstração usa dados sintéticos,
com contato fictício e proteção/autorização de menores ainda pendentes.

## Evidências e demonstração

[tutor.spec.js](../../frontend/e2e/tutor.spec.js) acrescenta E2E com MySQL descartável:
uso antigo, aceite 2.0, navegação, aviso e 503 real com Tutor desabilitado, sem
interceptação do Gemini. Os vinte casos anteriores seguem nos outros E2E.
Python/DOM controlados verificam timeout, formato, sanitização, concorrência e
ciclo de identidade; não comprovam acesso real ao provedor.

Para a aula: com ambiente local preparado, use a tela autenticada e uma dúvida
sintética. Confira as quatro partes, pertinência ao ENEM e ausência de gabarito.
Uma requisição autenticada com objeto vazio demonstra 400 antes do provedor;
o timeout é comprovado em unidade, sem alegar falha real observada no Gemini.
Registre somente data/modelo/status/checklist, sem dúvida/resposta, chave ou sessão.
A [validação desta change](../../openspec/changes/archive/2026-11-09-adicionar-tutor-revisao-com-gemini/validacao.md)
distingue esses testes da prova real. Em 09/11/2026, uma dúvida sintética enviada
pela interface retornou **HTTP 200**, com as quatro partes e exercício sem gabarito
conferidos. Cadastro/aceite/login/catálogo e envio usaram Chromium com MySQL
descartável, sem interceptação do Gemini; a entrada inválida retornou 400.
O modelo foi `gemini-3.6-flash`. Timeout permanece comprovado somente em unidade.
Também houve falhas externas/formato recusado em execuções manuais, tratadas como
502 sem retry automático. O relatório guarda apenas metadata/checklist, sem
payloads, chave ou captura de sessão. Sem chave/acesso/quota em outro ambiente,
a prova real precisa ser repetida nele.
O fluxo atende à consulta de LLM com Controller/Services e não aumenta a contagem
de CRUD ou substitui vídeo, slides ou entrega acadêmica anterior.
