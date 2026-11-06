# Tarefas: documentar os fluxos acadêmicos

## 1. Preflight

- [x] 1.1 Conferir proposta/design, AGENTS.md, conventions e os símbolos atuais dos dois casos de uso; registrar em `validacao.md` o estado local anterior e os limites do escopo. Verificar que alterações das changes acadêmica/SOLID, `tmp/`, histórico e binários oficiais serão preservados, sem reset/stash/commit e sem ler/expor `.env`.

## 2. Fluxograma de recuperação de dados

- [x] 2.1 Criar a seção de diagnóstico em `docs/technical/fluxogramas-casos-de-uso.md`, com objetivo, perfil, tela/ação, GET, fluxograma Mermaid e rastreabilidade por links. Verificar contra `desempenho.js`, routes, proteção HTTP, Controller, composição/contratos, Service, adaptador, Repository, projeções, Models e contexto/MySQL; representar retorno à interface sem gravação fictícia de métricas.
- [x] 2.2 Renderizar e inspecionar o fluxo de diagnóstico, verificando legibilidade e decisões de acesso, período, falha e ausência de dados. Conferir 401/403, 400, 500 sem resposta parcial e 200 `sem_dados` com percentual null; documentar as notas de snapshot, limiar e renovação de sessão sem alterar a lógica para acomodar o desenho.

## 3. Fluxograma de entrada de dados

- [x] 3.1 Acrescentar a seção de finalização de Simulado ao mesmo documento, com confirmação/cancelamento, POST/corpo e fluxograma independente. Verificar o caminho real por proteção HTTP, `SimuladoController`, `FinalizarSimuladoService`, consultas/locks do `SimuladoRepository`, versão histórica de Questões, Models e `TransactionManager`, incluindo resposta à tela.
- [x] 3.2 Renderizar e inspecionar os dois fluxos finais; conferir replay antes da comparação de revisão, 404 de ausência/propriedade, 409 de revisão, tratamento de brancos, persistência pelas Models, commit antes do sucesso e rollback sem resultado parcial. Verificar que Repository não ganhou CRUD fictício e que o desenho não inventa reautenticação ou evento de auditoria na finalização; manter saídas de QA em `test-results/` ignorado.

## 4. Informação correta sobre o Plano

- [x] 4.1 Substituir apenas a frase final do aviso em `frontend/aluno/desempenho.html` pelo texto definido no design, preservando limiar, ausência de dados, IDs, estrutura, scripts e navegação. Verificar o conteúdo pelo HTML/DOM e executar `npm run test:unit -- frontend/tests/desempenho.test.js frontend/tests/navigation.test.js`; não adicionar teste que apenas espelhe a string literal nem alterar `inicio.html`, onde a limitação de agenda é válida.
- [x] 4.2 Corrigir as referências atuais a Plano indisponível em `operacao-desempenho.md` e `operacao-simulados.md`, incluindo o consumidor antes chamado de futuro, com link relativo para `operacao-plano-estudos.md`. Conferir disponibilidade do plano básico versus limites de agenda, TRI, geradores e recomendações avançadas; preservar documentos arquivados e avisos de indisponibilidade contextual legítimos.

## 5. Descoberta e verificação final

- [x] 5.1 Adicionar links para os fluxogramas no README e em `entrega-academica.md`, relacionando recuperação/entrada aos casos já implementados. Verificar todos os links, preservação da lista numerada das vinte funcionalidades e distinção entre finalização de Simulado já existente e nova documentação; não duplicar integralmente a matriz nem acrescentar material de apresentação.
- [x] 5.2 Executar `openspec-verify-change` e `openspec validate documentar-fluxos-academicos --strict`; conferir o delta de implementação/documentação limitado aos seis arquivos previstos, com diagramas renderizados, caminhos coerentes e regressão DOM registrada. Consolidar resultados reais em `validacao.md`, resolver achados críticos e registrar que integrações MySQL/cobertura completa não se aplicam a esta alteração de documentação/texto sem lógica modificada.

## Workflow follow-up

- Registrar sync não aplicável por `skip_specs: true`, preservando specs principais e contratos existentes.
- Arquivar com `openspec-archive-change` apenas após tarefas concluídas e verificação sem achados críticos; conferir links após arquivamento.
- Apresentação, roteiro, vídeo, publicação/envio do checkpoint e commit/push/merge permanecem fora desta change e não serão executados automaticamente.
