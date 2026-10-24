# Delta — Gestão administrativa de Simulados

## ADDED Requirements

### Requirement: Gestão mínima utilizável de Simulados fixos
As telas administrativas de Simulados SHALL usar referências ADM-SIM-001/002 para listar, cadastrar composição manual ordenada, editar rascunho, revisar/publicar e arquivar, com dados reais e APIs protegidas. SHALL preservar campos, seleção, revisão e filtros diante de erro/sessão expirada, proteger alterações não salvas e exigir confirmação/reautenticação contextual em publicação/arquivamento. SHALL permitir teclado/foco e mostrar vazio, carregamento, falha e sucesso. Geradores, importação, calendário, TRI e recursos fora do recorte SHALL permanecer indisponíveis.

#### Scenario: Publicação de composição real
- **GIVEN** Administrador com rascunho válido
- **WHEN** revisa e confirma publicação pela tela
- **THEN** versão e composição retornadas pelo servidor são refletidas e a edição de publicado fica indisponível

#### Scenario: Falha e proteção da seleção
- **GIVEN** rascunho com Questões selecionadas e ainda não salvo
- **WHEN** falha gravação, expira sessão ou tenta sair
- **THEN** seleção é preservada, descarte exige confirmação e recuperação não repete mutação automaticamente
