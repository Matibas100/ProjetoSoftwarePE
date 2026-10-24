# Tarefas — 4. Simulado fixo

## 1. Dependências e schema

- [x] 1.1 Confirmar itens 2/3 encerrados, localizar artefatos finais pelo nome mesmo arquivados e reler versões/autorizações, conventions/ADRs e referências ADM-SIM-001/002 e ALU-SIM-001/002/003/004. Validar alinhamento antes do apply e reconciliar divergências no planejamento.
- [x] 1.2 Criar migration consecutiva, snapshot e Models de simulado/rascunho/versão/itens/eventos/tentativas/respostas conforme design. Validar zero/upgrade/reexecução, FKs, constraints de posição/Questão, chave de início e uma tentativa em andamento com MySQL real.
- [x] 1.3 Documentar persistência, composição imutável, ausência de prazo, backup/reversão e denominador do resultado em `docs/technical/operacao-simulados.md`; validar contra schema e specs.

## 2. Compor e disponibilizar

- [x] 2.1 Implementar Services/Controller/rotas administrativas de lista/cadastro/detalhe/edição de rascunho; testar título, limite 1–180, ordem, repetição por identidade, versão inelegível, revisão e paginação com unitários e integração MySQL.
- [x] 2.2 Implementar revisão/publicação e arquivamento auditados/transacionais com permissão, reautenticação/CSRF/Origin; testar snapshot, replay, 401/403/409, ausência de edição do publicado e rollback da última etapa; documentar contratos administrativos.

## 3. Realizar e finalizar

- [x] 3.1 Implementar catálogo seguro e início/retomada própria com chave UUID e limite de uma tentativa em andamento; testar concorrência, replay, conteúdo superado/retirado e tentativa antiga ainda concluível no MySQL real.
- [x] 3.2 Implementar persistência de respostas por item/revisão, sem feedback antecipado; testar alterar/limpar/recarga, ID de outra conta, revisão obsoleta e dados extras com testes unitários e integração; documentar DTOs seguros.
- [x] 3.3 Implementar finalização atômica, resultado e correção/histórico próprios; testar branco/acerto/erro/fórmula, replay, salvar versus finalizar concorrente, rollback e imutabilidade após publicação/transferência/arquivamento no MySQL real.
- [x] 3.4 Expor contrato de fatos respondidos de simulados finalizados ao desempenho sem criar práticas; testar exclusão de branco/em andamento e isolamento por dono, documentando origem, instante de finalização e classificação histórica.

## 4. Telas e recuperação

- [x] 4.1 Implementar gestão manual de Simulados e telas de seleção/execução/resultado/correção nas URLs do design; testar APIs reais e fluxo completo por DOM e inspeção visual em 1440 px/teclado conforme referências, sem recursos futuros ativos.
- [x] 4.2 Integrar revisão/confirmar finalização com quantidade em branco, progresso salvo, proteção de edição, recuperação/reautenticação no contexto e troca de conta; testar falhas preservando respostas sem replay automático e documentar navegação.

## 5. Validação integrada e fechamento

- [x] 5.1 Executar runners unitários e cobertura backend/frontend, opt-in MySQL apenas no processo e integrações reais; validar 29 cenários originais e regressões auth/catálogo/Questões/práticas, limiares e ausência de segredos, registrando resultados e limitações.
- [x] 5.2 Demonstrar criação/publicação -> início/respostas -> finalização -> recarga do mesmo resultado; executar `openspec validate simulado-fixo-com-resultado --strict`, verify, sync e archive somente com tarefas concluídas e sem achado crítico; sem commit/push automático.
