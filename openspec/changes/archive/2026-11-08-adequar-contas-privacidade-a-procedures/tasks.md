# Tarefas

## 1. Preflight e caracterização

- [x] 1.1 Conferir `adequar-plano-estudos-a-procedures` aplicada/verificada/sincronizada e prefixo 015; registrar no `validacao.md` estado inicial, alterações externas, hashes dos SQLs anteriores e inventário de métodos/consumidores. Verificar ausência de colisão da migration 016, exposição de segredos e mudança não planejada de contrato; conflito exige atualizar artefatos antes de aplicar.
- [x] 1.2 Acrescentar caracterização com fixtures MySQL sintéticas dos resultados atuais e provar mapeamento textual ORM de CALL (inclusive JOIN quando aplicável), leitura corrente e mutação/rollback na mesma sessão. Verificar tipos, identidade gerenciada, resultados vazios, fechamento/drenagem e código HTTP sem fallback; registrar comandos/resultados, sem SQLite/mocks nas integrações.

## 2. Identidade e sessões

- [x] 2.1 Iniciar `016_contas_privacidade_procedures.sql` e migrar busca por e-mail, consulta de sessão/Usuário associado e usuário ativo bloqueado. Verificar comparação de e-mail/collation, normalização no Service, LEFT JOIN anônimo, conta inativa, populate_existing e ausência de senha/hash/identificador em saída/log; documentar contratos internos e delegação da Model sem novo CRUD Repository.
- [x] 2.2 Migrar renovação, revogação individual e por usuário, sincronizando somente os atributos afetados de entidades carregadas. Verificar limites exatos de 8h/30min, correspondência válida com timestamp inalterado, revogação concorrente, sessões independentes, rollback e contagens próprias sem rowcount do CALL; documentar os mesmos predicados e controles de origem/CSRF.

## 3. Limites e limpeza operacional

- [x] 3.1 Migrar preparação/upsert bloqueante da chave do limite para a routine prevista, mantendo cálculo/reset/bloqueio no Service e atualizações básicas na Model. Verificar primeira tentativa concorrente, cinco falhas/15min, senha correta durante bloqueio, chaves independentes de login/reautenticação e rollback sem confirmação antecipada; documentar a operação auxiliar sem criar endpoint.
- [x] 3.2 Migrar limpeza de sessões/limites para a routine participante com contagens explícitas. Verificar cada corte temporal e sua igualdade, sessões válidas, dados de outra conta, evidências preservadas e falha entre os DELETEs com rollback total; documentar CLI/privilégios atuais e ausência de remoção de contas ou mudança de retenção.

## 4. Privacidade corrente e fechamento da cobertura

- [x] 4.1 Migrar lock exato de identidade, últimas decisões por tipo e replay por chave para as routines previstas. Últimas decisões usam duas capturas completas sequenciais FOR UPDATE e um único conjunto ORM ordenado uso/plano, omitindo tipos ausentes. Verificar tipos, vazios parciais/completos, identidade gerenciada, leituras correntes após snapshot anterior, ordem uso/plano, identidade sem filtro de ativo, revisões/chaves concorrentes e rollback da negativa com participante da 015; documentar integração mantendo composição/Models append-only/versões legais.
- [x] 4.2 Auditar executores especializados dos seis módulos contra inventários das cinco etapas, distinguindo CRUD básico, construção de projeção e consulta efetivamente executada. Verificar cada filtro/JOIN/ordenação/operação especializada restante por fonte e consumidor real, registrar cobertura e achados em `validacao.md` e na matriz técnica, sem esconder lacuna com contagem de procedures nem ampliar produto silenciosamente.

## 5. Instalação e integração documental

- [x] 5.1 Concluir `016_contas_privacidade_procedures.sql` e bootstrap equivalente e integrar reconhecimento/preflight até 016, com assinaturas/corpos/segurança oficiais. Verificar instalação vazia, upgrade 015 → 016 com dados, baseline/restauração, recursos ausentes/alterados, idempotência e preservação de prefixos/checksums anteriores; documentar pré-condições, privilégios e compensação.
- [x] 5.2 Atualizar README, documento SQL técnico e matrizes acadêmica/CRUD com o recorte real e caminhos ponta a ponta. Verificar links, correspondência método/procedure/Controller/Service/tela, vinte funcionalidades sem renumeração e pendências das próximas etapas sem promessa de aprovação acadêmica.

## 6. Verificação integrada

- [x] 6.1 Executar regressões afetadas (`test_autenticacao_integration.py`, `test_privacidade_integration.py`, `test_planos_integration.py`, regressões completas e E2E de sessão/privacidade.), as 29 integrações originais e suíte ampliada MySQL, gates de arquitetura, cobertura existente e E2E conforme conventions. Verificar contratos/metadata/guards/rollback e registrar comandos e resultados reais em `validacao.md`; não reduzir gates, substituir banco por mocks ou declarar sucesso se MySQL estiver indisponível.
- [x] 6.2 Executar `openspec validate adequar-contas-privacidade-a-procedures --strict`, `git diff --check` e revisão de escopo/segredos/hashes. Verificar preservação de alterações externas, migrations antigas, procedure legada, visuais e dados, sem DDL no banco de uso por efeito colateral.

## Continuidade do workflow

- Verificar a implementação, sincronizar os dois deltas e arquivar somente sem tarefas pendentes ou achados críticos.
- Aplicar a próxima etapa apenas depois da dependência concluída; não executar as changes em paralelo.
- Commit, push, AWS, uso real e envio ao Classroom dependem de instrução própria.
