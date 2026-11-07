# Validação — Alinhar a documentação da entrega

## Baseline anterior à edição

Data local: 07/11/2026. Revisão Git: `6f40f1303560cad908fbdd752fd0aaa4dd285b3b`.
Os dez arquivos de escopo correspondiam ao conteúdo dessa revisão antes da edição.
As referências Git abaixo preservam os blocos completos, inclusive descrições e cenários.
Hashes SHA-256 usam texto UTF-8 com quebras LF.

Estado inicial: somente esta change, `tornar-fingerprint-de-schema-portavel/` e `tmp/` estavam não rastreados; nenhum arquivo rastreado estava modificado. Esses diretórios preexistentes serão preservados.

| Arquivo | SHA-256 do baseline |
| --- | --- |
| `openspec/specs/autenticacao-escolar/spec.md` | `0e4ed8010d91f435f5ed76be600d759b74c9fab2b8fe3c477a3f93da050f2c04` |
| `openspec/specs/catalogo-academico/spec.md` | `a5b0cc4a4c2793cd1b4d9c1f07ff1ea97402d665d4e3494b5a9ee7ba91e7cc0c` |
| `openspec/specs/gestao-administrativa-conteudo/spec.md` | `aaf77080078ce44d18bf087dff12f8d8e2d4812d2648815c248a450b55306fb3` |
| `openspec/specs/desempenho-real/spec.md` | `065e0633f8cfffc632cc42a3b1ea120f7e09d2da0dd8065de49230d8ec4978eb` |
| `openspec/specs/plano-estudos-basico/spec.md` | `16f76c32dc7651af66cbfa73edd5a78cd0b1200c4b593f3e5774d8310c849b22` |
| `openspec/specs/questoes-versionadas/spec.md` | `4aff09783fea17c71d65954e4efe973f7786eb54be769bdc708a1e1e44fbe8c9` |
| `openspec/specs/simulados-fixos/spec.md` | `bb451996af3ed609e3086874d403c36918f65150e6f72140c933d1bc52cd35ab` |
| `README.md` | `fd754579e5e4c7ebb5b034cfe3dda15a4818b5571d1d4527dc6a8966bfbce63b` |
| `docs/technical/entrega-academica.md` | `038dc1282a930c47d0c1c38ad537f706aeea503569d1c98c989e12531cafb870` |
| `openspec/config.yaml` | `fe665710b9fa5afb39b31fd7cd516844dc2598c5e0f93d5a604595bf17b68d7d` |

## Inventário e avisos originais

`openspec validate --specs --strict --json`: saída 1; 11 capabilities, quatro válidas e sete com 31 avisos de descrição acima de 500 caracteres, sem erros.
Cada aviso abaixo corresponde ao índice zero-based retornado pelo CLI e a um dos títulos enumerados no design.

