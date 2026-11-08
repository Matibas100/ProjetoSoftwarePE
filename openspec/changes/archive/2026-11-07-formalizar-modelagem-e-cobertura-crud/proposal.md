# Proposta — Formalizar modelagem e cobertura CRUD

## Why

O grupo informou que não entregou uma modelagem de domínio anterior, mas o repositório já representa 21 Models e seus relacionamentos. A atividade de CRUD exige distinguir persistência disponível na Model, operações realmente expostas por API/tela e restrições de domínio, sem pressupor que os vinte casos documentados equivalem ao CRUD de todas as entidades.

## What Changes

- Formalizar a modelagem do domínio atual em `docs/technical/modelagem-de-dominio.md`, usando código, schema e diagrama existentes como fontes, sem inventar uma entrega anterior ou aprovação do professor.
- Revisar a organização de `diagrama-de-classes.md` para separar a visão de domínio das visões de aplicação/composição, mantendo classes, atributos e relacionamentos coerentes com as 21 Models.
- Publicar `docs/technical/matriz-crud.md` com cobertura das 21 Models: métodos herdados, casos de uso, rotas, telas, restrições e lacunas. O levantamento inicial está em [levantamento-crud.md](levantamento-crud.md).
- Distinguir CRUD convencional de Matéria/Assunto, gestão parcial de Usuário, arquivamento de Questão/Simulado, ciclo do plano, execução de tentativas, referências fixas e registros auxiliares/históricos.
- Registrar propostas de continuidade sem contratar funcionalidades novas: gestão de Usuários, consultas individuais de Matéria/Assunto se exigidas e definição acadêmica das restrições de exclusão. Ausência, restrição justificada e aceite do professor são situações diferentes.
- Acrescentar links no README e na matriz de entrega acadêmica, mantendo os vinte casos e seus IDs. A documentação deve declarar as pendências, não certificar cumprimento integral do CRUD de todas as Models.

### Fora de escopo

Alterar Models, capacidades Active Record, banco, migrations, rotas, Controllers, Services, Repositories ou telas; implementar gestão/exclusão de Usuários; equiparar arquivamento a DELETE; apagar históricos/evidências; presumir aceite docente; regularizar ou enviar atividade no Classroom; mudanças visuais, vídeo, slides, AWS, guia de estudo, commit, push ou merge.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma mudança de comportamento. Esta change usa `skip_specs: true`: formaliza documentação e rastreabilidade. As onze specs, 21 Models e funcionalidades existentes permanecem intactas. Cada evolução funcional futura precisará de escopo e change próprios.

## Impact

- Criar dois documentos técnicos e revisar apenas a organização/comentários do diagrama atual, mais links/contexto no README e em `docs/technical/entrega-academica.md`.
- Preservar ADRs 003, 008, 009 e 010: restrição de exclusão vinculada, capacidades por classe, negativa atômica do plano e propriedade modular.
- Nenhuma dependência nova, execução de migrations, acesso ao banco operacional ou teste de aplicação necessário. Verificações documentais por AST/metadata sem conexão, inventário de rotas sem SQL, links, contagens e comparação com fontes existentes.
- Sem dependência de change ativa. A proposta resolve a falta de clareza documental; não fecha automaticamente as lacunas funcionais ou a aceitação acadêmica identificadas no levantamento.
