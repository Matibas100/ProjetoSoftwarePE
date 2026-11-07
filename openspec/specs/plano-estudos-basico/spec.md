# Plano de estudos básico

## Purpose

Gerar um plano persistido de Assuntos prioritários a partir do desempenho próprio do Aluno, com seleção explicável e recálculo explícito.

## Requirements

### Requirement: Priorização determinística baseada em desempenho
O plano SHALL priorizar Assuntos elegíveis pelo desempenho próprio, com ordenação determinística e justificativa.

#### Scenario: Ordenação e desempate
- **GIVEN** Assuntos elegíveis com 2/10, 1/5 e 4/10 acertos
- **WHEN** Aluno gera plano
- **THEN** ordem é 2/10, 1/5 e 4/10, com justificativas correspondentes e no máximo três itens

#### Scenario: Assunto transferido ou sem conteúdo
- **GIVEN** grupo histórico transferido para outra Matéria ou sem Questão atualmente elegível
- **WHEN** gera/recalcula plano
- **THEN** grupo é excluído sem reclassificar fatos e sem recomendar conteúdo indisponível

#### Scenario: Base temporal e elegibilidade dos Assuntos
- **GIVEN** diagnóstico do Aluno para geração ou recálculo
- **WHEN** o plano seleciona candidatos disponíveis
- **THEN** O plano SHALL usar diagnóstico dos últimos 30 dias UTC, selecionar até três Assuntos com pelo menos cinco respostas, catálogo ativo, vínculo Assunto–Matéria atual igual ao grupo histórico e Questões publicadas elegíveis.
- **THEN** SHALL NOT preencher vagas com amostra insuficiente ou inventar dificuldade quando acerto for 100%.

#### Scenario: Comparação exata e explicação de prioridades
- **GIVEN** Assuntos elegíveis para o plano
- **WHEN** o sistema ordena e apresenta as prioridades
- **THEN** SHALL ordenar por menor taxa exata de acerto, maior total de respostas e menor ID do Assunto, sem arredondar antes de comparar.
- **THEN** SHALL explicar prioridade relativa com acertos, total, percentual, período e amostra.

### Requirement: Geração persistida exclusiva do dono
O sistema SHALL consultar e gerar somente o plano do dono autorizado, com persistência atômica e idempotência.

#### Scenario: Gerar, reenviar e recarregar
- **GIVEN** Aluno com os dois aceites vigentes, sem plano e diagnóstico suficiente
- **WHEN** gera com chave válida, reenvia e recarrega
- **THEN** existe um único plano e ele mantém itens, ordem e justificativas originais

#### Scenario: Falta de base ou falha de diagnóstico
- **GIVEN** Aluno autorizado sem candidatos suficientes ou serviço de diagnóstico indisponível
- **WHEN** solicita geração
- **THEN** falta de base retorna `sem_base_suficiente` sem plano vazio; indisponibilidade retorna erro e não é apresentada como ausência de dados

#### Scenario: Não consentiu ou revogou
- **GIVEN** Aluno sem os dois aceites vigentes
- **WHEN** consulta, gera ou reenvia uma chave antiga de geração
- **THEN** recebe 403 uniforme, sem snapshots, diagnóstico, geração ou autorização presumida

#### Scenario: Consulta autorizada e geração atômica do plano
- **GIVEN** Aluno consultando ou gerando o próprio plano
- **WHEN** o sistema processa a operação com autorização vigente
- **THEN** Com aceite de uso e consentimento do plano vigentes, `GET /api/aluno/plano` SHALL retornar plano atual próprio ou `sem_plano`, sem gerar dados.
- **THEN** `POST /api/aluno/plano/gerar` SHALL aceitar somente chave UUID, atribuir usuário pela sessão e persistir plano/itens/justificativas atomicamente com 201.
- **THEN** SHALL existir no máximo um plano atual por usuário.

#### Scenario: Plano existente e replay de geração
- **GIVEN** solicitação de geração de plano
- **WHEN** o sistema verifica plano atual e chave da operação
- **THEN** Geração com plano atual existente SHALL retornar 409 orientando recálculo.
- **THEN** Replay de mesma chave/operação/dados SHALL retornar o mesmo plano com 200 somente enquanto a autorização específica permanecer válida; chave divergente SHALL retornar 409.

#### Scenario: Autorização antes de consulta e replay do plano
- **GIVEN** solicitação de consulta ou geração sem autorização vigente
- **WHEN** o servidor verifica a permissão específica
- **THEN** Sem autorização vigente, consulta e geração SHALL retornar 403 `consentimento_plano_necessario` antes de consultar plano, replay ou diagnóstico.

