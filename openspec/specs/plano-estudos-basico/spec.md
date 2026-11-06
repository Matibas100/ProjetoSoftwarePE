# Plano de estudos básico

## Purpose

Gerar um plano persistido de Assuntos prioritários a partir do desempenho próprio do Aluno, com seleção explicável e recálculo explícito.

## Requirements

### Requirement: Priorização determinística baseada em desempenho
O plano SHALL usar diagnóstico dos últimos 30 dias UTC, selecionar até três Assuntos com pelo menos cinco respostas, catálogo ativo, vínculo Assunto–Matéria atual igual ao grupo histórico e Questões publicadas elegíveis. SHALL ordenar por menor taxa exata de acerto, maior total de respostas e menor ID do Assunto, sem arredondar antes de comparar. SHALL explicar prioridade relativa com acertos, total, percentual, período e amostra. SHALL NOT preencher vagas com amostra insuficiente ou inventar dificuldade quando acerto for 100%.

#### Scenario: Ordenação e desempate
- **GIVEN** Assuntos elegíveis com 2/10, 1/5 e 4/10 acertos
- **WHEN** Aluno gera plano
- **THEN** ordem é 2/10, 1/5 e 4/10, com justificativas correspondentes e no máximo três itens

#### Scenario: Assunto transferido ou sem conteúdo
- **GIVEN** grupo histórico transferido para outra Matéria ou sem Questão atualmente elegível
- **WHEN** gera/recalcula plano
- **THEN** grupo é excluído sem reclassificar fatos e sem recomendar conteúdo indisponível

### Requirement: Geração persistida exclusiva do dono
`GET /api/aluno/plano` SHALL retornar plano atual próprio ou `sem_plano`, sem gerar dados. `POST /api/aluno/plano/gerar` SHALL aceitar somente chave UUID, atribuir usuário pela sessão e persistir plano/itens/justificativas atomicamente com 201. SHALL existir no máximo um plano atual por usuário. Geração com plano atual existente SHALL retornar 409 orientando recálculo. Replay de mesma chave/operação/dados SHALL retornar o mesmo plano com 200; chave divergente SHALL retornar 409.

#### Scenario: Gerar, reenviar e recarregar
- **GIVEN** Aluno sem plano e diagnóstico suficiente
- **WHEN** gera com chave válida, reenvia e recarrega
- **THEN** existe um único plano e ele mantém itens, ordem e justificativas originais

#### Scenario: Falta de base ou falha de diagnóstico
- **GIVEN** Aluno sem candidatos suficientes ou serviço de diagnóstico indisponível
- **WHEN** solicita geração
- **THEN** falta de base retorna `sem_base_suficiente` sem plano vazio; indisponibilidade retorna erro e não é apresentada como ausência de dados

### Requirement: Início de prática e conclusão manual
Cada item SHALL ligar à seleção de Questões do próprio Assunto e informar disponibilidade atual. `POST /api/aluno/plano/itens/<id>/concluir` SHALL exigir confirmação e permitir concluir somente item próprio do plano atual, persistindo estado/data. Replay SHALL manter data original; item de plano anterior SHALL retornar 409. Conclusão manual SHALL NOT alterar respostas, desempenho ou afirmar domínio do Assunto. Conteúdo posteriormente retirado SHALL manter item/justificativa e indicar indisponibilidade.

#### Scenario: Estudar e concluir
- **GIVEN** item próprio pendente e disponível
- **WHEN** inicia prática contextual e depois confirma conclusão do item
- **THEN** usa fluxo real de Questões e item fica concluído com data, sem modificar correções ou métricas

#### Scenario: Conteúdo retirado após geração
- **GIVEN** plano persistido e conteúdo depois arquivado
- **WHEN** consulta o plano
- **THEN** item e justificativa permanecem e iniciar prática fica indisponível, sem gerar Questões fictícias

### Requirement: Recálculo explícito com preservação de histórico
`POST /api/aluno/plano/recalcular` SHALL exigir chave UUID, `plano_atual_id` e `confirmar:true`. SHALL gerar nova seleção antes de substituir plano atual, preservando plano/itens/conclusões anteriores atomicamente. ID atual desatualizado SHALL retornar 409. Sem candidatos SHALL retornar `sem_base_suficiente` preservando plano anterior no payload e no banco. Falha SHALL NOT apagar/trocar parcialmente o plano; novas respostas SHALL NOT provocar recálculo automático.

#### Scenario: Recálculo confirmado
- **GIVEN** plano com itens concluídos e diagnóstico atualizado
- **WHEN** confirma recálculo com ID atual válido
- **THEN** novo plano torna-se atual e plano anterior/conclusões permanecem preservados

#### Scenario: Concorrência ou falha
- **GIVEN** duas solicitações com mesmo ID atual ou falha ao criar itens
- **WHEN** recálculo é executado
- **THEN** no máximo um novo plano confirma, solicitação obsoleta recebe 409 e falha não deixa plano parcial

### Requirement: Privacidade e fluxo mínimo acessível
As APIs do plano SHALL exigir Aluno, propriedade por sessão, origem/CSRF nas mutações e no-store; recurso ausente/alheio SHALL produzir o mesmo 404 e campos extras SHALL gerar 400. `/aluno/plano.html` SHALL apresentar lista, justificativas, gerar/iniciar/concluir/recalcular com teclado/foco e estados reais de loading/vazio/erro/sucesso. Recuperação de sessão SHALL preservar contexto da mesma conta sem repetição automática; troca de conta SHALL impedir exposição do plano anterior. Agenda, prazo, IA e notificações SHALL permanecer fora do recorte.

#### Scenario: Acesso alheio
- **GIVEN** outro Aluno ou Administrador tentando concluir item de uma conta
- **WHEN** solicita operação
- **THEN** recebe respectivamente 404 ou 403 sem consultar/alterar dados do dono

#### Scenario: Falha recuperável na tela
- **GIVEN** plano visível e ação pendente
- **WHEN** rede/sessão falha e acesso é recuperado
- **THEN** plano continua visível para a mesma identidade e a mutação exige nova ação explícita

### Requirement: Acesso consistente ao plano na navegação do Aluno
Todas as páginas implementadas da área do Aluno SHALL oferecer na navegação principal um link identificável como `Plano de Estudos` para `/aluno/plano.html`. O plano SHALL indicar a página atual e o link SHALL ser utilizável por teclado, preservando autenticação, contexto e proteções de alterações não salvas.

#### Scenario: Abrir o plano a partir de qualquer página do Aluno
- **GIVEN** Aluno autenticado em início, questões, resolução, histórico, simulados, execução de simulado, desempenho ou plano
- **WHEN** aciona o link `Plano de Estudos` na navegação principal
- **THEN** acessa `/aluno/plano.html` e consulta o próprio plano ou o estado real de ausência de plano

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
