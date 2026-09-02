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
