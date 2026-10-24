# Delta — Gestão administrativa de Questões

## ADDED Requirements

### Requirement: Gestão mínima utilizável de Questões
As telas `/admin/questoes.html` e `/admin/questao.html` SHALL oferecer listagem, filtros, paginação, cadastro, edição de rascunho, revisão/publicação explícita e arquivamento com confirmação, usando referências ADM-QUE-001/002, moldura e ativos oficiais. SHALL verificar perfil antes de consultar dados e preservar formulário/filtros em falha de negócio, rede ou sessão. Recuperação/reautenticação SHALL ocorrer no contexto, sem repetição automática da mutação; troca de conta SHALL bloquear contexto antigo até descarte/recarga. SHALL proteger alterações não salvas, manter labels, foco e teclado e diferenciar carregamento, vazio, filtros sem resultado, erro e sucesso. Funções fora do recorte SHALL permanecer indisponíveis sem ação fictícia.

#### Scenario: Gerir Questão real
- **GIVEN** Administrador e catálogo ativo
- **WHEN** cadastra, edita, revisa/publica ou arquiva uma Questão
- **THEN** a tela chama APIs reais, reflete o estado confirmado e preserva contexto da listagem

#### Scenario: Falha ou saída durante edição
- **GIVEN** formulário alterado e ainda não salvo
- **WHEN** ocorre erro, sessão expirada ou tentativa de navegar/sair
- **THEN** dados são preservados, recuperação não repete escrita e descarte exige confirmação explícita

#### Scenario: Operação acessível e escopo limitado
- **GIVEN** usuário operando por teclado
- **WHEN** percorre filtros, formulário e confirmação de publicação/arquivamento
- **THEN** foco e consequências são compreensíveis e não há importação, IA ou upload funcional fora deste recorte
