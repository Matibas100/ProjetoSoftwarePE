# ADR-002 — Estratégia de autenticação

## 1. Status

**ACEITO**

## 2. Data da decisão

2026-08-29

## 3. Contexto

O produto terá ambientes Público, Aluno e Administração, múltiplos perfis, recuperação e troca de senha, revogação de sessões, logout de outros dispositivos e reautenticação de ações críticas. O MVP não possui autenticação. A experiência principal é web; aplicativo móvel é possibilidade futura, não requisito aprovado.

## 4. Problema

Escolher como representar, transportar, expirar e revogar a autenticação sem guardar segredo acessível ao JavaScript nem tornar autorização dependente apenas da interface.

## 5. Restrições do projeto e da disciplina

- Controllers continuam adaptando HTTP e chamando Services.
- Services de autenticação coordenam casos de uso sem SQL direto.
- Models fazem CRUD simples; consultas/revogações especializadas podem usar Repository.
- Autorização é verificada no servidor sob menor privilégio.
- CORS é configurável e os ambientes poderão usar origens distintas.
- Nenhuma biblioteca ou endpoint é escolhido nesta proposta.

## 6. Opções analisadas

- **A — Sessão no servidor:** identificador opaco em cookie seguro; estado e revogação no servidor.
- **B — JWT access + refresh:** access token curto e refresh token rotacionado/revogável.
- **C — Híbrido:** sessão/cookie para web e tokens separados para clientes móveis ou integrações futuras.

## 7. Vantagens de cada opção

- **A:** revogação simples, cookie `HttpOnly`, pouco estado sensível no frontend e boa adequação à aplicação web escolar.
- **B:** autenticação distribuída, útil a APIs independentes e clientes móveis; access token curto reduz janela de exposição.
- **C:** mantém simplicidade web e abre fronteira futura sem forçar JWT no navegador.

## 8. Desvantagens de cada opção

- **A:** requer armazenamento compartilhado ao escalar e proteção CSRF explícita.
- **B:** revogação e rotação são complexas; token em armazenamento JavaScript amplia impacto de XSS; logout não é automaticamente imediato.
- **C:** mantém dois mecanismos, políticas e suítes de testes; só se justifica quando existir segundo cliente aprovado.

## 9. Riscos

Cookie sem `Secure`/`HttpOnly`/`SameSite`; CORS permissivo com credenciais; ausência de CSRF; refresh token reutilizado; sessão não revogada após troca de senha; enumeração de contas; reautenticação apenas visual; logs contendo tokens.

## 10. Impacto no MVP atual

As rotas atuais permanecem temporariamente compatíveis durante uma transição aprovada. Antes de exposição definitiva, cada rota deverá receber política explícita. Nenhuma autenticação deve ser inserida silenciosamente quebrando os 29 testes e o frontend MVP.

## 11. Impacto nas 60 telas

Afeta diretamente PUB-AUT-001 a 005, ALU-PER-001, ADM-USU-001/002 e ADM-SEG-001. Afeta transversalmente as demais telas protegidas por sessão, perfil, reautenticação, expiração e retorno seguro ao destino original.

## 12. Impacto no MySQL

Entidades conceituais prováveis: usuário/credencial, sessão, token opaco de recuperação/verificação, revogação e eventos de segurança. Hashes de senha usam algoritmo apropriado; tokens são armazenados por hash quando possível. Campos finais dependem da modelagem.

## 13. Impacto na API

Serão necessários contratos de login, logout, sessão atual, recuperação, redefinição, revogação e reautenticação. Cookies exigem política de CORS/CSRF; respostas de erro devem ser neutras. URLs definitivas permanecem a definir.

## 14. Impacto nos testes

Testes de cookie e flags, CSRF, expiração, rotação/reuso, múltiplas sessões, logout, troca de senha, reautenticação, autorização por perfil, enumeração, CORS e regressão dos contratos existentes.

## 15. Impacto em segurança

É alto. Senhas nunca são armazenadas em texto; cookies web devem ser `HttpOnly`, `Secure` em produção e `SameSite` apropriado; toda mutação autenticada exige defesa CSRF; sessões possuem expiração absoluta e por inatividade; ações críticas exigem reautenticação recente.

## 16. Recomendação técnica

Fica aceita a **opção A — sessão realmente armazenada no servidor** para o cliente web, com as seguintes regras:

- o cookie conterá somente identificador opaco, aleatório e sem dados de identidade;
- JWT não será armazenado em `localStorage`;
- a sessão cookie-based padrão do Flask não será o armazenamento definitivo da sessão;
- registros de sessão permitirão múltiplas sessões, revogação individual e revogação global;
- cookie `HttpOnly`, `Secure` em produção e `SameSite=Lax`;
- proteção CSRF em operações autenticadas de mutação;
- expiração absoluta e expiração por inatividade;
- reautenticação recente para ações sensíveis;
- eventual aplicativo móvel terá ADR próprio.

Nenhuma biblioteca ou extensão específica de autenticação é selecionada por esta decisão.

## 17. Consequências da recomendação

Será necessário um armazenamento revogável de sessões, proteção CSRF e configuração coordenada de cookie/CORS. Logout, troca de senha e “sair de outros dispositivos” tornam-se invalidações reais no servidor.

## 18. Estratégia de adoção gradual

1. Aprovar modelo de implantação e origem do frontend.
2. Modelar usuário, credencial e sessão.
3. Implementar autenticação e recuperação em módulo isolado.
4. Introduzir autorização por rota/recurso em etapas.
5. Preservar contratos legados até migração dos consumidores.
6. Adicionar reautenticação e revogação.
7. Avaliar tokens somente quando surgir cliente não web.

## 19. Critérios de aceite

- Nenhuma senha/token aparece em URL, log ou armazenamento JavaScript.
- Cookies possuem flags adequadas ao ambiente.
- CSRF e CORS são testados.
- Sessões expiram e podem ser revogadas individualmente ou em conjunto.
- Troca de senha aplica a política aprovada de revogação.
- Autorização ocorre no servidor e ações críticas exigem reautenticação.

## 20. Pontos que dependem do professor ou da equipe

Permanecem para definição operacional da equipe: topologia de frontend/backend; durações absolutas e por inatividade; política de revogação após troca de senha; número máximo de sessões; experiência de sessão expirada; fluxo de verificação de e-mail; e biblioteca de infraestrutura. Um aplicativo móvel futuro exigirá ADR próprio.

## 21. Decisão final

**ACEITO.**
