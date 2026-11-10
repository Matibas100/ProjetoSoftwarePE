# Análise inicial do volume do projeto

Levantamento de 09/11/2026, no commit `663891a`. Esta análise acompanha a proposta de formatação e não autoriza simplificar ou excluir componentes. Contagens referem-se a arquivos-fonte versionados, não ao tamanho do banco em uso. Não houve consulta a credenciais ou medição de dados de usuários.

## O que os números mostram

- `backend/app/`: **192 arquivos Python e 6.474 linhas**. **161 arquivos têm até 60 linhas**; a mediana é 26 linhas. Há **42 `__init__.py`** usados para a organização dos pacotes.
- Entre esses arquivos, 73 ficam em pastas de Services, 21 em Controllers, 21 em Models, 22 em Repositories e 7 em contratos. São contagens de arquivos, incluindo inicializadores; não equivalem a quantidades de classes ou funcionalidades.
- A aplicação registra **21 Models/tabelas de domínio**. Sessões, versões, itens, respostas e evidências também ocupam tabelas, além das entidades mais visíveis nas telas.
- Testes próprios têm **9.696 linhas Python e 4.328 linhas JavaScript**. Esse material aumenta o repositório, mas não integra a execução normal de uma funcionalidade.
- `backend/database/create_database.sql` tem **1.948 linhas**, com 21 criações de tabela e 58 declarações de procedure. Existem **18 migrations**, de 000 a 017. O bootstrap descreve a instalação consolidada; as migrations guardam a evolução. Não se executam os dois como uma sequência duplicada de alterações.

O tamanho de um SQL de instalação não informa quantos registros existem nem quanto espaço o banco ocupa. Também não é possível concluir que os outros grupos estão melhores ou piores sem comparar requisitos, entregas e decisões.

## Para que servem os arquivos que parecem extras

| Parte | Função atual | Avaliação para agora |
| --- | --- | --- |
| [package.json](../../../../package.json) | Comandos e dependências do frontend/testes | Pequeno e necessário à execução das ferramentas atuais |
| [package-lock.json](../../../../package-lock.json) | Versões exatas das dependências e suas dependências | Gerado automaticamente; não é código de negócio para explicar linha a linha |
| `coverage-backend.json` | Relatório local de cobertura, cerca de 4,26 MB neste levantamento | Gerado e ignorado pelo Git; não é código da aplicação. Não foi lido ou apagado |
| [sql_resources_reference.json](../../../../backend/database/sql_resources_reference.json) | Assinaturas das procedures/views usadas pela verificação de integridade | Usado em runtime pela ferramenta do banco; não excluir como se fosse relatório |
| JSON em `openspec/changes/archive/` | Evidências e comparações de trabalhos anteriores | Histórico; não é carregado pela interface durante o estudo |
| `node_modules/` e `.venv/` | Bibliotecas instaladas | Não foram escritas pelo grupo; não contabilizar como código próprio |
| `tmp/`, `output/` e capturas | Apoio local e propostas de imagem | Não são funcionalidades do sistema; não limpar nesta change |
| `composition.py` e `contracts/` | Ligação dos colaboradores e definição dos contratos internos | Mais avançados que o CRUD básico; têm função atual, embora a disciplina não exija cada arquivo pelo nome |
| `transaction_manager.py` e `contexto_leitura.py` | Confirmação/rollback de ações compostas e leitura consistente | Protegem resultados e dados; retirar exige reavaliar transações, não apenas apagar arquivos |

## Onde há complexidade real

Nem todo o volume é inevitável ou exigido literalmente pelo professor. O runner próprio e o reconhecimento de todos os estados históricos do banco são mais sofisticados que um exemplo inicial de Flask/SQLAlchemy. A arquitetura modular, os contratos e as verificações ampliadas também acrescentam conceitos para a equipe compreender.

O maior arquivo Python de produção é [legacy_schema.py](../../../../backend/database/legacy_schema.py), com **730 linhas**, seguido de [migrate.py](../../../../backend/database/migrate.py), com **535**. Ambos tratam instalação/evolução do banco; não são o percurso normal Controller → Service → Model/Repository de cada ação.

Na interface, [admin-assuntos.js](../../../../frontend/js/admin-assuntos.js), com **382 linhas**, reúne listagem, edição, estados, impacto e transferência. [admin-materias.js](../../../../frontend/js/admin-materias.js) tem **301**. Há comportamento real aí; só contar linhas não demonstra redundância.

Também permanece uma interface antiga em [index.html](../../../../frontend/index.html), com scripts próprios, ao lado das páginas administrativas atuais. Há uma possível duplicação de experiência, mas links e testes existentes ainda a utilizam; sua retirada não seria uma limpeza pequena e independente.

## Caminho recomendado

1. **Agora:** formatar e separar visualmente os blocos, preservando o sistema e a preparação da apresentação. Isso pode aumentar linhas e diminuir a dificuldade de leitura.
2. **Depois da formatação:** avaliar repetições concretas nos JavaScripts administrativos. Extrair algo só se a regra for de fato a mesma e a explicação ficar mais simples; já existe `admin-common.js`, portanto não criar outra camada por hábito.
3. **Outro momento:** considerar retirar a interface antiga após migrar links e demonstrações; avaliar manutenção da ferramenta de migrations com backup e testes próprios. Não trocar essa infraestrutura perto da entrega apenas para reduzir quantidade de arquivos.

Não há evidência neste levantamento de que seja seguro apagar classes, tabelas ou validações em bloco. Há evidência de formatação irregular e de volume significativo de testes, histórico e infraestrutura. O primeiro ajuste tem escopo claro; simplificações precisam de exemplos e comprovação antes/depois.
