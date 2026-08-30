# Decisões em aberto v1 — Plataforma ENEM

## Finalidade

Este registro reúne decisões que exigem validação do professor e/ou da equipe antes da implementação da versão definitiva. As recomendações são preliminares, não constituem autorização para modificar código, banco ou infraestrutura.

## Situação após o Pacote de Decisões Arquiteturais 1

- 6 decisões foram aceitas: ADR-002 a ADR-007.
- 1 decisão foi aceita condicionalmente: ADR-001.
- 10 decisões permanecem abertas.
- O histórico das opções e recomendações preliminares permanece registrado abaixo.

## OD-01 — Ferramenta e runner de migrations

- **Contexto:** o MVP utiliza scripts SQL de criação e uma migration manual para a Stored Procedure. A evolução modular exigirá mudanças incrementais, reproduzíveis e reversíveis.
- **Opções:** manter scripts SQL numerados com runner controlado; adotar Alembic/Flask-Migrate; usar ferramenta institucional indicada pelo professor.
- **Impactos:** rastreabilidade do schema, ordem de implantação, rollback, compatibilidade entre ambientes e aderência à disciplina.
- **Recomendação preliminar:** confirmar primeiro a ferramenta permitida; se não houver restrição, adotar Flask-Migrate/Alembic sem descartar os scripts SQL auditáveis.
- **Status:** AGUARDANDO CONFIRMAÇÃO DO PROFESSOR — ADR-001 aceito condicionalmente: [ADR-001](adr/ADR-001-estrategia-de-migrations.md).

## OD-02 — Estratégia de autenticação

- **Contexto:** o produto definitivo possui ambientes Público, Aluno e Administração, mas o MVP não autentica usuários.
- **Opções:** sessão segura mantida pelo servidor; tokens de acesso curtos com renovação; solução institucional externa.
- **Impactos:** proteção contra CSRF/XSS, revogação, escalabilidade, armazenamento no cliente e experiência de sessão expirada.
- **Recomendação preliminar:** para uma aplicação web de mesma origem, avaliar primeiro sessão de servidor com cookie `HttpOnly`, `Secure` e `SameSite`; confirmar arquitetura de implantação antes da escolha.
- **Status:** ACEITA — decisão registrada no [ADR-002](adr/ADR-002-estrategia-de-autenticacao.md).

## OD-03 — Exclusão de Matéria com Assuntos

- **Contexto:** a relação `Materia → Assunto` precisa de política definitiva; exclusão automática pode apagar uma árvore de conteúdo acadêmico.
- **Opções:** `RESTRICT` e transferência prévia; arquivamento lógico; cascade explícito sob operação administrativa crítica.
- **Impactos:** integridade, histórico, UX administrativa e preservação de questões vinculadas.
- **Recomendação preliminar:** impedir exclusão enquanto houver dependências e oferecer arquivamento/transferência em caso de uso separado, sujeito a aprovação.
- **Status:** ACEITA — decisão registrada no [ADR-003](adr/ADR-003-politica-de-exclusao-catalogo.md).

## OD-04 — Unicidade de Assunto por Matéria

- **Contexto:** o schema atual não formaliza se nomes iguais podem coexistir dentro da mesma matéria.
- **Opções:** permitir duplicidade; unicidade textual exata; unicidade composta por matéria e nome normalizado.
- **Impactos:** pesquisa, importação, taxonomia, deduplicação e necessidade de saneamento dos dados antes de criar constraint.
- **Recomendação preliminar:** unicidade composta por `materia_id` e nome normalizado, somente após definição de normalização e auditoria dos dados existentes.
- **Status:** ACEITA — decisão registrada no [ADR-004](adr/ADR-004-unicidade-de-assunto.md).

## OD-05 — Armazenamento de imagens e arquivos

- **Contexto:** questões, resumos, redações e importações poderão possuir anexos e mídias.
- **Opções:** sistema de arquivos local; armazenamento de objetos; serviço gerenciado de mídia.
- **Impactos:** backup, URLs, segurança, tamanho do banco, disponibilidade e portabilidade.
- **Recomendação preliminar:** definir uma interface de armazenamento e usar armazenamento de objetos em produção; manter o provedor configurável.
- **Status:** ACEITA — decisão registrada no [ADR-007](adr/ADR-007-armazenamento-de-midias.md).

## OD-06 — Serviço de e-mail

- **Contexto:** verificação de e-mail, recuperação de senha e avisos dependem de entrega confiável.
- **Opções:** SMTP institucional; provedor transacional; nenhum envio na primeira fase autenticada.
- **Impactos:** entregabilidade, custo, privacidade, templates, filas e tratamento de falhas.
- **Recomendação preliminar:** integração por adaptador com provedor selecionado pela equipe; segredos exclusivamente por ambiente.
- **Status:** A decidir.

## OD-07 — Provedor de LLM

- **Contexto:** tutor, geração assistida e correção de redação poderão consumir um modelo externo, mas nenhum provedor foi aprovado.
- **Opções:** um provedor principal; estratégia multi-provedor; modelo local.
- **Impactos:** custo, latência, privacidade, moderação, disponibilidade, portabilidade e retenção de prompts.
- **Recomendação preliminar:** contrato de cliente independente de provedor, com políticas explícitas de dados e avaliação antes da ativação.
- **Status:** A decidir.

