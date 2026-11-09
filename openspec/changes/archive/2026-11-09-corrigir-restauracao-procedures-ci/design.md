# Design

## Context

Ver [causa e execuções](proposal.md). O traceback falha no `finally` de testes que removem routines para comprovar erro seguro da aplicação. No Linux/CI, o DDL inclui `DEFINER=...@'%'`; SQLAlchemy entrega parâmetros vazios ao PyMySQL, que interpreta `%` como marcador. A restauração não termina e contamina os casos seguintes do schema descartável.

A reprodução local, sem conexão MySQL, confirmou exatamente `ValueError: unsupported format character` no índice 24 para `cursor.mogrify(ddl,{})`; `cursor.mogrify(ddl)` preserva o mesmo texto. O ambiente da apresentação não foi alterado na investigação.

## Goals / Non-Goals

**Goals:** restaurar DDL literal de forma portátil e manter os testes de ausência de routines íntegros.

**Non-Goals:** alterar produção/migrations, criar conta MySQL com host especial, enfraquecer testes, mudar permissões, ocultar falhas ou publicar sem autorização.

## Decisions

Nas três restaurações identificadas, usar `exec_driver_sql(original, execution_options={"no_parameters": True})`. A opção faz SQLAlchemy chamar `cursor.execute(statement)` sem a tupla/dicionário vazio. Ela vale somente para DDL literal controlado do teste; consultas parametrizadas da aplicação permanecem como estão.

Acrescentar regressão MySQL real no suporte de testes existente, em schema descartável: criar routine cujo corpo devolva textos literais `100% ENEM` e `%s`, obter seu DDL, removê-la, restaurá-la sem parâmetros e conferir os valores retornados. Isso reproduz o risco também com definer local sem `%`, sem exigir usuário global ou privilégio para forjar outro definer. Garantir limpeza em `finally` e recuperação após resultado/erro.

Não substituir `%` no texto, retirar o `DEFINER` nem desativar os testes. Essas alternativas alterariam o objeto restaurado ou deixariam a causa sem prova. DDL e resultado devem permanecer semanticamente idênticos.

Registrar a regressão junto da correção e executar primeiro os três testes afetados, depois o conjunto relacionado necessário. Não há motivo para reexecutar Gemini real, alterar banco operacional ou revisar migrations já aplicadas. Evidência local não equivale a nova execução verde no GitHub; essa confirmação depende de publicação autorizada e do workflow posterior.

## Risks / Trade-offs

- Chamada sem parâmetros em SQL que precisasse de binds → limitar a opção às restaurações literais e testar `%s` como texto, sem estender para consultas de produção.
- Teste antigo deixa routine ausente após erro → a correção precisa preservar `finally`, e os testes seguintes devem conseguir consultar o domínio normalmente.

## Migration Plan

Nenhuma migration. Mudança apenas em testes, isolada das alterações legítimas locais. Após validação/aplicação, seguir verify/sync/archive; não há delta funcional para sincronizar. Commit/push exigem autorização explícita e somente um novo run comprova o resultado remoto.
