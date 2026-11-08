# Inventário — Catálogo e Questões editoriais

Levantamento estático do código em 07/11/2026. Recursos abaixo são planejados, não implementados. Dependência: `adequar-consultas-academicas-a-procedures`; prefixo anterior 012; nova migration `013_catalogo_editorial_procedures.sql`.

## Correspondência fechada

Cada nome da tabela é uma procedure específica; parâmetros IN seguem a ordem indicada.

| Método/fonte atual | Procedure prevista | Parâmetros, na ordem | Resultado e semântica |
|---|---|---|---|
| `AreaEnem.listar_ordenadas` | `sp_areas_enem_ordenadas` | nenhum | Área completa; ordem/ID |
| `Materia.listar_ativos` | `sp_materias_ativas` | nenhum | Matéria completa; nome/ID |
| `CatalogoRepository.listar_assuntos_ativos` | `sp_assuntos_ativos` | materia_id opcional | Assunto completo; JOIN Matéria ativa; nome_normalizado/ID |
| `CatalogoRepository.impacto_materia` | `sp_impacto_materia` | materia_id | uma linha: assuntos, questoes, transferencias |
| `CatalogoRepository.impacto_assunto` | `sp_impacto_assunto` | assunto_id | uma linha: questoes, transferencias |
| `CatalogoRepository.contar_assuntos_nao_arquivados` | `sp_assuntos_nao_arquivados` | materia_id | uma linha: total |
| `CatalogoRepository.buscar_assunto_para_atualizacao; QuestaoRepository.bloquear_classificacao (primeiro passo)` | `sp_bloquear_assunto` | assunto_id | Assunto completo FOR UPDATE |
| `CatalogoRepository.buscar_materias_para_atualizacao; QuestaoRepository.bloquear_classificacao (segundo passo)` | `sp_bloquear_materias` | ids_json | Matérias completas por ID crescente FOR UPDATE |
| `CatalogoRepository.existe_assunto_equivalente` | `sp_assunto_equivalente` | materia_id, nome_normalizado, ignorar_id opcional | uma linha: existe; mesmo predicado/collation |
| `QuestaoRepository.bloquear` | `sp_bloquear_questao` | questao_id | Questão completa FOR UPDATE, atualizar estado do identity map |
| `QuestaoRepository.versoes` | `sp_versoes_questao` | questao_id | versões completas, numero crescente |
| `QuestaoRepository.versao_elegivel` | `sp_questao_versao_elegivel` | versao_id, bloquear | versão completa elegível, FOR UPDATE somente se solicitado |
| `QuestaoRepository.listar_elegiveis` | `sp_questoes_elegiveis` | assunto_id opcional, materia_id opcional, pagina, limite | versões elegíveis ordenadas por questao_id; segundo conjunto com total |
| `QuestaoRepository.versoes_elegiveis` | `sp_questoes_versoes_elegiveis` | ids_json | versões elegíveis sem duplicação por ID |
| `QuestaoRepository.versoes_historicas` | `sp_questoes_versoes_historicas` | ids_json | versões históricas publicadas, sem filtros atuais de disponibilidade |

## Tipos e resultados

- IDs e paginação: BIGINT UNSIGNED, preservando IDs reais e filtros positivos acima de 2^31 já aceitos. IDs opcionais usam NULL sem converter consulta em leitura irrestrita.
- `limite`: INT, com os mesmos padrões/máximo de 100 nas listagens; flags de lock: TINYINT, apenas 0/1. Validações HTTP existentes permanecem no Service.
- `chave`: CHAR(36) ascii_bin para UUID; `chave_hash` e `identificador_hash`: CHAR(64) ascii_bin; `email`: VARCHAR(254) com comparação utf8mb4_bin; `nome_normalizado`: VARCHAR(150) com a collation atual de Assunto, sem normalização SQL alternativa.
- `inicio`, `fim` e `agora`: DATETIME(6), recebidos do relógio/contexto atual, sem NOW paralelo. `estado`: VARCHAR(20), validado pelos valores do fluxo existente.
- Listas de IDs: JSON, convertido em relação por JSON_TABLE dentro da routine; deduplicar IDs para reproduzir IN, preservar ordem explícita quando existente e manter lista vazia como resultado vazio. Não interpolar CSV/SQL nem introduzir limite novo de lote sem change.
- Colunas explícitas, completas para mapeamento ORM e com aliases não ambíguos em JOIN. Leituras de apresentação podem usar registros/DTOs; leituras que serão alteradas permanecem entidades gerenciadas. Não criar objetos ORM transientes para simular linhas persistidas.
- Em resultados de página, a linha de total é separada das linhas da página; vazios úteis são preservados. Conjuntos terminais sem colunas são drenados e descartados.
- Uma linha agregada sem ocorrências retorna zero nas contagens. Consulta individual ausente retorna zero linhas; adaptador mantém None/404/409 atual, sem inventar entidade.
- Comandos auxiliares não viram rotas nem funcionalidades novas. O Controller continua relacionado ao recurso existente, e cada Service mantém seu caso de uso.
- Cada procedure usa SQL SECURITY INVOKER; READS SQL DATA nas leituras e MODIFIES SQL DATA somente nas operações de escrita explicitamente listadas. Nenhuma rotina confirma, reverte ou inicia transação.

## Limites da divisão

As rotinas da primeira etapa não são recriadas. Projeções Python de compatibilidade que apenas constroem consultas, sem execução, devem ser rastreadas até consumidores: migrar o caminho executável especializado para CALL ou comprovar que a projeção foi substituída pelas views públicas; não usar fallback ORM para disfarçar uma lacuna. O método `pares_elegiveis_plano` pertence à change de Plano (015), embora implementado no Repository de Conteúdo. O lock de identidade de Contas pertence à 016 e continua sendo consumido pela API pública antes disso.

Consultar o design para preservação de locks, hidratação/identity map, escrita especializada e verificações específicas. Não afirmar conformidade integral pelo simples número de procedures.
