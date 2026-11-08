# Proposta — Plano de Estudos por procedures

## Why

Plano atual, itens, replay e disponibilidade ainda usam leituras especializadas ORM, e a eliminação por negativa usa DML especializado direto. A troca deve manter o consentimento antes de qualquer leitura e uma única transação para decisões e derivados. O objetivo é cumprir a exigência de acesso além do CRUD por procedures encapsuladas no Repository, mantendo o sistema demonstrável e compreensível.

## What Changes

- Converter o recorte fechado: Plano atual, consulta por chave, itens ordenados, item próprio, pares elegíveis de Conteúdo e eliminação especializada de gerações próprias por negativa confirmada.
- Criar 6 procedures específicas, descritas em [inventário](inventario-procedures.md), com SQL estático e parâmetros vinculados; CALL permanece exclusivamente nos Repositories.
- Acrescentar `015_plano_estudos_procedures.sql`, bootstrap equivalente, reconhecimento conservador do prefixo 015, preflight e testes MySQL reais.
- Preservar DTOs públicos, respostas HTTP, permissões, semântica temporal, locks e uma única transação externa; os métodos que alimentam escrita continuam retornando entidades ORM gerenciadas no proprietário.
- Atualizar documentação de procedures, rotas, Modules/Models/Repositories e cobertura da exigência. Não acrescentar funcionalidades à lista oficial por contar métodos SQL.

### Fora de escopo

Algoritmo/fórmula de prioridade, CRUD de plano/itens nas Models, mudanças legais/etárias, endpoint manual de exclusão e conversão do lock de identidade de Contas (reservada à 016). Sem novas telas, regras de produto, tabelas/colunas/FKs, bibliotecas, uso real de dados pessoais, gravação de vídeo, AWS ou operações Git.

## Capabilities

### New Capabilities

- `plano-estudos-mysql`: interfaces MySQL específicas do domínio para o recorte inventariado, com compatibilidade, autorização e participação transacional verificáveis.

### Modified Capabilities

- `migrations-sql`: acrescentar comprovação do prefixo 015 e seus objetos SQL, sem enfraquecer os prefixos anteriores.

As specs funcionais existentes continuam válidas. Os novos requisitos descrevem a interface SQL externa e garantias de compatibilidade, sem reabrir decisões de negócio.

## Impact

- **Dependência obrigatória:** aplicar, verificar e sincronizar `adequar-praticas-simulados-a-procedures` antes desta change. A sequência planejada é primeira etapa 011/012 → Catálogo 013 → Práticas/Simulados 014 → Plano 015 → Contas 016. Não aplicar essas changes simultaneamente; conferir eventual colisão de versão antes de editar.
- **Superfícies:** `plano_estudos/repositories/plano_estudo_repository.py`, participante de eliminação, Services de consulta/geração/recálculo/conclusão, `conteudo/repositories/questao_repository.py` e API pública de elegibilidade. Caminhos relativos a `backend/app/modules/`.
- **Entradas mantidas:** `/api/aluno/plano`, `/gerar`, `/recalcular`, `/itens/<id>/concluir` e participação interna nas negativas existentes de consentimento. Telas e Controllers atuais atendem às mesmas funcionalidades; não criar Controller por procedure auxiliar.
- **Invariantes:** Lock de usuário e aceites vigentes antes de replay/item/diagnóstico; mesma conexão/relógio; três prioridades determinísticas; gerações preservadas enquanto autorizadas; negativa atômica elimina somente derivados próprios.
- **Banco:** somente novas routines sobre as 21 Models existentes, sem DML funcional durante instalação/baseline. Procedures especializadas de escrita só executam no caso de uso autorizado, nunca pela migration.
- **ADRs:** preservar 001/002/003/004/005/006/008/009/010 conforme o domínio, complementando o ADR-011 e as interfaces SQL introduzidas pela primeira etapa sem alterar decisões históricas.
- **Testes:** `test_planos_integration.py`, `test_privacidade_integration.py`, migrations correspondentes e `test_desempenho_integration.py`. Preservar também as 29 integrações originais, gates de arquitetura, cobertura e E2E. Mocks somente em unitários.
- **Compatibilidade:** SQLs/checksums anteriores a 015, procedure legada, dados e artefatos oficiais permanecem. Nenhuma autorização para commit, push, DDL no banco de uso ou deploy é inferida deste planejamento.
