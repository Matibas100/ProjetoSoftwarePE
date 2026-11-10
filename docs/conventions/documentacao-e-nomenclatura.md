# Documentação e nomenclatura

## Idioma e codificação

- Use português brasileiro em texto natural.
- Preserve termos técnicos, comandos, rotas e identificadores na grafia contratual.
- Keywords normativas de specs, como `SHALL`, `MUST`, `WHEN` e `THEN`, permanecem em inglês.
- Preserve UTF-8, acentos e cedilha.

## Nomes

- Changes, capabilities e diretórios estruturais novos usam `kebab-case`.
- Python importável usa `snake_case.py`; classes usam `PascalCase`.
- Preserve nomes impostos como `README.md`, `AGENTS.md`, `.env.example`, `proposal.md`, `design.md`, `tasks.md` e `spec.md`.
- Não renomeie legado sem escopo aprovado.

## Documentação

- `docs/conventions/` contém regras normativas de trabalho.
- `docs/technical/` preserva arquitetura, decisões e planejamento técnico.
- `docs/design/desktop-v1/` permanece congelado; não altere os quatro binários oficiais.
- Evite duplicar uma fonte de verdade; prefira links relativos.
- Use tabelas para comparações e mapeamentos, e diagramas ASCII somente quando simplificarem relações.

## Git e temporários

- Use Conventional Commits em português quando um commit for autorizado.
- Não misture mudanças sem relação no mesmo commit.
- Arquivos temporários, caches, `.env` e credenciais não são versionados.

## Formatação do código

- Python usa 4 espaços; JavaScript, CSS, HTML e SVG usam 2 espaços.
- Separe instruções e blocos para facilitar a leitura; use uma declaração CSS por linha e linhas em branco entre regras, métodos e declarações de topo.
- Prefira linhas de aproximadamente 100 caracteres quando a quebra for segura. Não há obrigação de reduzir linhas nem de reescrever arquivos já legíveis.
- Preserve nomes, imports, comentários, diretivas, aspas, literais e ordem de operações, atributos e propriedades. Formatar não autoriza refatorar.
- Preserve espaços significativos em HTML, conteúdo de `pre`/`textarea`, scripts, templates, regexes, URLs, SQL embutido e valores CSS; esses trechos podem permanecer longos.
- Preserve UTF-8 e os finais de linha existentes. Este padrão não exige ferramenta, dependência, configuração ou gate novo.
