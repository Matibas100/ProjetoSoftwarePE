# Proposta — Termos e consentimento para o plano personalizado

## Why

A atividade exige Termo de Uso e Termo de Consentimento adaptados ao projeto. Hoje a Plataforma ENEM não apresenta esses documentos nem registra decisões de privacidade; adicionar esse fluxo permite demonstrar o bônus correspondente com persistência real, sem confundir aceite contratual com autorização genérica de tratamento.

## What Changes

- Elaborar os dois textos com base nos modelos fornecidos, descrevendo somente cadastro, autenticação, questões, práticas, simulados, desempenho e plano básico efetivamente existentes. Publicar documentos HTML versionados, legíveis e imprimíveis, com referência em `docs/legal/README.md` e no README principal.
- Identificar **Matheus Gabriel Oliveira Martins** como responsável informado pelo grupo. Usar `contato@plataformaenem.example` somente como contato fictício, explicitamente provisório e sem apresentá-lo como canal funcional.
- Manter como público pessoas que se preparam para o ENEM, sem criar limite etário de produto. Conforme decisão do grupo, esta entrega será uma demonstração acadêmica com dados sintéticos; autorização verificável de responsáveis e atendimento operacional a menores ficam para outra change antes do uso real.
- **BREAKING:** exigir aceite explícito da versão vigente do Termo de Uso no cadastro público. Criar conta e registro do aceite na mesma transação, mantendo validações, DTO público e ausência de login automático.
- Disponibilizar página de privacidade do Aluno para consultar registros, aceitar os termos para contas existentes e aceitar, recusar ou revogar **somente** o consentimento para gerar e manter o plano personalizado a partir do próprio desempenho.
- **BREAKING:** exigir Termo de Uso aceito e consentimento vigente no servidor para consultar, gerar, recalcular ou concluir itens de plano, inclusive reenvios de operações anteriores. Contas existentes começam sem decisão; não haverá aceite presumido.
- Recusar ou revogar o consentimento mantém questões, práticas, simulados e diagnóstico disponíveis. Como decisão de minimização desta proposta, qualquer dessas decisões negativas, confirmada após aviso, elimina os planos e itens derivados daquela conta, atomicamente com o registro da decisão; nova autorização começa sem plano.
- Persistir versão, hash do documento, decisão, instante do servidor e vínculo com a conta; proteger mudanças concorrentes e reenvios sem coletar CPF, documento, data de nascimento, IP ou assinatura digital.

### Fora de escopo

Autorização parental, verificação de idade, uso real com dados pessoais, canal de atendimento operacional, adequação jurídica integral, política completa de retenção de todas as categorias, exclusão/exportação geral de conta, certificação ISO, marketing, IA, hospedagem, slides, vídeo, commit e push. Os textos serão minutas acadêmicas e não devem afirmar que essas capacidades já existem. DOCX/PDF não são entregáveis obrigatórios desta change: os dois HTML completos poderão ser impressos como PDF.

## Capabilities

### New Capabilities

- `termos-e-consentimento`: documentos públicos versionados, aceite, consulta de decisões, consentimento específico do plano, recusa, revogação e evidência persistida.

### Modified Capabilities

- `autenticacao-escolar`: aceite explícito no cadastro público e consulta pública dos metadados dos termos, preservando os demais controles de sessão/perfil.
- `plano-estudos-basico`: autorização específica antes de acessar/processar o plano e exceção delimitada à preservação de histórico na revogação confirmada.

## Impact

- Frontend: `cadastro.html`, `login.html`, `js/auth-page.js`, `aluno/plano.html`, `js/aluno-plano.js`, início do Aluno, nova página `aluno/privacidade.html`, documentos em `frontend/legal/` e estilos locais. Não alterar os binários oficiais do Desktop V1 nem reformatar outras telas.
- Backend: novas Model, Controller e Services de privacidade; Repository somente para consultas de última decisão, locks, reenvios e eliminação coordenada dos derivados do plano. Integração pontual com cadastro e os quatro casos de uso de plano.
- API: `GET /api/termos`, `GET /api/aluno/privacidade`, `POST /api/aluno/privacidade/termos-uso` e POSTs em `/api/aluno/privacidade/consentimento-plano/{aceitar,recusar,revogar}`; evolução explícita do corpo de cadastro e das permissões do plano.
- MySQL: migration aditiva `010_create_registros_privacidade.sql`, snapshot consolidado, fingerprint e testes de instalação/upgrade. Sem mudar migrations 000–009, procedure ou dados funcionais durante o upgrade.
- Documentação: operação de privacidade, diagrama de classes, fluxogramas afetados, matriz acadêmica, README e ADR-009 para consentimento e eliminação restrita de planos. Complementa ADRs 001, 002, 006 e 008.
- Dependências: nenhuma biblioteca ou serviço externo novo. A change considera o estado local já aplicado das changes anteriores, preservando suas alterações. Antes de publicação com dados reais, são necessários contato válido, política de retenção geral e fluxo aprovado para menores.

### Compatibilidade e validação

Login, CLI de criação de Administrador, cookies, CSRF, perfis, catálogo, respostas e métricas permanecem com seus contratos atuais. Os 29 cenários originais continuam; helpers de cadastro passam a fornecer o aceite explícito e testes de plano consentem pela API real. Cobrir rollback, autorização, concorrência, revogação, atualização de versão e navegador com MySQL real, sem bypass ou mocks de integração. A pontuação do bônus depende da avaliação do professor, não apenas da existência dos documentos.
