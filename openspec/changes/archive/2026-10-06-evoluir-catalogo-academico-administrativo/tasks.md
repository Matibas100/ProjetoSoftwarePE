## 1. Caracterização e proteção da migração

- [x] 1.1 Registrar testes de caracterização do schema e dos contratos atuais de Matéria, Assunto e Questão antes das mudanças, verificando que os testes legados selecionados passam contra o MySQL real.
- [x] 1.2 Adicionar fixtures de upgrade com dados válidos, Matéria não classificável e Assuntos normalizados conflitantes, verificando que os cenários preservam IDs, nomes, descrições e vínculos.
- [x] 1.3 Criar consultas de auditoria seguras para classificação de Matérias e colisões de Assuntos, verificando que a saída identifica apenas IDs, nomes e causas, sem credenciais ou conteúdo de `.env`.

## 2. Migrations e Models do catálogo

- [x] 2.1 Criar a migration SQL preparatória para `areas_enem`, colunas de Área/status/timestamps/nome normalizado e `assunto_transferencias`, verificando aplicação em banco vazio e cópia do MVP sem remoção de dados.
- [x] 2.2 Implementar no SQL o backfill fechado de Áreas, status e nomes normalizados, verificando os quatro catálogos fixos, todas as correspondências previstas e a permanência de desconhecidos como pendência explícita.
- [x] 2.3 Criar a migration SQL restritiva com prechecks, `NOT NULL`, checks, unique composta e FKs `RESTRICT`, verificando bloqueio seguro para pendências e ausência de qualquer cascade Matéria → Assunto.
- [x] 2.4 Atualizar `backend/database/create_database.sql` para o mesmo estado final das migrations, verificando a equivalência pelo teste de fingerprint do runner e a continuidade de `sp_questoes_por_assunto`.
- [x] 2.5 Implementar as Models `AreaEnem` e `AssuntoTransferencia` e evoluir `Materia`, `Assunto` e relacionamentos ORM, verificando serialização, campos atualizáveis e inexistência de `delete-orphan` ou cascade destrutivo.

## 3. Domínio e transações

- [x] 3.1 Implementar a função única de normalização NFC, espaços e caixa, verificando por testes unitários caixa, acentos, espaços, Unicode, vazio e limite de tamanho.
- [x] 3.2 Evoluir o `CrudMixin` com participação explícita sem commit e criar `TransactionManager`, verificando que o CRUD autônomo mantém o comportamento atual e que falhas compostas revertem todas as alterações.
- [x] 3.3 Implementar regras reutilizáveis de disponibilidade, inativação, arquivamento e reativação, verificando dependências, proibição de novos vínculos e ausência de cascata de estado.
- [x] 3.4 Implementar `CatalogoRepository` apenas para filtros, contagens, impacto e locks, verificando que não contém CRUD duplicado, commit próprio nem Stored Procedure fora do `QuestaoRepository`.

## 4. APIs e casos de uso

- [x] 4.1 Implementar rota, Controller e Service de consulta das quatro Áreas, verificando ordem determinística, campos estáveis e ausência de rotas de mutação.
- [x] 4.2 Evoluir criação e atualização de Matérias para exigir Área e expor campos aditivos, verificando 201/200 válidos, 400 para dados inválidos, 404 para Área ausente e conflito de nome.
- [x] 4.3 Evoluir criação e atualização de Assuntos com `nome_normalizado` e disponibilidade da Matéria, verificando 409 para equivalentes ativos ou arquivados e aceitação em Matérias diferentes.
- [x] 4.4 Implementar listagens administrativas paginadas de Matérias e Assuntos, verificando filtros combinados, limites de paginação, ordenação estável, contagens e `resumos: null`.
- [x] 4.5 Implementar os casos de uso e endpoints de inativar, arquivar e reativar Matéria/Assunto, verificando transições válidas, dependências e mensagens HTTP previsíveis.
- [x] 4.6 Implementar impacto e exclusão física segura, verificando 204 somente sem vínculos, 409 com contagens quando bloqueada e preservação das dependências após corrida concorrente.
- [x] 4.7 Implementar prévia e transferência atômica de Assunto com registro histórico, verificando destino, conflito normalizado, impacto alterado, rollback e preservação de IDs e Questões.
- [x] 4.8 Encaminhar troca de `materia_id` pelo PUT legado ao mesmo caso de uso de transferência e manter as leituras legadas em arrays com campos antigos, verificando regressão dos consumidores atuais.

