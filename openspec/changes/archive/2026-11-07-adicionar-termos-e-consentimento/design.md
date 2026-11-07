# Design — Termos e consentimento do plano

## Context

Ver motivação e escopo em [proposal.md](proposal.md). A sessão e as permissões já são verificadas em `auth_http.py`; o cadastro rejeita qualquer campo além dos quatro atuais. Os quatro Services de plano ainda não consultam consentimento. A geração e a conclusão já bloqueiam a linha de `Usuario`, utilizando `TransactionManager`.

`PlanoEstudo` e `PlanoEstudoItem` impedem exclusão pelo ORM; a FK entre gerações usa RESTRICT. Portanto, registrar revogação sem alterar o acesso ao plano seria insuficiente, e uma eliminação precisa ser uma exceção explícita, pequena e testada. Não haverá framework de consentimento, módulo genérico de políticas ou biblioteca nova.

## Goals / Non-Goals

**Goals:** dois textos completos e acessíveis; decisões explícitas persistidas; autorização opcional efetiva para o plano; transações curtas e idempotentes; limites acadêmicos verificáveis.

**Non-Goals:** os itens declarados fora de escopo na proposta. Não modificar a fórmula de desempenho, o seletor determinístico, os snapshots durante uso normal ou o controle de versão editorial.

## Decisions

### 1. Documentos estáticos completos e identificáveis

As fontes dos textos publicados serão `frontend/legal/termo-de-uso-v1.html` e `frontend/legal/termo-de-consentimento-plano-v1.html`. Serão páginas HTML sem necessidade de sessão ou JavaScript, com título, versão `1.0`, data efetiva da elaboração, seções, linguagem simples, links entre documentos, retorno fixo ao cadastro e estilo de impressão. `docs/legal/README.md` e README apontarão para essas fontes; não manter cópias integrais divergentes. Os modelos DOCX do professor orientam o conteúdo, não impõem coleta de CPF, testemunhas ou upload de documentos.

Um módulo pequeno `app/domain/privacidade.py` conterá os metadados de versões conhecidas: tipo, versão, URL local fixa e SHA-256 dos bytes UTF-8 do documento. Um mapa separado indica a versão vigente de cada tipo. O teste compara os hashes registrados aos HTML. Documento publicado será imutável: alteração de texto exige novo arquivo/versão, novo hash e atualização explícita dos vigentes; o documento anterior continua acessível. Não haverá editor nem publicação de termos pelo painel.

`ConsultarTermosService` fornece esses metadados em `GET /api/termos`; é uma leitura de documentos públicos, não um caso CRUD ou uma funcionalidade adicional contabilizada isoladamente. API e frontend não dependem de ler arquivos um do outro em runtime, permitindo futura implantação separada. HEAD herda GET; respostas usam `no-store`. O middleware libera apenas GET/HEAD nessa rota exata, sem cookies obrigatórios; POST e caminhos desconhecidos conservam 405/404.

### 2. Conteúdo e limites das minutas

O Termo de Uso deve cobrir finalidade educacional, público amplo, funcionamento disponível, responsabilidades de conta/senha, proibições aplicáveis, limitações de resultados pedagógicos, privacidade, dados necessários, segurança efetivamente implementada, eventual revisão de versão e limites desta demonstração. O tratamento necessário à prestação solicitada deve ser distinguido da autorização opcional do plano; não invocar simultaneamente bases legais genéricas para toda operação.

O Termo de Consentimento terá finalidade delimitada: utilizar o desempenho próprio para selecionar até três Assuntos, gerar/manter snapshots e registrar conclusão manual de plano. Informará dados usados, benefício, caráter opcional, consequências da recusa/revogação, inexistência de IA nesse cálculo, ausência de promessa de nota e acesso posterior ao texto/registro. Não autoriza publicidade, publicação dos resultados individuais, compartilhamento com LLM nem mudança na finalidade de respostas e simulados.

Ambos identificarão Matheus Gabriel Oliveira Martins como responsável informado pelo grupo e o endereço `contato@plataformaenem.example` como **fictício e não operacional**, sem link de atendimento que finja funcionar. Aviso explícito: minutas para demonstração acadêmica com dados sintéticos; antes de uso real, definir canal válido, política geral de retenção/exercício de direitos e a change de proteção/autorização de menores. Não atribuir representação institucional, cargo DPO ou certificação a alguém sem essa definição.

