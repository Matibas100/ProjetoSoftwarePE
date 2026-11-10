# Proposta: padronizar a formatação do código

## Why

O código atual funciona e segue a arquitetura adotada, mas sua apresentação mistura blocos bem formatados com instruções, tags e declarações compactadas. A equipe precisa ler e explicar os arquivos com mais facilidade, preservando a versão validada e o prazo de apresentação.

## What Changes

- Revisar a formatação dos arquivos de código próprios e versionados: Python da aplicação, operação do banco e testes; HTML/CSS/JavaScript do frontend; scripts e configurações de teste existentes.
- Aplicar indentação consistente, espaços, linhas em branco e quebras de linha, incluindo uma instrução por linha quando isso preservar a estrutura do programa.
- Manter arquivos já legíveis sem alterações desnecessárias; a lista de arquivos elegíveis não obriga reescrever todos eles.
- Documentar o padrão adotado em uma seção curta da convenção existente de documentação e nomenclatura.
- Verificar equivalência estrutural e executar a regressão existente. A formatação pode aumentar o número de linhas; o objetivo é leitura, não reduzir artificialmente o tamanho.

### Limites

Não renomear variáveis/classes/arquivos, mover pastas, juntar Services, extrair helpers, remover imports, reordenar execução, modificar queries ou simplificar regras. Não modificar layout, textos visíveis, acessibilidade, autorização, transações, payloads ou integrações. Não introduzir formatador, dependência, framework, gate de CI ou abstração nova.

Arquivos SQL, HTML legais com hash, referências de integridade, locks de dependências, fixtures de dados, relatórios gerados e artefatos oficiais/históricos permanecem preservados. O escopo fechado e as proteções estão em [design.md](design.md).

### Análise de volume, sem refatoração nesta change

A preocupação com o tamanho é registrada em [analise-de-complexidade.md](analise-de-complexidade.md), distinguindo código da aplicação, ferramentas, testes, histórico e relatórios. Esse diagnóstico não autoriza exclusões, limpeza de arquivos locais ou mudanças arquiteturais. Qualquer simplificação posterior precisa de avaliação própria.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. A change usa `skip_specs: true`: altera a apresentação do código e documenta o padrão, preservando os comportamentos das dezenove specs atuais.

## Impact

- **Superfícies:** arquivos próprios existentes no baseline `663891af9f6b0cbe7c1df0b7841e104ae7f2cbf1`, selecionados pelas regras do design; todas as áreas Pública/Aluno/Administração e os sete módulos Python podem receber formatação.
- **Arquitetura:** Frontend → Route → Controller → Service → Model/Repository → MySQL permanece, assim como os ADRs 001, 002, 006, 008, 009 e 010. Não muda nenhuma tabela, procedure, migration, versão de termo ou fronteira de transação.
- **Compatibilidade:** preservar estrutura sintática, valores literais, ordem dos imports/operações, DOM funcional e cascata CSS. Python usa 4 espaços; HTML/CSS/JavaScript usam 2 espaços. Exceções por strings e conteúdo sensível são justificadas na validação.
- **Dependências:** nenhuma nova. Ferramentas já presentes no ambiente podem apoiar comparações temporárias, sem entrar no runtime.
- **Validação:** comparação antes/depois, cobertura das duas stacks, integrações e migrations em MySQL real descartável, suíte E2E existente e inspeção visual proporcional. Não usar o banco de demonstração para testes destrutivos nem executar Gemini real para provar formatação.
- **Entrega:** proposta apenas nesta etapa; o usuário fará o apply posteriormente. Sem implementação, commit ou push automáticos.
