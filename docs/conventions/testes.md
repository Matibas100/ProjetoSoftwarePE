# Testes e validação

## Regra central

Os testes existentes são de integração contra o MySQL real configurado pelo `.env`. Não use mocks nem SQLite para substituir essa validação.

## Regressão atual

| Recurso | Testes |
|---|---:|
| Matéria | 7 |
| Assunto | 10 |
| Questão | 12 |
| Total | 29 |

Execução completa:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Regras para changes

- Durante o apply, rode primeiro a menor validação que prove a tarefa.
- Antes de concluir uma mudança de backend, execute a regressão afetada e, quando aplicável, a suíte completa.
- Testes devem criar e limpar seus próprios dados temporários.
- Não leia nem mostre o conteúdo do `.env`.
- Não declare sucesso quando o MySQL estiver indisponível.
- Mudança somente documental ou de configuração não exige executar a suíte da aplicação.
- Registre no fechamento comandos, resultados e limitações reais.