Não coletar idade, data de nascimento ou documento nesta change e não criar bloqueio de produto por idade. Também não transformar uma marcação do próprio estudante em suposta autorização verificada de responsável. Essa limitação deve aparecer nos documentos, README e operação, sem afirmar que o público menor já está atendido operacionalmente.

Retenção neste recorte: planos existem enquanto a autorização permanece válida; decisão negativa confirmada elimina os derivados imediatamente. Os registros mínimos das decisões permanecem associados à conta para consulta e prova do fluxo. Exclusão da conta e prazo posterior desses comprovantes, retenção das respostas e tratamento de backups exigem política geral antes de dados reais; não inventar prazo legal universal nem prometer exclusão automática de backups. Revogação nesta change não equivale a exclusão de conta ou de respostas.

Referências consultadas em 06/11/2026, para a adaptação acadêmica:

- [LGPD, especialmente arts. 7º–9º, 14, 16, 18 e 19](https://www2.camara.leg.br/legin/fed/lei/2018/lei-13709-14-agosto-2018-787077-normaatualizada-pl.html): finalidades determinadas, transparência, direitos e consentimento revogável. Corrigir a referência do modelo: o prazo de 15 dias do art. 19 trata da declaração completa de confirmação/acesso, não de todos os direitos indistintamente.
- [Orientação da ANPD sobre crianças e adolescentes](https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-divulga-enunciado-sobre-o-tratamento-de-dados-pessoais-de-criancas-e-adolescentes): avaliar as bases e o melhor interesse, sem copiar a afirmação de que todo tratamento de todo menor depende exclusivamente de consentimento.
- [ECA Digital, Lei 15.211/2025](https://www2.camara.leg.br/legin/fed/lei/2025/lei-15211-17-setembro-2025-797997-normaatualizada-pl.html): proteção do público menor precisa de avaliação própria antes da operação real; este plano não declara adequação integral.

### 3. Uma Model de evidência, sem cadastro presumido

Tabela nova `registros_privacidade`, Model `RegistroPrivacidade` herdando `ModeloBase`, com eventos ORM que rejeitam alteração e exclusão comuns:

| Campo | Definição |
| --- | --- |
| `id` | BIGINT, PK autoincremental |
| `usuario_id` | INTEGER obrigatório, FK `usuarios.id`, RESTRICT em update/delete |
| `tipo` | VARCHAR(8), `uso` ou `plano` |
| `acao` | VARCHAR(8), `aceitar`, `recusar` ou `revogar`; `uso` admite somente `aceitar` |
| `versao` | VARCHAR(20), obrigatória, versão conhecida do documento |
| `documento_sha256` | CHAR(64) ASCII/binário, minúsculo hexadecimal; calculado/selecionado pelo servidor |
| `registrado_em` | DATETIME(6), UTC do servidor, obrigatório |
| `chave_envio` | CHAR(36) ASCII/binário, UUID canônico, obrigatório |
| `revisao_base` | BIGINT não negativo, ID da decisão anterior daquele tipo ou zero |

UNIQUE `(usuario_id, chave_envio)` e índice `(usuario_id, tipo, id)` para última decisão. CHECKs de tipo/ação, combinações e revisão não negativa. Não armazenar texto da senha, token, sessão, IP, CPF ou User-Agent como evidência.

Salvar registro individual é responsabilidade da Model com `confirmar=False`. `PrivacidadeRepository` consulta últimas decisões por tipo e reenvio por usuário/chave; não replica CRUD. Última decisão é o maior ID do tipo para a conta, não uma linha arbitrária por timestamp. Estado de autorização exige última ação `aceitar` **e** versão/hash vigentes, tanto para uso quanto plano. Uma versão anterior aceita nunca vira aceite da nova automaticamente.

Sem backfill: usuários e planos anteriores à migration são preservados, mas nenhuma decisão é criada. O primeiro acesso ao plano mostra a necessidade de decidir; outras funções permanecem acessíveis. Usuários antigos podem aceitar Termo de Uso na página de privacidade. CLI de Administrador continua com os quatro campos originais e não recebe um aceite fictício.

### 4. Controllers e Services pequenos

Manter `Frontend -> Route -> PrivacidadeController -> Service -> Model/Repository -> MySQL`. Novos casos: `ConsultarTermosService`, `ConsultarPrivacidadeService`, `AceitarTermosUsoService`, `ConsentirPlanoService`, `RecusarConsentimentoPlanoService`, `RevogarConsentimentoPlanoService` e `ValidarPermissaoPlanoService`. Cada classe executa somente sua ação; validações e serialização comuns ficam em `privacidade_validacao.py` e no módulo de domínio, sem importar helpers privados de outro caso de uso.

Controller interpreta HTTP e responde pelo padrão existente, sem regra de negócio, SQL ou acesso à sessão do banco. O guard de permissão é chamado pelos Services de plano, não apenas pelo JavaScript e não dentro do cálculo reutilizável do diagnóstico. Não ampliar a composição SOLID inteira nem criar novas interfaces artificiais para operações concretas de escrita.

### 5. Contratos HTTP

`GET /api/termos` retorna 200 `{termos_uso:{versao,url,sha256}, consentimento_plano:{versao,url,sha256}}`, com metadados vigentes. URLs apontam exclusivamente para os dois HTML locais conhecidos, sem parâmetro de redirecionamento externo.

`GET /api/aluno/privacidade` retorna 200:

```text
{
  termos_uso: {versao_vigente, documento_url, registro, aceite_vigente},
  consentimento_plano: {versao_vigente, documento_url, registro, estado},
  plano_liberado: boolean
}
```

`registro` é null ou `{id,acao,versao,documento_sha256,registrado_em}`. Datas usam ISO UTC com Z. Estado do plano: `nao_informado`, `aceito`, `recusado`, `revogado` ou `desatualizado`; somente última aceitação de versão/hash não vigentes produz `desatualizado`. Recusa/revogação continuam negativas após mudança de versão. `plano_liberado` exige os dois aceites vigentes. A consulta não cria registros nem gera plano, e a leitura dos dois tipos compartilha uma visão consistente.

| Método/rota | Corpo exato | Efeito |
| --- | --- | --- |
| `POST /api/auth/cadastro` | Os quatro campos atuais + `termos_uso:{versao,aceito:true}` | Conta e aceite de uso atômicos; resposta 201 atual, sem consentimento do plano |
| `POST /api/aluno/privacidade/termos-uso` | `{versao,chave_envio,revisao}` | Registra somente aceite de uso |
| `POST /api/aluno/privacidade/consentimento-plano/aceitar` | `{versao,chave_envio,revisao}` | Registra autorização opcional se uso estiver aceito/vigente |
| `POST /api/aluno/privacidade/consentimento-plano/recusar` | `{versao,chave_envio,revisao,confirmar:true}` | Registra recusa e elimina planos legados, se existirem |
| `POST /api/aluno/privacidade/consentimento-plano/revogar` | `{versao,chave_envio,revisao,confirmar:true}` | Revoga última aceitação e elimina todos os planos próprios |

Nas três ações de plano, `revisao` é ID do último registro **de plano**, ou zero; no aceite de uso, o último **de uso**. Inteiros rejeitam booleanos; UUID é canônico; versão é string conhecida para decisões novas. Campos extras/ausentes ou confirmação diferente do booleano true retornam 400 `dados_invalidos`. Nenhuma rota aceita `usuario_id`, hash ou data fornecidos pelo cliente.

Para aceite/recusa/novo cadastro exige-se a versão vigente do tipo. Revogação usa versão e hash da última aceitação persistida, inclusive se desatualizada; não depende de essa versão ainda ser vigente ou constar no mapa em memória. Seu texto antigo continua acessível. Versão divergente gera 409 `termo_desatualizado`; estado/revisão/chave conflitante gera 409 `decisao_desatualizada`. Recusar quando a última ação for aceitar e revogar sem última aceitação geram 400 `decisao_invalida`: a UI apresenta a ação correspondente, sem chamar uma recusa de revogação. Nova aceitação exige uso vigente, senão 409 `termos_uso_pendentes`.

Mutações novas retornam 201 `{registro,privacidade}`. Reenvio idêntico pela mesma chave retorna 200 com o registro original e a **privacidade atual**, sem repetir efeitos. Chave reaproveitada com outra rota, versão ou revisão-base retorna 409. Reenvio não restaura decisão antiga nem volta a eliminar um plano criado após nova autorização.

Todas as rotas privadas exigem Aluno, propriedade exclusivamente pela sessão, `no-store`, Origin e CSRF nas mutações. Anônimo recebe 401 e Administrador 403. O corpo/DTO de login e sessão não muda. Não adicionar privilégio administrativo de consultar decisões individuais.

### 6. Ordem transacional e autorização do plano

Ordem para mutação de privacidade: autenticação/CSRF; validação estrutural; `TransactionManager`; lock da linha do usuário; busca de chave; comparação do reenvio; validação de versão, revisão e transição; gravação da decisão e eventual eliminação; um único commit. A comparação de replay ocorre antes de exigir versão/revisão atualmente vigentes, para recuperar uma resposta perdida sem aplicar novamente sua decisão antiga. Cadastro gera a chave do aceite no servidor após criar a nova conta, com revisão-base zero, na mesma transação já responsável pelo usuário. Adaptar `CadastrarAlunoService`/sua coordenação; compartilhar preparação/validação do usuário com o caminho administrativo, mas não chamar um Service que faça commit intermediário. Preservar validação de credenciais e a CLI administrativa.

O mesmo lock de usuário serializa consentimento, recusa, revogação e os quatro casos do plano. Últimas decisões e chaves usam leituras correntes com lock e `populate_existing`, não o snapshot antigo que uma consulta de autenticação possa ter iniciado em REPEATABLE READ. Em gerar/recalcular, conferir permissão **depois do lock e antes de buscar replay ou consultar diagnóstico**. Em concluir, antes de buscar o item. Consultar passa a usar fronteira curta com o mesmo lock e consulta de consentimento antes de serializar o plano. Falha de leitura de consentimento gera erro 500, nunca autorização padrão.

Sem os dois aceites vigentes, APIs de plano retornam 403 `consentimento_plano_necessario`, sem snapshot ou consulta de diagnóstico. Para usuário autorizado, preservar todos os corpos/respostas, seleção, idempotência e 404 para item alheio. A regra de consentimento precede a consulta de item: usuário não autorizado recebe o mesmo 403 independentemente do ID tentado.

`ConsultarPrivacidadeService` também lê o estado sob a mesma fronteira/lock, sem criar decisão, para não combinar um registro de uso antigo com outro estado de plano. Não manter lock durante interação humana ou chamadas HTTP.

### 7. Eliminação delimitada dos derivados

Negativa exige aviso e confirmação: "Se houver planos salvos, eles e suas conclusões serão apagados. Suas respostas, simulados e desempenho continuarão disponíveis." Ao cancelar, não enviar POST. A exceção deve ser registrada no ADR-009 e na operação de plano, preservando guards ORM e métodos normais imutáveis.

Um único método especializado de `PrivacidadeRepository` seleciona os IDs dos planos em leitura corrente com lock, elimina os itens ligados aos planos **do usuário bloqueado** e depois as gerações em ID decrescente, respeitando a FK RESTRICT entre gerações. A instrução de cada exclusão inclui o usuário, além do ID; não desativar FKs, não relaxar a Model para deleção genérica, não alterar o histórico editorial nem executar SQL no Service. Usar operações de persistência especializadas que não disparem a exclusão ORM proibida, somente por esse caso transacional e com testes de escopo. É uma exceção de privacidade deliberada, não um método CRUD de Repository.

Apagar todos os derivados e salvar decisão são atômicos. Falha em qualquer etapa reverte ambos. Dados de outra conta, práticas, tentativas de simulado, métricas deriváveis, catálogo e evidências de privacidade permanecem. Nova autorização permite gerar plano novo, com nova chave; não recupera snapshots eliminados. Contagem de geração pode reiniciar em 1 porque não restou histórico de plano daquela conta; IDs de banco não são reutilizados.

Se geração vence a disputa de lock, negativa posterior elimina o plano que ela acabou de criar; se negativa vence, geração posterior retorna 403. Nenhuma decisão concorrente pode reautorizar usando uma revisão antiga. A eliminação é irreversível na aplicação; não anunciar recuperação ou exclusão imediata em backups.

### 8. Interface, sessão e navegação

Cadastro carrega metadados antes de habilitar o aceite, oferece links aos dois documentos e checkbox de uso desmarcado. Consentimento do plano não aparece como obrigatório no cadastro. Nova versão conflitando com o envio exige recarregar metadados, mostrar a mudança e desmarcar o aceite; nunca reenviar cadastro automaticamente.

`/aluno/privacidade.html` mostra os dois documentos, versão/data/ação registradas e estados sem decisão/pendente/aceito/recusado/revogado/desatualizado. Oferece aceitar uso, autorizar plano ou recusar com o mesmo destaque visual, e revogar quando houver aceitação, inclusive antiga. Origem do acesso é link fixo em início e plano; login/cadastro oferecem leitura pública dos documentos. Não reestruturar a navegação inteira nem interromper prova/simulado em andamento para obter aceite.

Plano verifica `/aluno/privacidade` antes de buscar dados do plano. Sem permissão, mostra explicação e link para decidir, sem lista residual. Após negativa, limpa a tela do plano, dados pendentes e UUIDs de ações, mantendo apenas estado público de decisão. Em retorno de outra aba, conferir identidade e permissão antes de reexibir conteúdo; erro ou 403 retira snapshots anteriores. Resposta atrasada de outra identidade/geração local é ignorada. Reenvios de privacidade usam a mesma chave/corpo pendentes e nunca são automáticos; a resposta traz estado atual para não mostrar uma aceitação histórica como vigente.

Reutilizar AuthUI, proteção de troca de conta, tratamento de sessão expirada e apiRequest; não usar localStorage para aceite ou dados privados. Teclado, foco, leitores de tela, mensagens reais e larguras 1440/390 devem ser verificados. O cadastro continua mantendo nome/e-mail em erro, sem senha em URL ou logs.

## Risks / Trade-offs

- Contato fictício e ausência do fluxo de menores podem sugerir prontidão jurídica → avisos de minuta acadêmica e checklist de pré-publicação; nenhuma habilitação para dados reais nesta change.
- Revogação conflita com histórico imutável → exceção especializada, confirmada, atômica e restrita aos derivados de plano, com ADR e cenários de falha/concorrência.
- Obrigatoriedade do novo campo pode quebrar consumidores e fixtures → atualizar frontend e helpers de testes juntamente com a API; documentar BREAKING, sem aceitar payload antigo presumindo aceite.
- Hash divergente de texto publicado ou resposta antiga de aba → testes dos documentos imutáveis, versão explícita, revisão-base, locks e descarte de respostas obsoletas.
- Aumentar complexidade por um bônus → uma tabela nova, HTML estático e Services concretos pequenos; nenhum provedor externo, painel de termos, assinatura ou framework novo.

## Migration Plan

1. Registrar baseline dos arquivos afetados sem ler/exibir `.env`; preservar mudanças locais legítimas. Registrar checksums de migrations 000–009, contagens funcionais e contratos atuais em ambiente de teste.
2. Acrescentar `010_create_registros_privacidade.sql` após 009, apenas criando a tabela vazia. Atualizar `create_database.sql` e o reconhecimento no módulo atual `backend/database/legacy_schema.py`; preservar reexports do runner refatorado. Não executar DDL no startup.
3. Validar instalação vazia, upgrade de 009 com usuários/planos/respostas, baseline do snapshot 010, segunda execução sem reaplicar, drift e equivalência com MySQL 8 real descartável. Nenhuma conta/plano será excluída ou consentida pelo upgrade.
4. Entregar frontend, backend, documentos e metadados em conjunto. Para banco real futuro, exigir backup, ensaio e autorização operacional própria; o apply usa apenas schemas de teste e não altera o banco operacional por conta própria.
5. Rollback de DDL não é automático: usar backup ou migration compensatória revisada. Não apagar evidências de decisão para voltar ao código anterior; desabilitar acesso ao plano durante reconciliação. A exclusão confirmada por usuário não pode ser desfeita pela aplicação e deve ser informada antes da ação.

## Validação prevista

Unitários: estados/transições, versões, hashes, validação estrita, Model imutável, chamadas por camada e ausência de SQL/session em Controllers/Services. Integração MySQL: atomicidade do cadastro, decisão e eliminação, propriedade, perfis, CSRF, chaves/revisões, concorrência, evolução de schema e regressão dos casos atuais. Vitest: checkbox desmarcado, estados/erros, confirmação, troca de identidade, resposta atrasada e limpeza de dados. Playwright: leitura pública, cadastro, recusa com questões/simulados utilizáveis, aceite, plano real com base suficiente, negativa, nova autorização e ausência de plano antigo; atualizar o E2E de plano existente para consentir pela interface. Executar cobertura exigida e registrar resultados reais, sem alegar conformidade jurídica ou bônus garantido.
