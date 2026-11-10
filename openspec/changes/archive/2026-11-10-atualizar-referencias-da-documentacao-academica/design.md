# Design: referências atuais com histórico preservado

## Context

Ver [proposal.md](proposal.md) para a motivação. O código de referência é o commit `bb9823de87f3be6ae4d0a0cb3484ff2725353d7e`. O design delimita uma ambiguidade importante da correção: um arquivo existente nem sempre contém o símbolo anunciado pela tabela, e contagens históricas de seis módulos não devem ser substituídas indiscriminadamente por sete.

## Goals / Non-Goals

**Objetivo:** permitir percorrer os dois fluxos até o símbolo implementado e identificar a suíte atual sem confundir documentação com nova execução de testes.

**Limite:** editar somente `docs/technical/fluxogramas-casos-de-uso.md` e `docs/technical/entrega-academica.md`, além dos artefatos desta change. Preservar os fluxos, requisitos, vinte IDs e ressalvas acadêmicas. Não redesenhar os diagramas nem ampliar o escopo para todo o acervo técnico.

## Decisions

### 1. Verificar símbolo e proprietário, além da existência do destino

Os 24 links quebrados estão nas duas tabelas de rastreabilidade dos fluxogramas. Usar os caminhos sob `backend/app/modules/` segundo o proprietário: autenticação em Contas, diagnóstico em Desempenho, execução em Simulados, versões em Conteúdo e tentativas de prática em Práticas.

Conferir também as referências próximas afetadas pelas mesmas reorganizações:

- Registro de rota em `modules/desempenho/routes.py` e `modules/simulados/routes.py`; `app/routes.py` continua o agregador, sem anunciar que declara diretamente as rotas dos casos de uso.
- `corpo` em `app/core/validacao.py` e persistência canônica em `app/core/persistencia.py`; distinguir a ponte estática `app/models/crud_mixin.py` da implementação.
- As Models de Simulado permanecem juntas em `backend/app/modules/simulados/models/simulado.py`. Apontar para esse arquivo após conferir cada classe e identificar `resultado` como método de `SimuladoTentativa`; não separar ou mover Models nesta change documental.
- Desempenho executa `DesempenhoRepository.agregar` e `CALL sp_desempenho_resumo`, apoiado nas views históricas documentadas. Retirar a referência inexistente a `DesempenhoRepository.fatos`; não apresentar projeções ORM de compatibilidade como execução de produção. Referenciar a seção existente das interfaces SQL, sem copiar consultas para o documento.

Alternativa rejeitada: substituir automaticamente prefixos de diretórios e considerar o trabalho concluído. A existência do arquivo não prova correspondência do fluxo descrito.

### 2. Atualizar o retrato atual sem reescrever a história

Na entrega, distinguir os seis módulos do recorte de domínio original do sétimo módulo Tutor, sem persistência própria. O agregador atual registra sete Blueprints proprietários; as 21 Models permanecem.

Descrever os seis testes E2E atuais pelos arquivos `entrega-academica.spec.js`, `plano-simulado.spec.js`, `privacidade.spec.js`, `tutor.spec.js`, `catalogo-detalhe.spec.js` e `usuarios.spec.js`. Os vinte casos continuam passos numerados do primeiro teste; não transformar seis testes em seis funcionalidades nem contar setup como caso entregue.

Preservar as evidências antigas com suas datas/SHAs. Acrescentar a aprovação da [execução 42736058343](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42736058343) para o SHA de referência, sem afirmar que esse CI executou a correção documental futura. Menções datadas à auditoria dos seis módulos SQL continuam históricas, pois Tutor não acrescenta Repository/procedure. Preservar as ressalvas de exclusão física, Models auxiliares, aceite docente e entrega externa; esta change não as resolve.

### 3. Validação proporcional, sem novo ferramental

Usar leitura estática e comandos existentes. Conferir todos os links locais nos dois documentos (incluindo âncoras alteradas), cada símbolo das tabelas afetadas, os sete registros de Blueprint e a descoberta dos seis casos em `npm run test:e2e:list`. A descoberta não executa os percursos nem exige MySQL.

Registrar em `validacao.md` os comandos, links corrigidos, contagens e limites. Confirmar que somente os dois documentos e os artefatos da change diferem do estado inicial. Executar `git diff --check` e `openspec validate --all --strict`. Não instalar bibliotecas, criar scripts permanentes, executar integrações ou inferir aprovação da aplicação a partir de uma checagem de Markdown.

## Risks / Trade-offs

- **Link válido para símbolo errado:** conferir a declaração e o chamador atuais, especialmente cada classe de Simulado no arquivo compartilhado e os helpers compartilhados.
- **Contagens históricas apagadas:** alterar apenas afirmações sobre o estado atual; manter relatórios arquivados e auditorias datadas.
- **Documentação prometer CRUD ou aprovação docente:** manter as ressalvas e os limites dos vinte casos.
- **Escopo crescer durante a revisão:** registrar eventuais outros pontos para análise futura, sem editar arquivos adicionais.

## Migration Plan

Sem migration, instalação ou mudança operacional. Aplicar as duas correções documentais e validar. Se necessário, reverter somente as edições desta change, preservando alterações legítimas locais. Specs são dispensadas por `skip_specs: true`; arquivamento segue a verificação, e commit/push exigem autorização própria.
