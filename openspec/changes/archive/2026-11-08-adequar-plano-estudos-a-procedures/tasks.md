# Tarefas

## 1. Preflight e caracterização

- [x] 1.1 Conferir `adequar-praticas-simulados-a-procedures` aplicada/verificada/sincronizada e prefixo 014; registrar no `validacao.md` estado inicial, alterações externas, hashes dos SQLs anteriores e inventário de métodos/consumidores. Verificar ausência de colisão da migration 015, exposição de segredos e mudança não planejada de contrato; conflito exige atualizar artefatos antes de aplicar.
- [x] 1.2 Acrescentar caracterização com fixtures MySQL sintéticas dos resultados atuais e provar mapeamento textual ORM de CALL (inclusive JOIN quando aplicável), leitura corrente e mutação/rollback na mesma sessão. Verificar tipos, identidade gerenciada, resultados vazios, fechamento/drenagem e código HTTP sem fallback; registrar comandos/resultados, sem SQLite/mocks nas integrações.

## 2. Consulta e geração autorizadas

- [x] 2.1 Iniciar `015_plano_estudos_procedures.sql` e migrar atual/replay/itens/item próprio para as routines inventariadas, mantendo entidades gerenciadas e a sequência lock de Contas → permissão → derivados. Verificar dono, 403 antes de qualquer derivado/diagnóstico, 404 alheio, geração atual, conclusão imutável e replay; documentar contratos sem duplicar o lock reservado à 016.
- [x] 2.2 Migrar pares elegíveis de Plano no Repository proprietário de Conteúdo e preservar sua API pública. Verificar lista JSON vazia/repetida, igualdade vínculo atual/snapshot, conteúdo retirado e locks compartilhados concorrendo com transferência/publicação; documentar a propriedade da routine e seu consumidor autorizado.
- [x] 2.3 Integrar geração/recalculo/consulta/conclusão com as novas leituras sem mudar ranking, Models ou diagnóstico. Verificar três prioridades, falta de base, snapshot/instante externo e falha depois de alterar a geração, com rollback real e ausência de commit interno; documentar os pontos que permanecem no Service.

## 3. Negativa e eliminação participante

- [x] 3.1 Implementar `sp_eliminar_planos_proprios` com remoção de itens antes de cada geração em ordem decrescente, sob o lock do dono, e adaptar exclusivamente o Repository/participante existente. Verificar múltiplas gerações com FK RESTRICT, contagens, outra conta preservada, ausência de endpoint novo e nenhuma modificação de evidência/resposta; documentar a escrita especializada e sua única transação externa.
- [x] 3.2 Acrescentar regressões MySQL de falha real após exclusão de itens e de revogação concorrente com recálculo/conclusão. Verificar rollback conjunto de negativa/derivados, sincronização das entidades afetadas e replay antigo após nova autorização sem apagar plano novo; documentar a evidência e preservar os guards ORM e hashes legais.

## 4. Instalação e integração documental

- [x] 4.1 Concluir `015_plano_estudos_procedures.sql` e bootstrap equivalente e integrar reconhecimento/preflight até 015, com assinaturas/corpos/segurança oficiais. Verificar instalação vazia, upgrade 014 → 015 com dados, baseline/restauração, recursos ausentes/alterados, idempotência e preservação de prefixos/checksums anteriores; documentar pré-condições, privilégios e compensação.
- [x] 4.2 Atualizar README, documento SQL técnico e matrizes acadêmica/CRUD com o recorte real e caminhos ponta a ponta. Verificar links, correspondência método/procedure/Controller/Service/tela, vinte funcionalidades sem renumeração e pendências das próximas etapas sem promessa de aprovação acadêmica.

## 5. Verificação integrada

- [x] 5.1 Executar regressões afetadas (`test_planos_integration.py`, `test_privacidade_integration.py`, migrations correspondentes e `test_desempenho_integration.py`.), as 29 integrações originais e suíte ampliada MySQL, gates de arquitetura, cobertura existente e E2E conforme conventions. Verificar contratos/metadata/guards/rollback e registrar comandos e resultados reais em `validacao.md`; não reduzir gates, substituir banco por mocks ou declarar sucesso se MySQL estiver indisponível.
- [x] 5.2 Executar `openspec validate adequar-plano-estudos-a-procedures --strict`, `git diff --check` e revisão de escopo/segredos/hashes. Verificar preservação de alterações externas, migrations antigas, procedure legada, visuais e dados, sem DDL no banco de uso por efeito colateral.

## Continuidade do workflow

- Verificar a implementação, sincronizar os dois deltas e arquivar somente sem tarefas pendentes ou achados críticos.
- Aplicar a próxima etapa apenas depois da dependência concluída; não executar as changes em paralelo.
- Commit, push, AWS, uso real e envio ao Classroom dependem de instrução própria.
