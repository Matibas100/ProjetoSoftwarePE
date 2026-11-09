# Gestão administrativa de Alunos

O Administrador acessa **Usuários** em `/admin/usuarios.html`. A listagem
busca nome/e-mail literalmente, filtra ativo/inativo e pagina resultados.
O detalhe `/admin/usuario.html?id=ID` consulta os dados atuais; sem ID, cria
uma conta de Aluno. Senha inicial aparece somente na criação e é limpa após
sucesso, perda de identidade ou descarte. Não existe envio por e-mail,
expiração da senha inicial ou troca obrigatória.

## Contrato HTTP

Todos os caminhos abaixo têm prefixo `/api/admin/usuarios`. Leituras exigem
Administrador; mutações também exigem Origin, CSRF e senha confirmada há menos
de 15 minutos. Respostas, inclusive erros, usam `Cache-Control: no-store`.

| Método e sufixo | Entrada exata | Sucesso |
| --- | --- | --- |
| GET coleção | `busca,status,pagina,por_pagina` opcionais | 200 paginado |
| POST coleção | `nome,email,senha,senha_confirmacao` | 201 detalhe |
| GET `/ID` | ID inteiro positivo até 2147483647 | 200 detalhe |
| PUT `/ID` | `nome,email` | 200 detalhe |
| POST `/ID/desativar` | `confirmar:true` | 200 detalhe |
| POST `/ID/reativar` | `confirmar:true` | 200 detalhe |
| DELETE `/ID` | `confirmar:true` | 204 |

Paginação começa em 1, com 20 itens e máximo 100. Status aceita vazio,
`ativo` ou `inativo`; busca tem até 254 caracteres após trim. Ordem:
`criado_em DESC,id DESC`. `%`, `_` e barras são literais. O envelope contém
`itens,pagina,por_pagina,total_itens,total_paginas`, inclusive em página vazia.

Detalhe contém `id,nome,email,perfil,ativo,criado_em`; listagem substitui
`email` por `email_mascarado` (`a***@dominio`). Datas são UTC ISO com `Z` e
ativo é booleano. Senhas, sessões, decisões e estudos não integram esses DTOs.
Nome/e-mail usam a validação do cadastro; perfil é sempre `aluno`.

Corpos JSON aceitam somente os campos indicados e têm limite local de 16 KiB.
Erros usam `{erro,codigo}`: 400 `dados_invalidos`; 401/403 da autenticação;
404 `usuario_nao_encontrado` também para alvo Administrador;
409 `email_em_uso`, `usuario_com_vinculos` ou `operacao_concorrente`;
413 `corpo_muito_grande`; 500 `erro_interno` sanitizado. Não há retry automático.
HEAD preserva autorização sem corpo; OPTIONS e 404 do roteador seguem a API.

## Sessões, vínculos e responsabilidade

`UsuarioController` chama um Service por caso de uso em Contas. CRUD simples
usa `Usuario.salvar/atualizar/deletar`, com `confirmar=False` e uma fronteira
`TransactionManager`. `Usuario.to_dict`, cadastro público e CLI permanecem.
As únicas adições à allowlist de atualização da Model são nome/e-mail.

Criação administrativa não cria sessão nem aceite para o titular. O cadastro
público mantém aceite obrigatório. O Aluno provisionado registra suas decisões
na própria área de privacidade; plano/Tutor mantêm os guards atuais.

Editar só o nome ou reenviar valores iguais preserva sessões. Trocar e-mail
revoga todas na mesma transação. Login conserva o e-mail normalizado esperado
na validação bloqueante da senha e na criação bloqueante de sessão. Desativar
marca inativo e revoga sessões atomicamente; repetir é seguro. Reativar exige
novo login e não restaura cookies. Histórico e decisões permanecem.

DELETE deixa as FKs `RESTRICT` arbitrarem a exclusão. Aceites, sessões mesmo
revogadas, planos, autoria e demais referências podem impedi-la. A API só
traduz 1451 em `usuario_com_vinculos`, após rollback, sem limpar dependências.
Desativação é outra ação confirmada; erro 409 não a executa automaticamente.
Duplicidade 1062 é traduzida somente para a chave `uq_usuarios_email`;
1205/1213 produzem conflito transitório após rollback.

## Interfaces SQL e instalação

| Routine | Proprietário/uso | Resultado |
| --- | --- | --- |
| `sp_alunos_admin(busca,ativo,offset,limite)` | `UsuarioRepository`, contrato `ConsultaAlunosAdmin` injetado por aplicação | Linhas sem senha e segundo conjunto `total_itens`, no mesmo `ContextoLeitura` próprio |
| `sp_usuario_gestao_bloqueado(id)` | `UsuarioRepository` na transação da mutação | Usuario completo privado, incluindo inativos, `FOR UPDATE` com estado corrente |
| `sp_revogar_sessoes_usuario(id,agora)` | `AutenticacaoRepository`, reutilizada da 016 | Revogação participante e sincronização seletiva, sem commit próprio |

As duas novas routines são `READS SQL DATA`, `SQL SECURITY INVOKER`, sem
transação própria. O Repository fecha/consome resultados; não há fallback ORM
para listagem ou lock. Hash do lock nunca atravessa os DTOs administrativos.
Não há nova tabela, FK, mapper ou módulo.

Antes de usar as telas, instalar **017** sobre 016 íntegro pelo runner oficial,
com privilégios de criação de routines e acesso aos metadados. Em banco
operacional, fazer e validar backup conforme o procedimento existente:

```powershell
python backend/database/migrate.py status
python backend/database/migrate.py up
python backend/database/migrate.py status
```

Não executar o bootstrap sobre um banco existente. Uma cópia equivalente sem
histórico pode usar `baseline --confirm` após backup. Referências da 017 foram
geradas em schema descartável pelas migrations oficiais; drift/parcial ou
dependência inválida bloqueiam adoção/upgrade. DDL não tem rollback transacional;
compensação exige restauração ou migration revisada. 000–016 são preservadas.

Integrações criam schemas descartáveis e exigem opt-ins somente no processo:

```powershell
$env:RUN_MYSQL_INTEGRATION = "1"
$env:RUN_MYSQL_MIGRATION_INTEGRATION = "1"
python backend/tests/run_backend_coverage.py
Remove-Item Env:RUN_MYSQL_INTEGRATION, Env:RUN_MYSQL_MIGRATION_INTEGRATION
```

E2E: `RUN_MYSQL_E2E=1` com configuração MySQL no ambiente e
`python scripts/run_e2e.py`. Não persistir opt-ins em `.env`.

## Alcance visual e evidências

ADM-USU-001/002 orientam o shell, tokens, hierarquia e ações das duas telas.
O recorte implementa somente Alunos: sem Visualizador, escolha de perfil,
e-mail verificado, métricas fictícias, auditoria, exportação, recuperação,
estudos alheios ou revogação manual avulsa. Em 390 px o menu se torna horizontal
e a tabela rola dentro do card; a página não deve ter overflow horizontal.
Teclado, confirmações, foco e rascunho seguem AuthUI/AdminUI, com consultas
obsoletas descartadas e ações sempre reconfirmadas após recuperação.

Os binários oficiais e HTMLs legais são preservados. Testes e resultados estão
na [validação da change](../../openspec/changes/archive/2026-11-09-gerenciar-contas-de-alunos/validacao.md).
F01 abrange somente Alunos após prova ponta a ponta; não representa gestão de
Administradores, exclusão geral, auditoria completa ou aceite acadêmico.