### Requirement: Início de prática e conclusão manual
O plano SHALL permitir prática contextual e conclusão manual de item próprio autorizado, sem alterar o desempenho.

#### Scenario: Estudar e concluir
- **GIVEN** Aluno autorizado e item próprio pendente e disponível
- **WHEN** inicia prática contextual e depois confirma conclusão do item
- **THEN** usa fluxo real de Questões e item fica concluído com data, sem modificar correções ou métricas

#### Scenario: Conteúdo retirado após geração
- **GIVEN** plano autorizado persistido e conteúdo depois arquivado
- **WHEN** consulta o plano
- **THEN** item e justificativa permanecem e iniciar prática fica indisponível, sem gerar Questões fictícias

#### Scenario: Conclusão após negativa
- **GIVEN** negativa confirmada que eliminou os planos próprios
- **WHEN** tenta concluir ou reenviar conclusão de um item anterior sem consentimento vigente
- **THEN** recebe 403 `consentimento_plano_necessario`, sem recriar o item ou alterar qualquer métrica

#### Scenario: Prática contextual e contrato de conclusão
- **GIVEN** Aluno acessando um item do próprio plano
- **WHEN** consulta disponibilidade ou solicita conclusão manual
- **THEN** Cada item de plano autorizado SHALL ligar à seleção de Questões do próprio Assunto e informar disponibilidade atual.
- **THEN** `POST /api/aluno/plano/itens/<id>/concluir` SHALL exigir os dois aceites vigentes e confirmação e permitir concluir somente item próprio do plano atual, persistindo estado/data.

#### Scenario: Replay e limites da conclusão manual
- **GIVEN** requisição de conclusão manual de item
- **WHEN** o servidor verifica replay e geração do plano e aplica seus efeitos
- **THEN** Replay SHALL manter data original enquanto autorizado; item de plano anterior SHALL retornar 409.
- **THEN** Conclusão manual SHALL NOT alterar respostas, desempenho ou afirmar domínio do Assunto.

#### Scenario: Item cujo conteúdo foi retirado
- **GIVEN** item persistido com conteúdo posteriormente retirado
- **WHEN** o plano autorizado é consultado
- **THEN** Conteúdo posteriormente retirado SHALL manter item/justificativa e indicar indisponibilidade, enquanto o plano permanecer autorizado e não for eliminado por negativa confirmada.

### Requirement: Recálculo explícito com preservação de histórico
O sistema SHALL recalcular o plano mediante confirmação explícita, preservando o histórico autorizado e a atomicidade.

#### Scenario: Recálculo confirmado
- **GIVEN** Aluno autorizado com plano com itens concluídos e diagnóstico atualizado
- **WHEN** confirma recálculo com ID atual válido
- **THEN** novo plano torna-se atual e plano anterior/conclusões permanecem preservados

#### Scenario: Concorrência ou falha
- **GIVEN** Aluno autorizado e duas solicitações com mesmo ID atual ou falha ao criar itens
- **WHEN** recálculo é executado
- **THEN** no máximo um novo plano confirma, solicitação obsoleta recebe 409 e falha não deixa plano parcial

#### Scenario: Recálculo concorrente com revogação
- **GIVEN** recálculo e revogação válida concorrentes da mesma conta
- **WHEN** as operações são serializadas
- **THEN** se o recálculo confirmar primeiro, a negativa elimina também seu novo plano; se a negativa confirmar primeiro, o recálculo recebe 403 e não cria dados posteriores à revogação

#### Scenario: Contrato e substituição atômica do plano
- **GIVEN** Aluno solicitando recálculo do próprio plano
- **WHEN** o servidor valida a requisição e prepara a nova seleção
- **THEN** `POST /api/aluno/plano/recalcular` SHALL exigir os dois aceites vigentes, chave UUID, `plano_atual_id` e `confirmar:true`.
- **THEN** SHALL gerar nova seleção antes de substituir plano atual, preservando plano/itens/conclusões anteriores atomicamente durante o uso autorizado.
- **THEN** ID atual desatualizado SHALL retornar 409.

#### Scenario: Ausência de candidatos e falha no recálculo
- **GIVEN** plano existente durante uso autorizado
- **WHEN** não há candidatos, ocorre falha ou chegam novas respostas
- **THEN** Sem candidatos SHALL retornar `sem_base_suficiente` preservando plano anterior no payload e no banco.
- **THEN** Falha SHALL NOT apagar/trocar parcialmente o plano; novas respostas SHALL NOT provocar recálculo automático.

#### Scenario: Exceção de eliminação por negativa confirmada
- **GIVEN** dono do plano no fluxo de consentimento
- **WHEN** confirma recusa ou revogação do consentimento
- **THEN** A única exceção à preservação é recusa/revogação explicitamente confirmada, que SHALL eliminar os derivados próprios e registrar a negativa atomicamente, sem alterar as respostas de origem.

