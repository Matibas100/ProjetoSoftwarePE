# Pacote de Decisões Arquiteturais 1

## Escopo

Este pacote consolida sete decisões revisadas antes da Modelagem Mestre do MySQL: seis aceitas e uma aceita condicionalmente. A aprovação documental não autoriza, por si só, código, schema, migration, dependência ou integração externa. Todas preservam o MVP, a arquitetura da disciplina e os contratos atuais durante uma adoção gradual.

## Síntese

| ADR | Decisão analisada | Opções principais | Decisão incorporada | Impacto dominante | Dependências | Status |
|---|---|---|---|---|---|---|
| [ADR-001](adr/ADR-001-estrategia-de-migrations.md) | Estratégia de migrations | Alembic; runner SQL; híbrido; manual | Histórico único Alembic; SQL MySQL explícito aplicado pela revision | Governança de todas as mudanças do banco | Confirmação da ferramenta pelo professor | **Aceito condicionalmente** |
| [ADR-002](adr/ADR-002-estrategia-de-autenticacao.md) | Autenticação | Sessão; JWT+refresh; híbrido | Sessão de servidor e cookie opaco seguro; mobile terá ADR próprio | Usuários, sessões, segurança e todas as telas protegidas | Implantação, CORS e autorização | **Aceito** |
| [ADR-003](adr/ADR-003-politica-de-exclusao-catalogo.md) | Exclusão de Matéria/Assunto | Cascade; bloqueio; soft delete; transferência; combinação | `RESTRICT` + arquivamento + transferência explícita; delete físico apenas sem uso/vínculo | Integridade do catálogo e preservação histórica | ADR-001; semântica de “utilizado”; ADR-005 | **Aceito** |
| [ADR-004](adr/ADR-004-unicidade-de-assunto.md) | Unicidade de Assunto | Livre; unique textual; normalizado; código interno | `UNIQUE(materia_id, nome_normalizado)` e reativação de arquivado | Taxonomia, importação e conflitos | ADR-003; normalização; ADR-001 | **Aceito** |
| [ADR-005](adr/ADR-005-versionamento-editorial.md) | Versionamento editorial | Update direto; cópia; entidade+versões; event sourcing | Entidade lógica + snapshots versionados e publicação imutável | Tentativas, publicação, histórico e auditoria | Estados editoriais; ADR-006; ADR-007 | **Aceito** |
| [ADR-006](adr/ADR-006-fronteira-de-transacoes.md) | Fronteira transacional | Commit por Model; Service; UoW; híbrido | Active Record para CRUD + `TransactionManager`/`UnitOfWork` para casos compostos | Atomicidade sem SQL/session em Services | Active Record; ADR-005; auditoria | **Aceito** |
| [ADR-007](adr/ADR-007-armazenamento-de-midias.md) | Mídias e arquivos | BLOB; filesystem; Object Storage; híbrido | `StorageService` com adapters local/objeto e bytes fora do MySQL | Upload, integridade, acesso e versionamento de mídia | ADR-005; hospedagem; política de segurança | **Aceito** |

## Ordem de adoção

1. **ADR-001 — Migrations:** confirmar a ferramenta e estabelecer o histórico único.
2. **ADR-006 — Fronteira de transações:** preparar a regra de atomicidade para os novos módulos.
3. **ADR-003 — Exclusão e arquivamento:** fixar preservação, FKs e ciclo de vida do catálogo.
4. **ADR-004 — Unicidade do catálogo:** aplicar a normalização sobre a política de arquivamento aceita.
5. **ADR-005 — Versionamento editorial:** definir entidades lógicas, snapshots e referências históricas.
6. **ADR-002 — Autenticação e sessões:** modelar credenciais e sessões reais no servidor.
7. **ADR-007 — Mídias e armazenamento:** conectar metadados e objetos às versões sem acoplar provedor.

## Impacto na Modelagem Mestre do MySQL

| ADR | Entidades/áreas futuras relacionadas | Constraints e decisões de schema condicionadas |
|---|---|---|
| ADR-001 | histórico de revisions e todos os módulos | baseline, ordem, checksum, compatibilidade entre instalação limpa e upgrade, SQL procedural |
| ADR-002 | usuários, credenciais, sessões, recuperação/verificação, revogações | unicidade de identidade, hashes, expiração, FK de usuário, índices de sessão/token, retenção |
| ADR-003 | matérias, assuntos e referências de Questões, Resumos, Simulados, Práticas | `RESTRICT`, arquivamento, integridade histórica, transferência, proibição de cascade silencioso |
| ADR-004 | assuntos e importações de taxonomia | valor normalizado, unicidade composta por Matéria, conflitos em mudança/reativação |
| ADR-005 | questões/versões, simulados/versões, resumos/versões, temas/versões, correções | identidade lógica, número de versão, imutabilidade publicada, versão atual/publicada, FKs históricas |
| ADR-006 | agregados de usuários, práticas, simulados, redações, importações, publicação e auditoria | fronteiras atômicas, locks, idempotência e eventual outbox/checkpoint |
| ADR-007 | arquivos, mídias, vínculos de mídia, uploads/importações | metadata, hash, chave de objeto, status, versão, integridade/retenção e referências sem BLOB por padrão |

## Regras preservadas

- Route chama Controller; Controller chama Service.
- Service coordena caso de uso sem SQL e sem acesso direto a `db.session`.
- CRUD simples permanece em Models Active Record.
- Repository trata consultas especializadas e procedures, sem repetir CRUD.
- MySQL e Stored Procedures continuam suportados.
- Nenhum endpoint novo recebe URL definitiva neste pacote.
- ADR-001 permanece condicionado à confirmação do professor; os ADRs 002 a 007 estão aceitos documentalmente.
