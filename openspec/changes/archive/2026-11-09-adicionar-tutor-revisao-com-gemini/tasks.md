# Tasks

Executar conforme [design](design.md) e [delta do Tutor](specs/tutoria-revisao-ia/spec.md). Este arquivo planeja implementação; nenhum item está concluído pela criação da proposta. Não configurar chave nem habilitar chamadas reais sem ambiente local preparado pelo responsável.

## 1. Publicar termos e preservar decisões

- [x] 1.1 Criar `frontend/legal/termo-de-uso-v2.html`, registrar seu hash e tornar uso 2.0 vigente em Contas, descrevendo envio opcional ao Gemini e limites reais; verificar GET/HEAD público, leitura sem JavaScript e hashes/bytes inalterados de uso 1.0 e consentimento do plano 1.0.
- [x] 1.2 Ajustar testes de cadastro, privacidade e plano para uso 2.0 e acrescentar regressões de evidência antiga, novo aceite sem decisão fabricada, plano preservado e recusa/revogação independentes; verificar unitários e integrações afetadas com MySQL real, sem mocks ou SQLite.
- [x] 1.3 Atualizar links vigentes e `docs/technical/operacao-privacidade.md`, documentando efeito do novo uso no plano e a independência da tutoria; verificar links existentes, consulta de documentos antigos e ausência de promessa de retenção zero ou autorização real de menores.

## 2. Preparar módulo, permissão e contrato HTTP

- [x] 2.1 Acrescentar módulo `tutor_ia`, contrato pequeno, composição por aplicação e configuração opcional desabilitada por padrão; atualizar gate modular, mapa/conventions e adendo ao ADR-010. Verificar sete proprietários, 21 mappers, factories independentes, imports públicos e ausência de chamadas externas na inicialização.
- [x] 2.2 Implementar/exportar `ValidarPermissaoTutoriaService` em Contas, exigindo somente uso vigente e encerrando a leitura antes da integração; verificar com MySQL real conta sem aceite, aceite antigo, uso 2.0 aceito com plano recusado e ausência de conexão/transação retida ao devolver permissão.
- [x] 2.3 Implementar `GerarTutoriaService`, Controller em classe, Blueprint `POST /api/tutoria`, validações e limite local de 16 KiB; adaptar autorização exata e `no-store` em Contas. Verificar contrato com unitários e HTTP/MySQL real para 400/401/403/409/413/503, precedência de autorização, rota parecida sem permissão indevida e rotas administrativas preservadas; não usar provedor falso nas integrações.
- [x] 2.4 Documentar contrato, quatro campos, códigos e fluxo Controller/Services no README; verificar exemplos sintéticos contra os testes e registrar que a consulta externa não cria Model/Repository ou novo CRUD.

## 3. Integrar Gemini e limitar consumo

- [x] 3.1 Implementar `GeminiService` com `requests` fixado, endpoint HTTPS, cabeçalho protegido, `store=false`, prompt pedagógico, limite de saída, timeouts 5/30 s e leitura máxima de 1 MiB; verificar em unitários payload mínimo, ausência de identidade/histórico, extração REST de `steps`, quatro títulos, fechamento de resposta, erros sanitizados e nenhuma repetição automática.
- [x] 3.2 Implementar limitador local por aplicação conforme design: quatro tentativas/60 s, uma em andamento por conta, duas globais e capacidade de 1024 contas; verificar em unitários concorrentes janela, expiração, saturação, `Retry-After`, falhas que contam e liberação em `finally`, sem retenção de dúvidas/respostas.
- [x] 3.3 Acrescentar placeholders e instruções de ativação em `.env.example` e README, sem abrir/alterar `.env`; verificar funcionamento sem chave, não encaminhamento de chaves aos runners comuns e ausência de segredo em ativos, logs e mensagens. Documentar limitação por processo e possível consumo mesmo após cancelamento local.

## 4. Entregar tela e navegação do Tutor

- [x] 4.1 Criar `frontend/aluno/tutor.html` e CSS/JS próprios, seguindo `ALU-TUT-001` do protótipo oficial página 26, com seletores do catálogo ativo, nível fixo, avisos e quatro seções; verificar contrato HTML/DOM, foco, teclado, texto longo e layouts de 1440/390 px sem overflow ou origem/usuário fictícios.
- [x] 4.2 Integrar `apiRequest`/AuthUI, envio explícito único, espera local de 45 s, erros/limite/termos pendentes, rascunho somente em memória e limpeza de identidade; verificar nos testes DOM XSS como texto, catálogo vazio/falho, respostas de filtros atrasadas, sucesso anterior identificado, duplo envio, abort, logout/troca de conta e resultado tardio ignorado, sem retries ou armazenamento persistente.
- [x] 4.3 Disponibilizar Tutor na navegação e atualizar somente menções antigas desse recurso; registrar recorte pontual em `screen-to-use-case-map-v1.md`, `architecture-master-v1.md` e fechamento parcial de OD-07 para este caso. Verificar que resumos, chat persistente, ações no plano e demais funções futuras não se tornaram controles ativos e que os quatro binários oficiais não mudaram.
- [x] 4.4 Acrescentar E2E com MySQL descartável para navegação, aviso, novo aceite e indisponibilidade real com Tutor desabilitado; verificar no navegador sem interceptação do Gemini, sem chave real no runner e preservando os cenários dos vinte casos anteriores. Documentar a separação desse E2E e da prova real.

## 5. Comprovar integração real e fechar documentação

- [x] 5.1 Com ambiente Gemini local preparado pelo responsável, demonstrar pela interface uma dúvida sintética e validar resposta real com quatro partes, pertinência ao ENEM e exercício sem gabarito; registrar data/modelo/status/checklist sem payload, chave ou captura de sessão em `validacao.md` desta change. Sem acesso/chave/quota, deixar este item pendente e declarar o bloqueio da prova real.
- [x] 5.2 Completar README e relatório com sucesso real, 400 sem chamada externa, timeout comprovado em unidade e explicação das camadas; verificar correspondência aos critérios da aula, apontar limitações reais e distinguir evidência de integração de testes com transporte controlado, sem inflar contagem de CRUD.

## 6. Verificar compatibilidade da entrega

- [x] 6.1 Executar regressão backend/frontend e coberturas conforme conventions, além de E2E/MySQL dos fluxos afetados; verificar manutenção dos 29 testes originais, vinte casos, 21 mappers, evidências históricas e recursos SQL existentes, sem migration, tabela ou persistência de conversa novas. Registrar comandos/resultados reais no relatório.
- [x] 6.2 Fazer verificação OpenSpec da implementação, revisar diffs/segredos/links/UTF-8 e executar `openspec validate adicionar-tutor-revisao-com-gemini --strict`; verificar rastreabilidade entre requisitos, tela, contrato e testes, corrigindo achados críticos antes de marcar conclusão.

## Workflow follow-up

- Depois de aplicar e verificar, sincronizar as duas capabilities e arquivar a change.
- Commit/push somente após autorização explícita; não publicar uso real, implantar AWS ou produzir vídeo nesta change.
