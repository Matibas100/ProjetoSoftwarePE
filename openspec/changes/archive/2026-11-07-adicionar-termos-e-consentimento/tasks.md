# Tarefas — Termos e consentimento

## 1. Preflight e documentos

- [x] 1.1 Conferir proposal, design, as três delta specs, conventions e ADRs 001/002/006/008; registrar baseline dos arquivos afetados, alterações locais já existentes e hashes de migrations 000–009 em `validacao.md`. Verificar que somente o escopo desta change será alterado e que `.env`/credenciais não foram lidos ou registrados.
- [x] 1.2 Elaborar os dois HTML completos em `frontend/legal/` conforme os modelos do professor e o conteúdo definido no design, com versão/data, leitura pública, estilo de impressão, responsável, contato explicitamente fictício e limites acadêmicos. Criar `docs/legal/README.md`, metadados/hashes em `app/domain/privacidade.py` e seus testes; verificar coerência do texto com dados reais do código, hashes, links, leitura sem JS, teclado e impressão.

## 2. Persistência de decisões

- [x] 2.1 Implementar `RegistroPrivacidade` em arquivo próprio, com herança `ModeloBase`, constraints, índices e proteção ORM contra alteração/exclusão; registrar import da Model. Verificar por unitários e MySQL real campos obrigatórios, combinações tipo/ação, unicidade usuário/chave, UTC, vínculo de usuário e imutabilidade, sem incluir dados sensíveis desnecessários.
- [x] 2.2 Acrescentar migration `010_create_registros_privacidade.sql`, atualizar snapshot e fingerprints no runner atual sem alterar 000–009 ou procedure; criar testes específicos de migration e documentar implantação/compensação em `operacao-privacidade.md`. Verificar instalação vazia, upgrade de 009 com dados/planos, ausência de backfill, baseline 010, equivalência, drift e reexecução em MySQL descartável.

## 3. API de termos e decisões

- [x] 3.1 Implementar `PrivacidadeController`, `ConsultarTermosService`, `ConsultarPrivacidadeService`, consultas especializadas do Repository e rotas GET, liberando somente os metadados públicos no middleware. Documentar contratos em `operacao-privacidade.md`; verificar por unitários/integrações 200/HEAD, 401/403, 404/405, `no-store`, estado inicial e isolamento entre contas, com leitura corrente consistente.
- [x] 3.2 Implementar `AceitarTermosUsoService`, `ConsentirPlanoService`, `RecusarConsentimentoPlanoService` e `RevogarConsentimentoPlanoService`, cada qual com sua rota fixa, validação estrita, UUID/revisão, lock de usuário e replay. Incluir eliminação especializada de itens e gerações próprias em ordem compatível com RESTRICT, sem relaxar guards gerais. Verificar em unitários e MySQL real transições, versão/hash, negativo sem confirmação, replay antigo sem novos efeitos, revisão obsoleta, conta alheia e rollback integral por falha real de persistência; documentar os efeitos e a irreversibilidade.
- [x] 3.3 Adaptar o cadastro para receber `termos_uso:{versao,aceito:true}` e persistir usuário+aceite em uma só transação, compartilhando a preparação existente sem commit intermediário e preservando CLI administrativa. Atualizar documentação de autenticação e helpers de cadastro dos testes; verificar corpo antigo recusado, validações atuais, duplicidade concorrente, falha da evidência sem conta parcial, DTO/destino existentes e inexistência de consentimento automático do plano.

## 4. Autorização efetiva do plano

- [x] 4.1 Implementar `ValidarPermissaoPlanoService` e integrá-lo aos quatro casos de plano depois do lock de usuário e antes de consultar snapshots, replay, itens ou diagnóstico. Adaptar a consulta ao limite transacional definido, sem mudar seletor/fórmula ou diagnóstico independente; verificar 403 uniforme sem autorização, autorização vigente, falha fechada de consulta e regressão de geração/recálculo/conclusão por unitários e MySQL real.
- [x] 4.2 Cobrir em MySQL real a concorrência decisão versus decisão e negativa versus geração/recálculo, incluindo snapshot antigo de autenticação, nova autorização, eliminação de todas as gerações e preservação de outra conta/respostas/simulados. Registrar ADR-009 e atualizar `operacao-plano-estudos.md`; verificar que nenhuma nova geração sobrevive à negativa vencedora e que os guards normais continuam impedindo exclusão fora do caso aprovado.

