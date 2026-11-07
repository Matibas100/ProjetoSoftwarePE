# Proposta: centralizar helpers de paginação

## Why

Questões, Práticas e Simulados importam `_inteiro_filtro` e `_envelope` de um Service de listagem administrativa do catálogo. Essas duas funções são utilitários compartilhados, e sua localização cria dependência entre casos de uso sem relação com suas regras de domínio.

## What Changes

- Criar somente `backend/app/services/paginacao.py`, com as funções públicas `inteiro_filtro` e `envelope_paginado`, extraídas das funções existentes sem alterar semântica.
- Atualizar o catálogo e os sete módulos consumidores para importar diretamente desse módulo neutro. Remover as duas definições privadas antigas, sem duplicação ou wrappers de compatibilidade desnecessários.
- Acrescentar testes comportamentais de limites/conversões/envelope e uma explicação curta na convenção de arquitetura sobre utilitários de paginação e Services de casos de uso.
- Preservar diferenças de validação entre recursos, filtros específicos, defaults, mensagens, chaves/valores dos envelopes e contratos HTTP existentes.

### Fora de escopo

Mover `corpo`, UUID, confirmação, `inicio` ou validações de domínio; unificar políticas de paginação; corrigir entradas antes aceitas; mudar SQL, Repository, Controller, composição, Models, transações ou schema. Não criar classe genérica, pacote utilitário amplo, nova dependência ou funcionalidade. Frontend, legibilidade, JSON inválido, README, AWS e commit/push/merge ficam fora desta change.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. A extração mantém os comportamentos de catálogo, Questões, Práticas e Simulados. `skip_specs: true` por refatoração interna sem delta funcional; testes novos caracterizam contratos já existentes.

## Impact

- Produção: novo `services/paginacao.py`; `listar_catalogo_admin_service.py`, `gestao_questao_service.py`, `gestao_simulado_service.py`, `listar_historico_simulados_service.py`, `listar_praticas_service.py`, `listar_questoes_aluno_service.py`, `listar_simulados_aluno_service.py` e `pratica_validacao.py`.
- Testes: novo `backend/tests/unit/test_paginacao.py`, sem enfraquecer os testes existentes. Documentação: somente `docs/conventions/arquitetura-da-aplicacao.md`.
- A API pública das classes de Service permanece. A remoção diz respeito aos nomes privados internos inventariados, cujos consumidores do repositório serão migrados; não há alteração de payload, rota, persistência ou regra de negócio.
- Validar equivalência das funções extraídas, consumidores, filtros estritos versus permissivos existentes, unitários/cobertura backend com MySQL real e dois E2E preservados. CRUD permanece nas Models, SQL especializado nos Repositories e cada caso de uso em seu Service.
- Ordem operacional: aplicar após conclusão/verificação da legibilidade e da correção de JSON, sem implementação paralela. Preservar os deltas anteriores, incluindo migrations locais; capturar baseline no início de seu próprio apply, não neste planejamento concorrente.
