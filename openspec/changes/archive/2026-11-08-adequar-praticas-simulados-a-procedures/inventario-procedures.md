# Inventário — Práticas e Simulados

Levantamento estático do código em 07/11/2026. Recursos abaixo são planejados, não implementados. Dependência: `adequar-catalogo-editorial-a-procedures`; prefixo anterior 013; nova migration `014_praticas_simulados_procedures.sql`.

## Correspondência fechada

Cada nome da tabela é uma procedure específica; parâmetros IN seguem a ordem indicada.

| Método/fonte atual | Procedure prevista | Parâmetros, na ordem | Resultado e semântica |
|---|---|---|---|
| `PraticaRepository.por_chave` | `sp_pratica_por_chave` | usuario_id, chave, bloquear | tentativa própria completa; FOR UPDATE opcional |
| `PraticaRepository.propria` | `sp_pratica_propria` | usuario_id, tentativa_id, bloquear | tentativa própria completa; FOR UPDATE opcional |
| `PraticaRepository.historico` | `sp_praticas_historico` | usuario_id, assunto_id opcional, pagina, limite | respondidas, resposta/ID decrescentes; segundo conjunto total |
| `PraticaRepository.fatos` | `sp_praticas_fatos` | usuario_id, inicio, fim | tentativas respondidas completas; resposta/ID crescentes |
| `SimuladoRepository.bloquear` | `sp_bloquear_simulado` | simulado_id | Simulado completo FOR UPDATE |
| `SimuladoRepository.itens` | `sp_simulado_itens` | simulado_id opcional, versao_id opcional | ramo rascunho ou versão conforme chamada atual; posicao crescente |
| `SimuladoRepository.itens_em_lote` | `sp_simulados_itens_lote` | simulado_ids_json opcional, versao_ids_json opcional | itens completos agrupáveis por identidade e posição |
| `SimuladoRepository.andamentos_em_lote` | `sp_simulados_andamentos_lote` | usuario_id, versao_ids_json | tentativas próprias em andamento |
| `SimuladoRepository.titulos_em_lote` | `sp_simulados_titulos_lote` | versao_ids_json | pares id/titulo da versão |
| `SimuladoRepository.listar` | `sp_simulados_listar` | pagina, limite, estado opcional | Simulados por ID decrescente; segundo conjunto total |
| `SimuladoRepository.propria` | `sp_simulado_tentativa_propria` | usuario_id, tentativa_id, bloquear | tentativa própria completa; FOR UPDATE opcional |
| `SimuladoRepository.por_chave` | `sp_simulado_tentativa_por_chave` | usuario_id, chave | tentativa própria completa FOR UPDATE |
| `SimuladoRepository.andamento` | `sp_simulado_em_andamento` | usuario_id, versao_id | tentativa própria em andamento FOR UPDATE |
| `SimuladoRepository.respostas` | `sp_simulado_respostas` | tentativa_id, bloquear | pares Resposta/Item completos, ordem posicao, FOR UPDATE opcional |
| `SimuladoRepository.historico` | `sp_simulados_historico` | usuario_id, pagina, limite | finalizadas, finalização/ID decrescentes; segundo conjunto total |
| `SimuladoRepository.fatos` | `sp_simulados_fatos` | usuario_id, inicio, fim | triplas Resposta/Item/Tentativa finalizada não branca, instante/Resposta.id crescentes |

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
