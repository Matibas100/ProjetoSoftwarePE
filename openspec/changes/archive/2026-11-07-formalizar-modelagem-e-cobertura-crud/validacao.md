# Validação — Modelagem e cobertura CRUD

Revisão local de 07/11/2026. Change exclusivamente documental, sem execução de integração, cobertura, E2E, migrations ou acesso ao banco.

## 1. Estado inicial (tarefa 1.1)

Preflight somente leitura: AGENTS.md, cinco conventions, arquitetura mestre, ADRs 003/008/009/010, proposal/design/tasks/levantamento, Models, bases, Blueprints, Controllers/Services e HTML/JavaScript do recorte.

`git status --short` inicial: apenas esta change e `tmp/` não rastreados; nenhum arquivo rastreado alterado. `tmp/` já existia e foi preservado.

| Documento | SHA-256 inicial |
| --- | --- |
| `docs/technical/modelagem-de-dominio.md` | Inexistente |
| `docs/technical/matriz-crud.md` | Inexistente |
| `docs/technical/diagrama-de-classes.md` | `8d204d28b487fc73addb271a515bd3e191422bf0b925f59356b002affd60576a` |
| `docs/technical/entrega-academica.md` | `c480bd9c83bd3554ccfd52473a3714ba3b7cf4644b82a9b3b4f857dd3e8cc5f5` |
| `README.md` | `5fde176b354a11c87aa234beb101bee1306c3656bc07297f512105d098ab40e7` |

A [referência inicial](referencia-inicial.json) conserva hashes, títulos e os doze blocos Mermaid originais, vinte funcionalidades do README e vinte linhas/IDs da matriz acadêmica. Contém somente metadados e trechos técnicos selecionados desses documentos do repositório; nenhum conteúdo de `.env`, configuração sensível ou dado pessoal real foi copiado. Nomes de atributos de hash não são seus valores.

## 2. Inventário estrutural (tarefa 1.2)

Resultado: **21 mappers**, com **13 CrudMixin, 2 ModeloAtualizavel e 6 ModeloBase**, distribuídos em Contas 4, Conteúdo 7, Práticas 1, Simulados 7, Desempenho 0 e Plano 2. **67 regras de API** (método/caminho, excluindo HEAD/OPTIONS e rota estática), resolvidas para Controllers existentes. Todas as FKs inspecionadas usam RESTRICT.

Factory inicializada com URI MySQL sintética em porta 1, chave sintética hexadecimal, `.env` desabilitado por variável e patch de `dotenv.load_dotenv`. `Engine.connect` e `pymysql.connect` bloqueados com AssertionError durante import/composição/inspeção; nenhuma chamada HTTP nem consulta foi executada. A primeira tentativa usou chave sintética fora do formato e foi rejeitada pela validação local; a repetição com 64 caracteres hexadecimais passou. Nenhuma conexão foi tentada.

Conferência com `levantamento-crud.md`: nenhuma divergência de inventário ou exposição encontrada. GET individual de Matéria/Assunto e DELETE de Questão/Simulado não existem; não há CRUD de gestão de contas. `Usuario.campos_atualizaveis` contém apenas ativo/senha_hash. A navegação marca Usuários indisponível. Os guards de versões/eventos/evidências e de plano permanecem. O ADR-009 descreve o proprietário anterior da eliminação; aplica-se o adendo do ADR-010: execução em Plano, injetada nas negativas de Contas.

Comandos de leitura: `rg -n` para classes/campos/FKs/guards, Controllers/Services e ações HTML/JS; `Get-Content -Encoding utf8` nos artefatos e fontes; Python da `.venv` para factory, mappers, métodos, campos permitidos, FKs e `app.url_map`. Globs e dois nomes de JS supostos não resolveram no Windows; a inspeção seguiu pelos caminhos reais descobertos no repositório. Não foram falhas da aplicação.

Método herdado confirma capacidade Python, sem comprovar autorização, fluxo HTTP ou persistência real. Evidências históricas de integração/E2E continuam nos relatórios já referenciados pela matriz acadêmica; não foram reexecutadas nem herdadas por esta change.

