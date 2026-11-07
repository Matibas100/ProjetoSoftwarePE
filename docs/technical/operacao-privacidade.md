# Operação de termos e consentimento

Código canônico: [`backend/app/modules/contas/`](../../backend/app/modules/contas/);
interfaces e transações no [mapa modular](organizacao-modular.md).

## Documentos e limites

Fontes e modelos: [minutas](../legal/README.md). Os dois HTML são públicos,
sem JavaScript, legíveis por teclado e imprimíveis. O módulo
`app/modules/contas/domain/privacidade.py` guarda versões, URLs locais e SHA-256 dos bytes.
Qualquer alteração em texto publicado exige novo arquivo/versão/hash; o arquivo
anterior permanece. API e frontend não leem arquivos um do outro em runtime.

Responsável informado: Matheus Gabriel Oliveira Martins. O endereço
`contato@plataformaenem.example` é fictício e não operacional. Usar apenas dados
sintéticos. Antes de dados reais: contato válido, política geral de retenção e
direitos e proteção/autorização de menores em change própria. Não há coleta de
idade nem autorização parental verificada; não se declara conformidade integral
ou certificação ISO. A avaliação do bônus cabe ao professor.

## Schema e implantação

`010_create_registros_privacidade.sql` cria apenas uma tabela vazia depois de
009; não faz backfill de decisões nem apaga planos, respostas ou usuários.
Snapshot e fingerprint 010 são equivalentes à sequência. O runner oficial
permanece `backend/database/migrate.py`, sem DDL no startup. As migrations
000–009 e a procedure permanecem intactas.

O reconhecimento 008–010 usa assinatura de metadados estruturais conhecidos,
derivada das migrations oficiais. Charset explícito/implícito na apresentação
do DDL não diverge quando os metadados são iguais; alterações de collation,
default, índices, FKs, CHECK/ENFORCED ou expressões geradas são recusadas.
Nome físico e contadores não entram na assinatura; referências externas de FKs
mantêm sua identidade. Ausência de metadado obrigatório causa erro e não há
promessa de compatibilidade universal entre versões.
Corpo e parâmetros da procedure conhecida também são conferidos em 008–010.

