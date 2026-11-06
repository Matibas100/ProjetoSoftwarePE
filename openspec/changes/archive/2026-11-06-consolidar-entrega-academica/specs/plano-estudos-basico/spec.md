# Plano de estudos básico: navegação consistente

## ADDED Requirements

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