| Capability | Caminho do aviso | Requisito | Caracteres | Bloco original na revisão Git |
| --- | --- | --- | ---: | --- |
| `autenticacao-escolar` | `requirements[0]` | Cadastro público exclusivo de Aluno | 1040 | [linhas 9–51](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L9-L51) |
| `autenticacao-escolar` | `requirements[2]` | Login por credenciais com rotação de sessão | 644 | [linhas 65–82](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L65-L82) |
| `autenticacao-escolar` | `requirements[3]` | Ciclo de vida da sessão no servidor | 746 | [linhas 83–110](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L83-L110) |
| `autenticacao-escolar` | `requirements[4]` | Proteção de origem e CSRF | 703 | [linhas 111–133](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L111-L133) |
| `autenticacao-escolar` | `requirements[5]` | Autorização por perfil e recurso | 1257 | [linhas 134–176](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L134-L176) |
| `autenticacao-escolar` | `requirements[6]` | Reautenticação de ações sensíveis | 639 | [linhas 177–199](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L177-L199) |
| `autenticacao-escolar` | `requirements[7]` | Limite básico de tentativas de senha | 560 | [linhas 200–212](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L200-L212) |
| `autenticacao-escolar` | `requirements[8]` | Navegação autenticada e telas utilizáveis | 971 | [linhas 213–245](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L213-L245) |
| `autenticacao-escolar` | `requirements[9]` | Evolução compatível do banco e do MVP | 561 | [linhas 246–263](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L246-L263) |
| `autenticacao-escolar` | `requirements[11]` | URLs canônicas das páginas públicas de autenticação | 1055 | [linhas 272–313](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/autenticacao-escolar/spec.md#L272-L313) |
| `catalogo-academico` | `requirements[7]` | Compatibilidade dos consumidores existentes | 659 | [linhas 138–164](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/catalogo-academico/spec.md#L138-L164) |
| `gestao-administrativa-conteudo` | `requirements[4]` | Proteção de alterações não salvas | 605 | [linhas 89–126](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/gestao-administrativa-conteudo/spec.md#L89-L126) |
| `gestao-administrativa-conteudo` | `requirements[6]` | Acesso administrativo autenticado | 515 | [linhas 138–160](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/gestao-administrativa-conteudo/spec.md#L138-L160) |
| `gestao-administrativa-conteudo` | `requirements[7]` | Gestão mínima utilizável de Questões | 745 | [linhas 161–178](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/gestao-administrativa-conteudo/spec.md#L161-L178) |
| `gestao-administrativa-conteudo` | `requirements[8]` | Gestão mínima utilizável de Simulados fixos | 571 | [linhas 179–190](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/gestao-administrativa-conteudo/spec.md#L179-L190) |
| `desempenho-real` | `requirements[0]` | Métricas derivadas de fatos concluídos | 537 | [linhas 9–21](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/desempenho-real/spec.md#L9-L21) |
| `desempenho-real` | `requirements[1]` | Período e classificação históricos explícitos | 674 | [linhas 22–39](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/desempenho-real/spec.md#L22-L39) |
| `desempenho-real` | `requirements[3]` | Dashboards privados e operacionais | 1134 | [linhas 53–77](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/desempenho-real/spec.md#L53-L77) |
| `desempenho-real` | `requirements[4]` | Contrato reutilizável e interface honesta | 1380 | [linhas 78–108](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/desempenho-real/spec.md#L78-L108) |
| `plano-estudos-basico` | `requirements[0]` | Priorização determinística baseada em desempenho | 533 | [linhas 9–21](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/plano-estudos-basico/spec.md#L9-L21) |
| `plano-estudos-basico` | `requirements[1]` | Geração persistida exclusiva do dono | 741 | [linhas 22–39](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/plano-estudos-basico/spec.md#L22-L39) |
| `plano-estudos-basico` | `requirements[2]` | Início de prática e conclusão manual | 658 | [linhas 40–57](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/plano-estudos-basico/spec.md#L40-L57) |
| `plano-estudos-basico` | `requirements[3]` | Recálculo explícito com preservação de histórico | 709 | [linhas 58–75](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/plano-estudos-basico/spec.md#L58-L75) |
| `plano-estudos-basico` | `requirements[4]` | Privacidade e fluxo mínimo acessível | 905 | [linhas 76–93](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/plano-estudos-basico/spec.md#L76-L93) |
| `questoes-versionadas` | `requirements[0]` | Listagem e detalhe administrativos de Questões | 637 | [linhas 9–26](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/questoes-versionadas/spec.md#L9-L26) |
| `questoes-versionadas` | `requirements[1]` | Cadastro e edição de rascunho compatíveis | 608 | [linhas 27–44](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/questoes-versionadas/spec.md#L27-L44) |
| `questoes-versionadas` | `requirements[2]` | Publicação explícita com versão imutável | 540 | [linhas 45–62](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/questoes-versionadas/spec.md#L45-L62) |
| `simulados-fixos` | `requirements[0]` | Composição fixa revisada e publicada | 636 | [linhas 9–26](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/simulados-fixos/spec.md#L9-L26) |
| `simulados-fixos` | `requirements[1]` | Início e retomada de tentativa própria | 584 | [linhas 27–39](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/simulados-fixos/spec.md#L27-L39) |
| `simulados-fixos` | `requirements[3]` | Finalização atômica com resultado imutável | 530 | [linhas 53–65](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/simulados-fixos/spec.md#L53-L65) |
| `simulados-fixos` | `requirements[4]` | Consulta privada e preservação histórica | 544 | [linhas 66–78](https://github.com/Matibas100/ProjetoSoftwarePE/blob/6f40f1303560cad908fbdd752fd0aaa4dd285b3b/openspec/specs/simulados-fixos/spec.md#L66-L78) |

## Títulos e cenários anteriores

### autenticacao-escolar

12 requisitos; 54 cenários originais. Purpose e requisitos fora do inventário permanecem integrais.

| Título original | Cenários | Títulos originais dos cenários |
| --- | ---: | --- |
| Cadastro público exclusivo de Aluno | 8 | Cadastro válido<br>Tentativa de escolher Administrador<br>Confirmação ou campos inválidos<br>Duplicidade normalizada e concorrente<br>Cadastro estando autenticado<br>Aceite ausente ou inválido<br>Texto mudou durante o preenchimento<br>Falha ao gravar a evidência |
| Provisionamento local de Administrador | 2 | Primeira conta administrativa<br>E-mail já pertence a Aluno |
| Login por credenciais com rotação de sessão | 3 | Login de Aluno ou Administrador<br>Credenciais recusadas sem identificação da causa<br>Persistência e saída sem segredos |
| Ciclo de vida da sessão no servidor | 5 | Consulta de identidade<br>Expiração nos dois limites<br>Logout em uma de duas sessões<br>Sessão revogada não pode reaparecer<br>Revogação global |
| Proteção de origem e CSRF | 4 | Bootstrap e mutação válida<br>CSRF de outra sessão<br>Origem não autorizada<br>Preflight |
| Autorização por perfil e recurso | 8 | Aluno lê catálogo ativo<br>Aluno tenta gestão ou gabarito<br>Requisição anônima<br>Métodos auxiliares e inválidos<br>Ação própria de Aluno<br>Recurso de outra conta ou perfil administrativo<br>Metadados de termos sem autenticação<br>Privacidade da conta ainda sem aceites |
| Reautenticação de ações sensíveis | 4 | Ação sensível com janela vencida<br>Recuperar a janela sensível<br>Caminho alternativo por PUT<br>Senha incorreta no diálogo |
| Limite básico de tentativas de senha | 2 | Quinta falha e bloqueio<br>Retomada e contagem concorrente |
| Navegação autenticada e telas utilizáveis | 6 | Fluxo escolar de Aluno<br>Entrada direta em gestão<br>Formulário com erro ou duplo clique<br>Acesso por teclado e tamanhos de tela<br>Alternância entre formulários<br>Sessão válida nas páginas públicas |
| Evolução compatível do banco e do MVP | 3 | Upgrade sem perda<br>Falha de login composto<br>Snapshot e regressão |
| Limpeza operacional restrita da autenticação | 1 | Limpeza de registros antigos |
| URLs canônicas das páginas públicas de autenticação | 8 | Entrada direta e recarga<br>Endereços antigos continuam utilizáveis<br>Barra final e parâmetros<br>Destino externo não controla o redirecionamento<br>Consulta sem corpo<br>Recursos e páginas existentes<br>Caminho inexistente e API no servidor de páginas<br>Diretório público delimitado |

### catalogo-academico

8 requisitos; 29 cenários originais. Purpose e requisitos fora do inventário permanecem integrais.

| Título original | Cenários | Títulos originais dos cenários |
| --- | ---: | --- |
| Áreas oficiais do ENEM | 2 | Consulta das quatro áreas<br>Tentativa de alterar o catálogo fixo |
| Matéria obrigatoriamente vinculada a uma Área | 3 | Criação válida de Matéria<br>Área ausente ou inexistente<br>Matéria existente sem mapeamento seguro |
| Ciclo de vida de Matérias e Assuntos | 4 | Inativação sem perda<br>Arquivamento de Assunto utilizado<br>Arquivamento de Matéria com Assunto disponível<br>Reativação válida |
| Unicidade normalizada de Assunto por Matéria | 4 | Duplicidade por caixa, espaço e acento<br>Mesmo nome em Matérias diferentes<br>Conflito com Assunto arquivado<br>Concorrência na criação |
| Exclusão física sem cascata destrutiva | 3 | Exclusão de Matéria com Assuntos<br>Exclusão de Assunto com Questões<br>Exclusão de registro sem vínculos |
| Impacto e transferência explícita de Assunto | 5 | Prévia de impacto<br>Transferência confirmada<br>Nome conflitante no destino<br>Impacto mudou após a prévia<br>Alteração legada de materia_id |
| Consultas administrativas do catálogo | 3 | Filtragem de Matérias<br>Filtragem de Assuntos<br>Página sem resultados |
| Compatibilidade dos consumidores existentes | 5 | Leitura legada<br>Seletor de novo vínculo<br>Leitura sem autenticação<br>Aluno tenta consultar todos os estados<br>Administrador consulta itens indisponíveis |

### gestao-administrativa-conteudo

9 requisitos; 35 cenários originais. Purpose e requisitos fora do inventário permanecem integrais.

| Título original | Cenários | Títulos originais dos cenários |
| --- | ---: | --- |
| Estrutura administrativa do Desktop V1 | 3 | Abertura de Gestão de Matérias<br>Abertura de Gestão de Assuntos<br>Elemento fora do escopo |
| Gestão utilizável de Matérias | 4 | Criação de Matéria<br>Filtros de Matérias<br>Exclusão bloqueada de Matéria<br>Arquivamento bloqueado por Assuntos disponíveis |
| Gestão utilizável de Assuntos | 5 | Filtros dependentes<br>Nome duplicado<br>Transferência com impacto<br>Exclusão bloqueada de Assunto<br>Resumos fora do escopo funcional |
| Estados de carregamento, vazio, erro e sucesso | 5 | Carregamento de tabela<br>Catálogo vazio<br>Filtros sem resultado<br>Falha ao salvar<br>Operação concluída |
| Proteção de alterações não salvas | 7 | Saída com formulário alterado<br>Saída sem alterações<br>Logout com formulário alterado<br>Sessão expira durante edição<br>Reautenticação sensível e nova confirmação<br>Outra conta após recuperar login<br>Falha de senha ou conexão |
| Acessibilidade operacional | 2 | Uso por teclado<br>Confirmação crítica |
| Acesso administrativo autenticado | 4 | Administrador abre a gestão<br>Acesso direto sem perfil<br>Serviço indisponível durante a verificação<br>Saída confirmada |
| Gestão mínima utilizável de Questões | 3 | Gerir Questão real<br>Falha ou saída durante edição<br>Operação acessível e escopo limitado |
| Gestão mínima utilizável de Simulados fixos | 2 | Publicação de composição real<br>Falha e proteção da seleção |

### desempenho-real

5 requisitos; 16 cenários originais. Purpose e requisitos fora do inventário permanecem integrais.

| Título original | Cenários | Títulos originais dos cenários |
| --- | ---: | --- |
| Métricas derivadas de fatos concluídos | 2 | Combinar origens sem dupla contagem<br>Reenvio e repetição real |
| Período e classificação históricos explícitos | 3 | Limites do período<br>Taxonomia muda<br>Datas inválidas |
| Ausência de dados e amostra pequena | 2 | Conta sem histórico<br>Limite de amostra |
| Dashboards privados e operacionais | 4 | Dashboard do Aluno<br>Atividades no período com desempate<br>Simulado sem respostas<br>Contagens administrativas |
| Contrato reutilizável e interface honesta | 5 | Plano consulta diagnóstico<br>Diagnóstico participa da geração de plano<br>Nova resposta durante a consulta<br>Consulta de bloco falha<br>Resposta atrasada após mudança de contexto |

### plano-estudos-basico

6 requisitos; 18 cenários originais. Purpose e requisitos fora do inventário permanecem integrais.

| Título original | Cenários | Títulos originais dos cenários |
| --- | ---: | --- |
| Priorização determinística baseada em desempenho | 2 | Ordenação e desempate<br>Assunto transferido ou sem conteúdo |
| Geração persistida exclusiva do dono | 3 | Gerar, reenviar e recarregar<br>Falta de base ou falha de diagnóstico<br>Não consentiu ou revogou |
| Início de prática e conclusão manual | 3 | Estudar e concluir<br>Conteúdo retirado após geração<br>Conclusão após negativa |
| Recálculo explícito com preservação de histórico | 3 | Recálculo confirmado<br>Concorrência ou falha<br>Recálculo concorrente com revogação |
| Privacidade e fluxo mínimo acessível | 3 | Acesso alheio<br>Falha recuperável na tela<br>Revogação em outra aba ou troca de conta |
| Acesso consistente ao plano na navegação do Aluno | 4 | Abrir o plano a partir de qualquer página do Aluno<br>Página atual e navegação por teclado<br>Navegação com alternativa ainda não salva<br>Acesso direto sem sessão |

### questoes-versionadas

5 requisitos; 14 cenários originais. Purpose e requisitos fora do inventário permanecem integrais.

| Título original | Cenários | Títulos originais dos cenários |
| --- | ---: | --- |
| Listagem e detalhe administrativos de Questões | 3 | Filtros combinados<br>Filtro ou recurso inválido<br>Consulta não autorizada |
| Cadastro e edição de rascunho compatíveis | 3 | Cadastro válido sem publicação<br>Edição de Questão publicada<br>Edição conflitante ou inválida |
| Publicação explícita com versão imutável | 3 | Publicação revisada<br>Nova versão ou replay<br>Falha composta ou sessão vencida |
| Arquivamento sem perda de conteúdo | 2 | Retirada de uso<br>Arquivamento repetido |
| Elegibilidade e preservação do legado | 3 | Backfill do banco existente<br>Consulta administrativa legada<br>Catálogo indisponível |

### simulados-fixos

6 requisitos; 12 cenários originais. Purpose e requisitos fora do inventário permanecem integrais.

| Título original | Cenários | Títulos originais dos cenários |
| --- | ---: | --- |
| Composição fixa revisada e publicada | 3 | Cadastro e publicação manual<br>Composição inválida ou indisponível<br>Edição obsoleta ou de publicado |
| Início e retomada de tentativa própria | 2 | Começar e retomar<br>Conteúdo retirado |
| Persistência de respostas sem correção antecipada | 2 | Salvar, alterar e recarregar<br>Escritas concorrentes |
| Finalização atômica com resultado imutável | 2 | Finalizar com itens em branco<br>Falha antes do commit e replay |
| Consulta privada e preservação histórica | 2 | Consulta após novo login<br>Consulta alheia ou antecipada |
| Execução acessível sem cronômetro obrigatório | 1 | Confirmar com falha recuperável |

## Rastreabilidade por cláusula

As tabelas registram 241 obrigações das 178 sentenças originais, conservadas literalmente nos cenários. Pontos e ponto e vírgula fora de literais delimitam os trechos citados. Quando um trecho coordena mais de um SHALL/MUST, há uma linha por ocorrência, numerada na ordem original e mantendo o contexto completo. Cada destino identifica o cenário e a posição de seu THEN. Keywords, payloads, limites, proibições e condições permanecem integrais.

### Cláusulas de autenticacao-escolar

#### Cadastro público exclusivo de Aluno

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL disponibilizar `/cadastro` como URL canônica, mantendo `/cadastro.html` por redirecionamento, e `POST /api/auth/cadastro` para criar Aluno ativo com nome, e-mail, senha, confirmação e `termos_uso:{versao,aceito:true}`. | `Contrato de entrada do cadastro`, THEN 1 |
| Nome SHALL ter 2–100 caracteres após trim; | `Contrato de entrada do cadastro`, THEN 2 |
| e-mail SHALL ser normalizado por trim/lowercase, ASCII, até 254 caracteres, com exatamente um `@`, partes não vazias, domínio com ponto e sem espaços, controles ou pontos consecutivos. | `Contrato de entrada do cadastro`, THEN 2 |
| Senha SHALL ter 8–128 caracteres, sem transformação, e confirmação idêntica. | `Contrato de entrada do cadastro`, THEN 3 |
| Campos extras SHALL ser recusados com 400. | `Contrato de entrada do cadastro`, THEN 4 |
| O aceite SHALL ser explícito, inicialmente desmarcado, referir-se ao Termo de Uso vigente e ser persistido atomicamente com a conta, sem autorizar o plano. | `Aceite de uso no cadastro`, THEN 1 |
| O e-mail normalizado SHALL ser único, inclusive sob concorrência. | `Unicidade e respostas do cadastro`, THEN 1 |
| Sucesso SHALL retornar 201 com `{usuario: {id, nome, email, perfil}}`, sem autenticar automaticamente; | `Unicidade e respostas do cadastro`, THEN 2 |
| validação SHALL retornar 400, versão de uso desatualizada SHALL retornar 409 `termo_desatualizado` e duplicidade SHALL retornar 409. (obrigação 1/3, na ordem do texto) | `Unicidade e respostas do cadastro`, THEN 2 |
| validação SHALL retornar 400, versão de uso desatualizada SHALL retornar 409 `termo_desatualizado` e duplicidade SHALL retornar 409. (obrigação 2/3, na ordem do texto) | `Unicidade e respostas do cadastro`, THEN 2 |
| validação SHALL retornar 400, versão de uso desatualizada SHALL retornar 409 `termo_desatualizado` e duplicidade SHALL retornar 409. (obrigação 3/3, na ordem do texto) | `Unicidade e respostas do cadastro`, THEN 2 |

#### Login por credenciais com rotação de sessão

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL oferecer `/login` como URL canônica, mantendo `/login.html` por redirecionamento, e `POST /api/auth/login` com `{email, senha}`. | `Contrato HTTP de login`, THEN 1 |
| Credenciais válidas SHALL retornar 200 com usuário público, `csrf_token` e `destino`, revogando a sessão anterior e estabelecendo nova sessão. | `Contrato HTTP de login`, THEN 2 |
| E-mail desconhecido, senha incorreta ou conta inativa SHALL produzir 401 `credenciais_invalidas` com a mesma mensagem `E-mail ou senha inválidos.`; | `Contrato HTTP de login`, THEN 3 |
| entrada malformada SHALL produzir 400. | `Contrato HTTP de login`, THEN 3 |
| Login de usuário já autenticado SHALL retornar 409 `ja_autenticado`. | `Contrato HTTP de login`, THEN 4 |
| Senhas SHALL ser persistidas somente por hash adequado e SHALL NOT aparecer em URL, storage ou logs. (obrigação 1/2, na ordem do texto) | `Proteção de senha no login`, THEN 1 |
| Senhas SHALL ser persistidas somente por hash adequado e SHALL NOT aparecer em URL, storage ou logs. (obrigação 2/2, na ordem do texto) | `Proteção de senha no login`, THEN 1 |

#### Ciclo de vida da sessão no servidor

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL manter sessões no servidor, consultar a identidade em `GET /api/auth/sessao` e revogar a atual em `POST /api/auth/logout`. | `Identidade e prazos da sessão`, THEN 1 |
| A sessão autenticada SHALL expirar em 8 horas absolutas ou 30 minutos de inatividade, considerando o limite atingido como expirado; | `Identidade e prazos da sessão`, THEN 2 |
| sessão anônima de CSRF SHALL durar 10 minutos e nunca conceder acesso. | `Identidade e prazos da sessão`, THEN 2 |
| Sessões revogadas, expiradas, inexistentes ou de conta inativa SHALL gerar 401 `sessao_invalida` nas rotas protegidas. | `Identidade e prazos da sessão`, THEN 3 |
| Cookie SHALL ser HttpOnly, SameSite=Lax, Path=/api, sem Domain e Secure em produção. | `Atributos do cookie de sessão`, THEN 1 |
| Logout SHALL retornar 204 e remover o cookie; | `Logout idempotente e revogação de sessões`, THEN 1 |
| sem sessão válida SHALL ser idempotente. | `Logout idempotente e revogação de sessões`, THEN 1 |
| Sessões múltiplas SHALL ser independentes e SHALL poder ser revogadas individualmente ou por usuário no servidor. (obrigação 1/2, na ordem do texto) | `Logout idempotente e revogação de sessões`, THEN 2 |
| Sessões múltiplas SHALL ser independentes e SHALL poder ser revogadas individualmente ou por usuário no servidor. (obrigação 2/2, na ordem do texto) | `Logout idempotente e revogação de sessões`, THEN 2 |

#### Proteção de origem e CSRF

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL oferecer `GET /api/auth/csrf` que devolve token vinculado à sessão válida ou cria sessão anônima. | `Contrato do bootstrap CSRF`, THEN 1 |
| Cadastro, login e mutações autenticadas SHALL exigir `X-CSRF-Token` correto e `Origin` exatamente autorizado; | `Erros de origem e CSRF nas mutações`, THEN 1 |
| origem ausente, `null` ou não permitida SHALL retornar 403 `origem_nao_permitida`, e CSRF ausente/incorreto SHALL retornar 403 `csrf_invalido`, sem executar negócio. (obrigação 1/2, na ordem do texto) | `Erros de origem e CSRF nas mutações`, THEN 1 |
| origem ausente, `null` ou não permitida SHALL retornar 403 `origem_nao_permitida`, e CSRF ausente/incorreto SHALL retornar 403 `csrf_invalido`, sem executar negócio. (obrigação 2/2, na ordem do texto) | `Erros de origem e CSRF nas mutações`, THEN 1 |
| Logout sem sessão válida SHALL exigir origem e dispensar CSRF. | `Erros de origem e CSRF nas mutações`, THEN 2 |
| CORS SHALL permitir credenciais apenas para origens explícitas e SHALL NOT aceitar wildcard. (obrigação 1/2, na ordem do texto) | `Transporte de credenciais e cache de autenticação`, THEN 1 |
| CORS SHALL permitir credenciais apenas para origens explícitas e SHALL NOT aceitar wildcard. (obrigação 2/2, na ordem do texto) | `Transporte de credenciais e cache de autenticação`, THEN 1 |
| O frontend SHALL enviar cookies por `credentials: include`, mantendo CSRF somente em memória. | `Transporte de credenciais e cache de autenticação`, THEN 2 |
| Respostas de autenticação SHALL usar `Cache-Control: no-store`. | `Transporte de credenciais e cache de autenticação`, THEN 3 |

#### Autorização por perfil e recurso

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL autorizar operações no servidor, independentemente da tela. | `Política de catálogo e consultas públicas`, THEN 1 |
| GET health e GET `/api/termos` SHALL continuar públicos. | `Política de catálogo e consultas públicas`, THEN 2 |
| Leituras simples de Áreas, Matérias e Assuntos SHALL aceitar Aluno e Administrador; | `Política de catálogo e consultas públicas`, THEN 3 |
| `status=todos`, consultas administrativas, prévias de impacto, todas as mutações do catálogo e consulta legada de Questões SHALL exigir Administrador. | `Política de catálogo e consultas públicas`, THEN 3 |
| Gabarito da consulta legada SHALL NOT ser fornecido ao Aluno. | `Política de catálogo e consultas públicas`, THEN 4 |
| Rotas existentes sob `/api/aluno/` SHALL exigir perfil Aluno e SHALL limitar coleções e recursos pessoais ao usuário da sessão; (obrigação 1/2, na ordem do texto) | `Política de recursos próprios e erros de autorização`, THEN 1 |
| Rotas existentes sob `/api/aluno/` SHALL exigir perfil Aluno e SHALL limitar coleções e recursos pessoais ao usuário da sessão; (obrigação 2/2, na ordem do texto) | `Política de recursos próprios e erros de autorização`, THEN 1 |
| Administrador SHALL receber 403 nessas rotas. | `Política de recursos próprios e erros de autorização`, THEN 1 |
| Recurso pessoal inexistente ou de outro Aluno SHALL retornar o mesmo 404 sem exposição de conteúdo. | `Política de recursos próprios e erros de autorização`, THEN 2 |
| Anônimo SHALL receber 401; | `Política de recursos próprios e erros de autorização`, THEN 3 |
| perfil insuficiente SHALL receber 403 `acesso_negado`. | `Política de recursos próprios e erros de autorização`, THEN 3 |
| Mutações permitidas ao Aluno SHALL manter os controles existentes de sessão, origem e CSRF. | `Política de recursos próprios e erros de autorização`, THEN 4 |
| HEAD SHALL herdar a política de GET; | `Política de métodos auxiliares`, THEN 1 |
| rotas/métodos inexistentes SHALL preservar 404/405. | `Política de métodos auxiliares`, THEN 1 |
| Políticas específicas do plano SHALL ser verificadas antes de consultar seu recurso; | `Consentimento antes do recurso e acesso à privacidade`, THEN 1 |
| ausência de consentimento SHALL produzir 403 uniforme sem expor existência do item. | `Consentimento antes do recurso e acesso à privacidade`, THEN 1 |
| Consulta de privacidade SHALL permitir ao próprio Aluno decidir mesmo sem aceite prévio, sem abrir gestão administrativa. | `Consentimento antes do recurso e acesso à privacidade`, THEN 2 |

#### Reautenticação de ações sensíveis

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL exigir autenticação de senha nos últimos 15 minutos para excluir, inativar, arquivar, reativar ou transferir catálogo e para PUT Matéria contendo `status`/`area_enem_id` ou PUT Assunto contendo `materia_id`. | `Escopo e prazo das ações sensíveis`, THEN 1 |
| Janela vencida SHALL retornar 403 `reautenticacao_necessaria`, sem mudança parcial. | `Escopo e prazo das ações sensíveis`, THEN 2 |
| `POST /api/auth/reautenticar` SHALL confirmar a senha do usuário atual e renovar a janela; | `Contrato da reautenticação contextual`, THEN 1 |
| senha incorreta SHALL retornar 401 `credenciais_invalidas` preservando a sessão, e sessão inválida SHALL retornar 401 `sessao_invalida`. (obrigação 1/2, na ordem do texto) | `Contrato da reautenticação contextual`, THEN 1 |
| senha incorreta SHALL retornar 401 `credenciais_invalidas` preservando a sessão, e sessão inválida SHALL retornar 401 `sessao_invalida`. (obrigação 2/2, na ordem do texto) | `Contrato da reautenticação contextual`, THEN 1 |
| A tela SHALL preservar contexto e exigir nova confirmação da ação, sem repetir mutação automaticamente. | `Contrato da reautenticação contextual`, THEN 2 |

#### Limite básico de tentativas de senha

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL limitar login a 5 falhas por e-mail normalizado em janela de 15 minutos e reautenticação a 5 falhas por usuário em janela independente. | `Identidades e janelas do limite de senha`, THEN 1 |
| A quinta falha SHALL iniciar bloqueio de 15 minutos e retornar 429 com Retry-After; | `Identidades e janelas do limite de senha`, THEN 2 |
| tentativas durante bloqueio SHALL manter 429 inclusive com senha correta. | `Identidades e janelas do limite de senha`, THEN 2 |
| E-mails desconhecidos/inativos SHALL seguir a mesma regra. | `Identidades e janelas do limite de senha`, THEN 3 |
| Após o bloqueio o contador SHALL reiniciar; | `Reinício e concorrência da contagem`, THEN 1 |
| sucesso anterior ao bloqueio SHALL zerar falhas. | `Reinício e concorrência da contagem`, THEN 1 |
| Atualizações concorrentes SHALL NOT perder contagem ou produzir erro interno por colisão da chave. | `Reinício e concorrência da contagem`, THEN 2 |

#### Navegação autenticada e telas utilizáveis

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| Login e cadastro SHALL usar identidade visual e estados de PUB-AUT-001/002 com acessibilidade por teclado, labels, foco visível, loading, erro e sucesso. | `Apresentação e links públicos de autenticação`, THEN 1 |
| Os links entre essas telas SHALL usar `/login` e `/cadastro`; | `Apresentação e links públicos de autenticação`, THEN 2 |
| após cadastro concluído, logout confirmado ou identificação de sessão inválida no bootstrap de página protegida, o frontend SHALL encaminhar a `/login`. | `Apresentação e links públicos de autenticação`, THEN 2 |
| Recuperação/onboarding não implementados SHALL NOT aparecer como links ativos. | `Apresentação e links públicos de autenticação`, THEN 3 |
| Aluno SHALL entrar em `/aluno/inicio.html` com nome real e saída; | `Destinos fixos e conteúdo autorizado`, THEN 1 |
| Administrador SHALL entrar em `/admin/materias.html`. | `Destinos fixos e conteúdo autorizado`, THEN 1 |
| Destinos SHALL ser fixos e SHALL NOT aceitar redirect externo. (obrigação 1/2, na ordem do texto) | `Destinos fixos e conteúdo autorizado`, THEN 2 |
| Destinos SHALL ser fixos e SHALL NOT aceitar redirect externo. (obrigação 2/2, na ordem do texto) | `Destinos fixos e conteúdo autorizado`, THEN 2 |
| Início de Aluno SHALL NOT exibir métricas fictícias ou gestão. | `Destinos fixos e conteúdo autorizado`, THEN 3 |
| `/index.html` e telas administrativas SHALL verificar sessão antes de carregar gestão. | `Destinos fixos e conteúdo autorizado`, THEN 4 |
| Sessão válida nas telas de login/cadastro SHALL encaminhar ao destino do perfil. | `Destinos fixos e conteúdo autorizado`, THEN 5 |
| Saída SHALL navegar somente depois de logout confirmado; | `Saída confirmada e falha de rede`, THEN 1 |
| falha de rede SHALL mostrar erro sem fingir sucesso. | `Saída confirmada e falha de rede`, THEN 1 |

#### Evolução compatível do banco e do MVP

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL adicionar autenticação por migration versionada e snapshot equivalente, preservando dados, identificadores, procedure e regras existentes. | `Migration e atomicidade da autenticação`, THEN 1 |
| Não SHALL modificar migrations aplicadas. | `Migration e atomicidade da autenticação`, THEN 2 |
| Operações de cadastro/login SHALL ser atômicas e falhas SHALL NOT deixar conta parcial ou sessão autenticada parcial. (obrigação 1/2, na ordem do texto) | `Migration e atomicidade da autenticação`, THEN 3 |
| Operações de cadastro/login SHALL ser atômicas e falhas SHALL NOT deixar conta parcial ou sessão autenticada parcial. (obrigação 2/2, na ordem do texto) | `Migration e atomicidade da autenticação`, THEN 3 |
| Instalação nova, upgrade de 004, baseline do snapshot completo e idempotência SHALL ser verificáveis no MySQL real. | `Regressão MySQL e autenticação real`, THEN 1 |
| Os 29 cenários originais e a suíte ampliada SHALL continuar validando comportamento com autenticação real, sem bypass de produção. | `Regressão MySQL e autenticação real`, THEN 2 |

#### URLs canônicas das páginas públicas de autenticação

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O servidor local do frontend SHALL responder a GET `/login` e GET `/cadastro` com 200 e conteúdo HTML das respectivas telas, mantendo essas URLs no navegador e permitindo entrada direta e recarga. | `Respostas canônicas GET e HEAD`, THEN 1 |
| HEAD SHALL apresentar o mesmo status e cabeçalhos de GET, sem corpo. | `Respostas canônicas GET e HEAD`, THEN 2 |
| GET e HEAD de `/login.html` e `/login/` SHALL retornar 302 com `Location: /login`; | `Aliases e query string de autenticação`, THEN 1 |
| `/cadastro.html` e `/cadastro/` SHALL retornar 302 com `Location: /cadastro`. | `Aliases e query string de autenticação`, THEN 1 |
| Havendo query string, ela SHALL ser preservada no Location, sem ser interpretada como destino de navegação. | `Aliases e query string de autenticação`, THEN 2 |
| Os redirecionamentos SHALL usar somente caminhos locais fixos e SHALL NOT criar ciclos ou aceitar destino externo. (obrigação 1/2, na ordem do texto) | `Aliases e query string de autenticação`, THEN 3 |
| Os redirecionamentos SHALL usar somente caminhos locais fixos e SHALL NOT criar ciclos ou aceitar destino externo. (obrigação 2/2, na ordem do texto) | `Aliases e query string de autenticação`, THEN 3 |
| CSS, JavaScript, imagens, fontes, `/`, `/index.html`, `/aluno/inicio.html`, `/admin/materias.html` e `/admin/assuntos.html` SHALL continuar acessíveis com seus comportamentos existentes. | `Recursos preservados e limite da raiz pública`, THEN 1 |
| Caminhos inexistentes SHALL retornar 404, sem fallback para login ou cadastro. | `Recursos preservados e limite da raiz pública`, THEN 2 |
| O servidor do frontend SHALL NOT executar ou encaminhar operações `/api` nem disponibilizar arquivos fora do diretório público do frontend. | `Recursos preservados e limite da raiz pública`, THEN 3 |

### Cláusulas de catalogo-academico

#### Compatibilidade dos consumidores existentes

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL preservar as rotas de leitura existentes e os campos legados de Matéria e Assunto para consumidores autenticados. | `Permissões nas leituras legadas do catálogo`, THEN 1 |
| As leituras simples SHALL aceitar Aluno ou Administrador; | `Permissões nas leituras legadas do catálogo`, THEN 2 |
| consultas com `status=todos` e consultas administrativas SHALL exigir Administrador. | `Permissões nas leituras legadas do catálogo`, THEN 2 |
| Anônimo SHALL receber 401 e perfil insuficiente SHALL receber 403, sem retornar dados protegidos. (obrigação 1/2, na ordem do texto) | `Permissões nas leituras legadas do catálogo`, THEN 3 |
| Anônimo SHALL receber 401 e perfil insuficiente SHALL receber 403, sem retornar dados protegidos. (obrigação 2/2, na ordem do texto) | `Permissões nas leituras legadas do catálogo`, THEN 3 |
| Seletores destinados a novos vínculos SHALL obter apenas itens ativos, enquanto consultas administrativas SHALL poder incluir todos os estados. (obrigação 1/2, na ordem do texto) | `Estados e contratos dos consumidores do catálogo`, THEN 1 |
| Seletores destinados a novos vínculos SHALL obter apenas itens ativos, enquanto consultas administrativas SHALL poder incluir todos os estados. (obrigação 2/2, na ordem do texto) | `Estados e contratos dos consumidores do catálogo`, THEN 1 |
| A introdução de autenticação SHALL NOT alterar payloads, ordenação, filtros, regras de negócio ou respostas de sucesso para o perfil autorizado. | `Estados e contratos dos consumidores do catálogo`, THEN 2 |

### Cláusulas de gestao-administrativa-conteudo

#### Proteção de alterações não salvas

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| As telas SHALL detectar mudanças locais ainda não persistidas e SHALL solicitar confirmação antes de descartá-las por cancelar, trocar de item, navegar, sair da conta ou fechar a página. (obrigação 1/2, na ordem do texto) | `Descarte e bloqueio sem perda de campos`, THEN 1 |
| As telas SHALL detectar mudanças locais ainda não persistidas e SHALL solicitar confirmação antes de descartá-las por cancelar, trocar de item, navegar, sair da conta ou fechar a página. (obrigação 2/2, na ordem do texto) | `Descarte e bloqueio sem perda de campos`, THEN 1 |
| Expiração de sessão, CSRF inválido ou necessidade de reautenticação SHALL bloquear mutações sem apagar campos e contexto. | `Descarte e bloqueio sem perda de campos`, THEN 2 |
| A recuperação da identidade SHALL ocorrer em diálogo no contexto; | `Recuperação da identidade com contexto local`, THEN 1 |
| operação pendente SHALL exigir nova confirmação explícita, sem repetição automática. | `Recuperação da identidade com contexto local`, THEN 1 |
| Se a conta recuperada for diferente, mutações SHALL continuar bloqueadas até descarte e recarga, permitindo copiar os dados locais antes de sair. | `Recuperação da identidade com contexto local`, THEN 2 |

#### Acesso administrativo autenticado

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| ADM-CON-001 e ADM-CON-002 SHALL verificar identidade antes de carregar conteúdo e chamar APIs administrativas. | `Identidade e moldura da gestão de catálogo`, THEN 1 |
| Somente Administrador SHALL utilizar a gestão; | `Identidade e moldura da gestão de catálogo`, THEN 2 |
| anônimo SHALL ir ao login e Aluno SHALL receber acesso negado com retorno ao seu início. (obrigação 1/2, na ordem do texto) | `Identidade e moldura da gestão de catálogo`, THEN 2 |
| anônimo SHALL ir ao login e Aluno SHALL receber acesso negado com retorno ao seu início. (obrigação 2/2, na ordem do texto) | `Identidade e moldura da gestão de catálogo`, THEN 2 |
| A moldura SHALL exibir nome real e ação `Sair`, mantendo composição, fluxos e funcionalidades existentes. | `Identidade e moldura da gestão de catálogo`, THEN 3 |
| Indisponibilidade da consulta de sessão SHALL mostrar erro/tentar novamente, sem conceder acesso. | `Falha de sessão e encerramento administrativo`, THEN 1 |
| Logout SHALL navegar ao login somente após revogação confirmada. | `Falha de sessão e encerramento administrativo`, THEN 2 |

#### Gestão mínima utilizável de Questões

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| As telas `/admin/questoes.html` e `/admin/questao.html` SHALL oferecer listagem, filtros, paginação, cadastro, edição de rascunho, revisão/publicação explícita e arquivamento com confirmação, usando referências ADM-QUE-001/002, moldura e ativos oficiais. | `Fluxos e referências oficiais da gestão de Questões`, THEN 1 |
| SHALL verificar perfil antes de consultar dados e preservar formulário/filtros em falha de negócio, rede ou sessão. | `Perfil e recuperação contextual de Questões`, THEN 1 |
| Recuperação/reautenticação SHALL ocorrer no contexto, sem repetição automática da mutação; | `Perfil e recuperação contextual de Questões`, THEN 2 |
| troca de conta SHALL bloquear contexto antigo até descarte/recarga. | `Perfil e recuperação contextual de Questões`, THEN 2 |
| SHALL proteger alterações não salvas, manter labels, foco e teclado e diferenciar carregamento, vazio, filtros sem resultado, erro e sucesso. | `Estados e acessibilidade da gestão de Questões`, THEN 1 |
| Funções fora do recorte SHALL permanecer indisponíveis sem ação fictícia. | `Estados e acessibilidade da gestão de Questões`, THEN 2 |

#### Gestão mínima utilizável de Simulados fixos

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| As telas administrativas de Simulados SHALL usar referências ADM-SIM-001/002 para listar, cadastrar composição manual ordenada, editar rascunho, revisar/publicar e arquivar, com dados reais e APIs protegidas. | `Composição manual e referências da gestão de Simulados`, THEN 1 |
| SHALL preservar campos, seleção, revisão e filtros diante de erro/sessão expirada, proteger alterações não salvas e exigir confirmação/reautenticação contextual em publicação/arquivamento. | `Preservação e confirmação da gestão de Simulados`, THEN 1 |
| SHALL permitir teclado/foco e mostrar vazio, carregamento, falha e sucesso. | `Estados acessíveis e limites da gestão de Simulados`, THEN 1 |
| Geradores, importação, calendário, TRI e recursos fora do recorte SHALL permanecer indisponíveis. | `Estados acessíveis e limites da gestão de Simulados`, THEN 2 |

### Cláusulas de desempenho-real

#### Métricas derivadas de fatos concluídos

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O diagnóstico SHALL considerar respostas de práticas corrigidas e itens respondidos de simulados finalizados uma vez por origem/registro. | `Elegibilidade dos fatos de desempenho`, THEN 1 |
| Tentativas em andamento e itens em branco SHALL NOT integrar o denominador de desempenho; | `Elegibilidade dos fatos de desempenho`, THEN 2 |
| repetições reais SHALL contar como respostas distintas. | `Elegibilidade dos fatos de desempenho`, THEN 2 |
| Total SHALL igualar acertos + erros; | `Fórmula e denominadores de desempenho`, THEN 1 |
| percentual SHALL ser `100 * acertos / total`, arredondado a duas casas; | `Fórmula e denominadores de desempenho`, THEN 1 |
| agregado SHALL usar totais, não média de percentuais. | `Fórmula e denominadores de desempenho`, THEN 1 |
| Resultado do simulado SHALL continuar usando todas as Questões em seu próprio denominador. | `Fórmula e denominadores de desempenho`, THEN 2 |

#### Período e classificação históricos explícitos

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| `GET /api/aluno/desempenho` e `/api/aluno/dashboard` SHALL aceitar `inicio`/`fim` juntos em datas ISO inclusivas, máximo 366 dias, início não posterior ao fim e fim não futuro em UTC. | `Intervalo UTC e metadados do diagnóstico`, THEN 1 |
| Padrão SHALL ser últimos 30 dias incluindo dia UTC atual. | `Intervalo UTC e metadados do diagnóstico`, THEN 2 |
| SHALL retornar período, timezone UTC, instante de cálculo, base e contagens por origem. | `Intervalo UTC e metadados do diagnóstico`, THEN 3 |
| Parâmetros extras ou inválidos SHALL retornar 400. | `Intervalo UTC e metadados do diagnóstico`, THEN 4 |
| Prática SHALL usar instante de resposta e simulado o de finalização. | `Instante e classificação dos fatos históricos`, THEN 1 |
| Matérias/Assuntos SHALL agrupar por IDs/classificação capturados na versão histórica, preservando referências após transferência/renomeação; | `Instante e classificação dos fatos históricos`, THEN 2 |
| rótulo de grupo SHALL vir do fato mais recente com desempate estável por origem/ID. | `Instante e classificação dos fatos históricos`, THEN 2 |

#### Dashboards privados e operacionais

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| Dashboard do Aluno SHALL mostrar diagnóstico próprio, até cinco últimas atividades próprias e links para fluxos existentes, usando ALU-DASH-001 e ALU-DES-001. | `Conteúdo e autorização dos dashboards`, THEN 1 |
| Dashboard administrativo SHALL mostrar somente contagens reais globais de catálogo ativo, Questões/simulados por estado e tentativas finalizadas, usando ADM-DASH-001 e exigindo Administrador. | `Conteúdo e autorização dos dashboards`, THEN 2 |
| APIs SHALL NOT aceitar usuário alvo do cliente nem expor histórico individual a Administrador. | `Conteúdo e autorização dos dashboards`, THEN 3 |
| Sessão/perfil SHALL ser verificados no servidor, mantendo 401/403 e no-store. | `Conteúdo e autorização dos dashboards`, THEN 4 |
| Atividades SHALL usar o mesmo período UTC do diagnóstico e expor `{tipo, id, ocorrido_em, titulo, url}`, com uma linha por tentativa de prática respondida ou simulado finalizado, inclusive simulado totalmente em branco. | `Contrato e ordenação das atividades recentes`, THEN 1 |
| SHALL ordenar por instante, tipo (`simulado` antes de `pratica`) e ID decrescentes e limitar o resultado a cinco linhas. | `Contrato e ordenação das atividades recentes`, THEN 2 |
| Lista vazia SHALL ser `[]`. | `Contrato e ordenação das atividades recentes`, THEN 3 |
| URLs SHALL apontar para `/aluno/questao.html?tentativa_id=<id>` ou `/aluno/simulado.html?tentativa_id=<id>` conforme a origem, mantendo autorização no destino. | `Destinos e significado das atividades`, THEN 1 |
| Quantidade de atividades SHALL NOT ser apresentada como quantidade de respostas. | `Destinos e significado das atividades`, THEN 2 |

#### Contrato reutilizável e interface honesta

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O diagnóstico SHALL disponibilizar ao plano a mesma base, período, limiar e fórmula da tela, sem fórmula paralela. | `Contrato comum e estados honestos do diagnóstico`, THEN 1 |
| As telas SHALL preservar destinos de login existentes, diferenciar vazio/amostra pequena/loading/erro por bloco e permitir nova tentativa de consulta. | `Contrato comum e estados honestos do diagnóstico`, THEN 2 |
| Recursos não implementados SHALL permanecer indisponíveis sem números fictícios. | `Contrato comum e estados honestos do diagnóstico`, THEN 3 |
| Métricas de uma resposta SHALL ser calculadas sobre visão consistente da mesma base de origem. | `Projeções e snapshot compartilhado do diagnóstico`, THEN 1 |
| Projeções dos Repositories de origem SHALL preservar a semântica dos fatos oferecidos pelos Services de práticas/simulados, sem acesso externo de escrita. | `Projeções e snapshot compartilhado do diagnóstico`, THEN 2 |
| Diagnóstico e cada linha de métrica SHALL expor `base:{pratica, simulado}` como quantidades de respostas cuja soma iguala o total respectivo. | `Projeções e snapshot compartilhado do diagnóstico`, THEN 3 |
| Consultas de um endpoint SHALL compartilhar snapshot consistente; | `Projeções e snapshot compartilhado do diagnóstico`, THEN 4 |
| consumidor interno autorizado SHALL poder fornecer o contexto e relógio da transação externa, sem que o diagnóstico os substitua ou encerre. | `Projeções e snapshot compartilhado do diagnóstico`, THEN 4 |
| Endpoints SHALL retornar payload completo ou erro, sem sucesso parcial. | `Falha integral e navegação do diagnóstico`, THEN 1 |
| Falha de consulta interna SHALL retornar HTTP 500 no formato de erro existente; | `Falha integral e navegação do diagnóstico`, THEN 2 |
| blocos da mesma requisição SHALL mostrar erro juntos e permitir recarga da requisição inteira. | `Falha integral e navegação do diagnóstico`, THEN 2 |
| Navegação SHALL continuar disponível. | `Falha integral e navegação do diagnóstico`, THEN 3 |
| Recarga/troca de período SHALL retirar dados anteriores dos blocos; | `Limpeza de blocos e resposta de contexto anterior`, THEN 1 |
| resposta atrasada de período ou identidade anterior SHALL NOT preencher a tela. | `Limpeza de blocos e resposta de contexto anterior`, THEN 1 |

### Cláusulas de plano-estudos-basico

#### Priorização determinística baseada em desempenho

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O plano SHALL usar diagnóstico dos últimos 30 dias UTC, selecionar até três Assuntos com pelo menos cinco respostas, catálogo ativo, vínculo Assunto–Matéria atual igual ao grupo histórico e Questões publicadas elegíveis. | `Base temporal e elegibilidade dos Assuntos`, THEN 1 |
| SHALL NOT preencher vagas com amostra insuficiente ou inventar dificuldade quando acerto for 100%. | `Base temporal e elegibilidade dos Assuntos`, THEN 2 |
| SHALL ordenar por menor taxa exata de acerto, maior total de respostas e menor ID do Assunto, sem arredondar antes de comparar. | `Comparação exata e explicação de prioridades`, THEN 1 |
| SHALL explicar prioridade relativa com acertos, total, percentual, período e amostra. | `Comparação exata e explicação de prioridades`, THEN 2 |

#### Geração persistida exclusiva do dono

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| Com aceite de uso e consentimento do plano vigentes, `GET /api/aluno/plano` SHALL retornar plano atual próprio ou `sem_plano`, sem gerar dados. | `Consulta autorizada e geração atômica do plano`, THEN 1 |
| `POST /api/aluno/plano/gerar` SHALL aceitar somente chave UUID, atribuir usuário pela sessão e persistir plano/itens/justificativas atomicamente com 201. | `Consulta autorizada e geração atômica do plano`, THEN 2 |
| SHALL existir no máximo um plano atual por usuário. | `Consulta autorizada e geração atômica do plano`, THEN 3 |
| Geração com plano atual existente SHALL retornar 409 orientando recálculo. | `Plano existente e replay de geração`, THEN 1 |
| Replay de mesma chave/operação/dados SHALL retornar o mesmo plano com 200 somente enquanto a autorização específica permanecer válida; | `Plano existente e replay de geração`, THEN 2 |
| chave divergente SHALL retornar 409. | `Plano existente e replay de geração`, THEN 2 |
| Sem autorização vigente, consulta e geração SHALL retornar 403 `consentimento_plano_necessario` antes de consultar plano, replay ou diagnóstico. | `Autorização antes de consulta e replay do plano`, THEN 1 |

#### Início de prática e conclusão manual

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| Cada item de plano autorizado SHALL ligar à seleção de Questões do próprio Assunto e informar disponibilidade atual. | `Prática contextual e contrato de conclusão`, THEN 1 |
| `POST /api/aluno/plano/itens/<id>/concluir` SHALL exigir os dois aceites vigentes e confirmação e permitir concluir somente item próprio do plano atual, persistindo estado/data. | `Prática contextual e contrato de conclusão`, THEN 2 |
| Replay SHALL manter data original enquanto autorizado; | `Replay e limites da conclusão manual`, THEN 1 |
| item de plano anterior SHALL retornar 409. | `Replay e limites da conclusão manual`, THEN 1 |
| Conclusão manual SHALL NOT alterar respostas, desempenho ou afirmar domínio do Assunto. | `Replay e limites da conclusão manual`, THEN 2 |
| Conteúdo posteriormente retirado SHALL manter item/justificativa e indicar indisponibilidade, enquanto o plano permanecer autorizado e não for eliminado por negativa confirmada. | `Item cujo conteúdo foi retirado`, THEN 1 |

#### Recálculo explícito com preservação de histórico

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| `POST /api/aluno/plano/recalcular` SHALL exigir os dois aceites vigentes, chave UUID, `plano_atual_id` e `confirmar:true`. | `Contrato e substituição atômica do plano`, THEN 1 |
| SHALL gerar nova seleção antes de substituir plano atual, preservando plano/itens/conclusões anteriores atomicamente durante o uso autorizado. | `Contrato e substituição atômica do plano`, THEN 2 |
| ID atual desatualizado SHALL retornar 409. | `Contrato e substituição atômica do plano`, THEN 3 |
| Sem candidatos SHALL retornar `sem_base_suficiente` preservando plano anterior no payload e no banco. | `Ausência de candidatos e falha no recálculo`, THEN 1 |
| Falha SHALL NOT apagar/trocar parcialmente o plano; | `Ausência de candidatos e falha no recálculo`, THEN 2 |
| novas respostas SHALL NOT provocar recálculo automático. | `Ausência de candidatos e falha no recálculo`, THEN 2 |
| A única exceção à preservação é recusa/revogação explicitamente confirmada, que SHALL eliminar os derivados próprios e registrar a negativa atomicamente, sem alterar as respostas de origem. | `Exceção de eliminação por negativa confirmada`, THEN 1 |

#### Privacidade e fluxo mínimo acessível

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| As APIs do plano SHALL exigir Aluno, propriedade por sessão, os dois aceites vigentes, origem/CSRF nas mutações e no-store. | `Política de acesso e erros das APIs do plano`, THEN 1 |
| Sem consentimento SHALL produzir 403 `consentimento_plano_necessario` antes da busca de recurso ou replay; | `Política de acesso e erros das APIs do plano`, THEN 2 |
| para Aluno autorizado, recurso ausente/alheio SHALL produzir o mesmo 404 e campos extras SHALL gerar 400. (obrigação 1/2, na ordem do texto) | `Política de acesso e erros das APIs do plano`, THEN 2 |
| para Aluno autorizado, recurso ausente/alheio SHALL produzir o mesmo 404 e campos extras SHALL gerar 400. (obrigação 2/2, na ordem do texto) | `Política de acesso e erros das APIs do plano`, THEN 2 |
| `/aluno/plano.html` SHALL apresentar lista, justificativas, gerar/iniciar/concluir/recalcular com teclado/foco e estados reais de loading/vazio/erro/sucesso quando autorizado; | `Apresentação autorizada e acesso à decisão de privacidade`, THEN 1 |
| caso contrário, SHALL oferecer explicação e link para `/aluno/privacidade.html`, sem dados residuais. | `Apresentação autorizada e acesso à decisão de privacidade`, THEN 1 |
| Agenda, prazo, IA e notificações SHALL permanecer fora do recorte. | `Apresentação autorizada e acesso à decisão de privacidade`, THEN 2 |
| Recuperação de sessão SHALL preservar a intenção da mesma conta sem repetição automática e exigir permissão válida antes de reexibir o plano; | `Recuperação e mudança de identidade ou permissão do plano`, THEN 1 |
| troca de conta ou perda de permissão SHALL impedir exposição de dados anteriores. | `Recuperação e mudança de identidade ou permissão do plano`, THEN 1 |

### Cláusulas de questoes-versionadas

#### Listagem e detalhe administrativos de Questões

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL oferecer `GET /api/admin/questoes` com filtros combináveis de busca por enunciado, Área, Matéria, Assunto, dificuldade e status, ordenado por ID decrescente. | `Filtros e paginação administrativos de Questões`, THEN 1 |
| SHALL usar envelope `itens`, `pagina`, `por_pagina`, `total_itens`, `total_paginas`, padrão 1/20 e máximo 100 itens por página. | `Filtros e paginação administrativos de Questões`, THEN 2 |
| Busca SHALL ter até 100 caracteres; | `Filtros e paginação administrativos de Questões`, THEN 3 |
| IDs SHALL ser inteiros positivos; | `Filtros e paginação administrativos de Questões`, THEN 3 |
| status SHALL aceitar rascunho/publicada/arquivada e dificuldade facil/media/dificil. | `Filtros e paginação administrativos de Questões`, THEN 3 |
| `GET /api/questoes/<id>` SHALL retornar conteúdo administrativo, status, revisão e versões. | `Detalhe e autorização administrativos de Questões`, THEN 1 |
| Todas essas operações SHALL exigir Administrador e SHALL NOT fornecer gabarito ao Aluno. (obrigação 1/2, na ordem do texto) | `Detalhe e autorização administrativos de Questões`, THEN 2 |
| Todas essas operações SHALL exigir Administrador e SHALL NOT fornecer gabarito ao Aluno. (obrigação 2/2, na ordem do texto) | `Detalhe e autorização administrativos de Questões`, THEN 2 |

#### Cadastro e edição de rascunho compatíveis

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| O sistema SHALL manter `POST /api/questoes` com validações, campos e sucesso 201 existentes, criando rascunho não publicado. | `Contrato de criação e atualização do rascunho`, THEN 1 |
| `PUT /api/questoes/<id>` SHALL editar somente campos de conteúdo/classificação com `revisao` obrigatória, permitir alterações parciais válidas e recusar campos desconhecidos com 400. | `Contrato de criação e atualização do rascunho`, THEN 2 |
| Enunciado e cinco alternativas SHALL ser textos não vazios; | `Contrato de criação e atualização do rascunho`, THEN 3 |
| gabarito SHALL ser A–E, dificuldade facil/media/dificil, explicação texto ou null e Assunto/Matéria SHALL estar ativos. (obrigação 1/2, na ordem do texto) | `Contrato de criação e atualização do rascunho`, THEN 3 |
| gabarito SHALL ser A–E, dificuldade facil/media/dificil, explicação texto ou null e Assunto/Matéria SHALL estar ativos. (obrigação 2/2, na ordem do texto) | `Contrato de criação e atualização do rascunho`, THEN 3 |
| Edição SHALL incrementar revisão sem alterar versão publicada; | `Revisão e versão publicada após edição`, THEN 1 |
| revisão obsoleta ou Questão arquivada SHALL retornar 409. | `Revisão e versão publicada após edição`, THEN 1 |

#### Publicação explícita com versão imutável

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| `POST /api/questoes/<id>/publicar` SHALL exigir Administrador, reautenticação nos últimos 15 minutos, origem/CSRF, revisão atual, `confirmar:true` e motivo de 3–500 caracteres após trim. | `Controles e snapshot da publicação de Questão`, THEN 1 |
| SHALL validar conteúdo e catálogo, registrar revisão/aprovação/publicação com ator e motivo e disponibilizar snapshot imutável com número único, conteúdo completo, gabarito e classificação. | `Controles e snapshot da publicação de Questão`, THEN 2 |
| Nova publicação SHALL preservar versões anteriores; | `Preservação e replay da publicação de Questão`, THEN 1 |
| revisão já publicada SHALL retornar a mesma versão sem duplicação. | `Preservação e replay da publicação de Questão`, THEN 1 |
| Arquivada SHALL rejeitar publicação com 409. | `Preservação e replay da publicação de Questão`, THEN 2 |

### Cláusulas de simulados-fixos

#### Composição fixa revisada e publicada

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| A gestão `/api/admin/simulados` SHALL exigir Administrador e permitir listar, cadastrar, consultar e editar rascunho com título de 3–150 caracteres e sequência de 1–180 versões elegíveis de Questões distintas. | `Composição e listagem administrativas de Simulados`, THEN 1 |
| Listagem SHALL usar paginação padrão 1/20, máximo 100, filtro de estado e ordem ID decrescente. | `Composição e listagem administrativas de Simulados`, THEN 2 |
| Publicar SHALL exigir revisão atual, confirmação, motivo 3–500 caracteres, reautenticação recente, origem/CSRF e revisão explícita, persistindo composição/decisão atomicamente. | `Confirmação e imutabilidade da publicação de Simulado`, THEN 1 |
| Publicado/arquivado SHALL NOT aceitar edição; | `Confirmação e imutabilidade da publicação de Simulado`, THEN 2 |
| nova composição SHALL exigir novo simulado. | `Confirmação e imutabilidade da publicação de Simulado`, THEN 2 |
| Publicação repetida SHALL retornar mesma versão sem duplicação. | `Confirmação e imutabilidade da publicação de Simulado`, THEN 3 |

#### Início e retomada de tentativa própria

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| `GET /api/aluno/simulados` SHALL listar publicados com quantidade real e disponibilidade atual sem gabarito. | `Catálogo e contrato de início de Simulado`, THEN 1 |
| `POST /api/aluno/tentativas-simulado` SHALL aceitar versão e chave UUID, criar tentativa própria com composição congelada e 201 ou recuperar tentativa em andamento com 200. | `Catálogo e contrato de início de Simulado`, THEN 2 |
| SHALL permitir no máximo uma tentativa em andamento por Aluno/versão; | `Catálogo e contrato de início de Simulado`, THEN 3 |
| replay da chave SHALL NOT duplicar tentativa e chave divergente SHALL retornar 409. (obrigação 1/2, na ordem do texto) | `Catálogo e contrato de início de Simulado`, THEN 3 |
| replay da chave SHALL NOT duplicar tentativa e chave divergente SHALL retornar 409. (obrigação 2/2, na ordem do texto) | `Catálogo e contrato de início de Simulado`, THEN 3 |
| Conteúdo retirado/superado SHALL impedir novo início com 409, sem substituir Questões. | `Disponibilidade e composição na retomada de Simulado`, THEN 1 |
| Tentativa já iniciada SHALL continuar na composição original. | `Disponibilidade e composição na retomada de Simulado`, THEN 2 |

#### Finalização atômica com resultado imutável

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| `POST /api/aluno/tentativas-simulado/<id>/finalizar` SHALL exigir confirmação e revisão atual, corrigir com gabaritos capturados e persistir respostas/correções/totais/instante/estado atomicamente. | `Correção e totais da finalização de Simulado`, THEN 1 |
| Resultado SHALL conter total, respondidas, acertos, erros, em_branco e percentual `100 * acertos / total` com duas casas. | `Correção e totais da finalização de Simulado`, THEN 2 |
| Total SHALL igualar acertos + erros + em_branco. | `Correção e totais da finalização de Simulado`, THEN 3 |
| Replay de finalização concluída SHALL retornar o mesmo resultado com 200. | `Replay e imutabilidade da tentativa finalizada`, THEN 1 |
| Tentativa finalizada SHALL NOT aceitar alterações de respostas ou recálculo retroativo. | `Replay e imutabilidade da tentativa finalizada`, THEN 2 |

#### Consulta privada e preservação histórica

| Cláusula original (literal) | Cenário de destino |
| --- | --- |
| Histórico, detalhe, resultado e correção SHALL ser exclusivos do Aluno dono. | `Conteúdo e paginação da consulta de Simulado`, THEN 1 |
| Resultado/correção antes da finalização SHALL retornar 409; | `Conteúdo e paginação da consulta de Simulado`, THEN 2 |
| após finalização SHALL apresentar alternativas escolhidas, versões, gabaritos e explicações originais. | `Conteúdo e paginação da consulta de Simulado`, THEN 2 |
| Histórico SHALL ser paginado padrão 1/20, máximo 100 e finalização/ID decrescentes. | `Conteúdo e paginação da consulta de Simulado`, THEN 3 |
| ID inexistente/alheio SHALL produzir o mesmo 404. | `Conteúdo e paginação da consulta de Simulado`, THEN 4 |
| Arquivamento administrativo confirmado e auditado SHALL impedir novos inícios sem excluir tentativas; | `Retirada de novos usos com histórico preservado`, THEN 1 |
| publicação/transferência do catálogo SHALL NOT reescrever histórico. | `Retirada de novos usos com histórico preservado`, THEN 1 |

## Resultados da aplicação

### Validações executadas em 07/11/2026

| Comando ou conferência | Resultado |
| --- | --- |
| `openspec validate <capability> --type spec --strict --json`, para cada uma das sete capabilities editadas | Saída 0 em todas, imediatamente após a edição correspondente. |
| `openspec validate --specs --strict` | Saída 0; 11 capabilities aprovadas, zero erros e zero avisos. Baseline: 31 avisos, eliminados por realocação editorial. |
| `openspec validate alinhar-documentacao-de-entrega --type change --strict` | Saída 0; somente INFO esperado de `skip_specs`, sem delta funcional. |
| `npm run test:e2e:list` | Saída 0; `Total: 3 tests in 3 files`: `entrega-academica.spec.js`, `plano-simulado.spec.js`, `privacidade.spec.js`. Somente descoberta, sem executar aplicação, navegador ou MySQL. |
| Here-string PowerShell com Node e `yaml` já instalado como dependência do CLI OpenSpec | Parsing YAML aprovado; comparação estrutural antes/depois excluindo `context` idêntica; texto a partir de `rules:` também idêntico. Nenhuma dependência instalada. |
| Here-string PowerShell com Python, `pathlib`, `re` e `git show HEAD:<arquivo>` | 51 títulos de requisitos e 178 cenários anteriores preservados nas sete specs. 31 descrições encurtadas, 78 cenários editoriais adicionados; 178 sentenças normativas originais conservadas literalmente, cobrindo 241 obrigações rastreadas. |
| Comparação dos blocos com o baseline Git | Purpose preservado em cada arquivo; 20 requisitos fora do inventário e quatro capabilities restantes intactos. Nenhuma mudança de regra inferida a partir do código. |
| Conferência Python de links e numeração | 45 links relativos/âncoras válidos no README, matriz e relatório; lista do README e todas as linhas da matriz intactas; IDs 1–20 correspondem aos vinte `test.step` numerados existentes. Passos auxiliares e os outros E2E não aumentam a contagem. |
| `git -c core.safecrlf=false diff --check` | Saída 0 após remover linhas vazias extras no final de quatro specs. |
| `git -c core.safecrlf=false diff --name-only` e `git diff --cached --name-only` | Exatamente os dez arquivos principais permitidos modificados; nenhum staged. Além deles, somente `tasks.md` e este `validacao.md` foram alterados/criados nesta change. |

Os títulos, corpos e ordem relativa dos cenários anteriores foram comparados com
os blocos Git; cada sentença realocada corresponde literalmente a um único THEN
novo do mesmo requisito. A contagem de SHALL/MUST por requisito só aumenta em um,
correspondente à nova síntese curta; nenhuma obrigação original desaparece.
A revisão semântica também conferiu permissões/ordem de autorização, origem/CSRF,
limites e literais HTTP, normalização, fórmulas/denominadores, UTC, snapshots,
atomicidade, replay, retirada de conteúdo e a exceção de eliminação após negativa.
Os cenários acrescentados apenas agrupam essas cláusulas por contexto.

### Evidência de publicação

Consulta somente leitura à API do GitHub:
`GET /repos/Matibas100/ProjetoSoftwarePE/actions/runs/42337772001`.
O [run 42337772001](https://github.com/Matibas100/ProjetoSoftwarePE/actions/runs/42337772001)
retornou `head_branch: main`, `head_sha: 6f40f1303560cad908fbdd752fd0aaa4dd285b3b`,
`event: push`, `status: completed` e `conclusion: success`.
Conclusão registrada em `2026-11-07T04:20:45Z` (01:20:45 em America/Sao_Paulo).
A aprovação é histórica desse SHA, sem atribuição às edições locais desta change.
Publicação do código não comprova AWS, slides ou demonstração do grupo.

### Limites e continuidade

Nenhum código, teste de aplicação, SQL, HTML legal, segredo, ADR/relatório
histórico ou binário oficial foi editado. Aplicação, E2E e integrações MySQL
não foram executados nesta edição documental. Os diretórios preexistentes da
outra change e de temporários foram preservados. Não houve commit, push ou merge.

As oito tarefas de aplicação estão concluídas. A verificação pelo workflow deve
preceder o arquivamento; esta execução de apply não arquivou a change.
Não há delta funcional para sincronizar (`skip_specs: true`).