Assinatura estrutural, checksum do SQL em `schema_migrations` e SHA-256 dos HTMLs
legais têm finalidades diferentes: reconhecer estrutura, proteger arquivos
aplicados e identificar documentos aceitos. Os dois últimos não mudam.
Ver [adendo ao ADR-001](adr/ADR-001-estrategia-de-migrations.md#22-adendo--assinatura-estrutural-portável-2026-11-07).

Ensaiar instalação vazia, upgrade de 009 com dados, segunda execução,
equivalência com snapshot, baseline explícito 010 e rejeição de drift em MySQL
descartável. Na implantação real futura: backup, ensaio em cópia, autorização
operacional própria, `status`, `up` e conferência de checksums/estrutura.
Esta execução de apply usa somente schemas de teste e não implanta no banco
operacional. DDL não tem downgrade automático. Reverter por backup ou migration
compensatória revisada, preservando evidências e suspendendo acesso ao plano
durante reconciliação; não apagar registros para executar código antigo.

`RegistroPrivacidade` herda `ModeloBase`: salvar/consultar, sem atualizar/deletar.
Eventos ORM bloqueiam alterações/exclusões usuais. Campos obrigatórios: usuário
FK RESTRICT, tipo, ação, versão, hash, data UTC DATETIME(6), UUID e revisão-base.
UNIQUE usuário/chave e índice usuário/tipo/id. CHECKs limitam tipos, ações,
uso somente aceitar e revisão não negativa. Não há senha, token, IP, CPF ou
User-Agent na evidência. O timestamp é do servidor; consultas usam ISO UTC `Z`.

## Contratos

| Método e rota | Corpo | Retorno/efeito |
| --- | --- | --- |
| GET/HEAD `/api/termos` | Sem corpo | 200 `{termos_uso:{versao,url,sha256},consentimento_plano:{versao,url,sha256}}`, público, no-store |
| GET/HEAD `/api/aluno/privacidade` | Sem corpo | 200 estado próprio, sem criar decisões |
| POST `/api/auth/cadastro` | `nome,email,senha,senha_confirmacao,termos_uso:{versao,aceito:true}` | 201 DTO anterior, usuário+aceite atômicos, sem login ou consentimento do plano |
| POST `/api/aluno/privacidade/termos-uso` | `{versao,chave_envio,revisao}` | Aceitar uso |
| POST `/api/aluno/privacidade/consentimento-plano/aceitar` | Mesmo corpo | Autorizar plano, exigindo uso vigente |
| POST `/api/aluno/privacidade/consentimento-plano/recusar` | Mesmo corpo + `confirmar:true` | Recusar sem última aceitação; eliminar derivados próprios |
| POST `/api/aluno/privacidade/consentimento-plano/revogar` | Mesmo corpo + `confirmar:true` | Revogar última aceitação, inclusive antiga; eliminar derivados próprios |

Privacidade retorna `termos_uso:{versao_vigente,documento_url,registro,aceite_vigente}`,
`consentimento_plano:{versao_vigente,documento_url,registro,estado}` e
`plano_liberado`. Registro é null ou `{id,acao,versao,documento_sha256,registrado_em}`.
Estado do plano: `nao_informado`, `aceito`, `recusado`, `revogado`, `desatualizado`.
A última ação negativa permanece negativa após atualização de versão.
Liberação exige ambas as últimas aceitações com versão e hash vigentes.

Privadas exigem Aluno por sessão (anônimo 401, Administrador 403), no-store,
Origin e CSRF nas mutações. Nenhuma recebe usuário/hash/data do cliente.
HEAD herda GET sem corpo; método/rota inexistente preservam 405/404.
Corpo exato, UUID canônico e revisão inteira não booleana; booleano true
obrigatório nas confirmações. Inválidos: 400 `dados_invalidos`.
Aceite/recusa/cadastro requerem versão vigente; divergência: 409
`termo_desatualizado`. Autorizar sem uso vigente: 409 `termos_uso_pendentes`.
Recusar última aceitação ou revogar sem aceitação: 400 `decisao_invalida`.
Revogação usa versão/hash da última aceitação persistida, mesmo fora do mapa.

## Atomicidade, concorrência e reenvio

Após validação estrutural, `TransactionManager` bloqueia a linha do usuário.
Últimas decisões (maior ID de cada tipo) e chaves usam leituras correntes com
lock/populate_existing, mesmo após snapshot antigo da autenticação.
Revisão é o ID anterior daquele tipo, ou zero. Revisão obsoleta ou chave usada
em outra rota/versão/revisão: 409 `decisao_desatualizada`.

Replay é verificado antes da versão/revisão atuais. Nova decisão retorna 201
`{registro,privacidade}`; reenvio idêntico retorna 200 com registro original e
estado atual, sem reaplicar efeitos. Assim, reenviar uma negativa antiga após
nova autorização não elimina o novo plano nem muda a decisão mais recente.
Uma falha ou perda de resposta exige nova ação explícita, com o mesmo corpo e
UUID pendentes; não existe reenvio automático.

Recusa/revogação exigem aviso e confirmação. Salvar negativa e eliminar todos
os planos próprios confirmam ou revertem juntos. O Repository elimina itens
restritos ao usuário/plano e gerações em ID decrescente, respeitando RESTRICT.
Guards normais continuam ativos. Outra conta, respostas, simulados e evidências
permanecem. A eliminação é irreversível na aplicação, sem promessa de recuperação
ou exclusão imediata em backups. Nova autorização começa sem planos antigos.

Os quatro casos do plano usam o mesmo lock e validam permissão antes de replay,
snapshot, item ou diagnóstico. Sem autorização: 403 uniforme
`consentimento_plano_necessario`; falha de consulta: 500, nunca autorização por
padrão. Consulta de privacidade também mantém essa fronteira curta consistente.
Se geração vence o lock, a negativa posterior elimina inclusive a geração nova;
se a negativa vence, geração/recálculo recebe 403. Ver [ADR-009](adr/ADR-009-consentimento-e-eliminacao-do-plano.md).

## Interface e retenção

Cadastro carrega metadados, mantém checkbox inicialmente desmarcado e nunca
autoriza o plano. Conflito de versão recarrega termos e desmarca o aceite, sem
reenviar cadastro. Login oferece leitura pública. `/aluno/privacidade.html`
mostra evidências e escolhas; autorizar/recusar usam o mesmo destaque. Cancelar
o aviso negativo não envia POST. Início e plano oferecem acesso fixo.

Plano consulta privacidade antes de carregar e reexibir conteúdo. Retorno de
outra aba, troca de conta, perda de permissão ou erro retiram snapshots; resposta
de geração/identidade anterior não os restaura. Reenvio pede ação explícita e
nova verificação. Recuperação da mesma conta preserva a intenção em memória;
outra conta a descarta. Não se utiliza localStorage para decisões/dados privados.

Planos duram enquanto autorizados; negativas confirmadas eliminam derivados
imediatamente. Evidências mínimas ficam vinculadas à conta. Retenção geral de
respostas, destino de comprovantes após encerramento, backups e direitos gerais
continuam pendentes. Revogação do plano não equivale a exclusão de conta.

A eliminação especializada pertence agora ao Repository de Plano, chamada pelo
Service participante injetado em Recusar/Revogar. Não há commit interno nem endpoint
novo; Contas mantém o lock e a única fronteira transacional (ADR-010).
