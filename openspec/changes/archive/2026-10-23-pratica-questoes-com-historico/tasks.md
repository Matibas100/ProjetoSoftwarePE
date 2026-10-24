# Tarefas — 3. Prática e histórico

## 1. Dependência e dados

- [x] 1.1 Confirmar `gestao-basica-questoes` aplicada/verificada/sincronizada/arquivada, localizar seus artefatos pelo nome inclusive no arquivo e reler contratos finais, conventions/ADRs e referências ALU-QUE-001/002/003. Validar alinhamento com esta change antes de escrever código; atualizar artefatos se necessário.
- [x] 1.2 Criar migration consecutiva, snapshot e Model de tentativas conforme design, sem histórico fictício. Testar instalação limpa/upgrade, reexecução, estado/checks, chave única e FKs `RESTRICT` em MySQL real.
- [x] 1.3 Documentar schema, backup/compensação, chave de início e privacidade em `docs/technical/operacao-praticas.md`; validar correspondência com migration e dados de origem sem conteúdo sensível.

## 2. Selecionar e iniciar Questão

- [x] 2.1 Implementar seleção segura e filtros via Service de conteúdo do item 2, Controller e rotas; testar DTO sem gabarito/explicação, catálogo indisponível, paginação, 400/401/403 com testes unitários e integração real.
- [x] 2.2 Implementar início idempotente, snapshot de classificação e GET de tentativa própria; validar 201/replay 200/chave divergente 409, versão superada e concorrência da chave no MySQL; documentar contratos de início/detalhe.
- [x] 2.3 Evoluir autorização explícita de `/api/aluno/*` em `auth_http.py`, sem liberar consultas legadas; testar perfil Administrador 403, anônimo 401, dono, ID alheio 404 uniforme, HEAD e CSRF/Origin com regressão de autenticação.

## 3. Responder e consultar histórico

- [x] 3.1 Implementar correção em Service próprio com lock e transação, permitindo concluir versão retirada após início. Testar A–E, entrada extra, acerto/erro, explicação nula, replay igual, alteração posterior 409 e rollback/conflito concorrente no MySQL real.
- [x] 3.2 Implementar histórico paginado/filtro/detalhe corrigido e contrato de fatos para desempenho; testar conta A/B, recarga e estabilidade após nova publicação/transferência/arquivamento, mantendo tentativas em andamento fora do histórico respondido.
- [x] 3.3 Documentar resposta definitiva, classificação histórica e fronteira de leitura do item 5 no documento operacional; validar exemplos contra testes e ausência de correção calculada no frontend.

## 4. Fluxo do Aluno

- [x] 4.1 Implementar seleção, execução/correção e histórico nas URLs do design e link no início; testar filtros, início, resposta, resultado e retomada por DOM, e conferir referência visual em 1440 px/teclado sem alterar arquivos oficiais.
- [x] 4.2 Integrar sessão e recuperação contextual, estados e preservação de alternativa; validar rede/expiração/troca de identidade sem replay automático, storage sensível ou gabarito antecipado em payload/HTML/DOM; documentar navegação e recorte individual.

## 5. Validação integrada e fechamento

- [x] 5.1 Executar runners unitários, cobertura backend/frontend e regressões com MySQL real e opt-in apenas no processo, cobrindo 29 cenários originais mais auth/catálogo/Questões versionadas; registrar resultados/limitações e confirmar limiares sem expor `.env`/credenciais.
- [x] 5.2 Demonstrar resposta -> logout/login -> mesmo histórico e isolamento de outra conta; validar esta change com `openspec validate pratica-questoes-com-historico --strict`, usar verify, sincronizar e arquivar somente após tarefas/achados resolvidos, sem commit/push automático.
