# Inventário — Contas e Privacidade

Levantamento estático do código em 07/11/2026. Recursos abaixo são planejados, não implementados. Dependência: `adequar-plano-estudos-a-procedures`; prefixo anterior 015; nova migration `016_contas_privacidade_procedures.sql`.

## Correspondência fechada

Cada nome da tabela é uma procedure específica; parâmetros IN seguem a ordem indicada.

| Método/fonte atual | Procedure prevista | Parâmetros, na ordem | Resultado e semântica |
|---|---|---|---|
| `Usuario.buscar_por_email (delegação)` | `sp_usuario_por_email` | email | Usuário completo interno, mesma normalização no Service e collation utf8mb4_bin |
| `AutenticacaoRepository.consultar_sessao` | `sp_consultar_sessao` | identificador_hash | linhas de LEFT JOIN Sessão/Usuário completas com aliases explícitos, sem filtro novo de ativo |
| `AutenticacaoRepository.renovar_acesso` | `sp_renovar_acesso_sessao` | sessao_id, agora | UPDATE condicional atual; uma linha correspondencias, preservar retorno booleano |
| `AutenticacaoRepository.revogar` | `sp_revogar_sessao` | sessao_id, agora | UPDATE somente não revogada; uma linha afetadas, adaptador preserva retorno atual |
| `AutenticacaoRepository.revogar_usuario` | `sp_revogar_sessoes_usuario` | usuario_id, agora | UPDATE de sessões não revogadas do dono; uma linha afetadas |
| `AutenticacaoRepository.usuario_ativo_bloqueado` | `sp_usuario_ativo_bloqueado` | usuario_id | Usuário ativo completo FOR UPDATE |
| `AutenticacaoRepository.limite_bloqueado` | `sp_preparar_limite_autenticacao` | chave_hash, agora | upsert idempotente da chave e SELECT completo FOR UPDATE |
| `AutenticacaoRepository.limpar` | `sp_limpar_autenticacao` | agora | DELETE especializado pelos mesmos cortes; uma linha sessoes/limites |
| `PrivacidadeRepository.bloquear_usuario` | `sp_bloquear_identidade_privacidade` | usuario_id | somente ID com FOR UPDATE, sem filtrar ativo |
| `PrivacidadeRepository.ultimas` | `sp_ultimas_decisoes_privacidade` | usuario_id | um conjunto com até duas evidências completas, uso → plano; duas capturas sequenciais por ID desc FOR UPDATE, omitindo tipos ausentes; entidades gerenciadas |
| `PrivacidadeRepository.por_chave` | `sp_decisao_privacidade_por_chave` | usuario_id, chave | evidência própria completa FOR UPDATE |

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