### Requirement: Privacidade e fluxo mínimo acessível
O plano SHALL proteger dados próprios por autorização específica e oferecer fluxo acessível sem dados residuais.

#### Scenario: Acesso alheio
- **GIVEN** outro Aluno com autorização específica válida ou Administrador tentando concluir item de uma conta
- **WHEN** solicita operação
- **THEN** recebe respectivamente 404 ou 403 sem consultar/alterar dados do dono

#### Scenario: Falha recuperável na tela
- **GIVEN** plano visível e ação pendente
- **WHEN** rede/sessão falha e acesso é recuperado
- **THEN** a mesma identidade pode recuperar a intenção, o plano só é reexibido após confirmar permissão e a mutação exige nova ação explícita

#### Scenario: Revogação em outra aba ou troca de conta
- **GIVEN** tela com plano carregado e resposta antiga ainda pendente
- **WHEN** retorna à aba após negativa em outra aba ou a identidade muda
- **THEN** retira dados privados anteriores, revalida acesso e ignora a resposta antiga, sem reautorizar ou gerar plano automaticamente

#### Scenario: Política de acesso e erros das APIs do plano
- **GIVEN** cliente acessando consulta ou mutação do plano
- **WHEN** o servidor verifica perfil, propriedade e consentimento
- **THEN** As APIs do plano SHALL exigir Aluno, propriedade por sessão, os dois aceites vigentes, origem/CSRF nas mutações e no-store.
- **THEN** Sem consentimento SHALL produzir 403 `consentimento_plano_necessario` antes da busca de recurso ou replay; para Aluno autorizado, recurso ausente/alheio SHALL produzir o mesmo 404 e campos extras SHALL gerar 400.

#### Scenario: Apresentação autorizada e acesso à decisão de privacidade
- **GIVEN** cliente abrindo a página do plano
- **WHEN** a tela resolve permissão e apresenta o fluxo disponível
- **THEN** `/aluno/plano.html` SHALL apresentar lista, justificativas, gerar/iniciar/concluir/recalcular com teclado/foco e estados reais de loading/vazio/erro/sucesso quando autorizado; caso contrário, SHALL oferecer explicação e link para `/aluno/privacidade.html`, sem dados residuais.
- **THEN** Agenda, prazo, IA e notificações SHALL permanecer fora do recorte.

#### Scenario: Recuperação e mudança de identidade ou permissão do plano
- **GIVEN** tela do plano com intenção pendente e dados anteriores
- **WHEN** a sessão é recuperada ou a identidade ou permissão muda
- **THEN** Recuperação de sessão SHALL preservar a intenção da mesma conta sem repetição automática e exigir permissão válida antes de reexibir o plano; troca de conta ou perda de permissão SHALL impedir exposição de dados anteriores.

### Requirement: Acesso consistente ao plano na navegação do Aluno
Todas as páginas implementadas da área do Aluno SHALL oferecer na navegação principal um link identificável como `Plano de Estudos` para `/aluno/plano.html`. O plano SHALL indicar a página atual e o link SHALL ser utilizável por teclado, preservando autenticação, contexto e proteções de alterações não salvas. O destino SHALL distinguir plano/ausência de plano autorizados de necessidade de decisão de privacidade, mantendo acessíveis os demais fluxos de estudo após recusa ou revogação.

#### Scenario: Abrir o plano a partir de qualquer página do Aluno
- **GIVEN** Aluno autenticado em início, questões, resolução, histórico, simulados, execução de simulado, desempenho ou plano
- **WHEN** aciona o link `Plano de Estudos` na navegação principal
- **THEN** acessa `/aluno/plano.html` e consulta o próprio plano ou ausência de plano quando autorizado; sem autorização vê explicação e link para decidir

#### Scenario: Página atual e navegação por teclado
- **GIVEN** Aluno na página do plano
- **WHEN** percorre a navegação usando teclado
- **THEN** o link recebe foco visível, indica a página atual e não depende de apontador para ser acionado

#### Scenario: Navegação com alternativa ainda não salva
- **GIVEN** Aluno em um simulado com alternativa local ainda não salva
- **WHEN** aciona o link para o plano e cancela a confirmação de descarte
- **THEN** permanece na tentativa com a alternativa preservada, sem salvar nem finalizar automaticamente

#### Scenario: Acesso direto sem sessão
- **GIVEN** visitante sem sessão válida
- **WHEN** abre diretamente o destino do link
- **THEN** o fluxo existente exige login e nenhum dado privado de plano é exibido
