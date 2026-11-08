# Inventário — Plano de Estudos

Levantamento estático do código em 07/11/2026. Recursos abaixo são planejados, não implementados. Dependência: `adequar-praticas-simulados-a-procedures`; prefixo anterior 014; nova migration `015_plano_estudos_procedures.sql`.

## Correspondência fechada

Cada nome da tabela é uma procedure específica; parâmetros IN seguem a ordem indicada.

| Método/fonte atual | Procedure prevista | Parâmetros, na ordem | Resultado e semântica |
|---|---|---|---|
| `PlanoEstudoRepository.atual` | `sp_plano_atual` | usuario_id, bloquear | plano atual completo, FOR UPDATE opcional |
| `PlanoEstudoRepository.por_chave` | `sp_plano_por_chave` | usuario_id, chave | plano próprio completo FOR UPDATE |
| `PlanoEstudoRepository.itens` | `sp_plano_itens` | plano_id | itens completos por posição FOR UPDATE |
| `PlanoEstudoRepository.item_proprio` | `sp_plano_item_proprio` | usuario_id, item_id | uma linha JOIN com Item/Plano completos e aliases explícitos, sob locks equivalentes ao JOIN atual |
| `QuestaoRepository.pares_elegiveis_plano (proprietário Conteúdo)` | `sp_pares_elegiveis_plano` | assunto_ids_json, bloquear | pares assunto_id/materia_id elegíveis; FOR SHARE opcional, preservando igualdade entre vínculo atual e snapshot |
| `PlanoEstudoRepository.eliminar_planos_proprios` | `sp_eliminar_planos_proprios` | usuario_id | DML especializado participante; uma linha planos_eliminados/itens_eliminados |

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
