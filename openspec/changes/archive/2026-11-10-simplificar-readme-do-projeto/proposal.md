# Proposta: simplificar o README do projeto

## Why

O README atual tem 701 linhas e mistura uma visão do produto com contratos detalhados, manutenção do banco e histórico de validação. A equipe precisa de uma entrada curta e confiável para compreender e apresentar o projeto, corrigindo também a indicação de migration 016 e a contagem antiga de quatro testes E2E.

## What Changes

- Reorganizar o README em até 350 linhas, com objetivo/público, destaques funcionais, lista oficial dos vinte casos, tecnologias, arquitetura resumida, execução, testes e índice da documentação. Esse limite é uma escolha de legibilidade, não exigência do professor.
- Preservar o título `Funcionalidades Implementadas`, a numeração e o significado dos vinte itens; destacar separadamente os recursos não CRUD existentes, sem inflar a contagem.
- Manter instruções suficientes para preparar dependências/configuração/banco, iniciar API e frontend e acessar login/cadastro e criação administrativa documentada, sem credenciais padrão ou leitura do `.env`.
- Concentrar detalhes operacionais ainda exclusivos do README em `docs/technical/operacao-do-projeto.md`: adoção/recuperação do banco, contratos legados do catálogo, clones antigos, preferências locais e evidências históricas.
- Transferir o contrato detalhado, configuração, limites e evidências do Tutor para `docs/technical/operacao-tutor-ia.md`, mantendo no README uma apresentação curta e o link.
- Reutilizar a documentação técnica existente para os demais domínios, arquitetura, diagrama, fluxogramas e testes; corrigir caminhos relativos após a transferência e preservar âncoras do README.
- Corrigir o retrato atual para migration 017 e seis testes E2E. Distinguir o roteiro final de apresentação da atividade anterior, sem presumir dispensa de entrega, hospedagem ou pontuação.

### Fora do escopo

Modificar código, testes, configurações, dependências, SQL, dados ou arquivos oficiais de design; alterar as decisões técnicas ou o conteúdo dos termos legais; criar slides, vídeo ou guia de estudo; editar relatórios arquivados; executar instalação, migrations, integrações ou Gemini para conferir documentação. Não realizar commit, push, merge ou limpeza de arquivos locais.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. `skip_specs: true` é aplicável à reorganização documental sem mudança de requisitos do sistema.

## Impact

- **Arquivos de implementação:** somente `README.md` e os dois novos documentos técnicos indicados. Demais fontes de verdade continuam com seus arquivos e links existentes.
- **Baseline:** HEAD `2a82c77b6978efdf32ecfc11deb25d529e576fc2` e README local SHA-256 `b62fe537d6a9e92d59f3921e4e51513c7ba7d25bc7e4be76e74e82c40f0aee5a`. A versão local já incorpora a simplificação das ferramentas, aplicada/arquivada e ainda não publicada; ela não pode ser substituída pela cópia do HEAD.
- **Compatibilidade:** preservar o hook aposentado, testes locais sob demanda, CI ativa e preferências locais ignoradas; não reintroduzir instruções de instalação do hook. Aplicação, vinte funcionalidades e as dezenove specs permanecem iguais.
- **Validação:** mapa de destino do conteúdo, links/âncoras, comandos comparados às fontes atuais, contagens estáticas, preservação dos casos e evidências e validação OpenSpec. Não é necessária nova execução dos testes da aplicação.