### Reprodução da inspeção sem SQL

Na raiz, executar o trecho abaixo com o Python da `.venv` (por exemplo, enviar
o here-string PowerShell ao comando `.\.venv\Scripts\python.exe -`). Todos os
valores são sintéticos e restritos ao processo; nenhuma configuração é impressa.
O bloqueio serve exclusivamente à inspeção estrutural, sem substituir integrações.

```python
import os, sys
from collections import Counter
from unittest.mock import patch
os.environ.update(
    PYTHON_DOTENV_DISABLED="1",
    DATABASE_URL="mysql+pymysql://inspecao:inspecao@127.0.0.1:1/inspecao_documental",
    AUTH_SECRET_KEY="1" * 64,
)
sys.path.insert(0, "backend")
with patch("dotenv.load_dotenv", return_value=False), \
     patch("sqlalchemy.engine.Engine.connect", side_effect=AssertionError("SQL proibido")) as sql, \
     patch("pymysql.connect", side_effect=AssertionError("MySQL proibido")) as mysql:
    from app import create_app
    from app.extensions import db
    class ConfigInspecao:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        AUTH_SECRET_KEY = os.environ["AUTH_SECRET_KEY"]
        AUTH_COOKIE_SECURE = False
        CORS_ORIGINS = []
    app = create_app(ConfigInspecao)
    mappers = sorted(db.Model.registry.mappers, key=lambda m: m.class_.__name__)
    print(len(mappers), Counter(m.class_.__bases__[0].__name__ for m in mappers))
    for m in mappers:
        print(m.class_.__name__, m.class_.__module__, m.local_table.name,
              [n for n in ("salvar", "listar_todos", "buscar_por_id", "atualizar", "deletar")
               if hasattr(m.class_, n)])
        print([(f.parent.name, f.target_fullname, f.parent.nullable, f.ondelete)
               for f in sorted(m.local_table.foreign_keys, key=lambda f: f.parent.name)])
    for r in sorted(app.url_map.iter_rules(), key=lambda r: (r.rule, sorted(r.methods))):
        if r.rule.startswith("/api"):
            print(sorted(r.methods - {"HEAD", "OPTIONS"}), r.rule,
                  app.view_functions[r.endpoint].__qualname__)
    assert sql.call_count == mysql.call_count == 0
```

## 3. Conferência dos documentos (tarefas 2.1–4.1)

O [resultado estruturado](conferencia-estrutural.json) registra os 21 mappers
(classes canônicas, bases, tabelas, métodos, campos declarados, colunas/FKs),
as 67 regras HTTP e os hashes finais dos cinco documentos. Não contém dados
de aplicação, credenciais ou configuração operacional.

| Verificação | Resultado |
| --- | --- |
| Modelagem de domínio | Contexto/data atual, glossário, seis módulos e 21 linhas conferidas com AST/mappers; Desempenho permanece projeção sem Model. |
| Matriz CRUD | Seis recursos centrais + quinze outras Models, nomes únicos e caminhos canônicos correspondentes aos mappers; bases C/U/B conferidas. Classes de Controller/Service/Repository citadas existem na AST de `backend/app`. |
| Métodos e interface | Separados persistência, API e UI; campos ausentes não tratados como atualização genérica; ações conferidas nos HTML/JS, incluindo histórico de Simulados na própria tela de Simulados. Não houve execução de navegador. |
| Pendências | D01 resolvida documentalmente; F01/F02 abertas para changes próprias; E01–E03 explicitam diferenças e aceitação acadêmica pendente. Aceite com FK RESTRICT/guard de Usuário documentado, sem política nova de retenção/exclusão. |
| Diagrama e relações | 152 atributos concretos conferidos com colunas ORM (abreviação de alternativas expandida); 43 FKs correspondem às 43 associações e cardinalidades de opcionalidade, todas RESTRICT. Heranças correspondem às bases inspecionadas. |
| Preservação das visões | Os doze blocos iniciais passaram a treze: a visão de privacidade foi dividida. Comparação por multiconjunto de linhas Mermaid, desconsiderando apenas linhas vazias, `classDiagram` e `direction LR`: classes, atributos, métodos, heranças e relações/cardinalidades idênticos. Todos os títulos anteriores continuam, com nível ajustado e âncoras preservadas. |
| Mermaid disponível | `Get-Command mmdc, mermaid`, `Test-Path node_modules/mermaid` e busca de arquivos Mermaid não localizaram parser/renderizador disponível. Python conferiu cercas, cabeçalho `classDiagram`, chaves/aspas balanceadas, declarações e relações. Não houve parse formal ou renderização visual; nenhuma dependência foi instalada. |
| Links | 252 links locais nos cinco documentos resolvidos; arquivos/diretórios existem e fragmentos Markdown/IDs HTML correspondem aos destinos. Links externos históricos não foram consultados nem revalidados. |
| Vinte funcionalidades | Lista numerada do README e vinte linhas completas da matriz acadêmica idênticas à referência inicial, incluindo IDs, textos, rotas e evidências. Nenhuma funcionalidade nova contabilizada. |
| Privacidade do plano | Recálculo preserva gerações durante autorização; negativa confirmada elimina derivados próprios via participante de Plano injetado em Contas, mantendo respostas, evidências e outra conta, conforme ADRs 009/010. |

