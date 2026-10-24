# Proposta — 3. Prática de Questões com histórico

## Why

O início do Aluno já autentica a conta, mas não permite estudar. Esta entrega permite escolher uma Questão, responder, receber correção do servidor e consultar o próprio histórico persistido.

## What Changes

- Oferecer Questões publicadas elegíveis com filtro por Matéria/Assunto, sem revelar gabarito antes da resposta.
- Criar tentativa individual vinculada à versão exata e corrigir no servidor.
- Persistir resposta, correção, data e classificação histórica; consultar histórico e detalhe após recarga ou novo login.
- Impedir duplicação por reenvio e acesso ao histórico de outra conta.
- Fora de escopo: montagem adaptativa, prática em lote, cronômetro, tutor, resumos, recomendações e métricas de dashboard. O recorte de ALU-QUE-001/002/003 resolve uma Questão por tentativa.

## Capabilities

### New Capabilities

- `pratica-questoes`: leitura segura, tentativa individual, correção e histórico do Aluno.

### Modified Capabilities

- `autenticacao-escolar`: explicitar autorização para `/api/aluno/*` por perfil e propriedade sem liberar consultas administrativas com gabarito.

## Impact

- Superfícies: Services/Models de tentativa e resposta, Repository especializado para histórico, Controllers/rotas de Aluno, autorização explícita em `auth_http.py` e telas ALU-QUE-001/002/003.
- Contratos propostos: listagem segura em `/api/aluno/questoes`, criação/consulta de tentativas em `/api/aluno/praticas` e envio da resposta em `/api/aluno/praticas/<id>/resposta`.
- Banco: migration aditiva de tentativas com referência a `questao_versao_id`, snapshot de taxonomia e preservação dos dados atuais.
- Dependências: aplicar, verificar, sincronizar e arquivar o item 2 (`gestao-basica-questoes`) antes desta entrega. Localizar sua change pelo nome, inclusive após arquivamento. Publicações e leituras versionadas do item 2 são o contrato de conteúdo; não consumir o endpoint legado de gabarito no Aluno.
- ADRs: 001, 002, 003, 005 e 006. Preservar catálogo, login/logout, contratos legados, testes existentes e artefatos visuais congelados.
