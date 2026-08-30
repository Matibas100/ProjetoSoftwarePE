# ADR-005 — Versionamento editorial

## 1. Status

**ACEITO**

## 2. Data da decisão

2026-08-29

## 3. Contexto

Questões, Simulados, Resumos e Temas de Redação terão rascunho, revisão, aprovação, publicação e arquivamento. Tentativas e correções precisam preservar exatamente o conteúdo usado. Hoje `questoes` é um registro mutável e os demais conteúdos ainda não existem. A Errata também exige que indicadores transversais não substituam o estado editorial.

## 4. Problema

Separar a identidade lógica de um conteúdo de suas revisões, garantindo que publicação e uso histórico apontem para versões imutáveis e auditáveis.

## 5. Restrições do projeto e da disciplina

- MySQL e SQLAlchemy permanecem.
- CRUD simples de entidades/rascunhos usa Model; histórico complexo pode usar Repository.
- Services coordenam criação, revisão e publicação sem SQL.
- Tentativas e resultados não podem mudar retroativamente.
- Conteúdo oficial original, autoria, origem e histórico devem ser preservados.
- Nenhuma tabela é autorizada por este ADR em proposta.

## 6. Opções analisadas

- **A — Atualização direta do registro.**
- **B — Cópia integral independente a cada versão.**
- **C — Entidade lógica + tabela de versões imutáveis.**
- **D — Event sourcing completo.**

## 7. Vantagens de cada opção

- **A:** schema e CRUD simples; menor armazenamento.
- **B:** snapshots fáceis de ler e pouca abstração inicial.
- **C:** identidade estável, versões ordenadas, referências históricas explícitas e publicação controlada.
- **D:** trilha completa de eventos e reconstrução temporal detalhada.

## 8. Desvantagens de cada opção

- **A:** destrói histórico e altera tentativas passadas.
- **B:** duplica identidade, dificulta “versão atual” e relações entre cópias.
- **C:** exige mais tabelas, constraints, transações e queries.
- **D:** complexidade operacional e conceitual desproporcional ao projeto escolar; leitura exige projeções.

## 9. Riscos

Editar versão publicada; tentativa referenciar entidade lógica em vez da versão; duas versões atuais; número de versão concorrente; mídia mutável; cópia incompleta; gabarito retroativo; arquivamento esconder histórico; estado editorial confundido com indicador transversal.

## 10. Impacto no MVP atual

`Questao` e seus endpoints continuam funcionando durante transição. A questão atual poderá ser tratada como versão inicial em backfill futuro, preservando seu `id` ou uma tabela de compatibilidade conforme plano aprovado. A procedure atual deve continuar retornando o contrato legado até evolução explícita.

## 11. Impacto nas 60 telas

Impacto direto em ALU-QUE-002/003, ALU-SIM-002/003/004, ALU-RES-002, ALU-RED-002/003/004; ADM-QUE-001/002/009/010, ADM-SIM-001 a 006, ADM-RES-001 a 003, ADM-TEM-001 a 005 e ADM-RED-001 a 003. Gestão, preview, revisão, publicação, histórico e correção precisam mostrar a versão correta.

## 12. Impacto no MySQL

Estrutura conceitual recomendada: entidades lógicas (`questoes`, `simulados`, `resumos`, `temas_redacao`) e respectivas tabelas de versões imutáveis. Tentativas, itens e submissões referenciam a versão utilizada. Constraints devem garantir número único por entidade e no máximo uma versão publicada/atual conforme política. Nomes e campos finais aguardam modelagem.

## 13. Impacto na API

Contratos administrativos futuros diferenciarão entidade, rascunho/versão e publicação. Leitura do Aluno resolve a versão publicada; tentativa recebe identificador da versão. APIs atuais permanecem temporariamente compatíveis e não ganham URL definitiva neste documento.

## 14. Impacto nos testes

Criação de primeira/nova versão; imutabilidade após publicação; concorrência de numeração; tentativa preservada após nova publicação; rollback de publicação; arquivamento; autoria/origem; mídia versionada; comparação antes/depois; compatibilidade dos 29 testes e da procedure.

## 15. Impacto em segurança

Somente perfis autorizados criam, revisam e publicam. Mudanças registram ator e motivo; conteúdo restrito respeita autorização por versão. Histórico não deve expor dados pessoais ou rascunhos a perfis de leitura pública.

## 16. Recomendação técnica

Fica aceita a **opção C — entidade lógica + tabela de versões**, com as seguintes regras:

- rascunho pode ser editado;
- envio para revisão cria snapshot versionado;
- ajustes solicitados criam nova versão de rascunho;
- versão aprovada ou publicada é imutável;
- alteração posterior cria nova versão;
- tentativa de Questão aponta para `questao_versao_id`;
- tentativa de Simulado aponta para `simulado_versao_id`;
- composição de Simulado aponta para `questao_versao_id`;
- Redação enviada é imutável e reescrita cria nova versão;
- reprocessamento cria nova versão de correção e preserva a anterior para auditoria;
- conteúdo oficial original permanece preservado;
- adaptação substancial cria nova entidade, com proveniência para o original.

Cada versão guarda snapshot editorial, autoria, origem, estado e referências de mídia. Nenhuma versão já utilizada pode ser alterada retroativamente.

## 17. Consequências da recomendação

Tentativas e históricos ficam estáveis, mas Services de publicação passam a coordenar múltiplas entidades e exigem a fronteira transacional do ADR-006. Consultas de gestão e comparação provavelmente usarão Repository; CRUD de rascunho/versão individual continua em Models.

## 18. Estratégia de adoção gradual

1. Aprovar estados e propriedade das entidades.
2. Modelar primeiro Questão como caso-piloto.
3. Auditar/backfill do conteúdo atual como versão inicial.
4. Manter adaptador de resposta para endpoints legados.
5. Fazer tentativas novas referenciarem versões.
6. Aplicar padrão a Simulados, Resumos e Temas.
7. Versionar correções e mídias vinculadas.

## 19. Critérios de aceite

- Conteúdo publicado não é alterado in-place.
- Toda tentativa aponta para versões exatas de simulado/questões.
- Resultado histórico permanece igual após nova publicação.
- Autoria, origem, revisão, estado e motivo são rastreáveis.
- Nova edição após publicação cria nova versão.
- Existe uma resolução determinística da versão atual/publicada.
- APIs legadas mantêm compatibilidade durante transição aprovada.

## 20. Pontos que dependem do professor ou da equipe

Permanecem para definição operacional da equipe: nomes e formato final das tabelas; alcance técnico do snapshot; numeração; retenção; backfill do `id` atual; exposição de histórico e comparação; e vínculo de mídias. A imutabilidade de versões aprovadas/publicadas e das submissões já está decidida.

## 21. Decisão final

**ACEITO.**