As conferências documentais usaram Python da `.venv`: `ast.parse` para classes,
`re` para inventários/blocos/links, `Counter` para declarações antes/depois,
metadata ORM para colunas/FKs/opcionalidade, comparação literal das vinte linhas
e SHA-256 dos cinco documentos. As checagens foram executadas por stdin, sem
criar scripts no código de produção. A checagem de links considera headings e
IDs explícitos locais; não substitui teste em um renderizador de Markdown.

## 4. Fechamento e escopo (tarefa 5.1)

Comandos executados a partir da raiz:

```powershell
openspec validate formalizar-modelagem-e-cobertura-crud --strict
git diff --check
git diff --name-only
git diff --stat
git diff -- README.md docs/technical/entrega-academica.md
git status --short
```

- OpenSpec estrito: change válida; `skip_specs: true` aceito, sem deltas funcionais.
- `git diff --check`: sem erros. Arquivos novos também conferidos para whitespace,
  UTF-8 válido e ausência de caracteres de substituição.
- Diff rastreado restrito a README, diagrama e entrega acadêmica; arquivos novos:
  modelagem e matriz CRUD, mais artefatos desta change. `tmp/` anterior preservado.
  O diff das inserções no README/entrega não altera as listas oficiais.
- Código, contratos, specs principais, schema, migrations, SQL, dependências e
  visuais oficiais sem alterações. Nenhum commit, push, merge, envio ou aprovação
  externa foi realizado. Não foram executados cobertura, E2E ou operações de banco.

Os resultados são estruturais/documentais. Permanecem a limitação de Mermaid
sem renderização, as lacunas F01/F02 e a avaliação acadêmica de E01–E03; elas não
são tratadas como implementações concluídas ou dispensas concedidas.

## 5. Verificação e arquivamento — 07/11/2026

A verificação posterior ao apply confirmou 8/8 tarefas, 21 Models (13/2/6),
67 regras de API, 152 atributos, 43 FKs, declarações dos treze blocos Mermaid
preservadas, 252 links e vinte funcionalidades/IDs intactos. OpenSpec estrito
e `git diff --check` passaram; nenhuma conexão SQL foi tentada. Não houve achado
crítico. Permanece a limitação de Mermaid sem renderização.

Arquivamento autorizado pelo usuário e realizado pelo CLI:

```powershell
openspec archive formalizar-modelagem-e-cobertura-crud --skip-specs --yes --json
```

Destino: `openspec/changes/archive/2026-11-07-formalizar-modelagem-e-cobertura-crud/`.
Não há delta funcional a sincronizar (`skip_specs: true`); specs principais
preservadas. O link da matriz CRUD foi ajustado para este destino. O resultado
estrutural conserva os hashes anteriores ao arquivamento e atualiza o hash final
da matriz após esse ajuste. A change externa
`adequar-consultas-academicas-a-procedures` e `tmp/` foram preservados.
Nenhum commit, push ou merge foi realizado.