## OD-08 — Política de retenção e exclusão de dados

- **Contexto:** contas, práticas, desempenho, redações, auditoria e conteúdo editorial têm necessidades de retenção diferentes.
- **Opções:** retenção uniforme; matriz por categoria; retenção indefinida.
- **Impactos:** privacidade, rastreabilidade, custo de armazenamento, exclusão de conta e recuperação.
- **Recomendação preliminar:** aprovar uma matriz por categoria de dado, incluindo base legal, prazo, anonimização e descarte.
- **Status:** A decidir.

## OD-09 — Paginação das coleções

- **Contexto:** as listas do MVP retornam coleções completas; as 60 telas incluem tabelas, buscas e históricos potencialmente grandes.
- **Opções:** offset/limit; cursor; estratégia híbrida.
- **Impactos:** desempenho, ordenação estável, navegação, cache e contratos HTTP.
- **Recomendação preliminar:** padronizar envelope e ordenação; avaliar offset para tabelas administrativas e cursor para históricos extensos.
- **Status:** A decidir.

## OD-10 — Versionamento de conteúdo

- **Contexto:** revisão, aprovação, publicação e auditoria exigem preservar versões de questões, resumos, temas e simulados.
- **Opções:** cópias imutáveis por versão; histórico de alterações; snapshots apenas na publicação.
- **Impactos:** rollback, comparação, autoria, tamanho do banco e consistência de simulados já realizados.
- **Recomendação preliminar:** versões imutáveis com identidade estável do conteúdo e referência explícita à versão publicada.
- **Status:** ACEITA — decisão registrada no [ADR-005](adr/ADR-005-versionamento-editorial.md).

## OD-11 — Política de transações

- **Contexto:** o `CrudMixin` atual confirma cada operação Active Record; casos de uso futuros combinarão múltiplas alterações.
- **Opções:** commits internos mantidos; transação coordenada por caso de uso; Unit of Work explícita.
- **Impactos:** atomicidade, testes, rollback e preservação da API Active Record ensinada na disciplina.
- **Recomendação preliminar:** manter a interface Active Record para CRUD simples e definir uma fronteira transacional coordenada para casos compostos, sem SQL nos Services.
- **Status:** ACEITA — decisão registrada no [ADR-006](adr/ADR-006-fronteira-de-transacoes.md).

## OD-12 — Estratégia futura do frontend

- **Contexto:** o frontend do MVP é uma página HTML/CSS/JavaScript; o Desktop V1 possui 60 telas, componentes e estados.
- **Opções:** JavaScript modular sem framework; SPA baseada em componentes; renderização híbrida/servidor.
- **Impactos:** roteamento, estado, acessibilidade, testes, curva de aprendizado e implantação.
- **Recomendação preliminar:** validar restrições da disciplina e da hospedagem antes de selecionar tecnologia; preservar a API como fronteira independente.
- **Status:** A decidir.

## OD-13 — Fluxo de verificação de e-mail

- **Contexto:** o inventário registra o estado de verificação pendente, mas não há tela ou rota aprovada dedicada.
- **Opções:** estado na tela de login; página própria; fluxo por link com confirmação inline.
- **Impactos:** mapa de navegação, reenvio, expiração do link e suporte.
- **Recomendação preliminar:** aprovar o fluxo e seus estados antes de definir contrato ou criar tela.
- **Status:** A decidir.

## OD-14 — Central de notificações e perfil administrativo

- **Contexto:** o cabeçalho administrativo apresenta notificações e perfil, mas seus destinos não estão definidos no conjunto aprovado.
- **Opções:** retirar/interditar os links até definição; painéis próprios; reutilização controlada de telas existentes.
- **Impactos:** autorização, navegação e possível alteração do inventário visual.
- **Recomendação preliminar:** manter as ações sem rota definitiva até decisão formal do design e da equipe.
- **Status:** A decidir.

## OD-15 — Preview de questão e retorno contextual

- **Contexto:** “Visualizar como aluno” e retornos contextuais do tutor aparecem no handoff sem contrato completo de navegação.
- **Opções:** modo somente leitura em tela existente; rota de preview; deep link com contexto assinado.
- **Impactos:** autorização, exposição de gabarito, histórico de navegação e novos contratos.
- **Recomendação preliminar:** aprovar um contrato de preview/retorno que nunca conceda permissões do Aluno ao Editor.
- **Status:** A decidir.

## OD-16 — Eixo principal da fila de redações

- **Contexto:** falha, timeout, revisão humana e indicadores podem ser interpretados como categorias somáveis ou estados exclusivos.
- **Opções:** um estado principal com indicadores transversais; múltiplos estados independentes; filas separadas.
- **Impactos:** métricas, filtros, transições, auditoria e automação da correção.
- **Recomendação preliminar:** adotar um estado principal mutuamente exclusivo e indicadores transversais, após validação funcional.
- **Status:** A decidir.

## OD-17 — Limiares de amostra em desempenho

- **Contexto:** o design prevê insights de desempenho, mas não congela quantidade mínima de respostas para exibir tendências confiáveis.
- **Opções:** limiar global; limiar por métrica; exibição com aviso de baixa amostra.
- **Impactos:** confiança estatística, mensagens de estado vazio e critérios de aceite.
- **Recomendação preliminar:** definir limiares mensuráveis com a equipe pedagógica antes da implementação.
- **Status:** A decidir.