## 5. Interface e navegação

- [x] 5.1 Adaptar `cadastro.html`/`js/auth-page.js` para carregar metadados, oferecer leitura dos dois documentos e enviar explicitamente o objeto de aceite, com checkbox inicialmente desmarcado; adicionar os links de leitura ao login. Verificar por Vitest carregamento/erro de metadados, desmarcação após versão desatualizada, serialização booleana correta, preservação de nome/e-mail, ausência de reenvio automático e regressão dos contratos HTML/autenticação.
- [x] 5.2 Criar `/aluno/privacidade.html`, seu JavaScript e estilos mínimos, com consulta da evidência, aceite de uso, autorização/recusa do plano, revogação e confirmação de eliminação. Adicionar acesso fixo pelo início e plano; verificar por DOM estados atuais, sucesso/erro, cancelamento sem POST, revisão/chave de retry, igualdade de acesso às escolhas, replay histórico com estado atual, sessão expirada e troca de identidade. Atualizar mapa de telas/casos de uso com a extensão acadêmica, sem tocar nos binários oficiais.
- [x] 5.3 Integrar `aluno/plano.html`/`js/aluno-plano.js` com a consulta prévia de privacidade, explicação de consentimento pendente e limpeza de snapshots/intenção após negativa ou perda de permissão. Verificar por DOM retorno de outra aba, identidade alterada, resposta atrasada, revalidação antes de reexibir plano e fluxo normal de estudo autorizado, mantendo proteção de alterações não salvas em simulados.

## 6. Integração final e documentação acadêmica

- [x] 6.1 Adicionar E2E independente de privacidade com MySQL real e atualizar os cadastros/E2E de plano existentes para aceitar pela interface, sem bypass. Verificar leitura pública, cadastro, recusa seguida de questões/simulado utilizáveis, base suficiente por respostas reais, autorização, geração, conclusão, revogação, nova autorização e ausência dos planos antigos; conferir teclado, 1440/390 e retorno de outra aba. Não criar vídeo, HAR ou storage state autenticado.
- [x] 6.2 Atualizar README, matriz acadêmica, diagrama de classes e links/fluxogramas afetados, descrevendo o que foi efetivamente implementado e preservando a lista original de 20 casos. Verificar correspondência com Model/rotas/UI, fontes dos dois termos e pendências de contato real, retenção geral e proteção de menores, sem declarar bônus garantido, publicação já feita desta change ou adequação jurídica integral.
- [x] 6.3 Executar regressão backend com integrações e migrations MySQL reais, cobertura frontend, testes do servidor e E2E completos, usando opt-ins apenas no processo. Verificar os 29 cenários originais, suíte ampliada, cobertura mínima por stack de 90% linhas/85% branches e ausência de executável de produção sem cobertura; registrar comandos, resultados e limitações reais em `validacao.md`.
- [x] 6.4 Revisar diff final contra baseline, checar segredos sem exibir valores, validar a change com `openspec validate adicionar-termos-e-consentimento --strict` e registrar a correspondência requisitos/cenários/evidências. Verificar ausência de edições de migrations aplicadas, perda de dados no upgrade, mudanças alheias ou artefatos visuais oficiais; manter commit/push fora desta execução.

## Workflow follow-up

- Executar `$openspec-verify-change` e resolver achados antes de concluir a entrega.
- Sincronizar as três capabilities com `$openspec-sync-specs`, preservando requisitos e cenários existentes não alterados.
- Arquivar com `$openspec-archive-change` somente após verificação e sincronização; commit e push precisam de autorização explícita própria.
- Antes de uso real, tratar contato operacional, política geral de retenção/direitos e proteção/autorização de menores em change própria. AWS, vídeo e apresentação continuam para etapas posteriores.