## 5. Base visual e comportamento compartilhado

- [x] 5.1 Copiar do pacote oficial somente os SVGs necessários e criar o shell administrativo compartilhado, verificando visualmente logo, sidebar, header, tipografia, cores, espaçamentos e estados de foco em 1440 px.
- [x] 5.2 Criar utilitários frontend compartilhados de API, filtros, paginação, mensagens e modal acessível, verificando tratamento de 400/404/409/500, contenção/retorno de foco e ausência de HTML não escapado.
- [x] 5.3 Implementar proteção de alterações não salvas em cancelamento, troca de edição e navegação, verificando confirmação apenas quando o formulário divergir do último estado persistido.

## 6. ADM-CON-001 — Gestão de Matérias

- [x] 6.1 Implementar a página de Matérias com busca, status, limpeza, tabela, contagens e paginação, verificando integração com `/api/admin/materias` e os estados loading, vazio e sem resultado.
- [x] 6.2 Implementar criação e edição de Matéria com Área obrigatória, descrição e status, verificando preservação do formulário em erro, atualização contextual da tabela e mensagem de sucesso.
- [x] 6.3 Implementar menu de ações, impacto, inativação, arquivamento, reativação e exclusão, verificando confirmações, bloqueios com contagens e inexistência de remoção em cascata.

## 7. ADM-CON-002 — Gestão de Assuntos

- [x] 7.1 Implementar a página de Assuntos com busca e filtros dependentes de Área, Matéria e status, verificando paginação, limpeza, contagens de Questões e marcador acessível para Resumos indisponíveis.
- [x] 7.2 Implementar criação e edição de Assunto, verificando Matéria ativa obrigatória, erro de duplicidade junto ao nome, preservação dos valores e atualização da lista sem perder filtros.
- [x] 7.3 Implementar prévia e confirmação de transferência, verificando origem/destino, impacto de Questões, reconfirmação após 409 e mudança somente após confirmação explícita.
- [x] 7.4 Implementar ações de ciclo de vida e exclusão de Assunto, verificando arquivamento com Questões preservadas, bloqueio da exclusão vinculada e reativação sem duplicidade.

## 8. Integração, regressão e entrega

- [x] 8.1 Atualizar os seletores do MVP para oferecer somente Matérias e Assuntos ativos sem reescrever a gestão de Questões, verificando cadastro e busca de Questões e a Stored Procedure existente.
- [x] 8.2 Ampliar os testes DOM e de contrato HTML das duas telas, verificando filtros, paginação, formulários, modais, estados, teclado, alterações não salvas e proteção contra injeção.
- [x] 8.3 Ampliar as integrações MySQL para migrations, FKs, unicidade, ciclo de vida, impacto, transferência, concorrência e APIs, verificando limpeza dos próprios dados e preservação das integrações originais.
- [x] 8.4 Executar `make test-unit`, `make test-frontend`, as integrações MySQL com opt-in e `make test-coverage`, verificando os limites de 90% de linhas e 85% de branches sem expor configurações sensíveis.
- [x] 8.5 Comparar ADM-CON-001 e ADM-CON-002 em 1440 px com o Protótipo, Handoff, Inventário e Errata oficiais, corrigindo divergências de hierarquia, espaçamento, texto, estados e acessibilidade sem alterar os artefatos congelados.
- [x] 8.6 Atualizar a documentação operacional de rotas, migrations, auditoria de dados e execução local, verificando links, comandos e a ausência de Alembic, Flask-Migrate, credenciais ou funcionalidades fora do escopo.
