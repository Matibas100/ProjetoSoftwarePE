# ADR-009 — Consentimento e eliminação do plano

**Aceito**, pela aplicação da change `adicionar-termos-e-consentimento`,
iniciada em 06/11/2026. Complementa ADRs 001, 002, 006 e 008.

O plano personalizado é opcional e depende de duas aceitações vigentes: uso e
finalidade específica do plano. Cadastro grava somente uso junto à conta, sem
commit intermediário ou backfill para contas anteriores. Evidências são
append-only com versão, hash, UTC e vínculo à sessão.

Os quatro Services do plano, consulta de privacidade e decisões usam a mesma
fronteira curta com lock do usuário. Decisões/chaves usam leitura corrente,
independente do snapshot anterior de autenticação. Validar permissão precede
replay, snapshot, item e diagnóstico; falha fecha acesso. UUID e revisão por
tipo impedem que resposta antiga reative ou elimine dados novamente.

A minimização aprovada cria uma exceção explícita à preservação de gerações:
recusa ou revogação confirmada elimina todos os planos/itens/conclusões próprios,
atomicamente com a negativa. `PrivacidadeRepository.eliminar_planos_proprios`
usa persistência especializada, predicados de usuário/plano, itens antes de
gerações e ordem decrescente para respeitar FK RESTRICT. Não desativa FKs nem
relaxa eventos/métodos normais das Models. Respostas, simulados, outra conta e
evidências não são eliminados. Rollback de falha real é testado.

Rejeitados consentimento presumido, registro sem enforcement, eliminação
genérica pelo ORM e apagar respostas como consequência de revogar o plano.
A aplicação não recupera derivados eliminados. Nova autorização inicia outro
histórico de plano, preservando as respostas. Retenção geral, contato real e
proteção de menores exigem decisões próprias antes de dados reais.

Evidências: [integrações de privacidade](../../../backend/tests/test_privacidade_integration.py),
[migrations](../../../backend/tests/test_privacidade_migration_integration.py) e
[operação](../operacao-privacidade.md).
