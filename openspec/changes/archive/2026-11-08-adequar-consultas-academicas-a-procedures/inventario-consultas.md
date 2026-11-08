# Inventário — Primeiro recorte de consultas por procedures

Levantamento de código em 07/11/2026. Evidência estática: não representa nova execução de banco nem aceite do professor. O recorte cobre seis rotas existentes; não representa todas as consultas especializadas do sistema.

## Operações desta change

| ID | Entrada existente | Caminho atual de leitura | Destino |
|---|---|---|---|
| C01 | `GET /api/admin/materias` | `ListarMateriasAdminService` → `CatalogoRepository.listar_materias_admin` | `sp_materias_admin` |
| C02 | `GET /api/admin/assuntos` | `ListarAssuntosAdminService` → `CatalogoRepository.listar_assuntos_admin` | `sp_assuntos_admin` |
| C03 | `GET /api/admin/questoes` | `ListarQuestoesAdminService` → `QuestaoRepository.listar_admin` | `sp_questoes_admin` |
| C04 | `GET /api/aluno/desempenho` | `ConsultarDesempenhoService` → `ConsultaMetricasMySQL` → `DesempenhoRepository.agregar` | `sp_desempenho_resumo` |
| C05 | `GET /api/aluno/dashboard` | diagnóstico reutilizado e `DesempenhoRepository.atividades` | `sp_desempenho_resumo` + `sp_atividades_recentes` |
| C06 | `GET /api/admin/dashboard` | `DesempenhoRepository.administrativo` → APIs de Conteúdo/Simulados → contagens dos proprietários | `sp_conteudo_contagens_dashboard` + `sp_simulados_contagens_dashboard` |

Consultar `backend/app/modules/conteudo/services/listar_catalogo_admin_service.py`, `gestao_questao_service.py`, os Repositories de Conteúdo, `desempenho/services/dashboard_service.py` e seus Repositories/adaptadores. Os wrappers/API dos módulos continuam respeitados.

## Recursos SQL aprovados para esta etapa

Todas as procedures usam parâmetros IN, SQL estático, `READS SQL DATA` e `SQL SECURITY INVOKER`. Dados são resultados tipados, sem JSON HTTP gerado pelo banco. Não há COMMIT/ROLLBACK/START TRANSACTION, SQL dinâmico ou tabelas temporárias nas procedures.

| Migration | Procedure | Parâmetros IN, na ordem | Resultados úteis, na ordem |
|---|---|---|---|
| 011 | `sp_materias_admin` | `p_busca VARCHAR(100)`, `p_status VARCHAR(20)`, `p_area_enem_id BIGINT UNSIGNED`, `p_pagina BIGINT UNSIGNED`, `p_por_pagina INT` | linhas da página com Matéria/Área e contagens; uma linha `total` |
| 011 | `sp_assuntos_admin` | `p_busca VARCHAR(100)`, `p_status VARCHAR(20)`, `p_area_enem_id BIGINT UNSIGNED`, `p_materia_id BIGINT UNSIGNED`, `p_pagina BIGINT UNSIGNED`, `p_por_pagina INT` | linhas da página com Assunto/Matéria/Área e contagem; uma linha `total` |
| 011 | `sp_questoes_admin` | `p_busca VARCHAR(100)`, `p_status VARCHAR(20)`, `p_dificuldade VARCHAR(10)`, `p_area_enem_id BIGINT UNSIGNED`, `p_materia_id BIGINT UNSIGNED`, `p_assunto_id BIGINT UNSIGNED`, `p_pagina BIGINT UNSIGNED`, `p_por_pagina INT` | linhas da página com Questão/Assunto/Matéria/Área; uma linha `total` |
| 011 | `sp_conteudo_contagens_dashboard` | nenhum | uma linha: matérias/assuntos ativos e Questões por estado |
| 012 | `sp_desempenho_resumo` | `p_usuario_id INT`, `p_inicio DATETIME(6)`, `p_fim DATETIME(6)` | resumo geral; grupos por Matéria; grupos por Matéria/Assunto |
| 012 | `sp_atividades_recentes` | `p_usuario_id INT`, `p_inicio DATETIME(6)`, `p_fim DATETIME(6)` | até cinco atividades próprias, sem duplicação de Simulado |
| 012 | `sp_simulados_contagens_dashboard` | nenhum | uma linha: Simulados por estado e tentativas finalizadas |

