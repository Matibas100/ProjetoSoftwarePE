# Proposal

## Why

O Tutor IA está previsto no Desktop V1, mas continua indisponível no sistema. A atividade de consulta a LLM pede um caso de tutoria com API, Service de integração, validações e tratamento de falhas; uma primeira versão com uma dúvida por envio atende esse objetivo sem introduzir um chat persistente.

## What Changes

- Entregar o recorte inicial de `ALU-TUT-001`, com Matéria, Assunto, dúvida e resposta de revisão para o ENEM: explicação, exemplo, pergunta de compreensão e exercício sem gabarito.
- Criar `POST /api/tutoria`, exclusivo do Aluno autenticado, com o contrato de quatro campos da aula, Origin/CSRF e erros claros.
- Acrescentar o módulo `tutor_ia`, Controller em classe, `GerarTutoriaService` e `GeminiService` específico, ligado por contrato pequeno na composição existente.
- Usar Gemini via REST, com chave somente no backend, tempo de espera limitado, envio independente e `store=false`. Não guardar dúvidas ou respostas no banco, em logs ou no armazenamento do navegador.
- Publicar Termo de Uso 2.0 antes de liberar envios, preservando os bytes, hashes e registros da versão 1.0. O consentimento do plano continua independente e não autoriza envio à IA.
- Cobrir a integração HTTP, a tela, os erros e a compatibilidade; documentar execução e demonstração com dados sintéticos. Uma chamada real ao provedor será validada separadamente das suítes sem acesso externo.

### Fora de escopo

Histórico de conversas, memória entre envios, anexos, streaming, agentes, ferramentas, RAG, banco vetorial, personalização por desempenho, correção de redação/prova, criação de questões, novo CRUD, autorização real de menores, implantação AWS, vídeo e guia de estudo. Ações futuras do protótipo não serão apresentadas como disponíveis.

## Capabilities

### New Capabilities

- `tutoria-revisao-ia`: revisão pontual via Gemini, incluindo contrato HTTP, autorização, integração externa, tela, limites e validação da entrega.

### Modified Capabilities

- `termos-e-consentimento`: transparência sobre a nova integração opcional, nova versão imutável de uso e aceite vigente exigido para o Tutor, sem ampliar o consentimento do plano.

## Impact

- Backend: novo módulo, contratos, composição, Blueprint, configuração opcional e reconhecimento exato de `/api/tutoria` na proteção de perfil e cache. O restante da API mantém sua autorização atual.
- Frontend: nova `/aluno/tutor.html`, JavaScript/CSS próprios, navegação e referências atuais a Tutor indisponível. Reusar `apiRequest` e `AuthUI`.
- Privacidade: documentos públicos, registro de versões e testes de cadastro/aceite/plano. Não há novo tipo de consentimento, tabela, migration ou Stored Procedure nesta change.
- Dependência: cliente HTTP `requests`, como na aula; valores de configuração somente no ambiente e placeholders em `.env.example`.
- Arquitetura: adendo ao ADR-010 e atualização do mapa modular para sete módulos; preservar os 21 mappers e a infraestrutura de persistência. ADRs 002, 006, 008 e 009 continuam aplicáveis.
- Referência visual: protótipo oficial, página 26, e inventário `ALU-TUT-001`; os binários congelados permanecem intactos. Registrar a diferença entre este recorte pontual e o chat contextual futuro.
- Compatibilidade: preservar os vinte casos acadêmicos e seus dados. A nova versão de uso exige novo aceite explícito, inclusive para voltar a liberar o plano conforme sua regra vigente, sem apagar planos ou consentimentos. Questões, simulados e desempenho continuam independentes dessa atualização.
- Dependências de demonstração: configuração local válida do Gemini e acesso ao modelo. Sem chave, o restante do sistema inicia normalmente e o Tutor informa indisponibilidade; não simular resposta como se fosse real nem contabilizar este fluxo sem histórico como novo CRUD completo.
