# ADR-007 — Armazenamento de mídias e arquivos

## 1. Status

**ACEITO**

## 2. Data da decisão

2026-08-29

## 3. Contexto

Questões poderão conter imagens, gráficos e fórmulas renderizadas; Resumos e Temas terão mídias/fontes; importações receberão provas e gabaritos em PDF. O MVP não armazena arquivos. A hospedagem futura e o provedor comercial ainda não foram aprovados.

## 4. Problema

Definir onde guardar bytes e metadados, como validar uploads e como fornecer acesso público/privado com integridade, backup e portabilidade entre desenvolvimento e produção.

## 5. Restrições do projeto e da disciplina

- MySQL guarda entidades e metadados; seu uso para BLOB precisa ser justificado.
- Integração de armazenamento fica atrás de adapter/Service específico.
- Controllers não manipulam filesystem diretamente.
- Repositories não viram camada de upload.
- Conteúdo publicado e histórico precisam referenciar mídia estável/versionada.
- Nenhum provedor comercial é escolhido nesta proposta.

## 6. Opções analisadas

- **A — BLOB no MySQL.**
- **B — Filesystem local.**
- **C — Object Storage.**
- **D — Híbrido por ambiente:** adapter comum, filesystem no desenvolvimento e Object Storage na produção.

## 7. Vantagens de cada opção

- **A:** transação conjunta e backup centralizado; FK direta possível.
- **B:** implementação local simples e sem serviço externo.
- **C:** escalabilidade, durabilidade, URLs assinadas, lifecycle e distribuição adequados a arquivos.
- **D:** desenvolvimento acessível sem acoplar domínio ao ambiente de produção.

## 8. Desvantagens de cada opção

- **A:** banco cresce rapidamente, backups/restores ficam pesados e entrega de arquivos compete com consultas.
- **B:** difícil compartilhar entre instâncias, risco de perda no deploy e controle de acesso manual.
- **C:** requer infraestrutura, credenciais, custo e tratamento de indisponibilidade.
- **D:** dois adapters devem apresentar semântica equivalente e ser testados; diferenças podem surgir entre ambientes.

## 9. Riscos

Upload malicioso; MIME declarado falso; path traversal; nome inseguro; arquivo público indevido; URL permanente vazada; malware; bomba de descompressão/PDF; hash calculado incorretamente; objeto órfão; remoção de mídia ainda referenciada por versão; backup inconsistente.

## 10. Impacto no MVP atual

Nenhum campo ou endpoint atual precisa mudar imediatamente. O cadastro de Questão sem mídia continua válido. A adoção futura deve acrescentar capacidades sem exigir que os quatro artefatos de Design sejam usados como dados da aplicação.

## 11. Impacto nas 60 telas

Impacto direto em ALU-QUE-002/003, ALU-RES-002, ALU-RED-002/003; ADM-QUE-002 a 009, ADM-RES-002/003, ADM-TEM-002 a 005 e fluxos de importação. Telas de gestão precisarão estados de upload, processamento, indisponibilidade, acessibilidade e permissão.

## 12. Impacto no MySQL

O banco provavelmente guardará: identificador, nome original, nome seguro/chave, MIME detectado, tamanho, hash, localização, origem, fonte, referência, legenda, descrição textual, autor, datas, status e versão. Os bytes ficam fora do MySQL na recomendação, salvo exceção pequena e explicitamente aprovada.

## 13. Impacto na API

Contratos futuros precisarão upload iniciado/concluído, metadados, vínculo, download autorizado e remoção/arquivamento. Arquivos privados devem usar resposta autenticada ou URL assinada curta. URLs e limites definitivos permanecem a definir.

## 14. Impacto nos testes

Testar tamanho, MIME real, extensão, hash, duplicidade, nome seguro, autorização, URL expirada, upload interrompido, malware/quarentena, objeto órfão, rollback de vínculo, adapter local e contrato do adapter de produção. Testes unitários podem usar armazenamento temporário; integração real depende do ambiente aprovado.

## 15. Impacto em segurança

Uploads ficam privados por padrão, fora de diretório executável, com allowlist de formatos, limite de tamanho, inspeção do conteúdo, nome gerado, checksum e quarentena até validação. Downloads validam autorização; logs não registram URL assinada/credencial. SVG e documentos ativos exigem tratamento especial.

## 16. Recomendação técnica

Fica aceita a **opção D**, com uma interface `StorageService`, `LocalStorageAdapter` no desenvolvimento e `ObjectStorageAdapter` na produção. Nenhum provedor comercial é escolhido nesta decisão.

Regras obrigatórias:

- arquivos ficam fora do Git e o filesystem local fica fora da pasta pública;
- o banco guarda `storage_key` independente do provedor, nunca URL ou caminho absoluto como identidade persistente;
- bytes ficam fora do MySQL por padrão;
- MySQL guarda metadados, hash, origem, fonte, acessibilidade, status e vínculo versionado;
- formatos permitidos, MIME real e limites de tamanho são validados no servidor;
- upload passa por quarentena e possui gancho para verificação antimalware;
- acesso é autorizado e conteúdo privado usa URL temporária;
- deduplicação pode usar hash, sem unir automaticamente registros semanticamente distintos;
- retenção e vínculos são verificados antes de qualquer exclusão física.

## 17. Consequências da recomendação

O domínio não conhece caminho físico nem SDK do provedor. Será necessário reconciliar objeto e metadata, definir lifecycle/retention, executar limpeza segura de órfãos e garantir paridade entre adapters. Backup passa a abranger banco e objetos.

## 18. Estratégia de adoção gradual

1. Aprovar formatos, limites e classificação público/privado.
2. Definir contrato do adapter e metadata conceitual.
3. Implementar adapter local seguro em etapa futura.
4. Integrar um fluxo piloto de imagem de Questão.
5. Adicionar processamento/quarentena de PDFs.
6. Selecionar Object Storage somente antes da hospedagem.
7. Definir backup, retenção, reconciliação e migração de objetos.

## 19. Critérios de aceite

- Bytes não ficam acoplados à Model de domínio nem a caminho absoluto.
- MIME, tamanho, hash e nome seguro são verificados no servidor.
- Arquivos privados não possuem URL pública permanente.
- Mídia publicada/histórica não é sobrescrita.
- Backup e restauração abrangem metadados e objetos.
- Adapters possuem contrato equivalente e testes.
- Nenhum provedor/segredo é hardcoded.

## 20. Pontos que dependem do professor ou da equipe

Permanecem para definição operacional da equipe: limites e allowlist de formatos; política para SVG/PDF; ferramenta antimalware; classificação de acesso; prazos de retenção; regra de deduplicação por hash; provedor/hospedagem; e ownership de mídias oficiais. O uso dos adapters local e de Object Storage já está decidido.

## 21. Decisão final

**ACEITO.**