Campos completos e aliases das linhas de listagem devem espelhar os `to_dict()` e adaptadores atuais: usar prefixos por recurso para evitar colisões, converter datas como hoje e não hidratar instâncias ORM incompletas. As três listas preservam todos os campos atuais e o envelope; o banco retorna dados e total, o Service mantém validações e envelope.

| View (012) | Proprietário e contrato de leitura |
|---|---|
| `vw_conteudo_classificacao_historica` | Conteúdo: versões publicadas com `questao_versao_id`, IDs e nomes históricos de Matéria/Assunto, conforme a projeção atual |
| `vw_praticas_fatos_desempenho` | Práticas: somente tentativas respondidas; `tipo`, `id`, `atividade_id`, `usuario_id`, `ocorrido_em`, `correta`, IDs/nomes históricos de Matéria/Assunto |
| `vw_simulados_fatos_desempenho` | Simulados: somente respostas não brancas de tentativas finalizadas, ligadas à classificação histórica pública; mesmas colunas de fatos |
| `vw_simulados_atividades` | Simulados: uma linha por tentativa finalizada, inclusive totalmente em branco; `tipo`, `id`, `usuario_id`, `ocorrido_em`, `titulo` |

As views não são novas Models/tabelas e não são publicadas pela API HTTP. São interfaces SQL de leitura explicitamente aprovadas entre proprietários. Todas usam `SQL SECURITY INVOKER`, colunas explícitas e dependências no próprio schema. A procedure de métricas usa as duas views de fatos; a de atividades deriva práticas de sua view de fatos e combina com a view de atividades de Simulados. Contagens permanecem no proprietário e são chamadas pelas APIs públicas existentes.

## Preservação semântica obrigatória

- Matérias: busca atual com semântica LIKE, filtros por status/Área, contagens DISTINCT e ordenação nome/ID.
- Assuntos: busca atual com semântica LIKE, filtros por status/Área/Matéria, contagem de Questões e ordenação nome normalizado/ID.
- Questões: busca atual literal com escape de curingas (`contains(..., autoescape=True)`), filtros atuais e ID decrescente. Não unificar seu comportamento de busca ao LIKE de Matérias/Assuntos.
- Paginação: mesmo padrão/máximo validado nos Services, total independente da página, página fora do intervalo com itens vazios e total correto.
- Desempenho: usuário da sessão, intervalo UTC `[inicio, fim)`, fatos históricos, exclusão de brancos e de tentativas abertas, uma contribuição por origem/registro, mesmos desempates de rótulos e contagens. Percentuais/estados da amostra continuam no Service.
- Atividades: cinco por instante/tipo/ID decrescentes, incluindo Simulado finalizado sem respostas; destinos continuam no Service.
- Plano: recebe o mesmo diagnóstico no ContextoLeitura e instante fornecidos pela transação externa; nenhuma confirmação ou troca de conexão é permitida.

## Consultas que continuam pendentes após esta etapa

| Família | Exemplos existentes a tratar em changes posteriores |
|---|---|
| Seletores/consulta especializada em Models | `Materia.listar_ativos`, `AreaEnem.listar_ordenadas`, `Assunto.listar_ativos` → Repository; não confundir esses filtros/ordenações com `listar_todos` básico |
| Catálogo e editorial | impactos, assuntos ativos, equivalência por nome/Matéria, histórico de versões, elegibilidade individual/em lote e locks |
| Práticas | histórico filtrado/paginado e consultas de propriedade/replay |
| Simulados | catálogo, composição, andamentos, respostas, histórico e consultas de propriedade/replay |
| Plano | seleção de pares elegíveis, plano atual/itens/replay e eliminação especializada já governada |
| Contas | consultas especializadas de sessão, limites e privacidade; avaliar por caso de uso, preservando os controles de segurança |

A presença dessas pendências não é corrigida por documentação nem por uma única procedure demonstrada. O CRUD básico permanece nas Models; as mudanças futuras devem manter transações e segurança e passar pelo workflow próprio.
